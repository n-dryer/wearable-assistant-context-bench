# Wearable Assistant Context Benchmark: Findings

**Benchmark:** canonical v1 benchmark for cross-turn reference resolution under context change

> **Note on provenance.** This sample run was captured against the
> pre-consolidation 121-scenario candidate bank. On 2026-04-22 that bank
> was consolidated into the frozen 101-scenario v1 by applying the
> scenario audit in `docs/audits/`. These numbers therefore predate the
> current `benchmark/v1/scenarios.json`; they are indicative and kept
> for shape, not as an authoritative baseline. A fresh baseline will
> accompany the next tagged release.

## Benchmark summary

- **Benchmark**: canonical v1 benchmark for cross-turn reference resolution under context change
- **Default comparison condition**: `baseline`
- **Primary score** (balanced Turn 2 accuracy): **80.3%**
- **How to read this run**: compare candidate models on the `baseline` score below; treat the other conditions as diagnostic sensitivity checks.
- **Per-class accuracy under `baseline`**:
    - `current`: 68.6%
    - `prior`: 91.9%

Condition sensitivity (balanced Turn 2 accuracy):

| Condition | Balanced Turn 2 accuracy |
| --- | --- |
| baseline (default) | 80.3% |

## Per-class pass rate by condition

| Class | baseline |
| --- | --- |
| `current` | 68.6% (35/51) |
| `prior` | 91.9% (34/37) |
| `clarify` (auxiliary) | 89.5% (17/19) |
| `abstain` (auxiliary) | 100.0% (14/14) |

## Simulated repair rate by condition

| Condition | Repair rate (repaired / failures) |
| --- | --- |
| baseline | 71.4% (15 / 21) |

## Code-judge disagreement by scenario

