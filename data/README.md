# Dataset Card: Wearable Assistant Context Benchmark

## Dataset summary

A cross-turn reference-resolution evaluation set for AI wearable assistants
used actively for advice or coaching (smart glasses, ear worn
devices). Each scenario is a three-turn conversation with a
deliberate context shift between Turn 1 and Turn 2 visible only in
the scene description. The model must integrate scene descriptions with
deictic user speech to determine which context the question refers
to.

For product motivation and quickstart, see
[`README.md`](../../README.md). For the full benchmark contract, see
[`docs/benchmark_spec.md`](../../docs/benchmark_spec.md).

## Supported tasks

- **Reference resolution under cross-turn context shift.** The
  primary task. The judge labels each Turn 2 response as `current`,
  `prior`, `clarify`, or `abstain`.
- **Model selection** for deployed multimodal coaching assistants.
  Use score deltas between candidate models on the same release as
  the comparison signal.

## Languages

English.

## Dataset structure

### Data files

All 70 scenarios live in a single `data/wacb.jsonl` file
(one JSON object per line) with inline `gold` labels. Records are
distinguished by the `subset` field:

| `subset` value | Count | Purpose |
|---|---|---|
| `bank` | 50 | Primary bank. The `baseline`, `baseline-alt`, `ablation-no-camera`, `baseline-qwen-cross-family`, and `baseline-deictic-repair` runs evaluate against this. |
| `contrast` | 20 | Distractor-rich minimal-pair scenarios for ceiling-effect probing. Run via `--subset contrast`. These are controlled minimal pairs, not adversarial-attack examples. |

There is no train/val/test split. The bank is an evaluation set; all
70 scenarios are intended for inference and labeling, not training.

### Data fields

See [`../../docs/schema.md`](../../docs/schema.md) for the full field
reference. The candidate model receives the audio (text-transcript)
and video (scene-description) channels; the judge additionally
receives the answer lists and a ground-truth section naming the
actual objects in frame.

## Statistics (Scenario Bank)

| Statistic | Value |
|---|---|
| Total scenarios | 50 |
| Distinct activity domains | 16 |

### Shift-type distribution (`change_type`)

| Category | Count |
|---|---|
| `object_in_hand` | 12 |
| `object_state` | 8 |
| `sequential_task` | 6 |
| `location` | 6 |
| `object_in_view` | 5 |
| `absent_referent` | 5 |
| `screen_content` | 4 |
| `cross_session_reference` | 4 |

### `target_context` distribution

| Label | Count |
|---|---|
| `current` | 33 |
| `prior` | 12 |
| `clarify` | 3 |
| `abstain` | 2 |

### `difficulty_tier` distribution

| Tier | Count |
|---|---|
| `easy` | 15 |
| `medium` | 20 |
| `hard` | 15 |

### Activity-domain coverage

The bank spans 16 distinct activity domains, including kitchen,
workshop, garden, art and craft, automotive, electronics, sports,
fitness, music, household, office, navigation, finance, and
communication. Coverage is broad but shallow.

## Curation rationale

The 50 Scenario Bank scenarios were authored from scratch following the
rules in
[`../../docs/scenario_authoring_rules.md`](../../docs/scenario_authoring_rules.md).
Each scenario was written within one of the eight shift-type
categories and validated against six checks before inclusion. The
20 contrast scenarios were authored as a separate pack to
discriminate at the top of the score range; same authoring rules,
same validator.

The user message uses natural deictic language without naming
objects, describing visible properties, or announcing context shifts.
The scene description describes scene-level features (shape, material,
color, motion, position) without object names or technique
evaluation. The gold answers (judge-only) uses object names,
technique vocabulary, and state descriptors freely.

## Annotations and validation

Every scenario passes six validation checks before being committed:

1. **Token-leakage scan.** Programmatic word-boundary check that no
   `current_answers` or `prior_answers` token appears in any
   user-speech field.
2. **Object-name scan.** Programmatic word-boundary check that no
   common object name (hammer, screwdriver, pan, etc.) appears in any
   image field.
3. **Schema and structural validation.** All required fields
   present, types correct, scenario IDs unique, category metadata
   matching, distributions matching the targets.
