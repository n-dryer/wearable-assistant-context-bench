# Wearable Assistant Context Benchmark: Findings

**Benchmark:** context-tracking benchmark for multimodal wearable assistants

## Benchmark summary

- **Benchmark**: context-tracking benchmark for multimodal wearable assistants
- **Default comparison condition**: `baseline`
- **Primary score** (balanced Turn 2 accuracy): **7.2%**
- **How to read this run**: compare candidate models on the `baseline` score below; treat the other conditions as diagnostic sensitivity checks.
- **Per-class accuracy under `baseline`**:
    - `current`: 6.1%
    - `prior`: 8.3%

Condition sensitivity (balanced Turn 2 accuracy):

| Condition | Balanced Turn 2 accuracy |
| --- | --- |
| baseline (default) | 7.2% |
| condition_a | 28.0% |
| condition_b | 65.5% |

## Per-class pass rate by condition

| Class | baseline | condition_a | condition_b |
| --- | --- | --- | --- |
| `current` | 6.1% (4/66) | 6.1% (4/66) | 39.4% (26/66) |
| `prior` | 8.3% (2/24) | 50.0% (12/24) | 91.7% (22/24) |
| `clarify` (auxiliary) | 100.0% (6/6) | 100.0% (6/6) | 100.0% (6/6) |
| `abstain` (auxiliary) | 100.0% (4/4) | 100.0% (4/4) | 100.0% (4/4) |

## Simulated repair rate by condition

| Condition | Repair rate (repaired / failures) |
| --- | --- |
| baseline | 59.5% (50 / 84) |
| condition_a | 54.1% (40 / 74) |
| condition_b | 42.9% (18 / 42) |

## Code-judge disagreement by scenario

- sc-01: 2 trial(s) with code/judge disagreement
- sc-02: 0 trial(s) with code/judge disagreement
- sc-03: 2 trial(s) with code/judge disagreement
- sc-04: 0 trial(s) with code/judge disagreement
- sc-05: 2 trial(s) with code/judge disagreement
- sc-06: 0 trial(s) with code/judge disagreement
- sc-07: 2 trial(s) with code/judge disagreement
- sc-08: 0 trial(s) with code/judge disagreement
- sc-09: 4 trial(s) with code/judge disagreement
- sc-10: 0 trial(s) with code/judge disagreement
- sc-11: 2 trial(s) with code/judge disagreement
- sc-12: 4 trial(s) with code/judge disagreement
- sc-13: 2 trial(s) with code/judge disagreement
- sc-14: 4 trial(s) with code/judge disagreement
- sc-15: 0 trial(s) with code/judge disagreement
- sc-16: 0 trial(s) with code/judge disagreement
- sc-17: 2 trial(s) with code/judge disagreement
- sc-18: 2 trial(s) with code/judge disagreement
- sc-19: 0 trial(s) with code/judge disagreement
- sc-20: 0 trial(s) with code/judge disagreement
- sc-21: 2 trial(s) with code/judge disagreement
- sc-22: 0 trial(s) with code/judge disagreement
- sc-23: 2 trial(s) with code/judge disagreement
- sc-24: 0 trial(s) with code/judge disagreement
- sc-25: 2 trial(s) with code/judge disagreement
- sc-26: 2 trial(s) with code/judge disagreement
- sc-27: 0 trial(s) with code/judge disagreement
- sc-28: 2 trial(s) with code/judge disagreement
- sc-29: 0 trial(s) with code/judge disagreement
- sc-30: 2 trial(s) with code/judge disagreement
- sc-31: 0 trial(s) with code/judge disagreement
- sc-32: 2 trial(s) with code/judge disagreement
- sc-33: 4 trial(s) with code/judge disagreement
- sc-34: 0 trial(s) with code/judge disagreement
- sc-35: 0 trial(s) with code/judge disagreement
- sc-36: 0 trial(s) with code/judge disagreement
- sc-37: 0 trial(s) with code/judge disagreement
- sc-38: 2 trial(s) with code/judge disagreement
- sc-39: 0 trial(s) with code/judge disagreement
- sc-40: 0 trial(s) with code/judge disagreement
- sc-41: 2 trial(s) with code/judge disagreement
- sc-42: 2 trial(s) with code/judge disagreement
- sc-43: 0 trial(s) with code/judge disagreement
- sc-44: 0 trial(s) with code/judge disagreement
- sc-45: 2 trial(s) with code/judge disagreement
- sc-46: 2 trial(s) with code/judge disagreement
- sc-47: 2 trial(s) with code/judge disagreement
- sc-48: 0 trial(s) with code/judge disagreement
- sc-49: 0 trial(s) with code/judge disagreement
- sc-50: 2 trial(s) with code/judge disagreement

