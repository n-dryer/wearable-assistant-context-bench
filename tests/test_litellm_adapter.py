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


class _FlakyCompletion:
    """Stub that raises a sequence of transient errors before succeeding."""

    def __init__(
        self, errors: list[Exception], final_text: str = "ok-after-retries"
    ) -> None:
        self._errors = list(errors)
        self._final_text = final_text
        self.calls: list[dict[str, Any]] = []

    def __call__(self, **kwargs: Any) -> dict[str, Any]:
        self.calls.append(kwargs)
        if self._errors:
            raise self._errors.pop(0)
        return {"choices": [{"message": {"content": self._final_text}}]}


def test_retry_on_transient_503(cache_dir: Path, monkeypatch) -> None:
    """LiteLLM service-unavailable errors are retried with backoff."""
    # Skip the actual sleeps so the test runs fast.
    import core.litellm_adapter as la
    monkeypatch.setattr(la.time, "sleep", lambda *_: None)

    flaky = _FlakyCompletion(
        errors=[Exception("503 UNAVAILABLE: high demand"),
                Exception("RateLimitError: rate limit exceeded")]
    )
    adapter = LiteLLMAdapter(client=flaky, cache_dir=cache_dir)
    out = adapter.query(
        messages=[{"role": "user", "content": "ping"}],
        system="SYS",
        config=ModelConfig(model_id="gemini/gemini-2.5-flash-lite"),
    )
    assert out == "ok-after-retries"
    assert len(flaky.calls) == 3  # two retries + the final success


def test_no_retry_on_auth_error(cache_dir: Path, monkeypatch) -> None:
    """Non-transient errors (auth, model-not-found) re-raise immediately."""
    import core.litellm_adapter as la
    monkeypatch.setattr(la.time, "sleep", lambda *_: None)

    class _Boom:
        def __init__(self) -> None:
            self.calls = 0

        def __call__(self, **kwargs: Any) -> Any:
            self.calls += 1
            raise Exception("AuthenticationError: invalid api key")

    boom = _Boom()
    adapter = LiteLLMAdapter(client=boom, cache_dir=cache_dir)
    with pytest.raises(Exception, match="invalid api key"):
        adapter.query(
            messages=[{"role": "user", "content": "ping"}],
            system="SYS",
            config=ModelConfig(model_id="openai/gpt-4o-mini"),
        )
    assert boom.calls == 1  # never retried


def test_dashscope_intl_prefix_rewrites_to_openai_with_api_base(
    cache_dir: Path, monkeypatch
) -> None:
    """``dashscope-intl/<model>`` rewrites to ``openai/<model>`` and
    sets ``api_base`` + ``api_key`` for the Singapore-region endpoint."""
    monkeypatch.setenv("DASHSCOPE_API_KEY", "sk-test-key-12345")
    stub = _StubCompletion(["routed"])
    adapter = LiteLLMAdapter(client=stub, cache_dir=cache_dir)
    out = adapter.query(
        messages=[{"role": "user", "content": "ping"}],
        system="SYS",
        config=ModelConfig(model_id="dashscope-intl/qwen3-vl-plus"),
    )
    assert out == "routed"
    call = stub.calls[0]
    assert call["model"] == "openai/qwen3-vl-plus"
    assert call["api_base"] == (
        "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
    )
    assert call["api_key"] == "sk-test-key-12345"


def test_dashscope_intl_prefix_errors_when_key_missing(
    cache_dir: Path, monkeypatch
) -> None:
    monkeypatch.delenv("DASHSCOPE_API_KEY", raising=False)
    stub = _StubCompletion(["unused"])
    adapter = LiteLLMAdapter(client=stub, cache_dir=cache_dir)
    with pytest.raises(RuntimeError, match="DASHSCOPE_API_KEY"):
        adapter.query(
            messages=[{"role": "user", "content": "ping"}],
            system="SYS",
            config=ModelConfig(model_id="dashscope-intl/qwen3-vl-plus"),
        )
    assert len(stub.calls) == 0  # never called the client


def test_retry_exhausted_reraises_last(cache_dir: Path, monkeypatch) -> None:
    """When all retry attempts hit transient errors, the last exception
    propagates."""
    import core.litellm_adapter as la
    monkeypatch.setattr(la.time, "sleep", lambda *_: None)

    flaky = _FlakyCompletion(
        errors=[Exception(f"503 UNAVAILABLE attempt {i}") for i in range(10)]
    )
    adapter = LiteLLMAdapter(client=flaky, cache_dir=cache_dir)
    with pytest.raises(Exception, match="503 UNAVAILABLE"):
        adapter.query(
            messages=[{"role": "user", "content": "ping"}],
            system="SYS",
            config=ModelConfig(model_id="gemini/gemini-2.5-flash-lite"),
        )
    # 4 attempts (DEFAULT_LITELLM_RETRY_ATTEMPTS).
    assert len(flaky.calls) == 4


@pytest.mark.parametrize(
    "model_id",
    [
        # HF Inference Providers — closed-family (open-weights served via HF).
        "huggingface/together/openai/gpt-oss-120b",
        # HF Inference Providers — open-weights multimodal candidates.
        "huggingface/together/Qwen/Qwen2.5-VL-7B-Instruct",
        "huggingface/together/meta-llama/Llama-3.2-11B-Vision-Instruct",
        "huggingface/fireworks-ai/Qwen/Qwen2.5-VL-72B-Instruct",
    ],
)
def test_huggingface_inference_providers_model_id_passes_through(
    cache_dir: Path, model_id: str
) -> None:
    """LiteLLM accepts ``huggingface/<provider>/<org>/<model>`` ids and
    routes them to HF Inference Providers using the ``HF_TOKEN`` env var.

    This smoke test verifies the adapter passes the model_id through
    to the litellm client unchanged — the actual HTTP routing is
    LiteLLM's responsibility. We don't fire a real API call; the stub
    records the kwargs and we assert the model id round-trips.
    """
    stub = _StubCompletion(["ok"])
    adapter = LiteLLMAdapter(client=stub, cache_dir=cache_dir)
    out = adapter.query(
        messages=[{"role": "user", "content": "ping"}],
        system="SYS",
        config=ModelConfig(model_id=model_id),
    )
    assert out == "ok"
    assert stub.calls[0]["model"] == model_id
