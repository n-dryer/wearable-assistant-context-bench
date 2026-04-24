from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
SCENARIOS_PATH = REPO_ROOT / "benchmark" / "v1" / "scenarios.json"
AUDIT_JSONL_PATH = REPO_ROOT / "docs" / "audits" / "2026-04-22-scenario-audit.jsonl"
AUDIT_CSV_PATH = REPO_ROOT / "docs" / "audits" / "2026-04-22-scenario-audit.csv"
AUDIT_MD_PATH = REPO_ROOT / "docs" / "audits" / "2026-04-22-scenario-audit.md"
BOOTSTRAP_AUDIT_SCRIPT = (
    REPO_ROOT / "scripts" / "scenario_audit" / "bootstrap_audit.py"
)

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


def load_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def test_audit_artifact_covers_canonical_bank() -> None:
    scenarios = json.loads(SCENARIOS_PATH.read_text(encoding="utf-8"))
    audit_rows = load_jsonl(AUDIT_JSONL_PATH)
    csv_rows = list(csv.DictReader(AUDIT_CSV_PATH.open("r", encoding="utf-8")))

    scenario_map = {scenario["scenario_id"]: scenario for scenario in scenarios}
    assert len(audit_rows) == len(scenarios) == 101
    assert len(csv_rows) == len(audit_rows)

    seen: set[str] = set()
    for row in audit_rows:
        sid = row["scenario_id"]
        assert sid in scenario_map
        assert sid not in seen
        seen.add(sid)

        assert row["title"]
        assert row["description"]
        assert row["alignment"] in ALLOWED_ALIGNMENTS
        assert row["evidence_status"] in ALLOWED_EVIDENCE_STATUSES
        assert row["scenario_action"] in ALLOWED_SCENARIO_ACTIONS
        assert row["answer_key_action"] in ALLOWED_ANSWER_KEY_ACTIONS
        assert row["severity"] in ALLOWED_SEVERITIES
        assert row["what_works"]
        assert row["what_doesnt"]
        assert row["gap_analysis"]
        assert row["recommended_changes"]

        category = row["category"]
        source = scenario_map[sid]
        assert category["target_context"] == source["target_context"]
        assert category["cue_type"] == source.get("cue_type")
        assert category["activity_domain"] == source.get("activity_domain")
        assert category["modality_required"] == source.get("modality_required")

        assert set(row["issue_types"]).issubset(ALLOWED_ISSUE_TYPES)

        rewritten_scenario = row["rewritten_scenario"]
        if row["scenario_action"] == "rewrite":
            assert rewritten_scenario is not None
            assert rewritten_scenario["turn_1_user"]
            assert rewritten_scenario["turn_2_user"]
            assert rewritten_scenario["turn_3_repair_anchor"]
        else:
            assert rewritten_scenario is None

        rewritten_answer_keys = row["rewritten_answer_keys"]
        if row["answer_key_action"] == "rewrite":
            assert rewritten_answer_keys is not None
            for key in (
                "current_answers",
                "prior_answers",
                "clarify_indicators",
                "abstain_indicators",
            ):
                assert key in rewritten_answer_keys
                assert isinstance(rewritten_answer_keys[key], list)
        else:
            assert rewritten_answer_keys is None

        if row["scenario_action"] == "merge":
            assert row["overlap_with"]
            for overlap in row["overlap_with"]:
                assert overlap in scenario_map
                assert (
                    scenario_map[overlap]["target_context"]
                    == source["target_context"]
                )


def test_bootstrap_audit_is_deterministic(tmp_path: Path) -> None:
    """Regenerating the audit artifacts must produce byte-identical outputs.

    Guards against silent drift between the committed audit artifacts and the
    reproducible generator. If scenarios.json or expected_answers.json change,
    the generator must be re-run and the committed artifacts refreshed in the
    same commit.
    """

    regen_jsonl = tmp_path / "regen.jsonl"
    regen_csv = tmp_path / "regen.csv"
    regen_md = tmp_path / "regen.md"

    result = subprocess.run(
        [
            sys.executable,
            str(BOOTSTRAP_AUDIT_SCRIPT),
            "build",
            "--jsonl-out",
            str(regen_jsonl),
            "--csv-out",
            str(regen_csv),
            "--markdown-out",
            str(regen_md),
        ],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
    )
    assert result.returncode == 0, (
        f"bootstrap_audit.py build failed:\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )

    assert (
        regen_jsonl.read_bytes() == AUDIT_JSONL_PATH.read_bytes()
    ), "Regenerated JSONL differs from committed audit artifact"
    assert (
        regen_csv.read_bytes() == AUDIT_CSV_PATH.read_bytes()
    ), "Regenerated CSV differs from committed audit artifact"
    assert (
        regen_md.read_bytes() == AUDIT_MD_PATH.read_bytes()
    ), "Regenerated Markdown differs from committed audit artifact"
