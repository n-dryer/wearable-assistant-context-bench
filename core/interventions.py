"""Intervention condition loading.

Loads the three prompt conditions (baseline, direct instruction, pre-answer
scaffold) from an interventions.json file. The JSON file itself is populated
by the experiment builder in Prompt 2; this module only handles loading and
lookup.

Expected JSON schema:
    [
        {
            "name": str,
            "description": str,
            "system_prompt": str,
            "token_count": int
        },
        ...
    ]
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class InterventionCondition:
    """A single prompt condition applied to every scenario.

    Attributes:
        name: Short identifier (e.g. "baseline", "condition_a").
        description: One-line human-readable summary of the strategy.
        system_prompt: The full system prompt sent to the model under test.
        token_count: Approximate token count of the system prompt; used for
            reporting prompt overhead alongside pass-rate deltas.
    """

    name: str
    description: str
    system_prompt: str
    token_count: int


def load_interventions(path: Path) -> list[InterventionCondition]:
    """Load intervention conditions from a JSON file.

    Args:
        path: Path to a JSON file containing a list of condition objects.

    Returns:
        List of InterventionCondition in the order defined in the file.

    Raises:
        FileNotFoundError: If the path does not exist.
        json.JSONDecodeError: If the file is not valid JSON.
        KeyError: If a condition object is missing a required field.
        TypeError: If the top-level JSON is not a list.
    """
    with path.open("r", encoding="utf-8") as f:
        raw = json.load(f)

    if not isinstance(raw, list):
        raise TypeError(
            f"Expected top-level JSON list of conditions, got {type(raw).__name__}"
        )

    conditions: list[InterventionCondition] = []
    for entry in raw:
        conditions.append(
            InterventionCondition(
                name=entry["name"],
                description=entry["description"],
                system_prompt=entry["system_prompt"],
                token_count=int(entry["token_count"]),
            )
        )
    return conditions


def get_intervention_by_name(
    conditions: list[InterventionCondition], name: str
) -> InterventionCondition:
    """Return the condition with the given name.

    Args:
        conditions: List of loaded intervention conditions.
        name: Name to look up.

    Returns:
        The matching InterventionCondition.

    Raises:
        ValueError: If no condition with that name exists. The error message
            includes the list of known names to aid debugging typos in
            experiment runners.
    """
    for condition in conditions:
        if condition.name == name:
            return condition
    known = ", ".join(c.name for c in conditions) or "(none loaded)"
    raise ValueError(f"Unknown intervention name {name!r}. Known: {known}")
