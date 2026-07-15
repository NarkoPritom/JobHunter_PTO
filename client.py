from __future__ import annotations

import json

import httpx
import structlog

from app.config.settings import settings

logger = structlog.get_logger(__name__)

ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"


class LLMClient:
    """Thin wrapper around the Anthropic Messages API."""

    def __init__(self) -> None:
        self._client = httpx.AsyncClient(
            headers={
                "x-api-key": settings.anthropic_api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            timeout=60.0,
        )

    async def close(self) -> None:
        await self._client.aclose()

    async def complete(self, system: str, user: str, max_tokens: int = 1000) -> str:
        payload = {
            "model": settings.anthropic_model,
            "max_tokens": max_tokens,
            "system": system,
            "messages": [{"role": "user", "content": user}],
        }
        resp = await self._client.post(ANTHROPIC_API_URL, json=payload)
        resp.raise_for_status()
        data = resp.json()
        text_blocks = [b["text"] for b in data.get("content", []) if b.get("type") == "text"]
        return "\n".join(text_blocks)

    async def complete_json(self, system: str, user: str, max_tokens: int = 1000) -> dict:
        raw = await self.complete(system, user, max_tokens=max_tokens)
        cleaned = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            logger.error("llm_json_parse_failed", raw=raw)
            return {}
