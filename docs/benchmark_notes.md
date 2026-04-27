# Benchmark Notes

This document covers how to read benchmark results, what the numbers
mean, and what the benchmark does not tell you. For the benchmark
contract, see [`benchmark_spec.md`](benchmark_spec.md).

## How to read the primary score

The primary score is **balanced accuracy across `current` and `prior`
on Turn 2 under the `baseline` prompt condition**.

The headline number is the average of two per-class accuracies:

```text
primary_score = mean(
    current_accuracy,    # correct labels among target_context = current scenarios
    prior_accuracy,      # correct labels among target_context = prior scenarios
)
```

This is the right number to compare two candidate models on the same
benchmark release. Score deltas between models on the same release
matter more than absolute values. Read the absolute number as a rough
indicator; read the delta as the actual signal.

`condition_a` and `condition_b` produce their own balanced accuracy
numbers but should not replace `baseline` as the ranking reference.
They tell you something about prompt sensitivity, not raw context
tracking.

## Per-class accuracy

The findings output reports accuracy per scored class, not just the
balanced mean. Read each one separately:

- **`current` accuracy.** Fraction of `target_context = current`
  scenarios where the judge labeled the response `current`. A model
  with high `current` accuracy responds well when the question is
  about what's in the camera right now.
- **`prior` accuracy.** Fraction of `target_context = prior`
  scenarios where the judge labeled the response `prior`. A model with
  high `prior` accuracy correctly answers about an earlier state when
  the user asks about it.
- **`clarify` accuracy.** Fraction of `target_context = clarify`
  scenarios where the judge labeled the response `clarify`. Auxiliary;
  not in the primary score.
- **`abstain` accuracy.** Fraction of `target_context = abstain`
  scenarios where the judge labeled the response `abstain`. Auxiliary;
  not in the primary score.

Auxiliary diagnostics report `clarify` and `abstain` accuracy
separately from the headline score because those failures reveal
different capability gaps than `current`/`prior` misses. A model
that hallucinates rather than abstaining is a different problem
than a model that picks the wrong frame.

The bank is dominated by `current` (33 scenarios) and `prior` (12).
With only 3 `clarify` and 2 `abstain` scenarios, those per-class
numbers are too noisy to be ranking-grade on their own.

## Strong on current, weak on prior (and vice versa)

A model that scores well on `current` but badly on `prior` defaults
to whatever it sees most recently. That is the most common failure
mode of a non-context-aware assistant: it responds to whatever frame
is in front of it, ignoring the user's reference to an earlier state.

A model that scores well on `prior` but badly on `current` is unusual.
Most often this means the model is confused about what to attend to
and is over-anchoring on Turn 1 even when Turn 2 is the right frame.

A balanced model handles both. The headline score is balanced for
exactly this reason: to reward models that handle both, not just one.

## Condition sensitivity

`baseline`, `condition_a`, and `condition_b` use different system
prompts:

- `baseline`. Minimal system prompt. The model is told it is helping
  a user with an ongoing project, nothing more.
- `condition_a`. Direct policy-selection instruction. Tells the model
  the visual context may shift between turns and asks it to decide
  which frame each question refers to before answering.
- `condition_b`. Pre-answer scaffold. Requires the model to identify
  the relevant context (`current` or `prior`) on the first line of its
  response, then answer.

Reading the deltas between conditions tells you about prompt
sensitivity:

- A model that improves a lot from `baseline` to `condition_a`
  responds well to explicit direction. It is capable of context
  tracking when reminded.
- A model that improves further from `condition_a` to `condition_b`
  benefits from forced structure. The scaffold is doing real work.
- A model that does not improve much across conditions either already
  handles context tracking on its own, or its underlying weakness is
  not addressable by prompting.

`condition_a` and `condition_b` are diagnostics, not headline scores.

## Repair rate

**Repair rate.** When the model gets Turn 2 wrong, the user can
clarify with a follow-up like "I mean the hammer I'm holding now, not
the one from before." The repair rate is how often the model fixes
its answer after this kind of correction. It measures how recoverable
a Turn 2 miss is.

In the runner, when the candidate misses on Turn 2, the runner appends
Turn 3, a repair anchor that names the intended frame explicitly
(`"I mean the hammer I'm holding now, not the screwdriver from
before"`). The judge labels the Turn 3 response, and the repair rate
is the fraction of Turn 2 misses that pass on Turn 3.

