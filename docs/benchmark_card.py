"""Render the Wearable Assistant Context Benchmark v1 card.

The card content is defined in a single Python data structure below.
This script rebuilds ``docs/benchmark_card.html`` from that data and
then renders ``docs/wearable_assistant_context_card.pdf`` from the HTML
using WeasyPrint, so the HTML and PDF stay in sync.

Run:
    .venv/bin/python docs/benchmark_card.py

Outputs:
    docs/benchmark_card.html
    docs/wearable_assistant_context_card.pdf
"""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent


# ---------------------------------------------------------------------------
# Card content
# ---------------------------------------------------------------------------

KICKER = "v1 &middot; scenario bank"

TITLE = "Wearable Assistant Context Benchmark"

SUBTITLE = (
    "A model-selection benchmark for whether a multimodal assistant "
    "updates to <strong>current context</strong> instead of staying "
    "anchored to <strong>prior context</strong> after the user's "
    "situation changes between turns."
)

HERO_BADGES = [
    "50 scenarios",
    "8 shift-type categories",
    "3 prompt conditions",
    "balanced Turn 2 accuracy",
]

PRODUCT_PROBLEM_PARAGRAPHS = [
    (
        "Users should not have to keep restating what they are looking "
        "at, holding, or referring to after they move, switch objects, "
        "or otherwise change context."
    ),
    "Examples:",
]

PRODUCT_PROBLEM_BULLETS = [
    (
        "Bedroom to kitchen. The user asks about a wall, walks into "
        "the kitchen, and asks about it again. The assistant should "
        "answer about the kitchen wall, not the bedroom wall."
    ),
    (
        "Hammer to screwdriver. The user asks about a hammer, swaps "
        "to a screwdriver, then asks \"how do I use this?\" The "
        "assistant should answer about the screwdriver."
    ),
]

WHAT_MEASURED_PARAGRAPH = (
    "This benchmark measures context tracking. Each scenario is a "
    "three-turn conversation with a deliberate context shift between "
    "Turn 1 and Turn 2. The shift is visible only in the camera "
    "channel; the user does not announce it."
)

PRIMARY_SCORE_METRIC = {
    "title": "Primary score",
    "body": (
        "Balanced Turn 2 accuracy across the <code>current</code> and "
        "<code>prior</code> classes under the <code>baseline</code> "
        "prompt condition."
    ),
}

AUXILIARY_METRIC = {
    "title": "Auxiliary signal",
    "body": (
        "<code>clarify</code> and <code>abstain</code> per-class "
        "accuracy, plus a repair rate after Turn 2 misses."
    ),
}

THREE_CHANNEL_INTRO = (
    "Every scenario uses three channels with different audiences:"
)

THREE_CHANNEL_BULLETS = [
    (
        "<strong>Audio.</strong> User speech "
        "(<code>turn_1_user</code>, <code>turn_2_user</code>). Natural "
        "and deictic; never names the object or announces the shift. "
        "Visible to candidate and judge."
    ),
    (
        "<strong>Camera.</strong> Scene descriptions "
        "(<code>turn_1_image</code>, <code>turn_2_image</code>) "
        "injected as <code>[Camera: &hellip;]</code> blocks on the "
        "user side. Shape, material, motion, position; no object "
        "names. The camera channel uses scene descriptions in text as "
        "a proxy for real video frames. Visible to candidate and "
        "judge."
    ),
    (
        "<strong>Ground truth.</strong> Answer keys naming the "
        "actual objects in Turn 1 and Turn 2. Visible to the judge only."
    ),
]

CUE_TYPE_COUNTS = [
    ("12", "object in hand"),
    ("8", "object state"),
    ("6", "sequential task"),
    ("6", "location"),
    ("5", "object in view"),
    ("5", "absent referent"),
    ("4", "screen content"),
    ("4", "pre-conversation recall"),
]

SCENARIO_BANK_INTRO = (
    "50 scenarios across 8 shift-type categories. The shape of the "
    "shift is what the categories describe."
)

