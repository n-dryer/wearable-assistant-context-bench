# Wearable Assistant Context Benchmark: Findings

**Benchmark:** context-tracking benchmark for multimodal AI assistants used actively for advice or coaching (wearable or handheld)

## Benchmark summary

- **Benchmark**: context-tracking benchmark for multimodal AI assistants used actively for advice or coaching (wearable or handheld)
- **Default comparison condition**: `baseline`
- **Primary score** (balanced Turn 2 accuracy): **67.3% (95% CI 55.5%–79.1%)**
- **How to read this run**: compare candidate models on the `baseline` score below; treat the other conditions as diagnostic sensitivity checks. CIs are 95% Wilson per class and 95% normal-approximation on the balanced mean.
- **Per-class accuracy under `baseline`**:
    - `current`: 84.6% (95% CI 73.9%–91.4%)
    - `prior`: 50.0% (95% CI 29.9%–70.1%)

Condition sensitivity (balanced Turn 2 accuracy):

| Condition | Balanced Turn 2 accuracy (95% CI) |
| --- | --- |
| baseline (default) | 67.3% (95% CI 55.5%–79.1%) |
| condition_a | 47.1% (95% CI 36.1%–58.1%) |
| condition_b | 72.1% (95% CI 61.1%–83.1%) |

## Per-class pass rate by condition

| Class | baseline | condition_a | condition_b |
| --- | --- | --- | --- |
| `current` | 84.6% [95% CI 73.9–91.4] (55/65) | 69.2% [95% CI 57.2–79.1] (45/65) | 69.2% [95% CI 57.2–79.1] (45/65) |
| `prior` | 50.0% [95% CI 29.9–70.1] (10/20) | 25.0% [95% CI 11.2–46.9] (5/20) | 75.0% [95% CI 53.1–88.8] (15/20) |
| `clarify` (auxiliary) | 100.0% [95% CI 72.2–100.0] (10/10) | 0.0% [95% CI 0.0–27.8] (0/10) | 0.0% [95% CI 0.0–27.8] (0/10) |
| `abstain` (auxiliary) | 0.0% [95% CI 0.0–43.4] (0/5) | 100.0% [95% CI 56.6–100.0] (5/5) | 0.0% [95% CI 0.0–43.4] (0/5) |

## Simulated repair rate by condition

| Condition | Repair rate (95% CI) |
| --- | --- |
| baseline | 20.0% [95% CI 8.9–39.1] (5 / 25) |
| condition_a | 33.3% [95% CI 21.4–47.9] (15 / 45) |
| condition_b | 25.0% [95% CI 14.2–40.2] (10 / 40) |

## Code-judge disagreement by scenario

- adv-01: 0 trial(s) with code/judge disagreement
- adv-02: 0 trial(s) with code/judge disagreement
- adv-03: 0 trial(s) with code/judge disagreement
- adv-04: 0 trial(s) with code/judge disagreement
- adv-05: 5 trial(s) with code/judge disagreement
- adv-06: 0 trial(s) with code/judge disagreement
- adv-07: 5 trial(s) with code/judge disagreement
- adv-08: 0 trial(s) with code/judge disagreement
- adv-09: 0 trial(s) with code/judge disagreement
- adv-10: 0 trial(s) with code/judge disagreement
- adv-11: 5 trial(s) with code/judge disagreement
- adv-12: 0 trial(s) with code/judge disagreement
- adv-13: 0 trial(s) with code/judge disagreement
- adv-14: 0 trial(s) with code/judge disagreement
- adv-15: 0 trial(s) with code/judge disagreement
- adv-16: 0 trial(s) with code/judge disagreement
- adv-17: 5 trial(s) with code/judge disagreement
- adv-18: 0 trial(s) with code/judge disagreement
- adv-19: 0 trial(s) with code/judge disagreement
- adv-20: 0 trial(s) with code/judge disagreement

## Inter-judge agreement (cross-LLM)

- **Trials with both judge labels**: 300
- **Observed agreement**: 63.3%
- **Cohen's kappa**: 0.443

