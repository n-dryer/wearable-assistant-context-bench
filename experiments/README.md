# Experiments

Each subdirectory is a self-contained slice of the visual-context
selection benchmark, with its own scenarios, intervention
conditions, scoring inputs, and findings.

## Directory conventions

Each experiment directory contains:

- `scenarios.json`: pinned scenario definitions for this slice
- `expected_answers.json`: pinned answer lists used by the code
  scorer and judge (`current_answers`, `prior_answers`,
  `clarify_indicators`, `abstain_indicators`)
- `interventions.json`: pinned intervention conditions
- `run.py`: runner with `--model`, `--judge-model`,
  `--judge-family`, `--trials`, `--output-dir` flags
- `findings.md`: report output, including the reproducibility
  manifest
- `transcripts/`: per-trial transcript artifacts written by the
  runner

Once a version result is recorded, inputs stay pinned. New slices
or extensions go in a new experiment directory or a new version
extension under the governance rule in
[../docs/concept_v0_2.md](../docs/concept_v0_2.md).

## Experiments in this repository

- `exp_001/`: **v1 runnable slice** of the benchmark. Covers the
  with-prior-Q variant. See
  [experiments/exp_001/README.md](exp_001/README.md).

Planned benchmark extensions (including the without-prior-Q
variant) are tracked in
[../docs/deferred_roadmap.md](../docs/deferred_roadmap.md).
