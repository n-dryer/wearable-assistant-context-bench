# Scenario Seeds (v1)

## Status

**Frozen as of v1.** 11 scenarios (sc-01 through sc-11).
8 `current`, 3 `prior`.

sc-01 through sc-04 are the pilot-grounded core of the set. sc-05
through sc-11 extend that core with additional failure shapes
(visual similarity, without-prior-Q, temporal state change,
screen-domain swap, absence detection, quantitative swap, and
object-label prior recall).

- sc-01 and sc-02 are `extended_from_pilot` extensions of `ex-09`
  that replaced earlier retrieval-shaped `prior` scenarios.
- sc-03 anchors to `ex-08` part 2 (the "look at the relevant video"
  clause), `pilot` basis.
- sc-04 anchors to `ex-09`, `pilot` basis.
- sc-05 extends `ex-09` into a visual-similarity trap with a
  text-proxy-degraded T2.
- sc-06 is a `theoretical` scenario for the without-prior-Q soft
  case defined in `docs/concept_v0_2.md`. No pilot anchor.
- sc-07 extends `ex-09` into a temporal state-change shape.
- sc-08 extends `ex-09` into a screen-domain swap shape.
- sc-09 extends `ex-08` into an absence-detection shape with
  directional recall (the object leaves while the user stays put).
- sc-10 extends `ex-09` into a numeric/quantitative swap shape.
- sc-11 extends `ex-08` into an object-label prior-recall shape
  (label was visible, object then put away).

The pre-v0.3.0 sc-01 and sc-02 shapes (retrieval from stored video
collections) were removed from the runnable benchmark set because
they do not match the v1 **visual-context selection** surface.
`ex-01` and `ex-02` remain valid corpus findings in
`PILOT_CORPUS_INVENTORY.md` and are now listed as adjacent
excluded classes in `docs/limitations.md`.

What the benchmark measures is prior-versus-current visual-context
selection. See `docs/concept_v0_2.md` and `CLAUDE.md`.

**Turn 1 and Turn 2 text is human-authored. Each scenario reconstructs a real pilot failure pattern; the source quote is the provenance anchor, not the scenario wording itself.**
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
seed's `target_context`. v1 target policies are always `prior` or
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
| sc-05   | `current`     | extended_from_pilot   | ex-09 (visual-similarity trap extension)         | wearable live-frame  |
| sc-06   | `current`     | theoretical           | (without-prior-Q soft case, doc-grounded)        | wearable live-frame  |
| sc-07   | `current`     | extended_from_pilot   | ex-09 (temporal state-change extension)          | wearable live-frame  |
| sc-08   | `current`     | extended_from_pilot   | ex-09 (screen-domain swap extension)             | wearable live-frame  |
| sc-09   | `prior`       | extended_from_pilot   | ex-08 (absence-detection extension)              | wearable live-frame  |
| sc-10   | `current`     | extended_from_pilot   | ex-09 (numeric/quantitative swap extension)      | wearable live-frame  |
| sc-11   | `prior`       | extended_from_pilot   | ex-08 (object-label prior-recall extension)      | wearable live-frame  |

The set is 8 `current` / 3 `prior`. The primary score is balanced
accuracy specifically because of this skew. See
`docs/limitations.md §Scenario-balance caveat`.

## Seed Template

