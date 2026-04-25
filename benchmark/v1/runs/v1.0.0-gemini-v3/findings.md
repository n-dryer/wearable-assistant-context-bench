# Wearable Assistant Context Benchmark: Findings

**Benchmark:** canonical v1 benchmark for cross-turn reference resolution under context change

## Benchmark summary

- **Benchmark**: canonical v1 benchmark for cross-turn reference resolution under context change
- **Default comparison condition**: `baseline`
- **Primary score** (balanced Turn 2 accuracy): **61.7%**
- **How to read this run**: compare candidate models on the `baseline` score below; treat the other conditions as diagnostic sensitivity checks.
- **Per-class accuracy under `baseline`**:
    - `current`: 50.0%
    - `prior`: 73.3%

Condition sensitivity (balanced Turn 2 accuracy):

| Condition | Balanced Turn 2 accuracy |
| --- | --- |
| baseline (default) | 61.7% |
| condition_a | 78.6% |
| condition_b | 78.8% |

## Per-class pass rate by condition

| Class | baseline | condition_a | condition_b |
| --- | --- | --- | --- |
| `current` | 50.0% (21/42) | 57.1% (24/42) | 64.3% (27/42) |
| `prior` | 73.3% (11/15) | 100.0% (15/15) | 93.3% (14/15) |
| `clarify` (auxiliary) | 88.9% (8/9) | 88.9% (8/9) | 77.8% (7/9) |
| `abstain` (auxiliary) | 100.0% (8/8) | 100.0% (8/8) | 100.0% (8/8) |

## Simulated repair rate by condition

| Condition | Repair rate (repaired / failures) |
| --- | --- |
| baseline | 88.5% (23 / 26) |
| condition_a | 73.7% (14 / 19) |
| condition_b | 94.4% (17 / 18) |

## Code-judge disagreement by scenario

- sc-01: 1 trial(s) with code/judge disagreement
- sc-02: 2 trial(s) with code/judge disagreement
- sc-03: 0 trial(s) with code/judge disagreement
- sc-04: 1 trial(s) with code/judge disagreement
- sc-05: 1 trial(s) with code/judge disagreement
- sc-06: 1 trial(s) with code/judge disagreement
- sc-07: 0 trial(s) with code/judge disagreement
- sc-08: 1 trial(s) with code/judge disagreement
- sc-09: 0 trial(s) with code/judge disagreement
- sc-10: 1 trial(s) with code/judge disagreement
- sc-12: 2 trial(s) with code/judge disagreement
- sc-13: 3 trial(s) with code/judge disagreement
- sc-14: 1 trial(s) with code/judge disagreement
- sc-15: 1 trial(s) with code/judge disagreement
- sc-16: 3 trial(s) with code/judge disagreement
- sc-17: 0 trial(s) with code/judge disagreement
- sc-18: 0 trial(s) with code/judge disagreement
- sc-19: 1 trial(s) with code/judge disagreement
- sc-20: 2 trial(s) with code/judge disagreement
- sc-21: 1 trial(s) with code/judge disagreement
- sc-22: 1 trial(s) with code/judge disagreement
- sc-23: 0 trial(s) with code/judge disagreement
- sc-25: 0 trial(s) with code/judge disagreement
- sc-26: 1 trial(s) with code/judge disagreement
- sc-27: 0 trial(s) with code/judge disagreement
- sc-30: 0 trial(s) with code/judge disagreement
- sc-32: 0 trial(s) with code/judge disagreement
- sc-33: 1 trial(s) with code/judge disagreement
- sc-34: 2 trial(s) with code/judge disagreement
- sc-35: 2 trial(s) with code/judge disagreement
- sc-36: 0 trial(s) with code/judge disagreement
- sc-37: 0 trial(s) with code/judge disagreement
- sc-38: 0 trial(s) with code/judge disagreement
- sc-39: 0 trial(s) with code/judge disagreement
- sc-40: 0 trial(s) with code/judge disagreement
- sc-41: 0 trial(s) with code/judge disagreement
- sc-42: 1 trial(s) with code/judge disagreement
- sc-43: 2 trial(s) with code/judge disagreement
- sc-44: 1 trial(s) with code/judge disagreement
- sc-45: 1 trial(s) with code/judge disagreement
- sc-46: 2 trial(s) with code/judge disagreement
- sc-47: 0 trial(s) with code/judge disagreement
- sc-48: 0 trial(s) with code/judge disagreement
- sc-49: 0 trial(s) with code/judge disagreement
- sc-50: 2 trial(s) with code/judge disagreement
- sc-51: 1 trial(s) with code/judge disagreement
- sc-53: 1 trial(s) with code/judge disagreement
- sc-54: 2 trial(s) with code/judge disagreement
- sc-55: 1 trial(s) with code/judge disagreement
- sc-56: 1 trial(s) with code/judge disagreement
- sc-57: 0 trial(s) with code/judge disagreement
- sc-59: 0 trial(s) with code/judge disagreement
- sc-60: 0 trial(s) with code/judge disagreement
- sc-63: 2 trial(s) with code/judge disagreement
- sc-64: 0 trial(s) with code/judge disagreement
- sc-65: 0 trial(s) with code/judge disagreement
- sc-66: 1 trial(s) with code/judge disagreement
- sc-67: 0 trial(s) with code/judge disagreement
- sc-69: 0 trial(s) with code/judge disagreement
- sc-71: 2 trial(s) with code/judge disagreement
- sc-73: 1 trial(s) with code/judge disagreement
- sc-74: 0 trial(s) with code/judge disagreement
- sc-76: 0 trial(s) with code/judge disagreement
- sc-77: 0 trial(s) with code/judge disagreement
- sc-78: 0 trial(s) with code/judge disagreement
- sc-79: 0 trial(s) with code/judge disagreement
- sc-81: 0 trial(s) with code/judge disagreement
- sc-82: 1 trial(s) with code/judge disagreement
- sc-83: 3 trial(s) with code/judge disagreement
- sc-84: 0 trial(s) with code/judge disagreement
- sc-85: 2 trial(s) with code/judge disagreement
- sc-86: 2 trial(s) with code/judge disagreement
- sc-87: 0 trial(s) with code/judge disagreement
- sc-88: 1 trial(s) with code/judge disagreement

