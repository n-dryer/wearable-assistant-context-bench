# Wearable Assistant Context Benchmark

**A benchmark for implicit context tracking in mobile multimodal assistants.**

This repository contains the **v1 runnable slice** of the benchmark. v1 scores one
sub-capability: **reference-state selection under implicit context shift**.
Given a two-turn conversation where the visual context changes between turns,
does the model anchor its Turn 2 answer to the **prior** visual context or the
**current** one?

The benchmark identity is broader than this slice. Object recognition is
assumed and out of scope. v1 focuses on the context-selection decision itself.

Example: Turn 1 asks about a screwdriver. Turn 2 asks, "am I holding this
correctly?" after the user has picked up a hammer. The benchmark checks whether
the answer follows the hammer in hand now or the screwdriver from a moment ago.

See [docs/benchmark_spec.md](docs/benchmark_spec.md) for the canonical spec and
[docs/benchmark_card.html](docs/benchmark_card.html) for the one-page summary.

## What v1 includes

- **11 frozen scenarios**
- **3 intervention conditions**: `baseline`, `condition_a`, `condition_b`
- **2 trials per (scenario, condition) cell** by default
- **Turn 2 scoring only**
- **Balanced Turn 2 accuracy** as the primary ranking metric
- **Cross-family LLM judge** by default through `--judge-family auto`
- **Reproducibility manifest** emitted with each run

v1 implements the **with-prior-Q** variant, where Turn 1 establishes the
referent before the ambiguous follow-up. A later slice will add
**without-prior-Q** coverage, where no earlier question created that anchor.

## Repository layout

- [docs/benchmark_spec.md](docs/benchmark_spec.md): canonical benchmark spec
- [docs/benchmark_card.html](docs/benchmark_card.html): one-page benchmark card
- [benchmark/v1](benchmark/v1): runnable slice inputs and runner
- [core](core): adapters, judge, scoring, report generation
- [tests](tests): verification for runtime behavior and benchmark inputs

## Install

Requires Python 3.11+.

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

Set API keys as needed:

- `ANTHROPIC_API_KEY` for Claude-family candidate or judge models
- `OPENAI_API_KEY` for OpenAI-family candidate or judge models
- `GEMINI_API_KEY` or `GOOGLE_API_KEY` for Gemini-family candidate or judge models

An example environment file is provided in [.env.example](.env.example).

## Run the benchmark

```bash
python -m benchmark.v1.run \
  --model <candidate_model_id> \
  --judge-model <judge_model_id>
```

Optional flags:

- `--judge-family auto|claude|openai|gemini`
- `--trials <int>`
- `--output-dir <path>`

With no `--output-dir`, the runner writes transcripts, findings, and the
manifest to `benchmark/v1/runs/latest/`.

## Verify the repo

```bash
python -m pytest tests/ -q
```

The test suite runs without real API keys by stubbing candidate models and the
judge.

## How to read the primary score

The v1 primary score is **balanced Turn 2 accuracy under the ranking
condition**. Balanced means the mean of per-class accuracy across the two
scored classes, `prior` and `current`.

This keeps the current-heavy v1 class mix from dominating the score.
`baseline` is the default ranking condition for model selection.
`condition_a` and `condition_b` remain diagnostic.

## Citation

Internal-use benchmark, no DOI. Cite the repo URL and exact release tag, then
include the candidate model, judge model, ranking condition, and trial count
from the manifest.
