"""Unit tests for core.llm_judge label parsing and family selection."""

from __future__ import annotations

from typing import Any

import pytest

from core.llm_judge import (
    ALLOWED_POLICIES,
    JUDGE_MODEL_ID_CLAUDE,
    JUDGE_MODEL_ID_GEMINI,
    JUDGE_MODEL_ID_OPENAI,
    JUDGE_SYSTEM_PROMPT,
    GeminiJudgeAdapter,
    JudgeAdapterBase,
    LLMJudge,
    LiteLLMJudgeAdapter,
    OpenAIJudgeAdapter,
    build_judge,
    infer_candidate_family,
    parse_verdict,
    resolve_judge_family,
)


def test_judge_prompt_mentions_all_four_policies() -> None:
    for policy in ALLOWED_POLICIES:
        assert f"`{policy}`" in JUDGE_SYSTEM_PROMPT, (
            f"policy {policy!r} should appear in the judge rubric"
        )


def test_parse_verdict_extracts_current_policy() -> None:
    raw = (
        "reasoning...\n"
        '{"selected_policy": "current", "rationale": "reflects new scene."}'
    )
    verdict = parse_verdict(raw)
    assert verdict.selected_policy == "current"
    assert "reflects new scene" in verdict.rationale


def test_parse_verdict_accepts_all_four_policies() -> None:
    for policy in ALLOWED_POLICIES:
        raw = f'{{"selected_policy": "{policy}", "rationale": "ok"}}'
        assert parse_verdict(raw).selected_policy == policy


def test_parse_verdict_rejects_unknown_policy() -> None:
    raw = '{"selected_policy": "nonsense", "rationale": "ok"}'
    with pytest.raises(ValueError):
        parse_verdict(raw)


def test_parse_verdict_falls_back_to_abstain_when_no_json_or_label_line() -> None:
    """Verbose prose with no JSON block and no `selected_policy:` line
    falls back to abstain rather than guessing from a bare label word.

    This is the v1.1 hardening: the previous heuristic scanned for the
    last bare label word, which would flip on contrastive prose like
    "uses prior context but I will select current."
    """
    verdict = parse_verdict("no JSON object here, just bare prose")
    assert verdict.selected_policy == "abstain"
    assert "no-verdict" in verdict.rationale.lower() or "fallback" in verdict.rationale.lower()


def test_parse_verdict_does_not_flip_on_contrastive_prose() -> None:
    """Verbose prose mentioning multiple labels but no explicit verdict
    line falls back to abstain — the old heuristic would have returned
    whichever label appeared last."""
    raw = (
        "Reasoning: the response discusses prior context briefly, but "
        "ultimately grounds in the current frame.\n"
        "(no JSON block, no selected_policy line)"
    )
    verdict = parse_verdict(raw)
    assert verdict.selected_policy == "abstain"


def test_parse_verdict_recovers_from_explicit_label_line() -> None:
    """When the judge skips JSON but emits an explicit
    `selected_policy: current` line, the parser recovers it."""
    raw = (
        "Reasoning: the response describes the new frame.\n"
        "selected_policy: current"
    )
    verdict = parse_verdict(raw)
    assert verdict.selected_policy == "current"
    assert "recovered" in verdict.rationale.lower()


def test_parse_verdict_falls_back_on_malformed_json() -> None:
    """Malformed JSON inside a {...} block (e.g. stray escape) falls
    through to the strict label-line check; if neither produces a
    label, the parser returns abstain."""
    verdict = parse_verdict('{"selected_policy": "prior", "rationale": }')
    # No valid JSON, no explicit selected_policy line -> abstain.
    assert verdict.selected_policy == "abstain"


def test_parse_verdict_falls_back_to_abstain_when_malformed_json_lacks_label_word() -> None:
    """Malformed JSON with no recoverable label line returns abstain
    so the runner doesn't abort."""
    verdict = parse_verdict('{"selected_policy": , "rationale": }')
    assert verdict.selected_policy == "abstain"


def test_parse_verdict_takes_last_object_when_multiple_present() -> None:
    raw = (
        '{"selected_policy": "prior", "rationale": "first"}\n'
        '{"selected_policy": "current", "rationale": "second"}'
    )
    assert parse_verdict(raw).selected_policy == "current"


# --- Family inference and auto resolution ---------------------------------


@pytest.mark.parametrize(
    "model_id,expected",
    [
        ("claude-sonnet-4-6", "claude"),
        ("claude-opus-4-7", "claude"),
        ("claude-haiku-4-5", "claude"),
        ("Sonnet-4.6", "claude"),
        ("gemini-2.5-flash", "gemini"),
        ("gemini-2.5-pro", "gemini"),
        ("gemini-2.5-flash-lite", "gemini"),
        ("Gemini-2.5-Flash", "gemini"),
        ("openai/gpt-4.1-mini", "openai"),
        ("openrouter/openai/gpt-4.1-mini", "openai"),
        ("gpt-4.1-mini", "openai"),
        # HuggingFace Inference Providers routing.
        # Closed-family models served via HF route through to the closed family.
        ("huggingface/together/openai/gpt-oss-120b", "openai"),
        ("huggingface/fireworks-ai/openai/gpt-oss-20b", "openai"),
        # Open-weights candidates (Llama, Qwen, Mistral, etc.) return
        # None — caller must pass --judge-family explicitly.
        ("huggingface/together/Qwen/Qwen2.5-VL-7B-Instruct", None),
        ("huggingface/together/meta-llama/Llama-3.2-11B-Vision-Instruct", None),
        ("huggingface/fireworks-ai/Qwen/Qwen2.5-VL-72B-Instruct", None),
        ("something-unknown", None),
        ("", None),
    ],
)
def test_infer_candidate_family(model_id: str, expected: str | None) -> None:
    assert infer_candidate_family(model_id) == expected


