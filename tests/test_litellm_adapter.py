"""Unit tests for the LiteLLM-backed adapter."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from core.litellm_adapter import LiteLLMAdapter
from core.models import ModelConfig


class _StubCompletion:
    """Callable stub that records completion kwargs and returns canned text."""

    def __init__(self, responses: list[str]) -> None:
        self._responses = list(responses)
        self.calls: list[dict[str, Any]] = []

    def __call__(self, **kwargs: Any) -> dict[str, Any]:
        self.calls.append(kwargs)
        text = self._responses.pop(0) if self._responses else ""
        return {"choices": [{"message": {"content": text}}]}


@pytest.fixture
def cache_dir(tmp_path: Path) -> Path:
    return tmp_path / "litellm-cache"


def test_query_returns_canned_text(cache_dir: Path) -> None:
    stub = _StubCompletion(["hello from litellm"])
    adapter = LiteLLMAdapter(client=stub, cache_dir=cache_dir)
    out = adapter.query(
        messages=[{"role": "user", "content": "hi"}],
        system="SYS",
        config=ModelConfig(model_id="openai/gpt-4.1-mini"),
    )
    assert out == "hello from litellm"
    assert len(stub.calls) == 1
    assert stub.calls[0]["model"] == "openai/gpt-4.1-mini"
    assert stub.calls[0]["timeout"] == 120


def test_repeat_call_hits_cache(cache_dir: Path) -> None:
    stub = _StubCompletion(["cached"])
    adapter = LiteLLMAdapter(client=stub, cache_dir=cache_dir)
    config = ModelConfig(model_id="openai/gpt-4.1-mini")
    messages = [{"role": "user", "content": "ping"}]
    first = adapter.query(messages=messages, system="SYS", config=config)
    second = adapter.query(messages=messages, system="SYS", config=config)
    assert first == "cached"
    assert second == "cached"
    assert len(stub.calls) == 1


def test_system_prompt_is_prepended_as_message(cache_dir: Path) -> None:
    stub = _StubCompletion(["x"])
    adapter = LiteLLMAdapter(client=stub, cache_dir=cache_dir)
    adapter.query(
        messages=[{"role": "user", "content": "hi"}],
        system="SYS",
        config=ModelConfig(model_id="openai/gpt-4.1-mini"),
    )
    assert stub.calls[0]["messages"][0] == {"role": "system", "content": "SYS"}
