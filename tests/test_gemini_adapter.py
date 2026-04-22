"""Unit tests for core.gemini_adapter.

These tests never hit the real Gemini API. They inject a stub client
that records its calls and returns canned responses.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from core.gemini_adapter import GeminiAdapter
from core.models import ModelConfig


class _StubResponse:
    """Shape-compatible with a `google.genai` GenerateContentResponse."""

    def __init__(self, text: str) -> None:
        self.text = text


class _StubModels:
    """Records `generate_content` calls and returns canned responses."""

    def __init__(self, responses: list[str]) -> None:
        self._responses = list(responses)
        self.calls: list[dict[str, Any]] = []

    def generate_content(self, **kwargs: Any) -> _StubResponse:
        self.calls.append(kwargs)
        text = self._responses.pop(0) if self._responses else ""
        return _StubResponse(text)


class _StubClient:
    """Mimics `genai.Client` with a `models.generate_content(...)` surface."""

    def __init__(self, responses: list[str]) -> None:
        self.models = _StubModels(responses)


@pytest.fixture
def cache_dir(tmp_path: Path) -> Path:
    return tmp_path / "gemini-cache"


def test_instantiates_without_api_call() -> None:
    adapter = GeminiAdapter(client=_StubClient([]))
    assert adapter._client is not None


def test_query_returns_canned_text(cache_dir: Path) -> None:
    stub = _StubClient(responses=["hello from gemini"])
    adapter = GeminiAdapter(client=stub, cache_dir=cache_dir)
    out = adapter.query(
        messages=[{"role": "user", "content": "hi"}],
        system="SYS",
        config=ModelConfig(model_id="gemini-2.5-flash"),
    )
    assert out == "hello from gemini"
    assert len(stub.models.calls) == 1
    assert stub.models.calls[0]["model"] == "gemini-2.5-flash"


def test_repeat_call_hits_cache(cache_dir: Path) -> None:
    stub = _StubClient(responses=["cached"])
    adapter = GeminiAdapter(client=stub, cache_dir=cache_dir)
    config = ModelConfig(model_id="gemini-2.5-flash")
    messages = [{"role": "user", "content": "ping"}]
    first = adapter.query(messages=messages, system="SYS", config=config)
    second = adapter.query(messages=messages, system="SYS", config=config)
    assert first == "cached"
    assert second == "cached"
    assert len(stub.models.calls) == 1


def test_flash_lite_disables_thinking(cache_dir: Path) -> None:
    stub = _StubClient(responses=["x"])
    adapter = GeminiAdapter(client=stub, cache_dir=cache_dir)
    adapter.query(
        messages=[{"role": "user", "content": "hi"}],
        system="SYS",
        config=ModelConfig(model_id="gemini-2.5-flash-lite", max_tokens=512),
    )
    gen_config = stub.models.calls[0]["config"]
    assert gen_config.thinking_config is not None
    assert gen_config.thinking_config.thinking_budget == 0


def test_non_flash_lite_uses_default_thinking_with_headroom(cache_dir: Path) -> None:
    stub = _StubClient(responses=["x"])
    adapter = GeminiAdapter(client=stub, cache_dir=cache_dir)
    adapter.query(
        messages=[{"role": "user", "content": "hi"}],
        system="SYS",
        config=ModelConfig(model_id="gemini-2.5-pro", max_tokens=512),
    )
    gen_config = stub.models.calls[0]["config"]
    assert gen_config.thinking_config is None
    assert gen_config.max_output_tokens >= 8192
