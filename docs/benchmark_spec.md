# Benchmark Spec: Wearable Assistant Context Bench

## Overview

The Wearable Assistant Context Bench tests one specific failure
mode of AI wearable assistants the user is actively engaging with
for advice or coaching (smart glasses, ear worn devices), with
audio/video/text input and audio/text output. When the user's
situation changes between turns, does the model respond from the
current situational evidence, or does it stay anchored to the prior
context?

The benchmark measures **cross-turn reference resolution**: whether the
model resolves the user's reference (their "this", "that", or "it")
to the current video frame instead of staying anchored to an earlier
one. (In standard ML and dialog terminology this is reference
resolution under cross-turn context shift; this document uses
**cross-turn reference resolution** throughout. This is distinct from
dialogue state tracking (DST), which fills slots from text alone.
Here the resolution depends on a perceptual frame, not slot
intents.)

An in-the-moment multimodal coach lives in a continuous stream. The
user puts down one object and picks up another. The user moves from
the workbench to the kitchen. The pan was empty a minute ago and now
holds simmering sauce. Each turn is a new chance for the model to
either update or stay stuck.

This benchmark is narrow on purpose. A model that fails it cannot
serve as an in-the-moment multimodal assistant; a model that passes
still needs separate evaluation for everything below.

## Scope boundaries: out-of-scope by design vs. limitations

**Out of scope by design.** The benchmark does not measure these and
does not intend to. Evaluate them separately:

- Coaching advice quality (correctness, safety, domain appropriateness)
- Multi-turn conversation dynamics beyond three turns
- Proactive coaching (assistance offered without a direct question)
- Domain expertise depth
- Latency, cost, and serving characteristics
- Speaker attribution, addressee detection, ambient audio

**Limitations (future follow-ups).** The benchmark could measure these
but does not yet, due to resource constraints:

- Human inter-annotator agreement on judge labels (the
  benchmark currently reports cross-LLM judge agreement only)
- Real-video validation on a held-out sample (the benchmark uses
  scene descriptions in text as a proxy)
- Raw-audio validation (the benchmark uses text transcripts as a proxy)
- Multi-trial variance reporting beyond the default (1 trial at
  temperature 0). Multi-trial runs only become meaningful at
  non-zero temperature.
- Full omnimodal stack (live audio I/O, real-time streaming, voice
  output)

See `## Design decisions` below for priority ranking.

## What the model and judge see

Each scenario splits its content between what the candidate model sees and what the judge sees:

| Channel | Field(s) | Visible to candidate | Visible to judge |
|---|---|---|---|
| Audio | `turn_1_user`, `turn_2_user`, `turn_3_repair_prompt` | Yes | Yes |
| Camera | `context_image`, `turn_1_image`, `turn_2_image` | Yes (as `[Camera: ...]` blocks) | Yes |
| Ground truth | `current_answers`, `prior_answers`, `clarify_indicators`, `abstain_indicators` | No | Yes |

The candidate model sees what a wearable would see: the user's spoken
words, plus a scene description of the video frame at each turn.

Both perceptual inputs are text proxies. The user's spoken
turns are represented as **text transcripts**, not raw audio. The
benchmark does not test acoustic grounding, speaker attribution,
addressee detection, or ambient audio cues. The video frame is
represented as a **scene description in text** (what a vision system
would say about a frame: shape, material, color, motion, position,
without naming the object directly), not a raw frame. The benchmark
does not score performance on real video. Both proxies are
deliberate: they let the benchmark isolate cross-turn reference
resolution from variability in the perceptual front-end. Raw-audio
and real-video variants are future work.

The judge sees the user message and the scene description plus the
gold answer keys, which name the actual objects in frame. The
candidate never sees the gold answer keys.

This split is the point of the benchmark. The candidate has to infer
from scene cues alone (shape, motion, material, position) which
context the question refers to. The judge has the privileged
information needed to score whether the candidate got it right.

For the rules that govern how each input field is written, see
[`scenario_authoring_rules.md`](scenario_authoring_rules.md).

## Scenario structure

Each scenario has three turns:

1. **Turn 1.** Optional `context_image` injected first (only on
   `cross_session_reference` scenarios), then `turn_1_image` plus
   `turn_1_user`. Turn 1 establishes the starting state.
2. **Turn 2.** `turn_2_image` plus `turn_2_user`. The image has
   changed. The user's question is natural and deictic; it does not
   announce the change. **Turn 2 is the only turn that contributes
   to the primary metric.**
3. **Turn 3.** `turn_3_repair_prompt`. Opt-in via `--enable-repair`
   (default off). When enabled and the candidate misses Turn 2, the
   anchor is sent as a follow-up; the judge labels the Turn 3
   response the same way it labels Turn 2. Used to compute the
   repair rate when enabled.

