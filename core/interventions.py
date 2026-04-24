"""Prompt condition loading for benchmark v1.

The benchmark stores its three prompt conditions in
``benchmark/v1/interventions.json`` for compatibility with the frozen
v1 file layout. This module provides the preferred prompt-condition
API while retaining intervention-based aliases for older callers.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class PromptCondition:
    """A single prompt condition applied to every scenario.

    Attributes:
        name: Short identifier such as ``baseline`` or ``condition_a``.
        description: One-line summary of the prompt strategy.
        system_prompt: Full system prompt sent to the candidate model.
        token_count: Approximate prompt length used for prompt-overhead reporting.
    """

    name: str
    description: str
    system_prompt: str
    token_count: int


# Backwards-compatible alias for older imports.
InterventionCondition = PromptCondition


def load_prompt_conditions(path: Path) -> list[PromptCondition]:
    """Load prompt conditions from a JSON file."""
    with path.open("r", encoding="utf-8") as f:
        raw = json.load(f)

    if not isinstance(raw, list):
        raise TypeError(
            f"Expected top-level JSON list of conditions, got {type(raw).__name__}"
        )

    conditions: list[PromptCondition] = []
    for entry in raw:
        conditions.append(
            PromptCondition(
                name=entry["name"],
                description=entry["description"],
                system_prompt=entry["system_prompt"],
                token_count=int(entry["token_count"]),
            )
        )
    return conditions


def load_interventions(path: Path) -> list[InterventionCondition]:
    """Compatibility wrapper around :func:`load_prompt_conditions`."""
    return load_prompt_conditions(path)


def get_prompt_condition_by_name(
    conditions: list[PromptCondition], name: str
) -> PromptCondition:
    """Return the prompt condition with the given name."""
    for condition in conditions:
        if condition.name == name:
            return condition
    known = ", ".join(c.name for c in conditions) or "(none loaded)"
    raise ValueError(f"Unknown prompt condition name {name!r}. Known: {known}")


def get_intervention_by_name(
    conditions: list[InterventionCondition], name: str
) -> InterventionCondition:
    """Compatibility wrapper around :func:`get_prompt_condition_by_name`."""
    return get_prompt_condition_by_name(conditions, name)