This number stands in for the cost of user correction. A high repair
rate means the model recovers gracefully when the user clarifies. A
low repair rate means even an explicit repair does not get the model
back on track.

What it does not measure: real user behavior, real correction
patterns, or the linguistic variety of how users actually repair
context misses. The repair anchor is templated and explicit. It tells
you whether the model can be corrected, not whether real users would
phrase their corrections that way.

## Video ablation

The video channel is what carries the scene description into the
model's context. The benchmark asserts that this channel does real
work: without it, the model should not be able to track context
shifts, because the only signal that something changed is the
difference between the Turn 1 scene description and the Turn 2 scene
description.

The v1 release ships an ablation that tests this assertion. Two runs
were executed with the same Gemini Flash Lite candidate and the same
GPT-4o-mini cross-family judge. The only variable was the video
channel itself, controlled by the `--no-camera` flag on the runner
(the flag name is preserved for backward compatibility with the
runner CLI).

| Run | Video | Primary score (`baseline`) | `current` accuracy | `prior` accuracy |
|-----|-------|----------------------------|---------------------|-------------------|
| `baseline` | shown | 60.6% | 87.9% | 33.3% |
| `ablation-no-camera` | hidden (`--no-camera`) | 14.4% | 12.1% | 16.7% |
| **Delta** | | **46.2 pp** | **75.8 pp** | **16.6 pp** |

What the ablation shows: take the camera description away and the
model can't get the answers from the user's words alone. That rules
out one alternative reading of the headline numbers, namely that the
model is solving the task through question-phrasing patterns or
memorized priors. It can't.

What the ablation does not show on its own: that the model is doing
"context tracking" in a deep sense. A simpler reading consistent
with the same data is that the model grounds in whatever the camera
most recently described, without any explicit notion of "this is
the current context vs. the prior context." The per-class breakdown
fills that in: the `current` class is where the model looks strong
(87.9%); the `prior` class is where it falls apart (33.3%). The
combined picture (reliance on camera input, high `current` accuracy,
low `prior` accuracy) reveals the capability gap the benchmark
targets.

The ablation methodology is reproducible. The `--no-camera` flag in
the runner strips every `[Camera: ...]` block from user messages and
skips injecting `context_image`. The candidate sees only the user's
text-transcript speech. The same flag can be used for any future
candidate model.

## Variance and reproducibility

Each (scenario, condition) cell is run with `--trials 5`. Findings
report 95% confidence intervals (Wilson) on every score so deltas
can be interpreted against sampling noise rather than a hand-waved
"3 pp guard band."

The judge prompt template, the scenario bank, the answer keys, and
the prompt conditions are all content-hashed in two places:

- Per-run, in `findings.md`'s reproducibility manifest, alongside the
  runner's git commit. Two runs with matching manifest hashes
  evaluate identical content.
- At the repo level, in `benchmark/v1/MANIFEST.lock.json`, checked
  by `scripts/validate_scenarios.py` so silent mutations between
  releases fail CI.

Beyond-5-trial multi-seed generalization studies remain a v2
follow-up.

## What this benchmark does not measure

The benchmark is narrow on purpose. It tests one specific failure
mode (context tracking under situational change) and nothing else.
The following are out of scope by design:

- **Advice quality.** The judge does not check whether the response
  is correct, safe, or domain-appropriate. A confidently wrong answer
  can pass if it picks the right context. A perfectly safe answer can
  fail if it picks the wrong one.
- **Multi-turn dynamics.** The conversation is 3 turns. Long
  conversations, branching dialogue, or extended back-and-forth are
  out of scope.
- **Proactive coaching.** The benchmark only scores responses to
  direct questions. A model that should have flagged a problem
  proactively but didn't is not penalized.
- **Domain knowledge depth.** Scenarios span 16 activity domains
  (kitchen, workshop, garden, etc.). Coverage is broad but shallow.
  Specialized expertise in any one domain is not measured.
- **Latency, cost, audio perception, speaker attribution, addressee
  detection, long-horizon memory.** All out of scope.

Score deltas between models on the same release matter more than
absolute values. The number itself is meaningful only relative to
other runs on the same scenario bank with the same judge prompt
version.

## What v1 ships

v1 publishes five runs across two scenario packs (50 canonical + 20
adversarial). Each `findings.md` carries its full reproducibility
manifest; the table below is the headline only.

