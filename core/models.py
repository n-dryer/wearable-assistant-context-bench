"""Claude model adapter with multi-turn support and disk caching.

The adapter wraps the Anthropic Python SDK. It accepts a full message
history so 2-turn scenarios work: the runner calls query() for Turn 1,
appends the assistant response to its own messages list, and calls query()
again for Turn 2 with the extended history.

The adapter does not mutate the caller's messages list. It computes a
content hash of (messages, system, config) and caches responses to disk so
reruns are deterministic and free when the inputs are identical.

Model version pinning: the default model_id is the Claude Sonnet 4.6
family alias `claude-sonnet-4-6`. The Anthropic public docs at
https://docs.claude.com/en/api/overview do not currently expose a dated
snapshot ID for this model family that can be pinned without risking a
404. Callers that need strict reproducibility should override model_id
with an exact snapshot when one is available.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from anthropic import Anthropic


DEFAULT_MODEL_ID = "claude-sonnet-4-6"
DEFAULT_CACHE_DIR = Path(".cache/models")


@dataclass
class ModelConfig:
    """Configuration for a single model query.

    Attributes:
        model_id: Pinned model identifier. Defaults to claude-sonnet-4-6.
            The judge uses the same family; see core.llm_judge.
        temperature: Sampling temperature. Experiments use 0.0 for
            reproducibility.
        max_tokens: Upper bound on response length in tokens.
    """

    model_id: str = DEFAULT_MODEL_ID
    temperature: float = 0.0
    max_tokens: int = 1024


class ClaudeAdapter:
    """Thin wrapper around the Anthropic Messages API.

    The adapter is stateless between calls. Each query takes a full
    message history, a system prompt (the intervention), and a ModelConfig.
    Results are cached on disk keyed on a hash of all three so repeat
    queries with identical inputs do not hit the API.
    """

    def __init__(
        self,
        client: Any | None = None,
        cache_dir: Path | None = None,
    ) -> None:
        """Construct the adapter.

        Args:
            client: An Anthropic client instance. If None, a default client
                is constructed lazily on first use. Tests inject a mock
                here to avoid network calls.
            cache_dir: Directory for on-disk response cache. Defaults to
                .cache/models under the project root.
        """
        self._client = client
        self._cache_dir = cache_dir if cache_dir is not None else DEFAULT_CACHE_DIR

    @property
    def client(self) -> Any:
        """Return the Anthropic client, constructing it lazily."""
        if self._client is None:
            self._client = Anthropic()
        return self._client

    def _cache_key(
        self,
        messages: list[dict],
        system: str,
        config: ModelConfig,
    ) -> str:
        """Compute a stable hash over the inputs to the model call."""
        payload = {
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
        """Send a multi-turn message history to Claude and return the reply.

        Args:
            messages: Conversation history. Each entry must have keys
                "role" in {"user", "assistant"} and "content" as str. The
                list is copied before being sent to the API; the caller's
                list is not mutated.
            system: System prompt. In this project this is the intervention
                condition's system_prompt.
            config: ModelConfig controlling model_id, temperature, and
                max_tokens.

        Returns:
            The assistant response text as a single concatenated string.
        """
        cache_key = self._cache_key(messages, system, config)
        cached = self._load_cached(cache_key)
        if cached is not None:
            return cached

        response = self.client.messages.create(
            model=config.model_id,
            max_tokens=config.max_tokens,
            temperature=config.temperature,
            system=system,
            messages=list(messages),
        )

        text = _extract_text(response)
        self._store_cached(cache_key, text)
        return text


def _extract_text(response: Any) -> str:
    """Pull plain text out of an Anthropic Messages response object.

    Handles both SDK response objects (with a .content list of blocks) and
    plain dicts returned by test mocks.
    """
    content = getattr(response, "content", None)
    if content is None and isinstance(response, dict):
        content = response.get("content")

    if not content:
        return ""

    parts: list[str] = []
    for block in content:
        if isinstance(block, dict):
            if block.get("type") == "text":
                parts.append(block.get("text", ""))
        else:
            text = getattr(block, "text", None)
            if text is not None:
                parts.append(text)
    return "".join(parts)
