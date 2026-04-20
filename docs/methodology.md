# Methodology

## Scope

This document describes the **v1 runnable slice** of the benchmark,
implemented in `core/` and `experiments/exp_001/`. The benchmark
definition (including the without-prior-Q variant, governance, and
primary score) lives in [docs/concept_v0_2.md](concept_v0_2.md). The
current runnable slice covers only the **with-prior-Q** variant.

The scored task is **prior-versus-current visual-context selection**:
does the model anchor its Turn 2 answer to the prior frame or the
current frame? Object recognition is assumed and out of scope.

## v1 is a text-proxy slice

v1 scenarios are text conversations. The `Scenario` dataclass exposes
optional `turn_1_image` and `turn_2_image` fields so future image
inputs can be plumbed into the message payload, but no scenario uses
them in v1. Treat v1 results as a text-proxy for a camera-grounded
task; image-enabled variants are deferred.

## Scenario shape

Each scenario is a two-turn conversation, optionally extended for
simulated repair.

- **Turn 1** establishes a visual-context reference state (prior
  frame) and an anchored question.
- **Turn 2** shifts visual context (current frame) and asks an
  ambiguously-referenced follow-up. Only Turn 2 is scored.
- **Turn 3** fires on Turn 2 failure. It is a templated "I mean,
  [explicit anchor]" prompt used for the simulated repair rate.

## Intervention conditions

`exp_001` runs three prompt conditions:

- **Baseline**: minimal system prompt. Default ranking condition.
- **Condition A**: direct instruction to answer from the correct
  visual context based on the most relevant state (not hard-coded
  to the most recent state).
- **Condition B**: pre-answer scaffold that requires a short
  summary identifying the relevant visual context before the
  answer.

See [docs/interventions.md](interventions.md) for framing and
`.agent-prompts/INTERVENTIONS.md` for the source-of-truth prompt
wording.

## Judge

The judge reads the Turn 2 response, the scenario description, both
answer lists (current / prior), and the clarify/abstain indicators,
and labels the response with one of four policy tags.

Judge family defaults to `auto`: the runner infers the candidate
family from `--model` and assigns the judge to a different family to
reduce same-family bias. If the candidate family cannot be inferred,
the runner errors out and requires explicit `--judge-family`. A
same-family Claude-judge comparison stays available via
`--judge-family claude`.

## Scoring

Scoring is hybrid.

The code-based scorer (`core/scoring.py`) reports:

- `has_current`: response fuzzy-matches any current answer.
- `has_prior`: response fuzzy-matches any prior answer after the
  contrastive-pattern suppressor runs.
- `has_prior_raw`: pre-suppression match value.
- `has_clarify`: substring match against clarify indicators.
- `has_abstain`: substring match against abstain indicators.
- `is_refusal`: response reads as a refusal or uncertainty hedge.
- `response_length_tokens_est`: rough length estimate.

The code scorer also exposes deprecated `has_stale` / `has_stale_raw`
aliases of `has_prior` / `has_prior_raw` for backward-compatible
callers.

The judge verdict is the primary signal. The code signals are an
audit cross-check; disagreements are surfaced in the report, not
auto-resolved.

## Benchmark evaluation protocol

1. Candidate models are run on the **same frozen v1 set**.
2. `baseline` is the default ranking condition.
3. The primary score is **balanced Turn 2 accuracy** under the
   ranking condition, aggregated as defined in
   [docs/concept_v0_2.md](concept_v0_2.md).
4. `clarify` and `abstain` tags count as wrong for the primary
   score; they are rendered as diagnostic rows in the report.
5. Condition sensitivity (baseline vs. condition_a vs. condition_b)
   is reported secondarily.
6. Every report emits a **reproducibility manifest** with scenario,
   intervention, and judge-prompt SHAs, candidate and judge model
   strings, trials, temperature, and the resolved ranking
   condition.

### Known scorer limitation

The code scorer is substring-driven and can false-fail contrastive
responses that mention both the old and new state. The contrastive-
pattern suppressor in [core/scoring.py](../core/scoring.py) handles
common cases. Residual false failures should be read against the
judge verdict.

## CLI invocation

```bash
python experiments/exp_001/run.py \
    --model <candidate_model_id> \
    --judge-model <judge_model_id>
```

Flags:

- `--model` — candidate model string under test.
- `--judge-model` — judge model string.
- `--judge-family` — `auto` | `claude` | `openai`. Default `auto`.
- `--trials` — trials per `(scenario, condition)` cell.
- `--output-dir` — path for transcripts **and** the generated
  findings file for this run.

All flags are optional; missing flags fall back to configured
defaults.

## Trial design

- trials per `(scenario, condition)` cell: 2 by default
- temperature: `0.0`
- two trials are a stability check, not a statistical-power claim

## Interpretation

`exp_001` is the **v1 runnable slice** of the benchmark. It can
differentiate candidate models on the v1 scenario set and under the
ranking condition. Without-prior-Q coverage, larger trial counts,
image-input variants, and judge-calibration against human raters
are tracked in [docs/deferred_roadmap.md](deferred_roadmap.md).
