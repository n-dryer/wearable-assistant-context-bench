"""Render the public GitHub Pages landing page for the benchmark.

Outputs:
    docs/index.html

Run:
    .venv/bin/python docs/index.py

The page is a single-file static HTML, designed to mirror the
visual language of the benchmark card. It is the landing page at
https://n-dryer.github.io/wearable-assistant-context-bench/.
"""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent


OUT_HTML = Path(__file__).parent / "index.html"


CSS = """
@import url('https://rsms.me/inter/inter.css');

* { box-sizing: border-box; }

html, body {
    margin: 0;
    padding: 0;
    font-family: "Inter", "Helvetica Neue", "Helvetica", "Arial", sans-serif;
    color: #2b2118;
    background: radial-gradient(circle at 30% 20%, #fffaf4 0%, #f6f1ea 100%);
    min-height: 100vh;
    font-size: 16px;
    line-height: 1.62;
    -webkit-font-smoothing: antialiased;
}

a { color: #b14f31; text-decoration: none; border-bottom: 1px solid rgba(177, 79, 49, 0.25); }
a:hover { border-bottom-color: #b14f31; }

code {
    font-family: ui-monospace, "SFMono-Regular", Menlo, monospace;
    background: rgba(255, 255, 255, 0.7);
    padding: 1px 6px;
    border-radius: 6px;
    font-size: 0.92em;
}

.page {
    max-width: 1100px;
    margin: 36px auto;
    background: #fffaf4;
    border-radius: 28px;
    padding: 56px 64px 48px;
    box-shadow: 0 20px 60px rgba(43, 33, 24, 0.08);
}

.kicker {
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.18em;
    color: #b14f31;
    background: #f4dfd5;
    display: inline-block;
    padding: 6px 14px;
    border-radius: 100px;
}

h1 {
    font-size: clamp(34px, 5vw, 58px);
    line-height: 1.05;
    font-weight: 800;
    letter-spacing: -0.04em;
    margin: 18px 0 12px 0;
    color: #2b2118;
}

.subtitle {
    font-size: 18px;
    color: #5b4a3d;
    max-width: 720px;
    margin: 0 0 22px 0;
}

.badges {
    margin-top: 18px;
    margin-bottom: 4px;
}

.badge {
    display: inline-block;
    font-size: 13px;
    font-weight: 600;
    padding: 6px 14px;
    border-radius: 100px;
    background: #f0e8dd;
    color: #5b4a3d;
    margin-right: 8px;
    margin-bottom: 8px;
    border: 1px solid #e3d8c8;
}

section.row {
    display: grid;
    grid-template-columns: 1fr;
    gap: 0;
    margin-top: 36px;
    border-top: 1px solid #e9dfce;
    padding-top: 28px;
}

section.row .label {
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.16em;
    color: #6b5a4d;
    margin-bottom: 12px;
}

section.row h2 {
    font-size: 26px;
    font-weight: 700;
    letter-spacing: -0.02em;
    margin: 0 0 14px 0;
    color: #2b2118;
}

section.row h3 {
    font-size: 13px;
    font-weight: 700;
    color: #b14f31;
    margin: 24px 0 4px 0;
    text-transform: uppercase;
    letter-spacing: 0.14em;
}

section.row h3:first-of-type {
    margin-top: 18px;
}

table.leaderboard {
    width: 100%;
    border-collapse: collapse;
    margin: 18px 0 8px 0;
    font-size: 15px;
}

table.leaderboard th, table.leaderboard td {
    padding: 12px 14px;
    text-align: left;
    border-bottom: 1px solid #e9dfce;
}

table.leaderboard th {
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: #6b5a4d;
    font-weight: 700;
    background: rgba(255, 255, 255, 0.5);
}

table.leaderboard td.score {
    font-weight: 700;
    font-variant-numeric: tabular-nums;
}

table.leaderboard tr.highlight td {
    background: #fff4ea;
}

.callout {
    background: #f0e8dd;
    border-radius: 14px;
    padding: 18px 22px;
    margin-top: 18px;
}

.callout .callout-title {
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.16em;
    color: #b14f31;
    font-weight: 700;
    margin-bottom: 8px;
}

.callout .callout-stat {
    font-size: 28px;
    font-weight: 800;
    letter-spacing: -0.02em;
    color: #2b2118;
    margin-bottom: 6px;
}

.callout p {
    margin: 0;
    font-size: 15px;
    color: #5b4a3d;
}

ul.bullets {
    margin: 8px 0 0 0;
    padding-left: 22px;
}

ul.bullets li {
    margin-bottom: 8px;
}

.callout.muted {
    background: #faf5ee;
}

.callout .callout-stat.flow {
    font-size: 22px;
    font-variant-numeric: tabular-nums;
}

.glossary-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 28px 40px;
    margin-top: 14px;
}

.glossary-cat h3 {
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.14em;
    color: #b14f31;
    margin: 0 0 10px 0;
}

.glossary-cat dl {
    margin: 0;
    padding: 0;
}

.glossary-cat dt {
    font-weight: 700;
    font-size: 15px;
    color: #2b2118;
    margin-top: 14px;
}

.glossary-cat dt:first-of-type {
    margin-top: 0;
}

.glossary-cat dd {
    margin: 4px 0 0 0;
    padding: 0;
    font-size: 15px;
    color: #5b4a3d;
}

@media (max-width: 720px) {
    .glossary-grid { grid-template-columns: 1fr; gap: 28px; }
}

.footer {
    margin-top: 40px;
    padding-top: 22px;
    border-top: 1px solid #e9dfce;
    font-size: 13px;
    color: #6b5a4d;
}

.footer .links {
    margin-top: 10px;
}

.footer .links a {
    margin-right: 18px;
}

.footer .links-label {
    display: inline-block;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    font-size: 11px;
    color: #6b5a4d;
    margin-right: 14px;
}

@media (max-width: 720px) {
    .page { padding: 32px 22px; margin: 12px; }
}
"""


