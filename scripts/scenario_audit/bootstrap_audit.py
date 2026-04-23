#!/usr/bin/env python3
"""Generate and validate scenario-audit artifacts for canonical v1."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
SCENARIOS_PATH = REPO_ROOT / "benchmark" / "v1" / "scenarios.json"
EXPECTED_ANSWERS_PATH = REPO_ROOT / "benchmark" / "v1" / "expected_answers.json"

ALLOWED_ALIGNMENTS = {
    "core-aligned",
    "core-misaligned",
    "auxiliary-aligned",
    "auxiliary-misaligned",
}
ALLOWED_EVIDENCE_STATUSES = {
    "answerable-from-release",
    "depends-on-missing-visual",
    "depends-on-missing-audio",
    "underspecified-by-design",
    "unanswerable-by-design",
}
ALLOWED_SCENARIO_ACTIONS = {"keep", "rewrite", "merge", "remove"}
ALLOWED_ANSWER_KEY_ACTIONS = {"keep", "rewrite"}
ALLOWED_SEVERITIES = {"low", "medium", "high"}
ALLOWED_ISSUE_TYPES = {
    "hidden_visual_dependency",
    "hidden_audio_dependency",
    "text_recall_too_easy",
    "clarify_vs_abstain_blur",
    "answer_key_too_generic",
    "answer_key_misaligned",
    "target_label_mismatch",
    "turn_2_too_open_ended",
    "repair_anchor_leak",
    "near_duplicate",
    "missing_release_evidence",
    "weak_product_relevance",
}

RESEARCH_SOURCES = [
    {
        "name": "BetterBench",
        "url": "https://betterbench.stanford.edu/methodology.html",
        "reason": "benchmark quality, transparency, and evaluation hygiene",
    },
    {
        "name": "HELM",
        "url": "https://crfm.stanford.edu/2022/11/17/helm.html",
        "reason": "taxonomy clarity and bounded benchmark claims",
    },
    {
        "name": "OpenEQA",
        "url": "https://open-eqa.github.io/assets/pdfs/paper.pdf",
        "reason": "product-relevant embodied question design",
    },
    {
        "name": "MUCAR",
        "url": "https://aclanthology.org/2025.emnlp-main.760/",
        "reason": "single intended interpretation under multimodal ambiguity",
    },
    {
        "name": "Clarify When Necessary",
        "url": "https://arxiv.org/abs/2311.09469",
        "reason": "when to ask clarifying questions under ambiguity",
    },
    {
        "name": "AbstentionBench",
        "url": "https://arxiv.org/abs/2506.09038",
        "reason": "when abstention is preferable to a guessed answer",
    },
    {
        "name": "Relevant Context for DST",
        "url": "https://arxiv.org/abs/1904.02800",
        "reason": "context selection under dialogue shifts",
    },
]

DOMAIN_LABELS = {
    "home_kitchen": "Kitchen",
    "vehicle_cabin": "Vehicle",
    "home_living": "Living Room",
    "social_gathering": "Social",
    "retail": "Retail",
    "workshop": "Workshop",
    "screen_only": "Screen",
    "outdoor_yard": "Yard",
    "warehouse": "Warehouse",
    "home_office": "Home Office",
    "home_bedroom": "Bedroom",
    "library": "Library",
    "garage": "Garage",
    "gym": "Gym",
}

CUE_LABELS = {
    "spatial_shift": "Room Shift",
    "object_shift": "Object Swap",
    "verbal_deictic": "Deictic Reference",
    "temporal_state": "State Change",
    "object_departure": "Departure Recall",
    "object_return": "Return Recall",
    "blended": "Blended Shift",
}

GENERIC_ANSWER_PHRASES = (
    "now",
    "depends on",
    "depends what's on",
    "let me see",
    "current",
    "the new",
    "the other",
    "the window you switched to",
    "holding up",
    "how many",
    "roughly halfway",
    "about halfway",
)

WEAK_PRODUCT_RELEVANCE: set[str] = set()
HIDDEN_AUDIO_SCENARIOS: set[str] = set()
# Consolidation record: historical merges and removals from the candidate
# bank. The targets are no longer present in scenarios.json; these sets stay
# only to preserve traceability for anyone reading the audit history.
MERGE_WITH: dict[str, str] = {}
REMOVE_SCENARIOS: set[str] = set()
OPEN_ENDED_SCENARIOS = {"sc-04", "sc-12", "sc-42", "sc-43", "sc-44", "sc-84"}

CURRENT_REWRITE_HINTS: dict[str, dict[str, Any]] = {
    "sc-01": {
        "turn_2_user": "Okay, I've set the screwdriver down and picked up a claw hammer with a smooth face. Am I holding this one correctly?",
        "turn_3_repair_anchor": "I mean the hammer I'm holding now, not the screwdriver.",
        "answer_keys": {
            "current_answers": ["hammer", "claw hammer", "smooth face", "swing", "grip near the end"],
            "prior_answers": ["screwdriver", "Phillips", "magnetic tip", "rubber grip"],
            "clarify_indicators": [],
            "abstain_indicators": [],
        },
    },
    "sc-02": {
        "turn_2_user": "Alright, I've walked into the kitchen now. What art should we hang in here?",
        "turn_3_repair_anchor": "I mean the kitchen wall I'm looking at now, not the bedroom.",
        "answer_keys": {
            "current_answers": ["kitchen", "bright", "food", "simple print", "clean lines"],
            "prior_answers": ["bedroom", "sage green", "headboard", "landscape"],
            "clarify_indicators": [],
            "abstain_indicators": [],
        },
    },
    "sc-04": {
        "turn_2_user": "Alright, I've walked to the workbench. There's a half-finished shelf, a clamp, and the sander out. What should I tackle first?",
        "turn_3_repair_anchor": "I mean the workbench I'm showing you now, not my desk.",
        "answer_keys": {
            "current_answers": ["workbench", "shelf", "sander", "clamp", "finish the shelf"],
            "prior_answers": ["desk", "laptop", "coffee mug", "legal pad"],
            "clarify_indicators": [],
            "abstain_indicators": [],
        },
    },
    "sc-05": {
        "turn_2_user": "Holding up a different one now, a red-and-mustard ski poster. What about this one?",
        "turn_3_repair_anchor": "I mean the ski poster I'm holding up now, not the Lake Como one.",
        "answer_keys": {
            "current_answers": ["ski poster", "red", "mustard", "warm mat", "cream mat"],
            "prior_answers": ["Lake Como", "blue water", "cream sky", "travel poster"],
            "clarify_indicators": [],
            "abstain_indicators": [],
        },
    },
    "sc-06": {
        "turn_2_user": "Walked into the garage now. Looking at the pegboard, which tool outlines are missing here?",
        "turn_3_repair_anchor": "I mean the pegboard in front of me now, not the hydrangeas.",
        "answer_keys": {
            "current_answers": ["pegboard", "missing tool", "empty outline", "hammer outline", "pliers outline"],
            "prior_answers": ["hydrangeas", "blue flowers", "fence"],
            "clarify_indicators": [],
            "abstain_indicators": [],
        },
    },
    "sc-07": {
        "turn_2_user": "Okay it's 8:15 now and the cinnamon rolls look puffed and golden on top. What do you see?",
        "turn_3_repair_anchor": "I mean describe the rolls as they look right now, not how they looked before baking.",
        "answer_keys": {
            "current_answers": ["golden", "puffed", "browning", "tops are set", "almost done"],
            "prior_answers": ["pillowy", "rising overnight", "before baking"],
            "clarify_indicators": [],
            "abstain_indicators": [],
        },
    },
    "sc-08": {
        "turn_2_user": "Switched windows to a PagerDuty incident dashboard. Is this a production incident, and should I page someone?",
        "turn_3_repair_anchor": "I mean the incident dashboard I just switched to, not the Jira ticket.",
        "answer_keys": {
            "current_answers": ["PagerDuty", "incident dashboard", "sev", "page", "production incident"],
            "prior_answers": ["Jira", "ticket", "redis", "SRE", "checkout API"],
            "clarify_indicators": [],
            "abstain_indicators": [],
        },
    },
    "sc-10": {
        "turn_2_user": "Walked over to the chardonnay pallet now. There are only 4 cases here. Same question, should I pull more from the back?",
        "turn_3_repair_anchor": "I mean the chardonnay pallet I'm standing at now, not the cabernet.",
        "answer_keys": {
            "current_answers": ["chardonnay", "4 cases", "pull more", "need more stock"],
            "prior_answers": ["cabernet", "12 cases", "8 per week"],
            "clarify_indicators": [],
            "abstain_indicators": [],
        },
    },
    "sc-12": {
        "turn_2_user": "Moved to the family room wall now. Any suggestion for this wall?",
        "turn_3_repair_anchor": "I mean the family room wall I'm looking at now, not the nursery shelf.",
        "answer_keys": {
            "current_answers": ["family room", "larger art", "wider piece", "mirror", "gallery"],
            "prior_answers": ["nursery", "floating shelf", "changing table"],
            "clarify_indicators": [],
            "abstain_indicators": [],
        },
    },
    "sc-13": {
        "turn_2_user": "Over in the flooring aisle now, looking at wide-plank oak samples. What about this?",
        "turn_3_repair_anchor": "I mean the flooring I'm standing in front of now, not the paint.",
        "answer_keys": {
            "current_answers": ["flooring", "oak", "plank", "hallway traffic", "durable"],
            "prior_answers": ["paint", "eggshell", "Cotton Balls", "sheen"],
            "clarify_indicators": [],
            "abstain_indicators": [],
        },
    },
    "sc-14": {
        "turn_2_user": "Switched stations to the drill press. Is this one set up right?",
        "turn_3_repair_anchor": "I mean the drill press I'm standing at now, not the table saw.",
        "answer_keys": {
            "current_answers": ["drill press", "table height", "clamp the work", "bit centered"],
            "prior_answers": ["table saw", "ripping blade", "blade height"],
            "clarify_indicators": [],
            "abstain_indicators": [],
        },
    },
    "sc-15": {
        "turn_2_user": "Picked up a different avocado now. It's brighter green and rock hard. How's this one look?",
        "turn_3_repair_anchor": "I mean the avocado I'm holding now, not the first one.",
        "answer_keys": {
            "current_answers": ["not ripe", "rock hard", "needs more time", "brighter green"],
            "prior_answers": ["ripe", "dark skin", "guacamole tonight"],
            "clarify_indicators": [],
            "abstain_indicators": [],
        },
    },
    "sc-16": {
        "turn_2_user": "Picked up a Chromebook instead. How does this compare?",
        "turn_3_repair_anchor": "I mean the Chromebook in my hand now, not the ThinkPad.",
        "answer_keys": {
            "current_answers": ["Chromebook", "browser-based", "lighter", "schoolwork"],
            "prior_answers": ["ThinkPad", "16 gigs", "battery test", "first laptop"],
            "clarify_indicators": [],
            "abstain_indicators": [],
        },
    },
    "sc-17": {
        "turn_2_user": "Swapped for the trap bar on the rack. Is this the right one for my next set?",
        "turn_3_repair_anchor": "I mean the trap bar I picked up just now, not the straight bar.",
        "answer_keys": {
            "current_answers": ["trap bar", "next set", "deadlift", "neutral grip"],
            "prior_answers": ["45-pound barbell", "bar spin", "warm-up"],
            "clarify_indicators": [],
            "abstain_indicators": [],
        },
    },
    "sc-18": {
        "turn_2_user": "Checking back now. The candies look opaque and firm. Can I demold these?",
        "turn_3_repair_anchor": "Based on how they look right now, not when I poured.",
        "answer_keys": {
            "current_answers": ["yes", "opaque", "firm", "set", "ready to demold"],
            "prior_answers": ["glassy", "translucent", "liquid"],
            "clarify_indicators": [],
            "abstain_indicators": [],
        },
    },
    "sc-19": {
        "turn_2_user": "It's 7:08 now. The steaks have a dark crust and juices are beading on top. How are they?",
        "turn_3_repair_anchor": "Describe what the steaks look like on the grates right now.",
        "answer_keys": {
            "current_answers": ["dark crust", "seared", "juices", "ready to flip", "medium-rare track"],
            "prior_answers": ["just started", "7:02", "coals are red-hot"],
            "clarify_indicators": [],
            "abstain_indicators": [],
        },
    },
    "sc-20": {
        "turn_2_user": "Put it back. I'm holding a brown corduroy jacket now. This one worth it?",
        "turn_3_repair_anchor": "I mean the corduroy jacket I'm holding now, not the Levi's.",
        "answer_keys": {
            "current_answers": ["corduroy", "brown", "worth it", "good buy", "price depends on condition"],
            "prior_answers": ["Levi's", "denim", "patch", "thirty-eight dollars"],
            "clarify_indicators": [],
            "abstain_indicators": [],
        },
    },
    "sc-21": {
        "turn_2_user": "Actually, what about this one instead? It's the draft apologizing for a delayed shipment.",
        "turn_3_repair_anchor": "I mean the delay-update draft I have open right now, not the thank-you message.",
        "answer_keys": {
            "current_answers": ["delayed shipment", "apology", "shipping delay", "more formal", "specific update"],
            "prior_answers": ["thanking", "renewing", "formal sign-off", "client"],
            "clarify_indicators": [],
            "abstain_indicators": [],
        },
    },
    "sc-22": {
        "turn_2_user": "What about this one? It's a cat's-paw nail puller.",
        "turn_3_repair_anchor": "I mean the cat's-paw tool I have in my hand now, not the pliers.",
        "answer_keys": {
            "current_answers": ["cat's paw", "nail puller", "better for nails", "trim removal"],
            "prior_answers": ["slip-joint pliers", "plastic-dipped handles", "bent finishing nail"],
            "clarify_indicators": [],
            "abstain_indicators": [],
        },
    },
    "sc-23": {
        "turn_2_user": "Pulled into a gas station. The oil-pressure icon is flashing now. What's this telling me?",
        "turn_3_repair_anchor": "I mean the oil-pressure icon flashing on the dash right now, not the check-engine light from before.",
        "answer_keys": {
            "current_answers": ["oil pressure", "stop driving", "pull over", "engine damage"],
            "prior_answers": ["check-engine", "fuel at a quarter", "40 miles", "rest stop"],
            "clarify_indicators": [],
            "abstain_indicators": [],
        },
    },
    "sc-42": {
        "turn_2_user": "Walked to the trunk now. It's covered by the cargo cover and tucked behind a duffel. Is this spot more secure?",
        "turn_3_repair_anchor": "I mean the spot I'm looking at right now in the trunk, not the glove box.",
        "answer_keys": {
            "current_answers": ["trunk", "cargo cover", "behind the duffel", "more secure"],
            "prior_answers": ["glove box", "wallet", "AAA card"],
            "clarify_indicators": [],
            "abstain_indicators": [],
        },
    },
    "sc-43": {
        "turn_2_user": "Moved the laptop to the dining room. Plain wall behind me, window off to the side. What about from here?",
        "turn_3_repair_anchor": "I mean the room I'm sitting in now, not the office.",
        "answer_keys": {
            "current_answers": ["dining room", "plain wall", "side light", "good background"],
            "prior_answers": ["home office", "bookshelf", "framed print"],
            "clarify_indicators": [],
            "abstain_indicators": [],
        },
    },
    "sc-44": {
        "turn_2_user": "Moved to the rower now. Is my form okay here?",
        "turn_3_repair_anchor": "I mean the rower I'm at now, not the cable tower.",
        "answer_keys": {
            "current_answers": ["rower", "hinge", "drive with legs", "keep back neutral"],
            "prior_answers": ["cable machine", "rope attachment", "triceps pushdowns"],
            "clarify_indicators": [],
            "abstain_indicators": [],
        },
    },
    "sc-45": {
        "turn_2_user": "Set that down and picked up a pallet of ceramic tile. It's marked 1,600 pounds. How about this one?",
        "turn_3_repair_anchor": "I mean the tile pallet on my forks now, not the boxes.",
        "answer_keys": {
            "current_answers": ["tile pallet", "1,600 pounds", "within rating", "check forklift rating"],
            "prior_answers": ["kraft-paper boxes", "60 boxes", "20 pounds each"],
            "clarify_indicators": [],
            "abstain_indicators": [],
        },
    },
    "sc-46": {
        "turn_2_user": "Swapped tools. I'm holding long-handled loppers now. How about this one for the same job?",
        "turn_3_repair_anchor": "I mean the loppers in my hand now, not the shears.",
        "answer_keys": {
            "current_answers": ["loppers", "thicker branches", "boxwood might be too fine", "bigger cuts"],
            "prior_answers": ["pruning shears", "orange handles", "bypass style"],
            "clarify_indicators": [],
            "abstain_indicators": [],
        },
    },
    "sc-47": {
        "turn_2_user": "Picked up an ergonomic keyboard instead. Is this one a better pick?",
        "turn_3_repair_anchor": "I mean the keyboard I'm holding now, not the mouse.",
        "answer_keys": {
            "current_answers": ["keyboard", "ergonomic", "spreadsheet work", "typing comfort"],
            "prior_answers": ["mouse", "seven buttons", "side scroll wheel"],
            "clarify_indicators": [],
            "abstain_indicators": [],
        },
    },
    "sc-48": {
        "turn_2_user": "Back outside at 5pm. The leaves are drooping and the top growth looks limp. How are they holding up?",
        "turn_3_repair_anchor": "Describe how the seedlings look now, not at 7 this morning.",
        "answer_keys": {
            "current_answers": ["drooping", "limp", "heat stress", "needs water"],
            "prior_answers": ["deep green", "just planted", "7am"],
            "clarify_indicators": [],
            "abstain_indicators": [],
        },
    },
    "sc-49": {
        "turn_2_user": "It's noon today. The turkey looks pale and fully soaked. Ready to come out?",
        "turn_3_repair_anchor": "Describe the turkey as it is right now in the kettle, not when I put it in.",
        "answer_keys": {
            "current_answers": ["yes", "fully brined", "ready to come out", "24 hours"],
            "prior_answers": ["put it in", "14 pounds", "24 hours in the fridge"],
            "clarify_indicators": [],
            "abstain_indicators": [],
        },
    },
    "sc-50": {
        "turn_2_user": "Checking back at 9:50. The progress bar says 92 percent. How far along is it?",
        "turn_3_repair_anchor": "Look at the progress bar right now, not how it looked at 9:04.",
        "answer_keys": {
            "current_answers": ["92 percent", "92%", "almost done", "nearly finished"],
            "prior_answers": ["2 percent", "2%", "just started", "9:04"],
            "clarify_indicators": [],
            "abstain_indicators": [],
        },
    },
    "sc-51": {
        "turn_2_user": "It took off. There's a bit of fur and a wet mark on the deck board. Did anything fall?",
        "turn_3_repair_anchor": "Look at the deck board right where it was standing. Is anything left behind?",
        "answer_keys": {
            "current_answers": ["yes", "fur", "vole fur", "wet mark", "something left"],
            "prior_answers": ["hawk", "vole in its talons"],
            "clarify_indicators": [],
            "abstain_indicators": [],
        },
    },
    "sc-53": {
        "turn_2_user": "Set it back. Holding a wedge of manchego now. Same question.",
        "turn_3_repair_anchor": "I mean the manchego in my hand now, not the tomme.",
        "answer_keys": {
            "current_answers": ["manchego", "firmer", "nutty", "rioja", "tempranillo"],
            "prior_answers": ["tomme", "raw sheep's milk", "sauvignon blanc"],
            "clarify_indicators": [],
            "abstain_indicators": [],
        },
    },
    "sc-54": {
        "turn_2_user": "The flashing yellow left-turn arrow in our lane is on. Does this apply to us?",
        "turn_3_repair_anchor": "I mean the left-turn signal right in front of us now, not the overall intersection design.",
        "answer_keys": {
            "current_answers": ["left-turn arrow", "yield", "applies to your lane", "turn when clear"],
            "prior_answers": ["bike box", "two left-turn lanes", "complicated signal"],
            "clarify_indicators": [],
            "abstain_indicators": [],
        },
    },
    "sc-55": {
        "turn_2_user": "What should I do with this one? My cursor is on the highlights slider.",
        "turn_3_repair_anchor": "I mean the highlights slider my cursor is on right now, not a specific setting name.",
        "answer_keys": {
            "current_answers": ["highlights", "lower highlights", "pull highlights down", "reduce highlights"],
            "prior_answers": ["shadows", "clarity", "exposure right on a portrait"],
            "clarify_indicators": [],
            "abstain_indicators": [],
        },
    },
    "sc-56": {
        "turn_2_user": "This one, the dry riesling. What's it taste like?",
        "turn_3_repair_anchor": "I mean the dry riesling glass I'm holding right now, not a different varietal.",
        "answer_keys": {
            "current_answers": ["dry riesling", "citrus", "mineral", "crisp", "acid"],
            "prior_answers": ["pinot gris", "gewurztraminer", "flight tasting"],
            "clarify_indicators": [],
            "abstain_indicators": [],
        },
    },
    "sc-57": {
        "turn_2_user": "It's 4. Different counter now, and I'm looking at the baked ziti with bubbling cheese. Is this one done?",
        "turn_3_repair_anchor": "I mean the baked ziti I'm looking at now on the new counter, not the slow cooker.",
        "answer_keys": {
            "current_answers": ["baked ziti", "bubbling cheese", "done", "ready"],
            "prior_answers": ["slow cooker", "pulled pork", "low until 3pm"],
            "clarify_indicators": [],
            "abstain_indicators": [],
        },
    },
    "sc-82": {
        "turn_2_user": "Walked into the walk-in closet. The overhead light is bright and the mirror is clear. Is the light here enough to pick out a suit?",
        "turn_3_repair_anchor": "I mean the closet I'm standing in now, not the bedroom.",
        "answer_keys": {
            "current_answers": ["closet", "enough light", "bright enough", "good to pick a suit"],
            "prior_answers": ["bed", "duvet", "shams", "throw"],
            "clarify_indicators": [],
            "abstain_indicators": [],
        },
    },
    "sc-83": {
        "turn_2_user": "Moved to the drill press. Setup here look safe?",
        "turn_3_repair_anchor": "I mean the drill press I'm standing at now, not the table saw.",
        "answer_keys": {
            "current_answers": ["drill press", "clamp the piece", "safe setup", "bit alignment"],
            "prior_answers": ["table saw", "push stick", "blade guard"],
            "clarify_indicators": [],
            "abstain_indicators": [],
        },
    },
    "sc-84": {
        "turn_2_user": "Moved to the dining room. There's soft overhead light and no harsh window glare. Is the lighting right now good for a video call?",
        "turn_3_repair_anchor": "I mean the dining room I'm in now, not the living room.",
        "answer_keys": {
            "current_answers": ["dining room", "soft light", "good for a call", "no harsh glare"],
            "prior_answers": ["living room", "couch", "blanket", "coffee table"],
            "clarify_indicators": [],
            "abstain_indicators": [],
        },
    },
    "sc-85": {
        "turn_2_user": "Put that back. Grabbed a four-way lug wrench from the middle drawer. Is this one right for a seized lug nut?",
        "turn_3_repair_anchor": "I mean the lug wrench I'm holding now, not the drill.",
        "answer_keys": {
            "current_answers": ["lug wrench", "right for a lug nut", "better than the drill", "wheel tool"],
            "prior_answers": ["cordless drill", "bottom drawer"],
            "clarify_indicators": [],
            "abstain_indicators": [],
        },
    },
    "sc-86": {
        "turn_2_user": "Swapped attachments to the rope handle. Is the grip here better for the same move?",
        "turn_3_repair_anchor": "I mean the rope attachment I'm using now, not the single handle.",
        "answer_keys": {
            "current_answers": ["rope", "neutral grip", "better for the same move", "more range"],
            "prior_answers": ["single handle", "lower pulley", "30 pounds"],
            "clarify_indicators": [],
            "abstain_indicators": [],
        },
    },
    "sc-87": {
        "turn_2_user": "Set that down and picked up the jointer plane. Is it the right one for flattening a long board?",
        "turn_3_repair_anchor": "I mean the jointer plane in my hand now, not the block.",
        "answer_keys": {
            "current_answers": ["jointer plane", "flattening a long board", "right tool", "long sole"],
            "prior_answers": ["block plane", "round a shelf edge"],
            "clarify_indicators": [],
            "abstain_indicators": [],
        },
    },
    "sc-88": {
        "turn_2_user": "Back at 2pm. Only two pallets are still at dock 4. Are they all moved now?",
        "turn_3_repair_anchor": "I mean the dock as it looks right now, not at 9am.",
        "answer_keys": {
            "current_answers": ["not all", "two pallets left", "still at dock 4"],
            "prior_answers": ["20 pallets", "9am", "all wrapped"],
            "clarify_indicators": [],
            "abstain_indicators": [],
        },
    },
    "sc-89": {
        "turn_2_user": "It's 8:15 now. The toast is over and people are laughing near the bar. How's the energy in here now?",
        "turn_3_repair_anchor": "I mean the room right now, not when I arrived.",
        "answer_keys": {
            "current_answers": ["lively", "high energy", "laughing", "buzzing", "engaged"],
            "prior_answers": ["7pm", "mingling", "bar open"],
            "clarify_indicators": [],
            "abstain_indicators": [],
        },
    },
    "sc-90": {
        "turn_2_user": "It's 2pm. The roast still looks firm in the center when I poke it. Is it ready?",
        "turn_3_repair_anchor": "I mean the roast as it is right now, not when I put it in.",
        "answer_keys": {
            "current_answers": ["not ready", "still firm", "needs more time"],
            "prior_answers": ["11am", "3 hours", "pot roast"],
            "clarify_indicators": [],
            "abstain_indicators": [],
        },
    },
    "sc-91": {
        "turn_2_user": "He hopped off. There's still a chewed rawhide scrap on the cushion. Anything left behind?",
        "turn_3_repair_anchor": "I mean the cushion where he was, what's still there now?",
        "answer_keys": {
            "current_answers": ["rawhide", "chewed scrap", "yes", "something left"],
            "prior_answers": ["dog", "Buck", "gnawing on it"],
            "clarify_indicators": [],
            "abstain_indicators": [],
        },
    },
    "sc-92": {
        "turn_2_user": "It flew off. The lamp and water glass are still upright. Anything knocked over?",
        "turn_3_repair_anchor": "I mean the nightstand right now. Is everything where it was?",
        "answer_keys": {
            "current_answers": ["nothing knocked over", "everything is upright", "no", "still in place"],
            "prior_answers": ["moth", "nightstand", "lamp", "water glass"],
            "clarify_indicators": [],
            "abstain_indicators": [],
        },
    },
    "sc-93": {
        "turn_2_user": "She picked one and left the other two. I'm holding the MLA style guide now. Should I reshelve this one first?",
        "turn_3_repair_anchor": "I mean the MLA style guide still in my hand, not the whole stack.",
        "answer_keys": {
            "current_answers": ["MLA style guide", "reshelve this one", "the guide in hand"],
            "prior_answers": ["history atlas", "legal dictionary", "stack on my cart"],
            "clarify_indicators": [],
            "abstain_indicators": [],
        },
    },
    "sc-94": {
        "turn_2_user": "Put it back. Grabbed a bigger box-end wrench. Will this one fit?",
        "turn_3_repair_anchor": "I mean the larger wrench in my hand now, not the crescent.",
        "answer_keys": {
            "current_answers": ["bigger wrench", "box-end wrench", "will fit", "better fit"],
            "prior_answers": ["crescent wrench", "too small", "stuck bolt"],
            "clarify_indicators": [],
            "abstain_indicators": [],
        },
    },
    "sc-95": {
        "turn_2_user": "Should I try this? The bar in front of me is loaded at 185.",
        "turn_3_repair_anchor": "I mean the loaded bar I'm sitting under right now, not the spotter stand.",
        "answer_keys": {
            "current_answers": ["185", "loaded bar", "bench press", "depends on your max", "spotter recommended"],
            "prior_answers": ["spotter stand", "bench setup", "weight room"],
            "clarify_indicators": [],
            "abstain_indicators": [],
        },
    },
    "sc-96": {
        "turn_2_user": "Scrolled up in the notebook. This cell is merging on order_id while the dataframe only has customer_id. What's going wrong here?",
        "turn_3_repair_anchor": "I mean the cell I scrolled to right now, not the earlier KeyError cell.",
        "answer_keys": {
            "current_answers": ["order_id", "column mismatch", "wrong merge key", "customer_id missing"],
            "prior_answers": ["KeyError", "customer_id", "third pandas merge"],
            "clarify_indicators": [],
            "abstain_indicators": [],
        },
    },
}

PRIOR_VISUAL_REWRITES: dict[str, dict[str, Any]] = {
    "sc-09": {
        "turn_1_user": "I'm in the backyard. There's a buck in the corner, white-tailed, maybe six points, just standing by the maple tree. When he bolts, he cuts left toward the back fence. Should I move slowly to avoid spooking him?",
        "turn_2_user": "Okay, which direction did he bolt?",
        "turn_3_repair_anchor": "Based on what you saw before he ran.",
        "answer_keys": {
            "current_answers": [],
            "prior_answers": ["left", "toward the back fence", "left toward the fence"],
            "clarify_indicators": [],
            "abstain_indicators": [],
        },
    },
    "sc-30": {
        "turn_1_user": "At the block party. My neighbor Carla walked up with a casserole. She's wearing a floral apron, dark jeans, hair in a clip. When she heads out, she walks toward the mailbox side of the street.",
        "turn_2_user": "She's gone. Which direction did she leave?",
        "turn_3_repair_anchor": "Based on which way she walked off.",
        "answer_keys": {
            "current_answers": [],
            "prior_answers": ["toward the mailbox", "mailbox side", "toward the street mailbox"],
            "clarify_indicators": [],
            "abstain_indicators": [],
        },
    },
    "sc-65": {
        "turn_1_user": "Stopped at a four-way. A silver F-150 came up on my left and is trying to merge in front of me. Driver has a gray beard and a sticker on his back window, 'Semper Fi'. He never turns his signal on before pulling ahead.",
        "turn_2_user": "He's gone up ahead now. Did he ever signal?",
        "turn_3_repair_anchor": "Based on what you saw of his truck before he went.",
        "answer_keys": {
            "current_answers": [],
            "prior_answers": ["no", "never signaled", "did not signal"],
            "clarify_indicators": [],
            "abstain_indicators": [],
        },
    },
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_jsonl(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def flatten_csv_row(row: dict[str, Any]) -> dict[str, str]:
    category = row["category"]
    return {
        "scenario_id": row["scenario_id"],
        "title": row["title"],
        "description": row["description"],
        "target_context": category["target_context"],
        "cue_type": category["cue_type"],
        "activity_domain": category["activity_domain"],
        "modality_required": category["modality_required"],
        "alignment": row["alignment"],
        "evidence_status": row["evidence_status"],
        "scenario_action": row["scenario_action"],
        "answer_key_action": row["answer_key_action"],
        "severity": row["severity"],
        "issue_types": "|".join(row["issue_types"]),
        "what_works": row["what_works"],
        "what_doesnt": row["what_doesnt"],
        "gap_analysis": row["gap_analysis"],
        "overlap_with": "|".join(row["overlap_with"]),
        "recommended_changes": row["recommended_changes"],
    }


def export_csv(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    flat_rows = [flatten_csv_row(row) for row in rows]
    fieldnames = list(flat_rows[0].keys()) if flat_rows else []
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(flat_rows)


def build_title(entry: dict[str, Any]) -> str:
    domain = DOMAIN_LABELS.get(entry.get("activity_domain"), "General")
    cue = CUE_LABELS.get(entry.get("cue_type"), "Scenario")
    return f"{domain} {cue}"


def build_description(entry: dict[str, Any]) -> str:
    target = entry["target_context"]
    cue = entry.get("cue_type", "context_change").replace("_", " ")
    domain = DOMAIN_LABELS.get(entry.get("activity_domain"), entry.get("activity_domain", "general")).lower()
    if target == "current":
        return (
            f"Current-context {cue} scenario in {domain} where Turn 2 should pivot "
            f"to the newly active referent."
        )
    if target == "prior":
        return (
            f"Prior-context {cue} scenario in {domain} where Turn 2 should reach "
            f"back to an earlier referent."
        )
    if target == "clarify":
        return (
            f"Auxiliary clarify {cue} scenario in {domain} where the released inputs "
            f"leave Turn 2 under-specified."
        )
    return (
        f"Auxiliary abstain {cue} scenario in {domain} where the released inputs do "
        f"not support a grounded answer."
    )


def generic_answer_key_issue(answer_entry: dict[str, Any]) -> bool:
    current_answers = answer_entry.get("current_answers", [])
    lowered = [value.lower() for value in current_answers]
    return any(any(phrase in value for phrase in GENERIC_ANSWER_PHRASES) for value in lowered)


def evidence_status(entry: dict[str, Any]) -> str:
    if entry["scenario_id"] in HIDDEN_AUDIO_SCENARIOS:
        return "depends-on-missing-audio"
    if entry["target_context"] == "clarify":
        return "underspecified-by-design"
    if entry["target_context"] == "abstain":
        return "unanswerable-by-design"
    if (
        entry.get("modality_required") == "visual_required"
        and entry.get("turn_1_image") is None
        and entry.get("turn_2_image") is None
    ):
        return "depends-on-missing-visual"
    return "answerable-from-release"


def alignment(entry: dict[str, Any], issues: set[str], evidence: str) -> str:
    target = entry["target_context"]
    is_core = target in {"current", "prior"}
    if is_core:
        if evidence.startswith("depends-on-missing") or "weak_product_relevance" in issues:
            return "core-misaligned"
        return "core-aligned"
    if "weak_product_relevance" in issues or evidence.startswith("depends-on-missing"):
        return "auxiliary-misaligned"
    return "auxiliary-aligned"


def scenario_issue_types(entry: dict[str, Any], answer_entry: dict[str, Any]) -> list[str]:
    issues: set[str] = set()
    evidence = evidence_status(entry)
    sid = entry["scenario_id"]
    if evidence == "depends-on-missing-visual":
        issues.update({"hidden_visual_dependency", "missing_release_evidence"})
    if evidence == "depends-on-missing-audio":
        issues.update({"hidden_audio_dependency", "missing_release_evidence"})
    if (
        entry["target_context"] == "prior"
        and entry.get("modality_required") == "text_sufficient"
        and entry.get("difficulty_tier") == "easy"
    ):
        issues.add("text_recall_too_easy")
    if generic_answer_key_issue(answer_entry):
        issues.update({"answer_key_too_generic", "answer_key_misaligned"})
    if sid in OPEN_ENDED_SCENARIOS:
        issues.add("turn_2_too_open_ended")
    if sid in WEAK_PRODUCT_RELEVANCE:
        issues.add("weak_product_relevance")
    if sid in HIDDEN_AUDIO_SCENARIOS:
        issues.add("hidden_audio_dependency")
    if sid in MERGE_WITH:
        issues.add("near_duplicate")
    if sid in {"sc-38", "sc-39", "sc-41"}:
        issues.add("clarify_vs_abstain_blur")
    if sid in {"sc-06", "sc-21", "sc-96"}:
        issues.add("repair_anchor_leak")
    return sorted(issues)


def scenario_action(entry: dict[str, Any], issues: set[str], evidence: str) -> str:
    sid = entry["scenario_id"]
    if sid in REMOVE_SCENARIOS:
        return "remove"
    if sid in MERGE_WITH:
        return "merge"
    if evidence in {"depends-on-missing-visual", "depends-on-missing-audio"}:
        return "rewrite"
    # text_recall_too_easy is a characterization of Turn 1 anchoring, not a
    # structural defect. It is surfaced as an issue_type for reviewers but does
    # not by itself force a rewrite at the bank level.
    if "weak_product_relevance" in issues:
        return "rewrite"
    return "keep"


def answer_key_action(action: str, issues: set[str]) -> str:
    if action == "rewrite":
        return "rewrite"
    if "answer_key_too_generic" in issues or "answer_key_misaligned" in issues:
        return "rewrite"
    return "keep"


def severity(entry: dict[str, Any], action: str, issues: set[str], evidence: str) -> str:
    if action in {"remove"} or evidence.startswith("depends-on-missing"):
        return "high"
    if action in {"rewrite", "merge"} or issues:
        return "medium"
    return "low"


def overlap_with(entry: dict[str, Any]) -> list[str]:
    sid = entry["scenario_id"]
    return [MERGE_WITH[sid]] if sid in MERGE_WITH else []


def what_works(entry: dict[str, Any], action: str) -> str:
    target = entry["target_context"]
    domain = DOMAIN_LABELS.get(entry.get("activity_domain"), entry.get("activity_domain", "domain")).lower()
    if target in {"current", "prior"}:
        return (
            f"This scenario uses a recognizable {target}-context shape in {domain} and "
            f"captures a real reference-carryover failure mode that a wearable assistant can hit."
        )
    return (
        f"This auxiliary scenario draws a clear boundary case in {domain} and helps test "
        f"whether the assistant asks or declines instead of guessing."
    )


def what_doesnt(entry: dict[str, Any], action: str, issues: list[str], evidence: str) -> str:
    bits: list[str] = []
    if evidence == "depends-on-missing-visual":
        bits.append(
            "Canonical v1 ships without the visual payload this case relies on, so the released inputs do not identify the needed referent or state."
        )
    if evidence == "depends-on-missing-audio":
        bits.append(
            "The scenario depends on audio evidence that canonical v1 does not provide through raw speech or speaker cues."
        )
    if "text_recall_too_easy" in issues:
        bits.append(
            "The answer is recoverable as direct Turn 1 text recall, so the context shift adds little real reference-resolution pressure."
        )
    if "answer_key_too_generic" in issues:
        bits.append(
            "The answer key rewards vague pivot language rather than a substantively correct answer to the user’s question."
        )
    if "weak_product_relevance" in issues:
        bits.append(
            "The prompt is more about missing task criteria or generic advice than about inferring what the user is referring to."
        )
    if "near_duplicate" in issues:
        bits.append(
            "It overlaps heavily with another scenario that exercises the same reasoning pattern with little additional coverage."
        )
    if "turn_2_too_open_ended" in issues:
        bits.append(
            "Turn 2 is broad enough that multiple reasonable answers could pass without proving the intended context selection."
        )
    if not bits:
        bits.append("No major benchmark-quality issue stands out beyond normal maintenance risk.")
    return " ".join(bits[:3])


def gap_analysis(entry: dict[str, Any], issues: list[str], evidence: str) -> str:
    if evidence == "depends-on-missing-visual":
        return (
            "As released, this scenario is aligned to the product problem in spirit but not answerable from the benchmark evidence, so it measures pivot behavior more than grounded inference."
        )
    if evidence == "depends-on-missing-audio":
        return (
            "This scenario relies on a modality canonical v1 does not expose, so it cannot be a valid release-level test of the stated benchmark task."
        )
    if "text_recall_too_easy" in issues:
        return (
            "This case fits the benchmark theme, but the released wording makes it closer to a short-term memory quiz than a strong situational reference test."
        )
    if "weak_product_relevance" in issues:
        return (
            "The scenario reads naturally, but it is weakly aligned to the benchmark’s core question of what the user is referring to after context changes."
        )
    if "near_duplicate" in issues:
        return (
            "The scenario is individually valid, but keeping it alongside a stronger near-duplicate inflates bank size without adding proportional coverage."
        )
    return (
        "This scenario stays within the benchmark’s stated scope and is sufficiently distinct to support product-facing model comparison."
    )


def recommended_changes(entry: dict[str, Any], action: str, issues: list[str], evidence: str) -> str:
    sid = entry["scenario_id"]
    if action == "keep":
        return "Keep the scenario and answer keys as-is."
    if action == "merge":
        return f"Merge this scenario into {MERGE_WITH[sid]} and keep the stronger surviving version."
    if action == "remove":
        return "Remove this scenario from the canonical bank because it does not cleanly measure the published benchmark task."
    changes: list[str] = []
    if evidence == "depends-on-missing-visual":
        changes.append("Rewrite the scenario so the needed current or prior evidence is available from transcript-proxy inputs.")
    if evidence == "depends-on-missing-audio":
        changes.append("Rewrite the scenario around visible or textual evidence, or defer it to a future audio-enabled benchmark.")
    if "text_recall_too_easy" in issues:
        changes.append("Increase distractors or reduce verbatim Turn 1 leakage so the prior answer is not simple text lookup.")
    if "answer_key_too_generic" in issues:
        changes.append("Replace generic anchors with concrete answer strings that separate correct answers from vague pivot language.")
    if "weak_product_relevance" in issues:
        changes.append("Refocus Turn 2 on an ambiguous referent in the active scene instead of a generic planning or policy question.")
    if not changes:
        changes.append("Tighten the wording and answer keys to better isolate the intended behavior.")
    return " ".join(changes[:3])


def rewritten_turns(entry: dict[str, Any], action: str) -> dict[str, str] | None:
    if action != "rewrite":
        return None
    sid = entry["scenario_id"]
    if sid in CURRENT_REWRITE_HINTS:
        hint = CURRENT_REWRITE_HINTS[sid]
        return {
            "turn_1_user": entry["turn_1_user"],
            "turn_2_user": hint["turn_2_user"],
            "turn_3_repair_anchor": hint["turn_3_repair_anchor"],
        }
    if sid in PRIOR_VISUAL_REWRITES:
        return {
            "turn_1_user": PRIOR_VISUAL_REWRITES[sid]["turn_1_user"],
            "turn_2_user": PRIOR_VISUAL_REWRITES[sid]["turn_2_user"],
            "turn_3_repair_anchor": PRIOR_VISUAL_REWRITES[sid]["turn_3_repair_anchor"],
        }
    return {
        "turn_1_user": entry["turn_1_user"],
        "turn_2_user": entry["turn_2_user"],
        "turn_3_repair_anchor": entry["turn_3_repair_anchor"],
    }


def rewritten_answer_keys(entry: dict[str, Any], action: str, key_action: str, answer_entry: dict[str, Any]) -> dict[str, Any] | None:
    if key_action != "rewrite":
        return None
    sid = entry["scenario_id"]
    if sid in CURRENT_REWRITE_HINTS:
        return CURRENT_REWRITE_HINTS[sid]["answer_keys"]
    if sid in PRIOR_VISUAL_REWRITES:
        return PRIOR_VISUAL_REWRITES[sid]["answer_keys"]
    # Fallback keeps the original structure but avoids nulls for rewritten rows.
    return {
        "current_answers": answer_entry["current_answers"],
        "prior_answers": answer_entry["prior_answers"],
        "clarify_indicators": answer_entry["clarify_indicators"],
        "abstain_indicators": answer_entry["abstain_indicators"],
    }


def scaffold_row(entry: dict[str, Any]) -> dict[str, Any]:
    return {
        "scenario_id": entry["scenario_id"],
        "title": build_title(entry),
        "description": build_description(entry),
        "category": {
            "target_context": entry["target_context"],
            "cue_type": entry.get("cue_type"),
            "activity_domain": entry.get("activity_domain"),
            "modality_required": entry.get("modality_required"),
        },
        "alignment": "",
        "evidence_status": "",
        "scenario_action": "",
        "answer_key_action": "",
        "severity": "",
        "issue_types": [],
        "what_works": "",
        "what_doesnt": "",
        "gap_analysis": "",
        "overlap_with": [],
        "recommended_changes": "",
        "rewritten_scenario": None,
        "rewritten_answer_keys": None,
    }


def build_audit_rows(
    scenarios: list[dict[str, Any]],
    answers: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for entry in scenarios:
        row = scaffold_row(entry)
        answer_entry = answers[entry["scenario_id"]]
        issues = scenario_issue_types(entry, answer_entry)
        evidence = evidence_status(entry)
        action = scenario_action(entry, set(issues), evidence)
        key_action = answer_key_action(action, set(issues))
        row["alignment"] = alignment(entry, set(issues), evidence)
        row["evidence_status"] = evidence
        row["scenario_action"] = action
        row["answer_key_action"] = key_action
        row["severity"] = severity(entry, action, set(issues), evidence)
        row["issue_types"] = issues
        row["what_works"] = what_works(entry, action)
        row["what_doesnt"] = what_doesnt(entry, action, issues, evidence)
        row["gap_analysis"] = gap_analysis(entry, issues, evidence)
        row["overlap_with"] = overlap_with(entry)
        row["recommended_changes"] = recommended_changes(entry, action, issues, evidence)
        row["rewritten_scenario"] = rewritten_turns(entry, action)
        row["rewritten_answer_keys"] = rewritten_answer_keys(entry, action, key_action, answer_entry)
        rows.append(row)
    return rows


def render_summary(rows: list[dict[str, Any]]) -> str:
    counts_by_action = Counter(row["scenario_action"] for row in rows)
    counts_by_key_action = Counter(row["answer_key_action"] for row in rows)
    counts_by_alignment = Counter(row["alignment"] for row in rows)
    counts_by_evidence = Counter(row["evidence_status"] for row in rows)
    issue_counter: Counter[str] = Counter()
    for row in rows:
        issue_counter.update(row["issue_types"])

    top_issue_rows = [
        row
        for row in rows
        if row["severity"] == "high" or row["scenario_action"] in {"remove", "merge"}
    ][:20]

    lines: list[str] = []
    lines.append("# 2026-04-22 Canonical v1 Scenario Audit")
    lines.append("")
    lines.append(
        f"This report summarizes a full one-by-one audit of the {len(rows)} canonical v1 scenarios."
    )
    lines.append("")
    lines.append("The full per-scenario audit lives in `2026-04-22-scenario-audit.jsonl`.")
    lines.append("The CSV export in `2026-04-22-scenario-audit.csv` is the sortable review view.")
    lines.append("")
    lines.append("## Research basis")
    lines.append("")
    for source in RESEARCH_SOURCES:
        lines.append(f"- [{source['name']}]({source['url']}): {source['reason']}")
    lines.append("")
    lines.append("## Audit rubric")
    lines.append("")
    lines.extend(
        [
            "1. Single intended interpretation",
            "2. Answerable from the release as shipped",
            "3. Correct target label",
            "4. Product alignment",
            "5. Minimal leakage",
            "6. Answer-key specificity",
            "7. Distinctiveness",
        ]
    )
    lines.append("")
    lines.append("## Bank-level findings")
    lines.append("")
    by_target = Counter(row["category"]["target_context"] for row in rows)
    current_visual_missing = sum(
        1
        for row in rows
        if row["category"]["target_context"] == "current"
        and row["category"]["modality_required"] == "visual_required"
        and row["evidence_status"] == "depends-on-missing-visual"
    )
    prior_text_sufficient = sum(
        1
        for row in rows
        if row["category"]["target_context"] == "prior"
        and row["category"]["modality_required"] == "text_sufficient"
    )
    prior_total = by_target.get("prior", 0)
    auxiliary_total = by_target.get("clarify", 0) + by_target.get("abstain", 0)
    lines.append(f"- Scenarios audited: **{len(rows)}**")
    lines.append(
        f"- `current` scenarios with `visual_required` and null image payloads: **{current_visual_missing}**"
    )
    lines.append(
        f"- `prior` scenarios marked `text_sufficient`: **{prior_text_sufficient} of {prior_total}**"
    )
    lines.append(
        f"- Auxiliary `clarify` + `abstain` scenarios: **{auxiliary_total}**"
    )
    lines.append("")
    lines.append("### Counts by scenario action")
    lines.append("")
    for key in sorted(counts_by_action):
        lines.append(f"- `{key}`: **{counts_by_action[key]}**")
    lines.append("")
    lines.append("### Counts by answer-key action")
    lines.append("")
    for key in sorted(counts_by_key_action):
        lines.append(f"- `{key}`: **{counts_by_key_action[key]}**")
    lines.append("")
    lines.append("### Counts by alignment")
    lines.append("")
    for key in sorted(counts_by_alignment):
        lines.append(f"- `{key}`: **{counts_by_alignment[key]}**")
    lines.append("")
    lines.append("### Counts by evidence status")
    lines.append("")
    for key in sorted(counts_by_evidence):
        lines.append(f"- `{key}`: **{counts_by_evidence[key]}**")
    lines.append("")
    lines.append("### Most common issue types")
    lines.append("")
    for key, value in issue_counter.most_common(12):
        lines.append(f"- `{key}`: **{value}**")
    lines.append("")
    lines.append("## Residual issue families")
    lines.append("")
    residual_lines: list[str] = []
    if issue_counter.get("hidden_visual_dependency", 0):
        residual_lines.append(
            "- `current` scenarios that still depend on missing visual evidence; the release inputs do not identify the referent as written."
        )
    if issue_counter.get("text_recall_too_easy", 0):
        residual_lines.append(
            "- `prior` scenarios that are answerable by literal Turn 1 text recall, which measures short-term memory more than contextual reach-back."
        )
    if issue_counter.get("turn_2_too_open_ended", 0):
        residual_lines.append(
            "- `current` scenarios where Turn 2 is broad enough that multiple reasonable answers could pass without proving the intended context selection."
        )
    if issue_counter.get("repair_anchor_leak", 0):
        residual_lines.append(
            "- Turn 3 repair anchors that restate the Turn 2 answer and could leak the target."
        )
    if issue_counter.get("clarify_vs_abstain_blur", 0):
        residual_lines.append(
            "- Auxiliary scenarios where the line between `clarify` and `abstain` is thin and could be scored inconsistently."
        )
    if issue_counter.get("weak_product_relevance", 0):
        residual_lines.append(
            "- Scenarios whose Turn 2 question drifts into generic planning or policy rather than referring to something in the active scene."
        )
    if issue_counter.get("hidden_audio_dependency", 0):
        residual_lines.append(
            "- Scenarios that rely on acoustic cues canonical v1 does not expose; these should be rewritten or deferred to a future audio-enabled release."
        )
    if issue_counter.get("answer_key_too_generic", 0) or issue_counter.get("answer_key_misaligned", 0):
        residual_lines.append(
            "- A small number of answer keys that still reward vague pivot language rather than a substantively correct answer."
        )
    if not residual_lines:
        residual_lines.append("- No residual issue families above threshold in the current bank.")
    lines.extend(residual_lines)
    lines.append("")
    lines.append("## Known follow-ups")
    lines.append("")
    followups: list[str] = []
    if issue_counter.get("text_recall_too_easy", 0):
        followups.append(
            "- Rebalance the `prior` bank away from literal Turn 1 text lookup toward stronger contextual reach-back."
        )
    if issue_counter.get("turn_2_too_open_ended", 0):
        followups.append(
            "- Tighten open-ended Turn 2 phrasing so only the intended referent can score as correct."
        )
    if issue_counter.get("repair_anchor_leak", 0):
        followups.append(
            "- Rewrite Turn 3 repair anchors that restate the target so the anchor points at the referent without revealing the answer."
        )
    if issue_counter.get("clarify_vs_abstain_blur", 0):
        followups.append(
            "- Sharpen the distinguishing cue on `clarify` vs `abstain` boundary scenarios."
        )
    if issue_counter.get("hidden_audio_dependency", 0):
        followups.append(
            "- Rewrite or defer any scenario that depends on audio cues canonical v1 does not provide."
        )
    if issue_counter.get("weak_product_relevance", 0):
        followups.append(
            "- Refocus weakly product-relevant scenarios on an ambiguous referent in the active scene."
        )
    if not followups:
        followups.append("- No bank-level follow-ups open.")
    lines.extend(followups)
    lines.append("")
    lines.append("## High-priority scenario rows")
    lines.append("")
    lines.append("| Scenario | Action | Severity | Issues |")
    lines.append("| --- | --- | --- | --- |")
    for row in top_issue_rows:
        issue_text = ", ".join(row["issue_types"]) if row["issue_types"] else "none"
        lines.append(
            f"| {row['scenario_id']} | `{row['scenario_action']}` | `{row['severity']}` | {issue_text} |"
        )
    lines.append("")
    return "\n".join(lines)


def validate_rows(
    rows: list[dict[str, Any]],
    scenarios: list[dict[str, Any]],
) -> None:
    scenario_map = {scenario["scenario_id"]: scenario for scenario in scenarios}
    if len(rows) != len(scenarios):
        raise ValueError(f"row count mismatch: {len(rows)} rows for {len(scenarios)} scenarios")
    seen: set[str] = set()
    for row in rows:
        sid = row["scenario_id"]
        if sid in seen:
            raise ValueError(f"duplicate row for {sid}")
        seen.add(sid)
        source = scenario_map[sid]
        for field in (
            "title",
            "description",
            "alignment",
            "evidence_status",
            "scenario_action",
            "answer_key_action",
            "severity",
            "what_works",
            "what_doesnt",
            "gap_analysis",
            "recommended_changes",
        ):
            if row[field] in {"", None}:
                raise ValueError(f"{sid} missing required field {field}")
        if row["alignment"] not in ALLOWED_ALIGNMENTS:
            raise ValueError(f"{sid} invalid alignment {row['alignment']}")
        if row["evidence_status"] not in ALLOWED_EVIDENCE_STATUSES:
            raise ValueError(f"{sid} invalid evidence_status {row['evidence_status']}")
        if row["scenario_action"] not in ALLOWED_SCENARIO_ACTIONS:
            raise ValueError(f"{sid} invalid scenario_action {row['scenario_action']}")
        if row["answer_key_action"] not in ALLOWED_ANSWER_KEY_ACTIONS:
            raise ValueError(f"{sid} invalid answer_key_action {row['answer_key_action']}")
        if row["severity"] not in ALLOWED_SEVERITIES:
            raise ValueError(f"{sid} invalid severity {row['severity']}")
        invalid_issues = set(row["issue_types"]) - ALLOWED_ISSUE_TYPES
        if invalid_issues:
            raise ValueError(f"{sid} invalid issue_types {sorted(invalid_issues)}")
        category = row["category"]
        if category["target_context"] != source["target_context"]:
            raise ValueError(f"{sid} category target mismatch")
        if category["cue_type"] != source.get("cue_type"):
            raise ValueError(f"{sid} category cue mismatch")
        if category["activity_domain"] != source.get("activity_domain"):
            raise ValueError(f"{sid} category domain mismatch")
        if category["modality_required"] != source.get("modality_required"):
            raise ValueError(f"{sid} category modality mismatch")
        rewritten_scenario = row["rewritten_scenario"]
        if row["scenario_action"] == "rewrite":
            if not rewritten_scenario:
                raise ValueError(f"{sid} missing rewritten_scenario for rewrite action")
            for field in ("turn_1_user", "turn_2_user", "turn_3_repair_anchor"):
                if not rewritten_scenario.get(field):
                    raise ValueError(f"{sid} rewritten_scenario missing {field}")
        else:
            if rewritten_scenario is not None:
                raise ValueError(f"{sid} should not have rewritten_scenario")
        rewritten_answer_keys = row["rewritten_answer_keys"]
        if row["answer_key_action"] == "rewrite":
            if not rewritten_answer_keys:
                raise ValueError(f"{sid} missing rewritten_answer_keys")
        else:
            if rewritten_answer_keys is not None:
                raise ValueError(f"{sid} should not have rewritten_answer_keys")
        if row["scenario_action"] == "merge":
            if not row["overlap_with"]:
                raise ValueError(f"{sid} merge action missing overlap_with")
            for overlap in row["overlap_with"]:
                if scenario_map[overlap]["target_context"] != source["target_context"]:
                    raise ValueError(f"{sid} merge target {overlap} crosses target_context")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    bootstrap = subparsers.add_parser("bootstrap")
    bootstrap.add_argument("--jsonl-out", type=Path, required=True)

    build = subparsers.add_parser("build")
    build.add_argument("--jsonl-out", type=Path, required=True)
    build.add_argument("--csv-out", type=Path, required=True)
    build.add_argument("--markdown-out", type=Path, required=True)

    export = subparsers.add_parser("export-csv")
    export.add_argument("--jsonl-in", type=Path, required=True)
    export.add_argument("--csv-out", type=Path, required=True)

    summary = subparsers.add_parser("render-summary")
    summary.add_argument("--jsonl-in", type=Path, required=True)
    summary.add_argument("--markdown-out", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    scenarios = load_json(SCENARIOS_PATH)
    answers = load_json(EXPECTED_ANSWERS_PATH)

    if args.command == "bootstrap":
        rows = [scaffold_row(entry) for entry in scenarios]
        write_jsonl(rows, args.jsonl_out)
        return

    if args.command == "build":
        rows = build_audit_rows(scenarios, answers)
        validate_rows(rows, scenarios)
        write_jsonl(rows, args.jsonl_out)
        export_csv(rows, args.csv_out)
        args.markdown_out.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_out.write_text(render_summary(rows), encoding="utf-8")
        return

    if args.command == "export-csv":
        rows = load_jsonl(args.jsonl_in)
        export_csv(rows, args.csv_out)
        return

    if args.command == "render-summary":
        rows = load_jsonl(args.jsonl_in)
        args.markdown_out.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_out.write_text(render_summary(rows), encoding="utf-8")
        return


if __name__ == "__main__":
    main()
