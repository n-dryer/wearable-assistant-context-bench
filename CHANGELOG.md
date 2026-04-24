# Changelog

All notable benchmark-release changes live here.

## [v1.0.0] - 2026-04-24

First public release of the **Wearable Assistant Context Benchmark**.

### Included

- public docs reframed around the product problem and current measured
  task: **cross-turn reference resolution under context change**
- canonical `benchmark/v1/` consolidated around the frozen 101-scenario
  scenario bank, produced by applying the 2026-04-22 scenario audit to
  a 121-scenario candidate bank (3 merged, 17 removed, 55 rewritten)
- 51 scenarios rewritten to remove answer-token leakage in
  `turn_2_user`; all now use deictics and pass the `scripts/scan_leakage.py` audit
- scoring documented as deterministic substring containment; macro
  average of four per-category means is the main score
- balanced Turn 2 accuracy over `current` and `prior` retained as the
  primary ranking metric
- `clarify` and `abstain` retained as auxiliary diagnostic classes in
  the findings output
- LiteLLM-first adapter path added for broader model coverage
- cross-family judging retained as the default policy under
  `--judge-family auto`
- reproducibility manifest bundled with run outputs
- `docs/schema.md` added covering all scenario and answer-key fields
- `benchmark/v1/dataset_card.md` added with Hugging Face YAML frontmatter
- `scripts/scan_leakage.py` added as a reusable leakage regression guard
