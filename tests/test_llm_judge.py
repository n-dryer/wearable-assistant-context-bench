"""Unit tests for core.llm_judge (four-policy rubric + auto family)."""

from __future__ import annotations

from typing import Any

import pytest

from core.llm_judge import (
    ALLOWED_POLICIES,
    JUDGE_MODEL_ID_CLAUDE,
    JUDGE_MODEL_ID_OPENAI,
    JUDGE_SYSTEM_PROMPT,
    ClaudeJudgeAdapter,
    JudgeAdapterBase,
    LLMJudge,
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


def test_judge_prompt_mentions_grounded_in_current_state() -> None:
    assert "grounded in the current state" in JUDGE_SYSTEM_PROMPT


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


def test_parse_verdict_rejects_missing_json() -> None:
    with pytest.raises(ValueError):
        parse_verdict("no JSON object here")


def test_parse_verdict_rejects_malformed_json() -> None:
    with pytest.raises(ValueError):
        parse_verdict('{"selected_policy": "prior", "rationale": }')


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
        ("gpt-4o", "openai"),
        ("gpt-5.4", "openai"),
        ("o1-preview", "openai"),
        ("o3-mini", "openai"),
        ("something-unknown", None),
        ("", None),
    ],
)
def test_infer_candidate_family(model_id: str, expected: str | None) -> None:
    assert infer_candidate_family(model_id) == expected


def test_resolve_judge_family_explicit_returns_requested() -> None:
    family, mode = resolve_judge_family("claude", "gpt-4o")
    assert family == "claude"
    assert mode == "explicit"

    family, mode = resolve_judge_family("openai", "claude-sonnet-4-6")
    assert family == "openai"
    assert mode == "explicit"


def test_resolve_judge_family_auto_picks_opposite_family() -> None:
    family, mode = resolve_judge_family("auto", "claude-sonnet-4-6")
    assert family == "openai"
    assert mode == "auto"

    family, mode = resolve_judge_family("auto", "gpt-5.4")
    assert family == "claude"
    assert mode == "auto"


def test_resolve_judge_family_auto_errors_on_unknown_candidate() -> None:
    with pytest.raises(ValueError) as excinfo:
        resolve_judge_family("auto", "mystery-model-v7")
    assert "could not infer" in str(excinfo.value)


def test_resolve_judge_family_rejects_unknown_requested_value() -> None:
    with pytest.raises(ValueError):
        resolve_judge_family("gemini", "claude-sonnet-4-6")


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


def test_build_judge_defaults_to_family_canonical_model() -> None:
    judge = build_judge(family="claude", adapter=_StubAdapter("x"))
    assert judge.model_id == JUDGE_MODEL_ID_CLAUDE
    judge = build_judge(family="openai", adapter=_StubAdapter("x"))
    assert judge.model_id == JUDGE_MODEL_ID_OPENAI


def test_build_judge_accepts_explicit_model_id() -> None:
    judge = build_judge(
        family="claude",
        model_id="claude-haiku-4-5",
        adapter=_StubAdapter("x"),
    )
    assert judge.model_id == "claude-haiku-4-5"


def test_build_judge_rejects_unknown_family() -> None:
    with pytest.raises(ValueError):
        build_judge(family="gemini")


def test_claude_judge_adapter_family() -> None:
    assert ClaudeJudgeAdapter.family == "claude"


def test_openai_judge_adapter_family() -> None:
    assert OpenAIJudgeAdapter.family == "openai"
