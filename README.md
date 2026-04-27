# Wearable Assistant Context Benchmark

[![tests](https://github.com/n-dryer/wearable-assistant-context-bench/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/n-dryer/wearable-assistant-context-bench/actions/workflows/test.yml)
[![python](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue.svg)](https://www.python.org/downloads/)
[![license](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

[![Wearable Assistant Context Benchmark: six published runs across the Scenario Bank and adversarial pack](docs/og-image.png)](https://n-dryer.github.io/wearable-assistant-context-bench/)

A multimodal AI assistant the user is actively using for advice or
coaching (wearable or handheld, with audio/video/text input and
audio/text output) sees what the user sees and hears what they say.
When the user's situation changes (they swap tools, walk into a new
room), does the assistant follow along, or stay stuck on what was
happening before? **This benchmark scores that.**

## Headline numbers

| Effect | Number |
|---|---|
| Camera input is load-bearing | **60.6% &rarr; 14.4%** when the camera channel is stripped |
| Stuck on the latest frame | **100.0% on `current` / 8.3% on `prior`** (cross-family integrity reference) |
| Bigger sibling, same family | **77.7% vs 60.6%** (Gemini Flash vs Flash-Lite, McNemar p = 0.0012) |
| Cross-LLM judge agreement | Cohen's &kappa; = **0.443** (moderate) on the adversarial pack |

Full leaderboard and per-class breakdown are in [Results](#results).

## Documentation

- **Live results page**: <https://n-dryer.github.io/wearable-assistant-context-bench/>
- **[One-page card (HTML)](docs/benchmark_card.html)**: the polished overview
- **[`docs/benchmark_spec.md`](docs/benchmark_spec.md)**: full benchmark specification
- **[`docs/decisions.md`](docs/decisions.md)**: design tradeoffs
- **[`docs/benchmark_notes.md`](docs/benchmark_notes.md)**: score interpretation and limitations
- **[`benchmark/v1/dataset_card.md`](benchmark/v1/dataset_card.md)**: dataset scope, runs, caveats

## What this benchmark measures

This benchmark measures **context tracking** for multimodal AI
assistants used actively for advice or coaching. Form factors covered
include wearable (smart glasses, ear-worn devices) and handheld
(phone-as-coach apps, AR/MR devices held in hand).

The product problem: a user asks about a hammer, puts it down, picks
up a screwdriver, then asks, "how do I use this?" The assistant
should answer about the screwdriver. Users should not have to keep
restating what they are looking at, holding, or referring to. The
assistant should infer the right reference from the situational cues
already present in the interaction.

The Scenario Bank is **50 scenarios across 8 shift-type categories**:
`object_in_hand`, `object_state`, `sequential_task`, `location`,
`object_in_view`, `absent_referent`, `screen_content`,
`pre_conversation_recall`. Per-category counts are in
[`benchmark/v1/dataset_card.md`](benchmark/v1/dataset_card.md#shift-type-distribution-cue_type).
Each scenario has three turns. Scene descriptions are injected on the
user side as `[Camera: ...]` blocks (the literal field name from the
scenario JSON). Scene descriptions are what a vision system would say
about a video frame: shape, material, color, motion, position, without
naming the object directly. The candidate combines those scene blocks
with deictic user speech and figures out what the question is about.

The judge labels each Turn 2 response as one of `current`, `prior`,
`clarify`, or `abstain`. The primary score is **Balanced Turn 2
accuracy**:

```text
primary_score = mean(current_accuracy, prior_accuracy)
```

The benchmark supports model-selection decisions for deployed
multimodal coaching assistants. In v1, both perceptual channels are
text proxies: spoken turns as text transcripts (not raw audio), and
camera frames as scene descriptions (as a proxy for what a vision
system would say about real video). This isolates context-tracking
ability from variability in the perceptual front-end. See
[`docs/benchmark_spec.md`](docs/benchmark_spec.md#the-three-channel-design)
for the three-channel design and proxy decisions.

## Results

v1 publishes six runs across the Scenario Bank (50 scenarios) and the
adversarial 20-scenario distractor-rich pack. All use 5 trials per
cell and report 95% Wilson CIs per class plus 95%
normal-approximation CIs on the balanced mean. A third pack of 15
ceiling-test scenarios in `scenarios_v2_candidates.json` (all
`difficulty_tier: hard`) is wired via `--pack hard` for users who
want to push frontier models, but no run is published against it
yet.

| Run | Candidate | Judge | Pack | Primary score (95% CI) |
|---|---|---|---|---|
| **baseline** | `gemini-2.5-flash-lite` | `gemini-2.5-flash-lite` (same-family) | Scenario Bank | **60.6%** (54.1&ndash;67.1) |
| **baseline-alt** | `gemini-2.5-flash` | `gemini-2.5-flash-lite` (same-family) | Scenario Bank | **77.7%** (71.3&ndash;84.0) |
| **ablation-no-camera** | `gemini-2.5-flash-lite`, `--no-camera` | `gemini-2.5-flash-lite` | Scenario Bank | **14.4%** (9.1&ndash;19.7) |
| **baseline-qwen-cross-family** | `dashscope-intl/qwen3-vl-plus` | `gemini-2.5-flash-lite` (cross-family) | Scenario Bank | **54.2%** (50.7&ndash;57.7) |
| **baseline-deictic-repair** | `gemini-2.5-flash-lite`, `--repair-style deictic` | `gemini-2.5-flash-lite` | Scenario Bank | **60.6%** (54.1&ndash;67.1) |
| **adversarial** | `gemini-2.5-flash-lite` (OpenRouter) | `gpt-4o-mini` (cross-family); `claude-haiku-4.5` ranking judge | adversarial 20 | **67.3%** (55.5&ndash;79.1) |

Per-class accuracy under `baseline` (full table per run in
`benchmark/v1/runs/<name>/findings.md`):

| Run | `current` | `prior` |
|---|---|---|
| baseline | 87.9% (82.0&ndash;92.0) | 33.3% (22.7&ndash;45.9) |
| baseline-alt | 97.0% (93.1&ndash;98.7) | 58.3% (45.7&ndash;69.9) |
| ablation-no-camera | 12.1% (8.0&ndash;18.0) | 16.7% (9.3&ndash;28.0) |
| baseline-qwen-cross-family | 100.0% (97.7&ndash;100.0) | 8.3% (3.6&ndash;18.1) |
| baseline-deictic-repair | 87.9% (82.0&ndash;92.0) | 33.3% (22.7&ndash;45.9) |
| adversarial | 84.6% (73.9&ndash;91.4) | 50.0% (29.9&ndash;70.1) |

Run-by-run interpretation, statistical analysis (McNemar paired test,
minimum detectable effect, MMStar empirical-difficulty grounding),
and condition-sensitivity findings are in
[`docs/benchmark_notes.md`](docs/benchmark_notes.md#what-the-runs-show).
Score-interpretation guidance is in
[`docs/benchmark_notes.md`](docs/benchmark_notes.md#how-to-read-the-primary-score).

### Reproducing a run

Each leaderboard row corresponds to one of the commands below. The
exact model ids and flags are taken from each run's reproducibility
manifest in `benchmark/v1/runs/<name>/findings.md`. Outputs land in
`benchmark/v1/runs/<name>/`.

```bash
# baseline
python -m benchmark.v1.run \
  --model gemini/gemini-2.5-flash-lite \
  --judge-model gemini/gemini-2.5-flash-lite --judge-family gemini \
  --output-dir benchmark/v1/runs/baseline

# baseline-alt
python -m benchmark.v1.run \
  --model gemini/gemini-2.5-flash \
  --judge-model gemini/gemini-2.5-flash-lite --judge-family gemini \
  --output-dir benchmark/v1/runs/baseline-alt

# ablation-no-camera
python -m benchmark.v1.run \
  --model gemini/gemini-2.5-flash-lite \
  --judge-model gemini/gemini-2.5-flash-lite --judge-family gemini \
  --no-camera \
  --output-dir benchmark/v1/runs/ablation-no-camera

# baseline-qwen-cross-family
python -m benchmark.v1.run \
  --model dashscope-intl/qwen3-vl-plus \
  --judge-model gemini/gemini-2.5-flash-lite --judge-family gemini \
  --output-dir benchmark/v1/runs/baseline-qwen-cross-family

# baseline-deictic-repair
python -m benchmark.v1.run \
  --model gemini/gemini-2.5-flash-lite \
  --judge-model gemini/gemini-2.5-flash-lite --judge-family gemini \
  --repair-style deictic \
  --output-dir benchmark/v1/runs/baseline-deictic-repair

# adversarial
python -m benchmark.v1.run \
  --model openrouter/google/gemini-2.5-flash-lite \
  --judge-model openrouter/openai/gpt-4o-mini --judge-family openai \
  --pack adversarial \
  --ranking-judge-model openrouter/anthropic/claude-haiku-4.5 \
  --ranking-judge-family claude \
  --output-dir benchmark/v1/runs/adversarial
```

### Caveats

- Same-family judging on four of five Scenario Bank runs; API budget
  across non-Gemini providers was exhausted mid-effort, leaving
  `baseline-qwen-cross-family` as the cross-family integrity
  reference for the Scenario Bank.
- Two model-config families across v1 (Gemini-direct +
  DashScope-International for the Scenario Bank, OpenRouter for the
  adversarial run); compare within a single run, or read each
  `findings.md` manifest before comparing across runs.
- `baseline-qwen-cross-family` cannot yet be ranked head-to-head with
  the Gemini Scenario Bank runs; cross-candidate ranking under a
  fixed ranking judge is a v1.0.x follow-up.

Full discussion and limitations are in
[`docs/benchmark_notes.md`](docs/benchmark_notes.md#caveats). Full
transcripts and per-scenario matrices live in
`benchmark/v1/runs/<name>/`.

## How it works

```mermaid
flowchart LR
    Ctx["[Camera: t0 frame]<br/>(optional context_image)"] --> T1["Turn 1<br/>[Camera: t1 frame]<br/>+ user speech"]
    T1 --> Shift["Context shift<br/>(visible only in video)"]
    Shift --> T2["Turn 2<br/>[Camera: t2 frame]<br/>+ user speech"]
    T2 --> Cand["Candidate model"]
    Cand --> Judge["LLM judge<br/>(different family by default)<br/>+ ground truth"]
    Judge --> Label{"Judge label"}
    Label -->|current or prior| Score["Primary score<br/>Balanced Turn 2 accuracy"]
    Label -->|clarify or abstain| Aux["Auxiliary diagnostics"]
```

The candidate sees the audio channel (user speech) and the video
channel (scene descriptions). The judge also receives a ground-truth
section that names the actual objects in Turn 1 and Turn 2; the
candidate never sees that. Each scenario runs under three system
prompts (the neutral `baseline` plus `condition_a` and `condition_b`,
two nudge variants) at temperature 0. Turn 3 fires only after a
Turn 2 miss and feeds the repair rate.

For what is out of scope by design (advice quality, multi-turn
dynamics beyond Turn 2, proactive coaching, domain depth, latency,
cost, raw-audio perception, long-horizon memory), see
[`docs/benchmark_notes.md`](docs/benchmark_notes.md#what-this-benchmark-does-not-measure).
A model that fails this benchmark cannot serve as an in-the-moment
multimodal assistant. A model that passes still needs separate
evaluation for the items in that list.

## Quickstart

```bash
git clone https://github.com/n-dryer/wearable-assistant-context-bench.git
cd wearable-assistant-context-bench
./scripts/setup.sh
. .venv/bin/activate

# Verify the repo without API access (stubs both candidate and judge):
python -m pytest tests/ -q
python scripts/validate_scenarios.py

# Run the benchmark against a real model (requires API keys, see below):
cp .env.example .env  # then fill in keys
python -m benchmark.v1.run --model <candidate_model_id>
```

`scripts/setup.sh` sets up the venv with pinned dependencies, then
downloads the spaCy `en_core_web_sm` model that the validator and
scoring code path need. Override the Python interpreter with
`PYTHON=python3.13 ./scripts/setup.sh` if you need a specific
version.

## API keys

Requires Python 3.11+. Set the API keys you need for the candidate
and judge models you plan to run:

- `ANTHROPIC_API_KEY`
- `GEMINI_API_KEY` or `GOOGLE_API_KEY`
- `OPENAI_API_KEY`
- `OPENROUTER_API_KEY`
- `HF_TOKEN` (and `HUGGINGFACE_API_KEY` as a fallback name) for
  Hugging Face Inference Providers

An example environment file is provided in
[`.env.example`](.env.example). To run open-weights multimodal
candidates via HF Inference Providers, see
[`docs/running_open_weights.md`](docs/running_open_weights.md).

## Run the benchmark

```bash
python -m benchmark.v1.run \
  --model <candidate_model_id> \
  --judge-model <judge_model_id>
```

Optional flags:

- `--judge-family auto|claude|gemini|openai`: judge family override.
  Default is `auto`, which picks a different family than the candidate.
- `--trials <int>`: trials per (scenario, condition) cell. Default is 5.
- `--output-dir <path>`: output directory. Default is
  `benchmark/v1/runs/latest/`.

The runner writes `transcripts.jsonl` and `findings.md` (which
includes a reproducibility manifest as a JSON block) into the output
directory.

## Verify the repo

```bash
python -m pytest tests/ -q
python scripts/validate_scenarios.py
```

The test suite stubs candidate models and the judge so the runtime
tests work without API access. The validator script runs four
programmatic checks (token leakage, object-name leakage, schema
validation, cross-scenario duplication) over the scenario bank.

## How the judge works

A second model labels each Turn 2 response with one of `current`,
`prior`, `clarify`, or `abstain`. By default, `--judge-family auto`
picks a different family than the candidate (Claude &rarr; Gemini,
Gemini &rarr; OpenAI, OpenAI &rarr; Gemini) to reduce
self-preference bias. For cross-candidate ranking, configure a fixed
ranking judge with `--ranking-judge-family`; each trial then carries
both verdicts and Cohen's kappa is reported. The judge sees the same
audio and video channels as the candidate plus a ground-truth section
naming the actual objects in frame; it does not see `target_context`,
`cue_type`, or authoring `notes`. The privileged-field constraint is
enforced by
[`tests/test_judge_prompt_constraints.py`](tests/test_judge_prompt_constraints.py).

Full design rationale (why two layers, why cross-family by default)
is in
[`docs/decisions.md`](docs/decisions.md#why-cross-family-judging-by-default--a-fixed-ranking-judge).

## Repository layout

- [`benchmark/v1`](benchmark/v1): scenario bank, runner, and run
  outputs
- [`core`](core): model adapters, judge logic, scoring, report
  generation
- [`docs/benchmark_spec.md`](docs/benchmark_spec.md): full benchmark
  specification
- [`docs/schema.md`](docs/schema.md): scenario field reference
- [`docs/scenario_authoring_rules.md`](docs/scenario_authoring_rules.md):
  authoring rules and validation checklist
- [`docs/benchmark_notes.md`](docs/benchmark_notes.md): score
  interpretation and limitations
- [`docs/running_open_weights.md`](docs/running_open_weights.md):
  HF Inference Providers candidate setup
- [`tests`](tests): runtime and input-validation tests
- [`scripts/validate_scenarios.py`](scripts/validate_scenarios.py):
  programmatic checks against the scenario bank

## Contributing

Edits to scenario text, answer keys, prompt text, or scoring semantics
are out of scope once the `v1.0.0` release tag is created. Bug fixes
and new model adapters are welcome at any time, as are doc and
reproducibility improvements. See
[`CONTRIBUTING.md`](CONTRIBUTING.md) for the full policy.

## Maintainer

Nate Dryer ([@n-dryer](https://github.com/n-dryer)).

## License

Released under the MIT License. See [LICENSE](LICENSE).

## Citation

If you reference this benchmark, use the citation metadata in
[CITATION.cff](CITATION.cff).
