# Benchmark Spec: Wearable Assistant Context Benchmark

## Overview

The Wearable Assistant Context Benchmark tests one specific failure mode
of multimodal wearable assistants: when the user's situation changes
between turns, does the model respond from the current situational
evidence, or does it stay anchored to the prior context?

A wearable assistant lives in a continuous stream. The user puts down
one object and picks up another. The user moves from the workbench to
the kitchen. The pan was empty a minute ago and now holds simmering
sauce. Each turn is a new chance for the model to either update or stay
stuck.

This benchmark is narrow on purpose. It does not measure whether the
assistant's coaching advice is correct, safe, or domain-appropriate.
It does not measure multi-turn conversation dynamics beyond a 3-turn
structure. It does not measure performance on real video frames.
It does not measure proactive coaching. A model that fails this
benchmark is unlikely to be viable as a wearable assistant. A model
that passes still needs separate evaluation for everything this
benchmark does not measure.

## The three-channel design

Every scenario uses three distinct channels. Each channel carries
different content and is visible to a different audience.

| Channel | Field(s) | Visible to candidate | Visible to judge |
|---|---|---|---|
| Audio | `turn_1_user`, `turn_2_user`, `turn_3_repair_anchor` | Yes | Yes |
| Camera | `context_image`, `turn_1_image`, `turn_2_image` | Yes (as `[Camera: ...]` blocks) | Yes |
| Ground truth | `current_answers`, `prior_answers`, `clarify_indicators`, `abstain_indicators` | No | Yes |

The candidate model sees what a wearable would see: the user's spoken
words, plus a perceptual description of the camera frame at each turn.
The judge sees the same thing plus the ground-truth answer keys, which
name the actual objects in frame. The candidate never sees the answer
keys.

This separation is the point of the benchmark. The candidate has to
infer from perceptual cues alone — shape, motion, material, position —
which context the question refers to. The judge has the privileged
information needed to score whether the candidate got it right.

For the rules that govern how each channel is written, see
[`scenario_authoring_rules.md`](scenario_authoring_rules.md).

## Scenario structure

Each scenario is a 3-turn conversation:

1. **Turn 1** — Optional `context_image` injected first (only on
   `pre_conversation_recall` scenarios), then `turn_1_image` plus
   `turn_1_user`. T1 establishes the starting state.
2. **Turn 2** — `turn_2_image` plus `turn_2_user`. The image has
   changed. The user's question is natural and deictic; it does not
   announce the change.
3. **Turn 3** — `turn_3_repair_anchor`. Fired only when the candidate
   misses on T2. Names the intended frame explicitly. Used to compute
   the simulated repair rate.

Field reference is in [`schema.md`](schema.md).

## Camera injection format

The runner builds each user turn as:

```text
[Camera: {turn_N_image}]
{turn_N_user}
```

When `turn_N_image` is null, the camera block is omitted and only the
user message is sent. When `context_image` is populated, it is injected
as a `[Camera: ...]` block before T1, with no accompanying user
message — this represents what the wearable's camera saw before the
user started speaking.

The candidate model sees the camera block as part of the user turn.
The judge receives the same content plus a separate ground-truth
section.

The implementation lives in `_build_message` and
`_build_context_image_message` in `benchmark/v1/run.py`.

## The 8 cue_type categories

Every scenario fits exactly one category. Categories describe the
shape of the context shift between T1 and T2.

| Category | Description |
|---|---|
| `object_in_hand` | User puts down one object, picks up another. Camera sees a different object in the user's hand. |
| `object_state` | Same object, different state (cooking progress, paint drying, plant growth). |
| `sequential_task` | Same task, the user has progressed to a later step. |
| `location` | Whole scene changes; user moves to a different room or work area. |
| `object_in_view` | Camera stays roughly in place; the user's attention has shifted to a different object visible in the scene. |
| `absent_referent` | The object the question is about is no longer in frame. |
| `screen_content` | Both T1 and T2 are looking at a screen; the screen content has changed. |
| `pre_conversation_recall` | Requires `context_image`; T2 asks about a state that existed before T1. |

## Target context labels

Each scenario carries a `target_context` field naming the correct
grounding target for a well-functioning assistant. One of:

