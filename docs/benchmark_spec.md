# Benchmark Spec: Wearable Assistant Context Benchmark

**Subtitle:** A benchmark for implicit context tracking in wearable
multimodal assistants.

This document defines v1 of the benchmark. In the spec, the v1 task is
called **reference-state selection under implicit context shift**. It
checks whether the answer follows the **prior** context or the
**current** context in Turn 2.

## What the benchmark measures

This benchmark measures how a wearable multimodal assistant handles
ambiguous user references when the user's context changes between
turns, such as where they are, what they are holding, or what is
around them. It focuses on a recurring interaction problem: the
assistant sometimes makes the wrong inference about what the user is
referring to and answers from the wrong context.

In v1, the benchmark asks a specific question: after the user's context
changes between turns, does the assistant answer from the:

- **prior context**: the object, place, or surrounding context from the
  earlier moment
- **current context**: the object, place, or surrounding context from the
  current moment

Although the benchmark was developed around a wearable multimodal
assistant, it can also apply to other multimodal assistant devices. The
device may be worn or simply on or near the user, but it must support
live multimodal input, such as audio and video, and respond through
audio and/or text. It also must be positioned to capture the context
relevant to the user's activity or question.

Object recognition is assumed and out of scope.

Concrete example:

- Turn 1: the user asks about a screwdriver in hand
- Turn 2: the user has switched to a hammer and asks, "am I holding this correctly?"
- The scored question is whether the answer follows the prior context or the
  current one

## Where the scenarios came from

This benchmark was built to support model-selection decisions for a wearable
multimodal assistant.

The scenarios come from a mix of pilot user feedback on a wearable
multimodal assistant at a stealth AI startup, direct hands-on testing of real
multimodal assistants and wearables, generalized cases based on repeated
patterns, and a smaller number of conceptual cases added to cover important
situations cleanly.

This pattern comes up often in real use, can be scored clearly, and keeps
the benchmark focused on context judgment rather than object recognition,
which is assumed and out of scope.

## What v1 includes

The current v1 set contains:

- **11 frozen scenarios**
- **3 prompt conditions**: `baseline`, `condition_a`, `condition_b`
- **2 trials per (scenario, condition) cell** by default
- **Turn 2 scoring only**
- **Turn 3 repair** as a secondary check

Every scenario is a two-turn setup:

- Turn 1 establishes a referent
- Turn 2 shifts context and asks an ambiguous follow-up
- The model must decide whether the answer belongs to the prior or current
  context

The benchmark is intentionally narrow. It measures one product-relevant
interaction problem and should not be read as a full measure of assistant
quality.

## Runtime inputs

The active runtime inputs are:

- [`benchmark/v1/scenarios.json`](../benchmark/v1/scenarios.json)
- [`benchmark/v1/expected_answers.json`](../benchmark/v1/expected_answers.json)
- [`benchmark/v1/interventions.json`](../benchmark/v1/interventions.json)

These JSON files are the source files used to run v1.

## Scenario schema

Each entry in `scenarios.json` is an object with the following fields.

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `scenario_id` | string | yes | unique identifier, e.g. `sc-01` |
| `target_context` | enum | yes | `current` or `prior`. The authored correct label for Turn 2. |
| `authoring_basis` | enum | yes | `pilot`, `extended_from_pilot`, or `theoretical`. How the scenario was sourced. |
| `source_example_id` | string or null | yes | reference ID from the pilot corpus, or `null` for `theoretical` scenarios |
| `surface` | enum | yes | `wearable_live_frame` for v1. Reserved values (`mobile_app_chat`, `synthetic`) are not used in v1. |
| `turn_1_user` | string | yes | the user's first message, establishing the prior context |
| `turn_2_user` | string | yes | the user's second message, after the context shift, with an ambiguous reference |
| `turn_3_repair_anchor` | string | yes | templated repair utterance used when Turn 2 fails; runs as a secondary check |
| `turn_1_image` | string or null | no | image path for Turn 1. Plumbed for future multimodal slices; unset in v1. |
| `turn_2_image` | string or null | no | image path for Turn 2. Unset in v1. |
| `variant` | string | no | optional variant label, e.g. `without_prior_q_soft` |
| `text_proxy_degraded` | boolean | no | `true` when the scenario's visual information has no textual proxy in Turn 2 |
| `notes` | string | no | authoring commentary |

