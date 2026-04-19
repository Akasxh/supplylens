from __future__ import annotations

import json
import logging
import os
from typing import Any

log = logging.getLogger(__name__)

_client = None
_available = True


def _get_client():
    global _client, _available
    if not _available:
        return None
    if _client is None:
        try:
            from google import genai
            _client = genai.Client(api_key=os.getenv("GEMINI_API_KEY", ""))
        except Exception:
            _available = False
            return None
    return _client


def _call_gemini(prompt: str) -> str | None:
    global _available
    client = _get_client()
    if not client:
        return None
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )
        return response.text.strip()
    except Exception as e:
        log.warning("Gemini API call failed: %s", e)
        if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
            _available = False
        return None


def _parse_json(text: str | None) -> dict[str, Any] | None:
    if not text:
        return None
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


INDUSTRY_MAP: dict[str, list[str]] = {
    "gpu": ["Semiconductor Manufacturing", "Computer Hardware"],
    "semiconductor": ["Semiconductor Manufacturing"],
    "chip": ["Semiconductor Manufacturing", "Computer Hardware"],
    "aerospace": ["Aviation and Aerospace Component Manufacturing", "Defense and Space Manufacturing"],
    "battery": ["Renewable Energy Semiconductor Manufacturing", "Electric Power Generation"],
    "optics": ["Appliances, Electrical, and Electronics Manufacturing"],
    "robotics": ["Automation Machinery Manufacturing", "Industrial Machinery Manufacturing"],
    "sensor": ["Appliances, Electrical, and Electronics Manufacturing", "Measuring and Control Instrument Manufacturing"],
    "motor": ["Motor Vehicle Manufacturing", "Industrial Machinery Manufacturing"],
    "pcb": ["Appliances, Electrical, and Electronics Manufacturing"],
    "circuit": ["Appliances, Electrical, and Electronics Manufacturing"],
    "solar": ["Renewable Energy Semiconductor Manufacturing", "Electric Power Generation"],
    "radar": ["Defense and Space Manufacturing"],
    "satellite": ["Defense and Space Manufacturing", "Telecommunications"],
    "drone": ["Aviation and Aerospace Component Manufacturing"],
    "lidar": ["Measuring and Control Instrument Manufacturing"],
    "composite": ["Plastics and Rubber Product Manufacturing"],
    "actuator": ["Industrial Machinery Manufacturing"],
    "valve": ["Industrial Machinery Manufacturing"],
    "pump": ["Industrial Machinery Manufacturing"],
    "laser": ["Appliances, Electrical, and Electronics Manufacturing"],
    "crystal": ["Semiconductor Manufacturing"],
    "wafer": ["Semiconductor Manufacturing"],
    "display": ["Appliances, Electrical, and Electronics Manufacturing"],
    "3d print": ["Industrial Machinery Manufacturing"],
    "cnc": ["Industrial Machinery Manufacturing", "Machinery Manufacturing"],
    "precision": ["Measuring and Control Instrument Manufacturing"],
}


def _local_parse(raw_query: str) -> dict[str, Any]:
    query_lower = raw_query.lower()
    terms: list[str] = []
    for keyword, industries in INDUSTRY_MAP.items():
        if keyword in query_lower:
            terms.extend(industries)

    if not terms:
        words = [w for w in raw_query.split() if len(w) > 3]
        terms = words[:3] if words else [raw_query]

    seen: list[str] = []
    for t in terms:
        if t not in seen:
            seen.append(t)

    return {
        "search_terms": seen[:5],
        "location_preference": None,
        "company_size": None,
        "summary": raw_query,
    }


async def parse_supply_query(raw_query: str) -> dict[str, Any]:
    prompt = f"""You are a supply chain search assistant. Given a user's natural language query about finding suppliers or parts, extract structured search parameters.

Return ONLY valid JSON with these fields:
- "search_terms": list of industry/product keywords to search (e.g., ["Semiconductor Manufacturing", "GPU", "NVIDIA"])
- "location_preference": string or null (e.g., "United States", "Asia", null)
- "company_size": string or null ("small", "medium", "large", null)
- "summary": one-line summary of what the user is looking for

User query: "{raw_query}"

JSON:"""

    result = _parse_json(_call_gemini(prompt))
    if result and "search_terms" in result:
        return result
    return _local_parse(raw_query)


async def analyze_supplier(company_data: dict[str, Any], user_need: str) -> dict[str, Any]:
    prompt = f"""You are a supply chain compliance and risk analyst. Analyze this potential supplier for someone who needs: "{user_need}"

Company data:
{json.dumps(company_data, indent=2, default=str)}

Provide a brief analysis as JSON with:
- "fit_score": 1-10 how well this company fits the need
- "fit_reasoning": one sentence why
- "compliance_flags": list of any concerns (empty if none)
- "outreach_suggestion": one sentence on how to approach this company
- "export_control_note": brief note on any export control considerations

JSON only:"""

    result = _parse_json(_call_gemini(prompt))
    if result:
        return result

    return _local_analyze(company_data, user_need)


def _local_analyze(company: dict[str, Any], user_need: str) -> dict[str, Any]:
    score = 5
    flags: list[str] = []
    year = company.get("year_founded")
    hc = company.get("headcount", 0)

    if year:
        try:
            age = 2026 - int(year)
            if age < 3:
                flags.append(f"Very young company (founded {year})")
                score -= 1
            elif age > 10:
                score += 1
        except ValueError:
            pass

    if hc and hc > 500:
        score += 1
    elif hc and hc < 20:
        flags.append("Very small company — verify capacity for order fulfillment")

    funding = company.get("funding_total_usd")
    if funding and funding > 50_000_000:
        score += 1

    score = max(1, min(10, score))

    return {
        "fit_score": score,
        "fit_reasoning": f"Based on company profile: {hc or 'unknown'} employees, founded {year or 'unknown'}.",
        "compliance_flags": flags,
        "outreach_suggestion": "Contact via LinkedIn or company website with a clear description of your requirements.",
        "export_control_note": "Review applicable export regulations (EAR/ITAR for US, EU dual-use regulation) before engaging.",
    }