| Value | Meaning |
|---|---|
| `current` | The correct answer refers to what the camera sees right now (T2 frame). |
| `prior` | The correct answer refers to something from an earlier scene (T1 frame, or `context_image`). |
| `clarify` | The question is ambiguous given the available context; the assistant should ask for clarification rather than guessing. |
| `abstain` | The needed information is not present in the context; the assistant should decline rather than hallucinating. |

## Scoring

For each Turn 2 response, the judge emits exactly one of the four
labels: `current`, `prior`, `clarify`, or `abstain`. A scenario is
counted correct when the judge's label matches `target_context`.

The primary score is **balanced accuracy across `current` and `prior`
under the `baseline` prompt condition**. Balanced means the mean of
per-class accuracy across the two scored classes, so one class does
not dominate the headline number. `current` and `prior` are the two
scored classes because the bank is dominated by them (33 and 12
scenarios respectively); `clarify` (3) and `abstain` (2) are too small
to support reliable per-class accuracy on their own.

`clarify` and `abstain` accuracy still appear in the findings output
as auxiliary diagnostic rows. They do not enter the primary number.

Deterministic substring containment is also computed alongside the
judge label. The substring scorer uses word-boundary matching
(`re.search(r'\b<token>\b', response, re.IGNORECASE)`) against the
four answer lists. This produces code signals that travel with the
trial record but are not the score; the headline metric is the judge
label.

## The judge

A second LLM acts as the judge. The judge sees:

1. A short scenario description (cue type, target context, activity
   domain).
2. The Turn 2 user message.
3. The candidate's Turn 2 response.
4. The four answer lists for the scenario.
5. A **ground-truth context section** that names the objects in the
   T1 and T2 frames in plain language.

The judge emits a JSON verdict naming one of the four labels and a
one-sentence rationale. See `core/llm_judge.py` for the prompt and
parsing logic. The judge prompt is versioned (`JUDGE_PROMPT_VERSION`)
and hashed into the run manifest.

### Cross-family default

By default, `--judge-family auto` resolves to a different model
family than the candidate. For example, a Claude candidate gets a
Gemini judge by default; a Gemini candidate gets an OpenAI judge.
The mapping is in `resolve_judge_family` in `core/llm_judge.py`.

Explicit `--judge-family claude|gemini|openai` overrides the default.

The cross-family default reduces the chance that a candidate model
appears to perform unusually well or unusually badly because the same
model is judging itself.

## Repair turn (T3)

When the candidate misses on T2, the runner appends the repair anchor
as a follow-up user message. The repair anchor names the intended
frame explicitly (for example, `"I mean the hammer I'm holding now,
not the screwdriver from before"`). The model gets one more chance to
respond. The judge labels the T3 response the same way it labeled T2.

The simulated repair rate is the fraction of T2 misses that pass on
T3. It is reported as a secondary product-facing metric and stands in
for the cost of user correction. It is not part of the primary score.

## Reproducibility

Each run emits a manifest recorded in the findings output. The
manifest fields include:

- `benchmark_version` — the runner code version (`v1`)
- `schema_revision` — internal scenario data-format counter (integer)
- `camera_injection` — boolean; always `true`
- `scenarios_sha256` — hash of `benchmark/v1/scenarios.json`
- `expected_answers_sha256` — hash of
  `benchmark/v1/expected_answers.json`
- `interventions_sha256` — hash of `benchmark/v1/interventions.json`
- `judge_prompt_version`, `judge_prompt_sha256` — judge prompt
  identification
- `candidate_model`, `judge_model`, `judge_family`,
  `judge_family_resolution` — model and resolution mode
- `trials`, `temperature`, `ranking_condition` — run parameters
- `timestamp_utc`, `runner_git_commit` — run identity

Two runs with the same `scenarios_sha256`,
`expected_answers_sha256`, and `judge_prompt_sha256` evaluate against
the same benchmark content. Comparison across runs is meaningful when
those hashes match.

## Reference

- Schema and field-level definitions: [`schema.md`](schema.md)
- Authoring rules and validation checklist:
  [`scenario_authoring_rules.md`](scenario_authoring_rules.md)
- Score interpretation and limitations:
  [`benchmark_notes.md`](benchmark_notes.md)
- Dataset card with bank statistics:
  [`../benchmark/v1/dataset_card.md`](../benchmark/v1/dataset_card.md)
