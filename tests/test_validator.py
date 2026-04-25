"""Run the four programmatic validator checks against the scenario bank.

`scripts/validate_scenarios.py` exposes four programmatic checks (Checks 1,
2, 3, and 6 from the rebuild plan):

  * Check 1 — token leakage from `current_answers`/`prior_answers` into
    user-speech fields
  * Check 2 — common object names appearing inside camera image fields
  * Check 3 — schema validation: required fields, enums, IDs, distributions,
    answer-set contracts, and per-cue-type constraints
  * Check 6 — cross-scenario duplication on T2 user/image and on the
    (cue_type, target_context, difficulty_tier, activity_domain) signature

This test imports the four functions directly and asserts each returns
zero failures against the committed scenario bank. The same checks run
in CI via the validator script invocation in `.github/workflows/test.yml`.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
SCENARIOS_PATH = REPO_ROOT / "benchmark" / "v1" / "scenarios.json"
EXPECTED_ANSWERS_PATH = REPO_ROOT / "benchmark" / "v1" / "expected_answers.json"


# Make `scripts/validate_scenarios.py` importable. The script lives outside
# any package so we add `scripts/` to sys.path explicitly.
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import validate_scenarios  # type: ignore[import-not-found]


@pytest.fixture(scope="module")
def scenarios() -> list[dict]:
    return json.loads(SCENARIOS_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def answers() -> dict:
    return json.loads(EXPECTED_ANSWERS_PATH.read_text(encoding="utf-8"))


def _format_fails(fails: list[dict]) -> str:
    return "\n".join(
        f"  [{f['check']}] {f['scenario_id']}: {f['detail']}" for f in fails
    )


def test_check_1_token_leakage_passes(scenarios, answers) -> None:
    fails = validate_scenarios.check_1_token_leakage(scenarios, answers)
    assert not fails, (
        f"check_1_token_leakage produced {len(fails)} failure(s):\n"
        f"{_format_fails(fails)}"
    )


def test_check_2_object_names_in_images_passes(scenarios) -> None:
    fails = validate_scenarios.check_2_object_name_in_images(scenarios)
    assert not fails, (
        f"check_2_object_name_in_images produced {len(fails)} failure(s):\n"
        f"{_format_fails(fails)}"
    )


def test_check_3_schema_validation_passes(scenarios, answers) -> None:
    fails = validate_scenarios.check_3_schema_validation(scenarios, answers)
    assert not fails, (
        f"check_3_schema_validation produced {len(fails)} failure(s):\n"
        f"{_format_fails(fails)}"
    )


def test_check_6_duplication_passes(scenarios) -> None:
    fails = validate_scenarios.check_6_duplication(scenarios)
    assert not fails, (
        f"check_6_duplication produced {len(fails)} failure(s):\n"
        f"{_format_fails(fails)}"
    )


def test_validator_main_returns_zero(monkeypatch, capsys) -> None:
    """Smoke-test the CLI entry point: `main()` must exit 0 against the
    scenario bank and print a success line."""
    monkeypatch.setattr(sys, "argv", ["validate_scenarios.py"])
    # validate_scenarios.SCENARIOS_PATH and ANSWERS_PATH are module-level
    # constants relative to the repo root; the script is run from the repo
    # root in CI, so we cd there for this test too.
    monkeypatch.chdir(REPO_ROOT)
    rc = validate_scenarios.main()
    assert rc == 0
    out = capsys.readouterr().out
    assert "All checks passed" in out
