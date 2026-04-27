# Wearable Assistant Context Benchmark: Findings

**Benchmark:** context-tracking benchmark for multimodal wearable assistants

## Benchmark summary

- **Benchmark**: context-tracking benchmark for multimodal wearable assistants
- **Default comparison condition**: `baseline`
- **Primary score** (balanced Turn 2 accuracy): **100.0%**
- **How to read this run**: compare candidate models on the `baseline` score below; treat the other conditions as diagnostic sensitivity checks.
- **Per-class accuracy under `baseline`**:
    - `current`: 100.0%
    - `prior`: 100.0%

Condition sensitivity (balanced Turn 2 accuracy):

| Condition | Balanced Turn 2 accuracy |
| --- | --- |
| baseline (default) | 100.0% |
| condition_a | 95.8% |
| condition_b | 100.0% |

## Per-class pass rate by condition

| Class | baseline | condition_a | condition_b |
| --- | --- | --- | --- |
| `current` | 100.0% (66/66) | 100.0% (66/66) | 100.0% (66/66) |
| `prior` | 100.0% (24/24) | 91.7% (22/24) | 100.0% (24/24) |
| `clarify` (auxiliary) | 100.0% (6/6) | 66.7% (4/6) | 100.0% (6/6) |
| `abstain` (auxiliary) | 100.0% (4/4) | 100.0% (4/4) | 100.0% (4/4) |

## Simulated repair rate by condition

| Condition | Repair rate (repaired / failures) |
| --- | --- |
| baseline | no Turn 2 failures |
| condition_a | 0.0% (0 / 4) |
| condition_b | no Turn 2 failures |

## Code-judge disagreement by scenario

- sc-01: 0 trial(s) with code/judge disagreement
- sc-02: 0 trial(s) with code/judge disagreement
- sc-03: 0 trial(s) with code/judge disagreement
- sc-04: 0 trial(s) with code/judge disagreement
- sc-05: 0 trial(s) with code/judge disagreement
- sc-06: 0 trial(s) with code/judge disagreement
- sc-07: 0 trial(s) with code/judge disagreement
- sc-08: 0 trial(s) with code/judge disagreement
- sc-09: 0 trial(s) with code/judge disagreement
- sc-10: 0 trial(s) with code/judge disagreement
- sc-11: 0 trial(s) with code/judge disagreement
- sc-12: 0 trial(s) with code/judge disagreement
- sc-13: 0 trial(s) with code/judge disagreement
- sc-14: 0 trial(s) with code/judge disagreement
- sc-15: 0 trial(s) with code/judge disagreement
- sc-16: 0 trial(s) with code/judge disagreement
- sc-17: 0 trial(s) with code/judge disagreement
- sc-18: 0 trial(s) with code/judge disagreement
- sc-19: 2 trial(s) with code/judge disagreement
- sc-20: 0 trial(s) with code/judge disagreement
- sc-21: 0 trial(s) with code/judge disagreement
- sc-22: 0 trial(s) with code/judge disagreement
- sc-23: 0 trial(s) with code/judge disagreement
- sc-24: 0 trial(s) with code/judge disagreement
- sc-25: 0 trial(s) with code/judge disagreement
- sc-26: 0 trial(s) with code/judge disagreement
- sc-27: 0 trial(s) with code/judge disagreement
- sc-28: 0 trial(s) with code/judge disagreement
- sc-29: 0 trial(s) with code/judge disagreement
- sc-30: 0 trial(s) with code/judge disagreement
- sc-31: 0 trial(s) with code/judge disagreement
- sc-32: 4 trial(s) with code/judge disagreement
- sc-33: 0 trial(s) with code/judge disagreement
- sc-34: 0 trial(s) with code/judge disagreement
- sc-35: 0 trial(s) with code/judge disagreement
- sc-36: 0 trial(s) with code/judge disagreement
- sc-37: 0 trial(s) with code/judge disagreement
- sc-38: 2 trial(s) with code/judge disagreement
- sc-39: 0 trial(s) with code/judge disagreement
- sc-40: 0 trial(s) with code/judge disagreement
- sc-41: 6 trial(s) with code/judge disagreement
- sc-42: 2 trial(s) with code/judge disagreement
- sc-43: 0 trial(s) with code/judge disagreement
- sc-44: 0 trial(s) with code/judge disagreement
- sc-45: 0 trial(s) with code/judge disagreement
- sc-46: 2 trial(s) with code/judge disagreement
- sc-47: 0 trial(s) with code/judge disagreement
- sc-48: 0 trial(s) with code/judge disagreement
- sc-49: 0 trial(s) with code/judge disagreement
- sc-50: 0 trial(s) with code/judge disagreement

## Scenario-by-condition matrix

