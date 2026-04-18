# Project Context: Grounding Evals

## What This Project Is

A prompt sensitivity evaluation framework for live-assistant AI products.
It tests whether prompt and scaffolding changes fix specific known
failure patterns from pilot feedback on a wearable camera product
(anonymized).

## Core Methodology

- 8 scenarios, each a 2-turn conversation (Turn 1: initial state plus
  question. Turn 2: state change plus follow-up question)
- Only Turn 2 is scored; Turn 1 establishes the context that Turn 2 state
  change overrides
- 3 intervention conditions: baseline, direct instruction (Condition A),
  pre-answer scaffold (Condition B)
- 1 model tested: Claude Sonnet 4.6 (the model under test, not the judge)
- 2 trials per condition at temperature=0
- Total runs: 8 scenarios x 3 conditions x 2 trials x 2 turns per
  conversation = 96 main calls, plus 48 judge calls on Turn 2 only = 144
  total API calls

## Tech Stack

- Python 3.11+
- anthropic Python SDK for both model under test and judge
- spaCy for entity extraction in scoring
- rapidfuzz for fuzzy answer matching
- pytest for testing

## File Organization

- `core/`: reusable scoring, judge, model adapter, intervention loader, report generator
- `experiments/exp_001/`: scenario definitions, runner, findings, transcripts
- `docs/`: methodology, limitations, incident classes, interventions, related work, deferred roadmap
- `.agent-prompts/`: input files for the agent build (INCIDENT_CLASSES.md, INTERVENTIONS.md, SCENARIO_SEEDS.md)
- `tests/`: unit tests for scoring, interventions, models

## Principles This Project Follows

- Honesty over novelty. The framework's novel application is
  pilot-derived scenarios and intervention comparison. The underlying
  methodology (hybrid scoring, LLM-as-judge) is standard.
- Clarity over cleverness. Prefer explicit loops to clever abstractions.
  The runner loop should be readable by a PM, not just an ML engineer.
- Scope discipline. v0.1 is intentionally small. Any feature not in the
  plan goes in docs/deferred_roadmap.md, not in the code.
- Version pinning. Model version strings go in config, never inline in
  code. This lets future runs be reproducible.

## Code Style

- Python: type hints everywhere; docstrings on every public function
- No bare `except:` clauses; catch specific exceptions
- Dataclasses for structured data, not raw dicts
- JSON schemas documented in dataclass docstrings
- Constants (temperature=0, trial count, etc.) live in a single config
  dict at the top of run.py
