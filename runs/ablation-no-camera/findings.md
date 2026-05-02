# Wearable Assistant Context Bench: Findings

**Benchmark:** context-tracking benchmark for multimodal AI assistants used actively for advice or coaching (wearable or handheld)

## Benchmark summary

- **Benchmark**: context-tracking benchmark for multimodal AI assistants used actively for advice or coaching (wearable or handheld)
- **Default comparison condition**: `baseline`
- **Primary score** (balanced Turn 2 accuracy): **14.4% (95% CI 9.1%–19.7%)**
- **How to read this run**: compare candidate models on the `baseline` score below; treat the other conditions as diagnostic sensitivity checks. CIs are 95% Wilson per class and 95% normal-approximation on the balanced mean.
- **Per-class accuracy under `baseline`**:
    - `current`: 12.1% (95% CI 8.0%–18.0%)
    - `prior`: 16.7% (95% CI 9.3%–28.0%)

Condition sensitivity (balanced Turn 2 accuracy):

| Condition | Balanced Turn 2 accuracy (95% CI) |
| --- | --- |
| baseline (default) | 14.4% (95% CI 9.1%–19.7%) |
| condition_a | 33.3% (95% CI 26.4%–40.3%) |
| condition_b | 86.4% (95% CI 83.0%–89.8%) |

## Per-class pass rate by condition

| Class | baseline | condition_a | condition_b |
| --- | --- | --- | --- |
| `current` | 12.1% [95% CI 8.0–18.0] (20/165) | 33.3% [95% CI 26.6–40.8] (55/165) | 72.7% [95% CI 65.5–78.9] (120/165) |
| `prior` | 16.7% [95% CI 9.3–28.0] (10/60) | 33.3% [95% CI 22.7–45.9] (20/60) | 100.0% [95% CI 94.0–100.0] (60/60) |
| `clarify` (auxiliary) | 100.0% [95% CI 79.6–100.0] (15/15) | 100.0% [95% CI 79.6–100.0] (15/15) | 0.0% [95% CI 0.0–20.4] (0/15) |
| `abstain` (auxiliary) | 50.0% [95% CI 23.7–76.3] (5/10) | 100.0% [95% CI 72.2–100.0] (10/10) | 0.0% [95% CI 0.0–27.8] (0/10) |

## Simulated repair rate by condition

| Condition | Repair rate (95% CI) |
| --- | --- |
| baseline | 35.0% [95% CI 28.7–41.8] (70 / 200) |
| condition_a | 56.7% [95% CI 48.7–64.3] (85 / 150) |
| condition_b | 71.4% [95% CI 59.9–80.7] (50 / 70) |

## Code-judge disagreement by scenario

- sc-01: 5 trial(s) with code/judge disagreement
- sc-02: 5 trial(s) with code/judge disagreement
- sc-03: 0 trial(s) with code/judge disagreement
- sc-04: 0 trial(s) with code/judge disagreement
- sc-05: 0 trial(s) with code/judge disagreement
- sc-06: 0 trial(s) with code/judge disagreement
- sc-07: 5 trial(s) with code/judge disagreement
- sc-08: 10 trial(s) with code/judge disagreement
- sc-09: 0 trial(s) with code/judge disagreement
- sc-10: 10 trial(s) with code/judge disagreement
- sc-11: 5 trial(s) with code/judge disagreement
- sc-12: 0 trial(s) with code/judge disagreement
- sc-13: 0 trial(s) with code/judge disagreement
- sc-14: 10 trial(s) with code/judge disagreement
- sc-15: 10 trial(s) with code/judge disagreement
- sc-16: 0 trial(s) with code/judge disagreement
- sc-17: 5 trial(s) with code/judge disagreement
- sc-18: 0 trial(s) with code/judge disagreement
- sc-19: 0 trial(s) with code/judge disagreement
- sc-20: 0 trial(s) with code/judge disagreement
- sc-21: 5 trial(s) with code/judge disagreement
- sc-22: 5 trial(s) with code/judge disagreement
- sc-23: 10 trial(s) with code/judge disagreement
- sc-24: 0 trial(s) with code/judge disagreement
- sc-25: 5 trial(s) with code/judge disagreement
- sc-26: 15 trial(s) with code/judge disagreement
- sc-27: 5 trial(s) with code/judge disagreement
- sc-28: 5 trial(s) with code/judge disagreement
- sc-29: 0 trial(s) with code/judge disagreement
- sc-30: 0 trial(s) with code/judge disagreement
- sc-31: 0 trial(s) with code/judge disagreement
- sc-32: 5 trial(s) with code/judge disagreement
- sc-33: 10 trial(s) with code/judge disagreement
- sc-34: 0 trial(s) with code/judge disagreement
- sc-35: 0 trial(s) with code/judge disagreement
- sc-36: 0 trial(s) with code/judge disagreement
- sc-37: 5 trial(s) with code/judge disagreement
- sc-38: 0 trial(s) with code/judge disagreement
- sc-39: 0 trial(s) with code/judge disagreement
- sc-40: 0 trial(s) with code/judge disagreement
- sc-41: 10 trial(s) with code/judge disagreement
- sc-42: 5 trial(s) with code/judge disagreement
- sc-43: 5 trial(s) with code/judge disagreement
- sc-44: 0 trial(s) with code/judge disagreement
- sc-45: 5 trial(s) with code/judge disagreement
- sc-46: 0 trial(s) with code/judge disagreement
- sc-47: 5 trial(s) with code/judge disagreement
- sc-48: 0 trial(s) with code/judge disagreement
- sc-49: 0 trial(s) with code/judge disagreement
- sc-50: 10 trial(s) with code/judge disagreement

