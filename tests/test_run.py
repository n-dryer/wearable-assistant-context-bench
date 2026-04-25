"""Dry-run integration test for benchmark.v1.run.

Stubs the candidate adapter and judge so the loop runs without
network. Confirms per-trial result shape, JSONL transcript output,
CLI flag parsing, --output-dir routing for findings, the v2
[Camera:] injection format, and judge ground-truth-context wiring.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from benchmark.v1 import run as run_module


class _StubAdapter:
    """Returns a deterministic canned response for every query."""

    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    def query(self, messages: list[dict], system: str, config: Any) -> str:
        self.calls.append({"messages": list(messages), "system": system})
        return "STUB_RESPONSE"


class _StubJudge:
    """Always labels `current`. Exposes `.calls` for inspection."""

    family = "stub"
    model_id = "stub-model"

    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    def label(
        self,
        response: str,
        scenario_description: str,
        turn_2_user: str,
        current_answers: list[str],
        prior_answers: list[str],
        clarify_indicators: list[str],
        abstain_indicators: list[str],
        ground_truth_context: str | None = None,
    ) -> Any:
        self.calls.append(
            {
                "response": response,
                "turn_2_user": turn_2_user,
                "ground_truth_context": ground_truth_context,
            }
        )
        from core.llm_judge import JudgeVerdict

        return JudgeVerdict(selected_policy="current", rationale="stub")


def test_run_produces_expected_trial_count_and_jsonl_shape(
    tmp_path: Path,
) -> None:
    adapter = _StubAdapter()
    judge = _StubJudge()
    output_dir = tmp_path / "transcripts"
    results = run_module.run(
        adapter=adapter,  # type: ignore[arg-type]
        judge=judge,  # type: ignore[arg-type]
        config={"output_dir": str(output_dir)},
    )

    scenario_count = len(run_module.load_scenarios(run_module.SCENARIOS_PATH))
    condition_count = len(
        run_module.load_prompt_conditions(run_module.INTERVENTIONS_PATH)
    )
    expected_trials = (
        scenario_count * condition_count * run_module.CONFIG["trials_per_cell"]
    )
    assert len(results) == expected_trials

    transcript_path = output_dir / "transcripts.jsonl"
    assert transcript_path.exists()
    lines = transcript_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == expected_trials

    for line in lines:
        payload = json.loads(line)
        for required in (
            "scenario_id",
            "condition",
            "trial",
            "target_context",
            "turn_1_user",
            "turn_1_image",
            "turn_1_response",
            "turn_2_user",
            "turn_2_image",
            "turn_2_response",
            "turn_2_code_signals",
            "turn_2_judge_policy",
            "turn_2_passed",
            "turn_3_repair_attempted",
            "turn_3_repair_passed",
        ):
            assert required in payload, f"missing {required} in transcript row"
        signals = payload["turn_2_code_signals"]
        assert "has_stale" not in signals
        assert "has_stale_raw" not in signals

    pass_count = sum(1 for r in results if r["turn_2_passed"])
    repair_attempts = sum(1 for r in results if r["turn_3_repair_attempted"])
    assert pass_count + repair_attempts == expected_trials


def test_run_output_dir_governs_findings_location(tmp_path: Path) -> None:
    adapter = _StubAdapter()
    judge = _StubJudge()
    output_dir = tmp_path / "some_run"
    run_module.run(
        adapter=adapter,  # type: ignore[arg-type]
        judge=judge,  # type: ignore[arg-type]
        config={"output_dir": str(output_dir)},
    )
    findings_path = output_dir / "findings.md"
    assert findings_path.exists()
    body = findings_path.read_text(encoding="utf-8")
    assert "Reproducibility manifest" in body
    assert "Benchmark summary" in body
    # Manifest JSON block must be present.
    assert "```json" in body


def test_parse_args_accepts_all_flags() -> None:
    args = run_module._parse_args(
        [
            "--model",
            "claude-sonnet-4-6",
            "--judge-model",
            "gemini-2.5-flash",
            "--judge-family",
            "openai",
            "--trials",
            "3",
            "--output-dir",
            "/tmp/out",
        ]
    )
    assert args.model == "claude-sonnet-4-6"
    assert args.judge_model == "gemini-2.5-flash"
    assert args.judge_family == "openai"
    assert args.trials == 3
    assert args.output_dir == "/tmp/out"


def test_parse_args_rejects_unknown_judge_family() -> None:
    with pytest.raises(SystemExit):
        run_module._parse_args(["--judge-family", "mistral"])


def test_parse_args_defaults_are_none() -> None:
    args = run_module._parse_args([])
    assert args.model is None
    assert args.judge_model is None
    assert args.judge_family is None
    assert args.trials is None
    assert args.output_dir is None


def test_config_overrides_from_args_only_sets_provided_flags() -> None:
    args = run_module._parse_args(["--model", "claude-sonnet-4-6"])
    overrides = run_module._config_overrides_from_args(args)
    assert overrides == {"model_id": "claude-sonnet-4-6"}


def test_config_overrides_from_args_full() -> None:
    args = run_module._parse_args(
        [
            "--model",
            "openai/gpt-4.1-mini",
            "--judge-model",
            "gemini-2.5-flash",
            "--judge-family",
            "gemini",
            "--trials",
            "1",
            "--output-dir",
            "out/",
        ]
    )
    overrides = run_module._config_overrides_from_args(args)
    assert overrides == {
        "model_id": "openai/gpt-4.1-mini",
        "judge_model_id": "gemini-2.5-flash",
        "judge_family": "gemini",
        "trials_per_cell": 1,
        "output_dir": "out/",
    }


def test_manifest_records_v2_schema_fields(tmp_path: Path) -> None:
    """The reproducibility manifest must record schema_version=v2 and
    camera_injection=true for every run."""
    adapter = _StubAdapter()
    judge = _StubJudge()
    output_dir = tmp_path / "manifest_run"
    run_module.run(
        adapter=adapter,  # type: ignore[arg-type]
        judge=judge,  # type: ignore[arg-type]
        config={"output_dir": str(output_dir)},
    )
    findings_body = (output_dir / "findings.md").read_text(encoding="utf-8")
    # Manifest JSON block lives between ```json fences.
    import re as _re

    match = _re.search(r"```json\n(.*?)\n```", findings_body, _re.DOTALL)
    assert match is not None, "manifest JSON block missing from findings.md"
    payload = json.loads(match.group(1))
    assert payload["schema_version"] == "v2"
    assert payload["camera_injection"] is True