def test_resolve_judge_family_auto_errors_for_open_hf_candidate() -> None:
    """Open-weights HF candidates must be paired with an explicit
    --judge-family, since the cross-family map only covers
    Claude/Gemini/OpenAI today."""
    with pytest.raises(ValueError, match="could not infer the candidate family"):
        resolve_judge_family(
            "auto",
            "huggingface/together/Qwen/Qwen2.5-VL-7B-Instruct",
        )


def test_resolve_judge_family_explicit_returns_requested() -> None:
    family, mode = resolve_judge_family("claude", "gemini-2.5-flash")
    assert family == "claude"
    assert mode == "explicit"

    family, mode = resolve_judge_family("gemini", "claude-sonnet-4-6")
    assert family == "gemini"
    assert mode == "explicit"

    family, mode = resolve_judge_family("openai", "gemini-2.5-flash")
    assert family == "openai"
    assert mode == "explicit"


def test_resolve_judge_family_auto_picks_opposite_family() -> None:
    family, mode = resolve_judge_family("auto", "claude-sonnet-4-6")
    assert family == "gemini"
    assert mode == "auto"

    family, mode = resolve_judge_family("auto", "gemini-2.5-flash")
    assert family == "openai"
    assert mode == "auto"

    family, mode = resolve_judge_family("auto", "openai/gpt-4.1-mini")
    assert family == "gemini"
    assert mode == "auto"


def test_resolve_judge_family_auto_errors_on_unknown_candidate() -> None:
    with pytest.raises(ValueError) as excinfo:
        resolve_judge_family("auto", "mystery-model-v7")
    assert "could not infer" in str(excinfo.value)


def test_resolve_judge_family_rejects_unknown_requested_value() -> None:
    with pytest.raises(ValueError):
        resolve_judge_family("mistral", "claude-sonnet-4-6")


# --- Judge adapter routing -----------------------------------------------


class _StubAdapter(JudgeAdapterBase):
    """Stub JudgeAdapter that returns canned judge text."""

    family = "stub"

    def __init__(self, canned: str) -> None:
        self.canned = canned
        self.calls: list[dict[str, Any]] = []

    def call(self, *, system: str, user: str, model_id: str) -> str:
        self.calls.append({"system": system, "user": user, "model_id": model_id})
        return self.canned


def test_judge_label_round_trips_through_stub_adapter() -> None:
    stub = _StubAdapter(
        '{"selected_policy": "prior", "rationale": "answered from earlier clips"}'
    )
    judge = LLMJudge(adapter=stub, model_id="stub-model")
    verdict = judge.label(
        response="I'll summarize the three clips from yesterday.",
        scenario_description="Turn 1 set up three uploaded clips.",
        turn_2_user="Tell me about my day yesterday.",
        current_answers=[],
        prior_answers=["art museum", "farmers market"],
        clarify_indicators=[],
        abstain_indicators=["don't have access"],
    )
    assert verdict.selected_policy == "prior"
    assert "earlier" in verdict.rationale
    assert len(stub.calls) == 1
    payload = stub.calls[0]["user"]
    assert "TURN 2 USER MESSAGE" in payload
    assert "CURRENT ANSWERS" in payload
    assert "PRIOR ANSWERS" in payload
    assert "CLARIFY INDICATORS" in payload
    assert "ABSTAIN INDICATORS" in payload


def test_build_judge_defaults_to_family_default_model() -> None:
    judge = build_judge(family="claude", adapter=_StubAdapter("x"))
    assert judge.model_id == JUDGE_MODEL_ID_CLAUDE
    judge = build_judge(family="gemini", adapter=_StubAdapter("x"))
    assert judge.model_id == JUDGE_MODEL_ID_GEMINI
    judge = build_judge(family="openai", adapter=_StubAdapter("x"))
    assert judge.model_id == JUDGE_MODEL_ID_OPENAI


def test_build_judge_accepts_explicit_model_id() -> None:
    judge = build_judge(
        family="claude",
        model_id="claude-haiku-4-5",
        adapter=_StubAdapter("x"),
    )
    assert judge.model_id == "claude-haiku-4-5"


@pytest.mark.parametrize(
    "family,model_id",
    [
        ("claude", "openrouter/anthropic/claude-3.5-haiku"),
        ("gemini", "openrouter/google/gemini-2.5-flash"),
    ],
)
def test_build_judge_uses_litellm_for_provider_qualified_models(
    family: str, model_id: str
) -> None:
    judge = build_judge(family=family, model_id=model_id)
    assert judge.model_id == model_id
    assert isinstance(judge._adapter, LiteLLMJudgeAdapter)
    assert judge.family == family


def test_build_judge_rejects_unknown_family() -> None:
    with pytest.raises(ValueError):
        build_judge(family="mistral")


def test_gemini_judge_adapter_family() -> None:
    assert GeminiJudgeAdapter.family == "gemini"


def test_openai_judge_adapter_family() -> None:
    assert OpenAIJudgeAdapter.family == "openai"


def test_litellm_judge_adapter_family_is_configurable() -> None:
    assert LiteLLMJudgeAdapter(family="claude").family == "claude"