**Repair rate.** (Opt-in.) When `--enable-repair` is set and
the model gets Turn 2 wrong, the user clarifies with a follow-up like
"I mean the hammer I'm holding now, not the one from before." The
repair rate is how often the model fixes its answer after this kind
of correction. It measures how recoverable a Turn 2 miss is. Default
runs (without `--enable-repair`) record the Turn 2 outcome as-is and
the repair-rate section is omitted from the report.

Field reference is in [`schema.md`](schema.md).

## Video block injection format

The runner builds each user turn as:

```text
[Camera: {turn_N_image}]
{turn_N_user}
```

When `turn_N_image` is null, the `[Camera: ...]` block is omitted and only the
user message is sent. When `context_image` is populated, it is injected
as a `[Camera: ...]` block before Turn 1, with no accompanying user
message. This represents what the wearable's video showed before the
user started speaking.

The candidate model sees the `[Camera: ...]` block as part of the user turn.
The judge receives the same content plus a separate ground-truth
section.

The implementation lives in `_build_message` and
`_build_context_image_message` in `wearable_assistant_context_bench/runner.py`.

## The 8 shift-type categories

Every scenario fits exactly one category. Categories describe the
shape of the context shift between Turn 1 and Turn 2. The shift type
is stored as the `change_type` field in the data files.

| Category | Description |
|---|---|
| `object_in_hand` | User puts down one object, picks up another. The video shows a different object in the user's hand. |
| `object_state` | Same object, different state (cooking progress, paint drying, plant growth). |
| `sequential_task` | Same task, the user has progressed to a later step. |
| `location` | Whole scene changes; user moves to a different room or work area. |
| `object_in_view` | The video stays roughly in place; the user's attention has shifted to a different object visible in the scene. |
| `absent_referent` | The object the question is about is no longer in frame. |
| `screen_content` | Both Turn 1 and Turn 2 are looking at a screen; the screen content has changed. |
| `cross_session_reference` | Requires `context_image`; Turn 2 asks about a state that existed before Turn 1. |

In prose throughout the docs we call these "shift types" or
"scenario categories." The data field name is `change_type`.

## Target context labels

Each scenario carries a `target_context` field naming the correct
grounding target for a well-functioning assistant. One of:

| Value | Meaning |
|---|---|
| `current` | The correct answer refers to what the video shows right now (Turn 2 frame). |
| `prior` | The correct answer refers to something from an earlier scene (Turn 1 frame, or `context_image`). |
| `clarify` | The question is ambiguous given the available context; the assistant should ask for clarification rather than guessing. |
| `abstain` | The needed information is not present in the context; the assistant should decline rather than hallucinating. |

## Scoring

For each Turn 2 response, the judge emits exactly one of the four
labels: `current`, `prior`, `clarify`, or `abstain`. A scenario is
counted correct when the judge's label matches `target_context`.

The primary metric is **mean per-class recall**: the mean of
`current_recall` and `prior_recall` under the `baseline` prompt
condition. These are class recall values (`TP / (TP + FN)`), not
overall accuracy. With four judge labels, "correct" means the judge
label equals the scenario's `target_context`, so each class has its
own denominator equal to the count of trials in that target class.
`current` and `prior` are the two scored classes because the bank is
dominated by them (33 and 12 scenarios respectively); `clarify` (3)
and `abstain` (2) are too small to support reliable per-class recall
on their own.

```text
primary_score = mean(current_recall, prior_recall)
```

The primary metric is reported with both a 95% normal-approximation CI
and a 95% percentile bootstrap CI; per-class numbers carry 95% Wilson
CIs. The findings template additionally reports per-pack recall
(bank vs contrast), per change-type recall (`change_type`), contrast
pair consistency (when `pair_id` metadata is present), and hedging
behavior (clarification rate, abstention rate, coverage).

`clarify` and `abstain` rates still appear in the findings output as
auxiliary diagnostic rows. They do not enter the primary number.

Deterministic substring containment is also computed alongside the
judge label. The substring scorer uses word-boundary matching
(`re.search(r'\b<token>\b', response, re.IGNORECASE)`) against the
four answer lists. This produces code signals that travel with the
trial record but are not the score; the headline metric is the judge
label.

## The judge

A second LLM labels each Turn 2 response as `current`, `prior`,
`clarify`, or `abstain`. It sees:

1. A neutral scenario description with the Turn 1 user message and
   the fact that the user's context shifts between turns. It does
   not see the target label, the shift type, or the authoring notes,
   since those would give away the answer.
