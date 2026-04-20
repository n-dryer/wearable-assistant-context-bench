# v1.1 Scenario Expansion (7 scenarios, landed) — historical

> **Historical authoring note.** This document captures the planning
> prompt used to extend the pre-freeze seed set from 4 scenarios to
> 11. The "v1.1" label in the body is the pre-release working name
> for what was subsequently released as **Deixis-Bench v1**; the
> initial public release collapses v1.0 + v1.1 into a single v1 tag.
> sc-01 through sc-11 are the frozen members of **v1**.
>
> This file is retained under `docs/history/` for authorship
> transparency. Current governance and scenario-set inventory live
> in `docs/concept_v0_2.md` and `experiments/exp_001/README.md`. Do
> not treat "v1.1" inside this file as a live project label.

Ready-to-drop-in expansion for `experiments/exp_001/scenarios.json` and
`experiments/exp_001/expected_answers.json`. Integrates after the
Phase 3 remediation has landed (which locks in sc-01 through sc-04 in
their corrected form).

## Purpose

The frozen v1 set is 4 scenarios. This expansion adds 7 to bring
v1.1 to 11 total, covering construct dimensions not represented in
the original set: visual-similarity trap, without-prior-Q, temporal
shift in the same place, screen-domain swap, absence/negative case,
and numeric/quantitative referent.

Selection rationale from the scenario-review sub-agent: each new
scenario earns its slot for a distinct construct dimension, not for
redundant variety within a dimension already covered.

## Authoring discipline adopted for v1.1 and beyond

Four rules derived from the scenario-review sub-agent's
construct-level flags. Apply to any scenario before admitting it to
the frozen set.

**Rule 1: T2-alone divergence test.** A scenario must produce a
different winning answer than a one-shot model given only T2 would
produce under anchoring-failure conditions. In practice: the
`prior_answers` list must contain tokens that a T1-anchored model
would use but a fresh-T2 model would not. If the only difference
between a pass and a fail is which frame the answer references (and
both references yield a reasonable answer to T2 on its own), the
scenario is a degraded context-selection test. Flag it.

**Rule 2: Single-dimension shift.** Turn 2 should change exactly one
thing (object, place, time, screen, person). If it changes two
things simultaneously (e.g., move rooms AND swap objects), an
anchoring failure can't be cleanly attributed. Combination scenarios
are deferred to a future adversarial subset.

**Rule 3: No category-prior confounds.** If a strong category prior
predicts the wrong answer independent of context selection (e.g.,
"soup should be heated" for gazpacho), exclude the scenario or tag
it as diagnostic-only. Mixed error modes produce composite error
rates that can't be interpreted for model ranking.

**Rule 4: Referent ambiguity rubric.** A T2 question is genuinely
ambiguous only if a reader with both frames but no conversation
history could not confidently pick which frame is being referenced.
Apply before admitting. T2 phrasings that already self-resolve to
the current frame ("Where should I set this?" when only the current
frame has a surface) fail this check.

## Scenarios

Each scenario block gives the `scenarios.json` entry and the
corresponding `expected_answers.json` entry.

### sc-05: Guest bedroom to master bedroom (visual-similarity trap)

Construct dimension: visual-similarity trap. Two rooms of the same
functional category where the model may lazily reuse the prior
assessment because the scenes look similar. Text-proxy partially
defuses this (prose differentiates the rooms explicitly), so flag
for image-version re-testing in v2.

```json
{
  "scenario_id": "sc-05",
  "target_policy": "current",
  "authoring_basis": "extended_from_pilot",
  "source_example_id": "ex-09",
  "surface": "wearable_live_frame",
  "turn_1_user": "I'm in our guest bedroom. The walls are eggshell white, there's a single framed botanical print above the bed, and the bedframe is light pine, twin-size, with a thin metal rail headboard. We're thinking of replacing this bedframe. Would a queen size even fit in this room given the narrow footprint?",
  "turn_2_user": "Okay, I've walked into the master bedroom. The walls are deep navy, the headboard is solid walnut with tufted gray upholstery, and the bedframe is king-size on a low modern platform. What about this one?",
  "turn_3_repair_anchor": "I mean, the master bedroom bedframe I'm looking at now, not the guest bedroom.",
  "notes": "Visual-similarity trap. Both frames are bedrooms with bedframes; prior frame is guest (small, light, pine, twin), current frame is master (large, dark, walnut, king). Turn 2's referent `this one` must resolve to the current bedframe. Anchoring failure reuses guest-bedroom tokens."
}
```

