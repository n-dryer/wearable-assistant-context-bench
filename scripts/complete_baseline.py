"""
Run only the scenarios missing from a partial baseline transcript.

Usage:
    python scripts/complete_baseline.py \
        --partial benchmark/v1/runs/v1.0.0-gemini-v3/transcripts.jsonl \
        --output  benchmark/v1/runs/v1.0.0-gemini-complete/transcripts.jsonl

Reads the partial transcript to find which (scenario_id, condition) pairs
are already done, then runs only the missing ones, appends to the output,
and generates a findings.md via the report module.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

# Allow running from repo root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from benchmark.v1.run import (
    SCENARIOS_PATH,
    EXPECTED_ANSWERS_PATH,
    INTERVENTIONS_PATH,
    CONFIG,
    Scenario,
    AnswerSet,
    _run_one_trial,
    _build_manifest,
    _public_code_signals,
    load_scenarios,
    load_expected_answers,
    _build_adapter,
)
from core.interventions import load_prompt_conditions
from core.llm_judge import build_judge, resolve_judge_family
from core.models import ModelConfig
from core.report import DEFAULT_RANKING_CONDITION, render_findings_markdown


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--partial", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--model", default="gemini-2.5-flash-lite")
    parser.add_argument("--judge-model", default="gemini-2.5-flash-lite")
    parser.add_argument("--judge-family", default="gemini")
    args = parser.parse_args()

    # Load .env
    env_path = Path(".env")
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            k = k.strip()
            v = v.strip().strip('"').strip("'")
            if k and not os.environ.get(k):
                os.environ[k] = v

    partial_path = Path(args.partial)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Read partial transcripts — collect already-done (scenario_id, condition) pairs
    done: set[tuple[str, str]] = set()
    partial_results: list[dict] = []
    if partial_path.exists():
        for line in partial_path.read_text().splitlines():
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            done.add((d["scenario_id"], d["condition"]))
            partial_results.append(d)

    print(f"Partial: {len(partial_results)} entries already done ({len(done)} (sc,cond) pairs)")

    scenarios = load_scenarios(SCENARIOS_PATH)
    answers_by_id = load_expected_answers(EXPECTED_ANSWERS_PATH)
    conditions = load_prompt_conditions(INTERVENTIONS_PATH)

    effective_config = {**CONFIG, "model_id": args.model, "judge_model_id": args.judge_model,
                       "judge_family": args.judge_family, "trials_per_cell": 1}

    model_config = ModelConfig(model_id=args.model, temperature=0.0)
    adapter = _build_adapter(args.model)

    family, resolution_mode = resolve_judge_family(args.judge_family, args.model)
    judge = build_judge(family=family, model_id=args.judge_model)

    missing = [
        (sc, cond)
        for sc in scenarios
        for cond in conditions
        if (sc.scenario_id, cond.name) not in done
    ]
    print(f"Missing: {len(missing)} (scenario, condition) pairs to run")

    new_results: list[dict] = []
    with output_path.open("w", encoding="utf-8") as f:
        # First write all existing partial entries
        for r in partial_results:
            f.write(json.dumps({**r, "turn_2_code_signals": r.get("turn_2_code_signals", {})},
                               ensure_ascii=False) + "\n")

        # Then run missing ones
        for i, (scenario, condition) in enumerate(missing):
            print(f"  [{i+1}/{len(missing)}] {scenario.scenario_id} / {condition.name}")
            answers = answers_by_id[scenario.scenario_id]
            result = _run_one_trial(
                scenario=scenario,
                answers=answers,
                condition=condition,
                trial=0,
                adapter=adapter,
                judge=judge,
                model_config=model_config,
            )
            new_results.append(result)
            f.write(json.dumps(
                {**result, "turn_2_code_signals": _public_code_signals(result["turn_2_code_signals"])},
                ensure_ascii=False,
            ) + "\n")
            f.flush()

    all_results = partial_results + new_results
    manifest = _build_manifest(
        effective_config=effective_config,
        resolved_judge=judge,
        judge_resolution_mode=resolution_mode,
    )
    findings = render_findings_markdown(
        all_results,
        scenario_policies={s.scenario_id: s.target_context for s in scenarios},
        manifest=manifest,
        ranking_condition=DEFAULT_RANKING_CONDITION,
    )
    findings_path = output_path.parent / "findings.md"
    findings_path.write_text(findings, encoding="utf-8")
    print(f"\nDone. findings.md -> {findings_path}")
    print(findings[:800])


if __name__ == "__main__":
    main()