| Scenario | Target context | baseline | condition_a | condition_b |
| --- | --- | --- | --- | --- |
| sc-01 | `current` | pass, pass | pass, pass | pass, pass |
| sc-02 | `current` | pass, pass | pass, pass | pass, pass |
| sc-03 | `current` | pass, pass | pass, pass | pass, pass |
| sc-04 | `prior` | pass, pass | pass, pass | pass, pass |
| sc-05 | `current` | pass, pass | pass, pass | pass, pass |
| sc-06 | `current` | pass, pass | pass, pass | pass, pass |
| sc-07 | `current` | pass, pass | pass, pass | pass, pass |
| sc-08 | `current` | pass, pass | pass, pass | pass, pass |
| sc-09 | `clarify` | pass, pass | pass, pass | pass, pass |
| sc-10 | `current` | pass, pass | pass, pass | pass, pass |
| sc-11 | `current` | pass, pass | pass, pass | pass, pass |
| sc-12 | `prior` | pass, pass | pass, pass | pass, pass |
| sc-13 | `current` | pass, pass | pass, pass | pass, pass |
| sc-14 | `current` | pass, pass | pass, pass | pass, pass |
| sc-15 | `current` | pass, pass | pass, pass | pass, pass |
| sc-16 | `prior` | pass, pass | pass, pass | pass, pass |
| sc-17 | `current` | pass, pass | pass, pass | pass, pass |
| sc-18 | `current` | pass, pass | pass, pass | pass, pass |
| sc-19 | `prior` | pass, pass | pass, pass | pass, pass |
| sc-20 | `current` | pass, pass | pass, pass | pass, pass |
| sc-21 | `current` | pass, pass | pass, pass | pass, pass |
| sc-22 | `current` | pass, pass | pass, pass | pass, pass |
| sc-23 | `current` | pass, pass | pass, pass | pass, pass |
| sc-24 | `prior` | pass, pass | pass, pass | pass, pass |
| sc-25 | `current` | pass, pass | pass, pass | pass, pass |
| sc-26 | `current` | pass, pass | pass, pass | pass, pass |
| sc-27 | `current` | pass, pass | pass, pass | pass, pass |
| sc-28 | `current` | pass, pass | pass, pass | pass, pass |
| sc-29 | `current` | pass, pass | pass, pass | pass, pass |
| sc-30 | `current` | pass, pass | pass, pass | pass, pass |
| sc-31 | `prior` | pass, pass | pass, pass | pass, pass |
| sc-32 | `clarify` | pass, pass | fail→repair-fail, fail→repair-fail | pass, pass |
| sc-33 | `current` | pass, pass | pass, pass | pass, pass |
| sc-34 | `current` | pass, pass | pass, pass | pass, pass |
| sc-35 | `current` | pass, pass | pass, pass | pass, pass |
| sc-36 | `current` | pass, pass | pass, pass | pass, pass |
| sc-37 | `prior` | pass, pass | pass, pass | pass, pass |
| sc-38 | `prior` | pass, pass | fail→repair-fail, fail→repair-fail | pass, pass |
| sc-39 | `abstain` | pass, pass | pass, pass | pass, pass |
| sc-40 | `current` | pass, pass | pass, pass | pass, pass |
| sc-41 | `clarify` | pass, pass | pass, pass | pass, pass |
| sc-42 | `abstain` | pass, pass | pass, pass | pass, pass |
| sc-43 | `current` | pass, pass | pass, pass | pass, pass |
| sc-44 | `current` | pass, pass | pass, pass | pass, pass |
| sc-45 | `current` | pass, pass | pass, pass | pass, pass |
| sc-46 | `prior` | pass, pass | pass, pass | pass, pass |
| sc-47 | `prior` | pass, pass | pass, pass | pass, pass |
| sc-48 | `prior` | pass, pass | pass, pass | pass, pass |
| sc-49 | `prior` | pass, pass | pass, pass | pass, pass |
| sc-50 | `current` | pass, pass | pass, pass | pass, pass |

## Reproducibility manifest

```json
{
  "benchmark_version": "v1",
  "scenarios_sha256": "f7d2f97501f77b82b342156c6e6ee0b2330d73a1fe0850dd9b7848d86cf413d9",
  "expected_answers_sha256": "d08c03bd0b3a82cca98a7c9ba5cd4d03062bdb2de1ac4dee79c06e356fb93cc9",
  "interventions_sha256": "374ca5837b4ca75cfa2f6b2fd65769c23ccefcf04697b29af19e109a7f6bebe9",
  "judge_prompt_version": "v1.0.0",
  "candidate_model": "openrouter/openai/gpt-4o-mini",
  "judge_model": "openrouter/google/gemini-2.5-flash-lite",
  "judge_family": "gemini",
  "trials": 2,
  "temperature": 0.0,
  "ranking_condition": "baseline",
  "timestamp_utc": "2026-04-25T23:38:45+00:00",
  "runner_git_commit": "3427bab8200194ff486a5b030eac7bc2fa5850c0",
  "random_seed": null,
  "schema_revision": 2,
  "camera_injection": true,
  "judge_prompt_sha256": "16bd055abe42bd3218da043be3f87d213f58b50ab53e8ec0d7c1df4b121eff6c",
  "judge_family_resolution": "explicit",
  "manifest_warnings": []
}
```
