# v1 language-pass plan

> **Historical.** This document was the authoring plan for the v1 plain-language
> pass executed in April 2026. All edits described here have been applied. It is
> retained for provenance only.

This file enumerates the plain-language edits for the v1 release.
Each entry lists the file, the tell (em dash, LLM cliche, stiff
passive, sentence length), and the target replacement. Literal
em-dash characters are written as `[EM]` in this plan so that the
plan itself is em-dash-free per the release rule.

Industry nomenclature is preserved: deixis, situated reference
resolution, balanced Turn 2 accuracy, target_context, judge,
candidate, abstain, clarify, frozen set, reproducibility manifest,
context shift, anchor, cue, reference resolution.

## Global rules

1. Replace every `[EM]` with a comma, period, parenthesis, or
   colon, whichever preserves meaning with least disruption.
2. Remove the LLM cliche "landscape" in `docs/concept_v0_2.md`
   (lines 98, 112). "lm-evaluation-harness" and "evaluation harness"
   are tool terminology and stay.
3. Leave industry nomenclature intact.
4. Do not shorten anything load-bearing for accuracy.
5. Do not re-introduce `[EM]` while rewriting.

## File-by-file

### README.md

- Lines 6 to 7 (lead paragraph): parenthetical `[EM]` pair around
  the cues list. Replace the opening `[EM]` and the closing `[EM]`
  with parentheses so the cue list becomes a parenthetical.

- Lines 127 to 135 (flag glossary): each bullet reads `` - `--flag`
  [EM] definition ``. Replace the `[EM]` with a colon. Five entries:
  `--model`, `--judge-model`, `--judge-family`, `--trials`,
  `--output-dir`.

- Lines 197 to 217 (glossary block): each entry reads
  `- **term** [EM] definition`. Replace the `[EM]` with a colon.
  Entries: surface, trial, cell, condition, ranking condition,
  target_context, with-prior-Q / without-prior-Q, candidate,
  judge.

- No LLM cliches found in README.

### docs/concept_v0_2.md

- Lines 10 to 11 (lead paragraph): parenthetical `[EM]` pair around
  "from the user's words, objects, location, and recent
  conversational history". Replace both `[EM]`s with commas so the
  phrase reads as a prose parenthetical.

- Lines 15 to 16: parenthetical `[EM]` pair around "reference
  resolution under context shift". Replace both with commas so the
  phrase reads as a parenthetical.

- Lines 28 to 40 (cue-taxonomy bullets): each bullet reads
  `- **X** [EM] definition`. Replace the `[EM]` with a colon.
  Five entries.

- Line 98: rename the section heading `### Scope relative to the
  broader pilot failure landscape` to `### Scope relative to the
  broader pilot failure surface`.

- Line 112: rephrase to drop "landscape". Current body says "not
  the full pilot failure landscape." Rewrite to "not every failure
  class the pilot corpus surfaced."

### docs/methodology.md

- Lines 125 to 129 (flag glossary): same pattern as README.
  Replace the `[EM]` in each bullet with a colon. Five entries.

### docs/limitations.md

- Line 38: inline `[EM]` between "clarifying question back" and
  "they already told the assistant where to look". Replace with a
  sentence break (period + capital T).

- Line 49: inline `[EM]` between "the candidate's clarify/abstain
  rate is still legible" and "it is just not rewarded in the
  ranking number". Replace with a semicolon.

- Line 82: `[EM]` inside a parenthetical list `(sc-03, sc-09,
  sc-10 [EM] the reach-back items)`. Replace with a comma.

### docs/related_work.md

- No `[EM]`. No LLM cliches. No edit. "lm-evaluation-harness" is a
  tool name and stays; "evaluation harness structure" is industry
  wording and stays.

### docs/deferred_roadmap.md

- Line 175: inline `[EM]` between "a small comparison slice" and
  "running the v1 candidates". Rewrite the sentence so it reads
  "a small comparison slice that runs the v1 candidates on a named
  external benchmark".

### docs/surface.md

- No `[EM]`. No LLM cliches. No edit.

### experiments/exp_001/README.md

- Line 67: `[EM]` pair around "it does not enter scoring". Replace
  with parentheses.

- Line 70 (table header): still reads `target\_policy` after the
  earlier rename. Fix to `target\_context`.

### CHANGELOG.md

- Lines 9, 54, 61, 67: release-header bracket form
  `## [v1] [EM] 2026-04-20`. Replace the `[EM]` with parentheses
  around the date: `## [v1] (2026-04-20)`. Apply identically to
  `v1.1-extension`, `v0.3.0`, `v0.1 / Phase 0-4 scaffold` headers.

### CONTRIBUTING.md

- No `[EM]`. No LLM cliches. No edit.

### results/README.md

- Lines 5 to 6: parenthetical `[EM]` pair around the listed report
  sections. Replace both `[EM]`s with parentheses.

### CITATION.cff

- No `[EM]`. No LLM cliches. No edit.

## Sentence length spot-check

The 30-word cap is a heuristic, not a hard rule. Spot reads of the
twelve files show most sentences under 30 words; no rewrites are
triggered by length alone.

## Out of scope

- `experiments/exp_001/scenarios.json`, `experiments/exp_001/expected_answers.json`.
  Frozen-set rule.
- `core/scoring.py` formula.
- `core/` docstrings and comments.
- `docs/history/` bodies. Banners added in Step 6.
