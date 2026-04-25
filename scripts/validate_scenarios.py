"""
Validate the scenario bank against the authoring rules.

Runs four programmatic checks (Checks 1, 2, 3, 6 from the rebuild plan).
The semantic checks (Check 4: human identification, Check 5: semantic leakage)
are LLM-driven and run separately during scenario authoring.

Usage:
    python scripts/validate_scenarios.py [--json]

Exits 0 if all checks pass, 1 otherwise.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

SCENARIOS_PATH = Path("benchmark/v1/scenarios.json")
ANSWERS_PATH = Path("benchmark/v1/expected_answers.json")

# Common-object blocklist for image descriptions. Image descriptions must
# NOT name the object directly. This list is non-exhaustive but catches
# obvious cases.
OBJECT_NAME_BLOCKLIST = {
    # Workshop tools
    "hammer", "claw hammer", "screwdriver", "phillips", "drill", "wrench",
    "ratchet", "pliers", "saw", "handsaw", "jigsaw", "circular saw",
    "chisel", "plane", "sander", "router", "level", "mallet", "soldering",
    "soldering iron", "tape measure", "stud finder", "clamp", "vise",
    # Kitchen
    "pan", "saucepan", "skillet", "frying pan", "pot", "wok", "ladle",
    "spatula", "whisk", "tongs", "knife", "chef's knife", "paring knife",
    "cutting board", "blender", "mixer", "kettle", "toaster",
    # Cleaning / household
    "broom", "mop", "vacuum", "dustpan", "sponge", "scrub brush",
    # Art / craft
    "paintbrush", "pencil", "marker", "pen", "ruler", "scissors", "needle",
    "knitting needle", "crochet hook", "loom", "easel", "palette",
    # Garden
    "trowel", "shovel", "spade", "rake", "hoe", "shears", "pruners",
    "secateurs", "pruning shears", "watering can", "hose", "sprayer",
    # Automotive
    "tire", "wheel", "jack", "lug wrench", "dipstick", "battery",
    "oil filter", "spark plug", "air filter",
    # Sports / fitness
    "barbell", "dumbbell", "kettlebell", "yoga mat", "jump rope",
    "tennis racket", "racquet", "bat", "club", "ski", "skis",
    # Electronics / digital (some only)
    "laptop", "phone", "smartphone", "tablet", "monitor",
    "keyboard", "mouse",
}


def word_match(token: str, text: str) -> bool:
    pattern = r"\b" + re.escape(token.lower()) + r"\b"
    return bool(re.search(pattern, text.lower()))


def check_1_token_leakage(scenarios, answers):
    """Check 1: No `current_answers` or `prior_answers` token appears in
    any user speech field."""
    fails = []
    for sc in scenarios:
        sid = sc["scenario_id"]
        ea = answers.get(sid, {})
        speech_fields = [
            ("turn_1_user", sc.get("turn_1_user", "") or ""),
            ("turn_2_user", sc.get("turn_2_user", "") or ""),
        ]
        for field_name, text in speech_fields:
            for token in ea.get("current_answers", []):
                if word_match(token, text):
                    fails.append({
                        "scenario_id": sid,
                        "check": "token_leakage",
                        "detail": f"current_answers token {token!r} appears in {field_name}",
                    })
            for token in ea.get("prior_answers", []):
                if word_match(token, text):
                    fails.append({
                        "scenario_id": sid,
                        "check": "token_leakage",
                        "detail": f"prior_answers token {token!r} appears in {field_name}",
                    })
    return fails


def check_2_object_name_in_images(scenarios):
    """Check 2: No common object name appears in any image description."""
    fails = []
    for sc in scenarios:
        sid = sc["scenario_id"]
        image_fields = [
            ("context_image", sc.get("context_image") or ""),
            ("turn_1_image", sc.get("turn_1_image") or ""),
            ("turn_2_image", sc.get("turn_2_image") or ""),
        ]
        for field_name, text in image_fields:
            if not text:
                continue
            for name in OBJECT_NAME_BLOCKLIST:
                if word_match(name, text):
                    fails.append({
                        "scenario_id": sid,
                        "check": "object_name_in_image",
                        "detail": f"object name {name!r} appears in {field_name}",
                    })
    return fails


def check_3_schema_validation(scenarios, answers):
    """Check 3: Required fields present, types correct, IDs unique,
    distributions match."""
    fails = []
    required_scenario_fields = {
        "scenario_id", "target_context", "cue_type", "activity_domain",
        "cognitive_load", "difficulty_tier",
        "context_image", "turn_1_image", "turn_1_user",
        "turn_2_image", "turn_2_user", "turn_3_repair_anchor",
    }
    valid_target_context = {"current", "prior", "clarify", "abstain"}
    valid_cue_type = {
        "object_in_hand", "object_state", "sequential_task", "location",
        "object_in_view", "absent_referent", "screen_content",
        "pre_conversation_recall",
    }
    valid_difficulty = {"easy", "medium", "hard"}

    seen_ids = set()
    for sc in scenarios:
        sid = sc.get("scenario_id", "<no-id>")
        # Required fields
        missing = required_scenario_fields - set(sc.keys())
        if missing:
            fails.append({
                "scenario_id": sid,
                "check": "schema",
                "detail": f"missing fields: {sorted(missing)}",
            })
        # Unique IDs
        if sid in seen_ids:
            fails.append({
                "scenario_id": sid,
                "check": "schema",
                "detail": "duplicate scenario_id",
            })
        seen_ids.add(sid)
        # Enum validation
        if sc.get("target_context") not in valid_target_context:
            fails.append({
                "scenario_id": sid,
                "check": "schema",
                "detail": f"invalid target_context: {sc.get('target_context')!r}",
            })
        if sc.get("cue_type") not in valid_cue_type:
            fails.append({
                "scenario_id": sid,
                "check": "schema",
                "detail": f"invalid cue_type: {sc.get('cue_type')!r}",
            })
        if sc.get("difficulty_tier") not in valid_difficulty:
            fails.append({
                "scenario_id": sid,
                "check": "schema",
                "detail": f"invalid difficulty_tier: {sc.get('difficulty_tier')!r}",
            })
        # pre_conversation_recall must have non-null context_image
        if sc.get("cue_type") == "pre_conversation_recall" and not sc.get("context_image"):
            fails.append({
                "scenario_id": sid,
                "check": "schema",
                "detail": "pre_conversation_recall scenarios must have context_image populated",
            })
        # turn_1_image and turn_2_image must be populated
        if not sc.get("turn_1_image"):
            fails.append({
                "scenario_id": sid,
                "check": "schema",
                "detail": "turn_1_image must be non-null",
            })
        if not sc.get("turn_2_image"):
            fails.append({
                "scenario_id": sid,
                "check": "schema",
                "detail": "turn_2_image must be non-null",
            })
        # Answers entry must exist
        ea = answers.get(sid)
        if ea is None:
            fails.append({
                "scenario_id": sid,
                "check": "schema",
                "detail": "no entry in expected_answers.json",
            })
            continue
        # Three-category answer rule for current and prior
        target = sc.get("target_context")
        if target == "current":
            if not ea.get("current_answers"):
                fails.append({
                    "scenario_id": sid,
                    "check": "schema",
                    "detail": "current target_context but current_answers is empty",
                })
            if len(ea.get("current_answers", [])) < 3:
                fails.append({
                    "scenario_id": sid,
                    "check": "schema",
                    "detail": "current_answers must include 3+ items (object name, technique, state) — fewer than 3 found",
                })
        if target == "prior":
            if not ea.get("prior_answers"):
                fails.append({
                    "scenario_id": sid,
                    "check": "schema",
                    "detail": "prior target_context but prior_answers is empty",
                })
            if len(ea.get("prior_answers", [])) < 3:
                fails.append({
                    "scenario_id": sid,
                    "check": "schema",
                    "detail": "prior_answers must include 3+ items (object name, technique, state) — fewer than 3 found",
                })
        if target == "abstain" and not ea.get("abstain_indicators"):
            fails.append({
                "scenario_id": sid,
                "check": "schema",
                "detail": "abstain target_context but abstain_indicators is empty",
            })
        if target == "clarify" and not ea.get("clarify_indicators"):
            fails.append({
                "scenario_id": sid,
                "check": "schema",
                "detail": "clarify target_context but clarify_indicators is empty",
            })

    # Distribution checks
    cue_counts = Counter(sc.get("cue_type") for sc in scenarios)
    expected_cue_counts = {
        "object_in_hand": 12, "object_state": 8, "sequential_task": 6,
        "location": 6, "object_in_view": 5, "absent_referent": 5,
        "screen_content": 4, "pre_conversation_recall": 4,
    }
    for cue, expected_count in expected_cue_counts.items():
        if cue_counts[cue] != expected_count:
            fails.append({
                "scenario_id": "<bank>",
                "check": "schema",
                "detail": f"cue_type {cue} count {cue_counts[cue]} does not match expected {expected_count}",
            })

    return fails


def check_6_duplication(scenarios):
    """Check 6: Cross-scenario near-duplication on T2 user + T2 image +
    (cue_type, target_context, difficulty_tier) signature."""
    fails = []
    seen_t2_user = {}
    seen_t2_image = {}
    seen_signatures = Counter()

    for sc in scenarios:
        sid = sc["scenario_id"]
        t2u = (sc.get("turn_2_user") or "").strip().lower()
        t2i = (sc.get("turn_2_image") or "").strip().lower()
        sig = (sc.get("cue_type"), sc.get("target_context"), sc.get("difficulty_tier"), sc.get("activity_domain"))

        if t2u and t2u in seen_t2_user:
            fails.append({
                "scenario_id": sid,
                "check": "duplication",
                "detail": f"identical turn_2_user as {seen_t2_user[t2u]}",
            })
        else:
            seen_t2_user[t2u] = sid

        if t2i and t2i in seen_t2_image:
            fails.append({
                "scenario_id": sid,
                "check": "duplication",
                "detail": f"identical turn_2_image as {seen_t2_image[t2i]}",
            })
        else:
            seen_t2_image[t2i] = sid

        seen_signatures[sig] += 1

    # Flag signatures with >2 instances (some duplication is fine; many
    # is a coverage problem)
    for sig, count in seen_signatures.items():
        if count > 2:
            fails.append({
                "scenario_id": "<bank>",
                "check": "duplication",
                "detail": f"signature {sig} appears {count} times (limit 2)",
            })

    return fails


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    scenarios = json.loads(SCENARIOS_PATH.read_text())
    answers = json.loads(ANSWERS_PATH.read_text())

    all_fails = []
    all_fails.extend(check_1_token_leakage(scenarios, answers))
    all_fails.extend(check_2_object_name_in_images(scenarios))
    all_fails.extend(check_3_schema_validation(scenarios, answers))
    all_fails.extend(check_6_duplication(scenarios))

    if args.json:
        print(json.dumps(all_fails, indent=2, ensure_ascii=False))
    else:
        if not all_fails:
            print(f"All checks passed ({len(scenarios)} scenarios validated).")
        else:
            print(f"{len(all_fails)} validation failure(s):")
            for f in all_fails:
                print(f"  [{f['check']}] {f['scenario_id']}: {f['detail']}")

    return 0 if not all_fails else 1


if __name__ == "__main__":
    sys.exit(main())
