"""Generate a human-readable scenario review sheet.

Reads `benchmark/v1/scenarios.json` and `benchmark/v1/expected_answers.json`,
produces a Markdown file at `docs/review/scenarios_review.md` with one
section per scenario plus a bank summary, review checklist, and a
table of contents.

Use the generated file to validate scenarios manually. Re-run this
script after any edit to the scenario or answer files to refresh
the review sheet.

Usage:
    python scripts/generate_review_sheet.py
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path


SCENARIOS_PATH = Path("benchmark/v1/scenarios.json")
ANSWERS_PATH = Path("benchmark/v1/expected_answers.json")
OUT_PATH = Path("docs/review/scenarios_review.md")

CUE_TYPE_ORDER = (
    "object_in_hand",
    "object_state",
    "sequential_task",
    "location",
    "object_in_view",
    "absent_referent",
    "screen_content",
    "pre_conversation_recall",
)


def _scenario_id_key(scenario: dict) -> int:
    return int(scenario["scenario_id"].split("-")[1])


def render() -> str:
    scenarios = sorted(
        json.loads(SCENARIOS_PATH.read_text()), key=_scenario_id_key
    )
    answers = json.loads(ANSWERS_PATH.read_text())

    cue_counts = Counter(s["cue_type"] for s in scenarios)
    target_counts = Counter(s["target_context"] for s in scenarios)
    diff_counts = Counter(s["difficulty_tier"] for s in scenarios)
    domain_counts = Counter(s["activity_domain"] for s in scenarios)

    lines: list[str] = []

    # Header
    lines.append(
        "# Scenario Review Sheet: Wearable Assistant Context Benchmark v1"
    )
    lines.append("")
    lines.append(
        "Use this file to validate each of the 50 scenarios. For each one,"
    )
    lines.append(
        "read all four channels (audio + camera × Turn 1 + Turn 2), then mark the"
    )
    lines.append("status box and add notes if anything needs to change.")
    lines.append("")
    lines.append(
        "**Source-of-truth files:** `benchmark/v1/scenarios.json` and"
    )
    lines.append("`benchmark/v1/expected_answers.json`.")
    lines.append("")
    lines.append(
        "**Re-generate this file after edits:** `python scripts/generate_review_sheet.py`"
    )
    lines.append("")
    lines.append("---")
    lines.append("")

    # Bank summary
    lines.append("## Bank summary")
    lines.append("")
    lines.append(f"- **Scenarios:** {len(scenarios)}")
    lines.append(
        "- **Target context:** "
        + ", ".join(f"{k} ({v})" for k, v in sorted(target_counts.items()))
    )
    lines.append(
        "- **Difficulty:** "
        + ", ".join(f"{k} ({v})" for k, v in sorted(diff_counts.items()))
    )
    lines.append("- **Shift types (`cue_type`):**")
    for c in CUE_TYPE_ORDER:
        lines.append(f"  - `{c}`: {cue_counts.get(c, 0)}")
    domains_sorted = sorted(
        domain_counts.items(), key=lambda x: (-x[1], x[0])
    )
    lines.append(
        f"- **Activity domains ({len(domain_counts)} distinct):** "
        + ", ".join(f"{k} ({v})" for k, v in domains_sorted)
    )
    lines.append("")
    lines.append("---")
    lines.append("")

    # Review checklist
    lines.append("## Review checklist (per scenario)")
    lines.append("")
    lines.append("Before marking PASS, confirm:")
    lines.append("")
    lines.append(
        "1. **Image identifiability.** A fresh reader can identify the "
        "object from the Turn 1 image and Turn 2 image alone, no scenario "
        "context, no answer key. If not, the description is "
        "underspecified."
    )
    lines.append(
        "2. **Speech naturalness.** Turn 1 and Turn 2 user speech sound like a "
        "real person talking to a wearable. No narration of visible "
        "objects, no announcement of the shift."
    )
    lines.append(
        "3. **Hidden shift.** The context shift is visible only in the "
        "camera channel. Turn 2 user speech does not give it away."
    )
    lines.append(
        "4. **Category fit.** The scenario actually tests what its "
        "shift type (stored as `cue_type` in the data files) claims."
    )
    lines.append(
        "5. **Answer fairness.** `current_answers` and `prior_answers` "
        "cover the three vocabulary categories (object name, "
        "technique/action, state/condition). They are reasonable evidence "
        "of which context the model used."
    )
    lines.append(
        "6. **Repair anchor.** The Turn 3 repair anchor names the intended "
        "frame explicitly, so a model that missed Turn 2 has a fair shot."
    )
    lines.append("")
    lines.append(
        "Mark each scenario as **PASS**, **EDIT** (small fix needed; "
        "describe in notes), or **REPLACE** (scenario doesn't work; new "
        "one needed in same category)."
    )
    lines.append("")
    lines.append("---")
    lines.append("")

    # Table of contents
    lines.append("## Table of contents")
    lines.append("")
    for sc in scenarios:
        sid = sc["scenario_id"]
        lines.append(
            f"- [{sid}](#{sid}): `{sc['cue_type']}` / "
            f"`{sc['target_context']}` / {sc['activity_domain']} / "
            f"{sc['difficulty_tier']}"
        )
    lines.append("")
    lines.append("---")
    lines.append("")

    # Per-scenario blocks
    for sc in scenarios:
        sid = sc["scenario_id"]
        ea = answers.get(sid, {})

        lines.append(f"### {sid}")
        lines.append("")
        lines.append("| | |")
        lines.append("|---|---|")
        lines.append(f"| **Shift type** | `{sc['cue_type']}` |")
        lines.append(f"| **Target context** | `{sc['target_context']}` |")
        lines.append(f"| **Activity domain** | {sc['activity_domain']} |")
        lines.append(f"| **Difficulty** | {sc['difficulty_tier']} |")
        lines.append(f"| **Cognitive load** | {sc['cognitive_load']} |")
        if sc.get("time_gap_bucket"):
            lines.append(f"| **Time gap** | {sc['time_gap_bucket']} |")
        lines.append("")

        if sc.get("context_image"):
            lines.append(
                "**Pre-conversation camera state (`context_image`):**"
            )
            lines.append("")
            lines.append(f"> {sc['context_image']}")
            lines.append("")

        lines.append("**Turn 1, camera (`turn_1_image`):**")
        lines.append("")
        lines.append(f"> {sc['turn_1_image']}")
        lines.append("")
        lines.append(
            f'**Turn 1, user speech (`turn_1_user`):** *"{sc["turn_1_user"]}"*'
        )
        lines.append("")

        lines.append("**Turn 2, camera (`turn_2_image`):**")
        lines.append("")
        lines.append(f"> {sc['turn_2_image']}")
        lines.append("")
        lines.append(
            f'**Turn 2, user speech (`turn_2_user`):** *"{sc["turn_2_user"]}"*'
        )
        lines.append("")
        lines.append(
            f'**Turn 3, repair anchor (`turn_3_repair_anchor`):** '
            f'*"{sc["turn_3_repair_anchor"]}"*'
        )
        lines.append("")

        if sc.get("notes"):
            lines.append(f"**Authoring notes:** {sc['notes']}")
            lines.append("")

        lines.append("**Expected answers (judge-only):**")
        lines.append("")
        if ea.get("current_answers"):
            lines.append(
                "- `current_answers`: "
                + ", ".join(f"`{a}`" for a in ea["current_answers"])
            )
        if ea.get("prior_answers"):
            lines.append(
                "- `prior_answers`: "
                + ", ".join(f"`{a}`" for a in ea["prior_answers"])
            )
        if ea.get("clarify_indicators"):
            lines.append(
                "- `clarify_indicators`: "
                + ", ".join(f"`{a}`" for a in ea["clarify_indicators"])
            )
        if ea.get("abstain_indicators"):
            lines.append(
                "- `abstain_indicators`: "
                + ", ".join(f"`{a}`" for a in ea["abstain_indicators"])
            )
        lines.append("")

        lines.append("**Review:**")
        lines.append("")
        lines.append("- [ ] PASS")
        lines.append("- [ ] EDIT")
        lines.append("- [ ] REPLACE")
        lines.append("")
        lines.append("**Notes:**")
        lines.append("")
        lines.append("> _(write any review notes here)_")
        lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines)


def main() -> None:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(render(), encoding="utf-8")
    size = OUT_PATH.stat().st_size
    print(f"Wrote {OUT_PATH} ({size:,} bytes)")


if __name__ == "__main__":
    main()
