# Methodology

## Overview

This framework measures whether specific prompt and scaffolding changes
fix a specific failure: a live-assistant model answering from earlier
conversation state after the user has described a state change. The
target product is a wearable camera whose assistant sees a stream of
scene descriptions; pilot feedback showed the assistant sometimes
replies using an earlier scene even when the user's most recent message
describes something new. The framework reproduces that failure mode in a
controlled way, then compares three prompt conditions side by side to
see which, if any, actually move the pass rate.

The novelty in this project is the scenario set and the intervention
comparison, not the underlying measurement technique. The scoring stack
combines standard code-based pattern matching with a standard
LLM-as-judge step. Both are well-trodden ideas. The framework's job is
to apply them to a specific, pilot-derived failure mode and to report
effect sizes honestly, including the classes where no intervention helps.

## Scenario design

Each scenario is a two-turn conversation. Turn 1 establishes an initial
state and asks a question grounded in that state; the model answers.
Turn 2 describes a state change, either a new scene or a new fact that
supersedes something from Turn 1, and then asks a follow-up question
that is only correctly answered from the updated state. Turn 2 is the
only turn that is scored. Turn 1 exists to create the grounding-failure
opportunity: without a prior state to bleed through, there is nothing
for the model to get wrong.

Eight scenarios are drawn from pilot incident classes. The exact
distribution across tiers lives in `.agent-prompts/SCENARIO_SEEDS.md`.
Tier 1 scenarios present clean single transitions; Tier 2 adds partial
state overlap or implied rather than explicit transitions; Tier 3 adds
ambiguity about which state is authoritative. The incident classes
themselves are documented separately in `docs/incident_classes.md` so
the scenarios can be traced back to real user complaints.

## Intervention conditions

Three prompt conditions are compared. The baseline condition uses a
minimal system prompt and measures raw model behavior on these
scenarios. Condition A adds a direct instruction that names the failure
mode and asks the model to ground answers in the most recent context.
Condition B replaces the direct instruction with a structured output
scaffold that forces the model to restate its understanding of the
current state before it answers. The three conditions are intentionally
distinct strategies rather than parameter sweeps of one strategy, so
that the comparison tells us which *kind* of fix helps rather than which
wording variant is best. Full prompts live in `docs/interventions.md`.

## Scoring

Scoring is hybrid. The code-based scorer reports three signals per
response: whether any current-state answer fuzzy-matches the response,
whether any stale-state answer fuzzy-matches it, and whether the
response reads as a refusal or "I don't know" hedge. These are
deterministic and fast but brittle on paraphrase. The LLM judge, also
Claude Sonnet 4.6 at temperature zero, receives the response alongside
the current and stale answer lists and a brief scenario description,
reasons step by step about grounding, and returns a structured verdict.
Both scores are reported in the findings. A trial passes only when both
signals agree that the response reflects current state and not stale
state. That is, the code-based rule (has_current=True, has_stale=False,
is_refusal=False) and the judge's passed=true verdict must both hold.
Disagreement between the two signals is itself a finding, reported
separately.

The judge is in the same model family as the model under test. That
introduces a known self-preference risk: agreement between them may be
inflated by shared training priors. Cross-family judge validation is
deferred to a future experiment (`exp_009`, see
`docs/deferred_roadmap.md`); for now the limitation is documented in
`docs/limitations.md` and callers are expected to treat single-family
judge verdicts as a ceiling rather than a ground truth.

## Trial design

Each scenario is run twice per condition at temperature zero, giving two
trials per (scenario, condition) cell and 48 scored Turn 2 responses
overall. Temperature zero does not guarantee bit-identical outputs
because of nondeterminism on the API side, but it keeps per-cell
variance low enough that two trials catch most of the realistic output
variation without the cost of five or ten. The two trials per cell are
not for statistical power; they are a cheap sanity check that a
condition's effect is stable across reruns.

## Interpretation

Findings are reported as a condition-by-incident-class matrix of pass
rates, plus per-condition aggregate pass rates and per-condition effect
sizes relative to baseline. Read the matrix row by row to see how a
condition performs across classes, and column by column to see which
classes respond to any intervention at all. Effect sizes are raw
arithmetic differences (condition pass rate minus baseline pass rate);
no confidence intervals are reported because the sample size is too
small to support them honestly. A class where no condition improves on
baseline is a signal that the failure mode needs a different kind of
fix, possibly structural rather than prompt-level, and that finding is
worth more than a table full of small positive deltas.