SCENARIO_BANK_FOOTER = (
    "Target context distribution: <strong>33 current</strong>, "
    "<strong>12 prior</strong>, <strong>3 clarify</strong>, "
    "<strong>2 abstain</strong>. Difficulty: 15 easy, 20 medium, "
    "15 hard. Coverage spans 16 activity domains."
)

HOW_TO_READ_BULLETS = [
    (
        "Score deltas between models on the same release matter more "
        "than absolute values."
    ),
    (
        "Strong on <code>current</code>, weak on <code>prior</code> "
        "means the model defaults to the latest frame and ignores "
        "user references to earlier state. The headline number is "
        "balanced for that reason."
    ),
    (
        "<code>condition_a</code> and <code>condition_b</code> are "
        "prompt-sensitivity diagnostics, not replacement scores. A "
        "model that only clears the bar with the pre-answer scaffold "
        "is not the same ship-readiness story as one that clears it "
        "under <code>baseline</code>."
    ),
    (
        "The repair rate stands in for user-correction cost after a "
        "miss; it is not part of the primary number."
    ),
]

NOT_MEASURED_BULLETS = [
    (
        "<strong>Advice quality.</strong> The judge does not check "
        "whether the response is correct, safe, or domain-appropriate. "
        "A confidently wrong answer can pass if it picks the right "
        "context."
    ),
    (
        "<strong>Multi-turn dynamics.</strong> The conversation is 3 "
        "turns. Long conversations and branching dialogue are out of "
        "scope."
    ),
    (
        "<strong>Real video.</strong> The camera channel uses scene "
        "descriptions in text as a proxy. Performance here is not a "
        "guarantee of performance on actual video frames."
    ),
    (
        "<strong>Proactive coaching.</strong> Only direct-question "
        "responses are scored."
    ),
    (
        "<strong>Domain knowledge depth.</strong> Coverage is broad "
        "across 16 domains but shallow in any one."
    ),
]

REPO_LINKS = [
    ("../README.md", "README.md", "product framing and quickstart"),
    ("benchmark_spec.md", "benchmark_spec.md", "the benchmark contract"),
    (
        "benchmark_notes.md",
        "benchmark_notes.md",
        "score interpretation and limitations",
    ),
    ("schema.md", "schema.md", "scenario field reference"),
    (
        "scenario_authoring_rules.md",
        "scenario_authoring_rules.md",
        "authoring rules and validation checklist",
    ),
    (
        "../benchmark/v1/dataset_card.md",
        "dataset_card.md",
        "bank statistics",
    ),
]

RESULTS_METRIC = {
    "title": "v1 results: 4 runs published",
    "body": (
        "Cross-family judging baselines and a camera channel ablation. "
        "Run A: <code>gemini-2.5-flash-lite</code> candidate + "
        "<code>gpt-4o-mini</code> judge: <strong>92.8%</strong>. "
        "Run B: <code>gpt-4o-mini</code> candidate + "
        "<code>gemini-2.5-flash-lite</code> judge: <strong>100.0%</strong>. "
        "Run C: same as Run A but with <code>--no-camera</code>: "
        "<strong>7.2%</strong>. The 85.6 percentage point gap between "
        "Run A and Run C is the camera channel's contribution. Full "
        "results table at "
        "<a href=\"https://n-dryer.github.io/wearable-assistant-context-bench/\">"
        "n-dryer.github.io/wearable-assistant-context-bench</a>."
    ),
}

FOOTER_PARAGRAPH = (
    "This benchmark supports a practical model-selection decision "
    "for a live wearable assistant. It is not a general multimodal "
    "benchmark. A model that fails it is unlikely to be viable as a "
    "wearable assistant; a model that passes still needs separate "
    "evaluation for advice quality, real video, latency, and "
    "everything else outside the context-tracking question."
)


# ---------------------------------------------------------------------------
# Rendering helpers
# ---------------------------------------------------------------------------

