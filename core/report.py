"""Aggregation and Markdown rendering for canonical v1 benchmark results.

The runner produces one result dict per trial. This module rolls
those up into a findings report for the `Wearable Assistant Context
Benchmark` v1 benchmark:

1. **Benchmark summary.** Headline primary score (balanced Turn 2
   accuracy under the default comparison condition), per-class
   accuracy, and a per-condition sensitivity row.
2. **Per-class pass rate by condition.** A 4-row internal grid for
   visibility. `current` and `prior` are the primary classes.
   `clarify` and `abstain` are auxiliary diagnostic classes in the
   canonical release and are not included in the primary score.
3. **Simulated repair rate per condition.**
4. **Code-judge disagreement count per scenario.**
5. **Scenario-by-condition matrix.**
6. **Reproducibility manifest.** A JSON block with the scenario /
   interventions / judge-prompt SHAs, model strings, trials,
   temperature, and the default comparison condition.

Expected per-trial result dict keys:
    scenario_id (str)
    target_context (str): one of "current", "prior", "clarify", "abstain"
    condition (str)
    trial (int)
    turn_2_code_signals (dict)
    turn_2_judge_policy (str)
    turn_2_passed (bool): judge_policy == target_context
    turn_3_repair_attempted (bool)
    turn_3_repair_passed (bool | None)
"""

from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass
from typing import Any


POLICIES: tuple[str, ...] = ("current", "prior", "clarify", "abstain")
SCORED_POLICIES: tuple[str, ...] = ("current", "prior")
CONDITIONS_ORDER: tuple[str, ...] = ("baseline", "condition_a", "condition_b")
AUXILIARY_POLICY_NOTE: str = (
    "auxiliary in canonical v1; not included in the primary current/prior score"
)

BENCHMARK_NAME: str = "Wearable Assistant Context Benchmark"
BENCHMARK_VERSION: str = "v1"
BENCHMARK_LABEL: str = (
    "canonical v1 benchmark for cross-turn reference resolution under "
    "context change"
)
DEFAULT_RANKING_CONDITION: str = "baseline"

# Kept for backwards compatibility with older call sites and tests.
BENCHMARK_SLICE: str = BENCHMARK_LABEL
DIAGNOSTIC_POLICY_NOTE: str = AUXILIARY_POLICY_NOTE
UNSCORED_POLICY_NOTE: str = AUXILIARY_POLICY_NOTE


@dataclass
class PassRateCell:
    """One cell of the per-policy-by-condition pass-rate grid.

    Attributes:
        passed: Trials in this cell where `turn_2_passed` was True.
        total: Total trials in this cell.
        primary_scored: True when the policy contributes to the primary
            balanced-accuracy metric (`current`, `prior`). Auxiliary
            policies still report rates when scenarios are present.
    """

    passed: int
    total: int
    primary_scored: bool

    @property
    def rate(self) -> float | None:
        if self.total == 0:
            return None
        return self.passed / self.total


@dataclass
class RepairRateCell:
    """One condition's simulated repair rate."""

    repaired: int
    failures: int

    @property
    def rate(self) -> float | None:
        if self.failures == 0:
            return None
        return self.repaired / self.failures


def _policies_with_scenarios(results: list[dict]) -> set[str]:
    return {r["target_context"] for r in results}


def per_policy_pass_rate_by_condition(
    results: list[dict],
) -> dict[str, dict[str, PassRateCell]]:
    """Group per-trial results into a policy x condition grid of pass rates."""
    observed_policies = _policies_with_scenarios(results)
    conditions = sorted({r["condition"] for r in results}, key=_condition_sort_key)
    grid: dict[str, dict[str, PassRateCell]] = {}
    for policy in POLICIES:
        grid[policy] = {}
        for condition in conditions:
            if policy not in observed_policies:
                grid[policy][condition] = PassRateCell(
                    passed=0, total=0, primary_scored=(policy in SCORED_POLICIES)
                )
                continue
            passed = 0
            total = 0
            for trial in results:
                if trial["target_context"] != policy:
                    continue
                if trial["condition"] != condition:
                    continue
                total += 1
                if bool(trial["turn_2_passed"]):
                    passed += 1
            grid[policy][condition] = PassRateCell(
                passed=passed,
                total=total,
                primary_scored=(policy in SCORED_POLICIES),
            )
    return grid


