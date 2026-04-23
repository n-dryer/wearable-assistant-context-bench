# Benchmark Notes

This document adds practical context for reading and using the
benchmark. For the benchmark contract and runtime rules, see
[benchmark_spec.md](benchmark_spec.md).

## Background and use context

The Wearable Assistant Context Benchmark is a **product benchmark**. It
was built to help choose the model that best infers what a user is
referring to during live wearable assistant interactions.

The current public v1 benchmark measures **cross-turn reference resolution under context change**.

That means the benchmark focuses on a recurring product problem:

- the user changes rooms, objects, screens, or scene state
- the user asks a follow-up question that is natural but ambiguous
- the assistant answers about the wrong thing unless it updates its
  reference correctly

This framing is narrow on purpose. The benchmark is optimized for
model-selection usefulness on a real product problem, not for being a
research-style omnibus benchmark of everything a multimodal assistant
can do.

## How to read the score

The primary score is for like-for-like comparison on the same benchmark
release. It is most useful when comparing candidate models under the
same prompt condition, with the same trial count, on the same frozen
v1 set.

On this benchmark, score deltas matter more than absolute values.

Balanced accuracy is used because the primary score is based on the two
scored classes, `current` and `prior`, and those classes are not evenly
represented in the public scenario bank. Averaging the two class
accuracies keeps one class from dominating the headline score.

The three prompt conditions serve different roles:

- `baseline` is the default comparison condition.
- `condition_a` checks whether a direct instruction to pick the right
  context changes the result.
- `condition_b` checks whether making the model name its chosen context
  changes the result.

Simulated repair rate is a secondary metric. It stands in for likely
user correction cost after a wrong follow-up answer and is not part of
the ranking.

## Why v1 is intentionally narrow

Canonical v1 does not try to measure every kind of multimodal inference
failure. It focuses on one problem that shows up often in real use and
can be scored consistently enough to support model choice.

That tradeoff is deliberate:

- product usefulness first
- broad benchmark coverage second

This is not a claim that cross-turn reference resolution under context
change is the only important assistant capability. It is a claim that
this is an important enough product problem to deserve its own repeatable
benchmark.

## Transcript-proxy scope

Spoken user questions already count as part of the cue set in this
benchmark, but canonical v1 represents them through transcript proxies
rather than raw audio.

So the benchmark already tests interpretation of spoken user queries,
but it does **not** yet directly test:

- raw acoustic grounding
- speaker attribution
- ambient audio cues

That distinction matters when interpreting results.

## Scenario origins

The scenario bank was built from a mix of:

- real user feedback from wearable assistant use
- direct product testing of wearable and multimodal assistants
- generalized patterns derived from repeated failures
- a smaller number of theoretical coverage cases

The current public release uses one consolidated 101-scenario bank.
The goal was not to maximize scenario count for its own sake. The goal
was to capture the recurring shapes of this product problem in a frozen
set that can support fair candidate comparison.

## Related benchmarks and overlap

This benchmark sits near several adjacent benchmark families:

- multimodal assistant evaluation
- wearable or egocentric multimodal evaluation
- streaming multimodal understanding
- reference-resolution under changing context

Some adjacent public efforts include
[OpenEQA](https://open-eqa.github.io/),
[StreamingBench](https://streamingbench.github.io/),
[WearVQA](https://arxiv.org/abs/2511.22154), and
[TeleEgo](https://arxiv.org/abs/2510.23981).

This benchmark differs from those efforts in a few ways:

- it is narrower
- it is more directly tied to a live assistant product problem
- it is explicitly framed as a model-selection tool
- it uses transcript-proxy scenarios rather than a broader raw
  multimodal evaluation stack

That narrower scope is a feature, not a defect, for the intended use.

## Freeze and versioning

Canonical v1 is frozen so models can be compared on the same release.
Scenario text, expected answers, prompt text, scoring semantics, and
the default comparison condition should stay fixed inside the release.

Documentation clarifications, adapter additions, and implementation
cleanup that do not change benchmark meaning are fine. Changes that
would alter benchmark comparability should be treated as a new release
decision.

## Glossary

- `turn`: one part of the conversation.
- `context change`: a meaningful change in what the user is showing,
  holding, looking at, or referring to between turns.
- `current`: scoring label for answers grounded in the current context.
- `prior`: scoring label for answers grounded in the earlier context.
- `clarify`: scoring label for answers that ask the user to disambiguate.
- `abstain`: scoring label for answers that decline or claim the model
  cannot answer.
- `prompt conditions`: the three prompt setups used in v1:
  `baseline`, `condition_a`, and `condition_b`.
- `default comparison condition`: the condition used for the main model
  comparison. In v1, this is `baseline`.
- `balanced accuracy`: the mean of accuracy on the `current` and
  `prior` scored classes.
- `simulated repair rate`: a secondary metric that stands in for likely
  user correction cost after a wrong answer.
