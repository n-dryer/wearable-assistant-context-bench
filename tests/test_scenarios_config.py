"""Schema / content tests for experiments/exp_001/scenarios.json.

These checks guard against silently drifting the scenario definitions
away from the Cowork-authored SCENARIO_SEEDS.md source of truth.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parent.parent
SCENARIOS_PATH = REPO_ROOT / "experiments" / "exp_001" / "scenarios.json"
EXPECTED_ANSWERS_PATH = (
    REPO_ROOT / "experiments" / "exp_001" / "expected_answers.json"
)
SEEDS_PATH = REPO_ROOT / ".agent-prompts" / "SCENARIO_SEEDS.md"


REQUIRED_FIELDS = {
    "scenario_id",
    "target_policy",
    "authoring_basis",
    "source_example_id",
    "surface",
    "turn_1_user",
    "turn_2_user",
    "turn_3_repair_anchor",
}
OPTIONAL_IMAGE_FIELDS = {"turn_1_image", "turn_2_image"}
ALLOWED_POLICIES = {"current", "prior", "clarify", "abstain"}
ALLOWED_SURFACES = {"wearable_live_frame", "mobile_app_chat", "synthetic"}


@pytest.fixture(scope="module")
def scenarios() -> list[dict]:
    return json.loads(SCENARIOS_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def expected_answers() -> dict:
    return json.loads(EXPECTED_ANSWERS_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def seeds_text() -> str:
    return SEEDS_PATH.read_text(encoding="utf-8")


def test_scenarios_json_is_non_empty_list(scenarios: list[dict]) -> None:
    assert isinstance(scenarios, list)
    assert len(scenarios) == 11


def test_every_scenario_has_required_fields(scenarios: list[dict]) -> None:
    for entry in scenarios:
        missing = REQUIRED_FIELDS - entry.keys()
        assert not missing, (
            f"scenario {entry.get('scenario_id')!r} missing fields: {missing}"
        )


def test_target_policies_in_allowed_set(scenarios: list[dict]) -> None:
    for entry in scenarios:
        assert entry["target_policy"] in ALLOWED_POLICIES, (
            f"{entry['scenario_id']}: unexpected target_policy "
            f"{entry['target_policy']!r}"
        )


def test_source_example_ids_non_null(scenarios: list[dict]) -> None:
    """Non-theoretical scenarios must anchor to a pilot example ID.

    `theoretical` scenarios (e.g. the without-prior-Q soft case
    defined in `docs/concept_v0_2.md`) may have a null
    `source_example_id` because no pilot quote anchors them.
    """
    for entry in scenarios:
        if entry["authoring_basis"] == "theoretical":
            continue
        assert entry["source_example_id"], (
            f"{entry['scenario_id']}: source_example_id must be non-null "
            "for non-theoretical scenarios (corpus-driven rule)"
        )


def test_surfaces_in_allowed_set(scenarios: list[dict]) -> None:
    for entry in scenarios:
        assert entry["surface"] in ALLOWED_SURFACES, (
            f"{entry['scenario_id']}: unexpected surface {entry['surface']!r}"
        )


def test_authoring_basis_documented(scenarios: list[dict]) -> None:
    allowed = {"pilot", "extended_from_pilot", "theoretical"}
    for entry in scenarios:
        assert entry["authoring_basis"] in allowed, (
            f"{entry['scenario_id']}: unexpected authoring_basis "
            f"{entry['authoring_basis']!r}"
        )


def test_turn_texts_match_seeds_verbatim(
    scenarios: list[dict], seeds_text: str
) -> None:
    """Turn 1 / Turn 2 / Turn 3 anchors must appear verbatim in SCENARIO_SEEDS.md."""
    # Normalize the seeds file text to a single whitespace-collapsed string
    # so we can check substring presence without getting tripped up by
    # Markdown blockquote "> " prefixes.
    normalized = _strip_blockquote_prefix(seeds_text)
    for entry in scenarios:
        for field_name in ("turn_1_user", "turn_2_user", "turn_3_repair_anchor"):
            assert entry[field_name] in normalized, (
                f"{entry['scenario_id']}.{field_name}: text not found verbatim "
                "in SCENARIO_SEEDS.md"
            )


def test_every_scenario_has_answer_set(
    scenarios: list[dict], expected_answers: dict
) -> None:
    for entry in scenarios:
        sid = entry["scenario_id"]
        assert sid in expected_answers, (
            f"{sid}: missing expected_answers entry"
        )
        ans = expected_answers[sid]
        for key in (
            "current_answers",
            "prior_answers",
            "clarify_indicators",
            "abstain_indicators",
        ):
            assert key in ans, f"{sid}: missing answer-set key {key!r}"
            assert isinstance(ans[key], list), (
                f"{sid}.{key}: must be a list"
            )


def test_image_seam_fields_allowed_but_optional(scenarios: list[dict]) -> None:
    """v1 is a text-proxy slice. Image seam fields must be either absent
    or null/str; they are never required."""
    for entry in scenarios:
        for field_name in OPTIONAL_IMAGE_FIELDS:
            if field_name in entry:
                value = entry[field_name]
                assert value is None or isinstance(value, str), (
                    f"{entry['scenario_id']}.{field_name}: must be null or str, "
                    f"got {type(value).__name__}"
                )


def test_v1_composition_is_eight_current_three_prior(scenarios: list[dict]) -> None:
    """The v1 runnable set is 8 `current` / 3 `prior`."""
    counts: dict[str, int] = {}
    for entry in scenarios:
        counts[entry["target_policy"]] = counts.get(entry["target_policy"], 0) + 1
    assert counts.get("current") == 8, f"expected 8 current, got {counts}"
    assert counts.get("prior") == 3, f"expected 3 prior, got {counts}"
    assert counts.get("clarify", 0) == 0
    assert counts.get("abstain", 0) == 0


def _strip_blockquote_prefix(text: str) -> str:
    """Strip Markdown "> " blockquote prefixes and collapse whitespace."""
    lines = [re.sub(r"^>\s?", "", line) for line in text.splitlines()]
    return "\n".join(lines)
