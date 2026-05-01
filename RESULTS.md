# Findings

Headline takeaways for the six published runs. The runner emits a
`findings.md` next to each run's `summary.json` under
`runs/<name>/`; this document is the consolidated
public summary that links out to those.

Full transcripts are not committed (they are gitignored).
Each run's `summary.json` carries the aggregated metrics and
manifest. To regenerate a transcript, re-run the matching command
from `data/README.md#reproducing-the-published-runs`.

## baseline (`gemini-2.5-flash-lite`, same-family judge)

- Primary metric (mean recall): **60.6%** (95% CI 54.1–67.1)
- Per-class recall: `current` 87.9% (82.0–92.0), `prior` 33.3%
  (22.7–45.9)
- The candidate is well-anchored to the new frame and over-sticks
  when the prior frame is the correct answer.
- Detail: `runs/baseline/findings.md`

## baseline-alt (`gemini-2.5-flash`, same-family judge)

- Primary metric: **77.7%** (71.3–84.0)
- Per-class recall: `current` 97.0% (93.1–98.7), `prior` 58.3%
  (45.7–69.9)
- Strongest published Scenario Bank result. The lift in
  `prior_recall` is the main difference between the two model
  sizes.
- Detail: `runs/baseline-alt/findings.md`

## baseline-deictic-repair (`gemini-2.5-flash-lite`, `--repair-style deictic`)

- Primary metric: **60.6%** (54.1–67.1), the same as baseline.
- Pairs against `baseline` to compare named vs deictic repair-anchor
  recoverability. The Turn 2 numbers match; the runs differ only in
  the Turn 3 branch, which is meaningful only when
  `enable_repair: true`.
- Detail: `runs/baseline-deictic-repair/findings.md`

## baseline-qwen-cross-family (`dashscope-intl/qwen3-vl-plus`, Gemini judge)

- Primary metric: **54.2%** (50.7–57.7)
- Per-class recall: `current` 100.0% (97.7–100.0), `prior` 8.3%
  (3.6–18.1)
- Cross-family judge run. The extreme gap between `current` and
  `prior` recall is the diagnostic signal: the candidate snaps to
  the latest frame and ignores the prior frame almost entirely.
- Detail: `runs/baseline-qwen-cross-family/findings.md`

## ablation-no-camera (`gemini-2.5-flash-lite` with `--no-camera`)

- Primary metric: **14.4%** (9.1–19.7)
- Per-class recall: `current` 12.1% (8.0–18.0), `prior` 16.7% (9.3–28.0)
- A 46.2 pp drop from `baseline`. The simplest evidence that the
  task depends on the scene description. Stripping the `[Camera: ...]`
  blocks leaves the model with nothing to ground deictic references
  against, and the score collapses.
- Detail: `runs/ablation-no-camera/findings.md`

## contrast (`gemini-2.5-flash-lite` (OpenRouter), GPT-4o-mini judge + Claude Haiku shared judge)

- Primary metric: **67.3%** (55.5–79.1)
- Per-class recall: `current` 84.6% (73.9–91.4), `prior` 50.0%
  (29.9–70.1)
- Cross-LLM inter-judge agreement (Cohen's kappa): 0.443.
- The contrast subset uses 20 distractor-rich scenarios where the
  prior object or scene may still be visible at Turn 2.
- Detail: `runs/contrast/findings.md`
