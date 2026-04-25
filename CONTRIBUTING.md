# Contributing

Thanks for your interest in this benchmark.

## Scope

This benchmark tests whether multimodal assistants update to current
context instead of staying anchored to prior context. It is narrow on
purpose. Contributions that fit that scope are welcome. Contributions
that broaden the benchmark into general assistant evaluation, coaching
quality, or domain expertise are not.

## Release policy

Once the `v1.0.0` release tag is created, the following stay stable
across patch releases so cross-model comparisons remain valid:

- `benchmark/v1/scenarios.json` — scenario text
- `benchmark/v1/expected_answers.json` — answer keys
- `benchmark/v1/interventions.json` — prompt conditions
- The four judge labels (`current`, `prior`, `clarify`, `abstain`)
- The primary scoring rule (balanced accuracy across `current` and
  `prior` under `baseline`)
- The default comparison condition (`baseline`)

Edits that change scenario meaning, answer-key vocabulary, prompt
text, or scoring semantics are out of scope after the tag. Those
changes would alter benchmark comparability and would require a new
benchmark release rather than an in-place edit.

## What is welcome at any time

- Bug fixes in the runner, adapters, judge, scoring, or report
- New candidate-model adapter support that preserves benchmark
  semantics
- Documentation improvements, typo fixes, broken-link fixes
- Test coverage for existing behavior
- Reproducibility improvements (better manifest fields, cache hygiene,
  run-output clarity)
- Validator improvements (new programmatic checks, better diagnostics)

## How to add a new model adapter

Adapters live in [`core/`](core). The existing examples are:

- `core/models.py` — Claude adapter
- `core/gemini_adapter.py` — Gemini adapter
- `core/litellm_adapter.py` — LiteLLM-backed adapter for OpenAI-family
  and provider-qualified model IDs

Each adapter exposes a `query(messages, system, config)` method
returning a string. To add a new adapter:

1. Implement the adapter in a new module under `core/`.
2. Add tests under `tests/` that stub the underlying client and
   exercise the adapter contract (the existing adapter tests are
   templates).
3. Update `_build_adapter` in `benchmark/v1/run.py` to dispatch to the
   new family.
4. Update `infer_candidate_family` and the cross-family map in
   `core/llm_judge.py` if the new family should participate in
   `--judge-family auto` resolution.

If your adapter is for a routing layer that supports multiple
families (like LiteLLM), keep family detection in
`infer_candidate_family` and reuse the existing `LiteLLMJudgeAdapter`.

## How to write a scenario

Scenarios are written from scratch following the rules in
[`docs/scenario_authoring_rules.md`](docs/scenario_authoring_rules.md).
That document is the source of truth for the audio, camera, and
ground-truth channel rules, and it includes the full validation
checklist.

Quick summary:

- **Audio channel** (user speech): natural and deictic. No object
  names, no property descriptions, no shift announcements, no answer
  vocabulary.
- **Camera channel** (image descriptions): scene-level features
  only. No object names, no functional labels, no technique
  evaluation. Detailed enough that a fresh reader can identify the
  object with high confidence.
- **Ground truth channel** (answer keys): judge-only. Object names
  permitted. Each `current_answers` and `prior_answers` list must
  cover three vocabulary categories: object name, technique vocabulary,
  state descriptors.

After the `v1.0.0` tag, new scenarios are not accepted into the
v1 scenario bank. Authoring rules remain published as a contributor
reference and as documentation for future benchmark releases.

## Validation

Before submitting any change to scenarios or answer keys, run:

```bash
python scripts/validate_scenarios.py
```

This runs four programmatic checks (token leakage, object-name
leakage, schema validation, cross-scenario duplication) over the
scenario bank. The semantic checks (human identification of image
descriptions, semantic-leakage isolation test) are LLM-driven and run
during scenario authoring; CI runs the four programmatic checks.

The full 10-point validation checklist is in
[`docs/scenario_authoring_rules.md`](docs/scenario_authoring_rules.md).

## Test requirements

Every PR must pass:

```bash
python -m pytest tests/ -q
python scripts/validate_scenarios.py
```

The test suite stubs candidate models and the judge so it works
without API access. CI runs both commands on every PR.

## Code style

- Python 3.11+ with type hints on every public function
- Docstrings on every public function and module-level docstrings on
  files in `core/` and `benchmark/`
- Dataclasses for structured payloads where they improve readability
- No bare `except:` clauses
- Preserve the runner CLI contract unless a change is explicitly
  needed and reviewed

## PR process

1. Open an issue first for non-trivial changes.
2. Fork and branch from `main`.
3. Make your change. Keep commits atomic and descriptive.
4. Run the full test suite and the validator locally.
5. Open a pull request against `main` and reference the issue.
6. CI must pass before review.

When reporting a runner or judge bug, include:

- The exact CLI invocation
- The manifest block from `findings.md`, or the full file
- The candidate model and judge model IDs
- The Python version
