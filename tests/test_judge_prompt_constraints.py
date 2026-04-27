"""Constraints on what the judge prompt may include.

The judge labels each Turn 2 response without seeing the scenario's
``target_context`` label, the ``cue_type`` shift category, or the
authoring ``notes``. Those fields would tell the judge the answer it
is being asked to produce. These tests verify the prompt-building
helpers respect those constraints.

Future PRs that touch ``benchmark.v1.run._build_scenario_description``
or ``benchmark.v1.run._build_ground_truth_context`` must keep these
assertions green.
"""

from __future__ import annotations

import pytest

from benchmark.v1.run import (
    EXPECTED_ANSWERS_PATH,
    SCENARIOS_PATH,
    _build_ground_truth_context,
    _build_scenario_description,
    load_expected_answers,
    load_scenarios,
)
from core.llm_judge import _build_user_prompt


@pytest.fixture(scope="module")
def scenarios():
    return load_scenarios(SCENARIOS_PATH)


@pytest.fixture(scope="module")
def answers_by_id():
    return load_expected_answers(EXPECTED_ANSWERS_PATH)


def _label_naming_phrases(target_context: str) -> tuple[str, ...]:
    """Sentence patterns that would name the answer for the judge."""
    return (
        f"target context for turn 2 is `{target_context}`",
        f"target context for turn 2 is {target_context}",
        f"target context: {target_context}",
        f"target_context: {target_context}",
        f"target context is `{target_context}`",
        f"the correct label is {target_context}",
        f"correct policy is {target_context}",
        f"the answer is {target_context}",
    )


def test_scenario_description_does_not_name_target_context(scenarios) -> None:
    """The scenario description sent to the judge must not state the target."""
    leaks: list[str] = []
    for scenario in scenarios:
        rendered = _build_scenario_description(scenario).lower()
        for phrase in _label_naming_phrases(scenario.target_context):
            if phrase in rendered:
                leaks.append(
                    f"{scenario.scenario_id}: {phrase!r} found in scenario_description"
                )
    assert not leaks, (
        "scenario_description names target_context for:\n  - "
        + "\n  - ".join(leaks)
    )


def test_ground_truth_context_omits_target_cue_and_notes(scenarios) -> None:
    """The judge-only ground truth must omit target_context, cue_type, notes."""
    leaks: list[str] = []
    for scenario in scenarios:
        rendered = _build_ground_truth_context(scenario)
        rendered_lower = rendered.lower()
        for phrase in _label_naming_phrases(scenario.target_context):
            if phrase in rendered_lower:
                leaks.append(
                    f"{scenario.scenario_id}: {phrase!r} found in ground_truth_context"
                )
        if scenario.cue_type and scenario.cue_type.lower() in rendered_lower:
            leaks.append(
                f"{scenario.scenario_id}: cue_type {scenario.cue_type!r} found in "
                f"ground_truth_context"
            )
        if scenario.notes and len(scenario.notes) >= 8:
            if scenario.notes.lower() in rendered_lower:
                leaks.append(
                    f"{scenario.scenario_id}: authoring notes appear in "
                    f"ground_truth_context"
                )
    assert not leaks, (
        "ground_truth_context exposes privileged fields for:\n  - "
        + "\n  - ".join(leaks)
    )


def test_full_rendered_judge_prompt_omits_privileged_fields(
    scenarios, answers_by_id
) -> None:
    """End-to-end: the full rendered judge user message contains no privileged fields."""
    sample_response = "An assistant response that mentions some object."
    leaks: list[str] = []
    for scenario in scenarios:
        answers = answers_by_id[scenario.scenario_id]
        rendered = _build_user_prompt(
            response=sample_response,
            scenario_description=_build_scenario_description(scenario),
            turn_2_user=scenario.turn_2_user,
            current_answers=answers.current_answers,
            prior_answers=answers.prior_answers,
            clarify_indicators=answers.clarify_indicators,
            abstain_indicators=answers.abstain_indicators,
            ground_truth_context=_build_ground_truth_context(scenario),
        )
        rendered_lower = rendered.lower()
        for phrase in _label_naming_phrases(scenario.target_context):
            if phrase in rendered_lower:
                leaks.append(
                    f"{scenario.scenario_id}: {phrase!r} found in rendered judge prompt"
                )
        if scenario.cue_type and scenario.cue_type.lower() in rendered_lower:
            leaks.append(
                f"{scenario.scenario_id}: cue_type {scenario.cue_type!r} found in "
                f"rendered judge prompt"
            )
        if scenario.notes and len(scenario.notes) >= 8:
            if scenario.notes.lower() in rendered_lower:
                leaks.append(
                    f"{scenario.scenario_id}: authoring notes appear in rendered "
                    f"judge prompt"
                )
    assert not leaks, (
        "Rendered judge prompt exposes privileged fields for:\n  - "
        + "\n  - ".join(leaks)
    )
