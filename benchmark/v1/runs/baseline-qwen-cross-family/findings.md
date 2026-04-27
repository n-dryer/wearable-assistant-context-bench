# Wearable Assistant Context Benchmark: Findings

**Benchmark:** context-tracking benchmark for multimodal AI assistants used actively for advice or coaching (wearable or handheld)

## Benchmark summary

- **Benchmark**: context-tracking benchmark for multimodal AI assistants used actively for advice or coaching (wearable or handheld)
- **Default comparison condition**: `baseline`
- **Primary score** (balanced Turn 2 accuracy): **54.2% (95% CI 50.7%–57.7%)**
- **How to read this run**: compare candidate models on the `baseline` score below; treat the other conditions as diagnostic sensitivity checks. CIs are 95% Wilson per class and 95% normal-approximation on the balanced mean.
- **Per-class accuracy under `baseline`**:
    - `current`: 100.0% (95% CI 97.7%–100.0%)
    - `prior`: 8.3% (95% CI 3.6%–18.1%)

Condition sensitivity (balanced Turn 2 accuracy):

| Condition | Balanced Turn 2 accuracy (95% CI) |
| --- | --- |
| baseline (default) | 54.2% (95% CI 50.7%–57.7%) |
| condition_a | 66.7% (95% CI 60.7%–72.6%) |
| condition_b | 79.2% (95% CI 72.9%–85.4%) |

## Per-class pass rate by condition

| Class | baseline | condition_a | condition_b |
| --- | --- | --- | --- |
| `current` | 100.0% [95% CI 97.7–100.0] (165/165) | 100.0% [95% CI 97.7–100.0] (165/165) | 100.0% [95% CI 97.7–100.0] (165/165) |
| `prior` | 8.3% [95% CI 3.6–18.1] (5/60) | 33.3% [95% CI 22.7–45.9] (20/60) | 58.3% [95% CI 45.7–69.9] (35/60) |
| `clarify` (auxiliary) | 33.3% [95% CI 15.2–58.3] (5/15) | 0.0% [95% CI 0.0–20.4] (0/15) | 33.3% [95% CI 15.2–58.3] (5/15) |
| `abstain` (auxiliary) | 50.0% [95% CI 23.7–76.3] (5/10) | 50.0% [95% CI 23.7–76.3] (5/10) | 0.0% [95% CI 0.0–27.8] (0/10) |

## Simulated repair rate by condition

| Condition | Repair rate (95% CI) |
| --- | --- |
| baseline | 42.9% [95% CI 31.9–54.5] (30 / 70) |
| condition_a | 25.0% [95% CI 15.8–37.2] (15 / 60) |
| condition_b | 33.3% [95% CI 21.4–47.9] (15 / 45) |

## Code-judge disagreement by scenario

- sc-01: 0 trial(s) with code/judge disagreement
- sc-02: 0 trial(s) with code/judge disagreement
- sc-03: 0 trial(s) with code/judge disagreement
- sc-04: 10 trial(s) with code/judge disagreement
- sc-05: 0 trial(s) with code/judge disagreement
- sc-06: 0 trial(s) with code/judge disagreement
- sc-07: 0 trial(s) with code/judge disagreement
- sc-08: 0 trial(s) with code/judge disagreement
- sc-09: 10 trial(s) with code/judge disagreement
- sc-10: 0 trial(s) with code/judge disagreement
- sc-11: 0 trial(s) with code/judge disagreement
- sc-12: 0 trial(s) with code/judge disagreement
- sc-13: 0 trial(s) with code/judge disagreement
- sc-14: 0 trial(s) with code/judge disagreement
- sc-15: 0 trial(s) with code/judge disagreement
- sc-16: 0 trial(s) with code/judge disagreement
- sc-17: 0 trial(s) with code/judge disagreement
- sc-18: 0 trial(s) with code/judge disagreement
- sc-19: 0 trial(s) with code/judge disagreement
- sc-20: 0 trial(s) with code/judge disagreement
- sc-21: 0 trial(s) with code/judge disagreement
- sc-22: 0 trial(s) with code/judge disagreement
- sc-23: 0 trial(s) with code/judge disagreement
- sc-24: 10 trial(s) with code/judge disagreement
- sc-25: 0 trial(s) with code/judge disagreement
- sc-26: 0 trial(s) with code/judge disagreement
- sc-27: 0 trial(s) with code/judge disagreement
- sc-28: 0 trial(s) with code/judge disagreement
- sc-29: 0 trial(s) with code/judge disagreement
- sc-30: 0 trial(s) with code/judge disagreement
- sc-31: 0 trial(s) with code/judge disagreement
- sc-32: 15 trial(s) with code/judge disagreement
- sc-33: 0 trial(s) with code/judge disagreement
- sc-34: 0 trial(s) with code/judge disagreement
- sc-35: 0 trial(s) with code/judge disagreement
- sc-36: 0 trial(s) with code/judge disagreement
- sc-37: 0 trial(s) with code/judge disagreement
- sc-38: 0 trial(s) with code/judge disagreement
- sc-39: 0 trial(s) with code/judge disagreement
- sc-40: 0 trial(s) with code/judge disagreement
- sc-41: 5 trial(s) with code/judge disagreement
- sc-42: 0 trial(s) with code/judge disagreement
- sc-43: 0 trial(s) with code/judge disagreement
- sc-44: 0 trial(s) with code/judge disagreement
- sc-45: 0 trial(s) with code/judge disagreement
- sc-46: 0 trial(s) with code/judge disagreement
- sc-47: 0 trial(s) with code/judge disagreement
- sc-48: 5 trial(s) with code/judge disagreement
- sc-49: 0 trial(s) with code/judge disagreement
- sc-50: 0 trial(s) with code/judge disagreement

