# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- Renamed `data/scenarios.jsonl` → `data/wacb.jsonl` to match the
  benchmark short-form filename convention used by HumanEval
  (`HumanEval.jsonl`) and TruthfulQA (`TruthfulQA.csv`). The prose term
  "scenario" is unchanged; the manifest lockfile does not need
  regeneration because `scenarios_sha256` hashes content, not paths.

## [0.1.0] - 2026-05-01

Initial public pre-release.

### Added

- Single Python package `wearable_assistant_context_bench/` with the runner,
  adapters (Gemini, LiteLLM), LLM-judge, scoring, report, and statistics modules.
- 70-scenario corpus split into `bank` (50) and `contrast` (20) subsets.
- `wac-bench` console script (`pyproject.toml` `[project.scripts]`).
- Per-run artifacts: `transcripts.jsonl`, `findings.md`, `summary.json`.
- Six published baseline runs under `runs/`.
- Reproducibility manifest at `data/MANIFEST.lock.json` with SHA256 pins.
- Validator script (`scripts/validate_scenarios.py`) and lockfile regen
  (`scripts/regen_manifest_lock.py`).
- Documentation: spec, schema, scenario authoring rules, dataset card,
  glossary, results.

### Frozen surface

- `data/scenarios.jsonl` (scenarios with inline gold labels)
- `data/prompt_conditions.json` (the three prompt conditions)
- The four judge labels (`current`, `prior`, `clarify`, `abstain`)
- Primary scoring rule: `mean(current_recall, prior_recall)` under `baseline`

[Unreleased]: https://github.com/n-dryer/wearable-assistant-context-bench/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/n-dryer/wearable-assistant-context-bench/releases/tag/v0.1.0
