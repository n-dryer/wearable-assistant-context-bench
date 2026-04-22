# Wearable Assistant Context Benchmark: Findings

**Slice:** v1 runnable slice (with-prior-Q; reference-state selection under implicit context shift)

> **Note:** this is an illustrative example run, not a reported score.
> Numbers here are plausible for a current-generation frontier model
> on v1 but are not from a real API run. Use this file to understand
> the report shape, not to rank models. Real runs emit the same
> layout with their own numbers.

## Benchmark summary

- **Benchmark slice**: v1 runnable slice (with-prior-Q; reference-state selection under implicit context shift)
- **Ranking condition**: `baseline`
- **Primary score** (balanced Turn 2 accuracy): **68.8%**
- **How to read this run**: compare candidate models on the `baseline` score below; treat the other conditions as diagnostic sensitivity checks.
- **Per-class accuracy under `baseline`**:
    - `current`: 87.5%
    - `prior`: 50.0%

Condition sensitivity (balanced Turn 2 accuracy):

| Condition | Balanced Turn 2 accuracy |
| --- | --- |
| baseline (ranking) | 68.8% |
| condition_a | 80.2% |
| condition_b | 77.1% |

The gap between `baseline` and `condition_a` (an instruction that tells the model to pick the right context before answering) is diagnostic: the candidate can make the right call when prompted to, but does not default to it. This is the pattern reference-resolution pilots consistently surface.

## Per-class pass rate by condition

| Class | baseline | condition_a | condition_b |
| --- | --- | --- | --- |
| `current` | 87.5% (14/16) | 93.8% (15/16) | 87.5% (14/16) |
| `prior` | 50.0% (3/6) | 66.7% (4/6) | 66.7% (4/6) |
| `clarify` (diagnostic) | diagnostic-only in v1; trials in this row count as wrong for the primary score | diagnostic-only in v1; trials in this row count as wrong for the primary score | diagnostic-only in v1; trials in this row count as wrong for the primary score |
| `abstain` (diagnostic) | diagnostic-only in v1; trials in this row count as wrong for the primary score | diagnostic-only in v1; trials in this row count as wrong for the primary score | diagnostic-only in v1; trials in this row count as wrong for the primary score |

## Simulated repair rate by condition

| Condition | Repair rate (repaired / failures) |
| --- | --- |
| baseline | 60.0% (3 / 5) |
| condition_a | 66.7% (2 / 3) |
| condition_b | 50.0% (2 / 4) |

## Code-judge disagreement by scenario

- sc-01: 0 trial(s) with code/judge disagreement
- sc-02: 0 trial(s) with code/judge disagreement
- sc-03: 1 trial(s) with code/judge disagreement
- sc-04: 0 trial(s) with code/judge disagreement
- sc-05: 0 trial(s) with code/judge disagreement
- sc-06: 0 trial(s) with code/judge disagreement
- sc-07: 0 trial(s) with code/judge disagreement
- sc-08: 0 trial(s) with code/judge disagreement
- sc-09: 1 trial(s) with code/judge disagreement
- sc-10: 0 trial(s) with code/judge disagreement
- sc-11: 0 trial(s) with code/judge disagreement

## Scenario-by-condition matrix

| Scenario | Target context | baseline | condition_a | condition_b |
| --- | --- | --- | --- | --- |
| sc-01 | `current` | pass, pass | pass, pass | pass, pass |
| sc-02 | `current` | pass, pass | pass, pass | pass, pass |
| sc-03 | `prior` | pass, fail→repair-pass | fail→repair-pass, pass | fail→repair-fail, pass |
| sc-04 | `current` | pass, pass | pass, pass | pass, pass |
| sc-05 | `current` | fail→repair-pass, pass | pass, pass | pass, pass |
| sc-06 | `current` | pass, pass | pass, pass | pass, pass |
| sc-07 | `current` | pass, pass | pass, pass | pass, pass |
| sc-08 | `current` | pass, pass | pass, pass | fail→repair-pass, pass |
| sc-09 | `prior` | fail→repair-fail, pass | pass, pass | fail→repair-pass, pass |
| sc-10 | `current` | pass, pass | pass, pass | pass, pass |
| sc-11 | `prior` | fail→repair-pass, fail→repair-fail | fail→repair-pass, pass | pass, pass |

`pass` means Turn 2 matched the target context. `fail→repair-pass` means Turn 2 missed but the Turn 3 repair anchor recovered the right context. `fail→repair-fail` means both turns missed. Only Turn 2 outcomes count for the primary score.

Reading the matrix: the candidate is almost flawless on `current`-target scenarios. The `prior`-target scenarios (sc-03, sc-09, sc-11) are where baseline struggles — the model tends to answer from the visible current scene instead of reaching back, or asks a clarifying question (counted as wrong). `condition_a` and `condition_b` close most of that gap.

## Reproducibility manifest

```json
{
  "benchmark_version": "v1",
  "scenarios_sha256": "EXAMPLE-REPLACE-ON-REAL-RUN",
  "expected_answers_sha256": "EXAMPLE-REPLACE-ON-REAL-RUN",
  "interventions_sha256": "EXAMPLE-REPLACE-ON-REAL-RUN",
  "judge_prompt_version": "v1",
  "judge_prompt_sha256": "EXAMPLE-REPLACE-ON-REAL-RUN",
  "candidate_model": "example-frontier-model",
  "judge_model": "example-cross-family-judge",
  "judge_family": "openai",
  "judge_family_resolution": "auto",
  "trials": 2,
  "temperature": 0.0,
  "ranking_condition": "baseline",
  "timestamp_utc": "2026-04-21T00:00:00+00:00",
  "runner_git_commit": "EXAMPLE-REPLACE-ON-REAL-RUN",
  "random_seed": null,
  "manifest_warnings": [
    "this is an illustrative example, not a recorded API run"
  ]
}
```
