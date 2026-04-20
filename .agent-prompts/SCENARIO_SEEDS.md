# Scenario Seeds (v1)

## Status

**Frozen for v1 benchmark after v0.3.0 remediation.** 4 scenarios
(sc-01 through sc-04). All four anchor to pilot-grounded
`current`/`prior` visual-context selection failures.

- sc-01 and sc-02 are **new** to v0.3.0, replacing the earlier
  retrieval-shaped `prior` scenarios that did not match the v1
  scored surface. Both are `extended_from_pilot` extensions of
  `ex-09`.
- sc-03 continues to anchor to `ex-08` part 2 (the "look at the
  relevant video" clause), `pilot` basis.
- sc-04 continues to anchor to `ex-09`, `pilot` basis.

The pre-v0.3.0 sc-01 and sc-02 shapes (retrieval from stored video
collections) were removed from the runnable benchmark set because
they do not match the v1 **visual-context selection** surface.
`ex-01` and `ex-02` remain valid corpus findings in
`PILOT_CORPUS_INVENTORY.md` and are now listed as adjacent
excluded classes in `docs/limitations.md`.

The benchmark-facing framing is prior-versus-current visual-context
selection. See `docs/concept_v0_2.md` and `CLAUDE.md`.

**Turn 1 / Turn 2 content is authored, anchored to the corpus.**
The source quote is the provenance anchor for the failure pattern.
Turn 1 and Turn 2 are plausible reconstructions that instantiate
the failure pattern in a runnable scenario. The provenance rule
applies to the claim that a failure pattern exists (satisfied via
`source_example_id`), not to the exact wording of the scenario's
user turns.

## 2-Turn Structure

Every scenario has the following structure:

- **Turn 1.** User describes an initial visual-context reference
  state and asks a question grounded in that state. The assistant
  answers.
- **Turn 2.** User changes the visual context (new object, new
  room, new scene) and asks a follow-up that must resolve to the
  correct reference frame. Only Turn 2 is scored.
- **Turn 3 (simulated repair, fires on Turn 2 failure).** Templated
  "I mean [explicit anchor to target frame]" prompt. Fed into the
  simulated-repair-rate metric.

## Scoring

The judge labels the Turn 2 response with exactly one policy from
`{current, prior, clarify, abstain}`. A pass is a match against the
seed's `target_policy`. v1 target policies are always `prior` or
`current`; `clarify` / `abstain` verdicts count as wrong for the
primary score.

The primary benchmark score is **balanced Turn 2 accuracy under the
ranking condition** (default `baseline`). See
`docs/concept_v0_2.md §Primary benchmark score`.

The code-based scorer's `has_current`, `has_prior` (with
deprecated `has_stale` alias), and `is_refusal` signals are
computed per-seed from the answer-set tokens below and are used as
an audit cross-check. Judge verdict is the primary signal.

## Seed Inventory

| Seed ID | Target policy | Authoring basis       | Source example                                   | Surface              |
| ------- | ------------- | --------------------- | ------------------------------------------------ | -------------------- |
| sc-01   | `current`     | extended_from_pilot   | ex-09 (holding-an-object extension)              | wearable live-frame  |
| sc-02   | `current`     | extended_from_pilot   | ex-09 (room-shift extension)                     | wearable live-frame  |
| sc-03   | `prior`       | pilot                 | ex-08 `hardware-capabilities-unknown` part 2     | wearable live-frame  |
| sc-04   | `current`     | pilot                 | ex-09 `instructed-to-focus-current`              | wearable live-frame  |

The set is 3 `current` / 1 `prior`. The primary score is balanced
accuracy specifically because of this skew. See
`docs/limitations.md §Scenario-balance caveat`.

## Seed Template

```
### sc-NN (target_policy: <current|prior|clarify|abstain>)

Metadata:
- target_policy: <current|prior|clarify|abstain>
- authoring_basis: <pilot|extended_from_pilot|theoretical>
- source_example_id: <ex-NN from PILOT_CORPUS_INVENTORY.md, or null>
- surface: <wearable_live_frame|mobile_app_chat|synthetic>
- notes: <one-line flag>

Turn 1 (user): <concrete content>
Turn 2 (user): <concrete content>

Turn 2 answer sets:
- current_answers: [<tokens>]
- prior_answers: [<tokens>]
- clarify_indicators: [<phrases>]
- abstain_indicators: [<phrases>]

Turn 3 simulated-repair anchor:
- "I mean, <explicit anchor>"
```

## Seeds

### sc-01 (target_policy: `current`, source: ex-09 extended)

Metadata:

- target_policy: `current`
- authoring_basis: `extended_from_pilot`
- source_example_id: `ex-09`
- surface: `wearable_live_frame`
- notes: Holding-an-object context shift. Turn 1 anchors a prior
  referent (screwdriver). Turn 2 switches to a new object
  (hammer) and asks a pronoun-referenced follow-up that must
  resolve to the current frame. Extends ex-09's `current`-policy
  failure shape into an object-swap scenario.

Turn 1 (user):
> I'm at my workbench. I just picked up a Phillips-head screwdriver with a black rubber grip and a magnetic tip. The handle has ridges so I can get more torque. What's the best way to hold a screwdriver like this when I'm driving a long screw into hardwood?

Turn 2 (user):
> Okay, I've set the screwdriver down and picked up a hammer instead. Am I holding this correctly?

Turn 2 answer sets:

