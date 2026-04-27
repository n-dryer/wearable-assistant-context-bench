"""Generate statistical analysis from published v1 run data.

Reads the JSONL transcripts from the canonical 50-scenario runs and
produces:

1. Wilson confidence intervals for the headline balanced and per-class
   accuracies under `baseline`.
2. Per-shift-type accuracy breakdown (cross-family runs only).
3. McNemar's paired comparison (Gemini Flash-Lite vs Gemini Flash on
   the canonical bank).
4. Empirical-difficulty grounding (MMStar protocol; 80/40 thresholds).
5. Minimum-detectable-effect disclosure for the canonical sample size.
6. Coverage matrix (shift type x difficulty x target_context).

Run:
    python scripts/analyze_runs.py
"""

from __future__ import annotations

import json
from pathlib import Path

from core.statistics import (
    wilson_ci,
    mcnemar_test,
    per_shift_type_accuracy,
    empirical_difficulty,
    minimum_detectable_effect,
)

RUNS_DIR = Path("benchmark/v1/runs")
SCENARIOS_PATH = Path("benchmark/v1/scenarios.json")

# Canonical 50-scenario runs only; the adversarial run uses a different
# scenario bank and is not directly comparable here.
RUN_PATHS = {
    "baseline (Gemini Flash-Lite, same-family judge)": RUNS_DIR / "baseline",
    "baseline-alt (Gemini Flash, same-family judge)": RUNS_DIR / "baseline-alt",
    "ablation-no-camera (Gemini Flash-Lite, --no-camera)": RUNS_DIR / "ablation-no-camera",
    "baseline-qwen-cross-family (Qwen3-VL, Gemini judge)": RUNS_DIR / "baseline-qwen-cross-family",
    "baseline-deictic-repair (Gemini Flash-Lite, deictic repair)": RUNS_DIR / "baseline-deictic-repair",
}

# The McNemar paired comparison is most informative when both runs
# share scenarios and condition, but use different candidate models.
PAIRED_COMPARISON = (
    "baseline (Gemini Flash-Lite, same-family judge)",
    "baseline-alt (Gemini Flash, same-family judge)",
)

# Cross-family runs used for empirical-difficulty grounding (excludes
# the camera ablation, which is a deliberately handicapped condition).
EMPIRICAL_DIFFICULTY_RUNS = (
    "baseline-qwen-cross-family (Qwen3-VL, Gemini judge)",
)


def load_transcripts(run_dir: Path) -> list[dict]:
    """Load JSONL transcripts from a run directory."""
    path = run_dir / "transcripts.jsonl"
    results = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                results.append(json.loads(line))
    return results


def load_scenarios() -> dict[str, dict]:
    """Load scenario metadata keyed by scenario_id."""
    with SCENARIOS_PATH.open("r", encoding="utf-8") as f:
        raw = json.load(f)
    return {s["scenario_id"]: s for s in raw}


def compute_balanced_accuracy_with_ci(
    results: list[dict], condition: str = "baseline"
) -> dict:
    """Compute balanced accuracy with Wilson CIs for each class."""
    from core.report import SCORED_POLICIES

    class_stats = {}
    for policy in SCORED_POLICIES:
        trials = [
            r for r in results
            if r["condition"] == condition and r["target_context"] == policy
        ]
        n = len(trials)
        k = sum(1 for t in trials if bool(t["turn_2_passed"]))
        ci = wilson_ci(k, n)
        class_stats[policy] = {
            "accuracy": ci.proportion,
            "ci_lower": ci.lower,
            "ci_upper": ci.upper,
            "n": n,
            "k": k,
        }

    accs = [s["accuracy"] for s in class_stats.values()]
    balanced = sum(accs) / len(accs) if accs else 0.0

    return {
        "balanced_accuracy": balanced,
        "per_class": class_stats,
    }


