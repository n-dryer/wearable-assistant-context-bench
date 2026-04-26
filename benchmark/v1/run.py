"""Runner for the Wearable Assistant Context Benchmark v1.

This runner implements the benchmark task over the v1 scenario set,
with a configurable trial count per cell, as a 2-turn conversation.
On Turn 2 failure it fires a templated Turn 3 "I mean, ..." repair
anchor and labels the Turn 3 response. Per-trial transcripts are
written as JSONL. Findings are rendered via `core.report`, including
a reproducibility manifest.

Candidate and judge models are selected via CLI flags (`--model`,
`--judge-model`, `--judge-family`, `--trials`, `--output-dir`).
All flags are optional; defaults live in `CONFIG`.

Model version strings are pinned in CONFIG or overridden via flags.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from core.interventions import PromptCondition, load_prompt_conditions
from core.llm_judge import (
    JUDGE_PROMPT_VERSION,
    JUDGE_SYSTEM_PROMPT,
    JudgeVerdict,
    LLMJudge,
    build_judge,
    infer_candidate_family,
    resolve_judge_family,
)
from core.gemini_adapter import GeminiAdapter
from core.litellm_adapter import LiteLLMAdapter
from core.models import ClaudeAdapter, ModelConfig
from core.report import (
    DEFAULT_RANKING_CONDITION,
    BENCHMARK_VERSION,
    render_findings_markdown,
)
from core.scoring import score_response

EXP_DIR = Path(__file__).resolve().parent
DEFAULT_OUTPUT_DIR = EXP_DIR / "runs" / "latest"
SCENARIOS_PATH = EXP_DIR / "scenarios.json"
EXPECTED_ANSWERS_PATH = EXP_DIR / "expected_answers.json"
INTERVENTIONS_PATH = EXP_DIR / "interventions.json"


CONFIG: dict[str, Any] = {
    "model_id": "claude-sonnet-4-6",
    "judge_model_id": None,
    "judge_family": "auto",
    "temperature": 0.0,
    "trials_per_cell": 2,
    "output_dir": str(DEFAULT_OUTPUT_DIR),
    "ranking_condition": DEFAULT_RANKING_CONDITION,
    "no_camera": False,
}


@dataclass
class Scenario:
    """One scenario.

    JSON schema (scenarios.json is a list of these):
        scenario_id: str
        target_context: str   # current | prior | clarify | abstain
        cue_type: str         # one of the 8 cue_type values
        activity_domain: str
        cognitive_load: str
        difficulty_tier: str  # easy | medium | hard
        time_gap_bucket: str | None
        context_image: str | None  # pre-T1 camera state, null when unused
        turn_1_image: str          # camera description at T1
        turn_1_user: str
        turn_2_image: str          # camera description at T2
        turn_2_user: str
        turn_3_repair_anchor: str
        notes: str (optional)
    """

    scenario_id: str
    target_context: str
    cue_type: str
    activity_domain: str
    cognitive_load: str
    difficulty_tier: str
    turn_1_image: str
    turn_1_user: str
    turn_2_image: str
    turn_2_user: str
    turn_3_repair_anchor: str
    context_image: str | None = None
    time_gap_bucket: str | None = None
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
                target_context=entry["target_context"],
                cue_type=entry["cue_type"],
                activity_domain=entry["activity_domain"],
                cognitive_load=entry["cognitive_load"],
                difficulty_tier=entry["difficulty_tier"],
                turn_1_image=entry["turn_1_image"],
                turn_1_user=entry["turn_1_user"],
                turn_2_image=entry["turn_2_image"],
                turn_2_user=entry["turn_2_user"],
                turn_3_repair_anchor=entry["turn_3_repair_anchor"],
                context_image=entry.get("context_image"),
                time_gap_bucket=entry.get("time_gap_bucket"),
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


def _current_git_commit() -> str:
    """Return the current git HEAD SHA, or "unknown" if unavailable."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=EXP_DIR,
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (FileNotFoundError, subprocess.SubprocessError, OSError):
        return "unknown"
    if result.returncode != 0:
        return "unknown"
    sha = result.stdout.strip()
    return sha or "unknown"


def _build_adapter(model_id: str) -> Any:
    """Pick a candidate adapter based on the model string and family."""
    family = infer_candidate_family(model_id)
    if "/" in model_id or family == "openai":
        return LiteLLMAdapter()
    if family == "claude":
        return ClaudeAdapter()
    if family == "gemini":
        return GeminiAdapter()
    raise ValueError(
        f"Unsupported candidate model family for model_id={model_id!r}. "
        "Supported families: claude, gemini, openai, plus provider-qualified "
        "LiteLLM-backed model IDs such as openrouter/... and huggingface/...."
    )


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
        "schema_revision": 2,
        "camera_injection": not bool(effective_config.get("no_camera", False)),
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
        "runner_git_commit": _current_git_commit(),
        "random_seed": None,
    }
    manifest["manifest_warnings"] = warnings
    return manifest


