from __future__ import annotations

import os
from contextlib import asynccontextmanager
from typing import Any

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.crustdata import CrustdataClient
from app.gemini import analyze_supplier, draft_outreach, parse_supply_query
from app.scoring import legitimacy_score

load_dotenv()

client: CrustdataClient | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global client
    api_key = os.getenv("CRUSTDATA_API_KEY", "")
    if not api_key:
        raise RuntimeError("CRUSTDATA_API_KEY not set")
    client = CrustdataClient(api_key)
    yield
    if client:
        await client.close()


app = FastAPI(title="SupplyLens", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def index():
    return FileResponse("static/index.html")


class SearchRequest(BaseModel):
    query: str
    limit: int = 20
    cursor: str | None = None


def _format_company(c: dict[str, Any]) -> dict[str, Any]:
    basic = c.get("basic_info", {})
    score_data = legitimacy_score(c)
    return {
        "name": basic.get("name", "Unknown"),
        "domain": basic.get("primary_domain", ""),
        "website": basic.get("website", ""),
        "linkedin": basic.get("professional_network_url", ""),
        "industries": basic.get("industries", []),
        "year_founded": basic.get("year_founded"),
        "employee_range": basic.get("employee_count_range", ""),
        "company_type": basic.get("company_type", ""),
        "headcount": c.get("headcount", {}).get("total", 0),
        "funding_total_usd": c.get("funding", {}).get("total_investment_usd"),
        "last_round_type": c.get("funding", {}).get("last_round_type"),
        "last_fundraise_date": c.get("funding", {}).get("last_fundraise_date"),
        "locations": c.get("locations", {}),
        "legitimacy": score_data,
    }


@app.post("/api/search")
async def search_suppliers(req: SearchRequest) -> dict[str, Any]:
    if not client:
        raise HTTPException(status_code=500, detail="Client not initialized")

    parsed = await parse_supply_query(req.query)

    all_results: list[dict[str, Any]] = []
    search_terms = parsed.get("search_terms", [req.query])
    if req.query not in search_terms:
        search_terms.append(req.query)

    seen_domains: set[str] = set()
    for term in search_terms[:5]:
        try:
            data = await client.search_companies(term, limit=req.limit, cursor=req.cursor)
            companies = data.get("companies", [])
            for c in companies:
                formatted = _format_company(c)
                key = formatted["domain"] or formatted["name"]
                if key not in seen_domains:
                    seen_domains.add(key)
                    all_results.append(formatted)
        except Exception:
            continue

    all_results.sort(key=lambda r: r["legitimacy"]["score"], reverse=True)

    return {
        "results": all_results[:req.limit],
        "parsed_query": parsed,
        "total_count": len(all_results),
    }


class AnalyzeRequest(BaseModel):
    company: dict[str, Any]
    user_need: str


@app.post("/api/analyze")
async def analyze(req: AnalyzeRequest) -> dict[str, Any]:
    result = await analyze_supplier(req.company, req.user_need)
    return result


class OutreachRequest(BaseModel):
    company_name: str
    contact_name: str
    contact_title: str
    user_need: str
    company_context: dict[str, Any] | None = None
    contact_context: dict[str, Any] | None = None


@app.post("/api/outreach")
async def outreach(req: OutreachRequest) -> dict[str, str]:
    email = await draft_outreach(
        req.company_name,
        req.contact_name,
        req.contact_title,
        req.user_need,
        company_context=req.company_context,
        contact_context=req.contact_context,
    )
    return {"email": email}


@app.get("/api/contacts")
async def get_contacts(domain: str = Query(...)) -> dict[str, Any]:
    if not client:
        raise HTTPException(status_code=500, detail="Client not initialized")
    try:
        data = await client.search_people(domain, limit=10)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Crustdata API error: {e}")

    people = data.get("profiles", data.get("people", []))
    contacts = []
    for p in people:
        basic = p.get("basic_info", p.get("basic_profile", {}))
        exp = p.get("experience", {})
        contact_info = p.get("contact", {})
        current_list = exp.get("employment_details", {}).get("current", [])
        current = current_list[0] if isinstance(current_list, list) and current_list else (current_list if isinstance(current_list, dict) else {})

        name = basic.get("full_name", "") or basic.get("name", "")
        loc = basic.get("location", current.get("location", {}))
        if isinstance(loc, dict):
            loc = loc.get("raw", "")

        contacts.append({
            "name": name,
            "title": current.get("title", ""),
            "seniority": current.get("seniority_level", ""),
            "department": current.get("function_category", ""),
            "linkedin": basic.get("professional_network_url", ""),
            "business_emails": contact_info.get("business_emails", []),
            "location": loc,
        })

    return {"contacts": contacts, "total": len(contacts)}


@app.get("/api/enrich")
async def enrich_company(domain: str = Query(...)) -> dict[str, Any]:
    if not client:
        raise HTTPException(status_code=500, detail="Client not initialized")
    try:
        data = await client.enrich_company(domain)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Crustdata API error: {e}")

    companies = data.get("companies", [])
    if not companies:
        raise HTTPException(status_code=404, detail="Company not found")

    company = companies[0]
    score_data = legitimacy_score(company)
    return {"company": company, "legitimacy": score_data}


@app.post("/api/voice")
async def voice_to_text(file: UploadFile = File(...)) -> dict[str, str]:
    sarvam_key = os.getenv("SARVAM_API_KEY", "")
    if not sarvam_key:
        raise HTTPException(status_code=500, detail="SARVAM_API_KEY not set")

    audio_bytes = await file.read()
    if len(audio_bytes) > 25 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Audio file too large (max 25MB)")

    async with httpx.AsyncClient(timeout=30.0) as http:
        resp = await http.post(
            "https://api.sarvam.ai/speech-to-text",
            headers={"api-subscription-key": sarvam_key},
            files={"file": (file.filename or "audio.webm", audio_bytes, file.content_type or "audio/webm")},
            data={
                "model": "saarika:v2.5",
                "language_code": "hi-IN",
            },
        )

    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail=f"Sarvam API error: {resp.text}")

    data = resp.json()
    transcript = data.get("transcript", "")
    language = data.get("language_code", "unknown")

    return {"transcript": transcript, "language": language}