- sc-01: 1 trial(s) with code/judge disagreement
- sc-02: 0 trial(s) with code/judge disagreement
- sc-03: 0 trial(s) with code/judge disagreement
- sc-04: 1 trial(s) with code/judge disagreement
- sc-05: 0 trial(s) with code/judge disagreement
- sc-06: 0 trial(s) with code/judge disagreement
- sc-07: 1 trial(s) with code/judge disagreement
- sc-08: 0 trial(s) with code/judge disagreement
- sc-09: 0 trial(s) with code/judge disagreement
- sc-10: 1 trial(s) with code/judge disagreement
- sc-100: 0 trial(s) with code/judge disagreement
- sc-101: 0 trial(s) with code/judge disagreement
- sc-102: 0 trial(s) with code/judge disagreement
- sc-103: 0 trial(s) with code/judge disagreement
- sc-104: 0 trial(s) with code/judge disagreement
- sc-105: 0 trial(s) with code/judge disagreement
- sc-106: 0 trial(s) with code/judge disagreement
- sc-107: 1 trial(s) with code/judge disagreement
- sc-108: 0 trial(s) with code/judge disagreement
- sc-109: 1 trial(s) with code/judge disagreement
- sc-11: 0 trial(s) with code/judge disagreement
- sc-110: 0 trial(s) with code/judge disagreement
- sc-111: 1 trial(s) with code/judge disagreement
- sc-112: 0 trial(s) with code/judge disagreement
- sc-113: 0 trial(s) with code/judge disagreement
- sc-114: 1 trial(s) with code/judge disagreement
- sc-115: 1 trial(s) with code/judge disagreement
- sc-116: 0 trial(s) with code/judge disagreement
- sc-117: 0 trial(s) with code/judge disagreement
- sc-118: 0 trial(s) with code/judge disagreement
- sc-119: 0 trial(s) with code/judge disagreement
- sc-12: 1 trial(s) with code/judge disagreement
- sc-120: 0 trial(s) with code/judge disagreement
- sc-121: 0 trial(s) with code/judge disagreement
- sc-13: 1 trial(s) with code/judge disagreement
- sc-14: 1 trial(s) with code/judge disagreement
- sc-15: 0 trial(s) with code/judge disagreement
- sc-16: 1 trial(s) with code/judge disagreement
- sc-17: 1 trial(s) with code/judge disagreement
- sc-18: 0 trial(s) with code/judge disagreement
- sc-19: 0 trial(s) with code/judge disagreement
- sc-20: 1 trial(s) with code/judge disagreement
- sc-21: 0 trial(s) with code/judge disagreement
- sc-22: 1 trial(s) with code/judge disagreement
- sc-23: 1 trial(s) with code/judge disagreement
- sc-24: 0 trial(s) with code/judge disagreement
- sc-25: 0 trial(s) with code/judge disagreement
- sc-26: 0 trial(s) with code/judge disagreement
- sc-27: 1 trial(s) with code/judge disagreement
- sc-28: 1 trial(s) with code/judge disagreement
- sc-29: 0 trial(s) with code/judge disagreement
- sc-30: 0 trial(s) with code/judge disagreement
- sc-31: 0 trial(s) with code/judge disagreement
- sc-32: 0 trial(s) with code/judge disagreement
- sc-33: 1 trial(s) with code/judge disagreement
- sc-34: 1 trial(s) with code/judge disagreement
- sc-35: 0 trial(s) with code/judge disagreement
- sc-36: 1 trial(s) with code/judge disagreement
- sc-37: 1 trial(s) with code/judge disagreement
- sc-38: 0 trial(s) with code/judge disagreement
- sc-39: 0 trial(s) with code/judge disagreement
- sc-40: 0 trial(s) with code/judge disagreement
- sc-41: 0 trial(s) with code/judge disagreement
- sc-42: 1 trial(s) with code/judge disagreement
- sc-43: 0 trial(s) with code/judge disagreement
- sc-44: 1 trial(s) with code/judge disagreement
- sc-45: 1 trial(s) with code/judge disagreement
- sc-46: 1 trial(s) with code/judge disagreement
- sc-47: 1 trial(s) with code/judge disagreement
- sc-48: 0 trial(s) with code/judge disagreement
- sc-49: 0 trial(s) with code/judge disagreement
- sc-50: 0 trial(s) with code/judge disagreement
- sc-51: 0 trial(s) with code/judge disagreement
- sc-52: 1 trial(s) with code/judge disagreement
- sc-53: 1 trial(s) with code/judge disagreement
- sc-54: 1 trial(s) with code/judge disagreement
- sc-55: 0 trial(s) with code/judge disagreement
- sc-56: 1 trial(s) with code/judge disagreement
- sc-57: 0 trial(s) with code/judge disagreement
- sc-58: 0 trial(s) with code/judge disagreement
- sc-59: 0 trial(s) with code/judge disagreement
- sc-60: 0 trial(s) with code/judge disagreement
- sc-61: 0 trial(s) with code/judge disagreement
- sc-62: 0 trial(s) with code/judge disagreement
- sc-63: 1 trial(s) with code/judge disagreement
- sc-64: 0 trial(s) with code/judge disagreement
- sc-65: 1 trial(s) with code/judge disagreement
- sc-66: 0 trial(s) with code/judge disagreement
- sc-67: 0 trial(s) with code/judge disagreement
- sc-68: 0 trial(s) with code/judge disagreement
- sc-69: 0 trial(s) with code/judge disagreement
- sc-70: 0 trial(s) with code/judge disagreement
- sc-71: 1 trial(s) with code/judge disagreement
- sc-72: 0 trial(s) with code/judge disagreement
- sc-73: 0 trial(s) with code/judge disagreement
- sc-74: 0 trial(s) with code/judge disagreement
- sc-75: 0 trial(s) with code/judge disagreement
- sc-76: 0 trial(s) with code/judge disagreement
- sc-77: 0 trial(s) with code/judge disagreement
- sc-78: 0 trial(s) with code/judge disagreement
- sc-79: 0 trial(s) with code/judge disagreement
- sc-80: 0 trial(s) with code/judge disagreement
- sc-81: 0 trial(s) with code/judge disagreement
- sc-82: 1 trial(s) with code/judge disagreement
- sc-83: 0 trial(s) with code/judge disagreement
- sc-84: 0 trial(s) with code/judge disagreement
- sc-85: 0 trial(s) with code/judge disagreement
- sc-86: 0 trial(s) with code/judge disagreement
- sc-87: 0 trial(s) with code/judge disagreement
- sc-88: 1 trial(s) with code/judge disagreement
- sc-89: 0 trial(s) with code/judge disagreement
- sc-90: 0 trial(s) with code/judge disagreement
- sc-91: 1 trial(s) with code/judge disagreement
- sc-92: 0 trial(s) with code/judge disagreement
- sc-93: 0 trial(s) with code/judge disagreement
- sc-94: 1 trial(s) with code/judge disagreement
- sc-95: 0 trial(s) with code/judge disagreement
- sc-96: 1 trial(s) with code/judge disagreement
- sc-97: 0 trial(s) with code/judge disagreement
- sc-98: 0 trial(s) with code/judge disagreement
- sc-99: 0 trial(s) with code/judge disagreement