```json
"sc-05": {
  "current_answers": [
    "master",
    "navy",
    "walnut",
    "tufted",
    "king",
    "platform",
    "modern",
    "larger",
    "upgrade"
  ],
  "prior_answers": [
    "guest",
    "eggshell",
    "pine",
    "twin",
    "metal rail",
    "botanical",
    "narrow",
    "small"
  ],
  "clarify_indicators": [],
  "abstain_indicators": [
    "I can't see",
    "I don't know which",
    "which bedframe"
  ]
}
```

### sc-06: Bedroom + unrelated T1 question to kitchen walls (without-prior-Q)

Construct dimension: without-prior-Q variant. T1 establishes a
visual context (bedroom) but asks a question unrelated to the
bedroom's contents (to-do list organization). Any stale anchoring in
T2 must come from the visual signal alone, not from a Turn-1
language anchor the model is overriding. This is the canonical
stricter test Nate described on 2026-04-19.

```json
{
  "scenario_id": "sc-06",
  "target_policy": "current",
  "authoring_basis": "extended_from_pilot",
  "source_example_id": "ex-09",
  "surface": "wearable_live_frame",
  "turn_1_user": "I'm sitting on the edge of the bed in our bedroom. The walls are a pale blue, the ceiling is white, and afternoon light is coming through the window. I'm trying to figure out the most effective way to organize a daily to-do list so I actually get things done. Any advice?",
  "turn_2_user": "Okay, I've walked into the kitchen. The walls are a warm terracotta, the cabinets are white with brass pulls, and the counters are butcher block. What color are the walls?",
  "turn_3_repair_anchor": "I mean, the kitchen walls I'm looking at now, not the bedroom.",
  "notes": "Without-prior-Q variant. Turn 1 establishes bedroom visual context but asks an unrelated productivity question, so there is no language-level anchor for Turn 2 to override. Turn 2 shifts to kitchen and asks a purely visual question. A stale-anchoring failure would answer `pale blue` (bedroom walls) instead of `terracotta` (current walls)."
}
```

```json
"sc-06": {
  "current_answers": [
    "terracotta",
    "warm",
    "orange",
    "red-brown",
    "rust",
    "earthy"
  ],
  "prior_answers": [
    "pale blue",
    "blue",
    "bedroom"
  ],
  "clarify_indicators": [],
  "abstain_indicators": [
    "I can't see",
    "I don't know",
    "which walls"
  ]
}
```

### sc-07: Raw to browned chicken (temporal shift, same place)

Construct dimension: temporal shift in the same place. sc-03 uses
temporal language ("a few minutes ago") as the anchor, but v1 has no
scenario where the place stays constant and the scene state evolves.
Cooking state is a natural fit because the correct action depends
sharply on what's changed.

```json
{
  "scenario_id": "sc-07",
  "target_policy": "current",
  "authoring_basis": "extended_from_pilot",
  "source_example_id": "ex-09",
  "surface": "wearable_live_frame",
  "turn_1_user": "I'm at the stove. A cast-iron skillet is on medium-high heat. I just dropped in four bone-in chicken thighs, skin-side down. They're hissing and releasing moisture, the meat is still raw with visible pink around the edges. When should I flip them?",
  "turn_2_user": "A few minutes have passed. The skin is now deep golden brown and crisped up, there's a strong sear smell, and the thighs have released cleanly from the pan. What should I do now?",
  "turn_3_repair_anchor": "I mean, the chicken I'm looking at right now with the browned skin, not when I first dropped it in.",
  "notes": "Temporal shift, same place. Turn 1 anchors a raw-state referent (wait before flipping). Turn 2 shifts the scene state to browned and released (flip now / finish other side). Stale-anchoring failure would repeat the `wait` advice from the raw state."
}
```