2. The Turn 2 user message.
3. The candidate's Turn 2 response.
4. The four answer lists.
5. A **ground-truth context section** with plain-language
   descriptions of the Turn 1 and Turn 2 video frames (plus the
   pre-conversation frame for recall scenarios). This is what tells
   the judge which frame the response actually matches.

The judge returns a JSON verdict with one label and a one-sentence
rationale. See `wearable_assistant_context_bench/llm_judge.py` for the prompt and parsing logic.
The judge prompt is versioned (`JUDGE_PROMPT_VERSION`) and hashed
into the run manifest. The privileged-field constraint (no
`target_context`, `change_type`, or authoring `notes` in the rendered
prompt) is enforced by `tests/test_llm_judge.py`.

**Cross-family default.** `--judge-family auto` picks a judge from a
different model family than the candidate (Claude → Gemini, Gemini →
OpenAI, OpenAI → Gemini); the mapping is in `resolve_judge_family`
in `wearable_assistant_context_bench/llm_judge.py`. Pass `--judge-family claude|gemini|openai`
to override. The default is cross-family because a model judging
itself can score itself too high or too low.

## Repair turn (Turn 3)

Turn 3 is opt-in via `--enable-repair`. When the flag is set and the
candidate misses on Turn 2, the runner appends the repair anchor as
a follow-up user message. The repair anchor names the intended frame
explicitly (for example, `"I mean the hammer I'm holding now, not
the screwdriver from before"`). The model gets one more chance to
respond. The judge labels the Turn 3 response the same way it
labeled Turn 2.

`--repair-style {named,deictic}` controls the anchor: `named`
(default, canonical floor metric) uses the explicit
`turn_3_repair_prompt`; `deictic` uses `turn_3_repair_prompt_deictic`
when populated and falls back to `named` for scenarios where a
deictic gesture cannot resolve the reference (`absent_referent`,
`cross_session_reference`, target_context other than `current`).

The repair rate is the fraction of Turn 2 misses that pass on Turn 3.
It is reported as a secondary product-facing metric and stands in for
the cost of user correction. It is not part of the primary metric.
With repair disabled (the default), the report omits this section.

## Reproducibility

Each run emits a manifest recorded in the findings output. The
manifest fields include:

- `benchmark_version`: the runner code version (`v0.1`)
- `schema_revision`: internal scenario data-format counter (integer)
- `camera_injection`: boolean; always `true`
- `subset`: `"bank"` or `"contrast"`, naming the pack the run evaluated
- `scenarios_sha256`: hash of `data/scenarios.jsonl`
- `interventions_sha256`: hash of `data/prompt_conditions.json`
- `judge_prompt_version`, `judge_prompt_sha256`: judge prompt
  identification
- `candidate_model`, `judge_model`, `judge_family`,
  `judge_family_resolution`: model and resolution mode
- `trials`, `temperature`, `ranking_condition`, `enable_repair`: run
  parameters
- `timestamp_utc`, `runner_git_commit`: run identity

Two runs with the same `scenarios_sha256` and `judge_prompt_sha256`
evaluate against the same benchmark content. Comparison across runs
is meaningful when those hashes match.

In addition to the per-run manifest, the repo commits
`data/MANIFEST.lock.json` with the SHA256 hashes of the
scenario bank, prompt conditions, and judge prompt template. `scripts/validate_scenarios.py` checks computed
hashes against this lockfile; CI fails if they drift without a
coordinated `BENCHMARK_VERSION` bump. This catches silent mutations
of the bank between releases.

## Related work

This benchmark borrows two design moves from recent multimodal
benchmarks. The semantic-leakage check (Check 5 in the validator) is
adapted from MMStar (Chen et al., NeurIPS 2024), which proposed
running questions through text-only models to filter items that don't
actually require vision. The audio/scene description separation is
adapted from VLSBench (Hu et al., ACL 2025), which showed that text
queries often leak the visual content of an image; we apply the same
separation principle to context cues. The non-labeled scene
description style follows Ego4D narrations (Grauman et al., CVPR
2022).

This benchmark is narrower (50 scenarios, single failure mode) and
product-focused, where the cited benchmarks operate at research
scale. They establish methods; this is a working evaluation built
around a specific product question.

## Configuration and runtime defaults

The runner loads its defaults from `data/config.json`. Key defaults:

- `trials_per_cell: 1`. Multiple trials are only meaningful at
  non-zero temperature; when used, variance is reported via Wilson
  CIs over the trial outcomes per scenario/condition cell.
- `enable_repair: false`. The Turn 3 deictic repair turn is opt-in.
  Without `--enable-repair` (or `enable_repair: true` in config), a
  Turn 2 failure is recorded as-is and no Turn 3 message is sent.
- `subset: "bank"`. The 50-scenario primary bank. Use `--subset contrast`
  for the 20-scenario distractor-rich pack.
