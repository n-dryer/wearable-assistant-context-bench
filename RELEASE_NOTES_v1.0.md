# Release Notes: Wearable Assistant Context Benchmark v1.0.0

**Tag:** `v1.0.0`
**Branch:** `v1-portfolio-release` merged into `main`
**Date:** 2026-04-24

---

## What this benchmark does

Tests whether a wearable assistant answers about the right thing after
the user's context changes between turns. The user may move to a new
location, pick up a different object, switch screens, or ask about
something from an earlier moment. The assistant must resolve the
ambiguous reference correctly without the user having to restate it.

Built from real user feedback and product testing to support a
practical model-selection decision.

---

## What shipped

**Scenario bank.** 101 frozen scenarios in `benchmark/v1/scenarios.json`.

| Category | Count | Description |
|---|---|---|
| `current` | 50 | Answer refers to what the user is doing now |
| `prior` | 24 | Answer refers to an earlier context |
| `clarify` | 15 | Question is ambiguous; clarification needed |
| `abstain` | 12 | Needed info is absent; model should decline |

**Answer keys.** `benchmark/v1/expected_answers.json`, one entry per
scenario. Substring-style lists for each of the four label types.

**Prompt conditions.** `benchmark/v1/interventions.json`, three frozen
variants: `baseline` (default ranking condition), `condition_a`
(policy-selection instruction), `condition_b` (pre-answer scaffold).

**Runner.** `benchmark/v1/run.py`. Supports Claude, Gemini, and
OpenAI-family models. LiteLLM adapter for provider-qualified IDs.
Emits `transcripts.jsonl`, `findings.md`, and a reproducibility
manifest.

**Scoring.** Deterministic substring containment. Main score is the
macro average of per-category accuracy across all four categories. See
`docs/benchmark_spec.md` for the full contract.

**Schema.** `docs/schema.md` documents every field.

**Dataset card.** `benchmark/v1/dataset_card.md` with Hugging Face
YAML frontmatter.

**Leakage audit.** `scripts/scan_leakage.py` (reusable regression
guard). 51 of 101 scenarios had answer tokens word-boundary-matched in
`turn_2_user`; all 51 were rewritten to use deictics. Scan now returns
zero flags.

---

## Known limits

**Substring scoring.** A correct response that paraphrases an answer
key without hitting a listed token will score incorrect. This is
acknowledged. LLM-as-judge scoring is planned for v1.1.

**Prior scenario reach-back.** 23 of 24 prior scenarios can be solved
by substring-matching `turn_1_user` text. The prior category tests
recall of explicit strings rather than genuine reach-back reasoning.
Scenario IDs: sc-03, sc-09, sc-25, sc-26, sc-27, sc-30, sc-32, sc-59,
sc-60, sc-63, sc-64, sc-66, sc-67, sc-69, sc-99, sc-100, sc-101,
sc-102, sc-104, sc-106, sc-107, sc-108, sc-109. Stronger prior
scenarios are planned for v1.1.

**Transcript proxies.** Spoken user queries are represented as text
transcripts. Raw audio grounding, speaker attribution, and ambient
audio cues are not tested in v1.

**Baseline run.** The pre-release baseline in `benchmark/v1/runs/v1-baseline/`
pre-dates the leakage fixes and covers the pre-consolidation scenario
bank. A fresh baseline against the final 101 scenarios is required
before comparing new candidate runs to it.

---

## What did not ship

- LLM-as-judge scoring (Task 9, deferred to v1.1)
- Human judge pilot
- Human speech-only spot check
- Audio grounding scenarios

These are documented as planned work on the `v1.1-extension` branch.

---

## Links

- Benchmark spec and scoring rules: `docs/benchmark_spec.md`
- Schema reference: `docs/schema.md`
- Dataset card: `benchmark/v1/dataset_card.md`
- Changelog: `CHANGELOG.md`
- Citation: `CITATION.cff`
- License: `LICENSE`
