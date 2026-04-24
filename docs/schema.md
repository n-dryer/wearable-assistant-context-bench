# Schema Reference

Field definitions for `benchmark/v1/scenarios.json` and
`benchmark/v1/expected_answers.json`.

---

## scenarios.json

A flat JSON array. Each element is a scenario object.

| Field | Type | Required | Description | Example |
|---|---|---|---|---|
| `scenario_id` | string | yes | Unique identifier. Format `sc-NN`. | `"sc-01"` |
| `target_context` | enum | yes | The correct grounding target for a well-functioning assistant. One of `current`, `prior`, `clarify`, `abstain`. | `"current"` |
| `authoring_basis` | enum | yes | Source of the scenario. One of `pilot`, `extended_from_pilot`, `theoretical`. | `"extended_from_pilot"` |
| `source_example_id` | string or null | yes | Internal reference to the source pilot example, or `null` if none. | `"ex-09"` |
| `surface` | enum | yes | Interaction surface. All v1 scenarios use `wearable_live_frame`. | `"wearable_live_frame"` |
| `cue_type` | string | no | Internal tag describing the main cue shape (e.g., `object_shift`, `location_shift`, `screen_shift`). | `"object_shift"` |
| `activity_domain` | string | no | Domain tag (e.g., `workshop`, `kitchen`, `fitness`). | `"workshop"` |
| `time_gap_bucket` | string | no | Approximate time between Turn 1 and Turn 2 (e.g., `seconds`, `minutes`, `hours`, `next_day`). | `"seconds"` |
| `ambiguity_marker` | string | no | The deictic or ambiguous reference word in Turn 2 (e.g., `this one`, `it`, `here`). | `"this one"` |
| `modality_required` | string | no | Whether text alone is sufficient to answer, or an image is required. One of `text_sufficient`, `image_required`. | `"text_sufficient"` |
| `cognitive_load` | string | no | Internal complexity estimate. One of `single_referent`, `multi_referent`. | `"single_referent"` |
| `difficulty_tier` | string | no | Internal difficulty estimate. One of `easy`, `medium`, `hard`. | `"medium"` |
| `turn_1_user` | string | yes | First user message. Establishes the earlier reference state. | `"I'm at my workbench..."` |
| `turn_2_user` | string | yes | Second user message after the context change. The message the candidate model must answer correctly. | `"Am I holding this one correctly?"` |
| `turn_3_repair_anchor` | string | yes | Repair prompt fired after a Turn 2 miss. Empty string if no repair is defined. | `"I mean the hammer I'm holding now."` |
| `turn_1_image` | string or null | no | Reserved image path for Turn 1. Null in all text-only scenarios. | `null` |
| `turn_2_image` | string or null | no | Reserved image path for Turn 2. Null in all text-only scenarios. | `null` |
| `variant` | string or null | no | Variant label when a scenario has a paired contrast version. Null on 100 of 101 scenarios; only `sc-06` uses this field currently. | `null` |
| `text_proxy_degraded` | boolean | no | True when the text transcript understates the visual distinction that a real device would provide. Informational only; does not affect scoring. | `true` |
| `notes` | string | no | Authoring commentary. Not used by the runner. | `"v2 optimization: ..."` |

### target_context values

| Value | Meaning |
|---|---|
| `current` | The correct answer refers to what the user is looking at, holding, or interacting with right now. |
| `prior` | The correct answer refers to something from an earlier turn or scene. |
| `clarify` | The question is ambiguous given the available context; the assistant should ask for clarification rather than guessing. |
| `abstain` | The needed information is not present in the context; the assistant should decline to answer rather than hallucinating. |

---

## expected_answers.json

A dict keyed by `scenario_id`. Each value is an object with four lists.

| Field | Type | Description | Example |
|---|---|---|---|
| `current_answers` | list of strings | Substrings indicating the response is grounded in the current context. A response is scored correct on a `current` scenario if it contains any of these tokens (word-boundary, case-insensitive). | `["hammer", "claw hammer"]` |
| `prior_answers` | list of strings | Substrings indicating the response is grounded in the prior context. Used to score `prior` scenarios and to detect confident-wrong answers on `clarify`/`abstain` scenarios. | `["screwdriver", "Phillips"]` |
| `clarify_indicators` | list of strings | Substrings indicating a clarifying question or expression of uncertainty. Used to score `clarify` scenarios. | `["which one", "do you mean"]` |
| `abstain_indicators` | list of strings | Substrings indicating refusal or inability to answer. Used to score `abstain` scenarios. | `["can't tell", "not sure"]` |

All four lists may be empty. A `current` scenario only needs `current_answers` populated; `clarify_indicators` and `abstain_indicators` may be empty on it.

### Scoring contract

Scoring is deterministic substring containment with word-boundary matching (`re.search(r'\b<token>\b', response, re.IGNORECASE)`). See `docs/benchmark_spec.md` for the full scoring rules.
