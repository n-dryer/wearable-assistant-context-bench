"""Gemini candidate-model adapter.

Parallel to `core.openai_adapter.OpenAIAdapter` and
`core.models.ClaudeAdapter`. Wraps the `google-genai` SDK behind the
same `query(messages, system, config) -> str` interface so the runner
can route by family.

Smoke-test scaffold. Not part of the frozen v1 release surface.
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import asdict
from pathlib import Path
from typing import Any

from core.models import ModelConfig


DEFAULT_GEMINI_CACHE_DIR = Path(".cache/gemini_models")


def _resolve_api_key() -> str | None:
    for var in ("GEMINI_API_KEY", "GOOGLE_API_KEY", "GOOGLE_GENAI_API_KEY"):
        val = os.environ.get(var)
        if val:
            return val
    return None


class GeminiAdapter:
    """Thin wrapper around `google.genai` for candidate queries."""

    def __init__(
        self,
        client: Any | None = None,
        cache_dir: Path | None = None,
    ) -> None:
        self._client = client
        self._cache_dir = (
            cache_dir if cache_dir is not None else DEFAULT_GEMINI_CACHE_DIR
        )

    @property
    def client(self) -> Any:
        if self._client is None:
            from google import genai

            api_key = _resolve_api_key()
            self._client = genai.Client(api_key=api_key) if api_key else genai.Client()
        return self._client

    def _cache_key(
        self,
        messages: list[dict],
        system: str,
        config: ModelConfig,
    ) -> str:
        payload = {
            "backend": "gemini",
            "messages": messages,
            "system": system,
            "config": asdict(config),
        }
        serialized = json.dumps(payload, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def _cache_path(self, key: str) -> Path:
        return self._cache_dir / f"{key}.json"

    def _load_cached(self, key: str) -> str | None:
        path = self._cache_path(key)
        if not path.exists():
            return None
        with path.open("r", encoding="utf-8") as f:
            payload = json.load(f)
        cached = payload.get("response")
        return cached if cached else None

    def _store_cached(self, key: str, response: str) -> None:
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        with self._cache_path(key).open("w", encoding="utf-8") as f:
            json.dump({"response": response}, f, ensure_ascii=False)

    def query(
        self,
        messages: list[dict],
        system: str,
        config: ModelConfig,
    ) -> str:
        """Send multi-turn history to Gemini and return assistant text."""
        cache_key = self._cache_key(messages, system, config)
        cached = self._load_cached(cache_key)
        if cached is not None:
            return cached

        from google.genai import types as gtypes

        contents = []
        for m in messages:
            role = "model" if m["role"] == "assistant" else "user"
            contents.append(
                gtypes.Content(
                    role=role,
                    parts=[gtypes.Part.from_text(text=m["content"])],
                )
            )

        # Flash-lite does not reason, so thinking_budget=0 is safe and
        # cheap. Flash-2.5 and Pro use thinking internally; forcing
        # thinking off makes them leak reasoning into output tokens and
        # loop. Leave thinking at default for those and give them headroom
        # so the thinking pass plus the text payload both fit.
        extra: dict[str, Any] = {}
        model_lower = config.model_id.lower()
        is_flash_lite = "flash-lite" in model_lower
        if is_flash_lite:
            extra["thinking_config"] = gtypes.ThinkingConfig(thinking_budget=0)
            max_output = config.max_tokens
        else:
            max_output = max(config.max_tokens, 8192)
        gen_config = gtypes.GenerateContentConfig(
            system_instruction=system or None,
            temperature=config.temperature,
            max_output_tokens=max_output,
            **extra,
        )

        response = self.client.models.generate_content(
            model=config.model_id,
            contents=contents,
            config=gen_config,
        )

        text = _extract_text(response)
        if text:
            self._store_cached(cache_key, text)
        return text


def _extract_text(response: Any) -> str:
    text = getattr(response, "text", None)
    if text:
        return text
    candidates = getattr(response, "candidates", None) or []
    for c in candidates:
        content = getattr(c, "content", None)
        if content is None:
            continue
        parts = getattr(content, "parts", None) or []
        for p in parts:
            t = getattr(p, "text", None)
            if t:
                return t
    return ""