```
### sc-NN (target_context: <current|prior|clarify|abstain>)

Metadata:
- target_context: <current|prior|clarify|abstain>
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

### sc-01 (target_context: `current`, source: ex-09 extended)

Metadata:

- target_context: `current`
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

### sc-02 (target_context: `current`, source: ex-09 extended)

Metadata:

- target_context: `current`
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

### sc-03 (target_context: `prior`, source: ex-08 part 2)

Metadata:

- target_context: `prior`
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

### sc-04 (target_context: `current`, source: ex-09)

Metadata:

- target_context: `current`
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

### sc-05 (target_context: `current`, source: ex-09 extended)

Metadata:

- target_context: `current`
- authoring_basis: `extended_from_pilot`
- source_example_id: `ex-09`
- surface: `wearable_live_frame`
- text_proxy_degraded: `true`
- notes: Visual similarity trap. T1 anchors on a richly described
  first poster; T2 swaps to a second poster without verbalizing
  its visual content. Failure pattern: model carries over Lake
  Como mat advice instead of pivoting. text_proxy_degraded because
  the visual differentiation has no textual proxy in T2.
  **Authoring note for the image-enabled slice:** the second poster
  should be selected so its palette could plausibly echo Lake
  Como's, otherwise the "trap" evaporates into a pure
  unknown-content case.

Turn 1 (user):
> I'm at the framing shop. I've got two posters with me. The one on the counter is a 24x36 vintage travel poster of Lake Como — lots of saturated blue water and a cream sky. What mat color would best complement this?

Turn 2 (user):
> Holding up the second poster now. What about this one?

Turn 2 answer sets:

- current_answers: ["the second poster", "second one", "this poster", "the new poster", "the other poster", "holding up"]
- prior_answers: ["Lake Como", "blue water", "cream sky", "vintage travel", "saturated blue", "24x36"]
- clarify_indicators: ["describe the second", "what's on the second", "tell me about the other", "what does the second poster show"]
- abstain_indicators: ["I can't see", "no information"]

Turn 3 simulated-repair anchor:
> "I mean the second poster I'm holding up now, not the Lake Como one."

### sc-06 (target_context: `current`, source: without-prior-Q soft case, doc-grounded)

Metadata:

- target_context: `current`
- authoring_basis: `theoretical`
- source_example_id: null
- surface: `wearable_live_frame`
- variant: `without_prior_q_soft`
- text_proxy_degraded: `true`
- notes: Without-prior-Q soft case from `docs/concept_v0_2.md`. T1
  is descriptive without a question that requires an anchor. T2 in
  a new room asks a specifically-visual current-frame question
  that cannot be answered from world knowledge alone. Correct
  behavior is to engage with the pegboard's visible layout.
  Failure mode: model gives generic pegboard-organization advice
  instead. text_proxy_degraded because which-tools-are-missing has
  no textual proxy in T2. Theoretical because no pilot example
  anchors this shape.

Turn 1 (user):
> I'm in the back garden. The hydrangeas along the fence are in full bloom — blue, but starting to fade. Just sharing what I'm seeing.

Turn 2 (user):
> Walked into the garage. Can you tell which tools are missing from the pegboard?

Turn 2 answer sets:

- current_answers: ["the gap", "the outline", "empty hook", "empty outline", "I can see the", "looking at the board", "looking at the pegboard", "the shadow board shows", "outlined spot"]
- prior_answers: ["hydrangea", "fence", "fading blue", "garden"]
- clarify_indicators: ["describe the pegboard", "what's on the pegboard"]
- abstain_indicators: ["I can't see", "no information"]

Turn 3 simulated-repair anchor:
> "I mean, actually look at the pegboard I'm standing in front of — which tool outlines have no tool hanging on them?"

### sc-07 (target_context: `current`, source: ex-09 extended)

Metadata:

- target_context: `current`
- authoring_basis: `extended_from_pilot`
- source_example_id: `ex-09`
- surface: `wearable_live_frame`
- text_proxy_degraded: `true`
- notes: Temporal state change. Same scene after time passes. T1
  describes the pre-bake state; T2 asks a purely visual question
  about the current in-oven state. Failure pattern: model retells
  T1 pre-bake details instead of engaging with the current visual.
  The question is chosen so world knowledge (cinnamon-roll doneness
  timing) cannot substitute for actually looking.
  text_proxy_degraded because the current visual has no textual
  proxy in T2.

Turn 1 (user):
> I'm in the kitchen at 8am. I just put a sheet pan of cinnamon rolls in the oven, top shelf, 350F. They've been rising overnight and looked pillowy when I slid them in. How long should I bake them?

Turn 2 (user):
> Okay it's 8:15 now and I'm back at the oven. Something's happening in there — what do you see?

Turn 2 answer sets:

- current_answers: ["golden brown", "look at", "let me see", "puffed", "color", "tops", "what do they look like", "describe"]
- prior_answers: ["pillowy", "rising", "350", "top shelf", "overnight", "8am"]
- clarify_indicators: ["what color are they", "how do they look now", "describe their appearance"]
- abstain_indicators: ["I can't see", "no information"]

Turn 3 simulated-repair anchor:
> "I mean describe the rolls as they are in the oven right now, not how they looked before baking."

### sc-08 (target_context: `current`, source: ex-09 extended)

Metadata:

- target_context: `current`
- authoring_basis: `extended_from_pilot`
- source_example_id: `ex-09`
- surface: `wearable_live_frame`
- text_proxy_degraded: `true`
- notes: Screen-domain swap. The wearable is looking at a screen,
  not a physical scene. T1 anchors on a Jira ticket; T2 swaps to a
  different window and asks a specific scoreable question
  (incident + page?) that requires reading the new window.
  Failure pattern: model answers "yes, page" on the strength of
  the Jira P1 rather than pivoting to the new window.
  text_proxy_degraded because the new window's content has no
  textual proxy in T2.

Turn 1 (user):
> I'm at my desk staring at my monitor. I've got a bug ticket open in Jira — it's a P1 about the checkout API returning 500s on cart-update. Suggested fix says 'check the redis lock'. Worth pinging the SRE on-call?

Turn 2 (user):
> Switched windows. Is this a production incident, and should I page someone?

Turn 2 answer sets:

- current_answers: ["depends what's on", "depends on the new window", "the new window", "this window shows", "I can see this", "the window you switched to", "this is a"]
- prior_answers: ["Jira", "ticket", "redis", "SRE", "P1", "checkout API", "cart-update", "500", "page the SRE", "page on-call"]
- clarify_indicators: ["what's on the new window", "what application did you switch", "describe what you switched to"]
- abstain_indicators: ["I can't see", "no information"]

Turn 3 simulated-repair anchor:
> "I mean the window I just switched to, not the Jira ticket."

### sc-09 (target_context: `prior`, source: ex-08 extended)

Metadata:

- target_context: `prior`
- authoring_basis: `extended_from_pilot`
- source_example_id: `ex-08`
- surface: `wearable_live_frame`
- text_proxy_degraded: `true`
- notes: Absence detection with directional recall. The visual
  context shifts because the object left, not because the user
  moved. T2 asks for a specific spatial fact (which direction)
  that only the prior frame can supply; world knowledge about
  deer behavior is not sufficient. Failure pattern: model
  speculates about cover-seeking without using the prior layout,
  or pivots to the empty current frame. Extends ex-08's
  prior-recall shape into an object-departure case.
  text_proxy_degraded because the directional answer requires the
  visual layout, not just the text description.

Turn 1 (user):
> I'm in the backyard. There's a buck in the corner — white-tailed, maybe six points, just standing by the maple tree. Should I move slowly to avoid spooking him?

Turn 2 (user):
> Okay — which direction did he bolt?

Turn 2 answer sets:

- current_answers: ["the empty corner", "I don't see him", "nothing there now"]
- prior_answers: ["toward the maple", "toward the fence", "past the maple", "behind the maple", "into the tree line", "into the trees", "through the gap", "away from", "opposite", "toward the fence line", "north", "south", "east", "west"]
- clarify_indicators: []
- abstain_indicators: ["I can't see", "I didn't see him bolt", "I can't tell", "no information"]

Turn 3 simulated-repair anchor:
> "Based on what you saw before he ran."

### sc-10 (target_context: `current`, source: ex-09 extended)

Metadata:

- target_context: `current`
- authoring_basis: `extended_from_pilot`
- source_example_id: `ex-09`
- surface: `wearable_live_frame`
- text_proxy_degraded: `true`
- notes: Numeric/quantitative swap. T1 establishes a specific case
  count and weekly sell-through. T2 moves to a different pallet
  without restating the numbers. Failure pattern: model carries
  over the 12-case math to the chardonnay pallet. text_proxy_degraded
  because the new pallet's count has no textual proxy in T2.

Turn 1 (user):
> I'm at the warehouse pulling holiday stock. There are 12 cases of the cabernet on this pallet. Typical ramp says we sell about 8 cases per week through the holiday window. Should I pull more from the back?

Turn 2 (user):
> Walked over to the chardonnay pallet. Same question — should I pull more from the back?

Turn 2 answer sets:

- current_answers: ["chardonnay", "how many cases", "depends on how many", "the chardonnay pallet", "count the chardonnay", "let me know how many"]
- prior_answers: ["12 cases", "cabernet", "8 per week", "8 cases", "holiday ramp"]
- clarify_indicators: ["how many chardonnay cases", "what's the chardonnay count", "how many cases of chardonnay are on the pallet"]
- abstain_indicators: ["I can't see", "no information"]

Turn 3 simulated-repair anchor:
> "I mean the chardonnay pallet I'm standing at now, not the cabernet."

### sc-11 (target_context: `prior`, source: ex-08 extended)

Metadata:

- target_context: `prior`
- authoring_basis: `extended_from_pilot`
- source_example_id: `ex-08`
- surface: `wearable_live_frame`
- notes: Object-label prior recall. T1 verbalizes a product label
  while the object is visible; T2 asks a specific label fact after
  the object is back on the shelf. Current frame (shelf) is
  irrelevant; the answer lives in the prior frame. Failure pattern:
  model refuses or clarifies (both wrong) instead of reaching back.
  Extends ex-08's prior-recall shape into a product-label case
  that is distinct from sc-03 (library layout) and sc-09 (animal
  direction).

Turn 1 (user):
> I'm in the baby aisle. I just picked up the formula we've been trying — the label says it's 'Stage 2 infant formula, for 6 to 12 months, made with organic cow's milk, no corn syrup solids, 20 calories per fluid ounce'. Is this the right stage for my 7-month-old?

Turn 2 (user):
> I just put it back on the shelf. What did the label say the calorie count was?

Turn 2 answer sets:

- current_answers: ["the shelf", "back on the shelf", "I can't read it from here", "you put it back"]
- prior_answers: ["20 calories", "20 cal", "per fluid ounce", "stage 2", "6 to 12 months", "organic cow's milk", "no corn syrup", "organic"]
- clarify_indicators: ["show me the label again", "can I see the label"]
- abstain_indicators: ["I don't remember", "I didn't catch", "I can't recall", "no information"]

Turn 3 simulated-repair anchor:
> "Based on what you just saw on the label before I put it back."

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
cells open and a later benchmark version (v2) can grow.
Until then, the thin cells are called out in
`docs/concept_v0_2.md §Scope` and `docs/limitations.md §Corpus
asymmetry` as explicit gaps.
