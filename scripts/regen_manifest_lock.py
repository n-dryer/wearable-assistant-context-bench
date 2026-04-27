"""Regenerate the static asset lockfile at ``benchmark/v1/MANIFEST.lock.json``.

The lockfile pins SHA256 hashes of the scenario bank, expected answers,
prompt-condition definitions, and the judge-prompt template, alongside
the benchmark and judge-prompt versions. ``scripts/validate_scenarios.py``
compares the computed hashes against this lockfile and fails CI if any
drift without a coordinated ``BENCHMARK_VERSION`` (or
``JUDGE_PROMPT_VERSION``) bump.

Run this script after a coordinated content change is merged to refresh
the lockfile.

Usage:
    python scripts/regen_manifest_lock.py
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LOCKFILE_PATH = REPO_ROOT / "benchmark" / "v1" / "MANIFEST.lock.json"
SCENARIOS_PATH = REPO_ROOT / "benchmark" / "v1" / "scenarios.json"
EXPECTED_ANSWERS_PATH = REPO_ROOT / "benchmark" / "v1" / "expected_answers.json"
INTERVENTIONS_PATH = REPO_ROOT / "benchmark" / "v1" / "interventions.json"
ADV_SCENARIOS_PATH = REPO_ROOT / "benchmark" / "v1" / "scenarios_adversarial.json"
ADV_ANSWERS_PATH = REPO_ROOT / "benchmark" / "v1" / "expected_answers_adversarial.json"
HARD_SCENARIOS_PATH = REPO_ROOT / "benchmark" / "v1" / "scenarios_v2_candidates.json"
HARD_ANSWERS_PATH = REPO_ROOT / "benchmark" / "v1" / "expected_answers_v2_candidates.json"

LOCKFILE_NOTE = (
    "Static lockfile. scripts/validate_scenarios.py compares computed "
    "hashes against this lock and fails CI if they drift without a "
    "coordinated benchmark_version bump. Regenerate by running "
    "scripts/regen_manifest_lock.py."
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_lockfile() -> dict:
    sys.path.insert(0, str(REPO_ROOT))
    from core.llm_judge import JUDGE_PROMPT_VERSION, JUDGE_SYSTEM_PROMPT
    from core.report import BENCHMARK_VERSION, SCHEMA_REVISION

    lockfile = {
        "benchmark_version": BENCHMARK_VERSION,
        "schema_revision": SCHEMA_REVISION,
        "judge_prompt_version": JUDGE_PROMPT_VERSION,
        "judge_prompt_sha256": hashlib.sha256(
            JUDGE_SYSTEM_PROMPT.encode("utf-8")
        ).hexdigest(),
        "scenarios_sha256": _sha256(SCENARIOS_PATH),
        "expected_answers_sha256": _sha256(EXPECTED_ANSWERS_PATH),
        "interventions_sha256": _sha256(INTERVENTIONS_PATH),
    }
    if ADV_SCENARIOS_PATH.exists() and ADV_ANSWERS_PATH.exists():
        lockfile["adversarial_scenarios_sha256"] = _sha256(ADV_SCENARIOS_PATH)
        lockfile["adversarial_expected_answers_sha256"] = _sha256(ADV_ANSWERS_PATH)
    if HARD_SCENARIOS_PATH.exists() and HARD_ANSWERS_PATH.exists():
        lockfile["hard_scenarios_sha256"] = _sha256(HARD_SCENARIOS_PATH)
        lockfile["hard_expected_answers_sha256"] = _sha256(HARD_ANSWERS_PATH)
    lockfile["_note"] = LOCKFILE_NOTE
    return lockfile


def main() -> int:
    lockfile = build_lockfile()
    LOCKFILE_PATH.write_text(json.dumps(lockfile, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {LOCKFILE_PATH.relative_to(REPO_ROOT)}")
    for key, value in lockfile.items():
        if key == "_note":
            continue
        print(f"  {key}: {value}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
