# exp_001

`exp_001` is the **v1 runnable slice** of the benchmark. It
implements the **with-prior-Q** variant of the visual-context
selection benchmark defined in
[docs/concept_v0_2.md](../../docs/concept_v0_2.md).

The without-prior-Q variant is part of the official benchmark
definition but is not yet implemented.

## Setup

- **Scenarios**: 11 two-turn conversations. Turn 1 establishes a
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

- `scenarios.json`: 11 scenario definitions with `target_context`
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

## Per-scenario cue types

Each v1 scenario exercises a dominant cue family. The cue axis is
descriptive (it does not enter scoring) but is documented so
readers can see the construct coverage of the set at a glance.

| Scenario | target\_context | Dominant cue family          | One-line framing                                |
|----------|----------------|-------------------------------|-------------------------------------------------|
| sc-01    | current        | Object-reference shift        | Put down screwdriver, picked up wrench          |
| sc-02    | current        | Spatial / scene shift         | Walked from bedroom to kitchen                  |
| sc-03    | prior          | Verbal / deictic (reach-back) | Back at front desk, asking about library book   |
| sc-04    | current        | Spatial / scene shift         | Walked from desk to kitchen                     |
| sc-05    | current        | Object-reference shift        | Held up second poster after first                |
| sc-06    | current        | Spatial / scene shift         | Walked from garden to garage                    |
| sc-07    | current        | Temporal / same-scene state   | Same office 15 minutes later                    |
| sc-08    | current        | Object-reference shift (UI)   | Switched windows on the monitor                 |
| sc-09    | prior          | Object departure (reach-back) | Buck bolted; asking direction                   |
| sc-10    | current        | Spatial / scene shift         | Walked from holiday stock to chardonnay pallet  |
| sc-11    | prior          | Object return (reach-back)    | Put item back on shelf; asking about it         |

Rows labeled "reach-back" are the items that defend against the
latest-mention heuristic. See
[docs/limitations.md](../../docs/limitations.md#latest-mention-heuristic-caveat).

## Contribution to the frozen v1 set

`exp_001`'s scenarios and answer sets, together with
`.agent-prompts/SCENARIO_SEEDS.md`, form the **frozen v1 with-prior-Q
scenario set** (11 scenarios: 8 `current`, 3 `prior`). Future
candidate models are evaluated on the same 11 scenarios. Extensions
happen by creating a new version (v2, etc.) under the
governance rule.