## Scenario-by-condition matrix

| Scenario | Target context | baseline | condition_a | condition_b |
| --- | --- | --- | --- | --- |
| sc-01 | `current` | fail→repair-pass | fail→repair-pass | fail→repair-pass |
| sc-02 | `current` | fail→repair-pass | fail→repair-fail | fail→repair-pass |
| sc-03 | `prior` | pass | pass | pass |
| sc-04 | `current` | fail→repair-pass | pass | fail→repair-pass |
| sc-05 | `current` | pass | fail→repair-pass | fail→repair-fail |
| sc-06 | `current` | fail→repair-pass | fail→repair-pass | pass |
| sc-07 | `current` | pass | pass | pass |
| sc-08 | `current` | pass | fail→repair-pass | pass |
| sc-09 | `prior` | pass | pass | pass |
| sc-10 | `current` | fail→repair-fail | fail→repair-pass | pass |
| sc-12 | `current` | fail→repair-pass | fail→repair-pass | pass |
| sc-13 | `current` | pass | pass | fail→repair-pass |
| sc-14 | `current` | fail→repair-pass | pass | fail→repair-pass |
| sc-15 | `current` | pass | pass | pass |
| sc-16 | `current` | fail→repair-pass | fail→repair-pass | fail→repair-pass |
| sc-17 | `current` | fail→repair-pass | pass | pass |
| sc-18 | `current` | pass | fail→repair-fail | pass |
| sc-19 | `current` | pass | pass | pass |
| sc-20 | `current` | pass | fail→repair-pass | pass |
| sc-21 | `current` | pass | pass | pass |
| sc-22 | `current` | fail→repair-pass | fail→repair-pass | fail→repair-pass |
| sc-23 | `current` | pass | pass | pass |
| sc-25 | `prior` | pass | pass | pass |
| sc-26 | `prior` | fail→repair-pass | pass | pass |
| sc-27 | `prior` | pass | pass | pass |
| sc-30 | `prior` | pass | pass | pass |
| sc-32 | `prior` | pass | pass | pass |
| sc-33 | `clarify` | pass | pass | pass |
| sc-34 | `clarify` | pass | pass | pass |
| sc-35 | `clarify` | fail→repair-pass | pass | fail→repair-pass |
| sc-36 | `clarify` | pass | pass | fail→repair-pass |
| sc-37 | `clarify` | pass | fail→repair-pass | pass |
| sc-38 | `abstain` | pass | pass | pass |
| sc-39 | `abstain` | pass | pass | pass |
| sc-40 | `abstain` | pass | pass | pass |
| sc-41 | `abstain` | pass | pass | pass |
| sc-42 | `current` | fail→repair-pass | fail→repair-pass | fail→repair-pass |
| sc-43 | `current` | fail→repair-pass | fail→repair-fail | pass |
| sc-44 | `current` | pass | pass | fail→repair-pass |
| sc-45 | `current` | pass | fail→repair-fail | pass |
| sc-46 | `current` | fail→repair-pass | pass | fail→repair-pass |
| sc-47 | `current` | fail→repair-pass | pass | fail→repair-pass |
| sc-48 | `current` | pass | pass | pass |
| sc-49 | `current` | pass | pass | pass |
| sc-50 | `current` | pass | pass | fail→repair-pass |
| sc-51 | `current` | pass | pass | pass |
| sc-53 | `current` | pass | pass | pass |
| sc-54 | `current` | fail→repair-fail | pass | pass |
| sc-55 | `current` | pass | pass | pass |
| sc-56 | `current` | fail→repair-pass | pass | fail→repair-pass |
| sc-57 | `current` | pass | fail→repair-fail | pass |
| sc-59 | `prior` | pass | pass | pass |
| sc-60 | `prior` | pass | pass | pass |
| sc-63 | `prior` | fail→repair-pass | pass | fail→repair-pass |
| sc-64 | `prior` | fail→repair-pass | pass | pass |
| sc-65 | `prior` | pass | pass | pass |
| sc-66 | `prior` | fail→repair-pass | pass | pass |
| sc-67 | `prior` | pass | pass | pass |
| sc-69 | `prior` | pass | pass | pass |
| sc-71 | `clarify` | pass | pass | pass |
| sc-73 | `clarify` | pass | pass | pass |
| sc-74 | `clarify` | pass | pass | pass |
| sc-76 | `clarify` | pass | pass | pass |
| sc-77 | `abstain` | pass | pass | pass |
| sc-78 | `abstain` | pass | pass | pass |
| sc-79 | `abstain` | pass | pass | pass |
| sc-81 | `abstain` | pass | pass | pass |
| sc-82 | `current` | fail→repair-pass | fail→repair-pass | pass |
| sc-83 | `current` | pass | fail→repair-pass | pass |
| sc-84 | `current` | fail→repair-pass | fail→repair-pass | pass |
| sc-85 | `current` | fail→repair-pass | pass | pass |
| sc-86 | `current` | fail→repair-pass | pass | fail→repair-pass |
| sc-87 | `current` | pass | pass | pass |
| sc-88 | `current` | fail→repair-fail | pass | pass |

## Reproducibility manifest

```json
{
  "benchmark_version": "v1.0.0",
  "scenarios_sha256": null,
  "expected_answers_sha256": null,
  "interventions_sha256": null,
  "judge_prompt_version": "v1.0.0",
  "candidate_model": "gemini-2.5-flash-lite",
  "judge_model": "gemini-2.5-flash-lite",
  "judge_family": "gemini",
  "trials": null,
  "temperature": 0.0,
  "ranking_condition": null,
  "timestamp_utc": null,
  "runner_git_commit": null,
  "random_seed": null,
  "judge_resolution_mode": "explicit",
  "trials_per_cell": 1,
  "scenarios_attempted": 74,
  "scenarios_total": 101,
  "note": "Partial run: sc-89+ stalled due to Gemini API SSL timeouts. 74/101 scenarios complete.",
  "manifest_warnings": [
    "manifest key missing: scenarios_sha256",
    "manifest key missing: expected_answers_sha256",
    "manifest key missing: interventions_sha256",
    "manifest key missing: trials",
    "manifest key missing: ranking_condition",
    "manifest key missing: timestamp_utc",
    "manifest key missing: runner_git_commit",
    "manifest key missing: random_seed"
  ]
}
```
