"""Async HTTP client for the Ollama REST API."""

from __future__ import annotations

from typing import AsyncIterator

import httpx

from app.core.config import settings


class OllamaClient:
    """Thin async wrapper around Ollama's /api/generate and /api/chat endpoints."""

    def __init__(self, base_url: str | None = None, model: str | None = None) -> None:
        self._base_url = (base_url or settings.ollama_base_url).rstrip("/")
        self._model = model or settings.ollama_model
        self._http = httpx.AsyncClient(base_url=self._base_url, timeout=120.0)

    # ── lifecycle ───────────────────────────────────────────────────

    async def close(self) -> None:
        await self._http.aclose()

    # ── health ──────────────────────────────────────────────────────

    async def is_reachable(self) -> bool:
        try:
            resp = await self._http.get("/api/tags")
            return resp.status_code == 200
        except httpx.HTTPError:
            return False

    async def list_models(self) -> list[str]:
        try:
            resp = await self._http.get("/api/tags")
            resp.raise_for_status()
            data = resp.json()
            return [m["name"] for m in data.get("models", [])]
        except httpx.HTTPError:
            return []

    # ── generation ──────────────────────────────────────────────────

    async def generate(
        self,
        prompt: str,
        *,
        system: str = "",
        temperature: float | None = None,
        model: str | None = None,
    ) -> str:
        """Non-streaming text generation. Returns the full response string."""
        payload: dict = {
            "model": model or self._model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature if temperature is not None else settings.temperature,
            },
        }
        if system:
            payload["system"] = system

        resp = await self._http.post("/api/generate", json=payload)
        resp.raise_for_status()
        return resp.json().get("response", "")

    async def chat(
        self,
        messages: list[dict[str, str]],
        *,
        temperature: float | None = None,
        model: str | None = None,
    ) -> str:
        """Chat-style completion (non-streaming). Messages are [{role, content}]."""
        payload: dict = {
            "model": model or self._model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature if temperature is not None else settings.temperature,
            },
        }
        resp = await self._http.post("/api/chat", json=payload)
        resp.raise_for_status()
        return resp.json().get("message", {}).get("content", "")

    async def generate_stream(
        self,
        prompt: str,
        *,
        system: str = "",
        temperature: float | None = None,
        model: str | None = None,
    ) -> AsyncIterator[str]:
        """Streaming text generation — yields token chunks."""
        payload: dict = {
            "model": model or self._model,
            "prompt": prompt,
            "stream": True,
            "options": {
                "temperature": temperature if temperature is not None else settings.temperature,
            },
        }
        if system:
            payload["system"] = system

        async with self._http.stream("POST", "/api/generate", json=payload) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if line:
                    import json
                    chunk = json.loads(line)
                    token = chunk.get("response", "")
                    if token:
                        yield token