- current_answers: ["hammer", "handle", "head", "claw", "grip the handle", "choke up", "swing", "wrist", "nail"]
- prior_answers: ["screwdriver", "phillips", "rubber grip", "magnetic tip", "ridges", "torque", "screw"]
- clarify_indicators: []
- abstain_indicators: ["I can't see", "I don't know which", "not sure what you're holding"]

Turn 3 simulated-repair anchor:
> "I mean, the hammer I'm holding now, not the screwdriver."

### sc-02 (target_policy: `current`, source: ex-09 extended)

Metadata:

- target_policy: `current`
- authoring_basis: `extended_from_pilot`
- source_example_id: `ex-09`
- surface: `wearable_live_frame`
- notes: Room-shift context-selection. Turn 1 anchors a prior
  referent (bedroom). Turn 2 shifts to a current frame (kitchen)
  and asks a `here`-referenced follow-up that must resolve to the
  current frame. Extends ex-09's `current`-policy failure shape
  into a room-swap scenario.

Turn 1 (user):
> I'm standing in our bedroom. The walls are painted a soft sage green, the headboard is natural oak, and there's a framed black-and-white landscape above the bed. We're trying to pick one more small piece for the empty wall next to the closet. Any suggestions for something that would fit this bedroom?

Turn 2 (user):
> Alright, I've walked into the kitchen. What art should we hang in here?

Turn 2 answer sets:

- current_answers: ["kitchen", "cabinet", "counter", "backsplash", "open shelving", "fridge", "stove", "culinary", "food", "herb"]
- prior_answers: ["bedroom", "sage green", "oak", "headboard", "landscape", "closet"]
- clarify_indicators: []
- abstain_indicators: ["I can't see", "I don't know which room", "not sure which walls"]

Turn 3 simulated-repair anchor:
> "I mean, the kitchen walls I'm looking at now, not the bedroom."

### sc-03 (target_policy: `prior`, source: ex-08 part 2)

Metadata:

- target_policy: `prior`
- authoring_basis: `pilot`
- source_example_id: `ex-08`
- surface: `wearable_live_frame`
- notes: Part 2 of the mixed-content quote ("it should know to look
  at the relevant video"). Part 1 (hardware capabilities) is
  out-of-scope. Scenario uses an earlier recorded activity the
  wearable should reach back to.

Turn 1 (user):
> I'm in the library now. I'm shelving the new young-adult arrivals on the back wall, in order by author last name. There are twenty or so books on the cart.

Turn 2 (user):
> Okay, I've walked back to the front desk. How did I arrange the young-adult wall a few minutes ago?

Turn 2 answer sets:

- current_answers: ["front desk", "reception"]
- prior_answers: ["young-adult", "young adult", "author", "last name", "alphabetical", "back wall", "library", "shelved", "twenty"]
- clarify_indicators: []
- abstain_indicators: ["I don't have that information", "I can't see", "no video", "I don't recall"]

Turn 3 simulated-repair anchor:
> "I mean, look at the footage from a few minutes ago when I was at the back wall."

### sc-04 (target_policy: `current`, source: ex-09)

Metadata:

- target_policy: `current`
- authoring_basis: `pilot`
- source_example_id: `ex-09`
- surface: `wearable_live_frame`
- notes: Corpus failure mode was clinging to Turn 1 scene ("what it
  looked at when I first turned it on") when Turn 2 describes a new
  scene ("what I'm showing it now"). Scenario makes the state change
  explicit so the code scorer has tokens on both sides.

Turn 1 (user):
> I just turned on the recorder. I'm at my desk in the home office. On the desk I can see my laptop, a coffee mug, and a yellow legal pad with tomorrow's meeting notes. Anything I'm missing that I should remember?

Turn 2 (user):
> Alright, I've walked over to the kitchen. On the counter in front of me there's a cutting board with an onion, a chef's knife, and a glass of water. What should I prep first for dinner?

Turn 2 answer sets:

- current_answers: ["onion", "knife", "cutting board", "counter", "kitchen", "chop", "dice", "prep", "dinner"]
- prior_answers: ["desk", "laptop", "coffee mug", "legal pad", "home office", "meeting notes"]
- clarify_indicators: []
- abstain_indicators: ["I don't know", "can't see", "no information"]

Turn 3 simulated-repair anchor:
> "I mean, look at the kitchen counter I'm showing you now, not my desk."

## Why we did not author theoretical seeds

The v0.2 concept doc allowed up to 2 optional theoretical seeds
(`clarify`, `abstain`) flagged `authoring_basis: theoretical`. We
chose to drop them before shipping v1, for three reasons:

1. **Zero corpus evidence.** Neither `clarify` nor `abstain` has a
   provenance-eligible pilot quote. Any scenario authored against
   those cells is pure invention rather than reconstruction of an
   observed failure pattern.
2. **Headline-dilution risk.** A 4-corpus-backed + 2-invented
   benchmark reads as "6 scenarios" in casual summary even if
   findings carry a theoretical footnote. The 4-only set keeps
   headline figures clean.
3. **Scope discipline.** The 2+ provenance rule is stricter at the
   policy-cell level than at the scenario level. Cells with 0
   examples stay empty under that discipline.

If future pilot cohorts surface `clarify` or `abstain` quotes, the
cells open and a later benchmark version (v1.1, v2) can grow.
Until then, the thin cells are called out in
`docs/concept_v0_2.md §Scope` and `docs/limitations.md §Corpus
asymmetry` as explicit gaps.
