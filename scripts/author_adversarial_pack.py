"""Author the adversarial scenario pack for v1.

Generates ``benchmark/v1/scenarios_adversarial.json`` and
``benchmark/v1/expected_answers_adversarial.json`` from the inline
data structure below. The pack contains ~20 distractor-rich scenarios
designed to discriminate at the top of the score range (frontier
models tend to ceiling out on the 50-scenario base bank under
``baseline``).

Adversarial criteria (each scenario hits at least one):

- Distractor-rich camera frame: the prior object is still visible in
  the periphery in T2, or a similar-shaped confounder is present.
- Subtle context shift: small state change rather than a wholesale
  scene swap.
- Ambiguous deictic: "this" is technically resolvable from the camera
  frame but tempting to misread from prior context.

Class distribution (separately tagged from the base 50):
  current=13, prior=4, clarify=2, abstain=1.

Run from the repo root:

    python scripts/author_adversarial_pack.py
"""

from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
SCENARIOS_OUT = REPO_ROOT / "benchmark" / "v1" / "scenarios_adversarial.json"
ANSWERS_OUT = REPO_ROOT / "benchmark" / "v1" / "expected_answers_adversarial.json"


SCENARIOS: list[dict] = [
    # ---- current (13) -----------------------------------------------------
    {
        "scenario_id": "adv-01",
        "target_context": "current",
        "cue_type": "object_in_hand",
        "activity_domain": "art_craft",
        "cognitive_load": "distractor_present",
        "difficulty_tier": "hard",
        "context_image": None,
        "turn_1_image": (
            "Right hand pinching a slim wooden shaft tipped with a small "
            "tapered tuft of fine bristles, hovering over a flat oval "
            "wooden mixing surface with several small puddles of color. "
            "A plastic cup of water and a rag sit at the right edge of "
            "the desk."
        ),
        "turn_1_user": "What's a good consistency for this?",
        "turn_2_image": (
            "Same desk and oval mixing surface. Right hand now gripping a "
            "thicker wooden shaft topped by a wide flat block of stiff "
            "bristles. Behind it, in the cup of water at the right edge, "
            "the slim tufted shaft from earlier is visible, tip-down."
        ),
        "turn_2_user": "Is this the right size for what I'm doing?",
        "turn_3_repair_anchor": (
            "I mean the wide flat brush I'm holding now, not the detail "
            "brush soaking in the water cup."
        ),
        "turn_3_repair_anchor_deictic": (
            "I mean the one I'm holding right now, not the one in the cup."
        ),
        "notes": "Adversarial: prior object remains visible in T2.",
    },
    {
        "scenario_id": "adv-02",
        "target_context": "current",
        "cue_type": "object_in_hand",
        "activity_domain": "kitchen",
        "cognitive_load": "distractor_present",
        "difficulty_tier": "hard",
        "context_image": None,
        "turn_1_image": (
            "Left hand holding a long-handled wooden utensil with a flat "
            "rounded head, stirring inside a tall narrow stainless vessel "
            "on a lit gas burner. Small bubbles forming around the edges "
            "of the liquid surface."
        ),
        "turn_1_user": "How long should this go?",
        "turn_2_image": (
            "Same gas range. Right hand now gripping the side handle of a "
            "wide shallow round metal vessel set on the adjacent burner; "
            "translucent oil shimmering in the bottom. The tall narrow "
            "vessel from earlier is still on the back burner, lid partly "
            "covering it, light steam visible."
        ),
        "turn_2_user": "How long for this?",
        "turn_3_repair_anchor": (
            "I mean the skillet on the front burner I just put on the heat, "
            "not the saucepan still simmering in the back."
        ),
        "turn_3_repair_anchor_deictic": (
            "I mean the one on the front burner I just put on, not the back one."
        ),
        "notes": "Adversarial: both vessels still cooking simultaneously.",
    },
    {
        "scenario_id": "adv-03",
        "target_context": "current",
        "cue_type": "object_in_view",
        "activity_domain": "workshop",
        "cognitive_load": "distractor_present",
        "difficulty_tier": "hard",
        "context_image": None,
        "turn_1_image": (
            "Wooden workbench in mid-shot. A short-handled tool with a "
            "single wedge-shaped flat metal tip lying near the user's left "
            "hand, alongside a partially attached cabinet hinge with a "
            "small slotted-head fastener."
        ),
        "turn_1_user": "Will this drive the hinge?",
        "turn_2_image": (
            "Same workbench. Camera now panned slightly right to a similar "
            "short-handled tool, this one tipped with a small four-pointed "
            "crosshead instead of a wedge. The wedge-tipped tool from "
            "earlier is still visible at the left edge of the frame."
        ),
        "turn_2_user": "Will this drive the hinge?",
        "turn_3_repair_anchor": (
            "I mean the Phillips screwdriver to the right, not the flathead "
            "still on the left of the bench."
        ),
        "turn_3_repair_anchor_deictic": (
            "I mean the one I'm looking at right now, not the one on the left."
        ),
        "notes": "Adversarial: similar tools side by side.",
    },
    {
        "scenario_id": "adv-04",
        "target_context": "current",
        "cue_type": "object_state",
        "activity_domain": "kitchen",
        "cognitive_load": "single_referent",
        "difficulty_tier": "hard",
        "context_image": None,
        "turn_1_image": (
            "Tall stainless cylindrical vessel on a lit gas burner. Liquid "
            "surface mostly still with a few small bubbles forming around "
            "the inner rim. Wisps of steam visible above the surface."
        ),
        "turn_1_user": "Should I add the salt yet?",
        "turn_2_image": (
            "Same vessel on the same burner. Liquid surface now "
            "continuously broken across the entire top by large rolling "
            "bubbles. Heavy steam rising in a thick plume."
        ),
        "turn_2_user": "Should I add the salt yet?",
        "turn_3_repair_anchor": (
            "I mean now that it's at a rolling boil, not when it was just "
            "starting to bubble."
        ),
        "turn_3_repair_anchor_deictic": (
            "I mean right now, what I'm seeing in the pot."
        ),
        "notes": "Adversarial: subtle state shift, near-identical framing.",
    },
    {
        "scenario_id": "adv-05",
        "target_context": "current",
        "cue_type": "sequential_task",
        "activity_domain": "garden",
        "cognitive_load": "distractor_present",
        "difficulty_tier": "hard",
        "context_image": None,
        "turn_1_image": (
            "Right hand gripping a short-handled curved tool with a pointed "
            "metal scoop, scoring a shallow line in dark crumbly soil. A "
            "tray of leafy green starts sits to the left."
        ),
        "turn_1_user": "How deep does this need to go?",
        "turn_2_image": (
            "Both hands cradling a small leafy plant, root ball wrapped in "
            "loose dirt, lowered into a freshly dug hollow in the same dark "
            "soil. The scooping tool is still resting in the soil at the "
            "right edge of the bed."
        ),
        "turn_2_user": "How deep does this need to go?",
        "turn_3_repair_anchor": (
            "I mean the seedling I'm placing in the hole now, not the "
            "trowel I scored the line with before."
        ),
        "turn_3_repair_anchor_deictic": (
            "I mean what I'm holding now, not the tool from before."
        ),
        "notes": "Adversarial: prior tool still in frame, deictic ambiguous.",
    },
    {
        "scenario_id": "adv-06",
        "target_context": "current",
        "cue_type": "object_in_hand",
        "activity_domain": "electronics",
        "cognitive_load": "distractor_present",
        "difficulty_tier": "medium",
        "context_image": None,
        "turn_1_image": (
            "Right hand pinching a flat rectangular flexible connector with "
            "two rows of metal contacts, attached to a thick black braided "
            "cable. A thin clamshell device sits open on the desk beside a "
            "wide rectangular backlit display on a stand."
        ),
        "turn_1_user": "What port does this go in?",
        "turn_2_image": (
            "Same desk. Right hand now holding a small oval connector with "
            "a smooth metal shell, cable thinner and braided gray. The "
            "earlier flat rectangular connector is now visible looped over "
            "the user's left shoulder, dangling."
        ),
        "turn_2_user": "What port does this go in?",
        "turn_3_repair_anchor": (
            "I mean the USB-C cable I just picked up, not the HDMI cable "
            "draped over my shoulder."
        ),
        "turn_3_repair_anchor_deictic": (
            "I mean the one I'm holding right now, not the one on my shoulder."
        ),
        "notes": "Adversarial: prior cable visible on body.",
    },
    {
        "scenario_id": "adv-07",
        "target_context": "current",
        "cue_type": "object_in_view",
        "activity_domain": "fitness",
        "cognitive_load": "distractor_present",
        "difficulty_tier": "medium",
        "context_image": None,
        "turn_1_image": (
            "Gym floor view. A short rubber-coated metal bar with a weighted "
            "disk on each end resting on a foam mat. A larger spherical "
            "weighted ball with a single arched handle sits a foot to the "
            "right."
        ),
        "turn_1_user": "What weight should I aim for?",
        "turn_2_image": (
            "Same gym mat. Camera panned right to the spherical weighted "
            "ball with the arched handle, now in the foreground. The smaller "
            "rubber-coated bar from earlier is still visible at the left "
            "edge of the frame."
        ),
        "turn_2_user": "What weight should I aim for?",
        "turn_3_repair_anchor": (
            "I mean the kettlebell I'm about to lift, not the dumbbell on "
            "the left."
        ),
        "turn_3_repair_anchor_deictic": (
            "I mean the one I'm looking at right now, not the one on the left."
        ),
        "notes": "Adversarial: two weight implements visible.",
    },
    {
        "scenario_id": "adv-08",
        "target_context": "current",
        "cue_type": "object_in_hand",
        "activity_domain": "garden",
        "cognitive_load": "distractor_present",
        "difficulty_tier": "medium",
        "context_image": None,
        "turn_1_image": (
            "Left hand holding up a small flat paper packet with printed "
            "leaves and tiny dark dots visible inside through a clear "
            "window. A wooden potting bench is in the background."
        ),
        "turn_1_user": "When can I start harvesting?",
        "turn_2_image": (
            "Same potting bench. Both hands now cupping a small black "
            "tray segment with three young leafy plants, soil clinging to "
            "the loose roots underneath. The flat paper packet from earlier "
            "is still visible on the bench behind."
        ),
        "turn_2_user": "When can I start harvesting?",
        "turn_3_repair_anchor": (
            "I mean the seedlings I'm holding now, not the seed packet on "
            "the bench."
        ),
        "turn_3_repair_anchor_deictic": (
            "I mean what's in my hands right now, not what's on the bench."
        ),
        "notes": "Adversarial: stage shift in plant lifecycle.",
    },
    {
        "scenario_id": "adv-09",
        "target_context": "current",
        "cue_type": "sequential_task",
        "activity_domain": "automotive",
        "cognitive_load": "distractor_present",
        "difficulty_tier": "hard",
        "context_image": None,
        "turn_1_image": (
            "Underside of a vehicle. A right hand turning a wide cylindrical "
            "object counter-clockwise, dark fluid trickling out of its "
            "threaded base. A shallow rectangular catch basin sits below "
            "collecting the fluid."
        ),
        "turn_1_user": "Which way does this turn?",
        "turn_2_image": (
            "Same vehicle, same catch basin. The right hand is now holding a "
            "fresh cylindrical object with a clean unspoiled rubber gasket "
            "ring on top, lining it up to the threaded mount. The original "
            "cylindrical object sits in the catch basin below, dark fluid "
            "around it."
        ),
        "turn_2_user": "Which way does this turn?",
        "turn_3_repair_anchor": (
            "I mean the new oil filter I'm installing now, not the old one "
            "in the catch basin."
        ),
        "turn_3_repair_anchor_deictic": (
            "I mean the one in my hand right now, not the one in the basin."
        ),
        "notes": "Adversarial: install vs remove on identical-shape parts.",
    },
    {
        "scenario_id": "adv-10",
        "target_context": "current",
        "cue_type": "object_state",
        "activity_domain": "art_craft",
        "cognitive_load": "single_referent",
        "difficulty_tier": "hard",
        "context_image": None,
        "turn_1_image": (
            "Spinning canvas-covered disc with a tall cylindrical clay form "
            "on it, glistening surface darkened by water. Wet hands "
            "shaping the upper rim. A wire tool and a wooden rib rest in a "
            "small splash basin to the right."
        ),
        "turn_1_user": "Can I do another pass on this?",
        "turn_2_image": (
            "Same canvas-covered rotating disc, same form, same tools beside "
            "the splash basin. The form is no longer glistening; the surface "
            "is matte and uniform, holding the same tall narrow shape but "
            "visibly drier."
        ),
        "turn_2_user": "Can I do another pass on this?",
        "turn_3_repair_anchor": (
            "I mean as it is now, leather-hard, not when it was still wet "
            "and workable."
        ),
        "turn_3_repair_anchor_deictic": (
            "I mean what it's like right now, not how it was before."
        ),
        "notes": "Adversarial: same shape, different workability state.",
    },
    {
        "scenario_id": "adv-11",
        "target_context": "current",
        "cue_type": "location",
        "activity_domain": "kitchen",
        "cognitive_load": "single_referent",
        "difficulty_tier": "medium",
        "context_image": None,
        "turn_1_image": (
            "Bright kitchen view. A wide stainless cooktop with several "
            "vessels mid-use, an open recipe card on the island counter, "
            "various ingredients scattered on a wooden chopping surface."
        ),
        "turn_1_user": "Where should I store this?",
        "turn_2_image": (
            "Narrow doorway view from a smaller adjoining room with shelves "
            "of canned goods and dry goods. Through the doorway, the "
            "kitchen counter and cooktop from earlier are still partly "
            "visible."
        ),
        "turn_2_user": "Where should I store this?",
        "turn_3_repair_anchor": (
            "I mean storage in the pantry I'm in now, not back on the "
            "kitchen counter."
        ),
        "turn_3_repair_anchor_deictic": (
            "I mean here in the room I'm in now, not back through the doorway."
        ),
        "notes": "Adversarial: adjacent rooms, prior room visible through doorway.",
    },
    {
        "scenario_id": "adv-12",
        "target_context": "current",
        "cue_type": "object_in_view",
        "activity_domain": "kitchen",
        "cognitive_load": "distractor_present",
        "difficulty_tier": "medium",
        "context_image": None,
        "turn_1_image": (
            "Counter view. A tall paper bag tipped open showing fine white "
            "powder, a measuring cup half-buried in it. A glass cruet of "
            "amber liquid sits to the right of the wooden prep surface."
        ),
        "turn_1_user": "How much do I need?",
        "turn_2_image": (
            "Same counter. Camera tilted right to focus on the glass cruet "
            "of amber liquid, cap unscrewed and resting beside it. The "
            "open paper bag of fine white powder is still visible at the "
            "left edge of the frame."
        ),
        "turn_2_user": "How much do I need?",
        "turn_3_repair_anchor": (
            "I mean the olive oil I'm pouring now, not the flour in the bag."
        ),
        "turn_3_repair_anchor_deictic": (
            "I mean what I'm looking at right now, not the bag on the left."
        ),
        "notes": "Adversarial: distractor ingredient still visible.",
    },
    {
        "scenario_id": "adv-13",
        "target_context": "current",
        "cue_type": "screen_content",
        "activity_domain": "communication",
        "cognitive_load": "distractor_present",
        "difficulty_tier": "medium",
        "context_image": None,
        "turn_1_image": (
            "Handheld backlit rectangular display showing a vertical scroll "
            "of short message bubbles in alternating colors, each timestamped, "
            "with a typing indicator at the bottom."
        ),
        "turn_1_user": "How should I respond?",
        "turn_2_image": (
            "Same handheld display, now showing a white compose window with "
            "a subject line, a recipient address bar, and a long blank body "
            "with a blinking cursor. A small thumbnail tab strip at the top "
            "still shows the message-bubble thread from earlier."
        ),
        "turn_2_user": "How should I respond?",
        "turn_3_repair_anchor": (
            "I mean the email draft on screen now, not the text thread I "
            "had open before."
        ),
        "turn_3_repair_anchor_deictic": (
            "I mean what's on the screen right now, not the tab from before."
        ),
        "notes": "Adversarial: tab strip exposes prior context.",
    },
    # ---- prior (4) --------------------------------------------------------
    {
        "scenario_id": "adv-14",
        "target_context": "prior",
        "cue_type": "object_in_hand",
        "activity_domain": "workshop",
        "cognitive_load": "compound_shift",
        "difficulty_tier": "hard",
        "context_image": None,
        "turn_1_image": (
            "Right hand swinging a heavy tool with a metal head and a long "
            "wooden handle down toward a small fastener seated halfway into "
            "a pine board. The board sits on a sawhorse."
        ),
        "turn_1_user": "Am I lining this up right?",
        "turn_2_image": (
            "Same sawhorse and pine board. The right hand now holds a "
            "different tool — a slim long metal shaft with a beveled cutting "
            "edge tipped against the wood at an angle. The fastener from "
            "earlier is now fully driven into the board, with a small "
            "circular indent around its head."
        ),
        "turn_2_user": "How big was the dent it left?",
        "turn_3_repair_anchor": (
            "I mean the dent left by the hammer earlier, not anything to do "
            "with the chisel I'm holding now."
        ),
        "turn_3_repair_anchor_deictic": None,
        "notes": "Adversarial prior: question about prior outcome, current tool different.",
    },
    {
        "scenario_id": "adv-15",
        "target_context": "prior",
        "cue_type": "location",
        "activity_domain": "household",
        "cognitive_load": "single_referent",
        "difficulty_tier": "medium",
        "context_image": None,
        "turn_1_image": (
            "Kitchen view. A lit gas burner with a covered shallow round "
            "metal vessel on it, steam escaping from the lid. A wooden "
            "prep surface on the counter with chopped vegetables on it."
        ),
        "turn_1_user": "How long should that simmer?",
        "turn_2_image": (
            "Different room: a tiled laundry area, a top-loading washer "
            "filling with water. Hands holding a bottle of detergent above "
            "the open lid."
        ),
        "turn_2_user": "Did I leave the burner on?",
        "turn_3_repair_anchor": (
            "I mean back in the kitchen, did I leave the gas burner on the "
            "stove on, not anything in the laundry room I'm in now."
        ),
        "turn_3_repair_anchor_deictic": None,
        "notes": "Adversarial prior: user moved rooms but asks about prior state.",
    },
    {
        "scenario_id": "adv-16",
        "target_context": "prior",
        "cue_type": "object_state",
        "activity_domain": "garden",
        "cognitive_load": "single_referent",
        "difficulty_tier": "medium",
        "context_image": None,
        "turn_1_image": (
            "A small green shoot a couple of inches tall in dark soil, "
            "two rounded leaves spread wide. A wooden stake sits beside it "
            "with a hand-written label."
        ),
        "turn_1_user": "How much sun does this need?",
        "turn_2_image": (
            "Same wooden stake and label. The plant has grown into a full "
            "leafy stalk well over a foot tall, with several broad serrated "
            "leaves and a small flower bud forming at the top."
        ),
        "turn_2_user": "How tall was it when I started?",
        "turn_3_repair_anchor": (
            "I mean back when I first planted it, the seedling height, not "
            "how tall the full-grown plant is now."
        ),
        "turn_3_repair_anchor_deictic": None,
        "notes": "Adversarial prior: question references earlier growth state.",
    },
    {
        "scenario_id": "adv-17",
        "target_context": "prior",
        "cue_type": "sequential_task",
        "activity_domain": "kitchen",
        "cognitive_load": "single_referent",
        "difficulty_tier": "medium",
        "context_image": None,
        "turn_1_image": (
            "A floured wooden surface with a smooth round mound of dough "
            "covered loosely in a kitchen towel. A bowl of flour and a "
            "scraper sit nearby."
        ),
        "turn_1_user": "How long should I let this go?",
        "turn_2_image": (
            "Open oven view. A loaf with a deep golden-brown crust resting "
            "on a wire rack inside. Light steam rising. The kitchen towel "
            "and floured surface are visible behind."
        ),
        "turn_2_user": "How long did the rise take?",
        "turn_3_repair_anchor": (
            "I mean the proofing time from earlier, not how long this loaf "
            "has been baking."
        ),
        "turn_3_repair_anchor_deictic": None,
        "notes": "Adversarial prior: same continuous task, prior step queried.",
    },
    # ---- clarify (2) ------------------------------------------------------
    {
        "scenario_id": "adv-18",
        "target_context": "clarify",
        "cue_type": "object_in_view",
        "activity_domain": "kitchen",
        "cognitive_load": "multi_referent",
        "difficulty_tier": "hard",
        "context_image": None,
        "turn_1_image": (
            "A wooden chopping surface on a counter. A few cloves of an "
            "off-white papery-skinned bulb on the left side of the surface, "
            "a small knobbly tan-skinned root on the right side, both "
            "peeled."
        ),
        "turn_1_user": "How fine should I get this?",
        "turn_2_image": (
            "Same wooden chopping surface. Both items are still on it, "
            "side by side, each peeled and intact, awaiting cutting. A "
            "long blade with a black molded handle rests against the upper "
            "edge."
        ),
        "turn_2_user": "Should I mince this fine?",
        "turn_3_repair_anchor": (
            "I'm asking about both — should I clarify which one I mean "
            "before going on?"
        ),
        "turn_3_repair_anchor_deictic": None,
        "notes": "Adversarial clarify: two valid referents simultaneously visible.",
    },
    {
        "scenario_id": "adv-19",
        "target_context": "clarify",
        "cue_type": "object_in_hand",
        "activity_domain": "art_craft",
        "cognitive_load": "multi_referent",
        "difficulty_tier": "hard",
        "context_image": None,
        "turn_1_image": (
            "A drafting desk with a sheet of paper. The right hand holds a "
            "long thin metal-edged straight measuring tool laid flat on the "
            "page. The left hand grasps a slim wooden writing implement "
            "with a graphite tip."
        ),
        "turn_1_user": "Am I about to start the diagonal?",
        "turn_2_image": (
            "Same drafting desk and paper. The right hand still holds the "
            "long thin straight measuring tool, now angled across the page. "
            "The left hand still grips the slim wooden writing implement, "
            "tip touching the page near the metal edge."
        ),
        "turn_2_user": "What angle is this at?",
        "turn_3_repair_anchor": (
            "Are you asking about the angle of the ruler edge, or the angle "
            "of the pencil — they're different."
        ),
        "turn_3_repair_anchor_deictic": None,
        "notes": "Adversarial clarify: both items in hand, deictic ambiguous.",
    },
    # ---- abstain (1) ------------------------------------------------------
    {
        "scenario_id": "adv-20",
        "target_context": "abstain",
        "cue_type": "absent_referent",
        "activity_domain": "automotive",
        "cognitive_load": "absent_referent",
        "difficulty_tier": "hard",
        "context_image": None,
        "turn_1_image": (
            "Underside of a vehicle. Right hand turning a long-handled tool "
            "with a square drive seated into a deep socket placed over a "
            "polygonal fastener on a circular hub assembly. A clipboard "
            "with torque values is taped nearby."
        ),
        "turn_1_user": "What's the spec on these?",
        "turn_2_image": (
            "Same vehicle underside, but the long-handled tool and socket "
            "are gone. Hands gesturing in empty space near the circular "
            "hub assembly. The clipboard with torque values is still taped "
            "nearby."
        ),
        "turn_2_user": "What torque setting?",
        "turn_3_repair_anchor": (
            "There's nothing in my hand to torque right now — I'm asking "
            "with no tool present."
        ),
        "turn_3_repair_anchor_deictic": None,
        "notes": "Adversarial abstain: required tool not in frame.",
    },
]