| Run | Candidate | Judge | Pack | Primary (95% CI) |
|---|---|---|---|---|
| `baseline` | `gemini-2.5-flash-lite` | `gemini-2.5-flash-lite` | canonical 50 | 60.6% (54.1–67.1) |
| `baseline-alt` | `gemini-2.5-flash` | `gemini-2.5-flash-lite` | canonical 50 | 77.7% (71.3–84.0) |
| `ablation-no-camera` | `gemini-2.5-flash-lite`, `--no-camera` | `gemini-2.5-flash-lite` | canonical 50 | 14.4% (9.1–19.7) |
| `baseline-qwen-cross-family` | `dashscope-intl/qwen3-vl-plus` | `gemini-2.5-flash-lite` | canonical 50 | 54.2% (50.7–57.7) |
| `adversarial` | `openrouter/google/gemini-2.5-flash-lite` | `openrouter/openai/gpt-4o-mini` (+ ranking judge `claude-haiku-4.5`) | adversarial 20 | 67.3% (55.5–79.1) |

### Methodology features in v1

- **Cross-family judging.** Two of five runs ship cross-family
  (judge family different from candidate family):
  `baseline-qwen-cross-family` and `adversarial`. The three Gemini
  canonical runs are same-family; see Caveats below.
- **Cross-LLM judge agreement.** Cohen's kappa across two
  cross-family judges is reported on the `adversarial` run
  (kappa = 0.443 across `gpt-4o-mini` and `claude-haiku-4.5`,
  observed agreement 63.3%, 110/300 trials in disagreement). The
  canonical runs use a single judge each; their findings render the
  inter-judge section as a placeholder pointing at this v1.0.x
  follow-up.
- **Adversarial subset.** 20 distractor-rich scenarios separately
  tagged from the canonical 50; each passes the same 10-point
  checklist + programmatic validator checks.
- **Deictic and named repair lines.** Visible-referent canonical
  scenarios ship two Turn 3 repair anchors: the named anchor (`"I
  mean the soldering iron I just picked up, not the multimeter
  probe"`) measuring floor recoverability, and a deictic anchor
  (`"no, this, what I'm holding now"`) measuring realistic recovery.
  The named repair is what the five published runs use; an explicit
  `--repair-style deictic` ablation across the bank is a v1.0.x
  follow-up.
- **Variance reporting.** `--trials 5` per cell with 95% Wilson CIs
  per class and 95% normal-approximation CIs on the balanced mean.
- **Frozen scenario bank with static lockfile.** SHA256 hashes of
  `scenarios.json`, `expected_answers.json`, `interventions.json`,
  the adversarial bank, and the judge-prompt template are committed
  to `benchmark/v1/MANIFEST.lock.json`; CI fails on drift without a
  coordinated `BENCHMARK_VERSION` bump.
- **Optional fixed ranking judge for cross-candidate comparison**
  (CLI: `--ranking-judge-family`). When set, every trial is also
  labeled by the fixed second judge. Demonstrated on the
  `adversarial` run with `claude-haiku-4.5` as the ranking judge
  alongside the auto-resolved cross-family judge.
- **Robust transient-error retry** in the LiteLLM transport
  (`core.litellm_adapter._call_with_retry`). Gemini 503/UNAVAILABLE,
  rate-limit, and timeout-style messages retry with exponential
  backoff (4 attempts, base 2s). Across the five published runs the
  retry wrapper absorbed 16 transient errors.

### What the runs show

- **The model is leaning heavily on the camera input.** Same
  candidate and judge, only the camera description toggled:
  `baseline` 60.6% → `ablation-no-camera` 14.4%. A 46.2 percentage
  point gap. This eliminates one alternative hypothesis: the
  model uses question-phrasing patterns instead of visual
  grounding. It does not on its own prove deeper context tracking
  (see Video ablation above for the longer treatment).
- **The model handles "current" but stumbles on "prior".**
  `baseline-qwen-cross-family` is the clearest example: 100% on
  `current`, 8.3% on `prior`. The model grounds in the latest
  visual input and struggles to refer back. Together with the
  camera ablation, this is the capability gap the benchmark
  targets.
- **Bigger Gemini sibling helps** within the family:
  `baseline` (Flash-Lite) 60.6% → `baseline-alt` (Flash) 77.7%.
- **Cross-family vs same-family on the canonical bank.**
  `baseline-qwen-cross-family` (cross-family) 54.2% vs `baseline`
  (same-family Gemini-on-Gemini) 60.6%, a 6.4 pp gap consistent
  with self-preference bias in the same-family numbers, though
  candidate quality also differs between the two runs.
