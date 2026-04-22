"""Unit tests for core.interventions."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.interventions import (
    InterventionCondition,
    get_intervention_by_name,
    load_interventions,
)


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "interventions_sample.json"
PROJECT_INTERVENTIONS = (
    Path(__file__).resolve().parent.parent
    / "benchmark"
    / "v1"
    / "interventions.json"
)


EXPECTED_BASELINE = (
    "You are an assistant helping a user with an ongoing project."
)

EXPECTED_CONDITION_A = (
    "You are an assistant helping a user with an ongoing project.\n"
    "The user's visual context may shift during the conversation - "
    "the assistant may see a new scene, a new object, or a new "
    "location between turns. Each question refers to one specific "
    "visual context: sometimes an earlier frame, sometimes the "
    "current frame. Before answering, decide which visual context "
    "the question actually refers to based on the wording, and "
    "answer from that context. Do not default to the most recent "
    "context if the question is clearly about an earlier one, and "
    "do not default to an earlier context if the question is "
    "clearly about the current one."
)

EXPECTED_CONDITION_B = (
    "You are an assistant helping a user with an ongoing project.\n\n"
    "Before answering any question, first decide which visual "
    "context the question refers to: the current frame (the one the "
    "user is showing you right now), or a prior frame (one from "
    "earlier in the conversation). Output a one-line summary naming "
    "the relevant context, then answer the question using only that "
    "context.\n\n"
    "Format your response exactly as:\n"
    "RELEVANT CONTEXT: [current | prior] - [one-line summary of "
    "which scene this answer is grounded in]\n"
    "ANSWER: [your answer]"
)


def test_load_interventions_from_valid_fixture() -> None:
    conditions = load_interventions(FIXTURE_PATH)
    assert len(conditions) == 3
    names = [c.name for c in conditions]
    assert names == ["baseline", "condition_a", "condition_b"]
    assert all(isinstance(c, InterventionCondition) for c in conditions)
    assert all(c.system_prompt for c in conditions)
    assert all(c.token_count > 0 for c in conditions)


def test_load_interventions_raises_on_malformed_json(tmp_path: Path) -> None:
    bad = tmp_path / "bad.json"
    bad.write_text("{ this is not valid json", encoding="utf-8")
    with pytest.raises(json.JSONDecodeError):
        load_interventions(bad)


def test_get_intervention_by_name_returns_correct_condition() -> None:
    conditions = load_interventions(FIXTURE_PATH)
    condition = get_intervention_by_name(conditions, "condition_a")
    assert condition.name == "condition_a"
    assert "visual context" in condition.system_prompt.lower()


def test_get_intervention_by_name_raises_on_unknown() -> None:
    conditions = load_interventions(FIXTURE_PATH)
    with pytest.raises(ValueError):
        get_intervention_by_name(conditions, "does_not_exist")


def test_project_interventions_json_loads_three_conditions() -> None:
    conditions = load_interventions(PROJECT_INTERVENTIONS)
    assert [c.name for c in conditions] == [
        "baseline",
        "condition_a",
        "condition_b",
    ]


def test_project_interventions_prompts_match_expected_text() -> None:
    """The JSON file is the canonical intervention source for v1."""
    conditions = load_interventions(PROJECT_INTERVENTIONS)
    by_name = {c.name: c.system_prompt for c in conditions}

    assert by_name["baseline"] == EXPECTED_BASELINE
    assert by_name["condition_a"] == EXPECTED_CONDITION_A
    assert by_name["condition_b"] == EXPECTED_CONDITION_B


def test_interventions_are_policy_neutral() -> None:
    """No condition should hard-code 'answer from the current state'."""
    conditions = load_interventions(PROJECT_INTERVENTIONS)
    forbidden_snippets = (
        "always answer based on the user's current state",
        "only that current state as your ground truth",
        "only that current state as ground truth",
    )
    for condition in conditions:
        lowered = condition.system_prompt.lower()
        for snippet in forbidden_snippets:
            assert snippet not in lowered, (
                f"{condition.name} contains policy-forcing snippet: "
                f"{snippet!r}"
            )
