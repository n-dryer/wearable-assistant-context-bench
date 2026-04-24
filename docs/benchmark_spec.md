# Benchmark Spec: Wearable Assistant Context Benchmark

**Subtitle:** A product benchmark for comparing models on cross-turn reference resolution under context change in a wearable multimodal assistant.

## Project purpose

This benchmark exists to support a practical model-selection decision
for a live wearable assistant.

The product problem is that users should not have to keep restating
what they are looking at, holding, or referring to after they move,
swap objects, change screens, or otherwise change context. The
assistant should infer the right reference from the situational cues
already present in the interaction.

This benchmark was built from real user feedback and product testing,
then turned into a frozen scenario bank so candidate models can be
compared on the same conditions over time.

## Current v1 measured task

This benchmark is pre-release; the first public release will be
tagged `v1` alongside the accompanying benchmark results. In its
pre-release form, v1 measures **cross-turn reference resolution under
context change**.

In plain language, it checks whether the assistant answers about the
right thing after the user's context changes, instead of forcing the
user to restate what they mean.

Canonical examples:

- the user asks about a bedroom wall, walks into the kitchen, and asks
  about the wall again
- the user asks about a hammer, switches to a screwdriver, and then
  says "how do I use this?"

Although the benchmark was developed around a wearable multimodal
assistant, it can also apply to related assistant devices on or near
the user if they support live multimodal interaction.

## What canonical v1 includes

The current v1 release contains:

- **101 frozen scenarios**
- **3 prompt conditions**: `baseline`, `condition_a`, `condition_b`
- **2 trials per (scenario, condition) cell** by default
- **Turn 2 scoring only**
- **Turn 3 repair** as a secondary product check

The scenario bank includes four authored target labels:

- `current`
- `prior`
- `clarify`
- `abstain`

`current` and `prior` are the two scored classes used in the headline
metric. `clarify` and `abstain` remain in the benchmark and findings
output as auxiliary diagnostic classes.

## Runtime inputs

The active runtime inputs are:

- [`benchmark/v1/scenarios.json`](../benchmark/v1/scenarios.json)
- [`benchmark/v1/expected_answers.json`](../benchmark/v1/expected_answers.json)
- [`benchmark/v1/interventions.json`](../benchmark/v1/interventions.json)

These JSON files define the current public benchmark release.

## Scenario schema

Each entry in `scenarios.json` is an object with the following fields.

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `scenario_id` | string | yes | unique identifier, e.g. `sc-01` |
| `target_context` | enum | yes | one of `current`, `prior`, `clarify`, `abstain` |
| `authoring_basis` | enum | yes | internal source label such as `pilot`, `extended_from_pilot`, or `theoretical` |
| `source_example_id` | string or null | yes | internal source reference, or `null` |
| `surface` | enum | yes | pre-release v1 uses `wearable_live_frame` |
| `turn_1_user` | string | yes | first user message, establishing the earlier reference state |
| `turn_2_user` | string | yes | second user message after the context change |
| `turn_3_repair_anchor` | string | yes | repair prompt used only after a Turn 2 miss |
| `turn_1_image` | string or null | no | reserved optional image path |
| `turn_2_image` | string or null | no | reserved optional image path |
| `cue_type` | string | no | optional internal tag for the main cue shape |
| `activity_domain` | string | no | optional domain tag |
| `time_gap_bucket` | string | no | optional short-horizon time-gap tag |
| `ambiguity_marker` | string | no | optional ambiguity tag |
| `modality_required` | string | no | optional tag describing whether text alone is sufficient |
| `cognitive_load` | string | no | optional internal complexity tag |
| `difficulty_tier` | string | no | optional internal difficulty tier |
| `variant` | string | no | optional variant label |
| `text_proxy_degraded` | boolean | no | optional flag for scenarios where transcript proxies understate the visual distinction |
| `notes` | string | no | authoring commentary |

