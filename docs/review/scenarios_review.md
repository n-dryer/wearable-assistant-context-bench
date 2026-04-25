# Scenario Review Sheet: Wearable Assistant Context Benchmark v1

Use this file to validate each of the 50 scenarios. For each one,
read all four channels (audio + camera × Turn 1 + Turn 2), then mark the
status box and add notes if anything needs to change.

**Source-of-truth files:** `benchmark/v1/scenarios.json` and
`benchmark/v1/expected_answers.json`.

**Re-generate this file after edits:** `python scripts/generate_review_sheet.py`

---

## Bank summary

- **Scenarios:** 50
- **Target context:** abstain (2), clarify (3), current (33), prior (12)
- **Difficulty:** easy (15), hard (15), medium (20)
- **Shift types (`cue_type`):**
  - `object_in_hand`: 12
  - `object_state`: 8
  - `sequential_task`: 6
  - `location`: 6
  - `object_in_view`: 5
  - `absent_referent`: 5
  - `screen_content`: 4
  - `pre_conversation_recall`: 4
- **Activity domains (16 distinct):** kitchen (9), garden (8), workshop (7), art_craft (5), automotive (5), fitness (4), household (2), office (2), communication (1), craft (1), electronics (1), finance (1), home (1), music (1), navigation (1), sports (1)

---

## Review checklist (per scenario)

Before marking PASS, confirm:

1. **Image identifiability.** A fresh reader can identify the object from the Turn 1 image and Turn 2 image alone, no scenario context, no answer key. If not, the description is underspecified.
2. **Speech naturalness.** Turn 1 and Turn 2 user speech sound like a real person talking to a wearable. No narration of visible objects, no announcement of the shift.
3. **Hidden shift.** The context shift is visible only in the camera channel. Turn 2 user speech does not give it away.
4. **Category fit.** The scenario actually tests what its shift type (stored as `cue_type` in the data files) claims.
5. **Answer fairness.** `current_answers` and `prior_answers` cover the three vocabulary categories (object name, technique/action, state/condition). They are reasonable evidence of which context the model used.
6. **Repair anchor.** The Turn 3 repair anchor names the intended frame explicitly, so a model that missed Turn 2 has a fair shot.

