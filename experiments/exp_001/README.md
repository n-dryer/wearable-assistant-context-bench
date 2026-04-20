# exp_001

`exp_001` is the **v1 runnable slice** of the benchmark. It
implements the **with-prior-Q** variant of the visual-context
selection benchmark defined in
[docs/concept_v0_2.md](../../docs/concept_v0_2.md).

The without-prior-Q variant is part of the official benchmark
definition but is not yet implemented.

## Setup

- **Scenarios**: four two-turn conversations. Turn 1 establishes a
  visual-context reference state. Turn 2 shifts visual context and
  asks an ambiguously-referenced follow-up. Only Turn 2 is scored.
- **Conditions**: three prompt conditions. `baseline` (default
  ranking condition), `condition_a` (policy-selection-neutral
  direct instruction), and `condition_b` (pre-answer scaffold that
  identifies the relevant visual context).
- **Candidate model under test**: configurable via `--model`.
  Defaults to the value in `CONFIG` at the top of `run.py`.
- **Judge**: configurable via `--judge-model` and `--judge-family`
  (default `auto`, cross-family).
- **Trials**: two per `(scenario, condition)` cell, configurable
  via `--trials`.

## Scoring

Judge verdict is primary. The code-based scorer (`core/scoring.py`)
is an audit cross-check. Judge may emit any of four tags
(`current`, `prior`, `clarify`, `abstain`); v1 target policies are
only `prior` or `current`, and `clarify`/`abstain` count as wrong
for the primary score.

## Primary score

**Balanced Turn 2 accuracy** under the ranking condition. See
[docs/concept_v0_2.md](../../docs/concept_v0_2.md#primary-benchmark-score).

## Files

- `scenarios.json`: four scenario definitions with `target_policy`
  and `authoring_basis`.
- `expected_answers.json`: per-scenario `current_answers`,
  `prior_answers`, and clarify/abstain indicators.
- `interventions.json`: the three prompt conditions.
- `run.py`: runner with `--model`, `--judge-model`,
  `--judge-family`, `--trials`, `--output-dir` flags.
- `findings.md`: report output, including the reproducibility
  manifest.

## Running

```bash
python experiments/exp_001/run.py \
    --model <candidate_model_id> \
    --judge-model <judge_model_id>
```

All flags are optional; missing flags fall back to configured
defaults. `--output-dir` governs both transcript artifacts and the
generated findings file for the run.

## Contribution to the frozen v1 set

`exp_001`'s scenarios and answer sets, together with
`.agent-prompts/SCENARIO_SEEDS.md`, form the **frozen v1 with-prior-Q
scenario set**. Future candidate models are evaluated on the same
four scenarios. Extensions happen by creating a new version (v1.1,
v2, etc.) under the governance rule.