`expected_answers.json` is a dict keyed by `scenario_id`. Each entry has:

| Field | Type | Notes |
| --- | --- | --- |
| `current_answers` | list of strings | substrings indicating the model anchored to the current context |
| `prior_answers` | list of strings | substrings indicating the model anchored to the prior context |
| `clarify_indicators` | list of strings | substrings indicating the model asked a clarifying question |
| `abstain_indicators` | list of strings | substrings indicating the model refused or claimed it could not see |

These lists drive the code-side scorer, which runs alongside the
LLM-as-judge. The judge is authoritative for the primary score; the
code signals surface as a diagnostic disagreement count.

`interventions.json` is a list of intervention conditions. Each has a
`name` (`baseline`, `condition_a`, or `condition_b`) and a
`system_prompt`. The system prompt is sent as the candidate's system
prompt for every trial under that condition.

## Scoring and ranking

Each trial produces a Turn 2 judge label:

- `current`
- `prior`
- `clarify`
- `abstain`

For v1, authored targets are only `current` or `prior`. If the judge emits
`clarify` or `abstain`, that trial counts as wrong for the primary score.

### Primary score

The primary score is **balanced Turn 2 accuracy under the ranking
condition**.

```text
primary_score = (prior_class_accuracy + current_class_accuracy) / 2
```

Class accuracy is the mean across all Turn 2 trials for that class under the
ranking condition.

### Default comparison condition

`baseline` is the default condition used to compare candidate models.

`condition_a` and `condition_b` remain in the benchmark as extra checks.
Their purpose is to show prompt sensitivity, not to replace the
baseline ranking condition.

## Judge and runtime behavior

The runner supports candidate and judge models across Claude and Gemini
families.

- `--judge-family auto` is the default
- under `auto`, the judge family must differ from the candidate family to
  reduce same-family bias
- explicit `claude` or `gemini` overrides remain available

Each run emits:

- `transcripts.jsonl`
- `findings.md`
- a machine-readable manifest bundled into the findings output

The manifest records the scenario, answers, and prompt file SHAs, judge
prompt version/hash, model IDs, trial count, ranking condition, timestamp,
and git commit.

## Governance and versioning

The following benchmark content is frozen in v1:

- scenario text
- expected answers
- prompt text
- scoring semantics
- the default ranking condition

The following changes do not require a new benchmark version:

- documentation clarifications
- implementation refactors that do not change benchmark meaning
- report or manifest polish that does not affect scoring

The following changes require a new version or explicit release change:

- changing scenario wording
- changing answer keys
- changing prompt wording
- changing score semantics
- changing the default ranking condition
- expanding what the benchmark measures in a way that changes what can be
  fairly compared to v1

Future published results should cite the release tag and the manifest details
for the run being reported.

## Limitations

v1 is intentionally narrow:

- it measures one specific interaction problem relevant to product evaluation, not
  overall model quality or product quality
- image fields on the scenarios are plumbed but unset
- the class mix is skewed toward `current`, which is why the primary metric is
  balanced accuracy
- prompt conditions are useful extra checks, but `baseline` is the
  default ranking condition
- results are best used for like-for-like model comparison on the same
  benchmark release

## Where this benchmark fits

This benchmark sits near multimodal assistant evaluation, wearable or
egocentric multimodal evaluation, and context-tracking or
reference-resolution under changing context.

It uses familiar benchmark mechanics: frozen scenarios, controlled
prompt conditions, judge scoring, and saved run details.

It does not claim to be a general multimodal benchmark, a full measure of
assistant quality, or a benchmark whose main contribution is research
novelty.
