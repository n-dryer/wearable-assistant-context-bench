# Scenario Seeds

## Status

**TEMPLATE-SEEDS-NOT-FILLED-IN.** Prompt 2 will refuse to
proceed until either (a) Nate has filled in the Turn 1 and Turn 2 content
for each seed, or (b) Prompt 2 is explicitly invoked with permission to
auto-generate seed content from the populated INCIDENT_CLASSES.md.

## How to Fill This In

Option A (manual): For each seed, replace the [TO FILL: ...] placeholders
with concrete Turn 1 and Turn 2 content. Update [IC-XX: TBD] to reference
a real class from your filled-in INCIDENT_CLASSES.md.

Option B (agent-assisted): Leave the placeholders. When you run Prompt 2,
tell Claude Code to generate seed content from the incident class descriptions
in INCIDENT_CLASSES.md. Review and edit before Phase 6.

When done, delete the "Status" and "How to Fill This In" sections so
Prompt 2's prereq check passes.

## 2-Turn Structure

Every scenario has the following structure:

Turn 1: User describes the initial situation and asks a question grounded
in that initial state. The assistant answers.

Turn 2: User describes a state change (moved to a different room, picked
up a different object, changed the topic) and asks a follow-up question
grounded in the new state.

Scoring: Only Turn 2 is scored. The failure mode we are testing is
whether the model correctly uses the updated state at Turn 2 instead of
letting Turn 1 state bleed through.

Total: 8 seeds. Distribution: 3 Tier 1, 4 Tier 2, 1 Tier 3.

## Tier 1 Seeds (clean single transitions)

### Seed 1 (Tier 1, [IC-XX: TBD])

Turn 1 (user): [TO FILL: describe a clear initial state and ask a
question about something in that state. Example: "I'm in the kitchen
looking at the counter. What's on the counter?"]

Turn 2 (user): [TO FILL: describe moving to a new state and ask a
follow-up question. The question should be answerable from the new
state, and any answer drawn from the Turn 1 state should be clearly
wrong. Example: "Okay, I've walked into the bathroom now. What can
you see here?"]

Turn 2 current answers (what a correct response should include):
- [TO FILL: items that belong to the NEW state]

Turn 2 stale answers (what a correct response should NOT include):
- [TO FILL: items that belonged to the OLD state and should not appear]

### Seed 2 (Tier 1, [IC-XX: TBD])

[Same structure as Seed 1]

### Seed 3 (Tier 1, [IC-XX: TBD])

[Same structure]

## Tier 2 Seeds (realistic complexity)

Tier 2 adds partial overlap between states, distracting details, or
implied rather than explicit transitions.

### Seed 4 (Tier 2, [IC-XX: TBD])
[Same structure]

### Seed 5 (Tier 2, [IC-XX: TBD])
[Same structure]

### Seed 6 (Tier 2, [IC-XX: TBD])
[Same structure]

### Seed 7 (Tier 2, [IC-XX: TBD])
[Same structure]

## Tier 3 Seed (adversarial combination)

### Seed 8 (Tier 3, [IC-XX: TBD + IC-YY: TBD])
[Same structure, combining two failure patterns]
