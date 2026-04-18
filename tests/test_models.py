"""Unit tests for core.models.

These tests never hit the real Anthropic API. They inject a stub client
that records its calls and returns canned responses.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from core.models import ClaudeAdapter, ModelConfig


class _StubResponse:
    """Shape-compatible with an Anthropic Messages API response object."""

    def __init__(self, text: str) -> None:
        self.content = [{"type": "text", "text": text}]


class _StubClient:
    """Records calls and returns canned responses in FIFO order."""

    def __init__(self, responses: list[str]) -> None:
        self._responses = list(responses)
        self.calls: list[dict[str, Any]] = []
        self.messages = self  # API: client.messages.create(...)

    def create(self, **kwargs: Any) -> _StubResponse:
        self.calls.append(kwargs)
        text = self._responses.pop(0) if self._responses else ""
        return _StubResponse(text)


@pytest.fixture
def cache_dir(tmp_path: Path) -> Path:
    return tmp_path / "cache"


def test_multi_turn_history_passed_to_client(cache_dir: Path) -> None:
    stub = _StubClient(responses=["Turn 1 reply", "Turn 2 reply"])
    adapter = ClaudeAdapter(client=stub, cache_dir=cache_dir)
    config = ModelConfig()

    messages: list[dict] = [{"role": "user", "content": "Turn 1 question"}]
    turn1 = adapter.query(messages=messages, system="SYS", config=config)
    assert turn1 == "Turn 1 reply"

    messages.append({"role": "assistant", "content": turn1})
    messages.append({"role": "user", "content": "Turn 2 question"})

    turn2 = adapter.query(messages=messages, system="SYS", config=config)
    assert turn2 == "Turn 2 reply"

    assert len(stub.calls) == 2
    turn2_messages = stub.calls[1]["messages"]
    assert turn2_messages == [
        {"role": "user", "content": "Turn 1 question"},
        {"role": "assistant", "content": "Turn 1 reply"},
        {"role": "user", "content": "Turn 2 question"},
    ]


def test_cache_key_differs_when_messages_differ(cache_dir: Path) -> None:
    adapter = ClaudeAdapter(client=_StubClient([]), cache_dir=cache_dir)
    config = ModelConfig()
    key_a = adapter._cache_key(
        [{"role": "user", "content": "A"}], system="SYS", config=config
    )
    key_b = adapter._cache_key(
        [{"role": "user", "content": "B"}], system="SYS", config=config
    )
    assert key_a != key_b


def test_cache_key_differs_when_system_differs(cache_dir: Path) -> None:
    adapter = ClaudeAdapter(client=_StubClient([]), cache_dir=cache_dir)
    config = ModelConfig()
    messages = [{"role": "user", "content": "same"}]
    key_a = adapter._cache_key(messages, system="SYS-A", config=config)
    key_b = adapter._cache_key(messages, system="SYS-B", config=config)
    assert key_a != key_b


def test_repeat_call_hits_cache(cache_dir: Path) -> None:
    stub = _StubClient(responses=["cached reply"])
    adapter = ClaudeAdapter(client=stub, cache_dir=cache_dir)
    config = ModelConfig()
    messages = [{"role": "user", "content": "hello"}]

    first = adapter.query(messages=messages, system="SYS", config=config)
    second = adapter.query(messages=messages, system="SYS", config=config)

    assert first == "cached reply"
    assert second == "cached reply"
    assert len(stub.calls) == 1


def test_adapter_does_not_mutate_caller_messages(cache_dir: Path) -> None:
    stub = _StubClient(responses=["reply"])
    adapter = ClaudeAdapter(client=stub, cache_dir=cache_dir)
    messages = [{"role": "user", "content": "hello"}]
    snapshot = list(messages)
    adapter.query(messages=messages, system="SYS", config=ModelConfig())
    assert messages == snapshot