## Inter-judge agreement (cross-LLM)

_No ranking-judge labels in this run. To enable cross-LLM inter-judge agreement, pass `--ranking-judge-family` to the runner so every trial is also labeled by a fixed second judge._

## Scenario-by-condition matrix

| Scenario | Target context | baseline | condition_a | condition_b |
| --- | --- | --- | --- | --- |
| sc-01 | `current` | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass |
| sc-02 | `current` | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass |
| sc-03 | `current` | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass |
| sc-04 | `prior` | fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass |
| sc-05 | `current` | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass |
| sc-06 | `current` | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass |
| sc-07 | `current` | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass |
| sc-08 | `current` | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass |
| sc-09 | `clarify` | pass, pass, pass, pass, pass | fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass | pass, pass, pass, pass, pass |
| sc-10 | `current` | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass |
| sc-11 | `current` | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass |
| sc-12 | `prior` | fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail | fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail | pass, pass, pass, pass, pass |
| sc-13 | `current` | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass |
| sc-14 | `current` | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass |
| sc-15 | `current` | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass |
| sc-16 | `prior` | fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass | fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail | fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass |
| sc-17 | `current` | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass |
| sc-18 | `current` | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass |
| sc-19 | `prior` | fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail | fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail | fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass |
| sc-20 | `current` | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass |
| sc-21 | `current` | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass |
| sc-22 | `current` | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass |
| sc-23 | `current` | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass |
| sc-24 | `prior` | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass | fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail |
| sc-25 | `current` | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass |
| sc-26 | `current` | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass |
| sc-27 | `current` | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass |
| sc-28 | `current` | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass |
| sc-29 | `current` | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass |
| sc-30 | `current` | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass |
| sc-31 | `prior` | fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass | fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail | pass, pass, pass, pass, pass |
| sc-32 | `clarify` | fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail | fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail | fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail |
| sc-33 | `current` | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass |
| sc-34 | `current` | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass |
| sc-35 | `current` | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass |
| sc-36 | `current` | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass |
| sc-37 | `prior` | fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail | fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail | fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail |
| sc-38 | `prior` | fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail | fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail | fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail |
| sc-39 | `abstain` | fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass | pass, pass, pass, pass, pass | fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail |
| sc-40 | `current` | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass |
| sc-41 | `clarify` | fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass | fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass | fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass |
| sc-42 | `abstain` | pass, pass, pass, pass, pass | fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass | fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail |
| sc-43 | `current` | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass |
| sc-44 | `current` | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass |
| sc-45 | `current` | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass |
| sc-46 | `prior` | fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass | fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail | pass, pass, pass, pass, pass |
| sc-47 | `prior` | fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail | fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail | pass, pass, pass, pass, pass |
| sc-48 | `prior` | fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass |
| sc-49 | `prior` | fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass |
| sc-50 | `current` | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass |

## Reproducibility manifest

```json
{
  "benchmark_version": "v1",
  "scenarios_sha256": "c8a5011421662e107c3c62c7f3365f26fd693a2749ec26290a15e1ea93c0dbc5",
  "expected_answers_sha256": "d08c03bd0b3a82cca98a7c9ba5cd4d03062bdb2de1ac4dee79c06e356fb93cc9",
  "interventions_sha256": "374ca5837b4ca75cfa2f6b2fd65769c23ccefcf04697b29af19e109a7f6bebe9",
  "judge_prompt_version": "v1.1.0",
  "candidate_model": "dashscope-intl/qwen3-vl-plus",
  "judge_model": "gemini/gemini-2.5-flash-lite",
  "judge_family": "gemini",
  "trials": 5,
  "temperature": 0.0,
  "ranking_condition": "baseline",
  "timestamp_utc": "2026-04-27T03:33:40+00:00",
  "runner_git_commit": "acb456415ed5c1d7fe799552a933169c187e5b68",
  "random_seed": null,
  "schema_revision": 3,
  "pack": "canonical",
  "camera_injection": true,
  "judge_prompt_sha256": "16bd055abe42bd3218da043be3f87d213f58b50ab53e8ec0d7c1df4b121eff6c",
  "judge_family_resolution": "explicit",
  "ranking_judge_model": null,
  "ranking_judge_family": null,
  "manifest_warnings": []
}
```
