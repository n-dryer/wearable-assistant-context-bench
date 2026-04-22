# Contributing

Thanks for your interest in this benchmark. The scope below reflects
that v1 is intentionally small and frozen so that runs across model
releases stay comparable.

## What is welcome

- Bug fixes in the runner, adapters, judge, scoring, or report.
- New candidate-model adapters that conform to the existing
  `core/models.py` and `core/gemini_adapter.py` shape.
- Documentation improvements: clarifications, typo fixes, broken
  links, additional reading guidance.
- Test coverage for existing behavior.
- Reproducibility improvements: tighter manifest fields, better
  cache hygiene, clearer run output.

## What is out of scope for v1

v1 is **frozen**. The following changes do not land in v1 because they
would break run-over-run comparability:

- Edits to scenarios in `benchmark/v1/scenarios/`.
- Edits to expected-answer lists, the four-policy taxonomy, or the
  judge system prompt.
- Edits to `benchmark/v1/interventions.json` or the conditions list.
- Changes to the primary scoring rule (balanced Turn 2 accuracy).
- Changes to the trial count, temperature, or ranking-condition
  default.

Ideas in those areas belong in `docs/deferred_roadmap.md` or in a new
versioned slice (e.g. `benchmark/v2/`).

## Workflow

1. Open an issue first for non-trivial changes so we can confirm the
   change fits the scope above.
2. Fork and branch from `main`.
3. Run the test suite locally:

   ```bash
   python -m pytest tests/ -q
   ```

4. Keep commits atomic and write descriptive commit messages.
5. Open a pull request against `main`.

## Code style

- Python 3.11+ with type hints on every public function.
- Docstrings on every public function. Module-level docstrings on
  every file in `core/` and `benchmark/`.
- Dataclasses for structured payloads.
- No bare `except:` clauses.
- Constants live in a single config dict at the top of the runner,
  not inline in code.

## Reporting issues

When filing a runner or judge bug, please include:

- The exact CLI invocation.
- The contents of `manifest` from `findings.md` (or attach the file).
- The candidate model and judge model IDs.
- The Python version.