- **Deictic vs named repair.** `baseline-deictic-repair` uses the
  deictic anchor (`"no, this, what I'm holding now"`) on the 31
  visible-referent `current`-target scenarios and falls back to the
  named anchor on the rest. Repair recovery: deictic 50/50 (100%),
  named-fallback 30/100 (30%). Compared to `baseline` (named only,
  80/150 = 53.3% overall), the deictic ablation has the same overall
  recovery rate but concentrates the recoveries on scenarios where a
  pointing gesture can resolve the reference. On `prior`, `clarify`,
  and `abstain`-target scenarios, where deixis cannot point at the
  intended referent, verbal clarification rarely recovers the miss.

### Caveats

- **Same-family judging on three of four canonical runs.** API
  budget across providers (OpenRouter, OpenAI direct, HF Inference
  Providers Pro) was exhausted mid-effort, leaving Gemini-direct
  via LiteLLM as the only viable transport for the bulk of the
  canonical runs. Gemini-Flash-Lite judges Gemini-Flash-Lite (and
  Gemini-Flash) on those three runs, which admits self-preference
  bias. The `baseline-qwen-cross-family` run is the cross-family
  integrity reference for the canonical bank.
- **Two model-config families across v1.** The four canonical runs
  use Gemini-direct + DashScope-International transports. The
  `adversarial` run uses an OpenRouter setup with a Claude-Haiku
  ranking judge. Each `findings.md` manifest names the candidate
  and judge identifiers; comparing within a single run is fully
  apples-to-apples.
- **`baseline-qwen-cross-family` cannot yet be ranked head-to-head
  against the Gemini canonical runs.** Cross-candidate ranking
  requires a fixed ranking judge held constant across candidates;
  v1 demonstrates that mechanism on the adversarial run only.
  Re-running the canonical bank with a fixed ranking judge across
  all candidates is a v1.0.x follow-up.

## Open limitations (v2 follow-ups)

Real limitations that affect how the v1 results should be
interpreted. These are not "out of scope"; they are work the
benchmark could do but does not yet.

- **Human inter-annotator agreement is not measured.** v1 reports
  cross-LLM judge agreement (Cohen's kappa across two cross-family
  judges) as a substitute. A second human rater labeling 25% of
  judge outputs, with kappa reported, remains the strongest
  defensibility move and is the highest-priority v2 follow-up.
