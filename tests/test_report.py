"""Unit tests for core.report (v1 benchmark-summary + manifest)."""

from __future__ import annotations

import json
import re

import pytest

from core.report import (
    AUXILIARY_POLICY_NOTE,
    BENCHMARK_LABEL,
    DEFAULT_RANKING_CONDITION,
    REQUIRED_MANIFEST_KEYS,
    balanced_accuracy_under_condition,
    balanced_accuracy_with_ci_under_condition,
    class_accuracy_under_condition,
    class_accuracy_with_ci_under_condition,
    code_judge_disagreement_by_scenario,
    cohens_kappa,
    inter_judge_agreement_summary,
    inter_judge_disagreement_by_scenario,
    per_policy_pass_rate_by_condition,
    render_findings_markdown,
    scenario_by_condition_matrix,
    simulated_repair_rate_by_condition,
    wilson_interval,
)


def _trial(
    *,
    scenario_id: str,
    condition: str,
    trial: int,
    target_context: str,
    turn_2_passed: bool,
    turn_2_judge_policy: str | None = None,
    turn_2_code_signals: dict | None = None,
    turn_3_repair_attempted: bool = False,
    turn_3_repair_passed: bool | None = None,
) -> dict:
    return {
        "scenario_id": scenario_id,
        "condition": condition,
        "trial": trial,
        "target_context": target_context,
        "turn_2_passed": turn_2_passed,
        "turn_2_judge_policy": turn_2_judge_policy
        if turn_2_judge_policy is not None
        else (target_context if turn_2_passed else "abstain"),
        "turn_2_code_signals": turn_2_code_signals or {},
        "turn_3_repair_attempted": turn_3_repair_attempted,
        "turn_3_repair_passed": turn_3_repair_passed,
    }


def _fixture_results() -> list[dict]:
    """Mini v1 fixture: one `prior` scenario (sc-03) and three
    `current` scenarios (sc-01, sc-02, sc-04). Two trials per cell."""
    results: list[dict] = []
    # sc-03 (prior): baseline fails both, condition_a passes 1,
    # condition_b passes 2.
    prior_cells = [
        ("baseline", [False, False], [True, False]),
        ("condition_a", [True, False], [None, True]),
        ("condition_b", [True, True], [None, None]),
    ]
    for condition, passes, repairs in prior_cells:
        for i, (passed, repaired) in enumerate(zip(passes, repairs)):
            results.append(
                _trial(
                    scenario_id="sc-03",
                    condition=condition,
                    trial=i,
                    target_context="prior",
                    turn_2_passed=passed,
                    turn_3_repair_attempted=(not passed),
                    turn_3_repair_passed=repaired,
                )
            )
    # sc-01, sc-02, sc-04 (current): baseline 4/6 pass, condition_a 5/6,
    # condition_b 6/6. Build concretely.
    current_plan = {
        "sc-01": {
            "baseline": [True, True],
            "condition_a": [True, True],
            "condition_b": [True, True],
        },
        "sc-02": {
            "baseline": [True, False],
            "condition_a": [True, True],
            "condition_b": [True, True],
        },
        "sc-04": {
            "baseline": [False, True],
            "condition_a": [True, False],
            "condition_b": [True, True],
        },
    }
    for scenario_id, conds in current_plan.items():
        for condition, passes in conds.items():
            for i, passed in enumerate(passes):
                results.append(
                    _trial(
                        scenario_id=scenario_id,
                        condition=condition,
                        trial=i,
                        target_context="current",
                        turn_2_passed=passed,
                        turn_3_repair_attempted=(not passed),
                        turn_3_repair_passed=(False if not passed else None),
                    )
                )
    return results


def test_per_policy_grid_includes_all_four_rows() -> None:
    grid = per_policy_pass_rate_by_condition(_fixture_results())
    assert set(grid.keys()) == {"current", "prior", "clarify", "abstain"}


def test_per_policy_grid_clarify_and_abstain_are_diagnostic() -> None:
    grid = per_policy_pass_rate_by_condition(_fixture_results())
    for condition_cell in grid["clarify"].values():
        assert condition_cell.primary_scored is False
        assert condition_cell.rate is None
    for condition_cell in grid["abstain"].values():
        assert condition_cell.primary_scored is False


