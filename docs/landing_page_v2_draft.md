# Wearable Assistant Context Benchmark

v1 · Published April 2026 · 50 scenarios · 4 published runs

A smart wearable sees what you see and hears what you say. When your
situation changes — you swap tools, walk into a new room — does the
assistant follow along, or stay stuck on what was happening before?
This benchmark scores that.

---

## Why this exists

This benchmark was built to support a model-selection decision for a
wearable assistant product.

The product problem is concrete:

- A user asks about the bedroom walls, walks into the kitchen, then
  asks about the walls again. The assistant answers as if the user is
  still in the bedroom.
- A user asks about a hammer, puts it down, picks up a screwdriver,
  then asks, "how do I use this?" The assistant answers about the
  hammer.

Users should not have to restate what they are looking at. The
assistant should infer the right reference from the situational cues
already visible to the camera. One-off manual testing is not enough
to make a model-selection call. Every candidate needs to be tested
on the same scenarios, with the same prompt conditions, the same judge
rules, and a saved run record. That is what this benchmark does.

In standard dialog evaluation terminology, the task is **reference
resolution under cross-turn context shift**. We use **context
tracking** as the plain-language name throughout.

---

## What this benchmark measures

One specific capability: **whether a model uses current situational
evidence from the visual context, or stays anchored to prior context
after a change.**

This is not a coaching benchmark. It does not measure whether the
advice is correct, safe, or domain-appropriate. A confidently wrong
answer can pass if it picks the right context. A perfectly safe answer
can fail if it picks the wrong one.

A model that fails this benchmark is unlikely to be viable as a
wearable assistant. A model that passes still needs separate
evaluation for advice quality, domain expertise, latency, and cost.

---

## How the test works

### The three-channel design

Each scenario uses three distinct information channels. The candidate
model and the judge model see different subsets:

| Channel | Content | Candidate sees | Judge sees |
|---|---|---|---|
| **Audio** | User's spoken words (`turn_1_user`, `turn_2_user`) | ✓ | ✓ |
| **Visual context** | Scene descriptions of what the camera sees (`turn_1_image`, `turn_2_image`) | ✓ (as `[Camera: ...]` blocks) | ✓ |
| **Ground truth** | Answer keys naming actual objects and expected responses | ✗ | ✓ |

The candidate has to infer from scene-level cues — shape, material,
color, motion, position — which context the user's question refers to.
The candidate never sees the object names. The judge has the privileged
ground-truth information needed to determine whether the candidate got
it right.

### Scenario structure

Each scenario has three turns:

1. **Turn 1.** The scene is established. The user asks a question.
2. **Turn 2.** The visual context has changed. The user asks a
   follow-up. The change is visible only in the camera channel — the
   user does not announce it.