## Scenario-by-condition matrix

| Scenario | Target context | baseline |
| --- | --- | --- |
| sc-01 | `current` | pass |
| sc-02 | `current` | fail→repair-fail |
| sc-03 | `prior` | pass |
| sc-04 | `current` | fail→repair-fail |
| sc-05 | `current` | pass |
| sc-06 | `current` | fail→repair-pass |
| sc-07 | `current` | pass |
| sc-08 | `current` | fail→repair-fail |
| sc-09 | `prior` | fail→repair-pass |
| sc-10 | `current` | pass |
| sc-11 | `prior` | pass |
| sc-12 | `current` | fail→repair-fail |
| sc-13 | `current` | pass |
| sc-14 | `current` | fail→repair-pass |
| sc-15 | `current` | fail→repair-pass |
| sc-16 | `current` | fail→repair-fail |
| sc-17 | `current` | fail→repair-pass |
| sc-18 | `current` | pass |
| sc-19 | `current` | pass |
| sc-20 | `current` | pass |
| sc-21 | `current` | pass |
| sc-22 | `current` | fail→repair-pass |
| sc-23 | `current` | fail→repair-fail |
| sc-24 | `prior` | pass |
| sc-25 | `prior` | pass |
| sc-26 | `prior` | pass |
| sc-27 | `prior` | pass |
| sc-28 | `prior` | pass |
| sc-29 | `prior` | fail→repair-pass |
| sc-30 | `prior` | fail→repair-pass |
| sc-31 | `prior` | pass |
| sc-32 | `prior` | pass |
| sc-33 | `clarify` | pass |
| sc-34 | `clarify` | pass |
| sc-35 | `clarify` | pass |
| sc-36 | `clarify` | pass |
| sc-37 | `clarify` | pass |
| sc-38 | `abstain` | pass |
| sc-39 | `abstain` | pass |
| sc-40 | `abstain` | pass |
| sc-41 | `abstain` | pass |
| sc-42 | `current` | pass |
| sc-43 | `current` | pass |
| sc-44 | `current` | pass |
| sc-45 | `current` | pass |
| sc-46 | `current` | pass |
| sc-47 | `current` | pass |
| sc-48 | `current` | pass |
| sc-49 | `current` | pass |
| sc-50 | `current` | pass |
| sc-51 | `current` | pass |
| sc-52 | `current` | pass |
| sc-53 | `current` | fail→repair-pass |
| sc-54 | `current` | fail→repair-pass |
| sc-55 | `current` | fail→repair-pass |
| sc-56 | `current` | pass |
| sc-57 | `current` | pass |
| sc-58 | `prior` | pass |
| sc-59 | `prior` | pass |
| sc-60 | `prior` | pass |
| sc-61 | `prior` | pass |
| sc-62 | `prior` | pass |
| sc-63 | `prior` | pass |
| sc-64 | `prior` | pass |
| sc-65 | `prior` | pass |
| sc-66 | `prior` | pass |
| sc-67 | `prior` | pass |
| sc-68 | `prior` | pass |
| sc-69 | `prior` | pass |
| sc-70 | `clarify` | pass |
| sc-71 | `clarify` | pass |
| sc-72 | `clarify` | fail→repair-pass |
| sc-73 | `clarify` | fail→repair-pass |
| sc-74 | `clarify` | pass |
| sc-75 | `clarify` | pass |
| sc-76 | `clarify` | pass |
| sc-77 | `abstain` | pass |
| sc-78 | `abstain` | pass |
| sc-79 | `abstain` | pass |
| sc-80 | `abstain` | pass |
| sc-81 | `abstain` | pass |
| sc-82 | `current` | pass |
| sc-83 | `current` | pass |
| sc-84 | `current` | pass |
| sc-85 | `current` | pass |
| sc-86 | `current` | fail→repair-pass |
| sc-87 | `current` | pass |
| sc-88 | `current` | pass |
| sc-89 | `current` | pass |
| sc-90 | `current` | pass |
| sc-91 | `current` | pass |
| sc-92 | `current` | pass |
| sc-93 | `current` | pass |
| sc-94 | `current` | pass |
| sc-95 | `current` | pass |
| sc-96 | `current` | fail→repair-pass |
| sc-97 | `prior` | pass |
| sc-98 | `prior` | pass |
| sc-99 | `prior` | pass |
| sc-100 | `prior` | pass |
| sc-101 | `prior` | pass |
| sc-102 | `prior` | pass |
| sc-103 | `prior` | pass |
| sc-104 | `prior` | pass |
| sc-105 | `prior` | pass |
| sc-106 | `prior` | pass |
| sc-107 | `prior` | pass |
| sc-108 | `prior` | pass |
| sc-109 | `prior` | pass |
| sc-110 | `clarify` | pass |
| sc-111 | `clarify` | pass |
| sc-112 | `clarify` | pass |
| sc-113 | `clarify` | pass |
| sc-114 | `clarify` | pass |
| sc-115 | `clarify` | pass |
| sc-116 | `clarify` | pass |
| sc-117 | `abstain` | pass |
| sc-118 | `abstain` | pass |
| sc-119 | `abstain` | pass |
| sc-120 | `abstain` | pass |
| sc-121 | `abstain` | pass |