- **Real video is approximated by scene descriptions in text.** The
  camera channel uses scene descriptions ("Hand wrapped around a
  long wooden handle. Heavy metal head at the top...") as a proxy
  for what a real wearable's vision system would produce from a
  camera frame. Performance on text scene descriptions is not a
  guarantee of performance on actual video. Validation against
  held-out video footage on a representative sample is acknowledged
  as v2 work.
- **The audio channel is text, not raw acoustic.** v1 represents
  the user's spoken turns as text transcripts, not raw audio. The
  benchmark therefore does not test acoustic grounding, speaker
  attribution, addressee detection, or ambient audio cues. A v2
  variant with raw audio input remains future work.
- **Beyond-5-trial generalization is not measured.** Each cell runs
  with `--trials 5` and CIs are reported. Multi-seed runs at higher
  trial counts to characterize the long-tail noise floor remain a
  v2 follow-up.
- **The benchmark does not exercise the full omnimodal stack the
  product requires, but candidates should still meet that bar.** A
  deployable in-the-moment multimodal coach (wearable or handheld)
  needs live audio input, voice-mode output, real-time streaming,
  and interruption handling. This benchmark uses text proxies for
  both vision and audio, and only scores text outputs, so the test
  mechanics only require a candidate with vision support. Candidate
  selection should still require the full deployable stack (vision
  in, audio in, audio out, real-time) because the goal is model
  selection for a live coaching product. Picking a candidate that
  can't physically run in production is wasted work, even if the
  benchmark mechanics would let it through. As of April 2026, Google
  (Gemini Live) and OpenAI (Realtime API) families meet this bar;
  Anthropic Claude does not yet have native audio output. A v2
  benchmark variant that exercises live audio and streaming directly
  is acknowledged as future work.

## When to use this benchmark vs. when to do separate evaluation

Use this benchmark to:

- Compare candidate models on context tracking for deployed wearable
  or multimodal assistants
- You need to verify that a new model release has not regressed on
  context tracking
- You want comparable numbers across models on the same scenario set

Run separate evaluation for:

- Domain advice quality (cooking, fitness, music, etc.)
- Real-video performance (run a vision benchmark or your own video
  evaluation)
- Long-horizon memory across sessions
- Latency and cost characteristics in your serving environment
- User-facing UX quality
- Audio perception, speaker attribution, addressee detection

A model selected with this benchmark still needs to clear those bars
in the evaluation pipeline that fits your product.

## Glossary

- **Reference resolution.** Figuring out what a word like "this",
  "that", "it", or "earlier" is pointing to. The same word can mean
  different things across a conversation, so the model has to work
  out which thing the user means. Standard term in dialog systems
  and computational linguistics.
- **Context tracking.** The plain-language name for the task this
  benchmark measures. The technical name is reference resolution
  under cross-turn context shift. Both names point at the same task:
  given that the user's situation changed between turns, did the
  model respond about the new situation or stay anchored to the old
  one. Used by MultiChallenge and other multi-turn benchmarks.
- **Deictic.** A word or phrase whose meaning depends on context: "this", "that", "it", "here", "now", "earlier". Deictic references point at something rather than naming it. The benchmark's user speech is intentionally deictic so the model has to use the camera channel and conversation history to figure out what the user means.
- **Turn.** One user message plus the assistant's response. Each
  scenario has up to three turns: Turn 1 (initial question), Turn 2
  (follow-up after the situation has changed), and an optional Turn 3
  (a clarifying repair line, fired only when the model gets Turn 2
  wrong).
- **Shift type** (stored as `cue_type`). Scenario category describing
  the shape of the context shift between Turn 1 and Turn 2. The 8
  values (`object_in_hand`, `object_state`, `sequential_task`,
  `location`, `object_in_view`, `absent_referent`, `screen_content`,
  `pre_conversation_recall`) are listed in
  [`benchmark_spec.md`](benchmark_spec.md#the-8-shift-type-categories).
  Closest standard term is "condition type" or "scenario category."
- **Context shift.** A meaningful change between Turn 1 and Turn 2
  in what the user is showing, holding, doing, or referring to.
  Examples: putting down a hammer and picking up a screwdriver,
  walking from the bedroom to the kitchen, finishing one step of a
  task and starting the next.
- **`current`.** Judge label for a response that uses the current
  Turn 2 context. This means the response is about what the camera
  sees right now.
- **`prior`.** Judge label for a response that uses an earlier
  context: the Turn 1 frame, or the `context_image` (pre-conversation
  state) for recall scenarios. This means the response is about what
  the camera saw earlier, not what it sees now.
- **`clarify`.** Judge label for a response that asks the user to
  clear up an ambiguity rather than guessing.
- **`abstain`.** Judge label for a response that declines to answer
  or says it cannot tell.
- **Prompt conditions.** The three prompt setups used: `baseline`,
  `condition_a`, `condition_b`.
- **Default comparison condition.** The condition used for the
  headline number. Always `baseline`.
- **Balanced accuracy.** The average of the per-class scores. In
  this benchmark, that means the average of `current` accuracy and
  `prior` accuracy. We use the average instead of the overall hit
  rate so the larger class (`current`) cannot dominate the headline
  number. A model that gets every `current` scenario right but
  misses every `prior` scenario would score 50%, not 73%.
- **Repair.** A conversational repair is a follow-up message that
  fixes a misunderstanding. The benchmark fires a Turn 3 repair when
  the model gets Turn 2 wrong; the model gets one chance to recover.
- **Repair rate.** Fraction of Turn 2 misses where the model gives
  the right answer after the Turn 3 repair line. Descriptive metric
  name; not a fixed term across benchmarks. Adjacent terms in the
  literature: "recovery rate," "correction success rate."
- **Repair line style.** How the user phrases the Turn 3 correction when the model misses Turn 2. Two main styles exist. Named: "I mean the soldering iron I just picked up, not the multimeter probe" (current v1 style). Deictic: "no, this, what I'm holding now". The v1 benchmark uses named repairs, which measures floor recoverability rather than realistic user behavior. See "Known v1 limitations and future work" for context.
- **Model family.** A group of related models from the same provider
  (and usually the same training pipeline). Examples: Claude Sonnet
  4.6 and Claude Opus 4.7 are in the Claude family. Gemini 2.5 Flash
  and Gemini 3 Pro are in the Gemini family. GPT-5.5 is in the
  OpenAI family.
- **Cross-family judging.** Using a judge from a different model
  family than the candidate being scored. For example, Claude judging
  a Gemini candidate. The default in this benchmark, because it
  reduces self-preference bias.
- **Self-preference bias.** The tendency of a model used as a judge
  to rate outputs from its own model family more favorably than
  outputs from other families. Established term in LLM-as-judge
  literature (JudgeBench, MT-Bench). Mitigated by cross-family
  judging.
- **Inter-annotator agreement (IAA).** When two or more people
  independently label the same item and you measure how often they
  agree. Standard practice in ML datasets to confirm labels reflect
  shared understanding rather than one person's opinion. Common
  metrics: Cohen's kappa (two raters), Fleiss' kappa (three or more),
  or simple percent agreement.
- **Scene description.** What a vision system would say about a
  camera frame: shape, material, color, motion, position. In this
  benchmark, scene descriptions follow an authoring rule: they
  describe physical features without naming the object directly. The
  model has to identify what's in frame from those features.
- **Proactive coaching.** When the assistant flags a problem or
  offers advice without being directly asked. Example: noticing that
  the user is reaching toward a hot pan and prompting them before
  they touch it. This benchmark only scores responses to direct user
  questions; proactive behavior is out of scope.
- **Ablation.** A controlled experiment that tests how much a
  specific feature or input contributes to a model's performance, by
  running the same evaluation with that feature removed and comparing
  scores. A "camera channel ablation" would compare runs with versus
  without the `[Camera: ...]` blocks to quantify how much the camera
  channel actually contributes to the score.
- **Hallucination.** When a model produces an answer that sounds
  confident but is not supported by the evidence available to it. In
  a context-tracking benchmark, hallucinating a description of an
  object that isn't actually in frame is a failure even if the wording
  is fluent.
- **Macro average.** The mean of per-class scores, weighting each
  class equally. Different from "micro average," which weights each
  example equally and lets large classes dominate. The primary score
  in this benchmark uses macro average across `current` and `prior`
  so neither class can dominate the headline number.
- **Scaffold (pre-answer scaffold).** A prompt structure that
  requires the model to produce intermediate reasoning before its
  final answer. The `condition_b` prompt asks the model to identify
  the relevant context (`current` or `prior`) on the first line of
  its response, then answer. The scaffold structures the reasoning
  step.
- **Speaker attribution.** Identifying which person spoke a given
  utterance when multiple people are present. Distinguishing the
  wearable's user from a coworker or family member in the same room.
  Out of scope for this benchmark.
- **Addressee detection.** Telling whether the user is talking to the
  assistant, to another person, or to themselves. A wearable that
  streams audio constantly needs to know when a question is for it.
  Out of scope for this benchmark.
- **Audio perception.** Understanding spoken-language input directly
  from raw audio (rather than from a text transcript). Includes
  accent handling, ambient noise robustness, prosody, and tone. Out
  of scope for this benchmark.
- **Long-horizon memory.** Memory that persists across multiple
  conversations or sessions, not just within a single conversation.
  A wearable might remember last week's project state when the user
  picks it back up; this benchmark does not test that.

## Acronyms and project terminology

Quick reference for the abbreviated forms used throughout these docs:

- **LLM judge.** A large language model used to label model outputs.
  Distinct from a human judge or annotator (see "Inter-annotator
  agreement").
- **Macro average.** The mean of per-class scores, weighting each
  class equally. The primary score uses macro-averaged accuracy
  across `current` and `prior`.
- **Balanced accuracy.** In this benchmark, the macro-average of
  `current` and `prior` accuracy.
- **Auxiliary diagnostic.** A metric reported alongside the primary
  score but not folded into it (e.g., `clarify` and `abstain` class
  accuracy).
- **CI.** Confidence interval. The benchmark reports 95% Wilson CIs
  per class and 95% normal-approximation CIs on the balanced mean.
- **IAA.** Inter-annotator agreement (the standard measure of label
  reliability across human annotators). v1 reports cross-LLM
  agreement as an automated substitute; human IAA is v2 work.
- **Turn 1 / Turn 2 / Turn 3.** The three conversation turns. Turn 1
  establishes initial context; Turn 2 fires after the context shift
  and is the scored turn; Turn 3 fires only when Turn 2 misses, as
  a repair attempt.
- **pp.** Percentage points (used for score-delta differences, e.g.,
  "a 46.2 pp drop").
- **Cross-family judge.** A judge whose model family differs from
  the candidate's, used to reduce self-preference bias within a run.
- **Fixed ranking judge.** A single judge held constant across runs,
  used to compare candidates apples-to-apples.
