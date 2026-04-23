"""Schema checks for benchmark/v1/scenarios.json.

These tests treat the benchmark JSON files as the only active source of
truth for scenario configuration.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parent.parent
SCENARIOS_PATH = REPO_ROOT / "benchmark" / "v1" / "scenarios.json"
EXPECTED_ANSWERS_PATH = REPO_ROOT / "benchmark" / "v1" / "expected_answers.json"


REQUIRED_FIELDS = {
    "scenario_id",
    "target_context",
    "authoring_basis",
    "source_example_id",
    "surface",
    "turn_1_user",
    "turn_2_user",
    "turn_3_repair_anchor",
}
OPTIONAL_IMAGE_FIELDS = {"turn_1_image", "turn_2_image"}
OPTIONAL_METADATA_FIELDS = {
    "cue_type",
    "activity_domain",
    "time_gap_bucket",
    "ambiguity_marker",
    "modality_required",
    "cognitive_load",
    "difficulty_tier",
    "variant",
    "text_proxy_degraded",
    "notes",
}
ALLOWED_CONTEXTS = {"current", "prior", "clarify", "abstain"}
ALLOWED_SURFACES = {"wearable_live_frame", "mobile_app_chat", "synthetic"}
ALLOWED_AUTHORING_BASIS = {"pilot", "extended_from_pilot", "theoretical"}


@pytest.fixture(scope="module")
def scenarios() -> list[dict]:
    return json.loads(SCENARIOS_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def expected_answers() -> dict:
    return json.loads(EXPECTED_ANSWERS_PATH.read_text(encoding="utf-8"))


def test_scenarios_json_is_non_empty_list(scenarios: list[dict]) -> None:
    assert isinstance(scenarios, list)
    assert len(scenarios) > 0


def test_scenario_ids_are_unique(scenarios: list[dict]) -> None:
    ids = [entry["scenario_id"] for entry in scenarios]
    assert len(ids) == len(set(ids))


def test_every_scenario_has_required_fields(scenarios: list[dict]) -> None:
    for entry in scenarios:
        missing = REQUIRED_FIELDS - entry.keys()
        assert not missing, (
            f"scenario {entry.get('scenario_id')!r} missing fields: {missing}"
        )


def test_target_contexts_in_allowed_set(scenarios: list[dict]) -> None:
    for entry in scenarios:
        assert entry["target_context"] in ALLOWED_CONTEXTS, (
            f"{entry['scenario_id']}: unexpected target_context "
            f"{entry['target_context']!r}"
        )


def test_source_example_ids_non_null_for_non_theoretical_scenarios(
    scenarios: list[dict],
) -> None:
    for entry in scenarios:
        if entry["authoring_basis"] == "theoretical":
            continue
        assert entry["source_example_id"], (
            f"{entry['scenario_id']}: source_example_id must be non-null "
            "for non-theoretical scenarios"
        )


def test_surfaces_in_allowed_set(scenarios: list[dict]) -> None:
    for entry in scenarios:
        assert entry["surface"] in ALLOWED_SURFACES, (
            f"{entry['scenario_id']}: unexpected surface {entry['surface']!r}"
        )


def test_authoring_basis_documented(scenarios: list[dict]) -> None:
    for entry in scenarios:
        assert entry["authoring_basis"] in ALLOWED_AUTHORING_BASIS, (
            f"{entry['scenario_id']}: unexpected authoring_basis "
            f"{entry['authoring_basis']!r}"
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


def test_image_seam_fields_allowed_but_optional(scenarios: list[dict]) -> None:
    for entry in scenarios:
        for field_name in OPTIONAL_IMAGE_FIELDS:
            if field_name in entry:
                value = entry[field_name]
                assert value is None or isinstance(value, str), (
                    f"{entry['scenario_id']}.{field_name}: must be null or str, "
                    f"got {type(value).__name__}"
                )


def test_optional_metadata_fields_have_expected_types(
    scenarios: list[dict],
) -> None:
    for entry in scenarios:
        for field_name in OPTIONAL_METADATA_FIELDS:
            if field_name not in entry:
                continue
            value = entry[field_name]
            if field_name == "text_proxy_degraded":
                assert value is None or isinstance(value, bool), (
                    f"{entry['scenario_id']}.{field_name}: must be null or bool, "
                    f"got {type(value).__name__}"
                )
                continue
            assert value is None or isinstance(value, str), (
                f"{entry['scenario_id']}.{field_name}: must be null or str, "
                f"got {type(value).__name__}"
            )


def test_canonical_v1_composition_includes_all_four_contexts(
    scenarios: list[dict],
) -> None:
    counts: dict[str, int] = {}
    for entry in scenarios:
        counts[entry["target_context"]] = counts.get(entry["target_context"], 0) + 1
    for context in ALLOWED_CONTEXTS:
        assert counts.get(context, 0) > 0, (
            f"expected canonical v1 to include {context!r} scenarios, got {counts}"
        )


def test_scenario_notes_do_not_reference_removed_paths(scenarios: list[dict]) -> None:
    forbidden = (
        "docs/" + "concept" + "_v0_2.md",
        "experiments/" + "exp_" + "001",
        ".agent-" + "prompts/",
        "docs/" + "history/",
    )
    for entry in scenarios:
        notes = entry.get("notes", "")
        for snippet in forbidden:
            assert snippet not in notes, (
                f"{entry['scenario_id']}.notes contains removed path {snippet!r}"
            )