Per-scenario disagreement counts (where the two judges differ):

- adv-02: 5 trial(s) where primary and ranking judges disagreed
- adv-04: 5 trial(s) where primary and ranking judges disagreed
- adv-06: 5 trial(s) where primary and ranking judges disagreed
- adv-08: 10 trial(s) where primary and ranking judges disagreed
- adv-09: 15 trial(s) where primary and ranking judges disagreed
- adv-10: 10 trial(s) where primary and ranking judges disagreed
- adv-11: 5 trial(s) where primary and ranking judges disagreed
- adv-12: 10 trial(s) where primary and ranking judges disagreed
- adv-14: 10 trial(s) where primary and ranking judges disagreed
- adv-17: 5 trial(s) where primary and ranking judges disagreed
- adv-18: 10 trial(s) where primary and ranking judges disagreed
- adv-19: 10 trial(s) where primary and ranking judges disagreed
- adv-20: 10 trial(s) where primary and ranking judges disagreed

## Scenario-by-condition matrix

| Scenario | Target context | baseline | condition_a | condition_b |
| --- | --- | --- | --- | --- |
| adv-01 | `current` | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass |
| adv-02 | `current` | pass, pass, pass, pass, pass | fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail | pass, pass, pass, pass, pass |
| adv-03 | `current` | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass |
| adv-04 | `current` | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass |
| adv-05 | `current` | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass | fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail |
| adv-06 | `current` | fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass |
| adv-07 | `current` | pass, pass, pass, pass, pass | fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail | fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail |
| adv-08 | `current` | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass | fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail |
| adv-09 | `current` | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass |
| adv-10 | `current` | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass |
| adv-11 | `current` | pass, pass, pass, pass, pass | fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail | fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass |
| adv-12 | `current` | fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail | fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail | pass, pass, pass, pass, pass |
| adv-13 | `current` | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass |
| adv-14 | `prior` | fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail | fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail | pass, pass, pass, pass, pass |
| adv-15 | `prior` | fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail | fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass | pass, pass, pass, pass, pass |
| adv-16 | `prior` | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass | pass, pass, pass, pass, pass |
| adv-17 | `prior` | pass, pass, pass, pass, pass | fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass | fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass |
| adv-18 | `clarify` | pass, pass, pass, pass, pass | fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass, fail→repair-pass | fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail |
| adv-19 | `clarify` | pass, pass, pass, pass, pass | fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail | fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail |
| adv-20 | `abstain` | fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail | pass, pass, pass, pass, pass | fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail, fail→repair-fail |

## Reproducibility manifest

```json
{
  "benchmark_version": "v1",
  "scenarios_sha256": "45f486adb801879ac7a24194c78f333abb3f6a8dc2dc656e8db39c5836254238",
  "expected_answers_sha256": "866944fdfe0326c827941fd292206c35ebce0218ea5daa969c0a0b0973ca4b3e",
  "interventions_sha256": "374ca5837b4ca75cfa2f6b2fd65769c23ccefcf04697b29af19e109a7f6bebe9",
  "judge_prompt_version": "v1.1.0",
  "candidate_model": "openrouter/google/gemini-2.5-flash-lite",
  "judge_model": "openrouter/openai/gpt-4o-mini",
  "judge_family": "openai",
  "trials": 5,
  "temperature": 0.0,
  "ranking_condition": "baseline",
  "timestamp_utc": "2026-04-26T21:17:10+00:00",
  "runner_git_commit": "acb456415ed5c1d7fe799552a933169c187e5b68",
  "random_seed": null,
  "schema_revision": 3,
  "pack": "adversarial",
  "camera_injection": true,
  "judge_prompt_sha256": "16bd055abe42bd3218da043be3f87d213f58b50ab53e8ec0d7c1df4b121eff6c",
  "judge_family_resolution": "explicit",
  "ranking_judge_model": "openrouter/anthropic/claude-haiku-4.5",
  "ranking_judge_family": "claude",
  "manifest_warnings": []
}
```
