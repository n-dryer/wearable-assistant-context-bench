# Scenario audits

This folder holds pre-release scenario quality reviews for the
`Wearable Assistant Context Benchmark`. Each audit evaluates a candidate
scenario bank against a fixed rubric before that bank is tagged as the
next public release.

## What an audit is

An audit is an internal QA pass. It identifies which candidate scenarios
are ready to ship, which need rewriting, and which should be dropped or
merged. Verdicts apply to the candidate bank in the working tree, not to
any already-released v1 bank on `main`.

Each audit is a three-file artifact produced by
`scripts/scenario_audit/bootstrap_audit.py`:

- `YYYY-MM-DD-scenario-audit.jsonl`, the per-scenario source of truth
- `YYYY-MM-DD-scenario-audit.csv`, a sortable review view
- `YYYY-MM-DD-scenario-audit.md`, a bank-level summary

The generator is deterministic. Re-running the generator against the
same scenario source produces byte-identical files. This is enforced by
`tests/test_scenario_audit_artifact.py::test_bootstrap_audit_is_deterministic`.

## How to read a verdict

- `scenario_action` is the recommended action for the scenario itself:
  `keep`, `rewrite`, `merge`, or `remove`.
- `answer_key_action` is the recommended action for the answer key:
  `keep` or `rewrite`. It can differ from `scenario_action`.
- `severity` tags the urgency of the change: `low`, `medium`, or `high`.
- `issue_types` is a fixed enum covering the defects an audit can raise.

A high `rewrite` count does not mean the benchmark is broken. It means
the candidate bank is not yet ready to tag, and the audit names what
has to change first.

## 2026-04-22 audit

The 2026-04-22 audit is the post-consolidation health check on the
101-scenario canonical v1 bank. It was also the audit that motivated
the consolidation: the pre-consolidation candidate bank (121 scenarios)
returned 77 `rewrite`, 3 `merge`, 4 `remove`, and 37 `keep` verdicts,
driven mainly by hidden visual dependencies and generic answer keys.

The rewrites and removals have since been applied to
`benchmark/v1/scenarios.json` and `benchmark/v1/expected_answers.json`,
and the committed audit artifacts reflect the consolidated bank. The
consolidation applied 3 merges, 17 removals, and 55 rewrites to the
121-scenario candidate. The 17 removals are:

- 4 from the initial audit verdicts: sc-72, sc-75, sc-112, sc-121
- 5 from a structural-defect second pass: sc-28 (internal answer-key
  data mismatch), sc-70 (weak product relevance), sc-80 (hidden audio
  dependency), sc-58 and sc-98 (near-duplicates of stronger surviving
  scenarios sc-25 and sc-59)
- 8 `prior`-class scenarios where the expected answer appeared
  verbatim in Turn 1 text, making the scenario a short-term recall
  check rather than a cross-turn reference resolution check: sc-11,
  sc-24, sc-31, sc-61, sc-62, sc-68, sc-103, sc-105

Headline counts on the consolidated bank:

- `keep`: 101
- `rewrite`: 0
- `merge`: 0
- `remove`: 0

A blind inter-rater spot check on a deterministic 10-scenario sample of
the pre-consolidation audit produced 6/10 exact agreement on
`scenario_action`, 8/10 on `answer_key_action`, and 0.83 mean Jaccard on
`issue_types`, with full agreement on every high-severity call.
Disagreements clustered on low- and medium-severity edge cases. The
high-severity findings that drove the rewrite backlog were trustworthy.

The shipped v1 release on `main` remains the frozen 11-scenario bank
until a tagged release promotes the consolidated 101-scenario bank.
