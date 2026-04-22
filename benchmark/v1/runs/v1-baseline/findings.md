# Wearable Assistant Context Benchmark: Findings

> **Note on this example baseline.** Candidate and judge are both
> `gemini-2.5-flash-lite` — same family AND same model. Self-preference
> inflates the absolute score. This run is shipped as a shape example,
> not a credible measurement. Cross-family results land when an
> ANTHROPIC_API_KEY is wired.

**Slice:** v1 runnable slice (with-prior-Q; reference-state selection under implicit context shift)

## Benchmark summary

- **Benchmark slice**: v1 runnable slice (with-prior-Q; reference-state selection under implicit context shift)
- **Ranking condition**: `baseline`
- **Primary score** (balanced Turn 2 accuracy): **70.8%**
- **How to read this run**: compare candidate models on the `baseline` score below; treat the other conditions as diagnostic sensitivity checks.
- **Per-class accuracy under `baseline`**:
    - `current`: 75.0%
    - `prior`: 66.7%

Condition sensitivity (balanced Turn 2 accuracy):

| Condition | Balanced Turn 2 accuracy |
| --- | --- |
| baseline (ranking) | 70.8% |
| condition_a | 87.5% |
| condition_b | 87.5% |

## Per-class pass rate by condition

| Class | baseline | condition_a | condition_b |
| --- | --- | --- | --- |
| `current` | 75.0% (12/16) | 75.0% (12/16) | 75.0% (12/16) |
| `prior` | 66.7% (4/6) | 100.0% (6/6) | 100.0% (6/6) |
| `clarify` (diagnostic) | diagnostic-only in v1; trials in this row count as wrong for the primary score | diagnostic-only in v1; trials in this row count as wrong for the primary score | diagnostic-only in v1; trials in this row count as wrong for the primary score |
| `abstain` (diagnostic) | diagnostic-only in v1; trials in this row count as wrong for the primary score | diagnostic-only in v1; trials in this row count as wrong for the primary score | diagnostic-only in v1; trials in this row count as wrong for the primary score |

## Simulated repair rate by condition

| Condition | Repair rate (repaired / failures) |
| --- | --- |
| baseline | 66.7% (4 / 6) |
| condition_a | 100.0% (4 / 4) |
| condition_b | 100.0% (4 / 4) |

## Code-judge disagreement by scenario

- sc-01: 4 trial(s) with code/judge disagreement
- sc-02: 2 trial(s) with code/judge disagreement
- sc-03: 0 trial(s) with code/judge disagreement
- sc-04: 0 trial(s) with code/judge disagreement
- sc-05: 0 trial(s) with code/judge disagreement
- sc-06: 4 trial(s) with code/judge disagreement
- sc-07: 2 trial(s) with code/judge disagreement
- sc-08: 2 trial(s) with code/judge disagreement
- sc-09: 0 trial(s) with code/judge disagreement
- sc-10: 2 trial(s) with code/judge disagreement
- sc-11: 0 trial(s) with code/judge disagreement

## Scenario-by-condition matrix

| Scenario | Target context | baseline | condition_a | condition_b |
| --- | --- | --- | --- | --- |
| sc-01 | `current` | fail→repair-pass, fail→repair-pass | pass, pass | pass, pass |
| sc-02 | `current` | pass, pass | fail→repair-pass, fail→repair-pass | pass, pass |
| sc-03 | `prior` | pass, pass | pass, pass | pass, pass |
| sc-04 | `current` | pass, pass | pass, pass | pass, pass |
| sc-05 | `current` | pass, pass | pass, pass | fail→repair-pass, fail→repair-pass |
| sc-06 | `current` | pass, pass | fail→repair-pass, fail→repair-pass | pass, pass |
| sc-07 | `current` | pass, pass | pass, pass | pass, pass |
| sc-08 | `current` | fail→repair-pass, fail→repair-pass | pass, pass | pass, pass |
| sc-09 | `prior` | fail→repair-fail, fail→repair-fail | pass, pass | pass, pass |
| sc-10 | `current` | pass, pass | pass, pass | fail→repair-pass, fail→repair-pass |
| sc-11 | `prior` | pass, pass | pass, pass | pass, pass |

## Reproducibility manifest

```json
{
  "benchmark_version": "v1",
  "scenarios_sha256": "f3db016582ce6ab683a789b05a55b45581802246fe36c463533167deebded099",
  "expected_answers_sha256": "7a199f45ea192cdc4a2bc8c37e7a9f592d1bb6f28415ae8f6de07a42a80c714f",
  "interventions_sha256": "374ca5837b4ca75cfa2f6b2fd65769c23ccefcf04697b29af19e109a7f6bebe9",
  "judge_prompt_version": "v1.0.0",
  "candidate_model": "gemini-2.5-flash-lite",
  "judge_model": "gemini-2.5-flash-lite",
  "judge_family": "gemini",
  "trials": 2,
  "temperature": 0.0,
  "ranking_condition": "baseline",
  "timestamp_utc": "2026-04-22T06:34:34+00:00",
  "runner_git_commit": "fd736984fe911c359b8dcc372dc653beea4ebeae",
  "random_seed": null,
  "judge_prompt_sha256": "eeb1431ee40e203d63e2d2efe8a80b983dbb63a2483b8fae955cc498612fee98",
  "judge_family_resolution": "explicit",
  "manifest_warnings": []
}
```
