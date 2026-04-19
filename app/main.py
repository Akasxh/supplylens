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


DEPT_KEYWORDS: dict[str, list[str]] = {
    "Sales & Business Development": ["sales", "business development", "bd ", "account executive", "revenue"],
    "Procurement & Supply Chain": ["procurement", "purchasing", "supply chain", "sourcing", "buyer", "logistics"],
    "Engineering & R&D": ["engineer", "cto", "r&d", "research", "developer", "architect", "technical"],
    "Operations & Manufacturing": ["operations", "coo", "manufacturing", "production", "plant", "factory"],
    "Executive & Leadership": ["ceo", "founder", "co-founder", "president", "managing director", "owner"],
    "Finance": ["cfo", "finance", "accounting", "controller", "treasurer"],
    "Marketing": ["marketing", "cmo", "brand", "communications", "pr "],
    "Human Resources": ["hr", "people", "talent", "recruit", "chro"],
    "Product": ["product manager", "product owner", "cpo"],
    "Legal & Compliance": ["legal", "counsel", "compliance", "regulatory"],
}


def _infer_department(department: str, title: str) -> str:
    if department:
        return department
    t = (title or "").lower()
    for dept, keywords in DEPT_KEYWORDS.items():
        if any(k in t for k in keywords):
            return dept
    return "Other"


def _normalize_name_part(s: str) -> str:
    return "".join(ch for ch in s.lower() if ch.isalpha())


def _predict_emails(name: str, domain: str) -> list[str]:
    if not name or not domain:
        return []
    parts = [p for p in name.strip().split() if p]
    if len(parts) < 1:
        return []
    first = _normalize_name_part(parts[0])
    last = _normalize_name_part(parts[-1]) if len(parts) > 1 else ""
    if not first:
        return []
    patterns: list[str] = []
    if last:
        patterns.extend([
            f"{first}.{last}@{domain}",
            f"{first}{last}@{domain}",
            f"{first[0]}{last}@{domain}",
            f"{first}_{last}@{domain}",
            f"{first}-{last}@{domain}",
        ])
    patterns.append(f"{first}@{domain}")
    seen: list[str] = []
    for p in patterns:
        if p not in seen:
            seen.append(p)
    return seen[:5]


@app.get("/api/contacts")
async def get_contacts(domain: str = Query(...)) -> dict[str, Any]:
    if not client:
        raise HTTPException(status_code=500, detail="Client not initialized")
    try:
        data = await client.search_people(domain, limit=25)
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=502, detail=f"Crustdata API error {e.response.status_code}: {e.response.text[:300]}")
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Crustdata API error: {type(e).__name__}: {e}")

    people = data.get("profiles", data.get("people", []))
    contacts = []
    for p in people:
        basic = p.get("basic_profile", p.get("basic_info", {}))
        exp = p.get("experience", {})
        contact_info = p.get("contact", {})
        social = p.get("social_handles", {})
        edu = p.get("education", {})
        current_list = exp.get("employment_details", {}).get("current", [])
        current = current_list[0] if isinstance(current_list, list) and current_list else (current_list if isinstance(current_list, dict) else {})

        name = basic.get("name", "") or basic.get("full_name", "")
        loc = basic.get("location", current.get("location", {}))
        if isinstance(loc, dict):
            loc = loc.get("raw", "")

        linkedin = social.get("professional_network_identifier", {}).get("profile_url", "")

        title = current.get("title", "")
        raw_dept = current.get("function_category", "")
        department = _infer_department(raw_dept, title)
        business_emails = contact_info.get("business_emails", []) or []
        predicted = _predict_emails(name, domain) if not business_emails else []

        headline = basic.get("headline", "")
        schools = [s.get("school", "") for s in edu.get("schools", [])[:2] if s.get("school")]

        contacts.append({
            "name": name,
            "title": title,
            "headline": headline,
            "seniority": current.get("seniority_level", ""),
            "department": department,
            "linkedin": linkedin,
            "business_emails": business_emails,
            "predicted_emails": predicted,
            "location": loc,
            "education": schools,
            "profile_picture": basic.get("profile_picture_permalink", ""),
        })

    groups: dict[str, list[dict[str, Any]]] = {}
    for c in contacts:
        groups.setdefault(c["department"], []).append(c)

    dept_order = list(DEPT_KEYWORDS.keys()) + ["Other"]
    ordered = [{"department": d, "contacts": groups[d]} for d in dept_order if d in groups]
    for d in groups:
        if d not in dept_order:
            ordered.append({"department": d, "contacts": groups[d]})

    return {"contacts": contacts, "groups": ordered, "total": len(contacts)}


@app.get("/api/enrich")
async def enrich_company(domain: str = Query(...)) -> dict[str, Any]:
    if not client:
        raise HTTPException(status_code=500, detail="Client not initialized")
    try:
        data = await client.enrich_company(domain)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Crustdata API error: {e}")

    results = data if isinstance(data, list) else data.get("results", [])
    if not results or not results[0].get("matches"):
        raise HTTPException(status_code=404, detail="Company not found")

    company = results[0]["matches"][0].get("company_data", {})
    score_data = legitimacy_score(company)
    return {"company": company, "legitimacy": score_data}


class PersonEnrichRequest(BaseModel):
    profile_urls: list[str] | None = None
    emails: list[str] | None = None


@app.post("/api/person/enrich")
async def person_enrich(req: PersonEnrichRequest) -> dict[str, Any]:
    if not client:
        raise HTTPException(status_code=500, detail="Client not initialized")
    if not req.profile_urls and not req.emails:
        raise HTTPException(status_code=400, detail="Provide profile_urls or emails")
    try:
        data = await client.enrich_person(
            profile_urls=req.profile_urls,
            emails=req.emails,
        )
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=502, detail=f"Crustdata API error {e.response.status_code}: {e.response.text[:300]}")
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Crustdata API error: {type(e).__name__}: {e}")

    results = data if isinstance(data, list) else []
    people = []
    for r in results:
        for match in r.get("matches", []):
            pd = match.get("person_data", {})
            bp = pd.get("basic_profile", {})
            contact_info = pd.get("contact", {})
            exp = pd.get("experience", {})
            people.append({
                "name": bp.get("name", ""),
                "headline": bp.get("headline", ""),
                "location": bp.get("location", {}).get("raw", ""),
                "current_title": bp.get("current_title", ""),
                "business_emails": contact_info.get("business_emails", []),
                "phone_numbers": contact_info.get("phone_numbers", []),
                "experience": exp,
                "skills": pd.get("skills", {}),
                "education": pd.get("education", {}),
                "dev_platforms": pd.get("dev_platform_profiles", []),
                "confidence": match.get("confidence_score"),
            })
    return {"people": people, "total": len(people)}


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
                "language_code": "unknown",
            },
        )

    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail=f"Sarvam API error: {resp.text}")

    data = resp.json()
    transcript = data.get("transcript", "")
    language = data.get("language_code", "unknown")

    return {"transcript": transcript, "language": language}