def _build_company_context(company: dict[str, Any]) -> str:
    parts = []
    parts.append(f"Company: {company.get('name', 'Unknown')}")
    if company.get("domain"):
        parts.append(f"Website: {company['domain']}")
    if company.get("industries"):
        parts.append(f"Industries: {', '.join(company['industries'])}")
    if company.get("year_founded"):
        parts.append(f"Founded: {company['year_founded']} ({2026 - int(company['year_founded'])} years old)")
    if company.get("headcount"):
        parts.append(f"Employees: {company['headcount']:,}")
    if company.get("company_type"):
        parts.append(f"Type: {company['company_type']}")
    funding = company.get("funding_total_usd")
    if funding and funding > 0:
        parts.append(f"Total funding: ${funding / 1e6:.0f}M")
    if company.get("last_round_type"):
        parts.append(f"Last round: {company['last_round_type']}")
    loc = company.get("locations", {})
    if isinstance(loc, dict):
        hq = loc.get("headquarters") or loc.get("hq_country") or loc.get("country")
        if hq:
            parts.append(f"HQ: {hq}")
    legitimacy = company.get("legitimacy", {})
    if legitimacy:
        parts.append(f"Legitimacy score: {legitimacy.get('score', 'N/A')}/100 ({legitimacy.get('verdict', '')})")
    return "\n".join(parts)


def _build_contact_context(contact: dict[str, Any]) -> str:
    parts = []
    if contact.get("name"):
        parts.append(f"Name: {contact['name']}")
    if contact.get("title"):
        parts.append(f"Title: {contact['title']}")
    if contact.get("seniority"):
        parts.append(f"Seniority: {contact['seniority']}")
    if contact.get("department"):
        parts.append(f"Department: {contact['department']}")
    if contact.get("location"):
        parts.append(f"Location: {contact['location']}")
    return "\n".join(parts)


async def draft_outreach(
    company_name: str,
    contact_name: str,
    contact_title: str,
    user_need: str,
    company_context: dict[str, Any] | None = None,
    contact_context: dict[str, Any] | None = None,
) -> str:
    company_info = _build_company_context(company_context) if company_context else f"Company: {company_name}"
    contact_info = _build_contact_context(contact_context) if contact_context else f"Name: {contact_name}\nTitle: {contact_title}"

    prompt = f"""You are an expert at writing highly personalized cold outreach emails for supply chain partnerships.
Write a concise, compelling email that feels genuinely personal — not templated.

RULES:
- Reference specific details about the company (size, industry, funding stage, HQ location) to show you've done research
- Reference the contact's role/title to explain why you're reaching out to THEM specifically
- Mention YOUR specific need clearly and concisely
- If the company is large/established, acknowledge their market position
- If they're a startup, reference their growth trajectory or funding
- Keep it to 4-5 sentences max. No fluff, no "I hope this finds you well"
- End with a specific, low-friction ask (15-min call, quick reply, etc.)
- Tone: professional but human, like a peer reaching out to a peer
- Do NOT include a subject line, greeting name, or sign-off — just the body paragraphs

SENDER'S NEED: {user_need}

COMPANY INTELLIGENCE:
{company_info}

CONTACT INTELLIGENCE:
{contact_info}

Write the email body now:"""

    result = _call_gemini(prompt)
    if result:
        return result

    return _local_outreach(company_name, contact_name, contact_title, user_need, company_context)


def _local_outreach(
    company_name: str,
    contact_name: str,
    contact_title: str,
    user_need: str,
    company: dict[str, Any] | None = None,
) -> str:
    lines = [f"Dear {contact_name},"]

    if company:
        hc = company.get("headcount", 0)
        year = company.get("year_founded", "")
        industries = company.get("industries", [])
        funding = company.get("funding_total_usd", 0)
        loc = company.get("locations", {})
        hq = ""
        if isinstance(loc, dict):
            hq = loc.get("headquarters") or loc.get("hq_country") or loc.get("country") or ""

        industry_str = industries[0] if industries else "your industry"

        if hc and hc > 10000:
            lines.append(f"\n{company_name}'s scale in {industry_str} — with {hc:,} employees globally — makes you exactly the kind of partner we're looking for.")
        elif hc and hc > 1000:
            lines.append(f"\n{company_name}'s strong presence in {industry_str} caught our attention as we source critical components for our operations.")
        elif year and (2026 - int(year)) < 10 and funding and funding > 1_000_000:
            lines.append(f"\n{company_name}'s rapid growth since {year} — backed by ${funding/1e6:.0f}M in funding — signals exactly the kind of innovative partner we need.")
        else:
            lines.append(f"\n{company_name}'s work in {industry_str} aligns well with what we're building.")

        if contact_title:
            lines.append(f"As {contact_title}, you're the right person to discuss whether a supply partnership makes sense.")
    else:
        lines.append(f"\nI'm reaching out because {company_name}'s capabilities are closely aligned with our current sourcing needs.")

    lines.append(f"\nWe're specifically looking for {user_need}. We need a reliable partner who can deliver on quality, lead times, and scalability.")

    if company and company.get("headcount", 0) > 5000:
        lines.append("\nWould a 15-minute call next week work to explore whether there's a fit? Happy to share our detailed specifications upfront.")
    else:
        lines.append("\nCould you point me to the right person to discuss this, or would you be open to a quick call? I can share detailed specs immediately.")

    lines.append("\nBest regards")
    return "\n".join(lines)
