# Dataset Card: Wearable Assistant Context Benchmark v1

## Dataset summary

A context-tracking evaluation set for multimodal AI assistants used
actively for advice or coaching (wearable or handheld). Each
scenario is a three-turn conversation with a deliberate context
shift between Turn 1 and Turn 2 visible only in the camera channel.
The model must integrate scene descriptions with deictic user speech
to determine which context the question refers to.

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

The bank ships in three split groups:

| Group | Files | Count | Purpose |
|---|---|---|---|
| Canonical | `scenarios.json`, `expected_answers.json` | 50 | Frozen primary bank. The `baseline`, `baseline-alt`, `ablation-no-camera`, `baseline-qwen-cross-family`, and `baseline-deictic-repair` runs evaluate against this. |
| Adversarial | `scenarios_adversarial.json`, `expected_answers_adversarial.json` | 20 | Distractor-rich scenarios for ceiling-effect probing. Run via `--pack adversarial`. |
| Hard | `scenarios_v2_candidates.json`, `expected_answers_v2_candidates.json` | 15 | Ceiling-test scenarios (all `difficulty_tier: hard`) targeting cells the canonical bank under-covers. Authored after the empirical-difficulty analysis showed that 36% of the canonical bank is harder than its author tier suggests. Run via `--pack hard`. |

There is no train/val/test split. The bank is an evaluation set; all
85 scenarios are intended for inference and labeling, not training.

### Data fields

See [`../../docs/schema.md`](../../docs/schema.md) for the full field
reference. The candidate model receives the audio (text-transcript)
and camera (scene-description) channels; the judge additionally
receives the answer lists and a ground-truth section naming the
actual objects in frame.

## Statistics (canonical bank)

| Statistic | Value |
|---|---|
| Total scenarios | 50 |
| Distinct activity domains | 16 |

### Shift-type distribution (`cue_type`)

| Category | Count |
|---|---|
| `object_in_hand` | 12 |
| `object_state` | 8 |
| `sequential_task` | 6 |
| `location` | 6 |
| `object_in_view` | 5 |
| `absent_referent` | 5 |
| `screen_content` | 4 |
| `pre_conversation_recall` | 4 |

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

The 50 canonical scenarios were authored from scratch following the
rules in
[`../../docs/scenario_authoring_rules.md`](../../docs/scenario_authoring_rules.md).
Each scenario was written within one of the eight shift-type
categories and validated against six checks before inclusion. The
20 adversarial scenarios were authored as a separate pack to
discriminate at the top of the score range; same authoring rules,
same validator.

The audio channel uses natural deictic language without naming
objects, describing visible properties, or announcing context shifts.
The camera channel describes scene-level features (shape, material,
color, motion, position) without object names or technique
evaluation. The ground-truth channel (judge-only) uses object names,
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

## v1 release runs

v1 publishes six runs across the canonical and adversarial packs.
Each run's full `findings.md` includes the reproducibility manifest.

| Run | Candidate | Judge | Pack | Primary (95% CI) |
|---|---|---|---|---|
| `baseline` | `gemini-2.5-flash-lite` | `gemini-2.5-flash-lite` | canonical 50 | 60.6% (54.1–67.1) |
| `baseline-alt` | `gemini-2.5-flash` | `gemini-2.5-flash-lite` | canonical 50 | 77.7% (71.3–84.0) |
| `ablation-no-camera` | `gemini-2.5-flash-lite`, `--no-camera` | `gemini-2.5-flash-lite` | canonical 50 | 14.4% (9.1–19.7) |
| `baseline-qwen-cross-family` | `dashscope-intl/qwen3-vl-plus` | `gemini-2.5-flash-lite` | canonical 50 | 54.2% (50.7–57.7) |
| `baseline-deictic-repair` | `gemini-2.5-flash-lite`, `--repair-style deictic` | `gemini-2.5-flash-lite` | canonical 50 | 60.6% (54.1–67.1) |
| `adversarial` | `openrouter/google/gemini-2.5-flash-lite` | `openrouter/openai/gpt-4o-mini` (+ ranking judge `claude-haiku-4.5`) | adversarial 20 | 67.3% (55.5–79.1) |

For the full per-class breakdown, see
[`README.md#results`](../../README.md#results).

### Methodology features exercised

- **Cross-family judging.** `baseline-qwen-cross-family` and
  `adversarial`. The three Gemini canonical runs are same-family
  (see Caveats).
- **Fixed ranking judge** (`--ranking-judge-family`). Demonstrated
  on `adversarial` with `claude-haiku-4.5`. Rolling out to all
  candidates is a v1.0.x follow-up.
- **Cross-LLM judge agreement.** Cohen's kappa = 0.443 on
  `adversarial` (`gpt-4o-mini` vs `claude-haiku-4.5`).
- **Camera-channel ablation.** `ablation-no-camera`. The 46.2 pp
  drop from `baseline` is reported in
  [`../../docs/benchmark_notes.md`](../../docs/benchmark_notes.md).
- **Deictic vs named repair anchors.** `baseline-deictic-repair`
  pairs against `baseline` for Turn 3 recovery comparison.
- **Adversarial subset.** 20 distractor-rich scenarios.
- **Variance reporting.** 5 trials per cell, 95% Wilson CIs per
  class, 95% normal-approximation CIs on the balanced mean.
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

### Caveats on published v1 runs

- **Same-family judging on four of five canonical runs.** API
  budget across providers (OpenRouter, OpenAI direct, HF Inference
  Providers Pro) was exhausted mid-effort, leaving Gemini-direct via
  LiteLLM as the only viable transport. Gemini-Flash-Lite judging
  Gemini-Flash-Lite (and Gemini-Flash) admits self-preference bias.
  `baseline-qwen-cross-family` is the cross-family integrity
  reference for the canonical bank.
- **Two model-config families across v1.** Five canonical runs use
  Gemini-direct + DashScope-International transports; `adversarial`
  uses an OpenRouter setup. Each `findings.md` manifest carries
  full identifiers.

### v1.0.x follow-ups

- Re-run the canonical bank with a single fixed ranking judge held
  constant across all candidates so cross-candidate ranking is
  apples-to-apples.
- Re-run `adversarial` under the same Gemini setup as the canonical
  bank so the model-config story across all six runs is consistent.

### v2 follow-ups

- **Human inter-annotator agreement.** v1 reports cross-LLM judge
  agreement only. Human IAA on a 25% sample with Cohen's kappa is
  the highest-priority v2 follow-up.
- **Real-video validation.** The camera channel uses text scene
  descriptions as a stand-in for actual video. Held-out video
  validation on a representative sample is v2 work.
- **Raw-audio validation.** v1 represents the user's spoken turns as
  text transcripts.
- **Beyond-5-trial multi-seed generalization.**
- **Full omnimodal stack** (live audio in, real-time streaming,
  voice-mode output, interruption handling).

For score-interpretation guidance and a longer treatment, see
[`../../docs/benchmark_notes.md`](../../docs/benchmark_notes.md).

## License

MIT, the same as the rest of the repository. See
[`../../LICENSE`](../../LICENSE).
