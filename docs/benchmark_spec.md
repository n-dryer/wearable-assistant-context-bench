# Benchmark Spec: Wearable Assistant Context Benchmark

**Subtitle:** A benchmark for implicit context tracking in mobile multimodal
assistants.

This document is the canonical benchmark spec for the active release. The
repository contains the **v1 runnable slice** for **reference-state selection
under implicit context shift**.

## Public benchmark and current slice

- **Public benchmark**: Wearable Assistant Context Benchmark
- **Current repository scope**: v1 runnable slice for reference-state
  selection under implicit context shift
- **Scored v1 behavior**: binary `prior` vs `current` Turn 2 anchor selection

Reference-state selection is a scored sub-capability, not the full benchmark
identity.

## What the benchmark measures

Mobile multimodal assistants operate in a world that changes silently between
turns. The user walks into a new room, sets down one object and picks up
another, returns to something from a minute ago, or asks with a deictic cue
like “this” or “here”. The benchmark measures whether the assistant tracks the
right implicit context for the user’s question.

The v1 runnable slice scores **reference-state selection under implicit context
shift**. In a two-turn conversation with a context shift between turns, does
the assistant answer from the:

- **prior visual context**: an object or place from a prior frame
- **current visual context**: an object or place from the current frame

Object recognition is assumed and out of scope.

Concrete example:

- Turn 1: the user asks about a screwdriver in hand
- Turn 2: the user has switched to a hammer and asks, "am I holding this correctly?"
- The scored question is whether the answer follows the prior context or the
  current one

## v1 runnable slice

The active runnable slice contains:

- **11 frozen scenarios**
- **3 intervention conditions**
- **2 trials per (scenario, condition) cell** by default
- **Turn 2 scoring only**
- **Turn 3 repair** as a secondary diagnostic

The implemented slice is the **with-prior-Q** variant:

- Turn 1 establishes a referent
- Turn 2 shifts context and asks an ambiguously anchored follow-up
- The model must decide whether the answer belongs to the prior or current
  context

The **without-prior-Q** variant remains part of the benchmark definition but is
not yet implemented in v1.

## Scenario and intervention inputs

The only active runtime inputs for the slice are:

- [`benchmark/v1/scenarios.json`](../benchmark/v1/scenarios.json)
- [`benchmark/v1/expected_answers.json`](../benchmark/v1/expected_answers.json)
- [`benchmark/v1/interventions.json`](../benchmark/v1/interventions.json)

These JSON files are the canonical runtime inputs for v1.

## Scoring and ranking

Each trial produces a Turn 2 judge label:

- `current`
- `prior`
- `clarify`
- `abstain`

For v1, authored targets are only `current` or `prior`. If the judge emits
`clarify` or `abstain`, that trial counts as wrong for the primary score.

### Primary score

The primary score is **balanced Turn 2 accuracy under the ranking condition**.

```text
primary_score = (prior_class_accuracy + current_class_accuracy) / 2
```

Class accuracy is the mean across all Turn 2 trials for that class under the
ranking condition.

### Default comparison condition

`baseline` is the default condition used to compare candidate models.

`condition_a` and `condition_b` remain in the benchmark as diagnostic
conditions. Their purpose is to show prompt sensitivity, not to replace the
baseline ranking condition unless the production wrapper changes later.

## Judge and runtime behavior

The runner supports candidate and judge models across Claude, OpenAI, and
Gemini families.

- `--judge-family auto` is the default
- under `auto`, the judge family must differ from the candidate family
- explicit `claude`, `openai`, or `gemini` overrides remain available

Each run emits:

- `transcripts.jsonl`
- `findings.md`
- a machine-readable manifest bundled into the findings output

The manifest records the scenario, answers, and intervention SHAs, judge prompt
version/hash, model IDs, trial count, ranking condition, timestamp, and git
commit.

## Governance

- The v1 scenario set is **frozen**
- candidate models are compared on the same frozen set
- benchmark growth happens through new versioned slices or extensions, not by
  silently changing v1

## Limitations

The repo is intentionally narrow:

- v1 measures one sub-capability, not the full benchmark space
- v1 is still a text-proxy slice; image fields are plumbed but unset
- the class mix is skewed toward `current`, which is why the primary metric is
  balanced accuracy
- v1 currently implements only the with-prior-Q variant
- prompt interventions are useful diagnostics, but baseline is the canonical
  ranking condition

## Future slices

The next material extension is **without-prior-Q** coverage. Later work may add
image-enabled inputs, broader context-tracking behaviors, and larger evaluation
sets, but those are outside the scope of this v1 release.