## Reproducibility manifest

```json
{
  "benchmark_version": "v1",
  "scenarios_sha256": "1ba3faf5e3b88f196408a3ee9a69b98b9c49e4a288d41cea5c5b697c6485f232",
  "expected_answers_sha256": "d97c8dc8b8e417697dd38ee3d22ad5030d56079532e7654327bf87f41a903542",
  "interventions_sha256": "374ca5837b4ca75cfa2f6b2fd65769c23ccefcf04697b29af19e109a7f6bebe9",
  "judge_prompt_version": "v1.0.0",
  "candidate_model": "openrouter/anthropic/claude-3.5-haiku",
  "judge_model": "openrouter/openai/gpt-4.1-mini",
  "judge_family": "openai",
  "trials": 1,
  "temperature": 0.0,
  "ranking_condition": "baseline",
  "timestamp_utc": "2026-04-22T20:36:12+00:00",
  "runner_git_commit": "fd09a51216a0fe9f5516bb34b7ad8f76d5019f55",
  "random_seed": null,
  "judge_prompt_sha256": "16bd055abe42bd3218da043be3f87d213f58b50ab53e8ec0d7c1df4b121eff6c",
  "judge_family_resolution": "explicit",
  "conditions_run": [
    "baseline"
  ],
  "run_scope": "baseline-only sample run over canonical v1",
  "scenario_count": 121,
  "manifest_warnings": []
}
```