def run(
    adapter: Any | None = None,
    judge: LLMJudge | None = None,
    config: dict[str, Any] | None = None,
) -> list[dict]:
    """Run the full benchmark and return the per-trial result list.

    Callers that want real API calls pass no arguments. Tests pass a
    stub `adapter` and `judge` so the loop runs without network.

    Args:
        adapter: Candidate adapter. Defaults to the family-appropriate
            adapter resolved from `model_id`.
        judge: `LLMJudge`. Defaults to the auto resolution against
            `CONFIG["model_id"]`.
        config: Overrides for CONFIG. Unrecognized keys are ignored.

    Returns:
        Per-trial result dicts ready for `core.report` aggregation.
    """
    effective_config = {**CONFIG, **(config or {})}

    scenarios = load_scenarios(SCENARIOS_PATH)
    answers_by_id = load_expected_answers(EXPECTED_ANSWERS_PATH)
    conditions = load_prompt_conditions(INTERVENTIONS_PATH)

    model_config = ModelConfig(
        model_id=effective_config["model_id"],
        temperature=effective_config["temperature"],
    )
    adapter_ = adapter if adapter is not None else _build_adapter(
        effective_config["model_id"]
    )

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
                        no_camera=bool(effective_config.get("no_camera", False)),
                    )
                    results.append(result)
                    transcript_file.write(
                        json.dumps(
                            {
                                **result,
                                "turn_2_code_signals": _public_code_signals(
                                    result["turn_2_code_signals"]
                                ),
                            },
                            ensure_ascii=False,
                        )
                        + "\n"
                    )

    manifest = _build_manifest(
        effective_config=effective_config,
        resolved_judge=judge_,
        judge_resolution_mode=resolution_mode,
    )

    findings = render_findings_markdown(
        results,
        scenario_policies={s.scenario_id: s.target_context for s in scenarios},
        manifest=manifest,
        ranking_condition=effective_config["ranking_condition"],
    )

    findings_path = output_dir / "findings.md"
    findings_path.write_text(findings, encoding="utf-8")

    return results

