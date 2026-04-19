from __future__ import annotations

import httpx
from typing import Any

BASE_URL = "https://api.crustdata.com"
API_VERSION = "2025-11-01"


class CrustdataClient:
    def __init__(self, api_key: str) -> None:
        self._headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "x-api-version": API_VERSION,
        }
        self._client = httpx.AsyncClient(
            base_url=BASE_URL,
            headers=self._headers,
            timeout=60.0,
        )

    async def search_companies(
        self,
        query: str,
        *,
        limit: int = 20,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        filters: dict[str, Any] = {
            "op": "or",
            "conditions": [
                {"field": "basic_info.industries", "type": "(.)", "value": query},
                {"field": "basic_info.name", "type": "(.)", "value": query},
                {"field": "taxonomy.categories", "type": "(.)", "value": query},
            ],
        }
        body: dict[str, Any] = {
            "filters": filters,
            "limit": limit,
            "sorts": [{"column": "headcount.total", "order": "desc"}],
            "fields": [
                "basic_info",
                "headcount",
                "funding",
                "hiring",
                "locations",
                "taxonomy",
                "followers",
                "revenue",
            ],
        }
        if cursor:
            body["cursor"] = cursor
        resp = await self._client.post("/company/search", json=body)
        resp.raise_for_status()
        return resp.json()

    async def enrich_company(self, domain: str) -> list[dict[str, Any]]:
        body: dict[str, Any] = {
            "domains": [domain],
            "fields": [
                "basic_info",
                "headcount",
                "funding",
                "hiring",
                "web_traffic",
                "seo",
                "competitors",
                "employee_reviews",
                "people",
                "locations",
                "taxonomy",
                "followers",
                "news",
                "revenue",
                "software_reviews",
                "social_profiles",
                "status",
            ],
        }
        resp = await self._client.post("/company/enrich", json=body)
        resp.raise_for_status()
        return resp.json()

    async def search_people(
        self,
        company_domain: str,
        *,
        limit: int = 25,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {
            "filters": {
                "op": "and",
                "conditions": [
                    {
                        "field": "experience.employment_details.current.company_website_domain",
                        "type": "=",
                        "value": company_domain,
                    },
                ],
            },
            "limit": limit,
            "sorts": [{"field": "professional_network.connections", "order": "desc"}],
            "fields": [
                "basic_profile",
                "experience",
                "contact",
                "skills",
                "social_handles",
                "education",
            ],
        }
        resp = await self._client.post("/person/search", json=body)
        resp.raise_for_status()
        return resp.json()

    async def enrich_person(
        self,
        *,
        profile_urls: list[str] | None = None,
        emails: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        body: dict[str, Any] = {
            "fields": [
                "basic_profile",
                "experience",
                "contact",
                "skills",
                "education",
                "dev_platform_profiles",
            ],
        }
        if profile_urls:
            body["professional_network_profile_urls"] = profile_urls[:25]
        elif emails:
            body["business_emails"] = emails
        else:
            return []
        resp = await self._client.post("/person/enrich", json=body)
        resp.raise_for_status()
        return resp.json()

    async def web_search(self, query: str) -> dict[str, Any]:
        body: dict[str, Any] = {"query": query, "limit": 10}
        resp = await self._client.post("/web/search/live", json=body)
        resp.raise_for_status()
        return resp.json()

    async def close(self) -> None:
        await self._client.aclose()