- `temperature: 0.0`, for reproducibility.

CLI flags override the config file. Use `--config <path>` to point at
an alternate config.

## Design decisions

### Pack composition: 50-scenario bank + 20-scenario contrast pack

v1 ships 50 scenarios as the Scenario Bank (`subset: "bank"`) plus a
separately-tagged 20-scenario contrast pack (`subset: "contrast"`).
Authoring is the bottleneck. Every scenario passes a 10-point
checklist plus four programmatic checks, and 50 scenarios authored
to that bar buys editorial control. 5,000 noisier scenarios would
buy statistical generalization at the cost of that control. The
contrast pack exists because frontier models can ceiling out at the
top of a balanced bank, and a separately-tagged distractor pack
discriminates at the high end without re-authoring the core 50.

The pack is named `contrast` rather than `adversarial` because
"adversarial" in ML usually means inputs optimized to attack a
specific model. These are not that; they are controlled minimal
pairs designed to discriminate by foregrounding distractors.

### Eight shift-type categories

`change_type ∈ {object_in_hand, object_state, sequential_task, location,
object_in_view, absent_referent, screen_content, cross_session_reference}`.
Distribution: 12 / 8 / 6 / 6 / 5 / 5 / 4 / 4. These cover the failure
modes seen in product testing on AI wearable coaching assistants:
`object_in_hand` is the dominant case (the hammer→screwdriver
example); `object_state` covers cooking-progress-style shifts;
`sequential_task` covers procedural drift; `location` covers room
changes; `object_in_view` covers attention shifts within a static
scene; `absent_referent` covers the question-about-something-no-
longer-visible case; `screen_content` covers tablet/phone shifts;
`cross_session_reference` covers the user asking about state from
before the assistant was listening. 

### Cross-family judging by default + a shared judge

`--judge-family auto` picks a judge from a different family than the
candidate (Claude → Gemini, Gemini → OpenAI, OpenAI → Gemini). A
model judging itself can self-prefer or under-rate; cross-family
judging removes that confound for per-run integrity. For ranking
multiple candidates against each other, `--ranking-judge-family`
holds one judge constant across the whole sweep so candidate quality
is isolated from judge strictness.

### Class recall vs overall accuracy

The primary metric is the **mean of `current_recall` and
`prior_recall`**, not overall accuracy. With four judge labels
(`current`, `prior`, `clarify`, `abstain`), a trial is correct only
when the judge label equals the scenario's `target_context`, so each
class has its own denominator. We report per-class recall (TP / (TP +
FN)) for the two scored classes and take their mean as the headline.
Clarify and abstain are diagnostic (auxiliary), not primary.

### Single trial at temperature 0 by default

Multiple trials are only meaningful at non-zero temperature. The
benchmark defaults to one trial per cell so headline numbers are reproducible
without repeated sampling. Runs that need variance reporting set a
non-zero temperature and pass `--trials N`; the report computes
Wilson CIs over the per-trial pass outcomes.

### Repair turn is opt-in

Turn 3 is opt-in via `--enable-repair`. The repair anchor names the
intended frame explicitly. It is a recovery rate metric, not
part of the primary metric, and the report omits the section
entirely when repair is disabled.

### Frozen content + lockfile

The scenario bank, prompt conditions, and judge prompt template are
hashed into `data/MANIFEST.lock.json`. CI fails on any drift
without a coordinated `BENCHMARK_VERSION` (or `JUDGE_PROMPT_VERSION`)
bump. This catches silent mutations between releases. To refresh the
lockfile after a deliberate content change, run
`python scripts/regen_manifest_lock.py`.

## How to read a run's primary metric

The primary metric on its own only tells you how often the model got
the right context. Read it alongside three secondary signals the
report emits.

`current_recall` vs `prior_recall`. A model that is great at
`current` and terrible at `prior` is over-anchored to the latest
frame. The reverse is rarer but signals a model that ignores the
new frame.

Coverage (`1 − clarify_rate − abstain_rate`). Below ~0.6, the model
is hedging on a majority of trials. The primary metric then reflects
only the substantive responses, not the model's overall helpfulness.

Per-pack split. A model that scores 80% on `bank` and 50% on
`contrast` is fragile under distractors. A model that scores 65% on
both is more robust at the same headline number.

When comparing two candidates, use the bootstrap CI on the primary
score for the headline comparison and the per-class Wilson CIs to
diagnose where the gap is.

## Reference

- Schema and field-level definitions: [`schema.md`](schema.md)
- Authoring rules and validation checklist:
  [`scenario_authoring_rules.md`](scenario_authoring_rules.md)
- Per-run findings: [`findings.md`](findings.md)
- Dataset card with bank statistics:
  [`../data/README.md`](../data/README.md)
