"""Schema checks for benchmark/v1/scenarios.json (v2 schema).

These tests treat the benchmark JSON files as the only active source of
truth for scenario configuration. They enforce v2 field requirements,
enum constraints, and the answer-set contract from `docs/schema.md`.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parent.parent
SCENARIOS_PATH = REPO_ROOT / "benchmark" / "v1" / "scenarios.json"
EXPECTED_ANSWERS_PATH = REPO_ROOT / "benchmark" / "v1" / "expected_answers.json"


REQUIRED_V2_FIELDS = {
    "scenario_id",
    "target_context",
    "cue_type",
    "activity_domain",
    "cognitive_load",
    "difficulty_tier",
    "context_image",
    "turn_1_image",
    "turn_1_user",
    "turn_2_image",
    "turn_2_user",
    "turn_3_repair_anchor",
}
OPTIONAL_FIELDS = {"time_gap_bucket", "notes"}

ALLOWED_TARGET_CONTEXTS = {"current", "prior", "clarify", "abstain"}
ALLOWED_CUE_TYPES = {
    "object_in_hand",
    "object_state",
    "sequential_task",
    "location",
    "object_in_view",
    "absent_referent",
    "screen_content",
    "pre_conversation_recall",
}
ALLOWED_DIFFICULTIES = {"easy", "medium", "hard"}
ALLOWED_COGNITIVE_LOADS = {
    "single_referent",
    "multi_referent",
    "distractor_present",
    "absent_referent",
    "compound_shift",
}

SCENARIO_ID_PATTERN = re.compile(r"^sc-\d{2}$")


@pytest.fixture(scope="module")
def scenarios() -> list[dict]:
    return json.loads(SCENARIOS_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def expected_answers() -> dict:
    return json.loads(EXPECTED_ANSWERS_PATH.read_text(encoding="utf-8"))


def test_scenarios_json_is_non_empty_list(scenarios: list[dict]) -> None:
    assert isinstance(scenarios, list)
    assert len(scenarios) > 0


def test_every_scenario_has_required_v2_fields(scenarios: list[dict]) -> None:
    for entry in scenarios:
        missing = REQUIRED_V2_FIELDS - entry.keys()
        assert not missing, (
            f"scenario {entry.get('scenario_id')!r} missing fields: {missing}"
        )


def test_scenario_ids_are_unique(scenarios: list[dict]) -> None:
    ids = [entry["scenario_id"] for entry in scenarios]
    assert len(ids) == len(set(ids))


def test_scenario_ids_follow_sc_nn_format(scenarios: list[dict]) -> None:
    for entry in scenarios:
        sid = entry["scenario_id"]
        assert SCENARIO_ID_PATTERN.match(sid), (
            f"scenario_id {sid!r} does not match `sc-NN` format"
        )


def test_target_contexts_in_allowed_set(scenarios: list[dict]) -> None:
    for entry in scenarios:
        assert entry["target_context"] in ALLOWED_TARGET_CONTEXTS, (
            f"{entry['scenario_id']}: unexpected target_context "
            f"{entry['target_context']!r}"
        )


def test_cue_types_in_allowed_set(scenarios: list[dict]) -> None:
    for entry in scenarios:
        assert entry["cue_type"] in ALLOWED_CUE_TYPES, (
            f"{entry['scenario_id']}: unexpected cue_type "
            f"{entry['cue_type']!r}"
        )


def test_difficulty_tiers_in_allowed_set(scenarios: list[dict]) -> None:
    for entry in scenarios:
        assert entry["difficulty_tier"] in ALLOWED_DIFFICULTIES, (
            f"{entry['scenario_id']}: unexpected difficulty_tier "
            f"{entry['difficulty_tier']!r}"
        )


def test_cognitive_loads_in_allowed_set(scenarios: list[dict]) -> None:
    for entry in scenarios:
        assert entry["cognitive_load"] in ALLOWED_COGNITIVE_LOADS, (
            f"{entry['scenario_id']}: unexpected cognitive_load "
            f"{entry['cognitive_load']!r}"
        )


def test_required_v2_string_fields_are_non_empty(scenarios: list[dict]) -> None:
    """Required string fields (excluding nullable context_image) must be non-empty strings."""
    for entry in scenarios:
        sid = entry["scenario_id"]
        for field_name in (
            "turn_1_image",
            "turn_1_user",
            "turn_2_image",
            "turn_2_user",
            "turn_3_repair_anchor",
            "activity_domain",
        ):
            value = entry[field_name]
            assert isinstance(value, str) and value, (
                f"{sid}.{field_name}: must be a non-empty string"
            )


def test_context_image_is_string_or_null(scenarios: list[dict]) -> None:
    for entry in scenarios:
        value = entry["context_image"]
        assert value is None or isinstance(value, str), (
            f"{entry['scenario_id']}.context_image: must be null or str, "
            f"got {type(value).__name__}"
        )


def test_pre_conversation_recall_has_context_image(scenarios: list[dict]) -> None:
    """Pre-conversation-recall scenarios must have a non-null context_image."""
    for entry in scenarios:
        if entry["cue_type"] != "pre_conversation_recall":
            continue
        sid = entry["scenario_id"]
        assert entry["context_image"], (
            f"{sid}: pre_conversation_recall scenarios must have a non-null "
            f"context_image populated"
        )
        assert isinstance(entry["context_image"], str) and entry["context_image"].strip(), (
            f"{sid}: context_image must be a non-empty string"
        )


def test_every_scenario_has_answer_set(
    scenarios: list[dict], expected_answers: dict
) -> None:
    for entry in scenarios:
        sid = entry["scenario_id"]
        assert sid in expected_answers, f"{sid}: missing expected_answers entry"
        ans = expected_answers[sid]
        for key in (
            "current_answers",
            "prior_answers",
            "clarify_indicators",
            "abstain_indicators",
        ):
            assert key in ans, f"{sid}: missing answer-set key {key!r}"
            assert isinstance(ans[key], list), f"{sid}.{key}: must be a list"


def test_current_target_has_three_plus_current_answers(
    scenarios: list[dict], expected_answers: dict
) -> None:
    """Three-category vocabulary requirement: current scenarios need 3+ current_answers tokens."""
    for entry in scenarios:
        if entry["target_context"] != "current":
            continue
        sid = entry["scenario_id"]
        ans = expected_answers[sid]
        assert len(ans["current_answers"]) >= 3, (
            f"{sid}: target_context=current requires 3+ items in current_answers "
            f"(object name + technique + state); got {len(ans['current_answers'])}"
        )


def test_prior_target_has_three_plus_prior_answers(
    scenarios: list[dict], expected_answers: dict
) -> None:
    """Three-category vocabulary requirement: prior scenarios need 3+ prior_answers tokens."""
    for entry in scenarios:
        if entry["target_context"] != "prior":
            continue
        sid = entry["scenario_id"]
        ans = expected_answers[sid]
        assert len(ans["prior_answers"]) >= 3, (
            f"{sid}: target_context=prior requires 3+ items in prior_answers "
            f"(object name + technique + state); got {len(ans['prior_answers'])}"
        )


def test_clarify_target_has_clarify_indicators(
    scenarios: list[dict], expected_answers: dict
) -> None:
    for entry in scenarios:
        if entry["target_context"] != "clarify":
            continue
        sid = entry["scenario_id"]
        ans = expected_answers[sid]
        assert ans["clarify_indicators"], (
            f"{sid}: target_context=clarify requires non-empty clarify_indicators"
        )


def test_abstain_target_has_abstain_indicators(
    scenarios: list[dict], expected_answers: dict
) -> None:
    for entry in scenarios:
        if entry["target_context"] != "abstain":
            continue
        sid = entry["scenario_id"]
        ans = expected_answers[sid]
        assert ans["abstain_indicators"], (
            f"{sid}: target_context=abstain requires non-empty abstain_indicators"
        )


def test_canonical_v1_composition_includes_all_four_contexts(
    scenarios: list[dict],
) -> None:
    counts: dict[str, int] = {}
    for entry in scenarios:
        counts[entry["target_context"]] = counts.get(entry["target_context"], 0) + 1
    for context in ALLOWED_TARGET_CONTEXTS:
        assert counts.get(context, 0) > 0, (
            f"expected canonical bank to include {context!r} scenarios, got {counts}"
        )


def test_no_removed_v1_fields_present(scenarios: list[dict]) -> None:
    """v2 removed several v1 fields. They must not reappear."""
    removed_fields = {
        "surface",
        "authoring_basis",
        "source_example_id",
        "ambiguity_marker",
        "modality_required",
        "variant",
        "text_proxy_degraded",
    }
    for entry in scenarios:
        sid = entry["scenario_id"]
        present = removed_fields & entry.keys()
        assert not present, (
            f"{sid}: removed v1 fields reappeared: {sorted(present)}"
        )
