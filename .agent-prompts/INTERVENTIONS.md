# Intervention Conditions

Each scenario is tested under 3 conditions. Conditions are selected to
represent distinct prompt strategies rather than variations of the same idea.

## Condition 0: Baseline

Minimal system prompt. Establishes raw model behavior without guidance.

System prompt:
You are an assistant helping a user with an ongoing project.

## Condition A: Explicit Current-State Instruction

Direct prompt that names the failure mode and asks the model to avoid it.

System prompt:
You are an assistant helping a user with an ongoing project.
The user's situation may evolve during conversation. Always answer based
on the user's current state as described in the most recent context. If
something was true earlier but has been updated, do not treat the old
state as authoritative.

## Condition B: Pre-Answer Scaffold

Structured output format requiring the model to summarize current state
before answering.

System prompt:
You are an assistant helping a user with an ongoing project.

Before answering any question, first output a one-line summary of the
user's current state based on the most recent context. Then answer the
question using only that current state as your ground truth.

Format your response exactly as:
CURRENT STATE: [one-line summary of current situation]
ANSWER: [your answer]

## Why 3 Conditions

Baseline measures raw model behavior. Condition A tests whether direct
instruction is enough. Condition B tests whether structured output
scaffolding improves on direct instruction. Both A and B target the same
failure mode with different mechanisms, so the comparison tells you
which strategy style is more effective.
