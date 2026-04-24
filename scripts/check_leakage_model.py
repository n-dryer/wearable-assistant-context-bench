"""
Task 5: Automated leakage check via model inference.

For each scenario, mask turn_1_user and image fields, run turn_2_user alone
through claude-sonnet-4-6 at temperature 0, seed 42, three times (majority vote).
Score using substring containment. Flag any scenario above chance + 10pp.

Chance baselines:
  current / prior: 33%
  clarify / abstain: 50%

Requires ANTHROPIC_API_KEY in environment.

Usage: python scripts/check_leakage_model.py [--output results/leakage_model.json]
"""

import json
import os
from pathlib import Path
from collections import Counter

import anthropic

SCENARIOS_PATH = Path("benchmark/v1/scenarios.json")
ANSWERS_PATH = Path("benchmark/v1/expected_answers.json")
MODEL = "claude-sonnet-4-6"
TEMPERATURE = 0.0
SEED = 42
RUNS = 3
CHANCE_THRESHOLDS = {
    "current": 0.33 + 0.10,
    "prior": 0.33 + 0.10,
    "clarify": 0.50 + 0.10,
    "abstain": 0.50 + 0.10,
}

SYSTEM_PROMPT = (
    "You are a wearable assistant. The user will ask a question. "
    "Answer concisely in one or two sentences."
)


def score_response(response: str, answers: dict, category: str) -> bool:
    text = response.lower()
    if category == "current":
        return any(a.lower() in text for a in answers.get("current_answers", []))
    elif category == "prior":
        return any(a.lower() in text for a in answers.get("prior_answers", []))
    elif category == "clarify":
        has_clarify = any(i.lower() in text for i in answers.get("clarify_indicators", []))
        no_confident_wrong = not any(a.lower() in text for a in answers.get("current_answers", []) + answers.get("prior_answers", []))
        return has_clarify and no_confident_wrong
    elif category == "abstain":
        has_abstain = any(i.lower() in text for i in answers.get("abstain_indicators", []))
        no_confident_wrong = not any(a.lower() in text for a in answers.get("current_answers", []) + answers.get("prior_answers", []))
        return has_abstain and no_confident_wrong
    return False


def run():
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    scenarios = json.loads(SCENARIOS_PATH.read_text())
    answers = json.loads(ANSWERS_PATH.read_text())

    flagged = []

    for sc in scenarios:
        sid = sc["scenario_id"]
        cat = sc["target_context"]
        t2 = sc.get("turn_2_user", "") or ""
        ans = answers.get(sid, {})

        scores = []
        for _ in range(RUNS):
            r = client.messages.create(
                model=MODEL,
                max_tokens=200,
                temperature=TEMPERATURE,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": t2}],
            )
            response_text = r.content[0].text
            scores.append(score_response(response_text, ans, cat))

        # majority vote
        majority_correct = Counter(scores).most_common(1)[0][0]
        score_rate = sum(scores) / len(scores)
        threshold = CHANCE_THRESHOLDS.get(cat, 0.43)

        if score_rate > threshold:
            flagged.append({
                "scenario_id": sid,
                "target_context": cat,
                "score_rate": score_rate,
                "threshold": threshold,
                "majority_correct": majority_correct,
                "turn_2_user": t2,
            })
            print(f"  FLAGGED {sid} [{cat}]: {score_rate:.0%} > {threshold:.0%}")
        else:
            print(f"  ok {sid} [{cat}]: {score_rate:.0%}")

    return flagged


def main():
    import sys
    output_path = Path("results/leakage_model.json")
    for i, arg in enumerate(sys.argv[1:]):
        if arg == "--output" and i + 2 < len(sys.argv):
            output_path = Path(sys.argv[i + 2])

    output_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"Running model leakage check ({MODEL}, T={TEMPERATURE}, seed={SEED}, {RUNS} runs/scenario)...")
    flagged = run()
    output_path.write_text(json.dumps(flagged, indent=2))
    print(f"\nFlagged: {len(flagged)} scenario(s)")
    print(f"Results: {output_path}")


if __name__ == "__main__":
    main()
