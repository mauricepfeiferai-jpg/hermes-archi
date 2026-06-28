"""Ollama client — minimal async wrapper around Ollama's REST API.

Used by Jarvis (reasoning + embedding) and Harvey (deep reasoning).
"""

from __future__ import annotations

import json
import os
from typing import AsyncIterator

import httpx


class OllamaClient:
    def __init__(self, base_url: str | None = None, timeout: float = 120.0):
        self.base_url = (base_url or os.getenv("OLLAMA_URL", "http://localhost:11434")).rstrip("/")
        self.timeout = timeout

    async def generate(self, model: str, prompt: str, system: str | None = None,
                       temperature: float = 0.7, max_tokens: int = 2048) -> str:
        """Single-shot non-streaming generation."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r = await client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "system": system,
                    "stream": False,
                    "options": {"temperature": temperature, "num_predict": max_tokens},
                },
            )
            r.raise_for_status()
            return r.json().get("response", "")

    async def chat(self, model: str, messages: list[dict], temperature: float = 0.7) -> str:
        """Chat completion (system + user/assistant turns)."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r = await client.post(
                f"{self.base_url}/api/chat",
                json={"model": model, "messages": messages, "stream": False,
                      "options": {"temperature": temperature}},
            )
            r.raise_for_status()
            return r.json().get("message", {}).get("content", "")

    async def stream_chat(self, model: str, messages: list[dict]) -> AsyncIterator[str]:
        """Streaming chat for low-latency UI."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            async with client.stream(
                "POST", f"{self.base_url}/api/chat",
                json={"model": model, "messages": messages, "stream": True},
            ) as r:
                async for line in r.aiter_lines():
                    if not line.strip():
                        continue
                    try:
                        chunk = json.loads(line)
                        yield chunk.get("message", {}).get("content", "")
                    except json.JSONDecodeError:
                        continue

    async def embed(self, model: str, text: str) -> list[float]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r = await client.post(
                f"{self.base_url}/api/embeddings",
                json={"model": model, "prompt": text},
            )
            r.raise_for_status()
            return r.json().get("embedding", [])

    async def list_models(self) -> list[str]:
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                r = await client.get(f"{self.base_url}/api/tags")
                if r.status_code == 200:
                    return [m["name"] for m in r.json().get("models", [])]
            except Exception:
                pass
            return []
