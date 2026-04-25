"""Generate a designed PDF review sheet for the 50 scenarios.

Renders one scenario per page in a clean, scannable layout with
plain-English labels (no field names from the JSON schema). Uses the
same visual language as the benchmark card so the review document
feels like part of the same family.

Output:
    docs/review/scenarios_review.pdf
    docs/review/scenarios_review.html  (the printable HTML used to render)

Usage:
    python scripts/generate_review_pdf.py
"""

from __future__ import annotations

import json
import html
from collections import Counter
from pathlib import Path


SCENARIOS_PATH = Path("benchmark/v1/scenarios.json")
ANSWERS_PATH = Path("benchmark/v1/expected_answers.json")
OUT_HTML = Path("docs/review/scenarios_review.html")
OUT_PDF = Path("docs/review/scenarios_review.pdf")


# Color coding by target context — quick visual filter when scanning
TARGET_COLORS = {
    "current": ("#1f6f4a", "#dff0e7"),   # green
    "prior": ("#234a85", "#e0e8f3"),     # blue
    "clarify": ("#9e6b1c", "#f6e9cc"),   # amber
    "abstain": ("#5a5a5a", "#e6e6e6"),   # gray
}


# Plain-English translations for shift types (the `cue_type` field)
CUE_LABELS = {
    "object_in_hand": "Object swap (in hand)",
    "object_state": "Object state change",
    "sequential_task": "Sequential task step",
    "location": "Location change",
    "object_in_view": "Attention shift (same scene)",
    "absent_referent": "Absent referent",
    "screen_content": "Screen content change",
    "pre_conversation_recall": "Recall from before Turn 1",
}


def _scenario_id_key(scenario: dict) -> int:
    return int(scenario["scenario_id"].split("-")[1])


def _esc(text: str) -> str:
    return html.escape(text or "")


