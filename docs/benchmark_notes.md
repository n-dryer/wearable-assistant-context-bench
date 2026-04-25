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

- **`current` accuracy** — fraction of `target_context = current`
  scenarios where the judge labeled the response `current`. A model
  with high `current` accuracy responds well when the question is
  about what's in the camera right now.
- **`prior` accuracy** — fraction of `target_context = prior`
  scenarios where the judge labeled the response `prior`. A model with
  high `prior` accuracy correctly answers about an earlier state when
  the user asks about it.
- **`clarify` accuracy** — fraction of `target_context = clarify`
  scenarios where the judge labeled the response `clarify`. Auxiliary;
  not in the primary score.
- **`abstain` accuracy** — fraction of `target_context = abstain`
  scenarios where the judge labeled the response `abstain`. Auxiliary;
  not in the primary score.

Auxiliary classes are reported because `clarify` and `abstain` failures
have different product implications than `current`/`prior` failures —
a model that hallucinates rather than abstaining is a different
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
and is over-anchoring on T1 even when T2 is the right frame.

A balanced model handles both. The headline score is balanced for
exactly this reason — to reward models that handle both, not just one.

## Condition sensitivity

`baseline`, `condition_a`, and `condition_b` use different system
prompts:

- `baseline` — minimal system prompt. The model is told it is helping
  a user with an ongoing project, nothing more.
- `condition_a` — direct policy-selection instruction. Tells the model
  the visual context may shift between turns and asks it to decide
  which frame each question refers to before answering.
- `condition_b` — pre-answer scaffold. Requires the model to identify
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

## Simulated repair rate

When the candidate misses on Turn 2, the runner appends Turn 3 — a
repair anchor that names the intended frame explicitly (`"I mean the
hammer I'm holding now, not the screwdriver from before"`). The judge
labels the T3 response, and the simulated repair rate is the fraction
of T2 misses that pass on T3.

This number stands in for the cost of user correction. A high repair
rate means the model recovers gracefully when the user clarifies. A
low repair rate means even an explicit repair does not get the model
back on track.

What it does not measure: real user behavior, real correction
patterns, or the linguistic variety of how users actually repair
context misses. The repair anchor is templated and explicit. It tells
you whether the model can be corrected, not whether real users would
phrase their corrections that way.

## Limitations

The benchmark is narrow on purpose. It tests one specific failure
mode — context tracking under situational change — and nothing else.
Specifically, it does not measure:

- **Advice quality.** The judge does not check whether the response
  is correct, safe, or domain-appropriate. A confidently wrong answer
  can pass if it picks the right context. A perfectly safe answer can
  fail if it picks the wrong one.
- **Multi-turn dynamics.** The conversation is 3 turns. Long
  conversations, branching dialogue, or extended back-and-forth are
  out of scope.
- **Real video.** The camera channel uses perceptual text descriptions
  as a proxy. A real wearable processes video frames; this benchmark
  does not. Performance on perceptual text proxies is not a guarantee
  of performance on actual video.
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

- `turn` — one user message plus the assistant's response.
- `context shift` — a meaningful change between T1 and T2 in what the
  user is showing, holding, doing, or referring to.
- `current` — judge label for responses grounded in the current (T2)
  context.
- `prior` — judge label for responses grounded in the earlier (T1 or
  `context_image`) context.
- `clarify` — judge label for responses that ask the user to
  disambiguate.
- `abstain` — judge label for responses that decline or claim the
  model cannot answer.
- `prompt conditions` — the three prompt setups used:
  `baseline`, `condition_a`, `condition_b`.
- `default comparison condition` — the condition used for the headline
  number. Always `baseline`.
- `balanced accuracy` — the mean of per-class accuracy across the two
  scored classes (`current` and `prior`).
- `simulated repair rate` — the fraction of Turn 2 misses that pass
  on Turn 3 after the repair anchor.