def test_per_policy_grid_prior_rates_reflect_fixture() -> None:
    grid = per_policy_pass_rate_by_condition(_fixture_results())
    assert grid["prior"]["baseline"].passed == 0
    assert grid["prior"]["baseline"].total == 2
    assert grid["prior"]["condition_a"].passed == 1
    assert grid["prior"]["condition_a"].total == 2
    assert grid["prior"]["condition_b"].passed == 2
    assert grid["prior"]["condition_b"].total == 2


def test_class_accuracy_under_baseline() -> None:
    results = _fixture_results()
    accs = class_accuracy_under_condition(results, "baseline")
    # prior: 0/2 under baseline.
    assert accs["prior"] == pytest.approx(0.0)
    # current: 4/6 under baseline (2 pass + 1 pass + 0 + 1 pass = 4 from sc-01/sc-02/sc-04).
    # sc-01 baseline: [True, True] -> 2; sc-02 baseline: [True, False] -> 1;
    # sc-04 baseline: [False, True] -> 1. Total 4/6.
    assert accs["current"] == pytest.approx(4 / 6)


def test_balanced_accuracy_under_baseline_is_mean_of_class_accs() -> None:
    results = _fixture_results()
    bal = balanced_accuracy_under_condition(results, "baseline")
    # (0 + 4/6) / 2 = 1/3
    assert bal == pytest.approx((0 + 4 / 6) / 2)


def test_balanced_accuracy_returns_none_when_a_class_is_empty() -> None:
    # No `prior` trials in this set.
    only_current = [
        _trial(
            scenario_id="sc-01",
            condition="baseline",
            trial=0,
            target_context="current",
            turn_2_passed=True,
        )
    ]
    assert (
        balanced_accuracy_under_condition(only_current, "baseline") is None
    )


def test_balanced_accuracy_penalizes_clarify_abstain_as_wrong() -> None:
    # Trial with target prior, judge emits clarify => not a match => wrong.
    results = [
        _trial(
            scenario_id="sc-03",
            condition="baseline",
            trial=0,
            target_context="prior",
            turn_2_passed=False,
            turn_2_judge_policy="clarify",
        ),
        _trial(
            scenario_id="sc-04",
            condition="baseline",
            trial=0,
            target_context="current",
            turn_2_passed=True,
        ),
    ]
    accs = class_accuracy_under_condition(results, "baseline")
    assert accs["prior"] == pytest.approx(0.0)
    assert accs["current"] == pytest.approx(1.0)
    assert balanced_accuracy_under_condition(
        results, "baseline"
    ) == pytest.approx(0.5)


def test_simulated_repair_rate_uses_failures_as_denominator() -> None:
    repair = simulated_repair_rate_by_condition(_fixture_results())
    # baseline: sc-03 2 fails, sc-01 0, sc-02 1 fail, sc-04 1 fail => 4 fails
    assert repair["baseline"].failures == 4
    # repaired under baseline: sc-03 trial 0 repaired; sc-03 trial 1 not;
    # current trials failure but repair=False. Total repaired = 1.
    assert repair["baseline"].repaired == 1
    # condition_b: 0 failures (all trials pass)
    assert repair["condition_b"].failures == 0
    assert repair["condition_b"].rate is None


def test_code_judge_disagreement_counts_per_scenario() -> None:
    results = [
        {
            "scenario_id": "sc-03",
            "condition": "baseline",
            "trial": 0,
            "target_context": "prior",
            "turn_2_passed": False,
            "turn_2_judge_policy": "abstain",
            "turn_2_code_signals": {
                "has_current": False,
                "has_prior": True,
                "has_clarify": False,
                "has_abstain": False,
                "is_refusal": False,
            },
            "turn_3_repair_attempted": False,
            "turn_3_repair_passed": None,
        },
        {
            "scenario_id": "sc-04",
            "condition": "baseline",
            "trial": 0,
            "target_context": "current",
            "turn_2_passed": True,
            "turn_2_judge_policy": "current",
            "turn_2_code_signals": {
                "has_current": True,
                "has_prior": False,
                "has_clarify": False,
                "has_abstain": False,
                "is_refusal": False,
            },
            "turn_3_repair_attempted": False,
            "turn_3_repair_passed": None,
        },
    ]
    disagreements = code_judge_disagreement_by_scenario(results)
    assert disagreements["sc-03"] == 1
    assert disagreements["sc-04"] == 0


def test_scenario_matrix_preserves_trial_order() -> None:
    matrix = scenario_by_condition_matrix(_fixture_results())
    trials = matrix["sc-03"]["baseline"]
    assert [entry["trial"] for entry in trials] == [0, 1]
    assert trials[0]["turn_3_repair_passed"] is True
    assert trials[1]["turn_3_repair_passed"] is False