```json
"sc-07": {
  "current_answers": [
    "flip",
    "turn",
    "other side",
    "golden",
    "brown",
    "crisp",
    "released",
    "ready",
    "5 to 7 more minutes",
    "finish"
  ],
  "prior_answers": [
    "wait",
    "don't touch",
    "leave",
    "raw",
    "not yet",
    "still pink",
    "hissing"
  ],
  "clarify_indicators": [],
  "abstain_indicators": [
    "I can't see",
    "I don't know"
  ]
}
```

### sc-08: Code editor to spreadsheet (screen-domain swap)

Construct dimension: screen-domain swap. v1 has no screen-content
scenario. Screens are a live context for a wearable assistant when
the user is working at a desk, and screen content shifts frequently
with no physical movement. The winning answer domain (formula
critique) differs sharply from the prior-anchored domain (code
efficiency), so scoring is crisp.

```json
{
  "scenario_id": "sc-08",
  "target_policy": "current",
  "authoring_basis": "extended_from_pilot",
  "source_example_id": "ex-09",
  "surface": "wearable_live_frame",
  "turn_1_user": "My screen shows a Python code editor. There's a 30-line function called `calculate_shipping_cost` that takes weight, distance, and tier as arguments. It has three nested if-else blocks and returns a float. Is this function efficient?",
  "turn_2_user": "Okay, I've switched windows. My screen now shows a spreadsheet. It's a monthly P&L with revenue, COGS, and opex across twelve columns. Row 8 is labeled `gross margin` and cell B8 contains the formula `=B2-B4`, copied across all twelve month columns. What's wrong with this?",
  "turn_3_repair_anchor": "I mean, the spreadsheet formula I'm looking at now, not the Python function.",
  "notes": "Screen-content shift. Turn 1 anchors a code-efficiency referent (nested if-else, function structure). Turn 2 shifts to a spreadsheet formula and asks `what's wrong`. Stale-anchoring failure would critique code structure rather than spreadsheet formula reference issues."
}
```

```json
"sc-08": {
  "current_answers": [
    "formula",
    "B2",
    "B4",
    "row 2",
    "row 4",
    "reference",
    "absolute",
    "relative",
    "column",
    "copied",
    "margin",
    "dollar sign",
    "anchor"
  ],
  "prior_answers": [
    "function",
    "nested",
    "if-else",
    "python",
    "efficient",
    "calculate_shipping_cost",
    "float",
    "code",
    "refactor"
  ],
  "clarify_indicators": [],
  "abstain_indicators": [
    "I can't see",
    "I don't know"
  ]
}
```

### sc-09: Desk inventory absence check (absence/negative case)

Construct dimension: absence/negative case. The failure mode is
assuming a prior-frame object is still present in the current frame.
This is a **strong Rule 1 scenario**: a one-shot model given only T2
would likely say "those three items, ready to go," while a correctly
context-selecting two-turn model would notice the phone is missing.
Different winning answers, clean anti-anchoring requirement.

```json
{
  "scenario_id": "sc-09",
  "target_policy": "current",
  "authoring_basis": "extended_from_pilot",
  "source_example_id": "ex-09",
  "surface": "wearable_live_frame",
  "turn_1_user": "I'm at my desk getting ready to head out for a meeting. On the surface in front of me I can see: my open laptop, my keys resting on the top-left corner, my brown leather wallet, and my phone face-up next to the keyboard. Am I ready to go?",
  "turn_2_user": "I stepped out for a minute and came back to the desk. On the surface now I see my laptop, my keys, and my wallet. What about now?",
  "turn_3_repair_anchor": "I mean, compare the desk now to before. Is anything missing?",
  "notes": "Absence/negative case. Turn 1 establishes a four-item inventory (laptop, keys, wallet, phone). Turn 2 lists three items, omitting the phone. Winning behavior notes the phone is missing; stale-anchoring failure reuses the `all set` Turn-1 framing. Passes Rule 1 sharply: a fresh-T2 model would describe three items without flagging absence."
}
```

```json
"sc-09": {
  "current_answers": [
    "phone",
    "missing",
    "not there",
    "gone",
    "forgot",
    "don't have",
    "three items",
    "only three",
    "left it"
  ],
  "prior_answers": [
    "ready",
    "all set",
    "good to go",
    "yes you're ready",
    "have everything",
    "all four"
  ],
  "clarify_indicators": [],
  "abstain_indicators": [
    "I can't see",
    "I don't know"
  ]
}
```

### sc-10: Receipt quantitative swap (numeric referent)

Construct dimension: numeric/quantitative referent. v1 has no
scenario where the answer depends on picking the right number from
the right frame. Receipt totals are natural because they're
self-explanatory and the judgment ("reasonable?") is context-bound.

```json
{
  "scenario_id": "sc-10",
  "target_policy": "current",
  "authoring_basis": "extended_from_pilot",
  "source_example_id": "ex-09",
  "surface": "wearable_live_frame",
  "turn_1_user": "I just got back from the grocery store. I'm looking at the receipt in my hand. The total at the bottom reads $47.82. This covered one week of groceries for two adults, mostly staples. Is that a reasonable amount?",
  "turn_2_user": "Later that evening my partner came home with a second receipt from a different store. I'm looking at it now. The total reads $112.40, also one week of groceries for two adults. How about this one?",
  "turn_3_repair_anchor": "I mean, the $112.40 receipt I'm looking at now, not the earlier one.",
  "notes": "Numeric referent. Turn 1 anchors a low-total receipt ($47.82, judgment: reasonable). Turn 2 shifts to a higher-total receipt ($112.40). Winning behavior evaluates the $112.40 figure specifically; stale-anchoring failure references $47.82 or averages the two."
}
```

```json
"sc-10": {
  "current_answers": [
    "112",
    "112.40",
    "high",
    "expensive",
    "above average",
    "on the higher end",
    "steep",
    "$15 per person per day",
    "second receipt"
  ],
  "prior_answers": [
    "47",
    "47.82",
    "reasonable",
    "first receipt",
    "earlier",
    "low",
    "good deal"
  ],
  "clarify_indicators": [],
  "abstain_indicators": [
    "I can't see",
    "I don't know",
    "which receipt"
  ]
}
```

## Integration instructions

When Claude Code integrates this expansion (after Phase 3
remediation is green):

1. Append sc-05 through sc-11 to
   `experiments/exp_001/scenarios.json` in the given order.
2. Append the seven corresponding entries to
   `experiments/exp_001/expected_answers.json`.
3. Update `experiments/exp_001/README.md` to note the v1.1
   expansion: scenario count is now 11 (was 4), breakdown by
   target_policy is 8 `current` / 3 `prior`.
4. Update `docs/methodology.md` scenario-count references.
5. Add a short subsection to `docs/concept_v0_2.md` naming the four
   authoring rules from this file as the admission criteria for any
   future scenario.
6. Run the test suite. No new tests required unless an integration
   test asserts a specific scenario count.
7. Do **not** run `run.py`. Experiment runs are out of scope for the
   integration task.

## Coverage after v1.1

| Dimension | v1.0 scenarios | v1.1 additions |
|---|---|---|
| Object swap (hand-held) | sc-01 | — |
| Place move (room-to-room) | sc-02, sc-04 | — |
| Temporal reach-back (language anchor) | sc-03 | — |
| Visual-similarity trap | — | sc-05 |
| Without-prior-Q | — | sc-06 |
| Temporal shift (scene evolves) | — | sc-07 |
| Screen-domain swap | — | sc-08 |
| Absence / negative | — | sc-09 |
| Numeric referent | — | sc-10 |
| Object-label prior recall | — | sc-11 |

## Deferred to v1.2 or beyond

Scenarios the sub-agent flagged as useful but not fit for v1:

- **Gazpacho visual-similarity adversarial** (category-prior
  confound dominates).
- **Combined object + place shift** (two simultaneous shifts,
  violates Rule 2).
- **Pure no-Turn-1 variant** (requires a distinct runner path where
  only a prior visual frame exists with no prior user question, so
  keep out of the with-prior-Q-assuming 2-turn loop until the
  without-prior-Q runner is built).
- **Person activity shift** and **short-horizon stovetop shift**
  (G4, G5 from review). Promising but can wait until v1.2 so v1.1
  stays focused.
