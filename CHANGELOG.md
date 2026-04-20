# Changelog

All notable changes to Deixis-Bench. This project loosely follows
[Keep a Changelog](https://keepachangelog.com/) and
[Semantic Versioning](https://semver.org/): version tags are applied
to the benchmark set as a whole (scenarios + scoring + reporting),
not to the codebase.

## [v1] (2026-04-20)

**Initial public release.** Deixis-Bench is renamed and reframed
as a benchmark for **situated reference resolution under visual
context shift** (prior vs. current visual context) on a wearable
live-assistant camera surface.

### Added

- Deixis-Bench project identity and README lead reframing the task
  around situated reference resolution.
- OpenAI candidate adapter (`core/openai_adapter.py`) and
  family-based routing in the runner (`experiments/exp_001/run.py`).
- `docs/surface.md` documenting the provisional wearable surface
  envelope (1080p / ~70° FOV / 30fps / ~10-min frame buffer).
- `docs/concept_v0_2.md` cue-taxonomy section enumerating the five
  cue families v1 exercises.
- `docs/limitations.md` latest-mention heuristic caveat.
- README "How to read a score", "How to cite", and glossary blocks.
- `results/` directory with a sample-run convention for committed
  findings.
- Reproducibility manifest now records the real git HEAD SHA.

### Changed

- Collapsed the pre-release v1.1 label into **v1**. The 11-scenario
  set previously labeled v1.1 is the frozen Deixis-Bench v1 set.
- Repository renamed `grounding-evals` → `deixis-bench`.
- README scoring-axis section renamed "Scoring axis: prior vs.
  current" and prepended with the cue-families framing.
- Archived the pre-freeze authoring plan to
  `docs/history/V1_1_SCENARIO_EXPANSION.md` with a historical
  banner.

### Removed

- The premature `v1.1` git tag (never the canonical release label
  for this set; collapsed into `v1`).

## [pre-release snapshots]

These snapshots predate the v1 public release. They are documented
for provenance; the tags were working labels, not canonical
releases.

### v1.1-extension (pre-release working label) (2026-04-20)

Expanded the scenario set from 4 to 11, adding sc-05 through
sc-11 to cover construct dimensions not represented in the
original seed set. Bumped internal `BENCHMARK_VERSION` string.
Aligned per-class composition (8 `current` / 3 `prior`).

### v0.3.0 (benchmark-reset pass) (2026-04-19)

Froze the with-prior-Q variant as the scored v1 surface. Adopted
balanced Turn 2 accuracy as the primary score and `auto` as the
default judge family. Added the reproducibility manifest.

### v0.1 / Phase 0-4 scaffold (2026-04-18)

Pre-flight setup, templates, and core infrastructure with
multi-turn support, disk-caching Claude adapter, and the initial
runner loop.
