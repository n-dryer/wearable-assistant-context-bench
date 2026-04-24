# Changelog

All notable benchmark-release changes live here.

## [Unreleased]

Pre-release state of the **Wearable Assistant Context Benchmark**. This
section describes the changes that will make up the first public
release. No version has been tagged yet. The first public release will
be tagged `v1` when the accompanying benchmark results are published.

### Included

- public docs reframed around the product problem and current measured
  task: **cross-turn reference resolution under context change**
- canonical `benchmark/v1/` consolidated around the frozen 101-scenario
  scenario bank, produced by applying the 2026-04-22 scenario audit to
  a 121-scenario candidate bank (3 merged, 17 removed, 55 rewritten)
- balanced Turn 2 accuracy over `current` and `prior` retained as the
  primary ranking metric
- `clarify` and `abstain` retained as auxiliary diagnostic classes in
  the findings output
- LiteLLM-first adapter path added for broader model coverage
- cross-family judging retained as the default policy under
  `--judge-family auto`
- reproducibility manifest bundled with run outputs
