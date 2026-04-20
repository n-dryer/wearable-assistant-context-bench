# Intervention Conditions

The benchmark runs three prompt conditions. This document covers
their **framing and semantics** only. The exact system-prompt text
for each condition lives in
`experiments/exp_001/interventions.json` and is mirrored in
`.agent-prompts/INTERVENTIONS.md`.

## Role of interventions in the benchmark

The primary score is balanced Turn 2 accuracy under a **ranking
condition**. The default ranking condition is `baseline`. Ship
decisions are made from that number. The other two conditions are
**secondary diagnostic conditions** that probe how sensitive the
candidate is to small changes in the surrounding prompt, unless a
different production wrapper is explicitly designated later.

The intervention axis is policy-neutral: a correct answer in a
given scenario may anchor to **either** the prior or current
visual context, and no intervention should hard-code a single
direction.

## Condition 0: Baseline

Minimal system prompt. Default ranking condition. Establishes the
candidate's unassisted behavior on the benchmark set.

## Condition A: Direct policy-selection instruction

Baseline plus a direct instruction to answer from the **correct
visual context based on the most relevant state**. The instruction
must not say "always answer from the current state" or "only use
the current state as ground truth"; it must leave room for answers
that anchor to a prior frame when the question refers to one.

## Condition B: Pre-answer scaffold

Baseline plus a required output format where the model first
identifies the **relevant visual context for this answer**, then
answers using that reference. The identified context may be
`current` or `prior` depending on the question; the scaffold must
not pre-commit to one direction.

## Why these three

- Baseline measures unassisted behavior and is the ranking
  condition.
- Condition A tests whether a plain reminder to pick the correct
  visual context changes behavior.
- Condition B tests whether a required pre-answer anchor step
  changes behavior beyond direct instruction.

## Out of scope for this experiment

`exp_001` does not test:

- few-shot examples
- explicit clarify-or-abstain instructions
- retrieval or tool-use context injection
- fine-tuning or RLHF changes

Those are separate intervention families and live in
[docs/deferred_roadmap.md](deferred_roadmap.md).
