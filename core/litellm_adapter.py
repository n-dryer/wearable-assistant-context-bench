"""LiteLLM-backed adapter for provider-qualified candidate and judge models.

This adapter keeps the same `query(messages, system, config) -> str`
interface used by the existing native adapters while routing calls
through LiteLLM's unified completion API. It is used for broader
provider coverage, including OpenAI, OpenRouter, and Hugging Face
Inference-backed chat-completion models.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any, Callable

from core.models import ModelConfig


DEFAULT_LITELLM_CACHE_DIR = Path(".cache/litellm_models")
DEFAULT_LITELLM_TIMEOUT_SECONDS = 120


class LiteLLMAdapter:
    """Thin cached wrapper around `litellm.completion`."""

    def __init__(
        self,
        client: Callable[..., Any] | None = None,
        cache_dir: Path | None = None,
    ) -> None:
        self._client = client
        self._cache_dir = (
            cache_dir if cache_dir is not None else DEFAULT_LITELLM_CACHE_DIR
        )

    @property
    def client(self) -> Callable[..., Any]:
        if self._client is None:
            from litellm import completion

            self._client = completion
        return self._client

    def _cache_key(
        self,
        messages: list[dict],
        system: str,
        config: ModelConfig,
    ) -> str:
        payload = {
            "backend": "litellm",
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
        return payload.get("response")

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
        """Send a multi-turn message history through LiteLLM."""
        cache_key = self._cache_key(messages, system, config)
        cached = self._load_cached(cache_key)
        if cached is not None:
            return cached

        payload_messages = list(messages)
        if system:
            payload_messages = [
                {"role": "system", "content": system},
                *payload_messages,
            ]

        response = self.client(
            model=config.model_id,
            messages=payload_messages,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            timeout=DEFAULT_LITELLM_TIMEOUT_SECONDS,
            stream=False,
        )

        text = _extract_text(response)
        self._store_cached(cache_key, text)
        return text


def _extract_text(response: Any) -> str:
    """Pull plain text from a LiteLLM/OpenAI-style chat response."""
    choices = getattr(response, "choices", None)
    if choices is None and isinstance(response, dict):
        choices = response.get("choices")
    if not choices:
        return ""

    first = choices[0]
    message = None
    if isinstance(first, dict):
        message = first.get("message") or first.get("delta")
    else:
        message = getattr(first, "message", None) or getattr(first, "delta", None)
    if message is None:
        return ""

    content = message.get("content") if isinstance(message, dict) else getattr(
        message, "content", None
    )
    return _normalize_content(content)


def _normalize_content(content: Any) -> str:
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, dict):
                if item.get("type") == "text":
                    parts.append(str(item.get("text", "")))
                    continue
                if "text" in item:
                    parts.append(str(item.get("text", "")))
                    continue
            text = getattr(item, "text", None)
            if text is not None:
                parts.append(str(text))
        return "".join(parts)
    return str(content)
