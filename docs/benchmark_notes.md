# Benchmark Notes

This document adds context for reading and using the benchmark. For the
benchmark definition, scoring rules, and runtime behavior, see
[benchmark_spec.md](benchmark_spec.md).

## Background and use context

This benchmark measures how a wearable multimodal assistant handles
ambiguous user references when the user's context changes between
turns, such as where they are, what they are holding, or what is
around them. It focuses on a recurring interaction problem: the
assistant sometimes makes the wrong inference about what the user is
referring to and answers from the wrong context.

This benchmark was built to support model-selection decisions for a
wearable multimodal assistant. It was built by a product manager for
internal product evaluation and later published so the benchmark design
can be inspected publicly.

Although the benchmark was developed around a wearable multimodal
assistant, it can also apply to related multimodal assistant devices on
or near the user. The README and benchmark spec define the supported
device requirements in more detail.

v1 is intentionally narrow. It measures one specific judgment call:
after the user's context changes, does the answer follow the earlier
context or the current one?

## How to read the score

The primary score is for like-for-like comparison on the same benchmark
release. It is most useful when comparing candidate models under the
same condition, with the same trial count, on the same frozen v1 set.

On this benchmark, score deltas matter more than absolute values. The
benchmark is narrow on purpose, so a higher score means a model handled
this specific context-selection task better, not that it is better
overall.

Balanced accuracy is used because v1 has more `current` scenarios than
`prior` scenarios. Averaging the two class accuracies keeps the larger
class from dominating the score.

The three prompt conditions serve different roles:

- `baseline` is the default ranking condition.
- `condition_a` checks whether a direct instruction to pick the right
  context changes the result.
- `condition_b` checks whether making the model name the context it is
  using changes the result.

Simulated repair rate is a secondary metric. It stands in for likely
user correction cost after a wrong follow-up answer and is not part of
the ranking.

## Limitations and caveats

- v1 measures one narrow interaction problem, not full assistant
  quality.
- v1 does not measure full product quality. Latency, reliability, UX,
  speech recognition, and many other product factors are out of scope.
- The benchmark focuses on context inference after a context change. It
  is not a general multimodal benchmark.
- Image fields are currently unset, so the public v1 release is still a
  text-proxy benchmark.
- Prompt sensitivity still matters. That is why `condition_a` and
  `condition_b` remain visible as extra checks.
- The benchmark is best used for model comparison on the same release.
  It should not be used to make broad claims about assistant capability
  outside this task.
- LLM-as-judge brings practical advantages for scale and consistency,
  but it is still a modeling choice with its own limits.

## Where the scenarios came from

The current scenario set was built from a mix of pilot user feedback,
direct hands-on testing of real multimodal assistants and wearables,
generalized cases based on repeated patterns, and a smaller number of
conceptual cases. The source materials reviewed for this benchmark
included pilot feedback exports, pilot reports, app feedback reports,
and pilot chat archives, along with direct product testing outside the
pilot.

In the current public v1 set, most scenarios are either directly based
on pilot user feedback or generalized from repeated pilot patterns. One
scenario is a conceptual coverage case added to cover an important
current-context shape not directly represented in a single pilot
example.

| Scenario | Expected context | Built from | Source | Notes |
| --- | --- | --- | --- | --- |
| `sc-01` | `current` | Generalized from repeated patterns | Pilot feedback pattern about switching from an earlier object to the current one | Extends the current-context object-swap pattern into a screwdriver-to-hammer case. |
| `sc-02` | `current` | Generalized from repeated patterns | Pilot feedback pattern about switching from an earlier room to the current room | Extends the current-context room-swap pattern into a bedroom-to-kitchen case. |
| `sc-03` | `prior` | Based on pilot user feedback | Pilot feedback about reaching back to an earlier activity in recorded video | Uses an earlier library task and asks about the arrangement from a few minutes before. |
| `sc-04` | `current` | Based on pilot user feedback | Pilot feedback about the assistant clinging to the first scene instead of the one being shown now | Keeps the original desk-to-kitchen scene shift that motivated the current-context benchmark shape. |
| `sc-05` | `current` | Generalized from repeated patterns | Pilot feedback pattern about switching from an earlier object to the current one | Turns the same current-context pattern into a two-poster visual similarity trap. |
| `sc-06` | `current` | Conceptual coverage case | Benchmark design coverage, informed by direct product testing and benchmark design work | Added to cover a current-context pegboard question that was important to the benchmark shape but not directly anchored in one pilot example. |
| `sc-07` | `current` | Generalized from repeated patterns | Pilot feedback pattern about following the current state after time passes | Uses the same scene at a later moment instead of a room or object swap. |
| `sc-08` | `current` | Generalized from repeated patterns | Pilot feedback pattern about following the current screen instead of the earlier one | Moves the same context-selection problem into a screen-based workflow. |
| `sc-09` | `prior` | Generalized from repeated patterns | Pilot feedback pattern about reaching back to the earlier scene after the relevant object is gone | Extends prior-context recall into an animal-departure case. |
| `sc-10` | `current` | Generalized from repeated patterns | Pilot feedback pattern about not carrying earlier quantities into the current scene | Uses a pallet swap to test whether the model updates to the current quantitative context. |
| `sc-11` | `prior` | Generalized from repeated patterns | Pilot feedback pattern about recalling a specific detail from the earlier scene | Extends prior-context recall into a product-label memory case. |

## Related benchmarks and positioning

This benchmark sits near a few benchmark families:

- multimodal assistant evaluation
- wearable or egocentric multimodal evaluation
- context-tracking or reference-resolution under changing context
- streaming multimodal understanding

Some adjacent public efforts include [OpenEQA](https://open-eqa.github.io/),
[StreamingBench](https://streamingbench.github.io/),
[WearVQA](https://arxiv.org/abs/2511.22154), and
[TeleEgo](https://arxiv.org/abs/2510.23981).

This benchmark differs from those efforts in a few ways. It is narrower,
more product-driven, and explicitly tied to model-selection decisions.
It focuses on context inference under live context change rather than
trying to be a broad benchmark of multimodal or embodied capability.

## Freeze and versioning

The v1 set is frozen so models can be compared on the same benchmark.
Scenario text, expected answers, prompt text, scoring semantics, and the
default ranking condition should stay fixed within the release.

Documentation clarifications and implementation cleanup that do not
change benchmark meaning do not require a new version. Changes that
would affect comparability should land as a new benchmark version or
explicit release change.

For the exact freeze rules, see [benchmark_spec.md](benchmark_spec.md).
In practice, comparisons should stay within the same release.

## Glossary

- `turn`: one part of the conversation.
- `between turns`: between one part of the conversation and the next,
  after something about the user's context has changed.
- `prior`: the scoring label for the earlier context.
- `current`: the scoring label for the current context.
- `prior context`: the object, place, or surrounding context from the
  earlier moment that the question is really about.
- `current context`: the object, place, or surrounding context from the
  current moment that the question is really about.
- `prompt conditions`: the three prompt setups used in v1:
  `baseline`, `condition_a`, and `condition_b`.
- `ranking condition`: the condition used for the main model
  comparison. In v1, this is `baseline`.
- `balanced accuracy`: the mean of accuracy on the `prior` and
  `current` classes so one class does not dominate the score.
- `simulated repair rate`: a secondary metric that stands in for likely
  user correction cost after a wrong answer.
- `multimodal assistant device`: a device on or near the user that can
  take live multimodal input and respond through audio and/or text.