CSS = dedent(
    """\
    :root {
      --bg: #f6f1ea;
      --paper: #fffaf4;
      --ink: #191613;
      --muted: #5c564e;
      --line: #ddd0bf;
      --accent: #b14f31;
      --accent-soft: #f4dfd5;
      --soft: #f0e8dd;
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      background:
        radial-gradient(circle at top left, #fff6ee 0, transparent 35%),
        linear-gradient(180deg, #efe7db 0%, var(--bg) 100%);
      color: var(--ink);
      font-family: "Helvetica Neue", Arial, sans-serif;
    }

    .page {
      max-width: 1100px;
      margin: 28px auto;
      padding: 20px;
    }

    .card {
      background: var(--paper);
      border: 1px solid var(--line);
      border-radius: 28px;
      box-shadow: 0 24px 80px rgba(41, 26, 10, 0.10);
      overflow: hidden;
    }

    .hero {
      padding: 34px 36px 28px;
      border-bottom: 1px solid var(--line);
      background:
        linear-gradient(135deg, rgba(177, 79, 49, 0.10), transparent 52%),
        linear-gradient(180deg, rgba(255,255,255,0.92), rgba(255,250,244,0.96));
    }

    .kicker {
      display: inline-block;
      margin-bottom: 14px;
      padding: 7px 11px;
      border-radius: 999px;
      background: var(--accent-soft);
      color: var(--accent);
      font-size: 12px;
      font-weight: 700;
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }

    h1 {
      margin: 0 0 12px;
      max-width: 12ch;
      font-size: clamp(34px, 5vw, 58px);
      line-height: 0.95;
      letter-spacing: -0.04em;
      font-weight: 800;
    }

    .subtitle {
      margin: 0 0 22px;
      max-width: 62ch;
      font-size: 18px;
      line-height: 1.48;
      color: var(--muted);
    }

    .badges {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
    }

    .badge {
      padding: 8px 12px;
      border-radius: 999px;
      border: 1px solid var(--line);
      background: rgba(255,255,255,0.82);
      font-size: 13px;
      font-weight: 600;
    }

    .grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
    }

    .section {
      padding: 28px 36px 32px;
      border-top: 1px solid var(--line);
    }

    .section.left {
      border-right: 1px solid var(--line);
    }

    h2 {
      margin: 0 0 12px;
      font-size: 13px;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      color: var(--accent);
    }

    p {
      margin: 0 0 12px;
      font-size: 15px;
      line-height: 1.62;
      color: var(--muted);
    }

    ul {
      margin: 0;
      padding-left: 18px;
      color: var(--muted);
    }

    li {
      margin: 0 0 10px;
      line-height: 1.56;
    }

    .metric {
      margin-bottom: 16px;
      padding: 18px 20px;
      border: 1px solid var(--line);
      border-radius: 18px;
      background: var(--soft);
    }

    .metric strong {
      display: block;
      margin-bottom: 6px;
      color: var(--ink);
      font-size: 16px;
    }

    .stat-row {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 6px;
    }

    .stat {
      flex: 1 1 auto;
      min-width: 0;
      padding: 10px 12px;
      border: 1px solid var(--line);
      border-radius: 12px;
      background: rgba(255,255,255,0.7);
      font-size: 13px;
      color: var(--muted);
    }

    .stat strong {
      display: block;
      color: var(--ink);
      font-size: 18px;
      font-weight: 800;
      letter-spacing: -0.01em;
      margin-bottom: 2px;
    }

    code {
      padding: 2px 5px;
      border-radius: 6px;
      background: rgba(255,255,255,0.9);
      font-family: "SFMono-Regular", Menlo, Consolas, monospace;
      font-size: 13px;
    }

    a {
      color: var(--accent);
      text-decoration: none;
      border-bottom: 1px solid rgba(177, 79, 49, 0.3);
    }

    .footer {
      padding: 18px 36px 24px;
      border-top: 1px solid var(--line);
      background: rgba(255,255,255,0.68);
    }

    .footer p {
      margin: 0;
      font-size: 13px;
    }

    @media (max-width: 860px) {
      .page { margin: 0; padding: 12px; }
      .grid { grid-template-columns: 1fr; }
      .section.left { border-right: none; }
      .hero, .section, .footer { padding-left: 22px; padding-right: 22px; }
    }
    """
)


def _bullets(items: list[str]) -> str:
    rendered = "\n".join(f"            <li>{item}</li>" for item in items)
    return f"          <ul>\n{rendered}\n          </ul>"