def test_render_findings_markdown_shape() -> None:
    output = render_findings_markdown(
        _fixture_results(),
        scenario_policies={
            "sc-01": "current",
            "sc-02": "current",
            "sc-03": "prior",
            "sc-04": "current",
        },
        manifest={
            "benchmark_version": "v1",
            "scenarios_sha256": "abc",
            "expected_answers_sha256": "def",
            "interventions_sha256": "ghi",
            "judge_prompt_version": "v1.0.0",
            "candidate_model": "claude-sonnet-4-6",
            "judge_model": "gemini-2.5-flash",
            "judge_family": "gemini",
            "trials": 2,
            "temperature": 0.0,
            "ranking_condition": "baseline",
            "timestamp_utc": "2026-04-19T00:00:00+00:00",
            "runner_git_commit": None,
        },
    )
    assert BENCHMARK_LABEL in output
    assert "Benchmark summary" in output
    assert "Per-class pass rate" in output
    assert "Simulated repair rate" in output
    assert "Code-judge disagreement" in output
    assert "Scenario-by-condition matrix" in output
    assert "Reproducibility manifest" in output
    assert "balanced Turn 2 accuracy" in output
    assert AUXILIARY_POLICY_NOTE in output
    # No old probe-study / aggregate-pass-rate leftovers.
    lowered = output.lower()
    for forbidden in (
        "probe " + "study",
        "aggregate " + "pass rate",
        "overall " + "pass rate",
    ):
        assert forbidden not in lowered
    for forbidden in (
        "benchmark slice",
        "v1 runnable slice",
        "with-prior-q",
        "ranking-friendly",
    ):
        assert forbidden not in lowered


def test_render_findings_markdown_emits_complete_manifest() -> None:
    manifest = {
        "benchmark_version": "v1",
        "scenarios_sha256": "sha-scenarios",
        "expected_answers_sha256": "sha-answers",
        "interventions_sha256": "sha-interventions",
        "judge_prompt_version": "v1.0.0",
        "candidate_model": "claude-sonnet-4-6",
        "judge_model": "gemini-2.5-flash",
        "judge_family": "gemini",
        "judge_family_resolution": "auto",
        "trials": 2,
        "temperature": 0.0,
        "ranking_condition": DEFAULT_RANKING_CONDITION,
        "timestamp_utc": "2026-04-19T12:00:00+00:00",
        "runner_git_commit": None,
        "random_seed": None,
        "manifest_warnings": [],
    }
    output = render_findings_markdown(
        _fixture_results(),
        manifest=manifest,
    )
    match = re.search(r"```json\n(.*?)\n```", output, re.DOTALL)
    assert match is not None, "manifest JSON block missing"
    payload = json.loads(match.group(1))
    for key in REQUIRED_MANIFEST_KEYS:
        assert key in payload, f"required manifest key {key!r} missing"
    # Extras should round-trip.
    assert payload["judge_family_resolution"] == "auto"
    assert payload["manifest_warnings"] == []


def test_render_findings_markdown_manifest_fills_missing_keys() -> None:
    output = render_findings_markdown(
        _fixture_results(),
        manifest={"benchmark_version": "v1"},
    )
    match = re.search(r"```json\n(.*?)\n```", output, re.DOTALL)
    assert match is not None
    payload = json.loads(match.group(1))
    for key in REQUIRED_MANIFEST_KEYS:
        assert key in payload
    # Missing keys should be flagged.
    warnings = payload["manifest_warnings"]
    assert any("scenarios_sha256" in w for w in warnings)
    assert payload["scenarios_sha256"] is None


def test_wilson_interval_zero_n_returns_none() -> None:
    assert wilson_interval(0, 0) is None


def test_wilson_interval_typical_case_brackets_rate() -> None:
    triple = wilson_interval(45, 50)
    assert triple is not None
    rate, lo, hi = triple
    assert abs(rate - 0.9) < 1e-9
    assert 0.0 <= lo <= rate <= hi <= 1.0
    # Wilson is asymmetric near boundaries; just assert the band is positive width.
    assert hi - lo > 0


def test_wilson_interval_full_pass_caps_at_one() -> None:
    triple = wilson_interval(50, 50)
    assert triple is not None
    rate, lo, hi = triple
    assert rate == 1.0
    # Wilson with k=n produces an upper bound numerically indistinguishable
    # from 1.0 (within float epsilon) and the lower bound stays below 1.
    assert hi == pytest.approx(1.0)
    assert lo < 1.0


