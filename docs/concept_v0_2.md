# Benchmark Spec: Visual-Context Selection for a Wearable Live-Assistant Camera Product

Status: rewritten 2026-04-19 for the v1 benchmark-reset pass.

## Benchmark definition

`Deixis-Bench` measures **situated reference resolution** in a
wearable live-assistant camera product. Given a two-turn
conversation in which visual context shifts between turns, does the
candidate model correctly infer, from the user's words, objects,
location, and recent conversational history, which visual context
the Turn 2 question refers to? The inferred anchor is labeled as
`prior` or `current` for scoring purposes.

This is the same phenomenon, **reference resolution under context
shift**, that linguists call deixis. Object recognition is assumed
and out of scope.

The benchmark is used internally to compare candidate model releases
and choose which one ships.

## Cue taxonomy

The scoring axis is binary (`prior` vs. `current`), but the cues a
candidate must use to land on the right answer are plural. The v1
set exercises five cue families:

- **Spatial / scene shift**: the user has walked from one room,
  camera angle, or physical location to another between Turn 1 and
  Turn 2.
- **Object-reference shift**: the user has put down object A and
  picked up object B, or object A has left frame and object B has
  entered.
- **Temporal / same-scene state change**: the camera is on the
  same scene as Turn 1 but meaningful state has changed (an item
  moved, a reading changed, an animation progressed).
- **Object departure or return**: an object present in Turn 1 has
  left frame by Turn 2, or re-entered after being gone.
- **Verbal / deictic cue**: the user's Turn 2 phrasing itself
  disambiguates ("this one", "the new one", "here", "still").

A correct response infers the anchor from whichever cue family the
Turn 2 question actually invokes. Per-scenario cue labels live in
`experiments/exp_001/README.md`.

## Prior and current visual contexts

- **prior visual context**: an object or place from a prior frame.
- **current visual context**: an object or place from the current,
  right-now frame.

A correct answer anchors to whichever visual context the question
actually refers to. Sometimes that is `current`; sometimes it is
`prior`.

## Variants

There are two official benchmark variants.

### With-prior-Q (implemented in v1)

Turn 1 asks about the prior frame in a way that establishes an
explicit referent. Turn 2 shifts visual context and asks an
ambiguously-referenced follow-up. The model must override the
Turn 1 anchor.

### Without-prior-Q (planned next)

The user's visual context shifts after the model has analyzed a
prior frame, but Turn 1 did not create the anchor the model needs
to override. Correct behavior is to default to the current frame.
Three subcases are preserved as part of the benchmark definition:

- **Soft case**: descriptive prior-frame question, then a new-room
  follow-up.
- **Unrelated-prior-question case**: prior frame was seen, but the
  prior question was unrelated.
- **Pure no-Turn-1 case**: prior frame was analyzed, but the user had
  not asked any prior question at all.

Without-prior-Q is not yet implemented. It remains part of the
official benchmark definition and is tracked in
`docs/deferred_roadmap.md`.

## Benchmark governance

- Pilot feedback from one model is the **authoring source** for the
  initial scenario seeds. That source does not define the benchmark
  boundary.
- The v1 scenario set is **frozen** after the v0.3.0 remediation
  pass. Future candidate models are evaluated on the same frozen
  set.
- Benchmark growth happens by creating **new versioned benchmark
  sets** (v2, etc.) or explicit version extensions, not by
  silently changing the meaning of v1 after results have been
  compared.

### Scope relative to the broader pilot failure surface

The pilot corpus (see `.agent-prompts/PILOT_CORPUS_INVENTORY.md`)
identifies several adjacent failure classes that are **valid corpus
findings** but are not part of the runnable v1 benchmark:

- retrieval-shaped prior-reach cases (ex-01, ex-02)
- intent routing / stateless phrasing (ex-03)
- weak-grounding fabrication / false confidence (ex-06)
- background audio leakage into recaps (ex-05)
- speaker identity / diarization (ex-07)