`expected_answers.json` is a dict keyed by `scenario_id`. Each entry
has:

| Field | Type | Notes |
| --- | --- | --- |
| `current_answers` | list of strings | substrings indicating grounding in the current context |
| `prior_answers` | list of strings | substrings indicating grounding in the prior context |
| `clarify_indicators` | list of strings | substrings indicating a clarifying question |
| `abstain_indicators` | list of strings | substrings indicating refusal or inability to answer |

These lists drive the deterministic code-side scorer. The judge remains
authoritative for the benchmark verdict.

`interventions.json` stores the three prompt conditions. Each entry has
a `name`, `description`, `system_prompt`, and `token_count`. The prompt
text is frozen for the current release.

## Scoring and ranking

Each trial produces a Turn 2 judge label:

- `current`
- `prior`
- `clarify`
- `abstain`

### Primary score

The primary score is **balanced Turn 2 accuracy under the default
comparison condition**.

Canonical v1 computes the headline score over the two scored classes:
`current` and `prior`.

```text
primary_score = (current_class_accuracy + prior_class_accuracy) / 2
```

`clarify` and `abstain` trials remain visible in the findings output,
but they are auxiliary diagnostic classes in the current release rather
than part of the headline ranking score.

### Default comparison condition

`baseline` is the default comparison condition used to rank candidate
models.

`condition_a` and `condition_b` remain in the benchmark to expose
prompt sensitivity, not to replace `baseline` as the default comparison
condition.

### Secondary metric

**Simulated repair rate** is reported as a secondary metric. It uses
Turn 3 repair prompts after Turn 2 misses as a rough stand-in for user
correction cost.

## Judge and runtime behavior

The runner supports native and LiteLLM-backed model access.

- Claude-family models
- Gemini-family models
- OpenAI-family models
- provider-qualified model IDs routed through LiteLLM, including
  supported OpenRouter and Hugging Face inference paths

Judge behavior:

- `--judge-family auto` is the default
- under `auto`, the judge should resolve to a different model family
  than the candidate whenever that can be done safely
- explicit `claude`, `gemini`, and `openai` overrides are supported

Each run emits:

- `transcripts.jsonl`
- `findings.md`
- a reproducibility manifest bundled into the findings output

The manifest records the scenario, answers, and prompt file SHAs, judge
prompt version/hash, model IDs, trial count, default comparison
condition, timestamp, and git commit.

## Audio and transcript-proxy scope

Spoken user questions already count as part of the cue set in the
benchmark. In the pre-release v1 bank, those spoken queries are
represented through transcript proxies rather than raw audio.

Canonical v1 does **not** yet directly test:

- raw acoustic grounding
- speaker attribution
- ambient audio cues

## Governance and versioning

The following benchmark content is frozen in canonical v1:

- scenario text
- expected answers
- prompt text
- scoring semantics
- the default comparison condition

The following changes do not require a new benchmark release:

- documentation clarifications
- implementation refactors that do not change benchmark meaning
- report or manifest polish that does not affect scoring
- new model adapters that preserve benchmark semantics

The following changes require a new release decision:

- changing scenario wording
- changing answer keys
- changing prompt wording
- changing score semantics
- changing the default comparison condition
- changing what counts toward the primary metric

## Limitations

Canonical v1 is intentionally product-shaped and narrow.

- It measures one recurring interaction problem, not overall assistant
  quality.
- It is a transcript-proxy benchmark, not a raw multimodal device log.
- It does not directly measure raw audio perception.
- It does not measure long-horizon memory across sessions.
- It is best used for like-for-like model comparison on the same
  release.

## Where this benchmark fits

This benchmark sits near multimodal assistant evaluation, wearable or
egocentric evaluation, and reference-resolution benchmarks. It is
narrower and more product-specific than broad embodied or streaming
benchmarks.

The goal is not to be a general multimodal benchmark. The goal is to
support one concrete model-selection question for a live assistant
product.
