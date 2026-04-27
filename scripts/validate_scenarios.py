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
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

SCENARIOS_PATH = Path("benchmark/v1/scenarios.json")
ANSWERS_PATH = Path("benchmark/v1/expected_answers.json")
INTERVENTIONS_PATH = Path("benchmark/v1/interventions.json")
LOCKFILE_PATH = Path("benchmark/v1/MANIFEST.lock.json")
ADVERSARIAL_SCENARIOS_PATH = Path("benchmark/v1/scenarios_adversarial.json")
ADVERSARIAL_ANSWERS_PATH = Path("benchmark/v1/expected_answers_adversarial.json")
HARD_SCENARIOS_PATH = Path("benchmark/v1/scenarios_v2_candidates.json")
HARD_ANSWERS_PATH = Path("benchmark/v1/expected_answers_v2_candidates.json")

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
    any user speech field (including the optional deictic repair anchor).

    The named repair anchor (``turn_3_repair_anchor``) is exempt because
    it deliberately names the intended and wrong objects to measure
    floor recoverability.
    """
    fails = []
    for sc in scenarios:
        sid = sc["scenario_id"]
        ea = answers.get(sid, {})
        speech_fields = [
            ("turn_1_user", sc.get("turn_1_user", "") or ""),
            ("turn_2_user", sc.get("turn_2_user", "") or ""),
        ]
        deictic = sc.get("turn_3_repair_anchor_deictic")
        if deictic:
            speech_fields.append(("turn_3_repair_anchor_deictic", deictic))
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


def check_3_schema_validation(scenarios, answers, enforce_distribution: bool = True):
    """Check 3: Required fields present, types correct, IDs unique,
    distributions match.

    ``enforce_distribution`` toggles the bank-level cue_type distribution
    check. The canonical 50-scenario bank pins exact counts; the
    adversarial pack uses its own distribution and skips this check.
    """
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

    # Distribution checks (canonical bank only).
    if enforce_distribution:
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


def check_7_lockfile_drift():
    """Check 7: Computed asset hashes match the static MANIFEST.lock.json.

    Catches silent mutations to the scenario bank, expected answers,
    prompt conditions, or judge-prompt template that ship without a
    coordinated benchmark_version (or judge_prompt_version) bump. To
    refresh the lockfile after a deliberate content change, run
    ``python scripts/regen_manifest_lock.py``.
    """
    fails = []
    if not LOCKFILE_PATH.exists():
        return [{
            "scenario_id": "<bank>",
            "check": "lockfile",
            "detail": (
                f"missing lockfile at {LOCKFILE_PATH}; run "
                "scripts/regen_manifest_lock.py to create it"
            ),
        }]
    try:
        lockfile = json.loads(LOCKFILE_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [{
            "scenario_id": "<bank>",
            "check": "lockfile",
            "detail": f"lockfile is not valid JSON: {exc}",
        }]

    # Imports here so the validator runs even when the package import
    # path is not set up (e.g., in a slimmed CI environment that only
    # checks scenarios). The hash checks above for assets remain the
    # primary signal even if these imports fail.
    try:
        repo_root = Path(__file__).resolve().parent.parent
        sys.path.insert(0, str(repo_root))
        from core.llm_judge import JUDGE_PROMPT_VERSION, JUDGE_SYSTEM_PROMPT
        from core.report import BENCHMARK_VERSION, SCHEMA_REVISION
    except ImportError as exc:
        return [{
            "scenario_id": "<bank>",
            "check": "lockfile",
            "detail": f"could not import benchmark package for lockfile check: {exc}",
        }]

    def _sha(path):
        return hashlib.sha256(path.read_bytes()).hexdigest()

    expected = {
        "benchmark_version": BENCHMARK_VERSION,
        "schema_revision": SCHEMA_REVISION,
        "judge_prompt_version": JUDGE_PROMPT_VERSION,
        "judge_prompt_sha256": hashlib.sha256(
            JUDGE_SYSTEM_PROMPT.encode("utf-8")
        ).hexdigest(),
        "scenarios_sha256": _sha(SCENARIOS_PATH),
        "expected_answers_sha256": _sha(ANSWERS_PATH),
        "interventions_sha256": _sha(INTERVENTIONS_PATH),
    }
    if ADVERSARIAL_SCENARIOS_PATH.exists():
        expected["adversarial_scenarios_sha256"] = _sha(ADVERSARIAL_SCENARIOS_PATH)
    if ADVERSARIAL_ANSWERS_PATH.exists():
        expected["adversarial_expected_answers_sha256"] = _sha(
            ADVERSARIAL_ANSWERS_PATH
        )
    if HARD_SCENARIOS_PATH.exists():
        expected["hard_scenarios_sha256"] = _sha(HARD_SCENARIOS_PATH)
    if HARD_ANSWERS_PATH.exists():
        expected["hard_expected_answers_sha256"] = _sha(HARD_ANSWERS_PATH)
    for key, value in expected.items():
        if lockfile.get(key) != value:
            fails.append({
                "scenario_id": "<bank>",
                "check": "lockfile",
                "detail": (
                    f"{key} mismatch: lockfile={lockfile.get(key)!r}, "
                    f"computed={value!r}. If this drift is intentional, "
                    "bump benchmark_version (or judge_prompt_version) "
                    "and regenerate via scripts/regen_manifest_lock.py."
                ),
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
    all_fails.extend(check_7_lockfile_drift())

    # Adversarial pack: same checks except the canonical-bank cue-type
    # distribution. Run only if the pack files exist (they are part of
    # the v1 release; missing means a slimmed checkout).
    if ADVERSARIAL_SCENARIOS_PATH.exists() and ADVERSARIAL_ANSWERS_PATH.exists():
        adv_scenarios = json.loads(ADVERSARIAL_SCENARIOS_PATH.read_text())
        adv_answers = json.loads(ADVERSARIAL_ANSWERS_PATH.read_text())
        all_fails.extend(check_1_token_leakage(adv_scenarios, adv_answers))
        all_fails.extend(check_2_object_name_in_images(adv_scenarios))
        all_fails.extend(
            check_3_schema_validation(
                adv_scenarios, adv_answers, enforce_distribution=False
            )
        )
        all_fails.extend(check_6_duplication(adv_scenarios))

    # Hard pack: same checks except canonical-bank distribution. Same
    # rationale as the adversarial pack — separately tagged scenarios
    # validated under their own distribution rules.
    if HARD_SCENARIOS_PATH.exists() and HARD_ANSWERS_PATH.exists():
        hard_scenarios = json.loads(HARD_SCENARIOS_PATH.read_text())
        hard_answers = json.loads(HARD_ANSWERS_PATH.read_text())
        all_fails.extend(check_1_token_leakage(hard_scenarios, hard_answers))
        all_fails.extend(check_2_object_name_in_images(hard_scenarios))
        all_fails.extend(
            check_3_schema_validation(
                hard_scenarios, hard_answers, enforce_distribution=False
            )
        )
        all_fails.extend(check_6_duplication(hard_scenarios))

    if args.json:
        print(json.dumps(all_fails, indent=2, ensure_ascii=False))
    else:
        if not all_fails:
            adv_count = (
                len(json.loads(ADVERSARIAL_SCENARIOS_PATH.read_text()))
                if ADVERSARIAL_SCENARIOS_PATH.exists()
                else 0
            )
            hard_count = (
                len(json.loads(HARD_SCENARIOS_PATH.read_text()))
                if HARD_SCENARIOS_PATH.exists()
                else 0
            )
            adv_note = f" + {adv_count} adversarial" if adv_count else ""
            hard_note = f" + {hard_count} hard" if hard_count else ""
            print(
                f"All checks passed ({len(scenarios)} canonical"
                f"{adv_note}{hard_note} scenarios validated)."
            )
        else:
            print(f"{len(all_fails)} validation failure(s):")
            for f in all_fails:
                print(f"  [{f['check']}] {f['scenario_id']}: {f['detail']}")

    return 0 if not all_fails else 1


if __name__ == "__main__":
    sys.exit(main())