def _badges(items: list[str]) -> str:
    rendered = "\n".join(
        f"          <span class=\"badge\">{item}</span>" for item in items
    )
    return f"        <div class=\"badges\">\n{rendered}\n        </div>"


def _metric(metric: dict[str, str]) -> str:
    return (
        "          <div class=\"metric\">\n"
        f"            <strong>{metric['title']}</strong>\n"
        f"            {metric['body']}\n"
        "          </div>"
    )


def _stat_row(rows: list[tuple[str, str]]) -> str:
    rendered = "\n".join(
        f"            <div class=\"stat\"><strong>{count}</strong>{label}</div>"
        for count, label in rows
    )
    return f"          <div class=\"stat-row\">\n{rendered}\n          </div>"


def _link_list(links: list[tuple[str, str, str]]) -> str:
    rendered = "\n".join(
        (
            "            <li>"
            f"<a href=\"{href}\">{text}</a>: {desc}"
            "</li>"
        )
        for href, text, desc in links
    )
    return f"          <ul>\n{rendered}\n          </ul>"


def render_html() -> str:
    """Return the complete HTML document for the card."""

    cue_first_row = CUE_TYPE_COUNTS[:4]
    cue_second_row = CUE_TYPE_COUNTS[4:]
    product_paragraphs = "\n".join(
        f"          <p>{para}</p>" for para in PRODUCT_PROBLEM_PARAGRAPHS
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Wearable Assistant Context Benchmark</title>
  <style>
{CSS}  </style>
</head>
<body>
  <div class="page">
    <article class="card">
      <section class="hero">
        <div class="kicker">{KICKER}</div>
        <h1>{TITLE}</h1>
        <p class="subtitle">
          {SUBTITLE}
        </p>
{_badges(HERO_BADGES)}
      </section>

      <div class="grid">
        <section class="section left">
          <h2>Product problem</h2>
{product_paragraphs}
{_bullets(PRODUCT_PROBLEM_BULLETS)}
        </section>

        <section class="section">
          <h2>What this benchmark measures</h2>
          <p>{WHAT_MEASURED_PARAGRAPH}</p>
{_metric(PRIMARY_SCORE_METRIC)}
{_metric(AUXILIARY_METRIC)}
        </section>

        <section class="section left">
          <h2>Three-channel design</h2>
          <p>{THREE_CHANNEL_INTRO}</p>
{_bullets(THREE_CHANNEL_BULLETS)}
        </section>

        <section class="section">
          <h2>Scenario bank</h2>
          <p>{SCENARIO_BANK_INTRO}</p>
{_stat_row(cue_first_row)}
{_stat_row(cue_second_row)}
          <p style="margin-top: 14px;">{SCENARIO_BANK_FOOTER}</p>
        </section>

        <section class="section left">
          <h2>How to read a score</h2>
{_bullets(HOW_TO_READ_BULLETS)}
        </section>

        <section class="section">
          <h2>What this benchmark does NOT measure</h2>
{_bullets(NOT_MEASURED_BULLETS)}
        </section>

        <section class="section left">
          <h2>Repo pointers</h2>
{_link_list(REPO_LINKS)}
        </section>

        <section class="section">
          <h2>Results</h2>
{_metric(RESULTS_METRIC)}
        </section>
      </div>

      <section class="footer">
        <p>
          {FOOTER_PARAGRAPH}
        </p>
      </section>
    </article>
  </div>
</body>
</html>
"""


def render_pdf(html_path: Path, pdf_path: Path) -> Path:
    """Render the HTML at ``html_path`` to a PDF at ``pdf_path``."""

    from weasyprint import HTML  # imported lazily so HTML render works alone

    HTML(filename=str(html_path)).write_pdf(str(pdf_path))
    return pdf_path


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    docs = repo_root / "docs"
    html_path = docs / "benchmark_card.html"
    pdf_path = docs / "wearable_assistant_context_card.pdf"

    html_path.write_text(render_html(), encoding="utf-8")
    print(f"wrote {html_path}")

    render_pdf(html_path, pdf_path)
    print(f"wrote {pdf_path}")


if __name__ == "__main__":
    main()