def render_html() -> str:
    scenarios = sorted(
        json.loads(SCENARIOS_PATH.read_text()), key=_scenario_id_key
    )
    answers = json.loads(ANSWERS_PATH.read_text())

    cue_counts = Counter(s["cue_type"] for s in scenarios)
    target_counts = Counter(s["target_context"] for s in scenarios)
    diff_counts = Counter(s["difficulty_tier"] for s in scenarios)

    # ------------------------------------------------------------------
    # CSS — print-friendly, A4 portrait, one scenario per page
    # ------------------------------------------------------------------
    css = """
    @page {
        size: Letter portrait;
        margin: 0.55in 0.55in 0.55in 0.55in;
    }

    * { box-sizing: border-box; }

    html, body {
        margin: 0;
        padding: 0;
        font-family: "Helvetica Neue", "Helvetica", "Arial", sans-serif;
        color: #2b2118;
        background: #fffaf4;
        font-size: 11pt;
        line-height: 1.45;
    }

    .cover {
        page-break-after: always;
        padding: 1.0in 0.4in 0.4in 0.4in;
    }

    .cover .kicker {
        font-size: 9pt;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.18em;
        color: #b14f31;
        background: #f4dfd5;
        display: inline-block;
        padding: 4pt 10pt;
        border-radius: 100pt;
    }

    .cover h1 {
        font-size: 32pt;
        line-height: 1.05;
        font-weight: 800;
        letter-spacing: -0.025em;
        margin: 14pt 0 6pt 0;
        color: #2b2118;
    }

    .cover .subtitle {
        font-size: 12pt;
        color: #5b4a3d;
        max-width: 5in;
        margin: 0 0 24pt 0;
    }

    .cover .summary {
        background: #f0e8dd;
        border-radius: 14pt;
        padding: 18pt 22pt;
        margin-bottom: 18pt;
    }

    .cover .summary h2 {
        font-size: 9pt;
        text-transform: uppercase;
        letter-spacing: 0.16em;
        color: #b14f31;
        margin: 0 0 10pt 0;
    }

    .cover .summary table {
        border-collapse: collapse;
        font-size: 10.5pt;
    }

    .cover .summary td {
        padding: 3pt 16pt 3pt 0;
        vertical-align: top;
    }

    .cover .summary td.label {
        color: #6b5a4d;
        white-space: nowrap;
    }

    .cover .summary td.value {
        font-weight: 600;
    }

    .cover .checklist {
        font-size: 10.5pt;
    }

    .cover .checklist h2 {
        font-size: 9pt;
        text-transform: uppercase;
        letter-spacing: 0.16em;
        color: #b14f31;
        margin: 0 0 10pt 0;
    }

    .cover .checklist ol {
        padding-left: 18pt;
        margin: 0;
    }

    .cover .checklist li {
        margin-bottom: 7pt;
    }

    /* Scenario page layout */
    .scenario {
        page-break-after: always;
        padding: 0;
    }

    .scenario:last-child {
        page-break-after: auto;
    }

    .scenario-header {
        border-bottom: 1.5pt solid #2b2118;
        padding-bottom: 10pt;
        margin-bottom: 14pt;
    }

    .scenario-id {
        font-size: 28pt;
        font-weight: 800;
        letter-spacing: -0.02em;
        color: #2b2118;
        margin: 0;
        line-height: 1;
    }

    .scenario-cue {
        font-size: 12pt;
        color: #5b4a3d;
        margin: 4pt 0 0 0;
    }

    .badges {
        margin-top: 10pt;
        display: block;
    }

    .badge {
        display: inline-block;
        font-size: 8.5pt;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        padding: 3pt 9pt;
        border-radius: 100pt;
        margin-right: 6pt;
        margin-bottom: 4pt;
    }

    .badge.target { /* color injected inline */ }
    .badge.difficulty { background: #efe6d9; color: #5b4a3d; }
    .badge.domain { background: #e8e1f0; color: #463760; }

    .pre-conversation {
        background: #fff4ea;
        border-left: 3pt solid #b14f31;
        padding: 10pt 14pt;
        margin-bottom: 14pt;
        border-radius: 0 8pt 8pt 0;
    }

    .pre-conversation .turn-label {
        font-size: 8.5pt;
        text-transform: uppercase;
        letter-spacing: 0.14em;
        color: #b14f31;
        font-weight: 700;
        margin-bottom: 5pt;
    }

    .pre-conversation .camera-text {
        font-size: 10.5pt;
        line-height: 1.5;
        color: #2b2118;
    }

    .turn-block {
        margin-bottom: 14pt;
    }

    .turn-block .turn-label {
        font-size: 8.5pt;
        text-transform: uppercase;
        letter-spacing: 0.14em;
        color: #6b5a4d;
        font-weight: 700;
        margin-bottom: 6pt;
    }

    .turn-block .turn-label .turn-num {
        color: #b14f31;
        margin-right: 5pt;
    }

    .channel-row {
        display: table;
        width: 100%;
        margin-bottom: 6pt;
    }

    .channel {
        background: #f0e8dd;
        border-radius: 8pt;
        padding: 9pt 13pt;
        margin-bottom: 6pt;
    }

    .channel .channel-label {
        font-size: 8pt;
        text-transform: uppercase;
        letter-spacing: 0.14em;
        color: #6b5a4d;
        font-weight: 700;
        margin-bottom: 4pt;
    }

    .channel.camera {
        background: #f0e8dd;
    }

    .channel.camera .channel-text {
        font-size: 10.5pt;
        line-height: 1.5;
        color: #2b2118;
    }

    .channel.speech {
        background: #fbf3e8;
    }

    .channel.speech .channel-text {
        font-size: 12pt;
        font-style: italic;
        line-height: 1.45;
        color: #1f1812;
        font-weight: 500;
    }

    .channel.speech .channel-text::before { content: "\\201C"; color: #b14f31; font-weight: 700; }
    .channel.speech .channel-text::after { content: "\\201D"; color: #b14f31; font-weight: 700; }

    .repair-line {
        background: #f4dfd5;
        border-radius: 8pt;
        padding: 8pt 13pt;
        margin-bottom: 14pt;
        font-size: 10pt;
    }

    .repair-line .repair-label {
        font-size: 8pt;
        text-transform: uppercase;
        letter-spacing: 0.14em;
        color: #b14f31;
        font-weight: 700;
        margin-bottom: 3pt;
    }

    .repair-line .repair-text {
        font-style: italic;
        color: #2b2118;
    }

    .judge-vocab {
        font-size: 9pt;
        color: #6b5a4d;
        background: #faf5ee;
        border-radius: 6pt;
        padding: 8pt 11pt;
        margin-bottom: 14pt;
        line-height: 1.55;
    }

    .judge-vocab .vocab-label {
        font-size: 8pt;
        text-transform: uppercase;
        letter-spacing: 0.13em;
        font-weight: 700;
        color: #b14f31;
        display: block;
        margin-bottom: 3pt;
    }

    .judge-vocab .vocab-row {
        margin-bottom: 4pt;
    }

    .judge-vocab .vocab-row strong {
        color: #2b2118;
    }

    .review-area {
        border-top: 1pt solid #2b2118;
        padding-top: 12pt;
        margin-top: 16pt;
    }

    .review-area .review-label {
        font-size: 8.5pt;
        text-transform: uppercase;
        letter-spacing: 0.14em;
        color: #b14f31;
        font-weight: 700;
        margin-bottom: 8pt;
    }

    .checkboxes {
        font-size: 11pt;
        margin-bottom: 12pt;
    }

    .checkboxes .check {
        display: inline-block;
        margin-right: 18pt;
    }

    .checkboxes .box {
        display: inline-block;
        width: 14pt;
        height: 14pt;
        border: 1.5pt solid #2b2118;
        border-radius: 3pt;
        vertical-align: middle;
        margin-right: 6pt;
    }

    .notes-area {
        font-size: 9.5pt;
        color: #6b5a4d;
    }

    .notes-area .notes-label {
        font-size: 8pt;
        text-transform: uppercase;
        letter-spacing: 0.14em;
        color: #6b5a4d;
        font-weight: 700;
        margin-bottom: 5pt;
    }

    .notes-line {
        border-bottom: 0.5pt solid #c9bdb0;
        height: 14pt;
        margin-bottom: 4pt;
    }

    .footer {
        position: running(footer);
    }

    @page {
        @bottom-center {
            content: counter(page) " of " counter(pages);
            font-size: 8pt;
            color: #9c8c7d;
            font-family: "Helvetica Neue", "Arial", sans-serif;
        }
    }
    """

    parts: list[str] = [
        "<!doctype html>",
        '<html><head><meta charset="utf-8">',
        "<title>Scenario Review Sheet</title>",
        f"<style>{css}</style>",
        "</head><body>",
    ]

    # ------------------------------------------------------------------
    # Cover page — overview, summary, checklist
    # ------------------------------------------------------------------
    parts.append('<section class="cover">')
    parts.append('<div class="kicker">Wearable Assistant Context Benchmark v1</div>')
    parts.append("<h1>Scenario Review Sheet</h1>")
    parts.append(
        '<p class="subtitle">'
        f"50 scenarios. One per page. Read all four channels (camera + "
        f"user speech, Turn 1 and Turn 2), then mark <strong>Pass</strong>, "
        f"<strong>Edit</strong>, or <strong>Replace</strong>. Add notes "
        f"if needed."
        "</p>"
    )

    # Summary block
    parts.append('<div class="summary">')
    parts.append("<h2>What's in this bank</h2>")
    parts.append("<table>")

    target_summary = ", ".join(
        f"{k} ({v})" for k, v in sorted(target_counts.items())
    )
    parts.append(
        f'<tr><td class="label">Total scenarios</td>'
        f'<td class="value">{len(scenarios)}</td></tr>'
    )
    parts.append(
        f'<tr><td class="label">Correct frame to use</td>'
        f'<td class="value">{_esc(target_summary)}</td></tr>'
    )
    diff_summary = ", ".join(
        f"{k} ({v})" for k, v in sorted(diff_counts.items())
    )
    parts.append(
        f'<tr><td class="label">Difficulty mix</td>'
        f'<td class="value">{_esc(diff_summary)}</td></tr>'
    )
    cue_summary = "; ".join(
        f"{CUE_LABELS[k]} ({cue_counts.get(k, 0)})"
        for k in CUE_LABELS.keys()
    )
    parts.append(
        f'<tr><td class="label">Shift types</td>'
        f'<td class="value">{_esc(cue_summary)}</td></tr>'
    )
    parts.append("</table>")
    parts.append("</div>")

    # Checklist block
    parts.append('<div class="checklist">')
    parts.append("<h2>Before you mark Pass, confirm</h2>")
    parts.append("<ol>")
    parts.append(
        "<li><strong>Camera identifies the object.</strong> Read the Turn 1 "
        "and Turn 2 camera descriptions cold — without seeing the answer "
        "vocabulary. You should be able to identify what's in frame from "
        "the description alone. If you can't, the description is too vague."
        "</li>"
    )
    parts.append(
        "<li><strong>The user speech sounds natural.</strong> Would a real "
        "person actually say that out loud to a wearable? No narration of "
        "what's visible. No announcement that something changed."
        "</li>"
    )
    parts.append(
        "<li><strong>The shift is hidden in the camera.</strong> Turn 2 "
        "user speech does not give away that the context changed. The "
        "model has to notice the difference by integrating the camera "
        "and the question."
        "</li>"
    )
    parts.append(
        "<li><strong>The shift fits the type.</strong> The shift type at "
        "the top of the page tells you what kind of shift this is "
        "supposed to be. Make sure the scenario actually does that."
        "</li>"
    )
    parts.append(
        "<li><strong>Answer vocabulary is reasonable.</strong> The "
        "judge-only vocabulary at the bottom should cover the right things "
        "for both contexts (object name, technique, state). You don't need "
        "to memorize it — just sanity-check it makes sense."
        "</li>"
    )
    parts.append(
        "<li><strong>Repair line is fair.</strong> If the model misses "
        "Turn 2, the repair line names the intended frame explicitly. "
        "Read it and confirm it gives a model a fair second shot."
        "</li>"
    )
    parts.append("</ol>")
    parts.append("</div>")

    parts.append("</section>")

    # ------------------------------------------------------------------
    # Per-scenario pages
    # ------------------------------------------------------------------
    for sc in scenarios:
        sid = sc["scenario_id"]
        ea = answers.get(sid, {})
        target = sc["target_context"]
        target_color, target_bg = TARGET_COLORS[target]

        parts.append('<section class="scenario">')

        # Header
        parts.append('<div class="scenario-header">')
        parts.append(
            f'<h2 class="scenario-id">'
            f'{sid.upper().replace("SC-", "Scenario ")}'
            f'</h2>'
        )
        parts.append(
            f'<p class="scenario-cue">{_esc(CUE_LABELS[sc["cue_type"]])}</p>'
        )
        parts.append('<div class="badges">')
        parts.append(
            f'<span class="badge target" '
            f'style="background:{target_bg};color:{target_color};">'
            f'Correct frame: {_esc(target)}</span>'
        )
        parts.append(
            f'<span class="badge difficulty">'
            f'{_esc(sc["difficulty_tier"].title())}'
            f'</span>'
        )
        parts.append(
            f'<span class="badge domain">'
            f'{_esc(sc["activity_domain"].replace("_", " ").title())}'
            f'</span>'
        )
        parts.append("</div>")
        parts.append("</div>")

        # Pre-conversation context if present
        if sc.get("context_image"):
            parts.append('<div class="pre-conversation">')
            parts.append(
                '<div class="turn-label">Before the conversation '
                "started — what the camera saw</div>"
            )
            parts.append(
                f'<div class="camera-text">{_esc(sc["context_image"])}</div>'
            )
            parts.append("</div>")

        # Turn 1
        parts.append('<div class="turn-block">')
        parts.append(
            '<div class="turn-label"><span class="turn-num">Turn 1</span>'
            "the user's first question</div>"
        )
        parts.append('<div class="channel camera">')
        parts.append('<div class="channel-label">What the camera sees</div>')
        parts.append(
            f'<div class="channel-text">{_esc(sc["turn_1_image"])}</div>'
        )
        parts.append("</div>")
        parts.append('<div class="channel speech">')
        parts.append('<div class="channel-label">What the user says</div>')
        parts.append(
            f'<div class="channel-text">{_esc(sc["turn_1_user"])}</div>'
        )
        parts.append("</div>")
        parts.append("</div>")

        # Turn 2
        parts.append('<div class="turn-block">')
        parts.append(
            '<div class="turn-label"><span class="turn-num">Turn 2</span>'
            "the follow-up after context shifts</div>"
        )
        parts.append('<div class="channel camera">')
        parts.append(
            '<div class="channel-label">What the camera sees now</div>'
        )
        parts.append(
            f'<div class="channel-text">{_esc(sc["turn_2_image"])}</div>'
        )
        parts.append("</div>")
        parts.append('<div class="channel speech">')
        parts.append(
            '<div class="channel-label">What the user says</div>'
        )
        parts.append(
            f'<div class="channel-text">{_esc(sc["turn_2_user"])}</div>'
        )
        parts.append("</div>")
        parts.append("</div>")

        # Repair line
        parts.append('<div class="repair-line">')
        parts.append(
            '<div class="repair-label">Repair line — fired only if model '
            "misses Turn 2</div>"
        )
        parts.append(
            f'<div class="repair-text">'
            f'“{_esc(sc["turn_3_repair_anchor"])}”'
            f'</div>'
        )
        parts.append("</div>")

        # Judge vocabulary
        parts.append('<div class="judge-vocab">')
        parts.append(
            '<span class="vocab-label">Judge vocabulary '
            "(model never sees this)</span>"
        )

        if ea.get("current_answers"):
            parts.append(
                f'<div class="vocab-row"><strong>'
                f"Vocabulary that signals current frame:</strong> "
                f"{_esc(', '.join(ea['current_answers']))}"
                f"</div>"
            )
        if ea.get("prior_answers"):
            parts.append(
                f'<div class="vocab-row"><strong>'
                f"Vocabulary that signals prior frame:</strong> "
                f"{_esc(', '.join(ea['prior_answers']))}"
                f"</div>"
            )
        if ea.get("clarify_indicators"):
            parts.append(
                f'<div class="vocab-row"><strong>'
                f"Vocabulary that signals a clarifying question:</strong> "
                f"{_esc(', '.join(ea['clarify_indicators']))}"
                f"</div>"
            )
        if ea.get("abstain_indicators"):
            parts.append(
                f'<div class="vocab-row"><strong>'
                f"Vocabulary that signals refusal/abstain:</strong> "
                f"{_esc(', '.join(ea['abstain_indicators']))}"
                f"</div>"
            )
        parts.append("</div>")

        # Review area — checkboxes + notes lines
        parts.append('<div class="review-area">')
        parts.append('<div class="review-label">Your call</div>')
        parts.append('<div class="checkboxes">')
        parts.append(
            '<span class="check"><span class="box"></span>'
            "<strong>Pass</strong></span>"
        )
        parts.append(
            '<span class="check"><span class="box"></span>'
            "<strong>Edit</strong></span>"
        )
        parts.append(
            '<span class="check"><span class="box"></span>'
            "<strong>Replace</strong></span>"
        )
        parts.append("</div>")
        parts.append('<div class="notes-area">')
        parts.append('<div class="notes-label">Notes</div>')
        # Provide writing lines
        for _ in range(4):
            parts.append('<div class="notes-line"></div>')
        parts.append("</div>")
        parts.append("</div>")
        parts.append("</section>")

    parts.append("</body></html>")
    return "\n".join(parts)


def main() -> None:
    OUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    html_text = render_html()
    OUT_HTML.write_text(html_text, encoding="utf-8")
    print(f"Wrote {OUT_HTML} ({OUT_HTML.stat().st_size:,} bytes)")

    from weasyprint import HTML
    HTML(string=html_text, base_url=str(OUT_HTML.parent)).write_pdf(
        str(OUT_PDF)
    )
    print(f"Wrote {OUT_PDF} ({OUT_PDF.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
