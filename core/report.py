"""Aggregation and Markdown rendering for experiment results.

The runner produces one result dict per trial. This module rolls those up
into per-condition pass rates, per-class pass rates, and a condition-by-class
matrix, and renders the matrix as a Markdown table ready to drop into
findings.md.

Expected per-trial result dict keys:
    condition (str): intervention name, e.g. "baseline" or "condition_a"
    incident_class (str): incident class label from INCIDENT_CLASSES.md
    passed (bool): final pass/fail for that trial
    scenario_id (str, optional): scenario identifier, not required for
        aggregation but normally present for traceability

Additional keys on each trial result are ignored by this module.
"""

from __future__ import annotations

from collections import defaultdict


BASELINE_CONDITION = "baseline"


def aggregate_results(results: list[dict]) -> dict:
    """Aggregate per-trial results into pass-rate summaries.

    Args:
        results: List of per-trial result dicts. See module docstring for
            required keys.

    Returns:
        Dict with three top-level keys:
            per_condition (dict[str, float]): condition name -> pass rate
                in [0.0, 1.0]. Conditions with zero trials are omitted.
            per_class (dict[str, float]): incident class -> pass rate
                aggregated across all conditions.
            matrix (dict[str, dict[str, float]]): condition -> incident
                class -> pass rate. Cells with zero trials are omitted
                rather than reported as 0.0, to distinguish "no data" from
                "all failed".
    """
    condition_totals: dict[str, list[bool]] = defaultdict(list)
    class_totals: dict[str, list[bool]] = defaultdict(list)
    cell_totals: dict[str, dict[str, list[bool]]] = defaultdict(
        lambda: defaultdict(list)
    )

    for trial in results:
        condition = trial["condition"]
        incident_class = trial["incident_class"]
        passed = bool(trial["passed"])

        condition_totals[condition].append(passed)
        class_totals[incident_class].append(passed)
        cell_totals[condition][incident_class].append(passed)

    per_condition = {
        condition: _rate(outcomes) for condition, outcomes in condition_totals.items()
    }
    per_class = {
        incident_class: _rate(outcomes)
        for incident_class, outcomes in class_totals.items()
    }
    matrix = {
        condition: {
            incident_class: _rate(outcomes)
            for incident_class, outcomes in classes.items()
        }
        for condition, classes in cell_totals.items()
    }

    return {
        "per_condition": per_condition,
        "per_class": per_class,
        "matrix": matrix,
    }


def format_markdown_table(matrix: dict) -> str:
    """Render a condition-by-class pass-rate matrix as a Markdown table.

    Args:
        matrix: Either a full aggregate dict returned by aggregate_results
            (which contains a "matrix" key) or a bare condition -> class ->
            rate dict. Both are accepted so callers can hand off the
            aggregate dict directly.

    Returns:
        A Markdown table string. Missing cells render as "-". Pass rates
        render as percentages with one decimal place.
    """
    cells = matrix["matrix"] if "matrix" in matrix and isinstance(
        matrix["matrix"], dict
    ) else matrix

    conditions = list(cells.keys())
    classes: list[str] = []
    seen: set[str] = set()
    for cond in conditions:
        for cls in cells[cond].keys():
            if cls not in seen:
                seen.add(cls)
                classes.append(cls)

    header = "| Condition | " + " | ".join(classes) + " |"
    separator = "| --- | " + " | ".join("---" for _ in classes) + " |"
    rows = [header, separator]
    for cond in conditions:
        row_cells = [cond]
        for cls in classes:
            rate = cells[cond].get(cls)
            row_cells.append("-" if rate is None else f"{rate * 100:.1f}%")
        rows.append("| " + " | ".join(row_cells) + " |")
    return "\n".join(rows)


def compute_effect_sizes(matrix: dict) -> dict:
    """Compute per-class deltas between each condition and baseline.

    Args:
        matrix: Either a full aggregate dict or a bare condition -> class ->
            rate dict. Must contain a baseline condition.

    Returns:
        Dict keyed on non-baseline condition name, each mapping incident
        class -> (condition_rate - baseline_rate). Classes missing from
        either the baseline or the condition are omitted from that
        condition's effect dict.

    Raises:
        KeyError: If the baseline condition is not present.
    """
    cells = matrix["matrix"] if "matrix" in matrix and isinstance(
        matrix["matrix"], dict
    ) else matrix

    if BASELINE_CONDITION not in cells:
        raise KeyError(
            f"Baseline condition {BASELINE_CONDITION!r} not present in matrix. "
            f"Known conditions: {list(cells.keys())}"
        )

    baseline = cells[BASELINE_CONDITION]
    effects: dict[str, dict[str, float]] = {}
    for condition, class_rates in cells.items():
        if condition == BASELINE_CONDITION:
            continue
        condition_effects: dict[str, float] = {}
        for incident_class, rate in class_rates.items():
            if incident_class not in baseline:
                continue
            condition_effects[incident_class] = rate - baseline[incident_class]
        effects[condition] = condition_effects
    return effects


def _rate(outcomes: list[bool]) -> float:
    """Return pass rate in [0.0, 1.0]. Assumes non-empty input."""
    return sum(1 for p in outcomes if p) / len(outcomes)