def class_accuracy_under_condition(
    results: list[dict],
    condition: str,
) -> dict[str, float | None]:
    """Compute per-class Turn 2 accuracy under one condition.

    Returns a dict keyed on the **scored** policies (`prior`,
    `current`) mapping to the accuracy in [0, 1], or None if there are
    no trials in that class.
    """
    out: dict[str, float | None] = {}
    for policy in SCORED_POLICIES:
        total = 0
        passed = 0
        for trial in results:
            if trial["condition"] != condition:
                continue
            if trial["target_context"] != policy:
                continue
            total += 1
            if bool(trial["turn_2_passed"]):
                passed += 1
        out[policy] = (passed / total) if total > 0 else None
    return out


def balanced_accuracy_under_condition(
    results: list[dict],
    condition: str,
) -> float | None:
    """Primary benchmark score under a given default comparison condition.

    Defined as the mean of per-class accuracy across the two scored
    policies (`prior`, `current`). Clarify / abstain trials contribute
    to their class's denominator as wrong answers (they never pass the
    target-policy match), matching the rule that they count as wrong
    for the primary score.
    """
    classes = class_accuracy_under_condition(results, condition)
    usable = [acc for acc in classes.values() if acc is not None]
    if not usable or len(usable) < len(classes):
        # All scored classes must have at least one trial for a score
        # to be defined. If one is missing, return None and let the
        # caller render that as "n/a" in the report.
        return None
    return sum(usable) / len(usable)


def simulated_repair_rate_by_condition(
    results: list[dict],
) -> dict[str, RepairRateCell]:
    """Compute simulated repair rate per condition."""
    by_condition: dict[str, list[dict]] = defaultdict(list)
    for trial in results:
        by_condition[trial["condition"]].append(trial)

    out: dict[str, RepairRateCell] = {}
    for condition in sorted(by_condition.keys(), key=_condition_sort_key):
        failures = 0
        repaired = 0
        for trial in by_condition[condition]:
            if bool(trial["turn_2_passed"]):
                continue
            failures += 1
            if bool(trial.get("turn_3_repair_passed")):
                repaired += 1
        out[condition] = RepairRateCell(repaired=repaired, failures=failures)
    return out


def code_judge_disagreement_by_scenario(results: list[dict]) -> dict[str, int]:
    """Count trials where code signals imply a different policy than judge."""
    counts: dict[str, int] = defaultdict(int)
    scenario_ids = {r["scenario_id"] for r in results}
    for scenario_id in scenario_ids:
        counts[scenario_id] = 0
    for trial in results:
        code_policy = _code_implied_policy(trial.get("turn_2_code_signals") or {})
        if code_policy is None:
            continue
        if code_policy != trial.get("turn_2_judge_policy"):
            counts[trial["scenario_id"]] += 1
    return dict(counts)


def scenario_by_condition_matrix(
    results: list[dict],
) -> dict[str, dict[str, list[dict]]]:
    """Group per-trial outcomes into a scenario x condition grid."""
    grid: dict[str, dict[str, list[dict]]] = defaultdict(lambda: defaultdict(list))
    for trial in results:
        grid[trial["scenario_id"]][trial["condition"]].append(
            {
                "trial": trial["trial"],
                "turn_2_passed": bool(trial["turn_2_passed"]),
                "turn_3_repair_attempted": bool(
                    trial.get("turn_3_repair_attempted", False)
                ),
                "turn_3_repair_passed": trial.get("turn_3_repair_passed"),
            }
        )
    for scenario in grid.values():
        for cell in scenario.values():
            cell.sort(key=lambda entry: entry["trial"])
    return {scenario_id: dict(cells) for scenario_id, cells in grid.items()}


REQUIRED_MANIFEST_KEYS: tuple[str, ...] = (
    "benchmark_version",
    "scenarios_sha256",
    "expected_answers_sha256",
    "interventions_sha256",
    "judge_prompt_version",
    "candidate_model",
    "judge_model",
    "judge_family",
    "trials",
    "temperature",
    "ranking_condition",
    "timestamp_utc",
    "runner_git_commit",
    "random_seed",
)


