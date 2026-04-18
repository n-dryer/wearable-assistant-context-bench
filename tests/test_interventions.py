"""Unit tests for core.interventions."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.interventions import (
    InterventionCondition,
    get_intervention_by_name,
    load_interventions,
)


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "interventions_sample.json"


def test_load_interventions_from_valid_fixture() -> None:
    conditions = load_interventions(FIXTURE_PATH)
    assert len(conditions) == 3
    names = [c.name for c in conditions]
    assert names == ["baseline", "condition_a", "condition_b"]
    assert all(isinstance(c, InterventionCondition) for c in conditions)
    assert all(c.system_prompt for c in conditions)
    assert all(c.token_count > 0 for c in conditions)


def test_load_interventions_raises_on_malformed_json(tmp_path: Path) -> None:
    bad = tmp_path / "bad.json"
    bad.write_text("{ this is not valid json", encoding="utf-8")
    with pytest.raises(json.JSONDecodeError):
        load_interventions(bad)


def test_get_intervention_by_name_returns_correct_condition() -> None:
    conditions = load_interventions(FIXTURE_PATH)
    condition = get_intervention_by_name(conditions, "condition_a")
    assert condition.name == "condition_a"
    assert "current state" in condition.system_prompt.lower()


def test_get_intervention_by_name_raises_on_unknown() -> None:
    conditions = load_interventions(FIXTURE_PATH)
    with pytest.raises(ValueError):
        get_intervention_by_name(conditions, "does_not_exist")