def test_class_accuracy_with_ci_returns_triples_or_none() -> None:
    # All passes for current, none for prior; both classes have trials.
    results = []
    for _ in range(5):
        results.append({
            "scenario_id": "sc-c", "condition": "baseline",
            "trial": 0, "target_context": "current",
            "turn_2_passed": True, "turn_2_code_signals": {},
            "turn_3_repair_attempted": False, "turn_3_repair_passed": None,
        })
    for _ in range(5):
        results.append({
            "scenario_id": "sc-p", "condition": "baseline",
            "trial": 0, "target_context": "prior",
            "turn_2_passed": False, "turn_2_code_signals": {},
            "turn_3_repair_attempted": False, "turn_3_repair_passed": None,
        })
    out = class_accuracy_with_ci_under_condition(results, "baseline")
    assert out["current"] is not None and out["current"][0] == 1.0
    assert out["prior"] is not None and out["prior"][0] == 0.0


def test_balanced_accuracy_with_ci_handles_missing_class() -> None:
    # Only current trials; prior is missing -> CI should be None.
    results = [
        {
            "scenario_id": "sc-c", "condition": "baseline",
            "trial": 0, "target_context": "current",
            "turn_2_passed": True, "turn_2_code_signals": {},
            "turn_3_repair_attempted": False, "turn_3_repair_passed": None,
        },
    ]
    assert balanced_accuracy_with_ci_under_condition(results, "baseline") is None


def test_cohens_kappa_perfect_agreement_is_one() -> None:
    assert cohens_kappa(["a", "b", "a"], ["a", "b", "a"]) == pytest.approx(1.0)


def test_cohens_kappa_independent_random_is_zero() -> None:
    # 4 items, balanced 2/2 split, 2 matches by chance
    a = ["x", "x", "y", "y"]
    b = ["x", "y", "x", "y"]
    # observed = 2/4 = 0.5; expected = 0.5*0.5 + 0.5*0.5 = 0.5; kappa = 0
    assert cohens_kappa(a, b) == pytest.approx(0.0)


def test_cohens_kappa_below_zero_when_systematically_disagreeing() -> None:
    a = ["x", "x", "y", "y"]
    b = ["y", "y", "x", "x"]
    # observed = 0; expected = 0.5; kappa = -1
    assert cohens_kappa(a, b) == pytest.approx(-1.0)


def test_cohens_kappa_unequal_lengths_raises() -> None:
    with pytest.raises(ValueError):
        cohens_kappa(["a"], ["a", "b"])


def test_inter_judge_agreement_summary_returns_none_without_ranking_labels() -> None:
    # Standard fixture has no ranking-judge fields; expect None.
    assert inter_judge_agreement_summary(_fixture_results()) is None


def test_inter_judge_agreement_summary_with_ranking_labels() -> None:
    results = _fixture_results()
    # Annotate every trial with a ranking-judge label that mostly matches
    # the primary judge's label, with a couple of disagreements.
    for i, trial in enumerate(results):
        primary = trial["turn_2_judge_policy"]
        # Disagree on every fifth trial.
        if i % 5 == 0 and primary == "current":
            trial["turn_2_ranking_judge_policy"] = "prior"
        else:
            trial["turn_2_ranking_judge_policy"] = primary
    summary = inter_judge_agreement_summary(results)
    assert summary is not None
    assert summary["trials"] == len(results)
    assert summary["observed_agreement"] < 1.0
    assert summary["kappa"] is not None
    assert -1.0 <= summary["kappa"] <= 1.0


def test_inter_judge_disagreement_by_scenario_counts_only_paired_trials() -> None:
    results = _fixture_results()
    # Tag a single trial with disagreeing ranking label.
    target_idx = 0
    results[target_idx]["turn_2_ranking_judge_policy"] = (
        "prior" if results[target_idx]["turn_2_judge_policy"] != "prior" else "current"
    )
    counts = inter_judge_disagreement_by_scenario(results)
    assert counts.get(results[target_idx]["scenario_id"]) == 1
    # Untagged trials should not surface.
    untagged_total = sum(counts.values())
    assert untagged_total == 1


def test_render_findings_markdown_includes_inter_judge_section() -> None:
    output = render_findings_markdown(_fixture_results())
    assert "Inter-judge agreement (cross-LLM)" in output
    # No ranking judge in the fixture -> placeholder text rendered.
    assert "ranking-judge-family" in output