4. **Semantic image-identification review.** Semantic check that
   each image description identifies its object with high confidence
   to a fresh reader.
5. **Semantic-leakage isolation test.** Semantic check that the
   Turn 2 image plus Turn 2 user speech alone (without Turn 1
   context) is not sufficient to answer the question correctly.
6. **Cross-scenario duplication check.** Programmatic textual and
   structural overlap scan to surface near-duplicates.

Checks 1, 2, 3, and 6 run on every PR via
`scripts/validate_scenarios.py`. Checks 4 and 5 run during
authoring.

## Published runs

Six runs are published across the Scenario Bank and the contrast pack.
Each run's `summary.json` (and the historical `findings.md`)
includes the reproducibility manifest.

| Run | Candidate | Judge | Pack | Primary (95% CI) |
|---|---|---|---|---|
| `baseline` | `gemini-2.5-flash-lite` | `gemini-2.5-flash-lite` | Scenario Bank | 60.6% (54.1–67.1) |
| `baseline-alt` | `gemini-2.5-flash` | `gemini-2.5-flash-lite` | Scenario Bank | 77.7% (71.3–84.0) |
| `ablation-no-camera` | `gemini-2.5-flash-lite`, `--no-camera` | `gemini-2.5-flash-lite` | Scenario Bank | 14.4% (9.1–19.7) |
| `baseline-qwen-cross-family` | `dashscope-intl/qwen3-vl-plus` | `gemini-2.5-flash-lite` | Scenario Bank | 54.2% (50.7–57.7) |
| `baseline-deictic-repair` | `gemini-2.5-flash-lite`, `--repair-style deictic` | `gemini-2.5-flash-lite` | Scenario Bank | 60.6% (54.1–67.1) |
| `contrast` | `openrouter/google/gemini-2.5-flash-lite` | `openrouter/openai/gpt-4o-mini` (+ shared judge `claude-haiku-4.5`) | contrast 20 | 67.3% (55.5–79.1) |

### Per-class recall

Per-class recall under `baseline` (full table per run in
`runs/<name>/summary.json`). These are class recall values
(`TP / (TP + FN)`), not overall accuracy:

| Run | `current_recall` | `prior_recall` |
|---|---|---|
| baseline | 87.9% (82.0–92.0) | 33.3% (22.7–45.9) |
| baseline-alt | 97.0% (93.1–98.7) | 58.3% (45.7–69.9) |
| ablation-no-camera | 12.1% (8.0–18.0) | 16.7% (9.3–28.0) |
| baseline-qwen-cross-family | 100.0% (97.7–100.0) | 8.3% (3.6–18.1) |
| baseline-deictic-repair | 87.9% (82.0–92.0) | 33.3% (22.7–45.9) |
| contrast | 84.6% (73.9–91.4) | 50.0% (29.9–70.1) |

### Reproducing the published runs

Each leaderboard row above corresponds to one of the commands below.
The model ids and flags are taken from each run's reproducibility
manifest in `runs/<name>/findings.md`. Outputs land in
`runs/<name>/`.

```bash
# baseline
wac-bench \
  --model gemini/gemini-2.5-flash-lite \
  --judge-model gemini/gemini-2.5-flash-lite --judge-family gemini \
  --output-dir runs/baseline

# baseline-alt
wac-bench \
  --model gemini/gemini-2.5-flash \
  --judge-model gemini/gemini-2.5-flash-lite --judge-family gemini \
  --output-dir runs/baseline-alt

# ablation-no-camera
wac-bench \
  --model gemini/gemini-2.5-flash-lite \
  --judge-model gemini/gemini-2.5-flash-lite --judge-family gemini \
  --no-camera \
  --output-dir runs/ablation-no-camera

# baseline-qwen-cross-family
wac-bench \
  --model dashscope-intl/qwen3-vl-plus \
  --judge-model gemini/gemini-2.5-flash-lite --judge-family gemini \
  --output-dir runs/baseline-qwen-cross-family

# baseline-deictic-repair
wac-bench \
  --model gemini/gemini-2.5-flash-lite \
  --judge-model gemini/gemini-2.5-flash-lite --judge-family gemini \
  --repair-style deictic \
  --output-dir runs/baseline-deictic-repair

# contrast
wac-bench \
  --model openrouter/google/gemini-2.5-flash-lite \
  --judge-model openrouter/openai/gpt-4o-mini --judge-family openai \
  --subset contrast \
  --ranking-judge-model openrouter/anthropic/claude-haiku-4.5 \
  --ranking-judge-family claude \
  --output-dir runs/contrast
```

