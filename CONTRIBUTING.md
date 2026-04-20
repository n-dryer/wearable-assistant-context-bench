# Contributing to Deixis-Bench

This repo is public so readers can inspect benchmark design. It is
not open to arbitrary benchmark-set changes: the scenario set is
**frozen by version** and grown by explicit version extension, not
by ad-hoc PRs.

## What lives under version control

- **Frozen v1 scenario set.** `experiments/exp_001/scenarios.json`
  and `experiments/exp_001/expected_answers.json` define the v1
  measurement. Changing either changes the benchmark. Do not edit
  these files without a new version.
- **Intervention conditions.** `experiments/exp_001/interventions.json`
  is similarly frozen per version.
- **Code.** Scorer, judge adapter, model adapters, runner, and
  reporting are code; they can be changed with PRs as long as
  measurement semantics on the frozen set are preserved.
- **Docs.** Readability, accuracy, and honest limitations are
  always welcome.

## Benchmark governance

The governance rule (see
[docs/concept_v0_2.md](docs/concept_v0_2.md#benchmark-governance))
is:

- The v1 set is **frozen** after the v1 tag. Candidate models are
  evaluated on the same frozen v1 set.
- Benchmark growth happens by creating a **new versioned
  benchmark set** (v2, etc.) or an explicit version extension, not
  by silently editing v1 after results have been compared.

Scenario additions, deletions, or rewording on the v1 set are
rejected by default. Proposals for v2 belong in
[docs/deferred_roadmap.md](docs/deferred_roadmap.md).

## What we accept as PRs

| Change                                      | Accepted?             |
|---------------------------------------------|-----------------------|
| Typo / clarity fix in prose                 | Yes                   |
| Doc-only update (limitations, related work) | Yes                   |
| Scorer refactor that preserves semantics    | Yes, with tests       |
| New adapter (new model family)              | Yes, with tests       |
| Intervention-prompt wording change          | No (frozen in v1)     |
| Scenario add / delete / reword on v1        | No (frozen)           |
| Primary-score formula change                | No in v1; propose v2  |
| Judge-prompt wording change                 | Only as a versioned bump |

## Running the suite

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
pytest tests/ -q
```

The suite uses stubbed adapters; no real API keys are needed.

## Commit hygiene

- Atomic commits that describe a single logical change.
- No force-push or history-rewriting on `main` once a release tag
  is cut.
- Release-note-worthy changes land in `CHANGELOG.md`.
