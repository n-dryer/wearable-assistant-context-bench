"""v1 benchmark runner for visual-context selection.

The runner walks the four frozen v1 scenarios through three
intervention conditions, with a configurable trial count per cell,
as a 2-turn conversation. On Turn 2 failure it fires a templated
Turn 3 "I mean, ..." repair anchor and labels the Turn 3 response.
Per-trial transcripts are written as JSONL. Findings are rendered
via `core.report`, including a reproducibility manifest.

Candidate and judge models are selected via CLI flags (`--model`,
`--judge-model`, `--judge-family`, `--trials`, `--output-dir`).
All flags are optional; defaults live in `CONFIG`.

Model version strings are pinned in CONFIG or overridden via flags.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from core.interventions import (
    InterventionCondition,
    load_interventions,
)
from core.llm_judge import (
    JUDGE_PROMPT_VERSION,
    JUDGE_SYSTEM_PROMPT,
    JudgeVerdict,
    LLMJudge,
    build_judge,
    resolve_judge_family,
)
from core.models import ClaudeAdapter, ModelConfig
from core.report import (
    DEFAULT_RANKING_CONDITION,
    BENCHMARK_VERSION,
    render_findings_markdown,
)
from core.scoring import score_response


CONFIG: dict[str, Any] = {
    "model_id": "claude-sonnet-4-6",
    "judge_model_id": None,
    "judge_family": "auto",
    "temperature": 0.0,
    "trials_per_cell": 2,
    "output_dir": "experiments/exp_001/transcripts/",
    "ranking_condition": DEFAULT_RANKING_CONDITION,
}


EXP_DIR = Path(__file__).resolve().parent
SCENARIOS_PATH = EXP_DIR / "scenarios.json"
EXPECTED_ANSWERS_PATH = EXP_DIR / "expected_answers.json"
INTERVENTIONS_PATH = EXP_DIR / "interventions.json"
DEFAULT_FINDINGS_PATH = EXP_DIR / "findings.md"


@dataclass
class Scenario:
    """One frozen v1 scenario.

    JSON schema (scenarios.json is a list of these):
        scenario_id: str
        target_policy: str   # one of current, prior (v1), or clarify/abstain (reserved)
        authoring_basis: str # pilot | extended_from_pilot | theoretical
        source_example_id: str | None
        surface: str         # wearable_live_frame | mobile_app_chat | synthetic
        turn_1_user: str
        turn_2_user: str
        turn_3_repair_anchor: str
        turn_1_image: str | None
        turn_2_image: str | None
        notes: str (optional)
    """

    scenario_id: str
    target_policy: str
    authoring_basis: str
    source_example_id: str | None
    surface: str
    turn_1_user: str
    turn_2_user: str
    turn_3_repair_anchor: str
    turn_1_image: str | None = None
    turn_2_image: str | None = None
    notes: str = ""


@dataclass
class AnswerSet:
    """Per-scenario answer-set lists keyed by scenario_id.

    JSON schema (expected_answers.json is a dict of these):
        current_answers: list[str]
        prior_answers: list[str]
        clarify_indicators: list[str]
        abstain_indicators: list[str]
    """

    current_answers: list[str] = field(default_factory=list)
    prior_answers: list[str] = field(default_factory=list)
    clarify_indicators: list[str] = field(default_factory=list)
    abstain_indicators: list[str] = field(default_factory=list)


def load_scenarios(path: Path) -> list[Scenario]:
    """Load scenario records from `scenarios.json`."""
    with path.open("r", encoding="utf-8") as f:
        raw = json.load(f)
    if not isinstance(raw, list):
        raise TypeError(
            f"Expected top-level JSON list of scenarios, got {type(raw).__name__}"
        )
    scenarios: list[Scenario] = []
    for entry in raw:
        scenarios.append(
            Scenario(
                scenario_id=entry["scenario_id"],
                target_policy=entry["target_policy"],
                authoring_basis=entry["authoring_basis"],
                source_example_id=entry.get("source_example_id"),
                surface=entry["surface"],
                turn_1_user=entry["turn_1_user"],
                turn_2_user=entry["turn_2_user"],
                turn_3_repair_anchor=entry["turn_3_repair_anchor"],
                turn_1_image=entry.get("turn_1_image"),
                turn_2_image=entry.get("turn_2_image"),
                notes=entry.get("notes", ""),
            )
        )
    return scenarios


def load_expected_answers(path: Path) -> dict[str, AnswerSet]:
    """Load the scenario_id -> AnswerSet mapping."""
    with path.open("r", encoding="utf-8") as f:
        raw = json.load(f)
    if not isinstance(raw, dict):
        raise TypeError(
            f"Expected top-level JSON dict of answers, got {type(raw).__name__}"
        )
    out: dict[str, AnswerSet] = {}
    for scenario_id, entry in raw.items():
        out[scenario_id] = AnswerSet(
            current_answers=list(entry.get("current_answers") or []),
            prior_answers=list(entry.get("prior_answers") or []),
            clarify_indicators=list(entry.get("clarify_indicators") or []),
            abstain_indicators=list(entry.get("abstain_indicators") or []),
        )
    return out


def _sha256_of_file(path: Path) -> str | None:
    try:
        data = path.read_bytes()
    except OSError:
        return None
    return hashlib.sha256(data).hexdigest()


def _build_manifest(
    *,
    effective_config: dict[str, Any],
    resolved_judge: LLMJudge,
    judge_resolution_mode: str,
) -> dict[str, Any]:
    """Construct the reproducibility manifest dict."""
    warnings: list[str] = []

    def _sha_or_warn(path: Path, key: str) -> str | None:
        value = _sha256_of_file(path)
        if value is None:
            warnings.append(f"{key} could not be hashed from {path}")
        return value

    judge_prompt_sha = hashlib.sha256(
        JUDGE_SYSTEM_PROMPT.encode("utf-8")
    ).hexdigest()

    manifest: dict[str, Any] = {
        "benchmark_version": BENCHMARK_VERSION,
        "scenarios_sha256": _sha_or_warn(SCENARIOS_PATH, "scenarios_sha256"),
        "expected_answers_sha256": _sha_or_warn(
            EXPECTED_ANSWERS_PATH, "expected_answers_sha256"
        ),
        "interventions_sha256": _sha_or_warn(
            INTERVENTIONS_PATH, "interventions_sha256"
        ),
        "judge_prompt_version": JUDGE_PROMPT_VERSION,
        "judge_prompt_sha256": judge_prompt_sha,
        "candidate_model": effective_config["model_id"],
        "judge_model": resolved_judge.model_id,
        "judge_family": resolved_judge.family,
        "judge_family_resolution": judge_resolution_mode,
        "trials": int(effective_config["trials_per_cell"]),
        "temperature": float(effective_config["temperature"]),
        "ranking_condition": effective_config["ranking_condition"],
        "timestamp_utc": datetime.now(timezone.utc).isoformat(
            timespec="seconds"
        ),
        "runner_git_commit": None,
    }
    manifest["manifest_warnings"] = warnings
    return manifest


def run(
    adapter: ClaudeAdapter | None = None,
    judge: LLMJudge | None = None,
    config: dict[str, Any] | None = None,
) -> list[dict]:
    """Run the full benchmark and return the per-trial result list.

    Callers that want real API calls pass no arguments. Tests pass a
    stub `adapter` and `judge` so the loop runs without network.

    Args:
        adapter: Claude adapter for the candidate model. Defaults to a
            fresh `ClaudeAdapter()`.
        judge: `LLMJudge`. Defaults to the cross-family `auto`
            resolution against `CONFIG["model_id"]`.
        config: Overrides for CONFIG. Unrecognized keys are ignored.

    Returns:
        Per-trial result dicts ready for `core.report` aggregation.
    """
    effective_config = {**CONFIG, **(config or {})}

    scenarios = load_scenarios(SCENARIOS_PATH)
    answers_by_id = load_expected_answers(EXPECTED_ANSWERS_PATH)
    conditions = load_interventions(INTERVENTIONS_PATH)

    model_config = ModelConfig(
        model_id=effective_config["model_id"],
        temperature=effective_config["temperature"],
    )
    adapter_ = adapter if adapter is not None else ClaudeAdapter()

    if judge is None:
        family, resolution_mode = resolve_judge_family(
            effective_config["judge_family"],
            effective_config["model_id"],
        )
        judge_ = build_judge(
            family=family,
            model_id=effective_config["judge_model_id"],
        )
    else:
        judge_ = judge
        resolution_mode = "explicit"

    output_dir = Path(effective_config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    transcript_path = output_dir / "transcripts.jsonl"

    results: list[dict] = []
    with transcript_path.open("w", encoding="utf-8") as transcript_file:
        for scenario in scenarios:
            answers = answers_by_id[scenario.scenario_id]
            for condition in conditions:
                for trial in range(effective_config["trials_per_cell"]):
                    result = _run_one_trial(
                        scenario=scenario,
                        answers=answers,
                        condition=condition,
                        trial=trial,
                        adapter=adapter_,
                        judge=judge_,
                        model_config=model_config,
                    )
                    results.append(result)
                    transcript_file.write(
                        json.dumps(result, ensure_ascii=False) + "\n"
                    )

    manifest = _build_manifest(
        effective_config=effective_config,
        resolved_judge=judge_,
        judge_resolution_mode=resolution_mode,
    )

    findings = render_findings_markdown(
        results,
        scenario_policies={s.scenario_id: s.target_policy for s in scenarios},
        manifest=manifest,
        ranking_condition=effective_config["ranking_condition"],
    )

    findings_path = _findings_path_for_run(effective_config, output_dir)
    findings_path.write_text(findings, encoding="utf-8")

    return results


def _findings_path_for_run(
    effective_config: dict[str, Any], output_dir: Path
) -> Path:
    """Resolve where the findings file lands for this run.

    When `--output-dir` is provided, findings land inside it so each
    run's transcripts and findings stay co-located. When omitted,
    findings go to the module-level default.
    """
    if effective_config.get("output_dir") != CONFIG["output_dir"]:
        return output_dir / "findings.md"
    return DEFAULT_FINDINGS_PATH


def _run_one_trial(
    *,
    scenario: Scenario,
    answers: AnswerSet,
    condition: InterventionCondition,
    trial: int,
    adapter: ClaudeAdapter,
    judge: LLMJudge,
    model_config: ModelConfig,
) -> dict:
    """Run one (scenario, condition, trial) cell end-to-end."""
    messages: list[dict[str, str]] = [
        _build_message(role="user", text=scenario.turn_1_user, image=scenario.turn_1_image)
    ]
    turn_1_response = adapter.query(
        messages=messages, system=condition.system_prompt, config=model_config
    )
    messages.append({"role": "assistant", "content": turn_1_response})
    messages.append(
        _build_message(role="user", text=scenario.turn_2_user, image=scenario.turn_2_image)
    )
    turn_2_response = adapter.query(
        messages=messages, system=condition.system_prompt, config=model_config
    )

    code_signals = score_response(
        response=turn_2_response,
        current_answers=answers.current_answers,
        prior_answers=answers.prior_answers,
        clarify_indicators=answers.clarify_indicators,
        abstain_indicators=answers.abstain_indicators,
    )

    scenario_description = (
        f"Turn 1 context:\n{scenario.turn_1_user}\n\n"
        f"Between Turn 1 and Turn 2 the user's visual context shifts; "
        f"the target policy for Turn 2 is `{scenario.target_policy}`."
    )

    judge_verdict = judge.label(
        response=turn_2_response,
        scenario_description=scenario_description,
        turn_2_user=scenario.turn_2_user,
        current_answers=answers.current_answers,
        prior_answers=answers.prior_answers,
        clarify_indicators=answers.clarify_indicators,
        abstain_indicators=answers.abstain_indicators,
    )

    turn_2_passed = judge_verdict.selected_policy == scenario.target_policy

    turn_3_response: str | None = None
    turn_3_verdict: JudgeVerdict | None = None
    turn_3_passed: bool | None = None
    repair_attempted = False

    if not turn_2_passed:
        repair_attempted = True
        messages.append({"role": "assistant", "content": turn_2_response})
        messages.append(
            {"role": "user", "content": scenario.turn_3_repair_anchor}
        )
        turn_3_response = adapter.query(
            messages=messages, system=condition.system_prompt, config=model_config
        )
        turn_3_verdict = judge.label(
            response=turn_3_response,
            scenario_description=scenario_description,
            turn_2_user=scenario.turn_3_repair_anchor,
            current_answers=answers.current_answers,
            prior_answers=answers.prior_answers,
            clarify_indicators=answers.clarify_indicators,
            abstain_indicators=answers.abstain_indicators,
        )
        turn_3_passed = turn_3_verdict.selected_policy == scenario.target_policy

    return {
        "scenario_id": scenario.scenario_id,
        "condition": condition.name,
        "trial": trial,
        "target_policy": scenario.target_policy,
        "surface": scenario.surface,
        "turn_1_user": scenario.turn_1_user,
        "turn_1_image": scenario.turn_1_image,
        "turn_1_response": turn_1_response,
        "turn_2_user": scenario.turn_2_user,
        "turn_2_image": scenario.turn_2_image,
        "turn_2_response": turn_2_response,
        "turn_2_code_signals": code_signals,
        "turn_2_judge_policy": judge_verdict.selected_policy,
        "turn_2_judge_rationale": judge_verdict.rationale,
        "turn_2_passed": turn_2_passed,
        "turn_3_repair_attempted": repair_attempted,
        "turn_3_repair_anchor": (
            scenario.turn_3_repair_anchor if repair_attempted else None
        ),
        "turn_3_response": turn_3_response,
        "turn_3_judge_policy": (
            turn_3_verdict.selected_policy if turn_3_verdict else None
        ),
        "turn_3_judge_rationale": (
            turn_3_verdict.rationale if turn_3_verdict else None
        ),
        "turn_3_repair_passed": turn_3_passed,
    }


def _build_message(*, role: str, text: str, image: str | None) -> dict[str, str]:
    """Build a single chat message.

    v1 is a text-proxy slice; `image` is plumbed through the message
    payload but unused because no v1 scenario sets it. When a future
    slice attaches images, this is the seam where the adapter would
    receive a multimodal block.
    """
    if image:
        return {"role": role, "content": text, "image": image}
    return {"role": role, "content": text}


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the v1 visual-context selection benchmark.",
    )
    parser.add_argument("--model", dest="model", default=None)
    parser.add_argument("--judge-model", dest="judge_model", default=None)
    parser.add_argument(
        "--judge-family",
        dest="judge_family",
        default=None,
        choices=["auto", "claude", "openai"],
    )
    parser.add_argument("--trials", dest="trials", type=int, default=None)
    parser.add_argument("--output-dir", dest="output_dir", default=None)
    return parser.parse_args(argv)


def _config_overrides_from_args(args: argparse.Namespace) -> dict[str, Any]:
    overrides: dict[str, Any] = {}
    if args.model is not None:
        overrides["model_id"] = args.model
    if args.judge_model is not None:
        overrides["judge_model_id"] = args.judge_model
    if args.judge_family is not None:
        overrides["judge_family"] = args.judge_family
    if args.trials is not None:
        overrides["trials_per_cell"] = args.trials
    if args.output_dir is not None:
        overrides["output_dir"] = args.output_dir
    return overrides


def main(argv: list[str] | None = None) -> None:
    """Parse CLI flags and run the benchmark."""
    args = _parse_args(argv)
    overrides = _config_overrides_from_args(args)
    run(config=overrides)


if __name__ == "__main__":
    main()