## Scenario-by-condition matrix

| Scenario | Target context | baseline | condition_a | condition_b |
| --- | --- | --- | --- | --- |
| sc-01 | `current` | fail→repair-pass, fail→repair-pass | fail→repair-fail, fail→repair-fail | pass, pass |
| sc-02 | `current` | fail→repair-pass, fail→repair-pass | fail→repair-pass, fail→repair-pass | pass, pass |
| sc-03 | `current` | fail→repair-pass, fail→repair-pass | fail→repair-pass, fail→repair-pass | fail→repair-fail, fail→repair-fail |
| sc-04 | `prior` | fail→repair-fail, fail→repair-fail | fail→repair-pass, fail→repair-pass | fail→repair-fail, fail→repair-fail |
| sc-05 | `current` | fail→repair-pass, fail→repair-pass | fail→repair-pass, fail→repair-pass | fail→repair-pass, fail→repair-pass |
| sc-06 | `current` | fail→repair-fail, fail→repair-fail | fail→repair-fail, fail→repair-fail | fail→repair-fail, fail→repair-fail |
| sc-07 | `current` | fail→repair-pass, fail→repair-pass | fail→repair-pass, fail→repair-pass | fail→repair-fail, fail→repair-fail |
| sc-08 | `current` | fail→repair-pass, fail→repair-pass | fail→repair-fail, fail→repair-fail | fail→repair-fail, fail→repair-fail |
| sc-09 | `clarify` | pass, pass | pass, pass | pass, pass |
| sc-10 | `current` | fail→repair-pass, fail→repair-pass | fail→repair-pass, fail→repair-pass | pass, pass |
| sc-11 | `current` | fail→repair-pass, fail→repair-pass | fail→repair-pass, fail→repair-pass | pass, pass |
| sc-12 | `prior` | fail→repair-fail, fail→repair-fail | fail→repair-pass, fail→repair-pass | pass, pass |
| sc-13 | `current` | fail→repair-fail, fail→repair-fail | pass, pass | pass, pass |
| sc-14 | `current` | fail→repair-fail, fail→repair-fail | fail→repair-pass, fail→repair-pass | pass, pass |
| sc-15 | `current` | pass, pass | fail→repair-pass, fail→repair-pass | pass, pass |
| sc-16 | `prior` | fail→repair-pass, fail→repair-pass | pass, pass | pass, pass |
| sc-17 | `current` | fail→repair-fail, fail→repair-fail | fail→repair-fail, fail→repair-fail | pass, pass |
| sc-18 | `current` | fail→repair-fail, fail→repair-fail | fail→repair-fail, fail→repair-fail | pass, pass |
| sc-19 | `prior` | fail→repair-fail, fail→repair-fail | fail→repair-fail, fail→repair-fail | pass, pass |
| sc-20 | `current` | fail→repair-pass, fail→repair-pass | fail→repair-fail, fail→repair-fail | pass, pass |
| sc-21 | `current` | fail→repair-fail, fail→repair-fail | fail→repair-pass, fail→repair-pass | fail→repair-fail, fail→repair-fail |
| sc-22 | `current` | fail→repair-fail, fail→repair-fail | fail→repair-fail, fail→repair-fail | fail→repair-fail, fail→repair-fail |
| sc-23 | `current` | fail→repair-fail, fail→repair-fail | fail→repair-fail, fail→repair-fail | fail→repair-fail, fail→repair-fail |
| sc-24 | `prior` | fail→repair-pass, fail→repair-pass | fail→repair-fail, fail→repair-fail | pass, pass |
| sc-25 | `current` | fail→repair-pass, fail→repair-pass | fail→repair-pass, fail→repair-pass | fail→repair-fail, fail→repair-fail |
| sc-26 | `current` | fail→repair-fail, fail→repair-fail | fail→repair-fail, fail→repair-fail | fail→repair-pass, fail→repair-pass |
| sc-27 | `current` | fail→repair-fail, fail→repair-fail | fail→repair-fail, fail→repair-fail | fail→repair-fail, fail→repair-fail |
| sc-28 | `current` | fail→repair-fail, fail→repair-fail | fail→repair-fail, fail→repair-fail | fail→repair-fail, fail→repair-fail |
| sc-29 | `current` | fail→repair-pass, fail→repair-pass | fail→repair-pass, fail→repair-pass | pass, pass |
| sc-30 | `current` | fail→repair-fail, fail→repair-fail | fail→repair-pass, fail→repair-pass | fail→repair-pass, fail→repair-pass |
| sc-31 | `prior` | fail→repair-pass, fail→repair-pass | fail→repair-fail, fail→repair-fail | pass, pass |
| sc-32 | `clarify` | pass, pass | pass, pass | pass, pass |
| sc-33 | `current` | fail→repair-pass, fail→repair-pass | fail→repair-pass, fail→repair-pass | fail→repair-pass, fail→repair-pass |
| sc-34 | `current` | fail→repair-fail, fail→repair-fail | fail→repair-pass, fail→repair-pass | fail→repair-pass, fail→repair-pass |
| sc-35 | `current` | fail→repair-pass, fail→repair-pass | fail→repair-fail, fail→repair-fail | fail→repair-fail, fail→repair-fail |
| sc-36 | `current` | fail→repair-pass, fail→repair-pass | fail→repair-pass, fail→repair-pass | fail→repair-pass, fail→repair-pass |
| sc-37 | `prior` | fail→repair-pass, fail→repair-pass | pass, pass | pass, pass |
| sc-38 | `prior` | fail→repair-pass, fail→repair-pass | pass, pass | pass, pass |
| sc-39 | `abstain` | pass, pass | pass, pass | pass, pass |
| sc-40 | `current` | fail→repair-pass, fail→repair-pass | fail→repair-pass, fail→repair-pass | pass, pass |
| sc-41 | `clarify` | pass, pass | pass, pass | pass, pass |
| sc-42 | `abstain` | pass, pass | pass, pass | pass, pass |
| sc-43 | `current` | pass, pass | pass, pass | fail→repair-pass, fail→repair-pass |
| sc-44 | `current` | fail→repair-pass, fail→repair-pass | fail→repair-pass, fail→repair-pass | fail→repair-pass, fail→repair-pass |
| sc-45 | `current` | fail→repair-pass, fail→repair-pass | fail→repair-fail, fail→repair-fail | fail→repair-pass, fail→repair-pass |
| sc-46 | `prior` | fail→repair-pass, fail→repair-pass | pass, pass | pass, pass |
| sc-47 | `prior` | fail→repair-pass, fail→repair-pass | pass, pass | pass, pass |
| sc-48 | `prior` | pass, pass | pass, pass | pass, pass |
| sc-49 | `prior` | fail→repair-pass, fail→repair-pass | fail→repair-pass, fail→repair-pass | pass, pass |
| sc-50 | `current` | fail→repair-fail, fail→repair-fail | fail→repair-fail, fail→repair-fail | pass, pass |

