# Wearable Assistant Context Benchmark

[![tests](https://github.com/n-dryer/wearable-assistant-context-bench/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/n-dryer/wearable-assistant-context-bench/actions/workflows/test.yml)
[![python](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue.svg)](https://www.python.org/downloads/)
[![license](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

[![Wearable Assistant Context Benchmark: 70 scenarios and six published runs](docs/og-image.png)](https://n-dryer.github.io/wearable-assistant-context-bench/)

A model-selection benchmark for live AI wearable assistants.

Wearable assistants need to keep up while a user talks and moves. A user might ask about a tool, look at a screen, walk to another place, or pick up a different object without explaining the change out loud. The assistant should actively use the latest audio, video, and text context, so the user does not have to narrate every shift.

This benchmark tests one part of that problem: context tracking — whether a model can answer the next question using the scene the user means now. In benchmark terms, it tests cross-turn multimodal reference resolution.

v1 uses text as a proxy for real video and live audio. Spoken turns are represented as transcripts. Video frames are represented as written scene descriptions. A planned next version will add real video scenarios, so the same reference-tracking task can be tested with visual input directly.

Use the score as one signal when comparing models for wearable assistant products. It does not test the full device experience.

## Quick links

| Need | Start here |
|---|---|
| View the project dashboard and published results | [Project dashboard](https://n-dryer.github.io/wearable-assistant-context-bench/) |
| Interpret scores | [`docs/benchmark_notes.md`](docs/benchmark_notes.md) |
| Reproduce v1 runs | [`benchmark/v1/dataset_card.md`](benchmark/v1/dataset_card.md#reproducing-the-v1-runs) |
| Read the benchmark design | [`docs/benchmark_spec.md`](docs/benchmark_spec.md) |
| Configure API keys | [`docs/api_keys.md`](docs/api_keys.md) |
| Run open-weight models | [`docs/running_open_weights.md`](docs/running_open_weights.md) |
| Report an issue | [GitHub Issues](https://github.com/n-dryer/wearable-assistant-context-bench/issues) |

## Published results

v1 includes six published runs.

- Five runs use the 50-scenario Scenario Bank.
- The `adversarial` run uses a separate 20-scenario pack where earlier objects or scenes may still be visible.

The primary score is Balanced Turn 2 accuracy. It averages two checks: how often the model answers correctly when the new scene matters, and how often it avoids switching when the earlier context is still the right answer.

The strongest published Scenario Bank result is `baseline-alt`, with a **77.7%** primary score. Without the camera channel, the same base model scores **14.4%**. That drop is the simplest check that the task depends on visual context.

| Run | Candidate | Judge | Primary score (95% CI) |
|---|---|---|---|
| **baseline** | `gemini-2.5-flash-lite` | `gemini-2.5-flash-lite` (same-family) | **60.6%** (54.1&ndash;67.1) |
| **baseline-alt** | `gemini-2.5-flash` | `gemini-2.5-flash-lite` (same-family) | **77.7%** (71.3&ndash;84.0) |
| **ablation-no-camera** | `gemini-2.5-flash-lite` with `--no-camera` | `gemini-2.5-flash-lite` | **14.4%** (9.1&ndash;19.7) |
| **baseline-qwen-cross-family** | `dashscope-intl/qwen3-vl-plus` | `gemini-2.5-flash-lite` (cross-family) | **54.2%** (50.7&ndash;57.7) |
| **baseline-deictic-repair** | `gemini-2.5-flash-lite` with `--repair-style deictic` | `gemini-2.5-flash-lite` | **60.6%** (54.1&ndash;67.1) |
| **adversarial** | `gemini-2.5-flash-lite` (OpenRouter) | `gpt-4o-mini` (cross-family); `claude-haiku-4.5` ranking judge | **67.3%** (55.5&ndash;79.1) |

More detail:

- New-scene and earlier-scene accuracy: [`benchmark/v1/dataset_card.md`](benchmark/v1/dataset_card.md#per-class-accuracy)
- Score interpretation: [`docs/benchmark_notes.md`](docs/benchmark_notes.md)
- Reproduction commands: [`benchmark/v1/dataset_card.md`](benchmark/v1/dataset_card.md#reproducing-the-v1-runs)

## Quickstart

Requires Python 3.11+. You can use [`uv`](https://docs.astral.sh/uv/) for dependency and environment management.

### Install and verify

```bash
git clone https://github.com/n-dryer/wearable-assistant-context-bench.git
cd wearable-assistant-context-bench

uv venv
source .venv/bin/activate
uv pip install -e .

pytest tests/ -q
```

If you prefer standard pip, run `./scripts/setup.sh` instead of the `uv` commands.

The test suite does not require API access.

### Configure API keys

Copy the example environment file, then add your provider keys:

```bash
cp .env.example .env
```

See [`docs/api_keys.md`](docs/api_keys.md) for provider-specific setup.

### Run a candidate model

```bash
python -m benchmark.v1.run --model <candidate_model_id>
```

For exact commands used in the published runs, see [`benchmark/v1/dataset_card.md`](benchmark/v1/dataset_card.md#reproducing-the-v1-runs).

For open-weight Hugging Face models, see [`docs/running_open_weights.md`](docs/running_open_weights.md).

### Common commands

```bash
# Run tests
python -m pytest tests/ -q

# Validate scenarios
python scripts/validate_scenarios.py

# Show runner options
python -m benchmark.v1.run --help
```

## Benchmark design

This section explains what the benchmark sends to the model, how the scenarios work, and how responses are scored.

### Inputs in v1

v1 does not use raw audio or raw video.

- Audio is represented as text transcripts.
- Video is represented as written scene descriptions.

The next version is planned to include real-video test scenarios. The goal is to keep the same reference-tracking task while testing whether models can read the visual scene directly.

For the full input design, see [`docs/benchmark_spec.md`](docs/benchmark_spec.md#the-three-channel-design).  
For limits of the benchmark, see [`docs/benchmark_notes.md`](docs/benchmark_notes.md#what-this-benchmark-does-not-measure).

### Evaluation flow

```mermaid
flowchart LR
    Ctx["Optional starting scene"] --> T1["Turn 1: scene description + user speech"]
    T1 --> Shift["Visible scene change"]
    Shift --> T2["Turn 2: new scene description + user speech"]
    T2 --> Cand["Candidate model"]
    Cand --> Judge["LLM judge + answer key"]
    Judge --> Label{"Judge label"}
    Label -->|current or prior| Score["Primary score"]
    Label -->|clarify or abstain| Aux["Reported separately"]
```

### Scenarios and packs

Each scenario is a three-turn conversation. Between Turn 1 and Turn 2, the user changes what they are holding, viewing, doing, or referring to. The user does not spell out the change. The model has to answer the Turn 2 question using the scene the user means at that moment.

The scene descriptions include visible details such as shape, material, color, motion, and position. They avoid naming the object directly.

| Pack | Size | Purpose | Status |
|---|---:|---|---|
| Scenario Bank | 50 scenarios | Main v1 benchmark across 8 shift types | Published |
| Adversarial | 20 scenarios | Harder cases where the earlier object or scene may still be visible | Published |
| Hard candidates | 15 scenarios | Hard cases for testing stronger models | Wired via `--pack hard`; no published run yet |

The Scenario Bank covers 8 shift types: `object_in_hand`, `object_state`, `sequential_task`, `location`, `object_in_view`, `absent_referent`, `screen_content`, and `pre_conversation_recall`.

For category counts, scenario fields, and authoring rules, see the [dataset card](benchmark/v1/dataset_card.md#shift-type-distribution-cue_type), [schema](docs/schema.md), and [authoring rules](docs/scenario_authoring_rules.md).

### Scoring and judging

Each scenario is scored on Turn 2, after the scene changes.

| Label | Meaning |
|---|---|
| `current` | The response answers using the new scene |
| `prior` | The response answers using the earlier scene |
| `clarify` | The response asks for clarification instead of answering |
| `abstain` | The response avoids answering |

The primary score measures whether the model can separate the new scene from the earlier scene. `clarify` and `abstain` are counted separately.

```text
primary_score = mean(current_accuracy, prior_accuracy)
```

By default (`--judge-family auto`), the judge comes from a different model family than the candidate. This reduces the risk that a model family favors its own outputs. To rank candidates directly against each other, add `--ranking-judge-family` for one judge held constant across all of them.

Full rationale: [`docs/decisions.md`](docs/decisions.md#why-cross-family-judging-by-default--a-fixed-ranking-judge).

## Code layout

| Path | Purpose |
|---|---|
| [`benchmark/v1`](benchmark/v1) | Scenarios, runner, and run outputs |
| [`core`](core) | Model adapters, judge, scoring, and reports |
| [`tests`](tests) | Runtime and input-validation tests |
| [`scripts/validate_scenarios.py`](scripts/validate_scenarios.py) | Scenario validator |
| [`.env.example`](.env.example) | Environment variable template |

## Contributing and support

Edits to scenario text, answer keys, prompt text, or scoring semantics are out of scope once the `v1.0.0` release tag is created.

Bug fixes, new model adapters, documentation fixes, and reproducibility improvements are welcome through issues and pull requests.

For bugs, failed reproduction attempts, or unclear documentation, open a GitHub issue with the command you ran, the model or provider used, and the relevant error output.

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the full policy.

## Maintainer

Nate Dryer ([@n-dryer](https://github.com/n-dryer)).

## License

Released under the MIT License. See [LICENSE](LICENSE).

## Citation

If you reference this benchmark, use the citation metadata in [CITATION.cff](CITATION.cff) or copy the BibTeX entry below.

```bibtex
@software{dryer_wearable_assistant_context_benchmark_2026,
  author = {Dryer, Nate},
  title = {{Wearable Assistant Context Benchmark}},
  year = {2026},
  url = {https://github.com/n-dryer/wearable-assistant-context-bench},
  version = {1.0.0},
  license = {MIT}
}
```
