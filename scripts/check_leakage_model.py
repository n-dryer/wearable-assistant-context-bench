"""
Task 5: Automated leakage check via model inference.

For each scenario, mask turn_1_user and image fields, run turn_2_user alone
through the model at temperature 0, three times (majority vote).
Score using substring containment. Flag any scenario above chance + 10pp.

Chance baselines:
  current / prior: 33%
  clarify / abstain: 50%

Uses Gemini (GEMINI_API_KEY from environment or .env).
Falls back to Anthropic if ANTHROPIC_API_KEY is set.

Usage: python scripts/check_leakage_model.py [--output results/leakage_model.json]
"""

import json
import os
from pathlib import Path
from collections import Counter


SCENARIOS_PATH = Path("benchmark/v1/scenarios.json")
ANSWERS_PATH = Path("benchmark/v1/expected_answers.json")
GEMINI_MODEL = "gemini-2.5-flash"
TEMPERATURE = 0.0
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


def _load_env() -> None:
    """Load .env from repo root if keys not already in environment."""
    env_path = Path(".env")
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        if key and not os.environ.get(key):
            os.environ[key] = val


def _build_client():
    """Return (client, backend) where backend is 'gemini' or 'anthropic'."""
    _load_env()

    gemini_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")

    if gemini_key:
        from google import genai
        return genai.Client(api_key=gemini_key), "gemini"
    elif anthropic_key:
        import anthropic
        return anthropic.Anthropic(api_key=anthropic_key), "anthropic"
    else:
        raise RuntimeError(
            "No API key found. Set GEMINI_API_KEY or ANTHROPIC_API_KEY."
        )


def _query_gemini(client, turn_2_user: str) -> str:
    from google.genai import types as gtypes
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=[
            gtypes.Content(
                role="user",
                parts=[gtypes.Part.from_text(text=turn_2_user)],
            )
        ],
        config=gtypes.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=TEMPERATURE,
            max_output_tokens=200,
            thinking_config=gtypes.ThinkingConfig(thinking_budget=0),
        ),
    )
    return getattr(response, "text", "") or ""


def _query_anthropic(client, turn_2_user: str) -> str:
    r = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=200,
        temperature=TEMPERATURE,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": turn_2_user}],
    )
    return r.content[0].text


def score_response(response: str, answers: dict, category: str) -> bool:
    text = response.lower()
    if category == "current":
        return any(a.lower() in text for a in answers.get("current_answers", []))
    elif category == "prior":
        return any(a.lower() in text for a in answers.get("prior_answers", []))
    elif category == "clarify":
        has_clarify = any(i.lower() in text for i in answers.get("clarify_indicators", []))
        no_wrong = not any(
            a.lower() in text
            for a in answers.get("current_answers", []) + answers.get("prior_answers", [])
        )
        return has_clarify and no_wrong
    elif category == "abstain":
        has_abstain = any(i.lower() in text for i in answers.get("abstain_indicators", []))
        no_wrong = not any(
            a.lower() in text
            for a in answers.get("current_answers", []) + answers.get("prior_answers", [])
        )
        return has_abstain and no_wrong
    return False


def run():
    client, backend = _build_client()
    print(f"Backend: {backend} / model: {GEMINI_MODEL if backend == 'gemini' else 'claude-sonnet-4-6'}")

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
            if backend == "gemini":
                resp = _query_gemini(client, t2)
            else:
                resp = _query_anthropic(client, t2)
            scores.append(score_response(resp, ans, cat))

        score_rate = sum(scores) / len(scores)
        threshold = CHANCE_THRESHOLDS.get(cat, 0.43)

        status = "FLAG" if score_rate > threshold else "ok"
        print(f"  {status} {sid} [{cat}]: {score_rate:.0%} (threshold {threshold:.0%})")

        if score_rate > threshold:
            flagged.append({
                "scenario_id": sid,
                "target_context": cat,
                "score_rate": score_rate,
                "threshold": threshold,
                "scores": scores,
                "turn_2_user": t2,
            })

    return flagged


def main():
    import sys
    output_path = Path("results/leakage_model_gemini.json")
    for i, arg in enumerate(sys.argv[1:]):
        if arg == "--output" and i + 2 < len(sys.argv):
            output_path = Path(sys.argv[i + 2])

    output_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"Running model leakage check ({RUNS} runs/scenario, T={TEMPERATURE})...")
    flagged = run()
    output_path.write_text(json.dumps(flagged, indent=2))
    print(f"\nFlagged: {len(flagged)} of 101 scenarios")
    print(f"Results: {output_path}")


if __name__ == "__main__":
    main()
