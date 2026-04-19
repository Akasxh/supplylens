from __future__ import annotations

from datetime import datetime
from typing import Any


def legitimacy_score(company: dict[str, Any]) -> dict[str, Any]:
    basic = company.get("basic_info", {})
    headcount = company.get("headcount", {})
    funding = company.get("funding", {})

    score = 0.0
    factors: list[dict[str, Any]] = []

    year_founded = basic.get("year_founded")
    if year_founded:
        age = datetime.now().year - int(str(year_founded)[:4])
        if age >= 10:
            score += 25
            factors.append({"name": "Company Age", "value": f"{age} years", "points": 25, "status": "strong"})
        elif age >= 5:
            score += 18
            factors.append({"name": "Company Age", "value": f"{age} years", "points": 18, "status": "moderate"})
        elif age >= 2:
            score += 10
            factors.append({"name": "Company Age", "value": f"{age} years", "points": 10, "status": "weak"})
        else:
            score += 3
            factors.append({"name": "Company Age", "value": f"{age} years", "points": 3, "status": "risk"})
    else:
        factors.append({"name": "Company Age", "value": "Unknown", "points": 0, "status": "unknown"})

    total_hc = headcount.get("total", 0)
    if total_hc >= 1000:
        score += 25
        factors.append({"name": "Employee Count", "value": f"{total_hc:,}", "points": 25, "status": "strong"})
    elif total_hc >= 200:
        score += 18
        factors.append({"name": "Employee Count", "value": f"{total_hc:,}", "points": 18, "status": "moderate"})
    elif total_hc >= 50:
        score += 10
        factors.append({"name": "Employee Count", "value": f"{total_hc:,}", "points": 10, "status": "weak"})
    elif total_hc > 0:
        score += 3
        factors.append({"name": "Employee Count", "value": f"{total_hc:,}", "points": 3, "status": "risk"})
    else:
        factors.append({"name": "Employee Count", "value": "Unknown", "points": 0, "status": "unknown"})

    total_funding = funding.get("total_investment_usd", 0)
    if total_funding and total_funding > 0:
        if total_funding >= 100_000_000:
            score += 20
            factors.append({"name": "Funding", "value": f"${total_funding / 1e6:.0f}M", "points": 20, "status": "strong"})
        elif total_funding >= 10_000_000:
            score += 15
            factors.append({"name": "Funding", "value": f"${total_funding / 1e6:.1f}M", "points": 15, "status": "moderate"})
        elif total_funding > 0:
            score += 8
            factors.append({"name": "Funding", "value": f"${total_funding / 1e6:.1f}M", "points": 8, "status": "weak"})
    else:
        factors.append({"name": "Funding", "value": "Undisclosed", "points": 0, "status": "unknown"})

    company_type = basic.get("company_type", "")
    if company_type == "Public Company":
        score += 15
        factors.append({"name": "Company Type", "value": "Public", "points": 15, "status": "strong"})
    elif company_type in ("Privately Held", "Partnership"):
        score += 8
        factors.append({"name": "Company Type", "value": company_type, "points": 8, "status": "moderate"})
    else:
        score += 3
        factors.append({"name": "Company Type", "value": company_type or "Unknown", "points": 3, "status": "weak"})

    website = basic.get("website", "")
    linkedin = basic.get("professional_network_url", "")
    if website and linkedin:
        score += 15
        factors.append({"name": "Web Presence", "value": "Website + LinkedIn", "points": 15, "status": "strong"})
    elif website or linkedin:
        score += 8
        factors.append({"name": "Web Presence", "value": "Partial", "points": 8, "status": "moderate"})
    else:
        factors.append({"name": "Web Presence", "value": "None", "points": 0, "status": "risk"})

    max_score = 100
    normalized = min(round(score / max_score * 100), 100)

    if normalized >= 75:
        verdict = "High Confidence"
    elif normalized >= 50:
        verdict = "Moderate Confidence"
    elif normalized >= 25:
        verdict = "Low Confidence"
    else:
        verdict = "Insufficient Data"

    return {
        "score": normalized,
        "verdict": verdict,
        "factors": factors,
    }