Mark each scenario as **PASS**, **EDIT** (small fix needed; describe in notes), or **REPLACE** (scenario doesn't work; new one needed in same category).

---

## Table of contents

- [sc-01](#sc-01): `object_in_hand` / `current` / kitchen / easy
- [sc-02](#sc-02): `object_in_hand` / `current` / electronics / medium
- [sc-03](#sc-03): `object_in_hand` / `current` / garden / easy
- [sc-04](#sc-04): `object_in_hand` / `prior` / art_craft / medium
- [sc-05](#sc-05): `object_in_hand` / `current` / workshop / hard
- [sc-06](#sc-06): `object_in_hand` / `current` / kitchen / easy
- [sc-07](#sc-07): `object_in_hand` / `current` / sports / medium
- [sc-08](#sc-08): `object_in_hand` / `current` / automotive / hard
- [sc-09](#sc-09): `object_in_hand` / `clarify` / music / hard
- [sc-10](#sc-10): `object_in_hand` / `current` / household / medium
- [sc-11](#sc-11): `object_in_hand` / `current` / art_craft / easy
- [sc-12](#sc-12): `object_in_hand` / `prior` / garden / medium
- [sc-13](#sc-13): `object_state` / `current` / kitchen / easy
- [sc-14](#sc-14): `object_state` / `current` / garden / medium
- [sc-15](#sc-15): `object_state` / `current` / art_craft / medium
- [sc-16](#sc-16): `object_state` / `prior` / workshop / medium
- [sc-17](#sc-17): `object_state` / `current` / household / easy
- [sc-18](#sc-18): `object_state` / `current` / automotive / hard
- [sc-19](#sc-19): `object_state` / `prior` / kitchen / medium
- [sc-20](#sc-20): `object_state` / `current` / art_craft / hard
- [sc-21](#sc-21): `sequential_task` / `current` / workshop / easy
- [sc-22](#sc-22): `sequential_task` / `current` / kitchen / easy
- [sc-23](#sc-23): `sequential_task` / `current` / garden / medium
- [sc-24](#sc-24): `sequential_task` / `prior` / art_craft / medium
- [sc-25](#sc-25): `sequential_task` / `current` / automotive / hard
- [sc-26](#sc-26): `sequential_task` / `current` / fitness / hard
- [sc-27](#sc-27): `location` / `current` / home / easy
- [sc-28](#sc-28): `location` / `current` / garden / easy
- [sc-29](#sc-29): `location` / `current` / kitchen / medium
- [sc-30](#sc-30): `location` / `current` / automotive / medium
- [sc-31](#sc-31): `location` / `prior` / fitness / medium
- [sc-32](#sc-32): `location` / `clarify` / workshop / hard
- [sc-33](#sc-33): `object_in_view` / `current` / kitchen / easy
- [sc-34](#sc-34): `object_in_view` / `current` / workshop / medium
- [sc-35](#sc-35): `object_in_view` / `current` / garden / medium
- [sc-36](#sc-36): `object_in_view` / `current` / automotive / hard
- [sc-37](#sc-37): `object_in_view` / `prior` / office / hard
- [sc-38](#sc-38): `absent_referent` / `prior` / garden / medium
- [sc-39](#sc-39): `absent_referent` / `abstain` / kitchen / hard
- [sc-40](#sc-40): `absent_referent` / `current` / workshop / easy
- [sc-41](#sc-41): `absent_referent` / `clarify` / fitness / medium
- [sc-42](#sc-42): `absent_referent` / `abstain` / craft / hard
- [sc-43](#sc-43): `screen_content` / `current` / communication / easy
- [sc-44](#sc-44): `screen_content` / `current` / finance / easy
- [sc-45](#sc-45): `screen_content` / `current` / office / hard
- [sc-46](#sc-46): `screen_content` / `prior` / navigation / medium
- [sc-47](#sc-47): `pre_conversation_recall` / `prior` / kitchen / easy
- [sc-48](#sc-48): `pre_conversation_recall` / `prior` / workshop / medium
- [sc-49](#sc-49): `pre_conversation_recall` / `prior` / garden / hard
- [sc-50](#sc-50): `pre_conversation_recall` / `current` / fitness / hard

---

### sc-01

| | |
|---|---|
| **Shift type** | `object_in_hand` |
| **Target context** | `current` |
| **Activity domain** | kitchen |
| **Difficulty** | easy |
| **Cognitive load** | single_referent |
| **Time gap** | seconds |

**Turn 1, camera (`turn_1_image`):**

> Right hand loosely gripping a long cylindrical wooden shaft. Bowl-shaped wooden head at the end is dipped into a deep steel vessel of simmering red sauce on a gas burner. Steam rising.

**Turn 1, user speech (`turn_1_user`):** *"Should I keep moving this around or let it sit?"*

**Turn 2, camera (`turn_2_image`):**

> Right hand wrapped around a black molded handle attached to a long flat triangular blade with a sharpened edge. Blade is resting on a flat raised wooden slab next to a halved yellow onion. Knuckles tucked inward.

**Turn 2, user speech (`turn_2_user`):** *"Is my grip okay for this?"*

**Turn 3, repair anchor (`turn_3_repair_anchor`):** *"I mean the chef's knife I'm holding now, not the wooden spoon I was stirring with."*

**Authoring notes:** Stir to chop swap. T2 deictic asks about grip on the new object.

**Expected answers (judge-only):**

- `current_answers`: `chef's knife`, `knife`, `pinch grip`, `claw the onion`, `knuckles tucked`, `rocking motion`, `blade flat`, `sharpened edge`, `tucked fingers`
- `prior_answers`: `wooden spoon`, `spoon`, `stir gently`, `scrape the bottom`, `fold the sauce`, `bowl-shaped head`, `simmering`

**Review:**

- [ ] PASS
- [ ] EDIT
- [ ] REPLACE

**Notes:**

> _(write any review notes here)_

---

### sc-02

| | |
|---|---|
| **Shift type** | `object_in_hand` |
| **Target context** | `current` |
| **Activity domain** | electronics |
| **Difficulty** | medium |
| **Cognitive load** | single_referent |
| **Time gap** | seconds |

**Turn 1, camera (`turn_1_image`):**

> Right hand pinching a slender red plastic rod tipped with a sharp exposed thin metal point. A coiled red wire trails from the back of the rod to a yellow handheld unit on the bench with a small LCD reading numbers. The metal point is touching one leg of a small black component on a green circuit board.

**Turn 1, user speech (`turn_1_user`):** *"Am I touching the right spot here?"*

**Turn 2, camera (`turn_2_image`):**

> Right hand holding a slim cylindrical tool by its rubberized blue grip. A thin metal shaft extends from the front, ending in a wedge-shaped tip glowing faint orange. A wisp of pale smoke rises from the tip. A coil of thin silver wire sits on the bench beside an open spool.

**Turn 2, user speech (`turn_2_user`):** *"What temperature should this be at?"*

**Turn 3, repair anchor (`turn_3_repair_anchor`):** *"I mean the soldering iron I just picked up, not the multimeter probe."*

**Authoring notes:** Diagnostic to repair workflow swap. T2 asks about temp of new tool.

**Expected answers (judge-only):**

- `current_answers`: `soldering iron`, `iron`, `tin the tip`, `around 350 C`, `wedge tip`, `glowing tip`, `feed solder`, `tinned tip`
- `prior_answers`: `multimeter`, `probe`, `test lead`, `continuity check`, `measure voltage`, `touch the lead`, `sharp tip on the leg`

**Review:**

- [ ] PASS
- [ ] EDIT
- [ ] REPLACE

**Notes:**

> _(write any review notes here)_

---

### sc-03

| | |
|---|---|
| **Shift type** | `object_in_hand` |
| **Target context** | `current` |
| **Activity domain** | garden |
| **Difficulty** | easy |
| **Cognitive load** | single_referent |
| **Time gap** | seconds |

**Turn 1, camera (`turn_1_image`):**

> Gloved right hand gripping a short wooden handle attached to a curved scoop-shaped metal blade caked with damp dark soil. Blade is part-buried in a raised garden bed beside a small green seedling.

**Turn 1, user speech (`turn_1_user`):** *"How deep should I be going with this?"*

**Turn 2, camera (`turn_2_image`):**

> Gloved right hand squeezing red rubber-coated handles that pivot around a central bolt. Two curved blades meet at a point — one thicker with a flat edge, the other thin and sharpened. Blades are open around a slim green stem about a quarter-inch thick on a rose bush.

**Turn 2, user speech (`turn_2_user`):** *"Where exactly do I cut?"*

**Turn 3, repair anchor (`turn_3_repair_anchor`):** *"I mean the pruning shears I'm holding now, not the trowel I was digging with."*

**Authoring notes:** Plant to prune swap. T2 deictic about cut placement.

**Expected answers (judge-only):**

- `current_answers`: `pruning shears`, `secateurs`, `bypass pruners`, `cut at a node`, `angled cut`, `above the bud`, `outward-facing bud`, `clean cut`, `blades open`
- `prior_answers`: `trowel`, `scoop blade`, `dig a hole`, `loosen the soil`, `plant depth`, `root ball`, `buried blade`

**Review:**

- [ ] PASS
- [ ] EDIT
- [ ] REPLACE

**Notes:**

> _(write any review notes here)_

---

### sc-04

| | |
|---|---|
| **Shift type** | `object_in_hand` |
| **Target context** | `prior` |
| **Activity domain** | art_craft |
| **Difficulty** | medium |
| **Cognitive load** | single_referent |
| **Time gap** | seconds |

**Turn 1, camera (`turn_1_image`):**

> Right hand pinching a slim wooden shaft near the metal ferrule. Soft round bristle tuft loaded with thinned blue pigment, tip touching a stretched canvas with damp washes of color. A flat oval wooden surface with puddles of multiple paint colors visible to the side.

**Turn 1, user speech (`turn_1_user`):** *"How much pressure should I be putting through this?"*

**Turn 2, camera (`turn_2_image`):**

> Right hand gripping a flat wooden handle. A flexible flat metal blade with a rounded diamond shape and beveled edge extends from the handle. Blade is loaded with a thick dollop of white pigment, hovering above the same flat oval wooden surface holding multiple paint colors.

**Turn 2, user speech (`turn_2_user`):** *"What was I doing right with the one before?"*

**Turn 3, repair anchor (`turn_3_repair_anchor`):** *"I mean the brush I was using a moment ago, before I picked this up."*

**Authoring notes:** Prior reference. User explicitly asks about earlier object via temporal phrase, no naming.

**Expected answers (judge-only):**

- `current_answers`: `palette knife`, `painting knife`, `spread the paint`, `scrape`, `drag the edge`, `impasto`, `thick dollop`, `flat blade`
- `prior_answers`: `brush`, `paintbrush`, `round brush`, `load the bristles`, `light pressure`, `soft pressure`, `let the tip glide`, `thinned wash`, `damp bristles`

**Review:**

- [ ] PASS
- [ ] EDIT
- [ ] REPLACE

**Notes:**

> _(write any review notes here)_

---

### sc-05

| | |
|---|---|
| **Shift type** | `object_in_hand` |
| **Target context** | `current` |
| **Activity domain** | workshop |
| **Difficulty** | hard |
| **Cognitive load** | distractor_present |
| **Time gap** | seconds |

**Turn 1, camera (`turn_1_image`):**

> Right hand holding a yellow rectangular plastic case. A flexible silver ribbon with black markings extends from one end and stretches across a sheet of plywood, hooked at one corner. A thin yellow wooden stick with a graphite tip and a framing square sit on the wood beside it.

**Turn 1, user speech (`turn_1_user`):** *"Is this lined up right?"*

**Turn 2, camera (`turn_2_image`):**

> Right hand pressing a long aluminum rectangular bar flat on top of a partially framed wall stud. Three small glass tubes are set into the bar, each containing a yellow-green liquid with a single bubble. Center tube bubble is sitting just left of two etched lines.

**Turn 2, user speech (`turn_2_user`):** *"What does this tell me?"*

**Turn 3, repair anchor (`turn_3_repair_anchor`):** *"I mean the level I'm holding now, not the tape measure I had before."*

**Authoring notes:** Measure to plumb-check swap. Distractor objects on bench. T2 asks about reading.

**Expected answers (judge-only):**

- `current_answers`: `spirit level`, `bubble level`, `level`, `plumb`, `bubble between the lines`, `centered bubble`, `off plumb`, `vial reading`, `out of level`
- `prior_answers`: `tape measure`, `measuring tape`, `hook the end`, `pull taut`, `read the mark`, `extended ribbon`, `metal blade extended`

**Review:**

- [ ] PASS
- [ ] EDIT
- [ ] REPLACE

**Notes:**

> _(write any review notes here)_

---

### sc-06

| | |
|---|---|
| **Shift type** | `object_in_hand` |
| **Target context** | `current` |
| **Activity domain** | kitchen |
| **Difficulty** | easy |
| **Cognitive load** | single_referent |
| **Time gap** | seconds |

**Turn 1, camera (`turn_1_image`):**

> Right hand gripping a slim metal handle. A bulb of looped thin metal wires fans out from the handle, dipped into a glass bowl of pale yellow liquid with foamy peaks beginning to form on the surface.

**Turn 1, user speech (`turn_1_user`):** *"How long until this is ready?"*

**Turn 2, camera (`turn_2_image`):**

> Two hands pressing down on a long smooth wooden cylinder with tapered ends. Cylinder is rolling across a flattened circle of pale dough on a floured marble countertop. Flour dusts the wood.

**Turn 2, user speech (`turn_2_user`):** *"Am I pushing too hard?"*

**Turn 3, repair anchor (`turn_3_repair_anchor`):** *"I mean the rolling pin I'm using now, not the whisk I had in the bowl."*

**Authoring notes:** Whip to roll swap. Easy single-referent.

**Expected answers (judge-only):**

- `current_answers`: `rolling pin`, `pin`, `even pressure`, `roll from the center outward`, `quarter turn`, `light pressure`, `smooth cylinder`, `floured surface`
- `prior_answers`: `whisk`, `wire whisk`, `balloon whisk`, `soft peaks`, `stiff peaks`, `whip`, `fold air in`, `looped wires`, `foamy`

**Review:**

- [ ] PASS
- [ ] EDIT
- [ ] REPLACE

**Notes:**

> _(write any review notes here)_

---

### sc-07

| | |
|---|---|
| **Shift type** | `object_in_hand` |
| **Target context** | `current` |
| **Activity domain** | sports |
| **Difficulty** | medium |
| **Cognitive load** | single_referent |
| **Time gap** | minutes |

**Turn 1, camera (`turn_1_image`):**

> Right hand wrapped around a black overgrip on a long shaft. Oval frame at the top is strung with a tight white grid of nylon. Yellow fuzzy ball mid-air just past the strings. Green court surface and a low net visible behind.

**Turn 1, user speech (`turn_1_user`):** *"Should I follow through more?"*

**Turn 2, camera (`turn_2_image`):**

> Both hands holding two short red foam handles. A thin black braided cord loops down from each handle, sweeping past the user's feet on a rubber gym floor. The cord blurs at the bottom of its arc. Mirror on the wall behind.

**Turn 2, user speech (`turn_2_user`):** *"What's a good pace for this?"*

**Turn 3, repair anchor (`turn_3_repair_anchor`):** *"I mean the jump rope I'm using now, not the racket from earlier."*

**Authoring notes:** Court to gym swap, time gap minutes. T2 about pacing.

**Expected answers (judge-only):**

- `current_answers`: `jump rope`, `skipping rope`, `rope`, `land on the balls of the feet`, `wrist rotation`, `bounce step`, `120 turns per minute`, `small jump`, `swinging cord`
- `prior_answers`: `racket`, `tennis racket`, `follow-through`, `swing path`, `topspin`, `strung frame`, `contact point`, `racket face`

**Review:**

- [ ] PASS
- [ ] EDIT
- [ ] REPLACE

**Notes:**

> _(write any review notes here)_

---

### sc-08

| | |
|---|---|
| **Shift type** | `object_in_hand` |
| **Target context** | `current` |
| **Activity domain** | automotive |
| **Difficulty** | hard |
| **Cognitive load** | distractor_present |
| **Time gap** | minutes |

**Turn 1, camera (`turn_1_image`):**

> Right hand pressing a stubby cylindrical chrome tool against the stem of a black rubber valve sticking out of a silver alloy rim wrapped in thick black rubber. A thin number-marked plastic stick has popped out the back end of the tool. Garage floor and a scissor-shaped lifting device with a screw drive visible.

**Turn 1, user speech (`turn_1_user`):** *"Is this where it should be?"*

**Turn 2, camera (`turn_2_image`):**

> Right hand gripping a long chrome handle with a knurled ring near the head. Square drive at the end is seated into a deep socket placed over a lug nut on the same alloy rim. A tick mark on the handle barrel sits beside printed numbers.

**Turn 2, user speech (`turn_2_user`):** *"How tight do I need to go?"*

**Turn 3, repair anchor (`turn_3_repair_anchor`):** *"I mean the torque wrench I'm using now, not the pressure gauge from before."*

**Authoring notes:** Pressure check to lug tightening swap. Hard, distractor present.

**Expected answers (judge-only):**

- `current_answers`: `torque wrench`, `click-type wrench`, `spec torque`, `around 100 ft-lbs`, `star pattern`, `criss-cross pattern`, `wait for the click`, `set the value`, `knurled ring`, `lug nut`
- `prior_answers`: `tire pressure gauge`, `gauge`, `pencil gauge`, `psi reading`, `press onto the valve stem`, `extended stick`, `pop-out scale`, `valve stem`

**Review:**

- [ ] PASS
- [ ] EDIT
- [ ] REPLACE

**Notes:**

> _(write any review notes here)_

---

### sc-09

| | |
|---|---|
| **Shift type** | `object_in_hand` |
| **Target context** | `clarify` |
| **Activity domain** | music |
| **Difficulty** | hard |
| **Cognitive load** | multi_referent |
| **Time gap** | seconds |

**Turn 1, camera (`turn_1_image`):**

> Right hand pinching a small flat triangular piece of tortoiseshell-patterned plastic between thumb and index finger. Tip resting against a metal-wound string on a sunburst-finish wooden body. Other strings visible below.

**Turn 1, user speech (`turn_1_user`):** *"Am I angling this right?"*

**Turn 2, camera (`turn_2_image`):**

> Right hand half-closed in a fist obscuring most of what it holds. A thin shaft of dark wood pokes out the top of the fist between thumb and index, and a hint of soft pale fibers fans out below the pinky. Bottom of the hand is in shadow against the dark wood of the same instrument body. Could be a slim brush, could be a bow frog, could be a small wide-faced striking head — the bulk is hidden.

**Turn 2, user speech (`turn_2_user`):** *"Is this the right one for what I'm doing?"*

**Turn 3, repair anchor (`turn_3_repair_anchor`):** *"Sorry — can you ask me to show you what I'm holding before answering?"*

**Authoring notes:** Genuinely ambiguous T2 image: hand obscures most of object, multiple plausible referents. Asking is correct response.

**Expected answers (judge-only):**

- `prior_answers`: `pick`, `plectrum`, `guitar pick`, `downstroke`, `strum angle`, `edge of the pick`, `tortoiseshell`, `string contact`
- `clarify_indicators`: `which one`, `do you mean`, `can you clarify`, `could you show`, `hard to tell`, `can you open your hand`, `what are you holding`, `rotate it`, `show me the object`, `not sure what you're holding`

**Review:**

- [ ] PASS
- [ ] EDIT
- [ ] REPLACE

**Notes:**

> _(write any review notes here)_

---

### sc-10

| | |
|---|---|
| **Shift type** | `object_in_hand` |
| **Target context** | `current` |
| **Activity domain** | household |
| **Difficulty** | medium |
| **Cognitive load** | single_referent |
| **Time gap** | seconds |

**Turn 1, camera (`turn_1_image`):**

> Both hands gripping a long blue painted wooden pole. Wide bristled head at the bottom is angled across a tile kitchen floor, pushing a small pile of dust and crumbs toward a corner.

**Turn 1, user speech (`turn_1_user`):** *"Am I doing this in the right order?"*

**Turn 2, camera (`turn_2_image`):**

> Right hand high on a long aluminum pole, left hand lower. At the bottom, a thick pad of damp blue twisted strands sits in a pool of soapy water on the same tile floor. A yellow bucket with a wringer attachment is two steps away.

**Turn 2, user speech (`turn_2_user`):** *"How wet should this be?"*

**Turn 3, repair anchor (`turn_3_repair_anchor`):** *"I mean the mop I have now, not the broom from before."*

**Authoring notes:** Sweep to mop sequence swap. T2 deictic about saturation.

**Expected answers (judge-only):**

- `current_answers`: `mop`, `string mop`, `wet mop`, `wring out`, `damp not soaking`, `figure-eight motion`, `wrung`, `twisted strands`, `soapy pad`
- `prior_answers`: `broom`, `sweep`, `short strokes`, `push the pile`, `corner first`, `bristled head`, `dust pile`

**Review:**

- [ ] PASS
- [ ] EDIT
- [ ] REPLACE

**Notes:**

> _(write any review notes here)_

---

### sc-11

| | |
|---|---|
| **Shift type** | `object_in_hand` |
| **Target context** | `current` |
| **Activity domain** | art_craft |
| **Difficulty** | easy |
| **Cognitive load** | single_referent |
| **Time gap** | seconds |

**Turn 1, camera (`turn_1_image`):**

> Right hand holding a slim hexagonal yellow-painted wooden shaft. Sharpened black tip touching a piece of cream-colored sketch paper, with light gray construction lines fanning out from a vanishing point.

**Turn 1, user speech (`turn_1_user`):** *"Should I press harder for these lines?"*

**Turn 2, camera (`turn_2_image`):**

> Right hand pinching a soft gray lump shaped like a flattened pyramid. Surface is smudged darker on the working face. Lump is pressed against the sketch paper, lifting away faint gray marks. Crumbs of darker material flake off where it touched.

**Turn 2, user speech (`turn_2_user`):** *"How do I use this without messing up the page?"*

**Turn 3, repair anchor (`turn_3_repair_anchor`):** *"I mean the kneaded eraser I'm holding, not the pencil."*

**Authoring notes:** Draw to lift swap. T2 deictic.

**Expected answers (judge-only):**

- `current_answers`: `kneaded eraser`, `eraser`, `putty eraser`, `dab the marks`, `press and lift`, `shape it to a point`, `lift graphite`, `no rubbing`, `soft gray lump`
- `prior_answers`: `pencil`, `graphite pencil`, `light pressure`, `construction lines`, `sharpened tip`, `vanishing point`, `hexagonal shaft`

**Review:**

- [ ] PASS
- [ ] EDIT
- [ ] REPLACE

**Notes:**

> _(write any review notes here)_

---

### sc-12

| | |
|---|---|
| **Shift type** | `object_in_hand` |
| **Target context** | `prior` |
| **Activity domain** | garden |
| **Difficulty** | medium |
| **Cognitive load** | single_referent |
| **Time gap** | minutes |

**Turn 1, camera (`turn_1_image`):**

> Right hand tilting a large green plastic vessel by a curved top handle. A long narrow spout with a perforated rose at the end is angled over a tray of small herb seedlings. A steady wide shower of water falls onto the soil.

**Turn 1, user speech (`turn_1_user`):** *"Am I giving these enough?"*

**Turn 2, camera (`turn_2_image`):**

> Right hand gripping a clear plastic bottle by a pistol-grip trigger. A short nozzle protrudes from the top, releasing a fine cone-shaped mist over the leaves of a tomato plant. Droplets clinging to the underside of the leaves.

**Turn 2, user speech (`turn_2_user`):** *"What was the right amount with the one I had earlier?"*

**Turn 3, repair anchor (`turn_3_repair_anchor`):** *"I mean the watering can from earlier, not what I have in my hand now."*

**Authoring notes:** Prior reference via temporal phrasing. T2 explicitly asks about earlier object.

**Expected answers (judge-only):**

- `current_answers`: `spray bottle`, `mister`, `fine mist`, `cone spray`, `even coverage`, `underside of the leaves`, `trigger spray`, `fine cone`
- `prior_answers`: `watering can`, `can`, `soak the soil`, `water at the base`, `deep watering`, `until it drains`, `perforated rose`, `wide shower`, `rose head`

**Review:**

- [ ] PASS
- [ ] EDIT
- [ ] REPLACE

**Notes:**

> _(write any review notes here)_

---

### sc-13

| | |
|---|---|
| **Shift type** | `object_state` |
| **Target context** | `current` |
| **Activity domain** | kitchen |
| **Difficulty** | easy |
| **Cognitive load** | single_referent |
| **Time gap** | minutes |

**Turn 1, camera (`turn_1_image`):**

> Tall stainless steel cylindrical vessel with a thin handle, sitting on a black glass cooktop. Clear liquid filling roughly two-thirds of the interior, surface flat and still. Faint wisps of vapor near the rim. A small red indicator light glows beside the burner.

**Turn 1, user speech (`turn_1_user`):** *"How long should this take?"*

**Turn 2, camera (`turn_2_image`):**

> Tall stainless steel cylindrical vessel with a thin handle on the same black glass cooktop. Surface of the liquid churning with large bubbles breaking continuously across the entire surface. Dense steam rising in a thick column. Droplets visible on the inside of the rim.

**Turn 2, user speech (`turn_2_user`):** *"Can I add the noodles yet?"*

**Turn 3, repair anchor (`turn_3_repair_anchor`):** *"I mean right now, looking at what's happening in the vessel in front of me."*

**Authoring notes:** Water heating from quiet to a full rolling boil. T2 user asks about adding pasta or eggs without naming the change.

**Expected answers (judge-only):**

- `current_answers`: `pot`, `boiling`, `rolling boil`, `drop them in`, `add the pasta`, `go ahead`, `ready to cook`, `fully boiling`, `vigorous boil`
- `prior_answers`: `kettle`, `heating up`, `not boiling yet`, `still warming`, `barely steaming`, `early stage`, `give it more time`, `below boiling`

**Review:**

- [ ] PASS
- [ ] EDIT
- [ ] REPLACE

**Notes:**

> _(write any review notes here)_

---

### sc-14

| | |
|---|---|
| **Shift type** | `object_state` |
| **Target context** | `current` |
| **Activity domain** | garden |
| **Difficulty** | medium |
| **Cognitive load** | single_referent |
| **Time gap** | next_day |

**Turn 1, camera (`turn_1_image`):**

> Small black plastic tray with twelve square cells filled with dark brown soil. Surface of each cell smooth and undisturbed. A few cells show a faint mound where the soil has been pressed back. No green visible. Tray sitting under a clip-on grow light.

**Turn 1, user speech (`turn_1_user`):** *"Did I plant these too deep?"*

**Turn 2, camera (`turn_2_image`):**

> Same black plastic twelve-cell tray under the same clip-on grow light. Pale green stems roughly an inch tall rising out of most cells, each topped by two narrow oval leaves. A couple of cells show stems bent sideways and leaning toward the light source. Soil surface dimpled where stems emerged.

**Turn 2, user speech (`turn_2_user`):** *"Should I move the lamp?"*

**Turn 3, repair anchor (`turn_3_repair_anchor`):** *"I'm asking about what I can see right now in the tray, with what's coming up."*

**Authoring notes:** Seeds in soil have germinated and now show seedlings with cotyledons. T2 question is about leggy growth toward the light.

**Expected answers (judge-only):**

- `current_answers`: `seedlings`, `sprouts`, `cotyledons`, `leggy`, `lower the light`, `bring the lamp closer`, `stretching toward`, `thin pale stems`, `two seed leaves`, `germinated`
- `prior_answers`: `seeds`, `freshly sown`, `haven't sprouted`, `wait for germination`, `still buried`, `untouched soil`, `before emergence`, `no growth yet`

**Review:**

- [ ] PASS
- [ ] EDIT
- [ ] REPLACE

**Notes:**

> _(write any review notes here)_

---

### sc-15

| | |
|---|---|
| **Shift type** | `object_state` |
| **Target context** | `current` |
| **Activity domain** | art_craft |
| **Difficulty** | medium |
| **Cognitive load** | single_referent |
| **Time gap** | hours |

**Turn 1, camera (`turn_1_image`):**

> Rectangular wooden panel laid flat on a drop cloth. A glossy navy coating covers the surface, light reflecting off it in long sharp streaks. Small ridges from a foam applicator visible across the finish. A bead of liquid pooling at one edge.

**Turn 1, user speech (`turn_1_user`):** *"Did I lay it on too thick?"*

**Turn 2, camera (`turn_2_image`):**

> Same rectangular wooden panel on the same drop cloth. Surface now matte and uniform, with the foam-applicator ridges still faintly visible but no longer reflective. The pooled edge has flattened. A fingertip pressed lightly at one corner leaves no print.

**Turn 2, user speech (`turn_2_user`):** *"Can I do another pass?"*

**Turn 3, repair anchor (`turn_3_repair_anchor`):** *"I mean as it is now, looking at how the surface feels at this point."*

**Authoring notes:** Latex or alkyd paint has dried from wet glossy to matte tack-free. T2 question is about recoating.

**Expected answers (judge-only):**

- `current_answers`: `paint`, `dry`, `tack-free`, `recoat`, `second coat`, `lightly sand`, `ready for another coat`, `cured enough`, `matte and set`
- `prior_answers`: `wet paint`, `still wet`, `let it dry`, `leveling out`, `wait`, `drips`, `glossy and soft`, `not ready`

**Review:**

- [ ] PASS
- [ ] EDIT
- [ ] REPLACE

**Notes:**

> _(write any review notes here)_

---

### sc-16

| | |
|---|---|
| **Shift type** | `object_state` |
| **Target context** | `prior` |
| **Activity domain** | workshop |
| **Difficulty** | medium |
| **Cognitive load** | single_referent |
| **Time gap** | minutes |

**Turn 1, camera (`turn_1_image`):**

> Long rectangular plank clamped to a workbench. Surface rough and fibrous with visible parallel kerf marks running across the grain. Small splinters lifted along one edge. Sawdust scattered in a fine layer along the length. A thin graphite line marked across the middle.

**Turn 1, user speech (`turn_1_user`):** *"Where do I start with this?"*

**Turn 2, camera (`turn_2_image`):**

> Same rectangular plank on the same workbench. Surface now smooth and even, grain visible as long parallel lines, no kerf marks remaining. Edges crisp and free of splinters. A light haze of fine dust on the surface. Thin graphite line still faintly visible.

**Turn 2, user speech (`turn_2_user`):** *"What grit was I starting from again?"*

**Turn 3, repair anchor (`turn_3_repair_anchor`):** *"I mean back at the beginning, before I did any of this — what grit did I start with?"*

**Authoring notes:** Wood before sanding (rough, saw marks) vs after sanding (smooth). T2 asks about the prior starting condition to recall grit.

**Expected answers (judge-only):**

- `current_answers`: `smooth`, `fine grit`, `220`, `180`, `finish sanding`, `ready for stain`, `polished surface`, `light final pass`, `tack cloth`
- `prior_answers`: `board`, `lumber`, `rough`, `coarse grit`, `60`, `80`, `saw marks`, `splinters`, `knock down the rough`, `heavy stock removal`, `raw cut surface`

**Review:**

- [ ] PASS
- [ ] EDIT
- [ ] REPLACE

**Notes:**

> _(write any review notes here)_

---

### sc-17

| | |
|---|---|
| **Shift type** | `object_state` |
| **Target context** | `current` |
| **Activity domain** | household |
| **Difficulty** | easy |
| **Cognitive load** | single_referent |
| **Time gap** | minutes |

**Turn 1, camera (`turn_1_image`):**

> Short cylindrical white wax shape sitting in a clear glass holder on a wooden side table. Top surface flat and smooth, with a straight upright cotton string at the center, bright white and stiff. No flame. Surrounding wax pristine.

**Turn 1, user speech (`turn_1_user`):** *"Should I trim this first?"*

**Turn 2, camera (`turn_2_image`):**

> Same white cylindrical wax shape in the same clear glass holder on the same wooden side table. A small steady teardrop flame at the top of the cotton string, which is now blackened and curled at the tip. A shallow circular pool of clear melted wax surrounds the string, extending almost to the outer edge.

**Turn 2, user speech (`turn_2_user`):** *"Is it good to leave for now?"*

**Turn 3, repair anchor (`turn_3_repair_anchor`):** *"Looking at it as it is right now, with what's happening at the top, can I leave it?"*

**Authoring notes:** Candle unlit with full straight wick vs lit candle with full melt pool. T2 asks if it can be left burning unattended or extinguished.

**Expected answers (judge-only):**

- `current_answers`: `candle`, `lit`, `burning`, `full melt pool`, `let it keep burning`, `safe to leave a bit longer`, `even burn established`, `flame is steady`, `do not blow out yet`
- `prior_answers`: `wick`, `trim the wick`, `before lighting`, `quarter inch`, `unlit`, `fresh wick`, `trim before you light`, `new candle`

**Review:**

- [ ] PASS
- [ ] EDIT
- [ ] REPLACE

**Notes:**

> _(write any review notes here)_

---

### sc-18

| | |
|---|---|
| **Shift type** | `object_state` |
| **Target context** | `current` |
| **Activity domain** | automotive |
| **Difficulty** | hard |
| **Cognitive load** | distractor_present |
| **Time gap** | hours |

**Turn 1, camera (`turn_1_image`):**

> Black rubber circular form filling the arched cutout of a parked sedan's body, viewed from a low angle on asphalt. Sidewall fully rounded, tread blocks evenly spaced and lifted clear of the ground. A small brass valve stem with a black cap sticks out from the rim. Slight gap between the bottom of the rubber and the pavement is uniform on either side of the contact patch.

**Turn 1, user speech (`turn_1_user`):** *"What pressure should I be running?"*

**Turn 2, camera (`turn_2_image`):**

> Same black rubber circular form in the same arched body cutout, same low angle. Sidewall now visibly bulged outward at the bottom, with a noticeable curve where the rubber meets the pavement. Contact patch widened, tread blocks splayed. The brass valve stem is at an angle, cap missing. A faint hissing sound suggested by a thin trail of dust drifting near the valve.

**Turn 2, user speech (`turn_2_user`):** *"What do I do here?"*

**Turn 3, repair anchor (`turn_3_repair_anchor`):** *"Looking at the wheel right now, what should I actually do?"*

**Authoring notes:** Tire properly inflated vs significantly underinflated/leaking. Hard because T1 already discusses pressure, so the model must catch the visible state shift to underinflation/leak.

**Expected answers (judge-only):**

- `current_answers`: `tire`, `flat`, `low`, `underinflated`, `leak`, `do not drive on it`, `pull the valve core`, `spare`, `patch`, `plug`, `call roadside`, `bulging sidewall`
- `prior_answers`: `psi`, `recommended pressure`, `door placard`, `32 psi`, `35 psi`, `properly inflated`, `check the placard`, `manufacturer spec`, `fully seated`

**Review:**

- [ ] PASS
- [ ] EDIT
- [ ] REPLACE

**Notes:**

> _(write any review notes here)_

---

### sc-19

| | |
|---|---|
| **Shift type** | `object_state` |
| **Target context** | `prior` |
| **Activity domain** | kitchen |
| **Difficulty** | medium |
| **Cognitive load** | single_referent |
| **Time gap** | hours |

**Turn 1, camera (`turn_1_image`):**

> Rounded pale beige mass sitting in the bottom of a large oiled glass bowl on a kitchen counter. Surface smooth and taut, occupying about a third of the bowl's interior. A clean tea towel draped over the top, partially pulled back. A faint smell of yeast suggested by a small bowl of flour beside it.

**Turn 1, user speech (`turn_1_user`):** *"How long does it usually need?"*

**Turn 2, camera (`turn_2_image`):**

> Same large glass bowl on the same kitchen counter. The pale mass now fills the bowl nearly to the rim, surface domed and slightly cracked, with visible round air pockets pressing against the glass on the sides. Tea towel pushed up at the center. A finger indentation near the edge slowly springing back about halfway.

**Turn 2, user speech (`turn_2_user`):** *"What was the original size on this when I started?"*

**Turn 3, repair anchor (`turn_3_repair_anchor`):** *"I'm asking about back at the start, before any of this happened — how much was there originally?"*

**Authoring notes:** Bread or pizza dough before and after first proof. T2 asks about the starting volume to figure out if it has fully doubled.

**Expected answers (judge-only):**

- `current_answers`: `doubled`, `fully proofed`, `ready to shape`, `punch down`, `second proof`, `well risen`, `domed top`, `poke test springs back halfway`
- `prior_answers`: `dough`, `ball`, `before rising`, `third of the bowl`, `half the volume`, `starting size`, `after the first knead`, `initial mass`, `pre-proof volume`, `tight smooth ball`

**Review:**

- [ ] PASS
- [ ] EDIT
- [ ] REPLACE

**Notes:**

> _(write any review notes here)_

---

### sc-20

| | |
|---|---|
| **Shift type** | `object_state` |
| **Target context** | `current` |
| **Activity domain** | art_craft |
| **Difficulty** | hard |
| **Cognitive load** | single_referent |
| **Time gap** | hours |

**Turn 1, camera (`turn_1_image`):**

> Cylindrical gray-brown lump on a canvas-covered rotating disc, roughly the size of a fist. Surface glistening wet, with thumb impressions pressed into the top. A thin film of slip pooled at the base. A wire tool and a wooden rib resting on the surrounding splash basin beside it.

**Turn 1, user speech (`turn_1_user`):** *"Am I ready to start pulling this?"*

**Turn 2, camera (`turn_2_image`):**

> Same canvas-covered rotating disc, same wire tool and wooden rib beside the splash basin. The form now stands upright as a tall narrow vessel with even walls, no longer glossy but uniformly matte gray. Surface holds a fingerprint without smearing. A faint hairline visible at the rim. Slight cool sheen rather than wet shine.

**Turn 2, user speech (`turn_2_user`):** *"Time to bring out the trimming tool?"*

**Turn 3, repair anchor (`turn_3_repair_anchor`):** *"I'm asking based on what it's like to the touch right now, not how it was earlier."*

**Authoring notes:** Clay freshly centered and wet vs leather-hard, ready to trim. Hard tier because both states involve clay vocabulary in adjacent stages.

**Expected answers (judge-only):**

- `current_answers`: `leather hard`, `ready to trim`, `trim the foot`, `matte surface`, `holds a fingerprint`, `stiffened up`, `good for trimming`, `no longer plastic`, `carve detail`
- `prior_answers`: `clay`, `centered`, `wet clay`, `pull the walls`, `open it up`, `throw the form`, `plastic stage`, `still wet`, `soft and workable`, `wedged ball`

**Review:**

- [ ] PASS
- [ ] EDIT
- [ ] REPLACE

**Notes:**

> _(write any review notes here)_

---

### sc-21

| | |
|---|---|
| **Shift type** | `sequential_task` |
| **Target context** | `current` |
| **Activity domain** | workshop |
| **Difficulty** | easy |
| **Cognitive load** | single_referent |
| **Time gap** | minutes |

**Turn 1, camera (`turn_1_image`):**

> Rectangular pine board resting across two sawhorses. A rectangular block wrapped in gritty paper held in a hand, sliding lengthwise across the board's surface in repeated passes. Fine pale powder collecting along the grain, the surface slightly hazy where the block has passed. Bare wood otherwise.

**Turn 1, user speech (`turn_1_user`):** *"Should I keep going over this same area?"*

**Turn 2, camera (`turn_2_image`):**

> Same pine board on the same sawhorses, the surface now uniformly even and dust-free. A flat row of stiff bristles attached to a wooden handle dipped into an open metal can of dark amber liquid. The bristled tool pulled across the board lengthwise, a glistening trail following behind it, the wood turning a richer brown tone where the liquid has been laid down.

**Turn 2, user speech (`turn_2_user`):** *"Am I doing this evenly enough?"*

**Turn 3, repair anchor (`turn_3_repair_anchor`):** *"I mean what I'm putting on the wood right now, not the smoothing I did before."*

**Authoring notes:** Sequential workshop task. T1 sanding step. T2 staining/finishing step. Same board, different step.

**Expected answers (judge-only):**

- `current_answers`: `stain`, `staining`, `finish`, `brush`, `applicator`, `wipe with the grain`, `long even strokes`, `wet edge`, `soak in`, `wet streak`, `darkening grain`, `absorbed`, `saturated`
- `prior_answers`: `sanding`, `sandpaper`, `sanding block`, `back and forth`, `even pressure`, `with the grain`, `smoothed surface`, `fine dust`, `scratch pattern`

**Review:**

- [ ] PASS
- [ ] EDIT
- [ ] REPLACE

**Notes:**

> _(write any review notes here)_

---

### sc-22

| | |
|---|---|
| **Shift type** | `sequential_task` |
| **Target context** | `current` |
| **Activity domain** | kitchen |
| **Difficulty** | easy |
| **Cognitive load** | single_referent |
| **Time gap** | minutes |

**Turn 1, camera (`turn_1_image`):**

> Flat raised wooden slab on a countertop. A halved white bulb resting cut-side down, papery skin peeled back at the edges. A long flat triangular blade with a black handle angled down on the bulb, fingertips of one hand tucked back holding the bulb steady, the other hand pressing the spine of the blade. Thin pale crescents fanning out next to the bulb.

**Turn 1, user speech (`turn_1_user`):** *"Are these uniform enough?"*

**Turn 2, camera (`turn_2_image`):**

> A wide round metal vessel with a flat bottom and low sloping sides, sitting on a lit gas ring with blue flames visible underneath. Translucent slices spread across the bottom in a thin layer of shimmering oil, edges starting to soften and turn golden in spots. A long wooden utensil with a flat angled end pushing the pieces around inside.

**Turn 2, user speech (`turn_2_user`):** *"Am I keeping it moving enough?"*

**Turn 3, repair anchor (`turn_3_repair_anchor`):** *"I mean what's on the heat right now, not the cutting before."*

**Authoring notes:** Sequential kitchen task. T1 dicing onion. T2 sautéing onion. Same ingredient, next step.

**Expected answers (judge-only):**

- `current_answers`: `sauté`, `sautéing`, `frying`, `skillet`, `pan`, `stir`, `stirring`, `medium heat`, `translucent`, `golden`, `softening`, `caramelize`, `even browning`, `keep them moving`, `spread in a single layer`
- `prior_answers`: `dicing`, `slicing`, `chopping`, `knife`, `chef's knife`, `claw grip`, `even slices`, `uniform pieces`, `rocking motion`, `consistent thickness`

**Review:**

- [ ] PASS
- [ ] EDIT
- [ ] REPLACE

**Notes:**

> _(write any review notes here)_

---

### sc-23

| | |
|---|---|
| **Shift type** | `sequential_task` |
| **Target context** | `current` |
| **Activity domain** | garden |
| **Difficulty** | medium |
| **Cognitive load** | single_referent |
| **Time gap** | minutes |

**Turn 1, camera (`turn_1_image`):**

> Patch of dark brown soil in a garden bed. A long-handled tool with a pointed metal blade pushed partway into the ground, hand on the wooden handle pressing down with a foot on the upper edge of the blade. A small mound of loose dirt piled to one side, a shallow opening forming in the ground.

**Turn 1, user speech (`turn_1_user`):** *"Is this deep enough?"*

**Turn 2, camera (`turn_2_image`):**

> Same garden bed, the opening now a clean rounded cavity. A small leafy green shoot with white roots wrapped in a tangled clump of dirt held just above the cavity, hand cradling the root mass from below. Loose soil piled to one side.

**Turn 2, user speech (`turn_2_user`):** *"Am I positioning this right?"*

**Turn 3, repair anchor (`turn_3_repair_anchor`):** *"I mean what I'm holding now, not the part before with the dirt."*

**Authoring notes:** Sequential garden task. T1 digging the hole. T2 placing the seedling. Same bed, sequential step.

**Expected answers (judge-only):**

- `current_answers`: `seedling`, `transplant`, `plant`, `root ball`, `set the crown level`, `loosen the roots`, `center it`, `soil line`, `backfill`, `root flare`, `tease apart roots`, `settle into the hole`
- `prior_answers`: `digging`, `shovel`, `spade`, `step on the blade`, `lever the dirt`, `hole depth`, `loosened soil`, `twice as wide`, `pile beside`

**Review:**

- [ ] PASS
- [ ] EDIT
- [ ] REPLACE

**Notes:**

> _(write any review notes here)_

---

### sc-24

| | |
|---|---|
| **Shift type** | `sequential_task` |
| **Target context** | `prior` |
| **Activity domain** | art_craft |
| **Difficulty** | medium |
| **Cognitive load** | single_referent |
| **Time gap** | minutes |

**Turn 1, camera (`turn_1_image`):**

> Sheet of cream-colored paper on a tilted board. A slim hexagonal wooden stick with a sharpened dark gray tip held between fingers, light feathery marks forming the rough outline of a face on the paper. Faint crosshatch reference lines across the cheekbones, soft smudges from a fingertip blending shadows.

**Turn 1, user speech (`turn_1_user`):** *"Does this look balanced so far?"*

**Turn 2, camera (`turn_2_image`):**

> Same sheet, the earlier marks now visible underneath. A slender black tube with a small pointed metal tip at one end held vertically over the paper, a dark shiny stroke being laid down along one of the previous gray marks. Small open glass bottle of black liquid nearby, a folded cloth with dark stains beside it.

**Turn 2, user speech (`turn_2_user`):** *"Was what I had laid down underneath actually balanced before I committed to this?"*

**Turn 3, repair anchor (`turn_3_repair_anchor`):** *"I mean the rough marks I put down first, not what I'm going over now."*

**Authoring notes:** Sequential art_craft task. T1 pencil sketching. T2 inking over the sketch. T2 user explicitly references the earlier step (prior target).

**Expected answers (judge-only):**

- `current_answers`: `inking`, `ink`, `dip pen`, `nib`, `line weight`, `follow the guideline`, `steady stroke`, `let it dry`, `wet ink`, `glossy line`, `trace over`
- `prior_answers`: `sketch`, `sketching`, `pencil`, `graphite`, `proportions`, `facial proportions`, `rule of thirds`, `loose construction lines`, `guidelines`, `feathery strokes`, `light underdrawing`, `blocked-in features`

**Review:**

- [ ] PASS
- [ ] EDIT
- [ ] REPLACE

**Notes:**

> _(write any review notes here)_

---

### sc-25

| | |
|---|---|
| **Shift type** | `sequential_task` |
| **Target context** | `current` |
| **Activity domain** | automotive |
| **Difficulty** | hard |
| **Cognitive load** | distractor_present |
| **Time gap** | minutes |

**Turn 1, camera (`turn_1_image`):**

> Side of a sedan parked on a flat concrete driveway. A black rubber-treaded ring on a metal hub with five hexagonal fasteners arranged in a circle around the central cap. A long heavy metal bar with a deep socket fitted on the end of one of the fasteners, hands gripping the far end of the bar pulling it to the left, body weight leaning into it. The rubber pressed flat against the concrete.

**Turn 1, user speech (`turn_1_user`):** *"Am I pulling this the right way?"*

**Turn 2, camera (`turn_2_image`):**

> Same sedan, same side. A red squat mechanical device with a flat saddle on top, positioned under a reinforced metal seam along the underside of the car behind the front arched body cutout, a long thin rod extending out from the body of the device. Hand pumping the rod up and down. The car's body visibly lifted a few inches above the concrete on this side, the rubber-treaded ring just barely touching the surface. The hexagonal fasteners on the spinning hub now loose in their seats but still threaded.

**Turn 2, user speech (`turn_2_user`):** *"Am I getting this in the right spot?"*

**Turn 3, repair anchor (`turn_3_repair_anchor`):** *"I mean what's lifting the car now, not the loosening part before."*

**Authoring notes:** Sequential automotive task. T1 breaking lug nuts loose with breaker bar while wheel on ground. T2 raising the car with a floor jack. Same wheel/car, sequential step. Distractor: lug nuts still visible in T2 image but not the focus.

**Expected answers (judge-only):**

- `current_answers`: `jack`, `floor jack`, `jacking point`, `frame rail`, `pinch weld`, `lift point`, `raise the vehicle`, `stable contact`, `pump the handle`, `off the ground`, `jack stand`
- `prior_answers`: `lug nuts`, `lug wrench`, `breaker bar`, `loosen`, `break loose`, `counterclockwise`, `lefty loosey`, `torque`, `crack them loose`, `wheel on the ground`

**Review:**

- [ ] PASS
- [ ] EDIT
- [ ] REPLACE

**Notes:**

> _(write any review notes here)_

---

### sc-26

| | |
|---|---|
| **Shift type** | `sequential_task` |
| **Target context** | `current` |
| **Activity domain** | fitness |
| **Difficulty** | hard |
| **Cognitive load** | single_referent |
| **Time gap** | minutes |

**Turn 1, camera (`turn_1_image`):**

> A person seated on a rubber mat in a gym, one leg extended out straight in front, the other folded inward with the sole of the foot against the inner thigh. Torso bent forward over the straight leg, fingertips touching the front of the foot, head tucked toward the knee. Held steady, no movement. A long metal rod with weighted disks on each end resting horizontally on a tall vertical stand in the background.

**Turn 1, user speech (`turn_1_user`):** *"Am I holding this long enough?"*

**Turn 2, camera (`turn_2_image`):**

> Same gym, mat now empty. The same long metal rod with weighted disks on each end now lifted off the stand, resting across the upper back of the shoulders just below the neck. Feet planted slightly wider than hip-width on the floor, knees bent outward over the toes, the lower body sunk down so the upper thighs are roughly horizontal. Torso angled forward, spine straight. The rod visibly bowing slightly under the load on each end.

**Turn 2, user speech (`turn_2_user`):** *"Does this look like the right position?"*

**Turn 3, repair anchor (`turn_3_repair_anchor`):** *"I mean what I'm doing under the bar right now, not the floor work before."*

**Authoring notes:** Sequential fitness task. T1 hamstring stretch as warmup. T2 weighted back squat. Same workout sequence, progressed step.

**Expected answers (judge-only):**

- `current_answers`: `squat`, `back squat`, `barbell`, `loaded bar`, `knees track over toes`, `hips back`, `neutral spine`, `brace your core`, `drive through the heels`, `depth`, `parallel`, `hip crease below the knee`
- `prior_answers`: `stretch`, `stretching`, `hamstring stretch`, `seated forward fold`, `warm-up`, `warmup`, `hold for thirty seconds`, `static stretch`, `reach toward the toes`, `hinge from the hips`

**Review:**

- [ ] PASS
- [ ] EDIT
- [ ] REPLACE

**Notes:**

> _(write any review notes here)_

---

### sc-27

| | |
|---|---|
| **Shift type** | `location` |
| **Target context** | `current` |
| **Activity domain** | home |
| **Difficulty** | easy |
| **Cognitive load** | single_referent |
| **Time gap** | minutes |

**Turn 1, camera (`turn_1_image`):**

> Wide view of a low-ceiling room. Soft carpet underfoot. A long rectangular upholstered platform along one wall, raised about knee height, covered in layered folded cloth and several soft padded rectangles at one end. Curtains drawn over a single window. Dim warm lamp on a low side table. A tall freestanding cabinet with hanging garments visible behind a slightly open hinged door.

**Turn 1, user speech (`turn_1_user`):** *"Should I open the window in here for a bit?"*

**Turn 2, camera (`turn_2_image`):**

> Wide view of a smaller room with bright overhead fluorescent lighting. Glossy tiled walls in pale blue. A deep ceramic basin set into a long counter with a tall arched metal spout. A wide rectangular reflective panel above the counter. A folded white cloth hangs from a metal rod on the side wall. Floor of small mosaic tiles.

**Turn 2, user speech (`turn_2_user`):** *"Should I open the window in here for a bit?"*

**Turn 3, repair anchor (`turn_3_repair_anchor`):** *"I mean the room I'm standing in right now, not the one with the bed."*

**Authoring notes:** Bedroom -> bathroom shift. Same ventilation question, but answer depends on current humid tiled space.

**Expected answers (judge-only):**

- `current_answers`: `bathroom`, `vent the steam`, `run the fan`, `let the moisture out`, `humid`, `after a shower`, `exhaust fan`, `tiled space`, `mirror is fogged`
- `prior_answers`: `bedroom`, `air the sheets`, `let in fresh air for sleeping`, `before bed`, `stuffy bedding`, `carpeted room`, `draw the curtains back`

**Review:**

- [ ] PASS
- [ ] EDIT
- [ ] REPLACE

**Notes:**

> _(write any review notes here)_

---

### sc-28

| | |
|---|---|
| **Shift type** | `location` |
| **Target context** | `current` |
| **Activity domain** | garden |
| **Difficulty** | easy |
| **Cognitive load** | single_referent |
| **Time gap** | minutes |

**Turn 1, camera (`turn_1_image`):**

> Outdoor wide view. Soft soil in long raised wooden beds. Green leafy plants in rows, some climbing up wooden stakes. A coiled length of long flexible green tubing rests on a flagstone path. Bright midday sun overhead casting hard shadows. A wheelbarrow with a metal tray sits at the edge of the path.

**Turn 1, user speech (`turn_1_user`):** *"Is it a good time to be doing this?"*

**Turn 2, camera (`turn_2_image`):**

> Indoor wide view. Concrete floor with oil stains. Pegboard wall with hanging metal hand tools in silhouette. A long workbench with a heavy metal clamping fixture — two parallel jaws and a horizontal screw handle — mounted at one end. A vehicle's front bumper visible at the right edge of frame. Single bare bulb overhead. Daylight only weakly entering through a small high window.

**Turn 2, user speech (`turn_2_user`):** *"Is it a good time to be doing this?"*

**Turn 3, repair anchor (`turn_3_repair_anchor`):** *"I mean the work I'd be doing in here, not the gardening outside."*

**Authoring notes:** Garden -> garage workshop. Question about timing transfers; current answer concerns indoor work conditions, prior concerns outdoor sun.

**Expected answers (judge-only):**

- `current_answers`: `garage`, `workshop`, `indoor work`, `tinkering on the car`, `bench work`, `fine to work anytime`, `vise work`, `pegboard tools`, `concrete floor`
- `prior_answers`: `garden`, `raised beds`, `midday sun is harsh`, `watering plants`, `weeding`, `hose work`, `soil is dry`, `leafy rows`

**Review:**

- [ ] PASS
- [ ] EDIT
- [ ] REPLACE

**Notes:**

> _(write any review notes here)_

---

### sc-29

| | |
|---|---|
| **Shift type** | `location` |
| **Target context** | `current` |
| **Activity domain** | kitchen |
| **Difficulty** | medium |
| **Cognitive load** | single_referent |
| **Time gap** | minutes |

**Turn 1, camera (`turn_1_image`):**

> Interior view. Stainless steel appliances along one wall. Granite counter strewn with a flat raised wooden slab, a heap of chopped onion, a long flat triangular blade with a black handle resting on a folded cloth. Steam rising from a deep round metal vessel with a handle on a four-burner cooktop. Open spice jars in a cluster. A pendant lamp hanging low above a small island.

**Turn 1, user speech (`turn_1_user`):** *"Where should I set things up?"*

**Turn 2, camera (`turn_2_image`):**

> Interior view of a different room. A long rectangular wooden table on a sisal rug. Six high-backed chairs evenly spaced. A glass-fronted cabinet on the far wall with stacks of plates and stemmed glasses. A chandelier with multiple small bulbs casting soft light. No food, no countertops visible.

**Turn 2, user speech (`turn_2_user`):** *"Where should I set things up?"*

**Turn 3, repair anchor (`turn_3_repair_anchor`):** *"I mean for serving in this room, not for prep back where I was cooking."*

**Authoring notes:** Cooking space -> dining space. The question about setup transfers; correct answer is about table layout for service.

**Expected answers (judge-only):**

- `current_answers`: `dining room`, `long table`, `place settings`, `set the table`, `lay out plates`, `stemmed glasses on the right`, `centerpiece in the middle`, `head of the table`, `linen runner`
- `prior_answers`: `kitchen`, `cooking station`, `next to the cutting board`, `near the cooktop`, `mise en place`, `prep station`, `spice jars within reach`, `knife work area`

**Review:**

- [ ] PASS
- [ ] EDIT
- [ ] REPLACE

**Notes:**

> _(write any review notes here)_

---

### sc-30

| | |
|---|---|
| **Shift type** | `location` |
| **Target context** | `current` |
| **Activity domain** | automotive |
| **Difficulty** | medium |
| **Cognitive load** | distractor_present |
| **Time gap** | minutes |

**Turn 1, camera (`turn_1_image`):**

> Wide indoor view. Polished vinyl floor with reflective sheen. Long aisles of metal shelving stocked with boxed merchandise. Overhead fluorescent strip lighting. A waist-high counter with a small flat backlit display on a stand and a scanner on a coiled cord. Suspended signs with arrows hanging from the ceiling beams.

**Turn 1, user speech (`turn_1_user`):** *"Is the lighting alright for what I need to check?"*

**Turn 2, camera (`turn_2_image`):**

> Wide indoor view. Concrete floor with a yellow painted line. A large vehicle raised on a hydraulic lift several feet off the ground. Metal toolboxes on rolling carts. A coiled black flexible air line hanging from a ceiling reel. Single high-bay lamp casting a pool of bright white light directly under the lifted vehicle. Most of the surrounding floor in shadow.

**Turn 2, user speech (`turn_2_user`):** *"Is the lighting alright for what I need to check?"*

**Turn 3, repair anchor (`turn_3_repair_anchor`):** *"I mean for the inspection I'm doing right here in this spot, not the place I was at before."*

**Authoring notes:** Retail floor -> automotive service bay. Same lighting question, but the inspection task changes; current answer focuses on under-vehicle visibility.

**Expected answers (judge-only):**

- `current_answers`: `service bay`, `under the lift`, `drop light`, `trouble light`, `underside inspection`, `shadow under the chassis`, `raised vehicle`, `high-bay lamp`, `look underneath`
- `prior_answers`: `store aisle`, `shelves`, `reading labels`, `scanner station`, `fluorescent strips`, `stock check`, `barcode glare`, `merchandise floor`

**Review:**

- [ ] PASS
- [ ] EDIT
- [ ] REPLACE

**Notes:**

> _(write any review notes here)_

---

### sc-31

| | |
|---|---|
| **Shift type** | `location` |
| **Target context** | `prior` |
| **Activity domain** | fitness |
| **Difficulty** | medium |
| **Cognitive load** | single_referent |
| **Time gap** | minutes |

**Turn 1, camera (`turn_1_image`):**

> Wide interior view. Sprung wooden floor with painted boundary lines. Mirrored wall along one side from floor to ceiling. A long horizontal wooden rail attached to the mirror at waist height. Black foam mats stacked in a corner. Bright even ceiling lighting. A water bottle and a folded towel on the floor near the mirror.

**Turn 1, user speech (`turn_1_user`):** *"Is my heart rate where it should be for this?"*

**Turn 2, camera (`turn_2_image`):**

> Wide interior view of a corridor. Rows of tall narrow metal cabinets with vertical handles along both walls. Wooden bench bolted to the floor down the center. Rubber mat flooring. Overhead lighting in recessed panels. A wall-mounted hand dryer visible at the far end. A shoe sits on the bench, laces loose.

**Turn 2, user speech (`turn_2_user`):** *"What was it doing earlier when I was working out?"*

**Turn 3, repair anchor (`turn_3_repair_anchor`):** *"I mean back when I was actually exercising in the room with the mirrored wall."*

**Authoring notes:** Studio floor -> locker corridor. T2 explicitly asks about earlier; correct answer reflects the prior workout context.

**Expected answers (judge-only):**

- `current_answers`: `locker room`, `changing area`, `resting heart rate`, `post-workout cooldown`, `recovery state`, `settling down`, `near baseline`, `bench seat`
- `prior_answers`: `studio`, `barre work`, `ballet barre`, `elevated during exercise`, `training zone`, `working heart rate`, `active range`, `cardio range`, `mirrored room`, `sprung floor`

**Review:**

- [ ] PASS
- [ ] EDIT
- [ ] REPLACE

**Notes:**

> _(write any review notes here)_

---

### sc-32

| | |
|---|---|
| **Shift type** | `location` |
| **Target context** | `clarify` |
| **Activity domain** | workshop |
| **Difficulty** | hard |
| **Cognitive load** | multi_referent |
| **Time gap** | minutes |

**Turn 1, camera (`turn_1_image`):**

> Indoor view. Long rectangular wooden surface scarred with old kerf marks. A partially assembled wooden frame clamped at one corner. A small bubble vial in a yellow housing resting across two of the frame's edges. Sawdust scattered on the bench. Pegboard wall behind with hanging hand tools.

**Turn 1, user speech (`turn_1_user`):** *"Is it level here?"*

**Turn 2, camera (`turn_2_image`):**

> Outdoor view. Patchy lawn with bare soil patches showing through. A rectangular wooden frame partially sunken into the ground, soil piled around its outside edges. A long-handled flat-bladed digging tool stuck upright in the dirt. A bag of bagged soil amendment leaning against the frame. Mid-afternoon shade across half the frame.

**Turn 2, user speech (`turn_2_user`):** *"Is it level here?"*

**Turn 3, repair anchor (`turn_3_repair_anchor`):** *"I'm asking about this spot outside where the frame is sitting in the dirt, not the one indoors on the bench."*

**Authoring notes:** Workshop bench -> garden raised-bed install. Both scenes plausibly concern leveling; without the repair, the assistant should ask which one is meant.

**Expected answers (judge-only):**

- `current_answers`: `raised bed`, `garden frame`, `ground is uneven`, `shim with soil`, `tamp the soil`, `dig down on the high side`, `bed is sitting crooked`, `pitched toward one corner`
- `prior_answers`: `workbench`, `carpentry frame`, `spirit level`, `bubble vial`, `frame is square`, `clamped joint`, `shim under one leg`, `true to the bench`
- `clarify_indicators`: `which one`, `do you mean`, `are you asking about`, `to clarify`, `could you specify`, `the frame on the bench or the one in the ground`, `indoors or outdoors`, `which surface`

**Review:**

- [ ] PASS
- [ ] EDIT
- [ ] REPLACE

**Notes:**

> _(write any review notes here)_

---

### sc-33

| | |
|---|---|
| **Shift type** | `object_in_view` |
| **Target context** | `current` |
| **Activity domain** | kitchen |
| **Difficulty** | easy |
| **Cognitive load** | single_referent |
| **Time gap** | seconds |

**Turn 1, camera (`turn_1_image`):**

> Close view of a small round fruit on a flat raised wooden slab, deep yellow-green skin with a slight give where a thumb has pressed in. A long flat broad triangular blade with a black handle rests at the edge of the slab. A metal colander and a row of small spice jars line the back of the counter behind it.

**Turn 1, user speech (`turn_1_user`):** *"Is this ripe enough yet?"*

**Turn 2, camera (`turn_2_image`):**

> Same flat raised wooden slab, camera now tilted toward an oblong fruit lying on it. Bright yellow skin freckled with brown spots, a curved stem at one end. The round green-skinned fruit visible at the edge of the frame. The same long flat broad-bladed cutting tool, colander, and row of spice jars in the background.

**Turn 2, user speech (`turn_2_user`):** *"Is this ripe enough yet?"*

**Turn 3, repair anchor (`turn_3_repair_anchor`):** *"I mean the speckled yellow one I'm looking at now, not the avocado."*

**Authoring notes:** Same cutting board scene, attention shifts from avocado to banana. Identical question.

**Expected answers (judge-only):**

- `current_answers`: `banana`, `peel back the stem`, `give it another day`, `freckled yellow`, `brown spots`, `soft skin`, `yellow with spots`, `ready to eat now`, `use for baking`
- `prior_answers`: `avocado`, `press near the stem`, `let it sit on the counter`, `deep yellow-green`, `slight give`, `firm flesh`, `still firm`, `needs another day`

**Review:**

- [ ] PASS
- [ ] EDIT
- [ ] REPLACE

**Notes:**

> _(write any review notes here)_

---

### sc-34

| | |
|---|---|
| **Shift type** | `object_in_view` |
| **Target context** | `current` |
| **Activity domain** | workshop |
| **Difficulty** | medium |
| **Cognitive load** | multi_referent |
| **Time gap** | seconds |

**Turn 1, camera (`turn_1_image`):**

> A wooden workbench with two clamps along its near edge. A flat rectangular electrical tool sits centered on the bench, dark housing with a circular disk of fine grit on its underside, a rounded handle and a power cord curling off the back. A pegboard with hanging tools fills the wall behind.

**Turn 1, user speech (`turn_1_user`):** *"What should I be using here for this stage?"*

**Turn 2, camera (`turn_2_image`):**

> Same workbench with the same clamps and pegboard wall behind. Camera now panned left to a long flat sheet of paper-backed abrasive folded around a felt-covered block, held in a hand. Visible scratch pattern on a small offcut beside it. A coiled black power cord lies on the bench at the far edge of the frame.

**Turn 2, user speech (`turn_2_user`):** *"What should I be using here for this stage?"*

**Turn 3, repair anchor (`turn_3_repair_anchor`):** *"I mean the block I'm sanding by hand with now, not the orbital."*

**Authoring notes:** Workbench scene, attention shifts from random orbital sander to hand sanding block. Same question.

**Expected answers (judge-only):**

- `current_answers`: `sanding block`, `hand sanding`, `with the grain`, `120 to 220 grit`, `fine grit by hand`, `felt-backed block`, `paper-backed abrasive`, `light pressure`, `long even strokes`
- `prior_answers`: `random orbital`, `orbital sander`, `power sander`, `circular motion`, `80 to 120 grit to start`, `let the tool do the work`, `spinning disk`, `hook and loop pad`, `moderate pressure`

**Review:**

- [ ] PASS
- [ ] EDIT
- [ ] REPLACE

**Notes:**

> _(write any review notes here)_

---

### sc-35

| | |
|---|---|
| **Shift type** | `object_in_view` |
| **Target context** | `current` |
| **Activity domain** | garden |
| **Difficulty** | medium |
| **Cognitive load** | single_referent |
| **Time gap** | seconds |

**Turn 1, camera (`turn_1_image`):**

> A raised wooden bed full of dark soil. Camera focused on a leafy plant with broad, crinkled blue-green leaves spreading low to the ground from a thick central stem. Drip irrigation line and a wooden stake at the bed's edge.

**Turn 1, user speech (`turn_1_user`):** *"When should I pull this?"*

**Turn 2, camera (`turn_2_image`):**

> Same raised bed, same dark soil and drip line, same wooden stake. Camera now angled toward a tall plant with feathery, finely divided leaves on slender stems, small yellow flowers just starting to open at the tips. A few broad crinkled leaves of another plant visible at the frame edge.

**Turn 2, user speech (`turn_2_user`):** *"When should I pull this?"*

**Turn 3, repair anchor (`turn_3_repair_anchor`):** *"I mean the one with the lacy leaves and yellow flowers, not the kale."*

**Authoring notes:** Raised bed scene, attention shifts from kale to dill. Same question.

**Expected answers (judge-only):**

- `current_answers`: `dill`, `harvest the seed heads`, `let the flowers open fully`, `feathery leaves`, `yellow umbels`, `finely divided foliage`, `cut at the base for seed`, `snip fronds for fresh use`, `wait for seeds to brown`
- `prior_answers`: `kale`, `cut outer leaves first`, `leave the crown intact`, `blue-green leaves`, `crinkled foliage`, `cut and come again`, `before a hard frost for sweetness`, `harvest from the bottom up`, `thick central stem`

**Review:**

- [ ] PASS
- [ ] EDIT
- [ ] REPLACE

**Notes:**

> _(write any review notes here)_

---

### sc-36

| | |
|---|---|
| **Shift type** | `object_in_view` |
| **Target context** | `current` |
| **Activity domain** | automotive |
| **Difficulty** | hard |
| **Cognitive load** | distractor_present |
| **Time gap** | seconds |

**Turn 1, camera (`turn_1_image`):**

> Open engine bay viewed from above. Camera focused on a yellow ring set into a black plastic tube near the front of the engine, ring sticking up about an inch with a small loop at the top. A black plastic intake manifold and a red fluid reservoir cap visible to one side.

**Turn 1, user speech (`turn_1_user`):** *"What level should this be at?"*

**Turn 2, camera (`turn_2_image`):**

> Same engine bay, same black intake manifold and red reservoir cap visible at the edges. Camera now shifted right toward a translucent plastic container with horizontal molded lines on its side and a thin bluish liquid visible inside, the fluid surface sitting between two of the marked lines. A yellow loop sticking up from a black tube visible at the far edge of the frame.

**Turn 2, user speech (`turn_2_user`):** *"What level should this be at?"*

**Turn 3, repair anchor (`turn_3_repair_anchor`):** *"I mean the windshield washer tank I'm looking at now, not the dipstick."*

**Authoring notes:** Engine bay scene, attention shifts from oil dipstick to washer fluid reservoir. Both visible across frames. Distractor present.

**Expected answers (judge-only):**

- `current_answers`: `washer fluid`, `windshield washer reservoir`, `fill to the max line`, `blue fluid`, `translucent tank`, `top off when low`, `between min and max`, `horizontal molded lines`
- `prior_answers`: `dipstick`, `engine oil`, `between the two marks`, `yellow pull ring`, `wipe and re-insert`, `check on level ground`, `engine off and cool`, `oil film on the stick`

**Review:**

- [ ] PASS
- [ ] EDIT
- [ ] REPLACE

**Notes:**

> _(write any review notes here)_

---

### sc-37

| | |
|---|---|
| **Shift type** | `object_in_view` |
| **Target context** | `prior` |
| **Activity domain** | office |
| **Difficulty** | hard |
| **Cognitive load** | multi_referent |
| **Time gap** | minutes |

**Turn 1, camera (`turn_1_image`):**

> A desk with a closed hinged thin slab device pushed to one side. Camera centered on a tall ceramic mug with steam rising off a dark liquid surface, a faint bitter-smelling vapor visible. A notebook open to a half-filled page and a pair of glasses sit beside it.

**Turn 1, user speech (`turn_1_user`):** *"About how long before this is safe to drink?"*

**Turn 2, camera (`turn_2_image`):**

> Same desk, same closed hinged thin slab device, same open notebook and glasses. Camera now tilted down toward a clear glass tumbler beside the mug, filled with a pale amber liquid, a wedge of yellow citrus floating at the top, beads of condensation running down the outside. The tall ceramic mug visible at the edge of the frame, a thin wisp of vapor above it.

**Turn 2, user speech (`turn_2_user`):** *"And the one I asked you about a couple of minutes ago — is that one okay yet?"*

**Turn 3, repair anchor (`turn_3_repair_anchor`):** *"I mean the hot drink from earlier, not the iced one in front of me now."*

**Authoring notes:** Desk scene, attention shifts from hot coffee to iced tea, but T2 explicitly asks back about the earlier item. target_context is prior.

**Expected answers (judge-only):**

- `current_answers`: `iced tea`, `lemon wedge`, `drink whenever`, `amber liquid`, `condensation on the glass`, `already cool`, `ready now`, `sip as is`
- `prior_answers`: `coffee`, `hot drink`, `let it cool a few minutes`, `steaming dark liquid`, `still too hot`, `wait three to five minutes`, `around 140 degrees to sip`, `blow across the surface`, `ceramic mug`

**Review:**

- [ ] PASS
- [ ] EDIT
- [ ] REPLACE

**Notes:**

> _(write any review notes here)_

---

### sc-38

| | |
|---|---|
| **Shift type** | `absent_referent` |
| **Target context** | `prior` |
| **Activity domain** | garden |
| **Difficulty** | medium |
| **Cognitive load** | absent_referent |
| **Time gap** | minutes |

**Turn 1, camera (`turn_1_image`):**

> Backyard scene in soft morning light. A long cylindrical clear plastic tube hangs by a wire from a maple branch, filled with small black seeds. Several small openings down the side, each with a short metal perch under it. Resting on the lowest perch sits a small bird, roughly the size of a fist, brilliant lemon-yellow body with deep black wings marked by two narrow white bars and a sharp black cap on the forehead. Short conical beak pointed toward one of the openings.

**Turn 1, user speech (`turn_1_user`):** *"Cute. Is that a regular for this season?"*

**Turn 2, camera (`turn_2_image`):**

> Same maple branch, same hanging clear plastic tube of black seeds. Lowest perch is empty. A scatter of light husks on the patio stones below the tube. Sun a bit higher in the frame, slight breeze in the leaves. No bird anywhere in view.

**Turn 2, user speech (`turn_2_user`):** *"What was the one from a minute ago, do you think?"*

**Turn 3, repair anchor (`turn_3_repair_anchor`):** *"I mean the little yellow bird that was at the feeder before."*

**Authoring notes:** Songbird at feeder at T1, gone at T2. User asks for ID of the bird from before — answer is recoverable from T1 perceptual description.

**Expected answers (judge-only):**

- `current_answers`: `empty feeder`, `tube feeder`, `bird feeder`, `refill the seed`, `wait it out`, `seed husks`, `no bird in frame`, `perch is empty`
- `prior_answers`: `American goldfinch`, `goldfinch`, `finch`, `breeding male`, `loves nyjer seed`, `loves thistle seed`, `feeds on thistle`, `yellow body`, `black cap`, `white wing bars`, `regular summer visitor`

**Review:**

- [ ] PASS
- [ ] EDIT
- [ ] REPLACE

**Notes:**

> _(write any review notes here)_

---

### sc-39

| | |
|---|---|
| **Shift type** | `absent_referent` |
| **Target context** | `abstain` |
| **Activity domain** | kitchen |
| **Difficulty** | hard |
| **Cognitive load** | absent_referent |
| **Time gap** | seconds |

**Turn 1, camera (`turn_1_image`):**

> Inside of a refrigerator door, light on. A hand holding up a tall rectangular paper container with a folded triangular top, brand label facing the camera showing a leaf graphic and printed name. The narrow side panel of the container, where a small printed string of numbers would normally appear, is angled away from the lens and in shadow against the door shelf.

**Turn 1, user speech (`turn_1_user`):** *"Should I just toss this or is it still okay?"*

**Turn 2, camera (`turn_2_image`):**

> Same refrigerator interior, door still open, light still on. The shelf where the container sat is empty except for a small ring of condensation. A hand reaching toward a different shelf in the background. No paper container visible anywhere in frame.

**Turn 2, user speech (`turn_2_user`):** *"Wait, what did the printing on the side actually say?"*

**Turn 3, repair anchor (`turn_3_repair_anchor`):** *"I mean the use-by date on the carton I was just holding."*

**Authoring notes:** Camera at T1 saw only the front label of the carton; the printed-date side was angled away and never read. T2 carton is gone. Model has no evidence of the printed date — abstain is the correct response.

**Expected answers (judge-only):**

- `prior_answers`: `oat milk`, `plant milk`, `milk carton`, `shake before pouring`, `smell test`, `give it a sniff`, `label side facing camera`, `date side angled away`, `front of carton visible only`
- `abstain_indicators`: `I didn't see the date`, `the date side was turned away`, `couldn't read the print`, `no view of the use-by`, `wasn't visible to me`, `can't say from what I saw`, `no evidence of the date`, `the printed side was hidden`

**Review:**

- [ ] PASS
- [ ] EDIT
- [ ] REPLACE

**Notes:**

> _(write any review notes here)_

---

### sc-40

| | |
|---|---|
| **Shift type** | `absent_referent` |
| **Target context** | `current` |
| **Activity domain** | workshop |
| **Difficulty** | easy |
| **Cognitive load** | absent_referent |
| **Time gap** | seconds |

**Turn 1, camera (`turn_1_image`):**

> Workbench top in overhead light. A pine board lying flat. Resting across it: a long wooden handle topped by a heavy steel head, one face flat and smooth, the other face split into two curved downward-pointing prongs. Beside it, a thin metal pin sits in the wood with its flat circular head flush against the surface. To the right of the board, separate from all of that, a small threaded piece is sunken slightly below the wood — its head shows a cross-shaped recess, edges of the recess chewed and rounded.

**Turn 1, user speech (`turn_1_user`):** *"That one looks done. What about this other thing over here?"*

**Turn 2, camera (`turn_2_image`):**

> Same workbench under the same overhead light. The pine board has been pushed to one side. The wooden-handled steel-headed item is no longer in frame. The small threaded piece with the cross-shaped recess is centered now, head clearly chewed, recess edges rounded into shallow curves. A short can of penetrating spray and a pair of two-armed metal gripping tools with locking levers sit on the bench beside it.

**Turn 2, user speech (`turn_2_user`):** *"How would you get this out?"*

**Turn 3, repair anchor (`turn_3_repair_anchor`):** *"I mean the fastener right in front of me now, the one with the messed-up head."*

**Authoring notes:** Hammer and nail visible at T1 then absent at T2. User pivots at T2 to the stripped screw still in frame. Correct answer is grounded in current T2 view, not the absent hammer.

**Expected answers (judge-only):**

- `current_answers`: `stripped screw`, `stripped Phillips`, `Phillips screw`, `screw extractor`, `left-handed drill bit`, `rubber band trick`, `lock the pliers on the head`, `penetrating oil first`, `bite into the head`, `rounded recess`, `chewed head`, `stripped recess`
- `prior_answers`: `claw hammer`, `hammer`, `pull the nail`, `rocking pull`, `claw under the head`, `smooth striking face`, `flush nail head`

**Review:**

- [ ] PASS
- [ ] EDIT
- [ ] REPLACE

**Notes:**

> _(write any review notes here)_

---

### sc-41

| | |
|---|---|
| **Shift type** | `absent_referent` |
| **Target context** | `clarify` |
| **Activity domain** | fitness |
| **Difficulty** | medium |
| **Cognitive load** | absent_referent |
| **Time gap** | minutes |

**Turn 1, camera (`turn_1_image`):**

> Home gym corner with rubber matting. On the floor, a black cast-iron sphere with a thick looped handle on top sits next to a coiled length of plastic-coated cord with two molded grip handles on either end. A small towel and a water bottle are off to the side. A wall mirror reflects the scene.

**Turn 1, user speech (`turn_1_user`):** *"Quick circuit. Anything I should watch for?"*

**Turn 2, camera (`turn_2_image`):**

> Same home gym corner. The mat is now empty — both the iron sphere with the looped handle and the coiled cord with grip handles are gone, returned to a wall rack barely visible at the edge of the frame holding several pieces of equipment. The towel and water bottle remain. Mirror still showing the empty floor.

**Turn 2, user speech (`turn_2_user`):** *"Did I get the form right on that one?"*

**Turn 3, repair anchor (`turn_3_repair_anchor`):** *"Sorry — which exercise are you asking about? You worked with two different things just now."*

**Authoring notes:** Two distinct pieces of equipment visible at T1, both absent at T2. T2 question 'that one' is ambiguous between the two — model should ask which exercise.

**Expected answers (judge-only):**

- `prior_answers`: `kettlebell swing`, `kettlebell`, `hip hinge`, `drive from the hips`, `bell to chest height`, `iron sphere with handle`, `jump rope`, `skipping rope`, `wrist rotation`, `stay on the balls of your feet`, `coiled cord with grips`
- `clarify_indicators`: `which one`, `which exercise`, `do you mean the swing or the rope`, `which of the two`, `can you clarify which`, `the bell or the rope`, `specify which one`, `which movement`

**Review:**

- [ ] PASS
- [ ] EDIT
- [ ] REPLACE

**Notes:**

> _(write any review notes here)_

---

### sc-42

| | |
|---|---|
| **Shift type** | `absent_referent` |
| **Target context** | `abstain` |
| **Activity domain** | craft |
| **Difficulty** | hard |
| **Cognitive load** | absent_referent |
| **Time gap** | minutes |

**Turn 1, camera (`turn_1_image`):**

> View down at the user's lap. Both hands holding up a small rectangular piece of soft fabric between them, edges loose and slightly curling. The face of the fabric shows neat rows of interlocking V-shaped loops in cream-colored yarn. Hands turning it sideways toward a window for the light. No long flat measuring tool, no flexible marked band in a metal case, and no printed grid of marked increments is anywhere in frame.

**Turn 1, user speech (`turn_1_user`):** *"First time trying this pattern. Looks alright?"*

**Turn 2, camera (`turn_2_image`):**

> Same lap view, same lighting. Hands now empty and resting on the thigh. The rectangular fabric piece is gone — likely set off-camera. A pair of long thin metal sticks with tapered tips lies across the leg next to a ball of cream yarn. No measuring instrument anywhere in the frame.

**Turn 2, user speech (`turn_2_user`):** *"Was the gauge actually on target, do you think?"*

**Turn 3, repair anchor (`turn_3_repair_anchor`):** *"I mean the swatch I was just holding up — was it knitting to the right gauge?"*

**Authoring notes:** Swatch visible at T1 but never measured against any ruler or gauge tool, and the camera never showed a stitch count over a known length. At T2 swatch is absent. Model has no quantitative evidence to assess gauge — abstain is the correct response.

**Expected answers (judge-only):**

- `prior_answers`: `knit swatch`, `stockinette swatch`, `stockinette`, `block the swatch`, `count stitches per inch`, `V-shaped loops`, `cream yarn`, `edges curling`, `no ruler in frame`, `uncounted stitches`
- `abstain_indicators`: `I didn't see it measured`, `no ruler was visible`, `couldn't count the stitches`, `no gauge tool in frame`, `can't assess gauge from what I saw`, `wasn't measured on camera`, `no evidence of stitches per inch`, `didn't see a tape measure`

**Review:**

- [ ] PASS
- [ ] EDIT
- [ ] REPLACE

**Notes:**

> _(write any review notes here)_

---

### sc-43

| | |
|---|---|
| **Shift type** | `screen_content` |
| **Target context** | `current` |
| **Activity domain** | communication |
| **Difficulty** | easy |
| **Cognitive load** | single_referent |
| **Time gap** | seconds |

**Turn 1, camera (`turn_1_image`):**

> View of a handheld backlit rectangular display held in portrait, glass front bezel narrow on all sides. A vertical stack of speech bubbles fills most of the display: gray bubbles aligned left, blue bubbles aligned right. Small circular avatar at the top with a single first name beneath it. A text entry field at the bottom with a send arrow. Faint timestamps between message clusters.

**Turn 1, user speech (`turn_1_user`):** *"How should I respond to this?"*

**Turn 2, camera (`turn_2_image`):**

> View of the same handheld backlit rectangular display, now showing a white compose window. A subject line field near the top, a recipient address with an at-symbol visible, and a long block of paragraph text in the body. Formatting controls along the bottom edge with a paperclip icon. The header strip shows folder labels rather than a single name.

**Turn 2, user speech (`turn_2_user`):** *"How should I respond to this?"*

**Turn 3, repair anchor (`turn_3_repair_anchor`):** *"I mean the email draft I'm looking at right now, not the text thread."*

**Authoring notes:** Screen swap from a casual chat thread to a long-form email draft. Reply guidance differs by register and length.

**Expected answers (judge-only):**

- `current_answers`: `email`, `subject line`, `recipient`, `formal`, `greeting`, `salutation`, `sign-off`, `paragraph structure`, `professional tone`, `long-form`, `draft body`, `reply-all consideration`
- `prior_answers`: `text`, `message thread`, `chat`, `casual tone`, `short reply`, `emoji`, `quick acknowledgment`, `blue bubble`, `gray bubble`, `informal phrasing`

**Review:**

- [ ] PASS
- [ ] EDIT
- [ ] REPLACE

**Notes:**

> _(write any review notes here)_

---

### sc-44

| | |
|---|---|
| **Shift type** | `screen_content` |
| **Target context** | `current` |
| **Activity domain** | finance |
| **Difficulty** | easy |
| **Cognitive load** | single_referent |
| **Time gap** | seconds |

**Turn 1, camera (`turn_1_image`):**

> View of a handheld backlit rectangular display showing a list of rows stacked vertically. Each row has a short merchant label on the left, a dollar amount on the right with a minus sign in front, and a small category icon. A search bar at the top and a tab strip at the bottom with several glyphs. Total balance figure in large type near the header.

**Turn 1, user speech (`turn_1_user`):** *"Anything I should be worried about here?"*

**Turn 2, camera (`turn_2_image`):**

> View of the same handheld backlit rectangular display, now showing a large circular chart split into colored wedges with percentages overlaid. Below the circle, a vertical legend with category labels and dollar totals. A month selector at the top with arrow buttons on either side. A horizontal bar across the middle showing budget remaining versus spent.

**Turn 2, user speech (`turn_2_user`):** *"Anything I should be worried about here?"*

**Turn 3, repair anchor (`turn_3_repair_anchor`):** *"I mean the budget breakdown I'm looking at now, not the transaction list."*

**Authoring notes:** Screen swap from transaction list to budget pie chart. Concerns differ: outliers/fraud vs. category overspend.

**Expected answers (judge-only):**

- `current_answers`: `budget`, `category`, `pie chart`, `wedge`, `overspend`, `remaining`, `month-to-date`, `percentage`, `category breakdown`, `spending by category`, `over budget`, `allocation`
- `prior_answers`: `transaction`, `merchant`, `charge`, `duplicate charge`, `unfamiliar charge`, `fraud`, `outlier`, `recurring subscription`, `negative amount`, `individual line item`, `running balance`

**Review:**

- [ ] PASS
- [ ] EDIT
- [ ] REPLACE

**Notes:**

> _(write any review notes here)_

---

### sc-45

| | |
|---|---|
| **Shift type** | `screen_content` |
| **Target context** | `current` |
| **Activity domain** | office |
| **Difficulty** | hard |
| **Cognitive load** | distractor_present |
| **Time gap** | minutes |

**Turn 1, camera (`turn_1_image`):**

> View of a hinged clamshell device's upper backlit display, opened wide above a flat lower half with rows of rectangular keys, the display filled by a large rectangular slide. A short title in bold sans-serif at the top, three bullet points centered below, and a small footer with a page number. Thumbnail strip running down the left edge showing a sequence of similar rectangles. Dark mode interface with a play-arrow icon in the top toolbar.

**Turn 1, user speech (`turn_1_user`):** *"Is there too much going on for one minute?"*

**Turn 2, camera (`turn_2_image`):**

> View of the same hinged clamshell device's upper display, now showing a dense grid of cells filled with numbers. Several columns shaded in alternating bands of pale blue. A long formula visible in a bar above the grid referencing multiple cell ranges. Tab strip at the bottom with five labeled sheets. A frozen header row in bold with column letters above.

**Turn 2, user speech (`turn_2_user`):** *"Is there too much going on for one minute?"*

**Turn 3, repair anchor (`turn_3_repair_anchor`):** *"I mean the spreadsheet I'm looking at now, not the slide."*

**Authoring notes:** Screen swap from a presentation slide to a dense spreadsheet. Pacing advice differs sharply: slide simplification vs. data-walkthrough chunking. Distractor: thumbnail strip on T1 could pull toward deck-level advice.

**Expected answers (judge-only):**

- `current_answers`: `spreadsheet`, `cells`, `data grid`, `columns`, `formula`, `walkthrough`, `highlight key cells`, `narrate the columns`, `freeze the header`, `pivot summary`, `callout the totals`, `shaded bands`, `split across views`
- `prior_answers`: `slide`, `bullet point`, `title`, `deck`, `slide deck`, `presentation`, `trim bullets`, `one idea per slide`, `speaker pacing`, `page footer`, `thumbnail`

**Review:**

- [ ] PASS
- [ ] EDIT
- [ ] REPLACE

**Notes:**

> _(write any review notes here)_

---

### sc-46

| | |
|---|---|
| **Shift type** | `screen_content` |
| **Target context** | `prior` |
| **Activity domain** | navigation |
| **Difficulty** | medium |
| **Cognitive load** | single_referent |
| **Time gap** | minutes |

**Turn 1, camera (`turn_1_image`):**

> View of a handheld backlit rectangular display in landscape. A stylized map fills the display with a thick blue line tracing a route across gray streets. A blue dot marks the current position with a forward-facing cone. A panel along the bottom shows an estimated arrival time, a distance figure, and a large arrow icon indicating an upcoming turn. Speed limit badge in the lower corner.

**Turn 1, user speech (`turn_1_user`):** *"Will this get me there on time?"*

**Turn 2, camera (`turn_2_image`):**

> View of the same handheld backlit rectangular display, now showing a list of cards stacked vertically. Each card has a thumbnail photo on the left, a name in bold, a row of small star icons, a price-tier indicator with dollar signs, and a short distance label. A search bar at the top with a filter chip row beneath it.

**Turn 2, user speech (`turn_2_user`):** *"Was the answer to my earlier question yes or no?"*

**Turn 3, repair anchor (`turn_3_repair_anchor`):** *"I mean my original question about getting there on time, when I was looking at the route screen."*

**Authoring notes:** Prior scenario: T2 user explicitly references the earlier question. Screen content has shifted to a list of nearby places, but the answer must come from the route/ETA shown in T1.

**Expected answers (judge-only):**

- `current_answers`: `restaurant list`, `search results`, `star rating`, `price tier`, `filter`, `thumbnail`, `distance label`, `place card`, `nearby places`, `results listing`
- `prior_answers`: `map`, `route`, `ETA`, `arrival time`, `blue line`, `turn arrow`, `navigation`, `on schedule`, `behind schedule`, `make it on time`, `current pace`, `remaining distance`, `speed limit`

**Review:**

- [ ] PASS
- [ ] EDIT
- [ ] REPLACE

**Notes:**

> _(write any review notes here)_

---

### sc-47

| | |
|---|---|
| **Shift type** | `pre_conversation_recall` |
| **Target context** | `prior` |
| **Activity domain** | kitchen |
| **Difficulty** | easy |
| **Cognitive load** | absent_referent |
| **Time gap** | minutes |

**Pre-conversation camera state (`context_image`):**

> Camera view of a stainless steel refrigerator door at close range. A small rectangular paper sticker stuck near eye height, off-white with handwritten ballpoint text reading a date in the format MM/DD followed by the word raw and an arrow. Below it, a faint smudge of red liquid streaked downward toward the floor. Tile floor visible at the bottom edge with a small puddle forming under the door.

**Turn 1, camera (`turn_1_image`):**

> Camera view inside an open refrigerator. Top shelf shows a cardboard egg carton, a clear glass jar of olives, and a half-empty plastic bottle of orange juice. Light from the interior bulb spilling onto the user's hands as they reach toward the middle shelf.

**Turn 1, user speech (`turn_1_user`):** *"What should I grab first to make breakfast?"*

**Turn 2, camera (`turn_2_image`):**

> Camera view at a kitchen counter. A ceramic plate sits in front of the user with two cracked eggshells, a fork resting in a small puddle of yolk, and a flat raised wooden slab to the side with a half-cut tomato. Morning light through a window above the sink.

**Turn 2, user speech (`turn_2_user`):** *"Hey, what was that note I noticed before I opened the fridge?"*

**Turn 3, repair anchor (`turn_3_repair_anchor`):** *"The little sticker I saw on the front of the fridge before I started cooking."*

**Authoring notes:** A handwritten date label was visible on the fridge door before any speech. T1 is inside the open fridge, T2 is at the counter cooking. The label info lives only in context_image.

**Expected answers (judge-only):**

- `current_answers`: `plate with eggshells`, `cracked eggs`, `tomato on the cutting board`, `yolk on the fork`, `ceramic plate`, `halved tomato`, `currently at the counter`
- `prior_answers`: `sticky note`, `handwritten label`, `date sticker`, `raw meat label`, `thaw date`, `use-by note`, `MM/DD raw`, `expiration reminder`, `ballpoint date`, `leaking package note`, `marked with a date`

**Review:**

- [ ] PASS
- [ ] EDIT
- [ ] REPLACE

**Notes:**

> _(write any review notes here)_

---

### sc-48

| | |
|---|---|
| **Shift type** | `pre_conversation_recall` |
| **Target context** | `prior` |
| **Activity domain** | workshop |
| **Difficulty** | medium |
| **Cognitive load** | absent_referent |
| **Time gap** | minutes |

**Pre-conversation camera state (`context_image`):**

> Camera view of a pegboard wall above a workbench. Pegboard hooks holding various hand tools. Near the center, an empty hook outlined in thick black ink shows the silhouette of a tool with a rubberized grip handle and a long flat angled head with a curved claw at one end. Hook is bare. To the right of the empty hook, a wall-mounted dispenser of yellow earplugs, three-quarters full.

**Turn 1, camera (`turn_1_image`):**

> Camera view down at a workbench surface. A long rectangular pale wood plank, roughly two inches by four inches in cross-section, held horizontally between the jaws of a heavy iron screw-tightened gripping fixture. The user's gloved hand is steadying a smaller cube of the same wood against it. Sawdust scattered around. A retractable yellow metal ribbon with black inch markings extended out across the surface, showing markings around the 18-inch line.

**Turn 1, user speech (`turn_1_user`):** *"Am I lined up straight enough to start cutting?"*

**Turn 2, camera (`turn_2_image`):**

> Camera view at a different bench section. A black and yellow pistol-shaped power tool with a rotating chuck at the front and a curved grip handle resting on its side, a rectangular black plastic power pack clipped into the base. Beside it, a small plastic case lying open with rows of slim metal cylinders sized in ascending diameter, each tipped with a spiral cutting edge. Two thin graphite tick marks visible on the surface of a sheet of layered wood. The user's hand is reaching toward the smaller cylinders.

**Turn 2, user speech (`turn_2_user`):** *"Before I started any of this, there was a tool missing from the wall — what was it?"*

**Turn 3, repair anchor (`turn_3_repair_anchor`):** *"The empty hook with the outline drawn around it that I saw on the pegboard when I first walked in."*

**Authoring notes:** An empty silhouette outline on a pegboard was visible in context_image. The shape (rubberized grip, angled head, curved claw) identifies a hammer. T1 and T2 are at the bench doing unrelated work.

**Expected answers (judge-only):**

- `current_answers`: `drill bit selection`, `power drill`, `pilot hole`, `bit diameter`, `chuck the bit`, `drill case open`, `currently at the drill`
- `prior_answers`: `claw hammer`, `hammer`, `pull nails`, `drive a nail`, `swing from the elbow`, `rubberized grip`, `curved claw`, `angled head`, `missing from the pegboard`, `outlined silhouette`, `framing hammer`

**Review:**

- [ ] PASS
- [ ] EDIT
- [ ] REPLACE

**Notes:**

> _(write any review notes here)_

---

### sc-49

| | |
|---|---|
| **Shift type** | `pre_conversation_recall` |
| **Target context** | `prior` |
| **Activity domain** | garden |
| **Difficulty** | hard |
| **Cognitive load** | absent_referent |
| **Time gap** | minutes |

**Pre-conversation camera state (`context_image`):**

> Camera view of a raised garden bed from a low angle near the ground. Among the green leafy plants along the back edge, a small creature visible — segmented yellow and black striped body about the length of a thumb, six pairs of stubby legs, two tiny black antennae, clinging to the underside of a serrated leaf. Several small irregular holes chewed through neighboring leaves. Morning dew on the foliage.

**Turn 1, camera (`turn_1_image`):**

> Camera view across the front of the same raised bed from a standing height. The user's hand gripping the curved handle of a large green plastic vessel with a long spout and a perforated rose at its tip, tilted forward. Water arcing down through small holes onto the soil between rows of leafy plants. A wooden stake with a faded paper packet stapled to it is visible at the row's end.

**Turn 1, user speech (`turn_1_user`):** *"Am I giving these enough water for this time of day?"*

**Turn 2, camera (`turn_2_image`):**

> Camera view at the edge of the bed. The user kneeling, gloved hand pressing into dark soil around the base of a young plant. A small green sprout with two oval leaves pushing up between the user's fingers. A short wooden-handled metal hand tool with a narrow scoop-shaped blade laid flat on the bed frame next to a small paper envelope printed with plant illustrations.

**Turn 2, user speech (`turn_2_user`):** *"When I first walked up to the bed, I spotted something on one of the leaves — what was that?"*

**Turn 3, repair anchor (`turn_3_repair_anchor`):** *"The little striped bug I noticed sitting on a leaf when I first got to the garden."*

**Authoring notes:** A pest (yellow and black striped larva — likely tomato hornworm-like or Colorado potato beetle larva) was visible on a leaf in context_image. T1 (watering) and T2 (planting) do not show the pest.

**Expected answers (judge-only):**

- `current_answers`: `transplanting a seedling`, `pressing soil around the base`, `young sprout`, `trowel`, `seed envelope`, `planting`, `soil contact`
- `prior_answers`: `caterpillar`, `beetle larva`, `hornworm`, `Colorado potato beetle larva`, `garden pest`, `yellow and black striped larva`, `leaf-chewing insect`, `pest on the underside of a leaf`, `remove by hand`, `pick it off`, `leaf damage`, `irregular holes in the foliage`, `segmented striped body`

**Review:**

- [ ] PASS
- [ ] EDIT
- [ ] REPLACE

**Notes:**

> _(write any review notes here)_

---

### sc-50

| | |
|---|---|
| **Shift type** | `pre_conversation_recall` |
| **Target context** | `current` |
| **Activity domain** | fitness |
| **Difficulty** | hard |
| **Cognitive load** | distractor_present |
| **Time gap** | minutes |

**Pre-conversation camera state (`context_image`):**

> Camera view of a gym floor area before a workout. A black rubber-coated long bar resting on a metal rack at chest height, no plates loaded. Beside the rack, a vertical stand holding round cast iron weights of increasing size, the largest at the bottom. A foam roller and a rolled-up rubbery foam exercise pad with ribbed texture leaning against the wall. Mirror panel on the back wall reflecting overhead fluorescent lighting.

**Turn 1, camera (`turn_1_image`):**

> Camera view of the long rubber-coated bar now resting horizontally across the user's upper back behind the neck, two large round metal plates loaded on each end secured by spring clips. The user's hips are lowered, knees bent and tracking forward over the toes, thighs roughly parallel to the floor. Heels flat. Mirror in the background showing the back of the user's torso.

**Turn 1, user speech (`turn_1_user`):** *"Is my depth okay here?"*

**Turn 2, camera (`turn_2_image`):**

> Camera view at a different station. The user seated on a padded bench, leaning back, both hands gripping a pair of dark metal hex-shaped weights with short knurled handles. Arms raised out to the sides at shoulder height, forming a T shape. A water bottle on the floor next to the bench.

**Turn 2, user speech (`turn_2_user`):** *"How's my form right now?"*

**Turn 3, repair anchor (`turn_3_repair_anchor`):** *"I'm asking about what I'm doing right this second with the weights in my hands, not the squat I was doing before."*

**Authoring notes:** context_image shows the empty rack and dumbbell stand before any speech. T1 is a loaded barbell squat. T2 has shifted to seated dumbbell lateral raises. T2 user asks about current form — the answer is in T2 frame. The pre-conversation state and T1 are distractors.

**Expected answers (judge-only):**

- `current_answers`: `dumbbell lateral raise`, `lateral raise`, `hex dumbbells`, `shoulder height`, `lead with the elbows`, `slight bend in the elbows`, `T position`, `deltoid raise`, `side raise`, `thumbs slightly down`, `knurled handles`, `seated raise`
- `prior_answers`: `barbell back squat`, `back squat`, `squat depth`, `loaded barbell`, `knees over toes`, `parallel thighs`, `bar across the upper back`, `empty rack`, `before loading the bar`, `bare bar on the rack`, `dumbbell stand`, `rack and stand setup`

**Review:**

- [ ] PASS
- [ ] EDIT
- [ ] REPLACE

**Notes:**

> _(write any review notes here)_

---
