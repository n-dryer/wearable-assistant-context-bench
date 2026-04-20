# Project Context: Grounding Evals

## What This Project Is

An **internal visual-context selection benchmark** for a wearable
live-assistant camera product. It measures whether a candidate
model picks the right visual context (prior frame vs. current
frame) when answering a question. Object recognition is assumed;
the benchmark scores the context-selection decision and is used
internally to compare candidate model releases for shipping.

The repo is public so readers can inspect benchmark design; the
benchmark itself is internal-use. It is not a paper or a public
leaderboard.

## Core Methodology

- 4 corpus-backed scenarios in the frozen v1 set (3 `current`, 1
  `prior`), each a 2-turn conversation. Turn 1 establishes the
  visual-context reference state. Turn 2 shifts visual context
  and asks an ambiguously-referenced follow-up. Turn 3 fires only
  on Turn 2 failure as a templated "I mean, ..." repair anchor.
- Only Turn 2 is scored. Turn 3 feeds the simulated repair rate.
- 3 intervention conditions: `baseline` (default ranking
  condition), `condition_a` (policy-selection-neutral direct
  instruction), `condition_b` (pre-answer scaffold identifying
  the relevant visual context).
- 2 trials per (scenario, condition) cell at temperature=0.
- Primary score: **balanced Turn 2 accuracy** under the ranking
  condition. `clarify`/`abstain` trials count as wrong for the
  primary score and render as diagnostic rows in the report.

## Tech Stack

- Python 3.11+
- `anthropic` Python SDK for the Claude judge and Claude candidate
  models
- `openai` Python SDK for the OpenAI judge path
- `spaCy` for entity extraction in scoring
- `rapidfuzz` for fuzzy answer matching
- `pytest` for testing

Default judge family is `auto`: the runner infers the candidate
family from `--model` and assigns a different-family judge. The
`auto` path requires either `ANTHROPIC_API_KEY` or `OPENAI_API_KEY`
depending on the resolved judge family. Explicit
`--judge-family claude|openai` overrides.

## File Organization

- `core/`: scoring, judge adapter, model adapter, intervention
  loader, report generator
- `experiments/exp_001/`: scenario definitions, runner, findings,
  transcripts (v1 runnable slice)
- `docs/`: `concept_v0_2.md`, `methodology.md`, `limitations.md`,
  `interventions.md`, `related_work.md`, `deferred_roadmap.md`
- `.agent-prompts/`: authoring inputs (PILOT_CORPUS_INVENTORY,
  FAILURE_MODES, INTERVENTIONS, SCENARIO_SEEDS)
- `tests/`: unit tests

## Principles This Project Follows

- Honesty over novelty. The novel contribution is a pilot-anchored
  visual-context selection benchmark with a frozen v1 set. Hybrid
  scoring and LLM-as-judge are standard.
- Clarity over cleverness. The runner loop is prose-readable.
- Scope discipline. v1 is intentionally small and frozen. New
  work goes in `docs/deferred_roadmap.md` or in a new version
  extension, not into v1.
- Version pinning. Model strings go in config or via CLI flags,
  never inline in code. Every run emits a reproducibility
  manifest with model strings, scenario/intervention/judge-prompt
  SHAs, trials, temperature, and the ranking condition.

## Code Style

- Python: type hints everywhere; docstrings on every public
  function.
- No bare `except:` clauses; catch specific exceptions.
- Dataclasses for structured data, not raw dicts.
- JSON schemas documented in dataclass docstrings.
- Constants (temperature=0, trial count, model strings) live in
  a single config dict at the top of `run.py`.
