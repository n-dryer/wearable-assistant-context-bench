"""OpenAI candidate-model adapter, parallel to `core.models.ClaudeAdapter`.

The adapter wraps the OpenAI Python SDK via the Chat Completions API. It
exposes the same `query(messages, system, config) -> str` interface as
`ClaudeAdapter` so the runner can route candidates to either backend by
family without changing the trial loop.

Behavior mirrors `ClaudeAdapter`:

- The adapter is stateless between calls.
- The caller's `messages` list is not mutated.
- Responses are cached on disk keyed on a SHA-256 hash of
  (messages, system, config), so repeat queries with identical inputs
  never hit the network.

The cache lives in `.cache/openai_models/` by default, separate from
the Claude cache, so that identical inputs against different backends
do not collide.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from core.models import ModelConfig


DEFAULT_OPENAI_CACHE_DIR = Path(".cache/openai_models")


class OpenAIAdapter:
    """Thin wrapper around the OpenAI Chat Completions API.

    The adapter keeps the same shape as `ClaudeAdapter`: a full message
    history plus a system prompt is translated into the Chat Completions
    `messages` array (system prompt prepended as the leading `system`
    message). Results are cached on disk keyed on a stable hash of the
    inputs.
    """

    def __init__(
        self,
        client: Any | None = None,
        cache_dir: Path | None = None,
    ) -> None:
        """Construct the adapter.

        Args:
            client: An OpenAI client instance. If None, a default client
                is constructed lazily on first use. Tests inject a mock
                here to avoid network calls.
            cache_dir: Directory for on-disk response cache. Defaults to
                `.cache/openai_models/` under the project root.
        """
        self._client = client
        self._cache_dir = (
            cache_dir if cache_dir is not None else DEFAULT_OPENAI_CACHE_DIR
        )

    @property
    def client(self) -> Any:
        """Return the OpenAI client, constructing it lazily."""
        if self._client is None:
            from openai import OpenAI

            self._client = OpenAI()
        return self._client

    def _cache_key(
        self,
        messages: list[dict],
        system: str,
        config: ModelConfig,
    ) -> str:
        """Compute a stable hash over the inputs to the model call."""
        payload = {
            "backend": "openai",
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
        """Send a multi-turn message history to OpenAI and return the reply.

        Args:
            messages: Conversation history. Each entry must have keys
                `"role"` in `{"user", "assistant"}` and `"content"` as
                str. The list is copied before being sent to the API; the
                caller's list is not mutated.
            system: System prompt. In this project this is the
                intervention condition's `system_prompt`. It is
                prepended as a leading `system` message in the Chat
                Completions payload.
            config: `ModelConfig` controlling `model_id`, `temperature`,
                and `max_tokens`.

        Returns:
            The assistant response text as a single string.
        """
        cache_key = self._cache_key(messages, system, config)
        cached = self._load_cached(cache_key)
        if cached is not None:
            return cached

        chat_messages: list[dict] = [{"role": "system", "content": system}]
        chat_messages.extend(list(messages))

        response = self.client.chat.completions.create(
            model=config.model_id,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            messages=chat_messages,
        )

        text = _extract_text(response)
        self._store_cached(cache_key, text)
        return text


def _extract_text(response: Any) -> str:
    """Pull plain text out of an OpenAI Chat Completions response object.

    Handles both SDK response objects (with `.choices[0].message.content`)
    and plain dicts returned by test mocks.
    """
    choices = getattr(response, "choices", None)
    if choices is None and isinstance(response, dict):
        choices = response.get("choices")
    if not choices:
        return ""

    first = choices[0]
    message = getattr(first, "message", None)
    if message is None and isinstance(first, dict):
        message = first.get("message")
    if message is None:
        return ""

    content = getattr(message, "content", None)
    if content is None and isinstance(message, dict):
        content = message.get("content")
    return content or ""