def render_findings_markdown(
    results: list[dict],
    scenario_policies: dict[str, str] | None = None,
    manifest: dict[str, Any] | None = None,
    ranking_condition: str = DEFAULT_RANKING_CONDITION,
) -> str:
    """Render the v1 findings.md body from per-trial results.

    Args:
        results: Per-trial result dicts.
        scenario_policies: Optional scenario_id -> target_context
            mapping. When provided, scenarios are ordered by this
            map's iteration order.
        manifest: Reproducibility manifest dict. Every required key in
            `REQUIRED_MANIFEST_KEYS` should be present; missing keys
            render as `null` with a `manifest_warnings` note.
        ranking_condition: Condition name to use for the primary score.

    Returns:
        A Markdown string including the benchmark-summary section,
        per-policy grid, scenario matrix, and a reproducibility
        manifest block.
    """
    grid = per_policy_pass_rate_by_condition(results)
    repair = simulated_repair_rate_by_condition(results)
    disagreements = code_judge_disagreement_by_scenario(results)
    matrix = scenario_by_condition_matrix(results)
    conditions = _sorted_conditions(results)

    primary_score = balanced_accuracy_under_condition(
        results, ranking_condition
    )
    class_accs = class_accuracy_under_condition(results, ranking_condition)
    per_condition_balanced = {
        condition: balanced_accuracy_under_condition(results, condition)
        for condition in conditions
    }

    sections = [
        f"# {BENCHMARK_NAME}: Findings",
        "",
        f"**Benchmark:** {BENCHMARK_LABEL}",
        "",
        "## Benchmark summary",
        "",
        _render_benchmark_summary(
            benchmark_slice=BENCHMARK_LABEL,
            ranking_condition=ranking_condition,
            primary_score=primary_score,
            class_accs=class_accs,
            per_condition_balanced=per_condition_balanced,
        ),
        "",
        "## Per-class pass rate by condition",
        "",
        _render_policy_grid(grid, conditions),
        "",
        "## Simulated repair rate by condition",
        "",
        _render_repair_table(repair),
        "",
        "## Code-judge disagreement by scenario",
        "",
        _render_disagreement_list(disagreements),
        "",
        "## Scenario-by-condition matrix",
        "",
        _render_scenario_matrix(matrix, conditions, scenario_policies),
        "",
        "## Reproducibility manifest",
        "",
        _render_manifest_block(manifest or {}),
        "",
    ]
    return "\n".join(sections)


def _render_benchmark_summary(
    *,
    benchmark_slice: str,
    ranking_condition: str,
    primary_score: float | None,
    class_accs: dict[str, float | None],
    per_condition_balanced: dict[str, float | None],
) -> str:
    def _pct(value: float | None) -> str:
        if value is None:
            return "n/a"
        return f"{value * 100:.1f}%"

    lines: list[str] = [
        f"- **Benchmark**: {benchmark_slice}",
        f"- **Default comparison condition**: `{ranking_condition}`",
        f"- **Primary score** (balanced Turn 2 accuracy): **{_pct(primary_score)}**",
        "- **How to read this run**: compare candidate models on the "
        f"`{ranking_condition}` score below; treat the other conditions as "
        "diagnostic sensitivity checks.",
        f"- **Per-class accuracy under `{ranking_condition}`**:",
    ]
    for policy in SCORED_POLICIES:
        lines.append(f"    - `{policy}`: {_pct(class_accs.get(policy))}")
    lines.append("")
    lines.append("Condition sensitivity (balanced Turn 2 accuracy):")
    lines.append("")
    lines.append("| Condition | Balanced Turn 2 accuracy |")
    lines.append("| --- | --- |")
    for condition, score in per_condition_balanced.items():
        marker = " (default)" if condition == ranking_condition else ""
        lines.append(f"| {condition}{marker} | {_pct(score)} |")
    return "\n".join(lines)


def _render_policy_grid(
    grid: dict[str, dict[str, PassRateCell]],
    conditions: list[str],
) -> str:
    header = "| Class | " + " | ".join(conditions) + " |"
    separator = "| --- | " + " | ".join("---" for _ in conditions) + " |"
    rows = [header, separator]
    for policy in POLICIES:
        label = f"`{policy}`"
        if policy not in SCORED_POLICIES:
            label = f"`{policy}` (auxiliary)"
        cells = [label]
        for condition in conditions:
            cell = grid[policy][condition]
            if cell.total == 0:
                if cell.primary_scored:
                    cells.append("-")
                else:
                    cells.append(AUXILIARY_POLICY_NOTE)
            elif cell.rate is None:
                cells.append("-")
            else:
                pct = cell.rate * 100 if cell.rate is not None else 0.0
                cells.append(f"{pct:.1f}% ({cell.passed}/{cell.total})")
        rows.append("| " + " | ".join(cells) + " |")
    return "\n".join(rows)