## Reproducibility manifest

```json
{
  "benchmark_version": "v1",
  "scenarios_sha256": "f7d2f97501f77b82b342156c6e6ee0b2330d73a1fe0850dd9b7848d86cf413d9",
  "expected_answers_sha256": "d08c03bd0b3a82cca98a7c9ba5cd4d03062bdb2de1ac4dee79c06e356fb93cc9",
  "interventions_sha256": "374ca5837b4ca75cfa2f6b2fd65769c23ccefcf04697b29af19e109a7f6bebe9",
  "judge_prompt_version": "v1.0.0",
  "candidate_model": "openrouter/google/gemini-2.5-flash-lite",
  "judge_model": "openrouter/openai/gpt-4o-mini",
  "judge_family": "openai",
  "trials": 2,
  "temperature": 0.0,
  "ranking_condition": "baseline",
  "timestamp_utc": "2026-04-25T23:56:59+00:00",
  "runner_git_commit": "3427bab8200194ff486a5b030eac7bc2fa5850c0",
  "random_seed": null,
  "schema_revision": 2,
  "camera_injection": false,
  "judge_prompt_sha256": "16bd055abe42bd3218da043be3f87d213f58b50ab53e8ec0d7c1df4b121eff6c",
  "judge_family_resolution": "explicit",
  "manifest_warnings": []
}
```
