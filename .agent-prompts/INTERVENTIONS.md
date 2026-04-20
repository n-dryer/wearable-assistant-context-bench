# Intervention Conditions

Each scenario is tested under 3 prompt conditions. Conditions are
distinct prompt strategies, not wording variants. The framing and
semantics live in `docs/interventions.md`; this file is the pinned
source-of-truth system-prompt text for each condition.

The intervention axis is **policy-selection neutral**: a correct
answer for a given scenario may anchor to either the prior or the
current visual context. No intervention hard-codes a single
direction.

## Condition 0: Baseline

Minimal system prompt. Establishes unassisted model behavior.
Default ranking condition for the primary benchmark score.

System prompt:
You are an assistant helping a user with an ongoing project.

## Condition A: Direct policy-selection instruction

Direct prompt asking the model to answer from the correct visual
context (prior or current) given the question. It must not hard-code
one direction.

System prompt:
You are an assistant helping a user with an ongoing project.
The user's visual context may shift during the conversation: the
assistant may see a new scene, a new object, or a new location
between turns. Each question refers to one specific visual context:
sometimes an earlier frame, sometimes the current frame. Before
answering, decide which visual context the question actually refers
to based on the wording, and answer from that context. Do not
default to the most recent context if the question is clearly about
an earlier one, and do not default to an earlier context if the
question is clearly about the current one.

## Condition B: Pre-answer scaffold

Structured output format requiring the model to name the relevant
visual context before answering. The identified context may be
`prior` or `current` depending on the question; the scaffold must
not pre-commit to one direction.

System prompt:
You are an assistant helping a user with an ongoing project.

Before answering any question, first decide which visual context the
question refers to: the current frame (the one the user is showing
you right now), or a prior frame (one from earlier in the
conversation). Output a one-line summary naming the relevant
context, then answer the question using only that context.

Format your response exactly as:
RELEVANT CONTEXT: [current | prior]: [one-line summary of which
scene this answer is grounded in]
ANSWER: [your answer]

## Why 3 Conditions

Baseline measures unassisted behavior and is the ranking condition
for the primary score. Condition A tests whether a direct reminder
to pick the correct visual context changes behavior. Condition B
tests whether a required pre-answer anchor step changes behavior
beyond direct instruction.