def _render_repair_table(repair: dict[str, RepairRateCell]) -> str:
    header = "| Condition | Repair rate (repaired / failures) |"
    separator = "| --- | --- |"
    rows = [header, separator]
    for condition, cell in repair.items():
        if cell.failures == 0:
            rows.append(f"| {condition} | no Turn 2 failures |")
            continue
        pct = cell.rate * 100 if cell.rate is not None else 0.0
        rows.append(
            f"| {condition} | {pct:.1f}% ({cell.repaired} / {cell.failures}) |"
        )
    return "\n".join(rows)


def _render_disagreement_list(disagreements: dict[str, int]) -> str:
    if not disagreements:
        return "_No trials recorded._"
    lines: list[str] = []
    for scenario_id in sorted(disagreements.keys()):
        lines.append(
            f"- {scenario_id}: {disagreements[scenario_id]} trial(s) "
            "with code/judge disagreement"
        )
    return "\n".join(lines)


def _render_scenario_matrix(
    matrix: dict[str, dict[str, list[dict]]],
    conditions: list[str],
    scenario_policies: dict[str, str] | None,
) -> str:
    header = "| Scenario | Target context | " + " | ".join(conditions) + " |"
    separator = "| --- | --- | " + " | ".join("---" for _ in conditions) + " |"
    rows = [header, separator]

    if scenario_policies is not None:
        scenario_order = list(scenario_policies.keys())
    else:
        scenario_order = sorted(matrix.keys())

    for scenario_id in scenario_order:
        if scenario_id not in matrix:
            continue
        target_context = (
            scenario_policies[scenario_id] if scenario_policies else "?"
        )
        cells = [scenario_id, f"`{target_context}`"]
        for condition in conditions:
            trials = matrix[scenario_id].get(condition, [])
            cells.append(_format_trial_outcomes(trials))
        rows.append("| " + " | ".join(cells) + " |")
    return "\n".join(rows)


def _format_trial_outcomes(trials: list[dict]) -> str:
    if not trials:
        return "-"
    tokens: list[str] = []
    for entry in trials:
        if entry["turn_2_passed"]:
            tokens.append("pass")
            continue
        if not entry["turn_3_repair_attempted"]:
            tokens.append("fail")
            continue
        if entry["turn_3_repair_passed"]:
            tokens.append("fail→repair-pass")
        else:
            tokens.append("fail→repair-fail")
    return ", ".join(tokens)


def _render_manifest_block(manifest: dict[str, Any]) -> str:
    """Render the reproducibility manifest as a JSON code block.

    Ensures every required key is present (with `null` fallback) and
    attaches any `manifest_warnings` provided by the runner.
    """
    out: dict[str, Any] = {}
    missing: list[str] = []
    for key in REQUIRED_MANIFEST_KEYS:
        if key in manifest:
            out[key] = manifest[key]
        else:
            out[key] = None
            missing.append(key)
    warnings = list(manifest.get("manifest_warnings") or [])
    for key in missing:
        warnings.append(f"manifest key missing: {key}")
    extras = {
        key: value
        for key, value in manifest.items()
        if key not in REQUIRED_MANIFEST_KEYS
        and key != "manifest_warnings"
    }
    out.update(extras)
    out["manifest_warnings"] = warnings
    return "```json\n" + json.dumps(out, indent=2, sort_keys=False) + "\n```"


def _code_implied_policy(signals: dict) -> str | None:
    """Map a Turn 2 code-signal dict to a single implied policy, if any."""
    if not signals:
        return None
    if signals.get("is_refusal") or signals.get("has_abstain"):
        return "abstain"
    if signals.get("has_clarify"):
        return "clarify"
    has_current = bool(signals.get("has_current"))
    has_prior = bool(signals.get("has_prior"))
    if has_current and not has_prior:
        return "current"
    if has_prior and not has_current:
        return "prior"
    return None


def _sorted_conditions(results: list[dict]) -> list[str]:
    observed = {r["condition"] for r in results}
    return sorted(observed, key=_condition_sort_key)


def _condition_sort_key(condition: str) -> tuple[int, str]:
    if condition in CONDITIONS_ORDER:
        return (CONDITIONS_ORDER.index(condition), condition)
    return (len(CONDITIONS_ORDER), condition)