def render_html() -> str:
    return dedent(f"""\
    <!doctype html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Wearable Assistant Context Benchmark</title>
        <meta name="description" content="When the user's situation changes mid-conversation, does a wearable AI assistant follow along, or stay stuck on what was happening before? 50 scenarios scored across four runs.">

        <meta property="og:type" content="website">
        <meta property="og:title" content="Wearable Assistant Context Benchmark">
        <meta property="og:description" content="When the user's situation changes mid-conversation, does the assistant follow along, or stay stuck on what was happening before? 50 scenarios, four published runs. v1.0.0 April 2026.">
        <meta property="og:url" content="https://n-dryer.github.io/wearable-assistant-context-bench/">
        <meta property="og:image" content="https://n-dryer.github.io/wearable-assistant-context-bench/og-image.png">
        <meta property="og:image:width" content="1200">
        <meta property="og:image:height" content="630">
        <meta property="og:image:alt" content="Wearable Assistant Context Benchmark v1.0.0. 50 scenarios, four published runs, MIT license.">

        <meta name="twitter:card" content="summary_large_image">
        <meta name="twitter:title" content="Wearable Assistant Context Benchmark">
        <meta name="twitter:description" content="When the user's situation changes mid-conversation, does the assistant follow along, or stay stuck on what was happening before? 50 scenarios, four published runs. v1.0.0 April 2026.">
        <meta name="twitter:image" content="https://n-dryer.github.io/wearable-assistant-context-bench/og-image.png">
        <meta name="twitter:image:alt" content="Wearable Assistant Context Benchmark v1.0.0.">

        <style>{CSS}</style>
    </head>
    <body>
    <main class="page">

        <div class="kicker">v1.0.0 &middot; April 2026</div>
        <h1>Wearable Assistant Context Benchmark</h1>
        <p class="subtitle">
            A multimodal AI assistant the user is actively using
            for advice or coaching (wearable or handheld) sees what
            the user sees and hears what they say. When the user's
            situation changes (they swap tools, walk into a new
            room), does the assistant follow along, or stay stuck
            on what was happening before? This benchmark measures
            <strong>context tracking</strong>: whether the model's
            answer reflects the user's current situation or the
            previous one.
        </p>

        <div class="badges">
            <span class="badge">50 + 20 scenarios</span>
            <span class="badge">6 published runs</span>
            <span class="badge">5 trials per cell, 95% CIs</span>
        </div>

        <section class="row">
            <div class="label">Methodology</div>
            <h2>How the test works</h2>
            <p>Picture an assistant that sees what you see and
            hears what you say. You ask it questions and it
            answers.</p>
            <p>In the middle of a conversation, your situation
            changes. You picked up a different tool. You walked
            into another room. The thing on screen switched. You
            didn't say it out loud. It just happened in front of
            the device. Then you ask a follow-up. Does the
            assistant answer about what's happening now, or about
            what was happening a minute ago?</p>
            <p>Each scenario is structured around three
            <strong>turns</strong> (a turn is one user message
            plus the model's response). Turn 1 sets the scene.
            Between Turn 1 and Turn 2, the
            <strong>context shifts</strong> (something visible
            changes) without being announced. Turn 2 is a question
            that only makes sense if the model noticed the shift.
            Turn 3 fires only when the model misses Turn 2: the
            user clarifies and the model gets one more chance,
            scored as the <strong>repair rate</strong>.</p>
            <p>Each scenario carries a target label that says what
            the right answer should refer to:
            <code>current</code> (the new situation),
            <code>prior</code> (an earlier situation the user is
            referring back to), <code>clarify</code> (the
            assistant should ask which thing is meant), or
            <code>abstain</code> (the assistant should say it
            can't tell). The 50 canonical scenarios are spread
            across eight kinds of context shift: object switched
            in hand, same object in a different state, the next
            step of a sequential task, a change of location, a
            new object brought into view, an absent referent (the
            thing the question is about is no longer visible),
            the content of a screen changing, and recall of
            something the device saw before the conversation
            began.</p>
            <p><strong>One disclosure up front.</strong> The
            camera input is short text descriptions of the scene,
            not actual video frames. The audio input is text
            transcripts, not raw audio. Both are deliberate
            proxies that isolate context tracking from
            perceptual-front-end noise. That keeps the benchmark
            cheap and reproducible, but it means a model that does
            well here might not do well on real video or raw
            audio. More on that in
            <a href="#out-of-scope">Out of scope</a>.</p>
        </section>

        <section class="row">
            <div class="label">Results</div>
            <h2>Six published runs</h2>

            <p>Each row below is an isolated experiment, not a
            ranked leaderboard. The score measures how often the
            assistant correctly realizes the situation has changed
            versus getting stuck on what happened before. The
            <strong>primary score</strong> is balanced Turn 2
            accuracy: the average of accuracy on
            <code>current</code>-target scenarios and accuracy on
            <code>prior</code>-target scenarios under the neutral
            system prompt, weighted equally so the larger class
            doesn't dominate the headline.</p>

            <p>Five runs use the canonical 50-scenario bank; one
            uses a separate 20-scenario adversarial pack designed
            to discriminate at the top of the score range. CIs are
            95% Wilson intervals per class, 95% normal-approximation
            on the balanced mean.</p>

            <table class="leaderboard">
                <thead>
                    <tr>
                        <th>Run</th>
                        <th>What it shows</th>
                        <th>Candidate</th>
                        <th>Judge</th>
                        <th>Pack</th>
                        <th>Primary score (95% CI)</th>
                    </tr>
                </thead>
                <tbody>
                    <tr class="highlight">
                        <td><strong>baseline</strong></td>
                        <td>Same-family Gemini canonical</td>
                        <td><code>gemini-2.5-flash-lite</code></td>
                        <td><code>gemini-2.5-flash-lite</code></td>
                        <td>50</td>
                        <td class="score">60.6% (54.1&ndash;67.1)</td>
                    </tr>
                    <tr class="highlight">
                        <td><strong>baseline-alt</strong></td>
                        <td>Bigger Gemini sibling</td>
                        <td><code>gemini-2.5-flash</code></td>
                        <td><code>gemini-2.5-flash-lite</code></td>
                        <td>50</td>
                        <td class="score">77.7% (71.3&ndash;84.0)</td>
                    </tr>
                    <tr class="highlight">
                        <td><strong>ablation-no-camera</strong></td>
                        <td>Camera channel stripped</td>
                        <td><code>gemini-2.5-flash-lite</code></td>
                        <td><code>gemini-2.5-flash-lite</code></td>
                        <td>50</td>
                        <td class="score">14.4% (9.1&ndash;19.7)</td>
                    </tr>
                    <tr class="highlight">
                        <td><strong>baseline-qwen-cross-family</strong></td>
                        <td>Cross-family integrity reference</td>
                        <td><code>qwen3-vl-plus</code></td>
                        <td><code>gemini-2.5-flash-lite</code></td>
                        <td>50</td>
                        <td class="score">54.2% (50.7&ndash;57.7)</td>
                    </tr>
                    <tr>
                        <td>baseline-deictic-repair</td>
                        <td>Deictic vs named repair</td>
                        <td><code>gemini-2.5-flash-lite</code></td>
                        <td><code>gemini-2.5-flash-lite</code></td>
                        <td>50</td>
                        <td class="score">60.6% (54.1&ndash;67.1)</td>
                    </tr>
                    <tr>
                        <td>adversarial</td>
                        <td>Distractor-rich pack</td>
                        <td><code>gemini-2.5-flash-lite</code></td>
                        <td><code>gpt-4o-mini</code></td>
                        <td>20</td>
                        <td class="score">67.3% (55.5&ndash;79.1)</td>
                    </tr>
                </tbody>
            </table>

            <p>The five canonical runs share the same 50-scenario
            bank, so primary scores compare directly within a run
            (apples-to-apples). The fifth canonical run
            (<code>baseline-deictic-repair</code>) shares the same
            Turn 2 setup as <code>baseline</code>, so its primary
            score is identical; the difference shows up in the
            repair rate (Turn 3 recovery), discussed below.</p>
        </section>

        <section class="row">
            <div class="label">Camera ablation</div>
            <h2>Without the camera input, the model can't answer</h2>
            <div class="callout">
                <div class="callout-title">Same model, camera shown vs hidden</div>
                <div class="callout-stat flow">60.6% &rarr; 14.4%</div>
                <p>The <strong>camera ablation</strong> takes the
                same candidate model and the same judge and runs
                them twice: once with the scene description
                included in the prompt (<code>baseline</code>),
                once with it stripped (<code>ablation-no-camera</code>).
                The 46.2 percentage-point drop rules out one
                alternative reading of the headline numbers, namely
                that the model is solving the task by guessing
                from question phrasing alone. It can't. It needs
                the camera input. (This isn't on its own a proof
                of deeper context tracking; the per-class pattern
                below fills in the rest.)</p>
            </div>
        </section>

        <section class="row">
            <div class="label">Per-class pattern</div>
            <h2>The model handles "current," but stumbles on "prior"</h2>
            <div class="callout">
                <div class="callout-title">Cross-family integrity reference: Qwen3-VL-Plus + Gemini judge</div>
                <div class="callout-stat flow">100.0% on <code>current</code> / 8.3% on <code>prior</code></div>
                <p>Across all six runs the model is much better
                when the right answer is about the most recent
                frame than when the right answer is about an
                earlier frame. The
                <code>baseline-qwen-cross-family</code> run is the
                clearest example: 100% accuracy when the target is
                <code>current</code>, 8.3% when the target is
                <code>prior</code>. The model grounds in the
                latest visual input and struggles to refer back.
                Together with the camera ablation, this is the
                capability gap the benchmark targets: a strong
                read on what's in front of the model right now,
                paired with a weak read on what the user is
                referring back to.</p>
            </div>
        </section>

        <section class="row">
            <div class="label">Repair rate</div>
            <h2>When the user clarifies, what recovers?</h2>
            <div class="callout">
                <div class="callout-title">Deictic vs named repair on the canonical bank</div>
                <div class="callout-stat flow">Deictic 50/50 (100%) &middot; Named 30/100 (30%)</div>
                <p>If the model misses Turn 2, the user gets one
                clarifying follow-up. The
                <strong>repair rate</strong> is how often the
                model gets it right after that clarification. v1
                ships two clarification styles. The
                <strong>named anchor</strong> spells out both
                objects ("I mean the hammer I'm holding now, not
                the screwdriver from before"); it's the floor
                metric. The <strong>deictic anchor</strong> uses
                gesture-style language only ("no, this, what I'm
                holding now"); it's the realistic-recovery signal.
                On scenarios where a pointing gesture can resolve
                the reference, deictic recovery is perfect.
                Elsewhere (when the user is referring back to
                something not currently visible), verbal
                clarification rarely helps.</p>
            </div>
        </section>

        <section class="row">
            <div class="label">Judge agreement</div>
            <h2>Two models, the same labels: how often do they agree?</h2>
            <div class="callout muted">
                <div class="callout-title">Cross-LLM agreement on the adversarial pack</div>
                <div class="callout-stat flow">Cohen's &kappa; = 0.443 (moderate)</div>
                <p>Each Turn 2 answer is read by a second model
                (the <strong>judge</strong>) that emits one of the
                four target labels. The default is
                <strong>cross-family judging</strong>: the judge
                comes from a different model maker than the
                candidate, which removes self-preference bias (the
                tendency of a model to rate its own family's
                outputs more favorably). The
                <strong>fixed ranking judge</strong> is a second
                judge held constant across runs so candidates can
                be compared apples-to-apples. On the adversarial
                pack, both judges labeled the same 300 trials and
                agreed on 190 of them. Cohen's &kappa; (a standard
                measure of inter-rater agreement that corrects for
                chance agreement) of 0.443 is moderate. The labels
                are not idiosyncratic to one model family, but they
                aren't perfectly aligned either. v1 reports this
                cross-LLM agreement as a
                substitute for human inter-annotator agreement
                (planned v2 work).</p>
            </div>
        </section>

        <section class="row">
            <div class="label">Caveats on v1 numbers</div>
            <h2>What to keep in mind when reading the table</h2>
            <p>API budget exhausted across multiple providers
            mid-effort, leaving Gemini-direct as the only
            transport for the bulk of the canonical runs. Three
            of the four canonical Gemini runs ended up
            same-family (Gemini-Flash-Lite judging itself).
            Same-family judging admits self-preference bias, so
            those numbers may be inflated.
            <code>baseline-qwen-cross-family</code> is the
            cross-family integrity reference for the canonical
            bank: same scenarios, same scoring rules, but a
            non-Gemini candidate paired with the Gemini judge.
            The 6.4-point gap between same-family
            <code>baseline</code> (60.6%) and cross-family
            <code>baseline-qwen-cross-family</code> (54.2%) is the
            visible self-preference signal, though candidate
            quality differs between the two runs and explains
            some of the gap as well.</p>
        </section>

        <section class="row" id="out-of-scope">
            <div class="label">Limitations</div>
            <h2>What is out of scope</h2>

            <h3>Inputs</h3>
            <ul class="bullets">
                <li><strong>Real video frames.</strong> The camera
                    input is text descriptions of the scene, not
                    actual frames. A model that does well here
                    might not do well on real video.</li>
                <li><strong>Raw audio.</strong> Scoring is on
                    text. The user's spoken turns are represented
                    as text transcripts. Acoustic grounding,
                    speaker attribution, ambient audio cues are
                    not exercised.</li>
                <li><strong>Live audio and voice mode.</strong> A
                    real wearable also needs to listen, talk back,
                    and handle interruptions in real time. None of
                    that is exercised here.</li>
            </ul>

            <h3>Answer characteristics</h3>
            <ul class="bullets">
                <li><strong>Advice quality.</strong> The judge
                    doesn't check whether the answer is correct,
                    safe, or appropriate to the domain. A
                    confidently wrong answer can pass.</li>
                <li><strong>Domain depth.</strong> Whether the
                    advice is expert-level for cooking,
                    woodworking, or any other activity in the
                    scenario.</li>
                <li><strong>Proactive coaching.</strong> Whether
                    the assistant volunteers help unprompted.</li>
            </ul>

            <h3>Conversation shape</h3>
            <ul class="bullets">
                <li><strong>Multi-turn flow past Turn 2.</strong>
                    Whether the conversation works naturally from
                    Turn 3 onward.</li>
                <li><strong>Long-horizon memory.</strong> Recall
                    across days or weeks.</li>
            </ul>

            <h3>Engineering and statistics</h3>
            <ul class="bullets">
                <li><strong>Latency and cost.</strong> Wall-clock
                    response time and price per call. Not
                    measured.</li>
                <li><strong>Generalization beyond 5 trials per
                    cell.</strong> v1 reports 95% CIs. Higher
                    trial counts and seed sweeps are v2 work.</li>
                <li><strong>Human inter-annotator agreement.</strong>
                    v1 reports cross-LLM agreement only. A second
                    human rater on a 25% sample is the
                    highest-priority v2 follow-up.</li>
            </ul>

            <p>Full discussion in
            <a href="https://github.com/n-dryer/wearable-assistant-context-bench/blob/main/docs/benchmark_notes.md">benchmark_notes.md</a>.</p>
        </section>

        <div class="footer">
            <div>Built by <strong>Nate Dryer</strong>. Released under the MIT License. Code and scenarios at
            <a href="https://github.com/n-dryer/wearable-assistant-context-bench">github.com/n-dryer/wearable-assistant-context-bench</a>.
            For citation, see <a href="https://github.com/n-dryer/wearable-assistant-context-bench/blob/main/CITATION.cff">CITATION.cff</a>.</div>
            <div class="links">
                <span class="links-label">For readers:</span>
                <a href="benchmark_card.html">One-page card</a>
                <a href="wearable_assistant_context_card.pdf">PDF</a>
                <a href="https://github.com/n-dryer/wearable-assistant-context-bench">GitHub repo</a>
            </div>
            <div class="links">
                <span class="links-label">For implementers:</span>
                <a href="https://github.com/n-dryer/wearable-assistant-context-bench/blob/main/docs/benchmark_spec.md">Spec</a>
                <a href="https://github.com/n-dryer/wearable-assistant-context-bench/blob/main/docs/benchmark_notes.md">Notes</a>
                <a href="https://github.com/n-dryer/wearable-assistant-context-bench/blob/main/docs/schema.md">Schema</a>
                <a href="https://github.com/n-dryer/wearable-assistant-context-bench/blob/main/docs/scenario_authoring_rules.md">Authoring rules</a>
            </div>
        </div>

    </main>
    </body>
    </html>
    """)


def main() -> None:
    OUT_HTML.write_text(render_html(), encoding="utf-8")
    size = OUT_HTML.stat().st_size
    print(f"Wrote {OUT_HTML} ({size:,} bytes)")


if __name__ == "__main__":
    main()