def main() -> None:
    scenarios = load_scenarios()
    scenario_tiers = {
        sid: s["difficulty_tier"] for sid, s in scenarios.items()
    }

    # Load all runs
    all_results = {}
    for name, path in RUN_PATHS.items():
        if path.exists():
            all_results[name] = load_transcripts(path)
            print(f"Loaded {len(all_results[name])} trials from {name}")
        else:
            print(f"SKIP: {path} not found")

    print("\n" + "=" * 72)
    print("STATISTICAL ANALYSIS: Wearable Assistant Context Benchmark v1")
    print("=" * 72)

    # --- 1. Balanced accuracy with Wilson CIs ---
    print("\n## 1. Balanced Turn 2 Accuracy with 95% Wilson CIs\n")
    for name, results in all_results.items():
        stats = compute_balanced_accuracy_with_ci(results)
        ba = stats["balanced_accuracy"]
        print(f"### {name}")
        print(f"  Balanced accuracy: {ba * 100:.1f}%")
        for policy, ps in stats["per_class"].items():
            ci = wilson_ci(ps["k"], ps["n"])
            print(
                f"  {policy}: {ps['accuracy'] * 100:.1f}% "
                f"[{ci.lower * 100:.1f}–{ci.upper * 100:.1f}] "
                f"(n={ps['n']}, k={ps['k']})"
            )
        print()

    # --- 2. Per-shift-type breakdown ---
    print("\n## 2. Per-Shift-Type Accuracy (baseline condition)\n")
    for name, results in all_results.items():
        if "no-camera" in name:
            continue
        print(f"### {name}\n")
        print(f"| Shift type | Scenarios | Trials | Accuracy | 95% CI |")
        print(f"| --- | ---: | ---: | ---: | --- |")
        breakdown = per_shift_type_accuracy(results, condition="baseline")
        for b in breakdown:
            print(
                f"| `{b.cue_type}` | {b.n_scenarios} | {b.n_trials} | "
                f"{b.accuracy * 100:.1f}% | "
                f"[{b.ci.lower * 100:.1f}–{b.ci.upper * 100:.1f}] |"
            )
        print()

    # --- 3. McNemar's paired model comparison ---
    name_a, name_b = PAIRED_COMPARISON
    print(f"\n## 3. McNemar's Paired Model Comparison ({name_a} vs {name_b})\n")
    if name_a in all_results and name_b in all_results:
        results_a = all_results[name_a]
        results_b = all_results[name_b]
        mcnemar = mcnemar_test(results_a, results_b, condition="baseline")
        print(f"  Discordant pairs: {mcnemar.n_discordant}")
        print(f"    A correct, B incorrect: {mcnemar.b}")
        print(f"    A incorrect, B correct: {mcnemar.c}")
        print(f"  Concordant pairs: {mcnemar.n_concordant}")
        print(f"  chi-squared (continuity corrected): {mcnemar.chi2:.3f}")
        print(f"  p-value: {mcnemar.p_value:.4f}")
        print(f"  Interpretation: {mcnemar.interpretation}")
    else:
        print(f"  Cannot compute - need both {name_a} and {name_b}.")

    # --- 4. Empirical difficulty grounding ---
    print("\n\n## 4. Empirical Difficulty Grounding\n")
    cross_family_runs = [
        all_results[name] for name in EMPIRICAL_DIFFICULTY_RUNS
        if name in all_results
    ]
    if cross_family_runs:
        emp = empirical_difficulty(
            cross_family_runs, scenario_tiers, condition="baseline"
        )
        # Compute agreement between author and empirical tiers
        agree = sum(1 for e in emp if e.author_tier == e.empirical_tier)
        total = len(emp)
        print(f"Author vs empirical tier agreement: {agree}/{total} "
              f"({agree / total * 100:.0f}%)\n")
        print(f"| Scenario | Author tier | Pass rate | Empirical tier | Match |")
        print(f"| --- | --- | ---: | --- | --- |")
        for e in emp:
            match = "✓" if e.author_tier == e.empirical_tier else "✗"
            print(
                f"| {e.scenario_id} | {e.author_tier} | "
                f"{e.pass_rate * 100:.0f}% ({e.n_trials} trials) | "
                f"{e.empirical_tier} | {match} |"
            )
        
        # Summary of mismatches
        mismatches = [e for e in emp if e.author_tier != e.empirical_tier]
        if mismatches:
            print(f"\n### Mismatches ({len(mismatches)}):\n")
            for e in mismatches:
                print(
                    f"  {e.scenario_id}: author={e.author_tier}, "
                    f"empirical={e.empirical_tier} "
                    f"(pass rate {e.pass_rate * 100:.0f}%)"
                )

    # --- 5. Minimum detectable effect ---
    print("\n\n## 5. Statistical Power Disclosure\n")
    n_baseline = 50 * 5  # 50 scenarios x 5 trials per cell (v1 default)
    mde = minimum_detectable_effect(n_baseline)
    print(
        f"  Observations per model under baseline: {n_baseline} "
        f"(50 scenarios x 5 trials)"
    )
    print(
        f"  Minimum detectable effect (80% power, 95% CI): "
        f"~{mde * 100:.0f} percentage points"
    )
    print(
        f"\n  Interpretation: Score differences below ~{mde * 100:.0f}pp "
        f"may not be statistically reliable at this sample size."
    )

    # --- 6. Coverage matrix ---
    print("\n\n## 6. Coverage Matrix (shift type × difficulty × target)\n")
    matrix: dict[tuple[str, str, str], int] = {}
    for sid, s in scenarios.items():
        key = (s["cue_type"], s["difficulty_tier"], s["target_context"])
        matrix[key] = matrix.get(key, 0) + 1

    cue_types = sorted({k[0] for k in matrix})
    difficulties = ["easy", "medium", "hard"]
    targets = sorted({k[2] for k in matrix})

    print(f"| Shift type | Target | easy | medium | hard | Total |")
    print(f"| --- | --- | ---: | ---: | ---: | ---: |")
    for ct in cue_types:
        for tgt in targets:
            cells = [matrix.get((ct, d, tgt), 0) for d in difficulties]
            if sum(cells) > 0:
                total = sum(cells)
                print(
                    f"| `{ct}` | `{tgt}` | "
                    + " | ".join(str(c) if c > 0 else "—" for c in cells)
                    + f" | {total} |"
                )

    # Flag gaps
    print("\n### Coverage gaps (empty cells where scenarios could exist):")
    gaps = []
    for ct in cue_types:
        for tgt in ["current", "prior"]:
            for d in difficulties:
                if matrix.get((ct, d, tgt), 0) == 0:
                    gaps.append(f"  {ct} × {tgt} × {d}")
    if gaps:
        for g in gaps:
            print(g)
    else:
        print("  None — all scored-policy cells are populated.")


if __name__ == "__main__":
    main()