def _run_one_trial(
    *,
    scenario: Scenario,
    answers: AnswerSet,
    condition: PromptCondition,
    trial: int,
    adapter: Any,
    judge: LLMJudge,
    model_config: ModelConfig,
    no_camera: bool = False,
) -> dict:
    """Run one (scenario, condition, trial) cell end-to-end.

    When `no_camera` is True, the runner strips the `[Camera: ...]`
    blocks from every user message and skips injecting the
    `context_image` standalone message. The candidate sees only the
    user's spoken text. Used for camera channel ablation runs.
    """
    messages: list[dict[str, str]] = []
    # Pre-conversation camera state (only set on recall scenarios)
    if scenario.context_image and not no_camera:
        messages.append(_build_context_image_message(scenario.context_image))
    messages.append(
        _build_message(
            role="user",
            text=scenario.turn_1_user,
            image=None if no_camera else scenario.turn_1_image,
        )
    )
    turn_1_response = adapter.query(
        messages=messages, system=condition.system_prompt, config=model_config
    )
    messages.append({"role": "assistant", "content": turn_1_response})
    messages.append(
        _build_message(
            role="user",
            text=scenario.turn_2_user,
            image=None if no_camera else scenario.turn_2_image,
        )
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
        f"Between Turn 1 and Turn 2 the user's context changes; "
        f"the target context for Turn 2 is `{scenario.target_context}`."
    )

    ground_truth_context = _build_ground_truth_context(scenario)

    judge_verdict = judge.label(
        response=turn_2_response,
        scenario_description=scenario_description,
        turn_2_user=scenario.turn_2_user,
        current_answers=answers.current_answers,
        prior_answers=answers.prior_answers,
        clarify_indicators=answers.clarify_indicators,
        abstain_indicators=answers.abstain_indicators,
        ground_truth_context=ground_truth_context,
    )

    turn_2_passed = judge_verdict.selected_policy == scenario.target_context

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
            ground_truth_context=ground_truth_context,
        )
        turn_3_passed = turn_3_verdict.selected_policy == scenario.target_context

    return {
        "scenario_id": scenario.scenario_id,
        "condition": condition.name,
        "trial": trial,
        "target_context": scenario.target_context,
        "cue_type": scenario.cue_type,
        "activity_domain": scenario.activity_domain,
        "difficulty_tier": scenario.difficulty_tier,
        "context_image": scenario.context_image,
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


def _public_code_signals(signals: dict[str, Any]) -> dict[str, Any]:
    """Return the code-signal subset suitable for shipped transcripts."""
    return {
        key: value
        for key, value in signals.items()
        if key not in {"has_stale", "has_stale_raw"}
    }


def _build_ground_truth_context(scenario: Scenario) -> str:
    """Construct the judge-only ground-truth description.

    The candidate model sees perceptual camera descriptions only (no
    object names). The judge sees this richer ground-truth description
    so it can determine whether the response reflects T2 or T1 context.
    """
    parts: list[str] = []
    parts.append(
        f"Cue type: {scenario.cue_type}. "
        f"Target context: {scenario.target_context}. "
        f"Activity domain: {scenario.activity_domain}."
    )
    if scenario.context_image:
        parts.append(f"Pre-conversation camera state: {scenario.context_image}")
    parts.append(f"Turn 1 camera state: {scenario.turn_1_image}")
    parts.append(f"Turn 2 camera state: {scenario.turn_2_image}")
    if scenario.notes:
        parts.append(f"Authoring notes: {scenario.notes}")
    return "\n\n".join(parts)


def _build_message(*, role: str, text: str, image: str | None) -> dict[str, str]:
    """Build a single chat message with optional camera channel injection.

    The benchmark uses a perceptual-text proxy for the camera frame. When
    `image` is non-null, it is prepended to the user message as a tagged
    `[Camera: ...]` block, simulating what a vision backbone would have
    returned alongside the transcribed user speech.

    Format:
        [Camera: {image}]
        {text}

    The `[Camera:]` block represents content the candidate would have
    received from the wearable's vision channel; the user's spoken words
    follow on the next line.
    """
    if image:
        content = f"[Camera: {image}]\n{text}"
        return {"role": role, "content": content}
    return {"role": role, "content": text}


def _build_context_image_message(image: str) -> dict[str, str]:
    """Build a standalone camera channel message for `context_image`.

    `context_image` represents what the wearable's camera saw before any
    user speech began. It is injected as a user-role message containing
    only the `[Camera: ...]` block, with no spoken text. This precedes
    the T1 message in the conversation.
    """
    return {"role": "user", "content": f"[Camera: {image}]"}


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run v1 of the Wearable Assistant Context Benchmark."
        ),
        epilog=(
            "Example: python -m benchmark.v1.run "
            "--model claude-sonnet-4-6 --judge-model gemini-2.5-flash"
        ),
    )
    parser.add_argument(
        "--model",
        dest="model",
        default=None,
        help=(
            "candidate model ID; default is "
            f"{CONFIG['model_id']}"
        ),
    )
    parser.add_argument(
        "--judge-model",
        dest="judge_model",
        default=None,
        help=(
            "judge model ID; defaults to the family-specific judge chosen for "
            "the run"
        ),
    )
    parser.add_argument(
        "--judge-family",
        dest="judge_family",
        default=None,
        choices=["auto", "claude", "gemini", "openai"],
        help=(
            "judge family override; default is auto, which picks a judge "
            "from a different model family when candidate family inference succeeds"
        ),
    )
    parser.add_argument(
        "--trials",
        dest="trials",
        type=int,
        default=None,
        help=(
            "trials per (scenario, condition) cell; default is "
            f"{CONFIG['trials_per_cell']}"
        ),
    )
    parser.add_argument(
        "--output-dir",
        dest="output_dir",
        default=None,
        help=(
            "directory for transcripts, findings, and manifest; defaults to "
            f"{DEFAULT_OUTPUT_DIR}"
        ),
    )
    parser.add_argument(
        "--no-camera",
        dest="no_camera",
        action="store_true",
        default=False,
        help=(
            "ablation flag: strip [Camera: ...] blocks from every user "
            "message and skip injecting context_image. Run with this flag "
            "to measure the contribution of the camera channel by "
            "comparing the score against a normal run with the same model."
        ),
    )
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
    if getattr(args, "no_camera", False):
        overrides["no_camera"] = True
    return overrides


def main(argv: list[str] | None = None) -> None:
    """Parse CLI flags and run the benchmark."""
    args = _parse_args(argv)
    overrides = _config_overrides_from_args(args)
    run(config=overrides)


if __name__ == "__main__":
    main()
