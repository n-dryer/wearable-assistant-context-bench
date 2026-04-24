"""
Scan scenarios for leakage: answer tokens appearing word-boundary-matched in turn_2_user.

Checks current_answers and prior_answers against turn_2_user.
Usage: python scripts/scan_leakage.py [--json]
"""

import json
import re
import sys
from pathlib import Path

SCENARIOS_PATH = Path("benchmark/v1/scenarios.json")
ANSWERS_PATH = Path("benchmark/v1/expected_answers.json")


def word_match(token: str, text: str) -> bool:
    pattern = r"\b" + re.escape(token.lower()) + r"\b"
    return bool(re.search(pattern, text.lower()))


def scan():
    scenarios = json.loads(SCENARIOS_PATH.read_text())
    answers = json.loads(ANSWERS_PATH.read_text())

    flagged = []

    for sc in scenarios:
        sid = sc["scenario_id"]
        t2 = sc.get("turn_2_user", "") or ""
        ans = answers.get(sid, {})

        leaked = []
        for token in ans.get("current_answers", []):
            if word_match(token, t2):
                leaked.append({"token": token, "source": "current_answers"})
        for token in ans.get("prior_answers", []):
            if word_match(token, t2):
                leaked.append({"token": token, "source": "prior_answers"})

        if leaked:
            flagged.append({
                "scenario_id": sid,
                "target_context": sc.get("target_context"),
                "turn_2_user": t2,
                "leaked_tokens": leaked,
            })

    return flagged


def main():
    as_json = "--json" in sys.argv
    flagged = scan()

    if as_json:
        print(json.dumps(flagged, indent=2))
        return

    if not flagged:
        print("No leakage detected.")
        return

    print(f"Flagged: {len(flagged)} scenario(s)\n")
    for f in flagged:
        tokens = ", ".join(
            f"{t['token']} ({t['source']})" for t in f["leaked_tokens"]
        )
        print(f"  {f['scenario_id']} [{f['target_context']}]  leaked: {tokens}")
        print(f"    T2: {f['turn_2_user'][:120]}")
        print()


if __name__ == "__main__":
    main()