The v1 benchmark is deliberately narrow: it measures prior-versus-
current visual-context selection, not every failure class the
pilot corpus surfaced. Adjacent classes are tracked in
`docs/deferred_roadmap.md` and `docs/limitations.md`.

## Shipping-use purpose

The benchmark is how the team decides which candidate model to ship
in the wearable live-assistant camera product. A candidate is
evaluated on the same frozen v1 scenario set, and its score under
the default ranking condition is compared against the currently
shipped model and against other candidates.

## Primary benchmark score

The primary score for v1 is **balanced Turn 2 accuracy on the fixed
benchmark set under the ranking condition**. Balanced means the
mean of per-class accuracy over the two scored policy classes:

```
primary_score = (prior_class_accuracy + current_class_accuracy) / 2
```

Within a class, accuracy is the **mean across all Turn 2 trial
outcomes for items in that class** under the ranking condition.

### Aggregation rule

```
class_accuracy = correct_trials_in_class / total_trials_in_class
```

Trials are expanded across scenarios, conditions, and repeats; each
trial contributes one 0/1 outcome to its class before the mean is
taken.

### Why balanced accuracy

The v1 runnable set is 8 scenarios with `target_context: current`
and 3 scenarios with `target_context: prior`. Raw accuracy on that
skew still rewards a trivial "always current" policy at roughly
73%. Balanced accuracy closes that loophole without reshaping
scenario content. Future versions with closer class balance may
revert to raw mean Turn 2 accuracy.

### Ranking condition

The default ranking condition is `baseline`. Ship decisions are made
from balanced accuracy under `baseline`. The intervention axis
stays in the benchmark as a secondary analysis axis; reports show
per-condition sensitivity.

### Clarify / abstain scoring

For v1, `target_context` is always `prior` or `current`. If the judge
emits `clarify` or `abstain` on a v1 item, the trial is **counted as
wrong for the primary score** (equivalent to any other non-target
policy selection). The report still renders `clarify` and `abstain`
as separate **diagnostic-only rows** for visibility; their pass
counts never feed the primary score.

## Scenario design

Every scenario is a two-turn conversation, optionally extended to
three turns for simulated repair.

- **Turn 1** establishes a visual-context reference state.
- **Turn 2** changes the state or shifts the implied visual context
  and asks a follow-up. Only Turn 2 is scored.
- **Turn 3 (simulated repair)** fires only on Turn 2 failure and is
  a templated "I mean, [explicit anchor]" follow-up. The repair
  rate is secondary reporting.

The `Scenario` dataclass exposes optional `turn_1_image` and
`turn_2_image` fields so future image inputs can be attached to the
message payload. Both are unset in v1; v1 is a text-proxy slice of
the benchmark.

## Judge and Scoring

The judge reads the Turn 2 response, the scenario description and
both answer lists, and labels the response with one of four policy
tags. v1 scores only `prior` vs `current`; `clarify` and `abstain`
remain emittable tags for diagnostic visibility but count as wrong
for the primary score.

The judge family defaults to `auto`: at run time, the candidate
model string is inspected, and the judge is assigned to a different
family to reduce same-family bias. If the candidate family cannot be
inferred from the string, the runner errors out and requires an
explicit `--judge-family` flag. Same-family comparisons remain
available via `--judge-family claude`.

The code-based scorer (`core/scoring.py`) is retained as an audit
cross-check. Judge verdict is the primary signal.

## Related literature positioning

The closest literature-facing anchor is reference resolution under
context shift in multimodal/egocentric settings. Common ground
tracking and clarificational-exchange work are adjacent influences,
not the top-level story here. The repo should not overstate novelty
around streaming input or wearable sensing; those are context-
setting neighbors.

Detailed literature pointers live in `docs/related_work.md`.

## Conflict of Interest

The author works with the maker of the wearable live-assistant
camera product that generated the pilot corpus on a contract
research basis. The product's assistant runs on a non-Claude
production model family. This benchmark is used internally to
compare candidate models for shipping; it is not a leaderboard or a
public ranking of production assistants.
