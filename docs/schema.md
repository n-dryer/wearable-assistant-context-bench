# Schema Reference

Field definitions for `benchmark/v1/scenarios.json` and
`benchmark/v1/expected_answers.json`.

The benchmark uses a three-channel design. The candidate model sees two
of these channels: the audio (user speech) and the camera (image
descriptions). The third channel — ground truth answers — is visible
only to the judge.

For the rules that govern how each channel is written, see
[scenario_authoring_rules.md](scenario_authoring_rules.md).

---

## scenarios.json

A flat JSON array. Each element is a scenario object.

| Field | Type | Required | Description | Example |
|---|---|---|---|---|
| `scenario_id` | string | yes | Unique identifier. Format `sc-NN`. | `"sc-01"` |
| `target_context` | enum | yes | The correct grounding target for a well-functioning assistant. One of `current`, `prior`, `clarify`, `abstain`. | `"current"` |
| `cue_type` | enum | yes | The category of context shift between T1 and T2. See list below. | `"object_in_hand"` |
| `activity_domain` | string | yes | Domain tag (e.g., `workshop`, `kitchen`, `garden`). Used for coverage reporting. | `"workshop"` |
| `cognitive_load` | enum | yes | Internal complexity estimate. One of `single_referent`, `multi_referent`, `distractor_present`, `absent_referent`, `compound_shift`. | `"single_referent"` |
| `difficulty_tier` | enum | yes | Internal difficulty estimate. One of `easy`, `medium`, `hard`. | `"medium"` |
| `time_gap_bucket` | enum | no | Approximate time between Turn 1 and Turn 2. One of `seconds`, `minutes`, `hours`, `next_day`. | `"seconds"` |
| `context_image` | string or null | yes | Camera description of what was visible **before the conversation started**. Null when `turn_1_image` already establishes the starting state. Required for scenarios where the user asks about a state from before T1. | `null` |
| `turn_1_image` | string or null | yes | Camera description at the moment T1 is spoken. Perceptual; describes physical properties without naming the object. | `"Hand resting on a slim metal handle..."` |
| `turn_1_user` | string | yes | First user message. Natural speech only. Must not narrate visible objects or evaluate technique. | `"How do I get more torque on this?"` |
| `turn_2_image` | string or null | yes | Camera description at the moment T2 is spoken. Different from `turn_1_image` (this is where the context shift becomes visible). | `"Hand wrapped around a wooden handle..."` |
| `turn_2_user` | string | yes | Second user message after the context change. Natural follow-up. Must not announce the shift. | `"Am I doing this right?"` |
| `turn_3_repair_anchor` | string | yes | Repair prompt fired after a Turn 2 miss. Names the intended frame explicitly. | `"I mean the hammer I'm holding now."` |
| `notes` | string | no | Authoring commentary. Not used by the runner. | `"Object swap mid-task; T2 deictic."` |

### target_context values

| Value | Meaning |
|---|---|
| `current` | The correct answer refers to what the camera sees right now (T2 frame). |
| `prior` | The correct answer refers to something from an earlier scene (T1 or `context_image`). |
| `clarify` | The question is ambiguous given the available context; the assistant should ask for clarification rather than guessing. |
| `abstain` | The needed information is not present in the context; the assistant should decline to answer rather than hallucinating. |

### cue_type values

The eight categories of context shift. Each scenario fits exactly one.

| Value | Description |
|---|---|
| `object_in_hand` | User puts down one object, picks up another. Camera sees a different object in the user's hand. |
| `object_state` | Same object, different state (cooking progress, paint drying, etc.). |
| `sequential_task` | Same task, the user has progressed to a later step. |
| `location` | Whole scene changes; user moves to a different room or work area. |
| `object_in_view` | Camera stays roughly in place; the user's attention has shifted to a different object visible in the scene. |
| `absent_referent` | The object the question is about is no longer in frame. |
| `screen_content` | Both T1 and T2 are looking at a screen; the screen content has changed. |
| `pre_conversation_recall` | Requires `context_image`; T2 asks about a state that existed before T1. |

---

## expected_answers.json

A dict keyed by `scenario_id`. Each value is an object with four lists.
**This file is judge-only.** The candidate model never sees it.

| Field | Type | Description |
|---|---|---|
| `current_answers` | list of strings | Vocabulary indicating a response grounded in the current (T2) context. Includes object name, technique or action vocabulary specific to that object, and state or condition descriptors. |
| `prior_answers` | list of strings | Vocabulary indicating a response anchored to the prior (T1) context. Same three-category structure. |
| `clarify_indicators` | list of strings | Vocabulary indicating a clarifying question or expression of uncertainty. Used to score `clarify` scenarios. |
| `abstain_indicators` | list of strings | Vocabulary indicating refusal or inability to answer. Used to score `abstain` scenarios. |

### Required vocabulary categories per answer list

For `current_answers` and `prior_answers`, every list must include at
least one item from each of these three categories:

1. The object name (e.g., `"hammer"`, `"screwdriver"`)
2. Technique or action vocabulary specific to that object (e.g., `"swing"`, `"torque"`, `"grip near the end"`)
3. State or condition descriptors (e.g., `"flat face"`, `"crosshead tip"`, `"partially driven"`)

This three-category rule ensures the judge can score responses that
name the object, responses that describe technique without naming the
object, and responses that describe state — all as evidence of which
context the model used.

### Scoring contract

Scoring is deterministic substring containment with word-boundary
matching: `re.search(r'\b<token>\b', response, re.IGNORECASE)`. See
[`docs/benchmark_spec.md`](benchmark_spec.md) for the full scoring
rules.

---

## Removed fields

The following fields existed in earlier scenario formats and are no
longer part of the schema:

- `text_proxy_degraded` — replaced by the camera channel; no longer
  meaningful
- `modality_required` — replaced by required `turn_1_image` /
  `turn_2_image`; no longer meaningful
- `authoring_basis` — replaced by `cue_type` and category-driven
  authoring
- `source_example_id` — internal reference no longer tracked
- `surface` — single value (`wearable_live_frame`) made the field
  redundant
- `ambiguity_marker` — implicit in deictic user speech, not separately
  tagged
- `variant` — paired-contrast versions are not used