3. **Turn 3 (repair).** Fired only when the candidate fails Turn 2.
   The user names the intended frame explicitly ("I mean the knife I'm
   holding now, not the spoon from before"), giving the model one
   chance to recover.

### The eight shift-type categories

Every scenario fits one of eight categories describing the kind of
context change between Turn 1 and Turn 2:

| Shift type | Count | Description |
|---|---|---|
| `object_in_hand` | 12 | User puts down one object, picks up another |
| `object_state` | 8 | Same object, different state (cooking progress, paint drying) |
| `sequential_task` | 6 | Same task, the user has progressed to a later step |
| `location` | 6 | Whole scene changes; user moves to a different room |
| `object_in_view` | 5 | Camera stays roughly in place; attention shifts to a different object |
| `absent_referent` | 5 | The object from Turn 1 is no longer in frame |
| `screen_content` | 4 | Both turns look at a screen; the screen content has changed |
| `pre_conversation_recall` | 4 | Turn 2 asks about something visible before Turn 1 |

### Scoring

The judge labels each Turn 2 response with one of four labels:

- **`current`** — the answer is about the new situation (Turn 2 frame)
- **`prior`** — the answer is about the earlier situation (Turn 1 frame)
- **`clarify`** — the model asked for clarification (appropriate when the question is ambiguous)
- **`abstain`** — the model declined to answer (appropriate when evidence is insufficient)

A scenario passes when the judge label matches the scenario's target
context. The **primary score** is **Balanced Turn 2 accuracy**: the
mean of `current`-class accuracy and `prior`-class accuracy under
the `baseline` prompt condition. Balanced means both classes are
weighted equally, so a model that always defaults to "current" cannot
score above 50%.

### How to read the primary score

- **100%** = the model always noticed the situation changed and
  answered from the correct context.
- **50%** = the model gets one direction right (e.g., always answers
  about the current frame) but fails the other (e.g., never answers
  about a prior frame when asked).
- **Below 50%** = the model is actively confused about which context
  to use.

Score deltas between models on the same scenario bank are the primary
signal. Absolute values are meaningful only relative to other runs on
the same release.

### One disclosure up front

The visual context is short text descriptions of what the camera would
see, not actual video frames. This keeps the benchmark cheap and
reproducible, but it means a model that does well here might not do
well on real video. Validation against real video frames is future work.

---

## Results

### Four experimental runs

Each row is an isolated experiment. The primary score is Balanced Turn 2
accuracy under the `baseline` prompt condition. 95% Wilson confidence
intervals are reported — these are appropriate for binary outcomes with
small N, following Bowyer et al. (2025).

| Run | Candidate | Judge | Visual context | Balanced accuracy | 95% CI | `current` acc (n=66) | `prior` acc (n=24) |
|---|---|---|---|---|---|---|---|
| **Run A** | Gemini 2.5 Flash Lite | GPT-4o-mini (cross-family) | shown | **92.8%** | | 93.9% [85–98] | 91.7% [74–98] |
| **Run B** | GPT-4o-mini | Gemini 2.5 Flash Lite (cross-family) | shown | **100.0%** | | 100% [95–100] | 100% [86–100] |
| Original | Gemini 2.5 Flash Lite | Gemini 2.5 Flash Lite (same-family) | shown | 98.5% | | 97.0% [90–99] | 100% [86–100] |
| **Run C** | Gemini 2.5 Flash Lite | GPT-4o-mini (cross-family) | **hidden** | **7.2%** | | 6.1% [2–15] | 8.3% [2–26] |

Each run: 50 scenarios × 3 prompt conditions × 2 trials = 300 model
calls. All candidates are vision-capable models from families that
ship full omnimodal stacks (vision in, audio in, audio out, real-time
streaming). Cross-family judging is used by default to mitigate
self-preference bias.

### Statistical comparison: Run A vs Run B

McNemar's paired test on 100 matched observations under `baseline`:
6 discordant scenarios, all favoring GPT-4o-mini (χ² = 4.17,
p = 0.041). The difference is statistically significant. Gemini Flash
Lite's failures concentrate in `object_in_hand` and `location` shift
types.

**Minimum detectable effect at this sample size:** ≈14 percentage
points at 80% power. Score differences smaller than this should be
treated with caution.

### Per-shift-type accuracy (baseline, Run A — Gemini Flash Lite)

| Shift type | Scenarios | Accuracy | 95% CI |
|---|---|---|---|
| `object_in_hand` | 12 | 83.3% | [64–93] |
| `location` | 6 | 83.3% | [55–95] |
| `object_state` | 8 | 100% | [81–100] |
| `sequential_task` | 6 | 100% | [76–100] |
| `object_in_view` | 5 | 100% | [72–100] |
| `absent_referent` | 5 | 100% | [72–100] |
| `screen_content` | 4 | 100% | [68–100] |
| `pre_conversation_recall` | 4 | 100% | [68–100] |

GPT-4o-mini (Run B) scores 100% on all shift types under baseline.

---

### What the runs show

**Visual context ablation — the camera channel carries the evaluation.**

Same Gemini candidate, visual context shown vs. hidden:
92.8% → 7.2% (85.6 pp drop)

Strip the visual context from the prompt and the same candidate
collapses to near-floor. The user's deictic speech alone ("is this
right?") provides almost no signal without the scene description. The
visual context channel is doing real work.

**Evaluation bias — cross-family judging corrects self-preference.**

Same Gemini candidate, judge swapped:
98.5% (same-family) → 92.8% (cross-family, 5.7 pp drop)

Gemini judging Gemini gives 98.5%. GPT-4o-mini judging the same
Gemini gives 92.8%. The gap is consistent with self-preference bias
documented in Zheng et al. (2023). Cross-family judging is the
default throughout to prevent this.

**Ceiling effect — v1 scenarios do not fully separate frontier models.**

GPT-4o-mini scores 100% on baseline. Gemini Flash Lite scores 92.8%.
Empirical difficulty analysis shows 46 of 50 scenarios are "easy"
(100% pass rate across both models under baseline). The benchmark
mechanism is validated by the ablation, but harder scenarios are needed
for v2 to separate models with finer resolution.

---

## Scope boundaries

These are permanent design decisions. The benchmark will not measure
these because they are different evaluation tasks:

- **Advice quality.** Whether the answer is correct, safe, or
  domain-appropriate.
- **Proactive coaching.** Noticing a problem without being asked.
- **Domain expertise.** Depth of knowledge in cooking, woodworking,
  fitness, etc.
- **Multi-turn dynamics.** Conversation flow past Turn 2.
- **Audio perception.** Recognizing sounds, voices, or interruptions.
- **Speaker attribution and addressee detection.** Who said what, and
  to whom.
- **Long-horizon memory.** Recall across days or weeks.

## Known v1 limitations

These are real gaps that affect how results should be interpreted.
Future versions are expected to address them:

- **Text proxy for visual context.** Scene descriptions in text stand
  in for actual video frames. Correlation with real-video performance
  is not yet measured.
- **Inter-annotator agreement not measured.** All 50 scenarios were
  written and reviewed by one person against a written checklist of
  authoring rules. Multi-rater validation is future work.
- **Judge-human agreement not formally quantified.** Cross-family
  judging mitigates self-preference bias, but formal agreement with
  human labelers (target: ≥80%, following Zheng et al. 2023) has not
  been measured.
- **Limited statistical power.** 50 scenarios × 2 trials = 100 scored
  observations per condition. Minimum detectable effect ≈14 pp. Small
  differences are not reliably distinguishable.
- **Empirical difficulty diverges from author tiers.** Author-assigned
  difficulty has 32% agreement with model-grounded difficulty. 46 of
  50 scenarios are empirically easy. v2 needs harder scenarios.
- **Repair line style is named, not deictic.** The Turn 3 repair
  explicitly names both objects. This measures floor recoverability,
  not realistic user correction behavior.
- **`prior` class is underpowered.** Only 12 `prior` scenarios (24
  observations under baseline). The 95% CI spans ±12 pp for `prior`
  accuracy. v2 needs at least 20 `prior` scenarios.
- **`clarify` and `abstain` classes are too small for reliable
  per-class scoring.** 3 and 2 scenarios respectively. These are
  diagnostic only in v1.

---

## Reference

### Glossary

**What's being tested**

- **Wearable AI assistant.** A body-worn device — smart glasses, an AI
  pin, a clip-on — that captures what the user sees and hears, paired
  with an AI model that answers questions about the live scene.
- **Context tracking.** The task this benchmark measures. When the
  user's situation changes between turns, does the model respond about
  the new situation or stay anchored to the old one. The technical name
  is reference resolution under cross-turn context shift.
- **Context shift.** A meaningful change between Turn 1 and Turn 2 in
  what the user is showing, holding, doing, or referring to.

**How the test runs**

- **Scenario.** One evaluation situation with a defined context shift,
  three turns, and a target label. The benchmark has 50 scenarios in
  v1.
- **Prompt condition.** The system prompt sent to the candidate model.
  Three conditions: `baseline` (minimal), `condition_a` (explicit
  policy-selection instruction), `condition_b` (pre-answer scaffold).
  Headline scores use `baseline`; the other two are sensitivity checks.
- **Instance.** One (scenario × condition × trial) cell. Each run has
  300 instances (50 scenarios × 3 conditions × 2 trials).
- **Visual context.** Short text descriptions of what the camera sees,
  injected as `[Camera: ...]` blocks in the user message. Stands in
  for what a real video frame would show.

**How the test is graded**

- **Judge model.** A second LLM that labels each Turn 2 response.
  Cross-family by default (e.g., Gemini candidate → OpenAI judge).
- **`current` / `prior` / `clarify` / `abstain`.** The four judge
  labels. `current` and `prior` are the scored classes. `clarify` and
  `abstain` are auxiliary diagnostics.
- **Balanced Turn 2 accuracy.** The primary score: mean of
  `current`-class accuracy and `prior`-class accuracy under `baseline`.
- **Self-preference bias.** A model's tendency to rate its own family
  more favorably. Mitigated by cross-family judging.
- **Repair rate.** Fraction of Turn 2 failures where the model
  recovers after the Turn 3 correction. Measures how costly a miss is
  to the user.

---

Built by Nate Dryer. Released under the MIT License. Code and
scenarios at github.com/n-dryer/wearable-assistant-context-bench.
For citation, see CITATION.cff.

For readers: [Glossary](#glossary) · [One-page card (PDF)](docs/wearable_assistant_context_card.pdf) · [GitHub repo](https://github.com/n-dryer/wearable-assistant-context-bench)

For implementers: [Spec](docs/benchmark_spec.md) · [Notes](docs/benchmark_notes.md) · [Schema](docs/schema.md) · [Authoring rules](docs/scenario_authoring_rules.md)