## Inter-judge agreement (cross-LLM)

_No ranking-judge labels in this run. To enable cross-LLM inter-judge agreement, pass `--ranking-judge-family` to the runner so every trial is also labeled by a fixed second judge._

## Scenario-by-condition matrix

| Scenario | Target context | baseline | condition_a | condition_b |
| --- | --- | --- | --- | --- |
| sc-01 | `current` | fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass | fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass | pass, pass, pass, pass, pass |
| sc-02 | `current` | fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass |
| sc-03 | `current` | fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass | fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass | pass, pass, pass, pass, pass |
| sc-04 | `prior` | fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail | fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass | pass, pass, pass, pass, pass |
| sc-05 | `current` | fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass | fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass | pass, pass, pass, pass, pass |
| sc-06 | `current` | pass, pass, pass, pass, pass | fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail | pass, pass, pass, pass, pass |
| sc-07 | `current` | fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass | fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass | fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass |
| sc-08 | `current` | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass |
| sc-09 | `clarify` | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass | fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass |
| sc-10 | `current` | fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail | fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass | pass, pass, pass, pass, pass |
| sc-11 | `current` | fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass | fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass | fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass |
| sc-12 | `prior` | fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail | fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail | pass, pass, pass, pass, pass |
| sc-13 | `current` | fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail | fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail | fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass |
| sc-14 | `current` | fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass | fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass | pass, pass, pass, pass, pass |
| sc-15 | `current` | pass, pass, pass, pass, pass | fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail | pass, pass, pass, pass, pass |
| sc-16 | `prior` | fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail | fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail | pass, pass, pass, pass, pass |
| sc-17 | `current` | fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass |
| sc-18 | `current` | fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail | fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail | pass, pass, pass, pass, pass |
| sc-19 | `prior` | fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail | fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail | pass, pass, pass, pass, pass |
| sc-20 | `current` | fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass |
| sc-21 | `current` | fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail | fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass | pass, pass, pass, pass, pass |
| sc-22 | `current` | fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass |
| sc-23 | `current` | fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail | fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass | pass, pass, pass, pass, pass |
| sc-24 | `prior` | fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail | fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail | pass, pass, pass, pass, pass |
| sc-25 | `current` | fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass | fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass | pass, pass, pass, pass, pass |
| sc-26 | `current` | fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass |
| sc-27 | `current` | fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail | pass, pass, pass, pass, pass | fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail |
| sc-28 | `current` | fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass | fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass | pass, pass, pass, pass, pass |
| sc-29 | `current` | fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail | fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass | pass, pass, pass, pass, pass |
| sc-30 | `current` | fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail | fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass | fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass |
| sc-31 | `prior` | fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail | fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail | pass, pass, pass, pass, pass |
| sc-32 | `clarify` | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass | fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail |
| sc-33 | `current` | fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail | fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass | fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass |
| sc-34 | `current` | fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail | pass, pass, pass, pass, pass | fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass |
| sc-35 | `current` | fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass | fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail | fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail |
| sc-36 | `current` | fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass |
| sc-37 | `prior` | fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass |
| sc-38 | `prior` | pass, pass, pass, pass, pass | fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail | pass, pass, pass, pass, pass |
| sc-39 | `abstain` | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass | fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass |
| sc-40 | `current` | pass, pass, pass, pass, pass | fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass | pass, pass, pass, pass, pass |
| sc-41 | `clarify` | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass | fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass |
| sc-42 | `abstain` | fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail | pass, pass, pass, pass, pass | fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail |
| sc-43 | `current` | fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass | fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass | pass, pass, pass, pass, pass |
| sc-44 | `current` | fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass |
| sc-45 | `current` | fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail | fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail | fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass |
| sc-46 | `prior` | fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail | fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail | pass, pass, pass, pass, pass |
| sc-47 | `prior` | fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass |
| sc-48 | `prior` | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass |
| sc-49 | `prior` | fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass |
| sc-50 | `current` | fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass |

## Reproducibility manifest

```json
{
  "benchmark_version": "v1",
  "scenarios_sha256": "c8a5011421662e107c3c62c7f3365f26fd693a2749ec26290a15e1ea93c0dbc5",
  "expected_answers_sha256": "d08c03bd0b3a82cca98a7c9ba5cd4d03062bdb2de1ac4dee79c06e356fb93cc9",
  "interventions_sha256": "374ca5837b4ca75cfa2f6b2fd65769c23ccefcf04697b29af19e109a7f6bebe9",
  "judge_prompt_version": "v1.1.0",
  "candidate_model": "gemini/gemini-2.5-flash-lite",
  "judge_model": "gemini/gemini-2.5-flash-lite",
  "judge_family": "gemini",
  "trials": 5,
  "temperature": 0.0,
  "ranking_condition": "baseline",
  "timestamp_utc": "2026-04-27T03:11:57+00:00",
  "runner_git_commit": "acb456415ed5c1d7fe799552a933169c187e5b68",
  "random_seed": null,
  "schema_revision": 3,
  "pack": "canonical",
  "camera_injection": false,
  "judge_prompt_sha256": "16bd055abe42bd3218da043be3f87d213f58b50ab53e8ec0d7c1df4b121eff6c",
  "judge_family_resolution": "explicit",
  "ranking_judge_model": null,
  "ranking_judge_family": null,
  "manifest_warnings": []
}
```