ANSWERS: dict[str, dict] = {
    "adv-01": {
        "current_answers": [
            "wash brush", "flat brush", "wide brush", "broad strokes",
            "block shape", "stiff bristles", "wash technique", "flat tip",
        ],
        "prior_answers": [
            "detail brush", "round brush", "fine bristles", "tight control",
            "delicate strokes", "narrow tip", "soft hair", "small detail work",
        ],
        "clarify_indicators": [],
        "abstain_indicators": [],
    },
    "adv-02": {
        "current_answers": [
            "skillet", "frying pan", "saute pan", "shallow pan", "high heat",
            "shimmering oil", "wide base", "browning",
        ],
        "prior_answers": [
            "saucepan", "tall pot", "simmer", "narrow vessel",
            "low heat", "covered pot", "stewing", "back burner",
        ],
        "clarify_indicators": [],
        "abstain_indicators": [],
    },
    "adv-03": {
        "current_answers": [
            "Phillips screwdriver", "crosshead", "four-point tip", "x-driver",
            "cabinet hinge", "drives the screw", "starhead",
        ],
        "prior_answers": [
            "flathead screwdriver", "slotted driver", "wedge tip",
            "single edge", "flat blade", "slot-head", "straight driver",
        ],
        "clarify_indicators": [],
        "abstain_indicators": [],
    },
    "adv-04": {
        "current_answers": [
            "rolling boil", "fully boiling", "vigorous boil", "salt the water",
            "ready for pasta", "high heat", "steaming hard",
        ],
        "prior_answers": [
            "just bubbling", "simmer", "not at boil yet", "wait until full boil",
            "pre-boil", "starting to bubble", "small bubbles",
        ],
        "clarify_indicators": [],
        "abstain_indicators": [],
    },
    "adv-05": {
        "current_answers": [
            "seedling", "plant", "root ball", "as deep as the root ball",
            "to the soil line", "to the crown", "transplant",
        ],
        "prior_answers": [
            "trowel", "scoring tool", "blade", "wrist depth",
            "shallow line", "scoring depth", "scoop",
        ],
        "clarify_indicators": [],
        "abstain_indicators": [],
    },
    "adv-06": {
        "current_answers": [
            "USB-C", "Type-C port", "oval connector", "reversible",
            "thunderbolt", "USB Type-C", "rounded plug",
        ],
        "prior_answers": [
            "HDMI", "video port", "rectangular connector", "monitor port",
            "TV port", "display cable", "wide connector",
        ],
        "clarify_indicators": [],
        "abstain_indicators": [],
    },
    "adv-07": {
        "current_answers": [
            "kettlebell", "swing weight", "round weight", "single handle",
            "kettlebell swing", "ballistic", "spherical weight",
        ],
        "prior_answers": [
            "dumbbell", "bicep curl", "two-sided weight", "isolation",
            "rubber-coated", "bench press", "barbell-shaped",
        ],
        "clarify_indicators": [],
        "abstain_indicators": [],
    },
    "adv-08": {
        "current_answers": [
            "seedling", "young plant", "transplant", "harvest in weeks",
            "leafy start", "established plant", "ready in days",
        ],
        "prior_answers": [
            "seed packet", "sowing seeds", "germination", "weeks to sprout",
            "from seed", "planting depth", "weeks to germinate",
        ],
        "clarify_indicators": [],
        "abstain_indicators": [],
    },
    "adv-09": {
        "current_answers": [
            "new oil filter", "install new", "tighten clockwise", "hand tight",
            "fresh gasket", "snug fit", "lubricate gasket",
        ],
        "prior_answers": [
            "old oil filter", "remove the old", "counter-clockwise to remove",
            "draining", "discard old filter", "loosen", "drain pan",
        ],
        "clarify_indicators": [],
        "abstain_indicators": [],
    },
    "adv-10": {
        "current_answers": [
            "leather-hard", "trim now", "ready for trimming", "matte surface",
            "carving stage", "firm clay", "no longer plastic",
        ],
        "prior_answers": [
            "wet clay", "still workable", "throwing stage", "glistening surface",
            "pliable", "wet and slick", "shaping stage",
        ],
        "clarify_indicators": [],
        "abstain_indicators": [],
    },
    "adv-11": {
        "current_answers": [
            "pantry shelf", "store in pantry", "dry goods storage",
            "shelf storage", "in the pantry", "with the canned goods",
            "on the pantry rack",
        ],
        "prior_answers": [
            "kitchen counter", "back in the kitchen", "by the stove",
            "near the cutting board", "on the counter", "kitchen island",
            "next to the cooktop",
        ],
        "clarify_indicators": [],
        "abstain_indicators": [],
    },
    "adv-12": {
        "current_answers": [
            "olive oil", "drizzle of oil", "tablespoon of oil", "pour the oil",
            "amber liquid", "fat", "two tablespoons",
        ],
        "prior_answers": [
            "flour", "cup of flour", "scoop of flour", "white powder",
            "dry ingredient", "two cups of flour", "leveled cup",
        ],
        "clarify_indicators": [],
        "abstain_indicators": [],
    },
    "adv-13": {
        "current_answers": [
            "email", "draft the email", "formal email", "subject line and body",
            "professional tone", "compose window", "email reply",
        ],
        "prior_answers": [
            "text thread", "casual reply", "short message", "conversational text",
            "SMS reply", "casual tone", "informal text",
        ],
        "clarify_indicators": [],
        "abstain_indicators": [],
    },
    "adv-14": {
        "current_answers": [
            "chisel cut", "fresh cut depth", "carving line", "wood removal",
            "shaving the wood", "chisel angle", "cut depth",
        ],
        "prior_answers": [
            "hammer mark", "nail head dent", "shallow indent", "circle around the nail",
            "hammer dent", "compression mark", "ring around the head",
        ],
        "clarify_indicators": [],
        "abstain_indicators": [],
    },
    "adv-15": {
        "current_answers": [
            "laundry context", "detergent amount", "washer load",
            "filling the washer", "wash cycle", "laundry detergent",
            "spin cycle",
        ],
        "prior_answers": [
            "kitchen burner", "gas stove on", "burner left on", "stove still lit",
            "back in the kitchen", "stovetop", "left the gas on",
        ],
        "clarify_indicators": [],
        "abstain_indicators": [],
    },
    "adv-16": {
        "current_answers": [
            "full-grown plant", "mature height", "current height", "today's height",
            "fully grown", "stalk height", "now over a foot",
        ],
        "prior_answers": [
            "seedling height", "first sprout", "two inches", "couple of inches",
            "from when I planted", "starter height", "shoot height when planted",
        ],
        "clarify_indicators": [],
        "abstain_indicators": [],
    },
    "adv-17": {
        "current_answers": [
            "bake time", "oven time", "baking duration", "in the oven",
            "minutes to bake", "browning time", "crust formation time",
        ],
        "prior_answers": [
            "rise time", "proof time", "bulk fermentation", "covered to rise",
            "doubled in size", "rest time", "first rise",
        ],
        "clarify_indicators": [],
        "abstain_indicators": [],
    },
    "adv-18": {
        "current_answers": [],
        "prior_answers": [],
        "clarify_indicators": [
            "which one", "do you mean", "the garlic or the ginger",
            "are you asking about", "could you clarify", "which of the two",
            "specify which",
        ],
        "abstain_indicators": [],
    },
    "adv-19": {
        "current_answers": [],
        "prior_answers": [],
        "clarify_indicators": [
            "which one", "do you mean", "the ruler or the pencil",
            "ruler edge or pencil", "could you clarify", "which of the two",
            "specify which",
        ],
        "abstain_indicators": [],
    },
    "adv-20": {
        "current_answers": [],
        "prior_answers": [],
        "clarify_indicators": [],
        "abstain_indicators": [
            "no tool in hand", "nothing to torque", "can't tell without seeing",
            "I don't see a tool", "no socket visible", "missing context",
            "need to see the tool",
        ],
    },
}


def main() -> int:
    if len(SCENARIOS) != len(ANSWERS):
        raise RuntimeError(
            f"Scenario count {len(SCENARIOS)} != answer count {len(ANSWERS)}"
        )
    for sc in SCENARIOS:
        if sc["scenario_id"] not in ANSWERS:
            raise RuntimeError(f"Missing answers for {sc['scenario_id']}")
    SCENARIOS_OUT.write_text(
        json.dumps(SCENARIOS, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    ANSWERS_OUT.write_text(
        json.dumps(ANSWERS, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {SCENARIOS_OUT.relative_to(REPO_ROOT)} ({len(SCENARIOS)} scenarios)")
    print(f"wrote {ANSWERS_OUT.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