### Methodology features exercised

- **Cross-family judging.** `baseline-qwen-cross-family` and
  `contrast`. The four Gemini Scenario Bank runs are same-family
  (see Caveats).
- **Shared judge for ranking** (`--ranking-judge-family`). Demonstrated
  on `contrast` with `claude-haiku-4.5`. Rolling out to all
  candidates is a future follow-up.
- **Cross-LLM judge agreement.** Cohen's kappa = 0.443 on
  `contrast` (`gpt-4o-mini` vs `claude-haiku-4.5`).
- **Vision ablation.** `ablation-no-camera`. The 46.2 pp
  drop from `baseline` is reported in
  [`../../docs/benchmark_spec.md`](../../docs/benchmark_spec.md).
- **Deictic vs named repair anchors.** `baseline-deictic-repair`
  pairs against `baseline` for Turn 3 recovery comparison.
- **Contrast pack.** 20 distractor-rich minimal-pair scenarios.
- **Variance reporting.** Single trial per cell at temperature 0
  (default); 95% Wilson CIs per class, 95%
  normal-approximation + percentile bootstrap CIs on the mean
  recall. Re-run with `--trials N` and non-zero temperature when
  variance reporting matters.
- **Static lockfile.** `MANIFEST.lock.json` pins asset hashes; CI
  fails on drift.

## Considerations for using the data

### Out-of-scope by design

The benchmark does not measure these and does not intend to:

- **Coaching advice quality** (correctness, safety, domain
  appropriateness)
- **Multi-turn dynamics** beyond three turns
- **Proactive coaching** (assistance offered without a direct
  question)
- **Domain expertise depth** (coverage spans 16 domains, broad not
  deep)
- **Latency, cost, serving characteristics**
- **Speaker attribution, addressee detection, ambient audio**

### Caveats on the published runs

- **Same-family judging on four of five Scenario Bank runs.** Mid-run,
  the API budget ran out across non-Gemini providers (OpenRouter,
  OpenAI direct, HF Inference Providers Pro), leaving Gemini-direct
  via LiteLLM as the only working path. Gemini-Flash-Lite ended up
  judging Gemini-Flash-Lite (and Gemini-Flash). Same-family pairings
  can show self-preference bias.
  `baseline-qwen-cross-family` is the cross-family reference for the
  Scenario Bank.
- **Two model-config families across the published runs.** Five Scenario Bank runs
  use Gemini-direct + DashScope-International; `contrast` uses
  OpenRouter. Each `summary.json` carries full candidate and judge
  ids.

### Future follow-ups

- Re-run the Scenario Bank under one shared judge so candidates
  can be ranked directly against each other.
- Re-run `contrast` under the same Gemini setup as the Scenario
  Bank so the model-config story across all six runs is consistent.

### Future follow-ups

- **Human inter-annotator agreement.** The benchmark currently reports cross-LLM judge
  agreement only. Human IAA on a 25% sample with Cohen's kappa is
  the highest-priority future follow-up.
- **Real-video validation.** The scene description uses text scene
  descriptions as a stand-in for actual video. Held-out video
  validation on a representative sample is future work.
- **Raw-audio validation.** The benchmark represents the user's spoken turns as
  text transcripts.
- **Multi-trial generalization.** Default is one trial at
  temperature 0. Multi-seed generalization at non-zero temperature
  is unreported.
- **Full omnimodal stack** (live audio in, real-time streaming,
  voice-mode output, interruption handling).

For score-interpretation guidance and a longer treatment, see
[`../../docs/benchmark_spec.md`](../../docs/benchmark_spec.md).

## License

MIT, the same as the rest of the repository. See
[`../../LICENSE`](../../LICENSE).
