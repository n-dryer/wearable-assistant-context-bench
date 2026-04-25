"""Render the one-page Wearable Assistant Context Benchmark v1.0.0 card to PDF.

Run:
    .venv/bin/python docs/benchmark_card.py

Output:
    docs/wearable_assistant_context_card.pdf
"""

from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)


TITLE = "Wearable Assistant Context Benchmark v1.0.0"
TAGLINE = "Cross-turn reference resolution under context change."
REPO_URL = "https://github.com/n-dryer/wearable-assistant-context-bench"
CITATION_LINE = (
    "Dryer, N. (2026). Wearable Assistant Context Benchmark v1.0.0. "
    "https://github.com/n-dryer/wearable-assistant-context-bench"
)

PRODUCT_CONTEXT = (
    "The product surface is a wearable live-assistant camera. A "
    "first-person camera worn by the user is paired with a "
    "conversational AI assistant that sees what the user sees and "
    "answers spoken questions in-flight. The camera moves with the "
    "user, so visual context can change mid-conversation, and a "
    "follow-up question often refers back to something the user "
    "said or held a moment earlier."
)

WHAT_IT_MEASURES = (
    "Each scenario is a two-turn conversation. Turn 1 establishes a "
    "reference state. Turn 2 shifts the context and asks an "
    "ambiguously-referenced follow-up. The candidate model has to "
    "resolve the reference correctly: current context, prior context, "
    "clarify (ambiguous), or abstain (info not available). "
    "Scoring is deterministic substring containment against "
    "expected_answers.json."
)

EXAMPLE_1 = (
    "<b>Object swap.</b> The user is at a workbench holding a "
    "Phillips-head screwdriver and asks how to grip it. A moment "
    "later they put it down, pick up a different tool, and ask "
    "\"am I holding it correctly?\" The correct anchor is the "
    "current tool (current frame)."
)

EXAMPLE_2 = (
    "<b>Room shift.</b> The user is in a bedroom asking about wall "
    "art. A moment later they move to the next room and ask "
    "\"what art should we hang in here?\" The correct anchor is "
    "the new room (current frame)."
)

PRIMARY_SCORE = (
    "<b>Primary score:</b> macro average of per-category Turn 2 "
    "accuracy across all four categories under the ranking condition "
    "<i>baseline</i>."
)

PRIMARY_FORMULA = (
    "main_score = mean(current_acc, prior_acc, clarify_acc, abstain_acc)"
)

INTERPRETIVE_ANCHORS = [
    "0.25 is the random-chance floor across four categories.",
    "Substring scoring does not handle paraphrase. A correct response "
    "that avoids answer-key tokens scores incorrect. Results are "
    "lower bounds on true accuracy.",
    "Condition sensitivity matters: a candidate that only clears "
    "the bar under condition_b (pre-answer scaffold) is not the "
    "same ship-readiness story as one that clears it under baseline.",
]

ONE_COMMAND = (
    "python -m benchmark.v1.run --model &lt;MODEL_ID&gt; "
    "--judge-model &lt;JUDGE_MODEL&gt;"
)

LIMITATIONS = [
    "Substring scoring; paraphrase is not handled. LLM-as-judge "
    "scoring planned for v1.1.",
    "23 of 24 prior scenarios can be answered by substring-matching "
    "Turn 1 text. Prior-recall depth is limited in v1.",
    "Spoken queries represented as text transcript proxies. "
    "Raw audio grounding not tested.",
]

SCENARIO_COUNTS = (
    "<b>101 frozen scenarios:</b> 50 current, 24 prior, "
    "15 clarify, 12 abstain."
)


def build_styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    styles: dict[str, ParagraphStyle] = {}

    styles["title"] = ParagraphStyle(
        "title",
        parent=base["Title"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        spaceAfter=2,
        textColor=colors.HexColor("#111111"),
    )
    styles["tagline"] = ParagraphStyle(
        "tagline",
        parent=base["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=11,
        leading=14,
        spaceAfter=10,
        textColor=colors.HexColor("#555555"),
    )
    styles["section"] = ParagraphStyle(
        "section",
        parent=base["Heading3"],
        fontName="Helvetica-Bold",
        fontSize=10.5,
        leading=13,
        spaceBefore=8,
        spaceAfter=3,
        textColor=colors.HexColor("#111111"),
    )
    styles["body"] = ParagraphStyle(
        "body",
        parent=base["BodyText"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=12.5,
        spaceAfter=4,
        textColor=colors.HexColor("#222222"),
    )
    styles["mono"] = ParagraphStyle(
        "mono",
        parent=base["Code"],
        fontName="Courier",
        fontSize=9,
        leading=12,
        leftIndent=8,
        spaceAfter=4,
        textColor=colors.HexColor("#222222"),
        backColor=colors.HexColor("#f4f4f4"),
    )
    styles["footer"] = ParagraphStyle(
        "footer",
        parent=base["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#666666"),
    )
    return styles


def build_story(styles: dict[str, ParagraphStyle]) -> list:
    story: list = []
    story.append(Paragraph(TITLE, styles["title"]))
    story.append(Paragraph(TAGLINE, styles["tagline"]))
    story.append(HRFlowable(
        width="100%",
        thickness=0.7,
        color=colors.HexColor("#cccccc"),
        spaceAfter=6,
    ))

    story.append(Paragraph("Product context", styles["section"]))
    story.append(Paragraph(PRODUCT_CONTEXT, styles["body"]))

    story.append(Paragraph("What it measures", styles["section"]))
    story.append(Paragraph(WHAT_IT_MEASURES, styles["body"]))
    story.append(Paragraph(SCENARIO_COUNTS, styles["body"]))

    story.append(Paragraph("Two illustrative examples", styles["section"]))
    story.append(Paragraph(EXAMPLE_1, styles["body"]))
    story.append(Paragraph(EXAMPLE_2, styles["body"]))

    story.append(Paragraph("Primary score", styles["section"]))
    story.append(Paragraph(PRIMARY_SCORE, styles["body"]))
    story.append(Paragraph(PRIMARY_FORMULA, styles["mono"]))

    story.append(Paragraph("How to read a score", styles["section"]))
    for anchor in INTERPRETIVE_ANCHORS:
        story.append(Paragraph("&bull; " + anchor, styles["body"]))

    story.append(Paragraph("One-command run", styles["section"]))
    story.append(Paragraph(ONE_COMMAND, styles["mono"]))

    story.append(Paragraph("Top three limitations", styles["section"]))
    for limitation in LIMITATIONS:
        story.append(Paragraph("&bull; " + limitation, styles["body"]))

    story.append(Spacer(1, 6))
    story.append(HRFlowable(
        width="100%",
        thickness=0.4,
        color=colors.HexColor("#cccccc"),
        spaceAfter=4,
    ))
    story.append(Paragraph(CITATION_LINE, styles["footer"]))
    story.append(Paragraph(REPO_URL, styles["footer"]))
    return story


def render(output_path: Path) -> Path:
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=LETTER,
        leftMargin=0.6 * inch,
        rightMargin=0.6 * inch,
        topMargin=0.6 * inch,
        bottomMargin=0.6 * inch,
        title="Wearable Assistant Context Benchmark v1.0.0 card",
        author="n-dryer",
        subject="Wearable Assistant Context Benchmark v1.0.0",
    )
    styles = build_styles()
    doc.build(build_story(styles))
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    out = repo_root / "docs" / "wearable_assistant_context_card.pdf"
    render(out)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
