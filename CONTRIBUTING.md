# Contributing

Thanks for your interest in this benchmark.

The current public v1 release is intentionally narrow and frozen in
meaning so model runs stay comparable.

## What is welcome

- bug fixes in the runner, adapters, judge, scoring, or report
- new candidate-model adapter support that preserves benchmark semantics
- documentation improvements, typo fixes, and broken-link fixes
- test coverage for existing behavior
- reproducibility improvements such as better manifest fields, cache
  hygiene, or run-output clarity

## What is out of scope for canonical v1

Canonical v1 is frozen in the following areas:

- edits to `benchmark/v1/scenarios.json`
- edits to `benchmark/v1/expected_answers.json`
- edits to `benchmark/v1/interventions.json`
- changes to the judge label set
- changes to the primary scoring rule
- changes to the default comparison condition

Those changes would alter benchmark meaning and should be treated as a
new benchmark-release discussion, not an in-place edit to canonical v1.

## Workflow

1. Open an issue first for non-trivial changes.
2. Fork and branch from `main`.
3. Run the test suite locally:

   ```bash
   python -m pytest tests/ -q
   ```

4. Keep commits atomic and write descriptive commit messages.
5. Open a pull request against `main`.

## Code style

- Python 3.11+ with type hints on every public function
- docstrings on every public function and module-level docstrings on
  files in `core/` and `benchmark/`
- dataclasses for structured payloads where they improve readability
- no bare `except:` clauses
- preserve the runner CLI contract unless a change is explicitly needed

## Reporting issues

When filing a runner or judge bug, include:

- the exact CLI invocation
- the manifest block from `findings.md`, or the full file
- the candidate model and judge model IDs
- the Python version
