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

Auxiliary classes are reported because `clarify` and `abstain` failures
have different product implications than `current`/`prior` failures.
A model that hallucinates rather than abstaining is a different
problem than a model that picks the wrong frame.

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

## Camera channel ablation

The camera channel is what carries the scene description into the
model's context. The benchmark asserts that this channel does real
work: without it, the model should not be able to track context
shifts, because the only signal that something changed is the
difference between the Turn 1 scene description and the Turn 2 scene
description.

The v1 release ships an ablation that tests this assertion. Two runs
were executed with the same Gemini Flash Lite candidate and the same
GPT-4o-mini cross-family judge. The only variable was the camera
channel itself, controlled by the `--no-camera` flag on the runner.

| Run | Camera channel | Primary score (`baseline`) | `current` accuracy | `prior` accuracy |
|-----|----------------|----------------------------|---------------------|-------------------|
| Run A | on | 92.8% | 93.9% | 91.7% |
| Run C | off (`--no-camera`) | 7.2% | 6.1% | 8.3% |
| **Delta** | | **85.6 pp** | **87.8 pp** | **83.4 pp** |

Without the camera channel, the same model collapses from 92.8%
balanced accuracy to 7.2%, a drop of 85.6 percentage points. The
camera channel is doing essentially all the work in this benchmark.
The deictic user speech alone is not enough for the model to track
context shifts.

One interesting condition-sensitivity finding: under `condition_b`
(the pre-answer scaffold that asks the model to identify the
relevant context before answering), the no-camera score recovers to
65.5%. The scaffold compensates partially for missing visual context
by forcing explicit context selection in text. Even so, the model
without camera input cannot recover its with-camera performance.

The ablation methodology is reproducible. The `--no-camera` flag in
the runner strips every `[Camera: ...]` block from user messages and
skips injecting `context_image`. The candidate sees only the user's
spoken text. The same flag can be used for any future candidate
model.

## Variance and reproducibility

Each (scenario, condition) cell is run with `--trials 2`. The judge
prompt and scenario file are content-hashed in the run manifest so two
runs with the same hashes evaluate identical content.

Formal variance estimation across multi-seed reruns is not yet
measured. As a rough guide on this 50-scenario bank, treat score
deltas under approximately 3 percentage points with caution until
variance is bounded. Multi-seed variance estimation is acknowledged
as future work.

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

## Known v1 limitations and future work

These are real limitations of the v1 release that affect how the
results should be interpreted. They are not "out of scope". The
benchmark could measure them but does not yet. Future versions are
expected to address them.

- **Repair-line style is named, not deictic.** The Turn 3 repair line
  explicitly names both the right and the wrong objects (for example,
  *"I mean the soldering iron I just picked up, not the multimeter
  probe"*). This measures floor recoverability. Given a maximally
  specific user correction, can the model recover? It is not a model
  of realistic user correction behavior, where users typically start
  with deictic emphasis (*"no, this, what I'm holding now"*) and only
  escalate to explicit naming after the deictic attempt fails. Future
  versions may add deictic-only repair lines for visible-referent
  scenarios to better isolate camera channel attentiveness from
  word-matching recovery.
- **Real video is approximated by scene descriptions in text.** The
  camera channel uses scene descriptions ("Hand wrapped around a
  long wooden handle. Heavy metal head at the top...") as a proxy
  for what a real wearable's vision system would produce from a
  camera frame. Performance on text scene descriptions is not a
  guarantee of performance on actual video. Validation against held
  out video footage is acknowledged as future work.
- **Inter-annotator agreement is not measured.** Inter-annotator
  agreement is when two or more people independently label the same
  item and you measure how often they agree. It's the standard way to
  confirm that labels reflect shared understanding rather than one
  person's opinion. All 50 scenarios were written and reviewed by
  one person, against a written checklist of authoring rules.
  Multi-rater validation is acknowledged as future work.
- **The v1 baseline run uses same-family judging.** The committed
  baseline at `benchmark/v1/runs/baseline/` runs Gemini as both the
  candidate model and the judge. Same-family judging can introduce
  self-preference bias, where a model rates outputs from its own
  family more favorably than outputs from other families. A
  cross-family judge run (for example, Gemini candidate with a Claude
  judge) is the recommended next baseline and is acknowledged as
  future work.
- **The v1 baseline tests only one candidate model.** The benchmark's
  stated purpose is model selection. With only one candidate run, no
  comparative claim can be made yet. Multi-model comparison across
  several candidates is acknowledged as future work.
- **Camera-channel ablation has not been performed.** The benchmark
  asserts that the camera channel matters, but the design has not
  been tested by running the same scenarios with the camera blocks
  stripped to quantify how much the channel contributes to the
  primary score. A controlled ablation comparing with-camera vs.
  without-camera runs is acknowledged as future work.
- **No formal variance estimation.** Each cell runs with
  `--trials 2`. Multi-seed reruns to formally bound score noise have
  not been performed. As a rough guide, treat score deltas under
  approximately 3 percentage points on this 50-scenario bank with
  caution until variance is measured.
- **The benchmark does not exercise the full omnimodal stack a
  wearable requires, but candidates should still meet that bar.** A
  deployable wearable assistant needs live audio input, voice-mode
  output, real-time streaming, and interruption handling. This
  benchmark uses text proxies for both vision and audio, and only
  scores text outputs, so the test mechanics only require a candidate
  with vision support. Candidate selection should still require the
  full deployable stack (vision in, audio in, audio out, real-time)
  because the goal is model selection for a real wearable. Picking a
  candidate that can't physically run in production is wasted work,
  even if the benchmark mechanics would let it through. As of April
  2026, Google (Gemini Live) and OpenAI (Realtime API) families meet
  this bar; Anthropic Claude does not yet have native audio output.
  A future benchmark version that exercises live audio and streaming
  directly is acknowledged as future work.

## When to use this benchmark vs. when to do separate evaluation

Use this benchmark when:

- You are choosing between candidate models for a wearable or
  multimodal assistant product
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
- **Shift type.** Project-specific label for the kind of context
  change between Turn 1 and Turn 2. The benchmark covers eight:
  object swap, object state change, sequential task step, location,
  attention shift, absent referent, screen content, and
  pre-conversation recall. Stored in the data files as `cue_type`.
  Not a standardized ML benchmark term; closest standard alternative
  would be "scenario category."
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
