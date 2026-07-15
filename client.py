"""
SuperJob API client. Optional — only active if SUPERJOB_API_KEY is set in .env.
Docs: https://api.superjob.ru/
"""
from __future__ import annotations

import httpx
import structlog

from app.config.settings import settings

logger = structlog.get_logger(__name__)

SJ_BASE_URL = "https://api.superjob.ru/2.0"


class SuperJobClient:
    def __init__(self) -> None:
        self.enabled = bool(settings.superjob_api_key)
        self._client = httpx.AsyncClient(base_url=SJ_BASE_URL, timeout=20.0)

    async def close(self) -> None:
        await self._client.aclose()

    async def search_vacancies(self, keyword: str, town: str | None = None, payment_from: int | None = None) -> list[dict]:
        if not self.enabled:
            return []

        headers = {"X-Api-App-Id": settings.superjob_api_key}
        params: dict = {"keyword": keyword, "count": 50}
        if town:
            params["town"] = town
        if payment_from:
            params["payment_from"] = payment_from

        try:
            resp = await self._client.get("/vacancies/", headers=headers, params=params)
            resp.raise_for_status()
            return resp.json().get("objects", [])
        except httpx.HTTPError as exc:
            logger.error("superjob_search_failed", error=str(exc))
            return []


# NOTE on Avito Работа:
# Avito has no official public jobs API. Scraping their site programmatically
# is against their Terms of Service, so no scraper is included here. If you
# still want Avito listings, the safest approach is to manually browse and
# forward interesting links to yourself — this bot's LLM analyzer can still
# score/write a cover letter for a manually-pasted vacancy description
# (see app/llm/analyzer.py — it works on raw text, not just API results).
