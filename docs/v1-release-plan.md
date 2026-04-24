# v1 Release Plan (Final)

Final plan for shipping v1.0 of the Wearable Assistant Context Benchmark. Plain language. Specific files, branches, and recommendations. In execution order.

## Where you are today

- **Repo:** `/Users/nate/Developer/wearable-assistant-context-bench`
- **Active branch:** `v1-portfolio-release`
- **Scenario file:** `benchmark/v1/scenarios.json`, 101 scenarios, flat JSON array.
- **Distribution:** 50 current, 24 prior, 15 clarify, 12 abstain.
- **Answer keys:** `benchmark/v1/expected_answers.json`, per-scenario lists of `current_answers`, `prior_answers`, `clarify_indicators`, `abstain_indicators`.
- **Prompt variants:** `benchmark/v1/interventions.json`, 3 variants already authored (`baseline`, and two others).
- **HEAD commit:** `c01faf3` "release(v1): consolidate canonical v1 for portfolio release" (2026-04-23).
- **Uncommitted edits:** 8 doc files (CHANGELOG.md, CITATION.cff, CONTRIBUTING.md, README.md, docs/audits/README.md, docs/benchmark_notes.md, docs/benchmark_spec.md, docs/decisions.md).
- **Branch sprawl:** 30+ `claude/*` worktree branches plus `v1-completion`, `v1-language-pass`, `v1.1-extension`, `v2-expansion`, `codex/gemini-deep-research-prompt`.
- **Twins:** v1 does not use twin-pair scoring. The `variant` field is null on 100 of 101 scenarios. Scenarios are grouped by `source_example_id` but those are thematic families, not paired contrast tests.
- **Scoring:** answer keys are substring-style lists. Scoring is substring containment. Leakage example: sc-01 turn_2_user contains "claw hammer" and the expected `current_answers` contains "hammer" plus "claw hammer." Exact substring match. The leakage problem is real.

## The plan in one sentence

Commit the in-flight doc edits, fix leakage in the scenario set, finish a small list of release machinery tasks on `v1-portfolio-release`, open one PR to `main`, tag `v1.0.0`, delete stale branches.

## Three upfront decisions (recommendations with reasoning)

### Which branch should Claude Code work on?

**Recommendation: `v1-portfolio-release`.**

**Reasoning:** It has the consolidation commit plus in-flight doc edits. Any other starting point loses that work. `main` is 2 commits behind and doesn't have the consolidation yet.

### Should Claude Code do the branch cleanup autonomously?

**Recommendation: NO, do it manually or have Claude Code propose the list and wait for your approval.**

**Reasoning:** A bulk `git branch -D` on 30+ branches can silently discard unmerged work. Git refuses to delete branches with unmerged commits, but a branch created from main and then left alone will still delete cleanly even if it was meant to be kept. Human judgment on what to keep is cheaper than recovering lost work. Five minutes of review saves a bad outcome.

### Should Claude Code regenerate the baseline after scenario edits?

**Recommendation: YES, automatically after leakage fixes land.**

**Reasoning:** The c01faf3 commit already refreshed the baseline against the 101-scenario set. If Task 6 changes any scenarios, the baseline drifts. A fresh automated regeneration is low-risk since the runner is deterministic (temperature 0, fixed seed). No manual step needed.

### Scoring method for v1.0

**Recommendation: keep substring containment (what's already built). Defer LLM-as-judge to v1.1.**

**Reasoning:** `expected_answers.json` is already structured for substring matching. The runner and scoring code are already built around it. Migrating to LLM-as-judge would require authoring a judge rubric, piloting it against humans, and rewriting answer keys. That is v1.1 scope. For v1.0, use what exists, document the known limit in release notes (substring scoring is brittle on paraphrase), and ship.

### PR strategy

**Recommendation: one final PR from `v1-portfolio-release` into `main` at the end.**

**Reasoning:** You are solo on this. Multiple PRs add overhead without review benefit. Each task still lands as a distinct commit for clean history, but they roll into one review. If you want finer-grained review later, you can still look at individual commits.

---

## Phase A: Tidy the branch state

### Task 1: Review and commit the in-flight doc edits

**What:** 8 doc files have uncommitted changes on `v1-portfolio-release`.

**How:** from repo root, run `git diff` on each file. Keep the edits that reflect the intended v1.0 framing; revert any that don't.

**Recommendation:** commit them in one commit titled `docs: finalize v1.0 release docs`. Reasoning: the edits are all docs for the same release; one commit keeps history readable without being sloppy.

**Exit:** working tree is clean on `v1-portfolio-release`.

### Task 2: Delete stale Claude worktree branches

**What:** 30+ `claude/*` branches from past sessions.

**How:**

```
git for-each-ref --format '%(refname:short)' refs/heads/claude/ | xargs -n1 git branch -D
```

Git refuses to delete branches with unmerged commits, but review the output anyway.

**Recommendation:** run this yourself, not Claude Code. Reasoning: bulk deletions are the highest-risk step in the whole plan. Five minutes of human judgment here is cheaper than recovering lost work if something unexpected was on one of those branches.

**Exit:** fewer than 5 `claude/*` branches remain, each with a clear reason to stay.

### Task 3: Decide keep or delete on the other version branches

**What:** six branches beyond `main`, `v1-portfolio-release`, and `claude/*`.

**Recommendation per branch:**

- `v1-completion` — **delete.** Reasoning: the consolidation happened in c01faf3 on v1-portfolio-release. v1-completion is almost certainly an earlier draft superseded by the consolidation.
- `v1-language-pass` — **delete.** Reasoning: the language pass (plain-language cleanup of public docs) was rolled into c01faf3.
- `v1.1-extension` — **keep.** Reasoning: future work. Will house the human judge pilot and human speech-only spot check that v1.0 defers.
- `v2-expansion` — **delete.** Reasoning: v2 was retired in c01faf3. Nothing on this branch is the future of the benchmark.
- `codex/gemini-deep-research-prompt` — **delete** if the research is already integrated; keep if not. Reasoning: it's a research branch. If the outputs fed into docs or the research doc, it has served its purpose.

**How:** before deleting, run `git log v1-portfolio-release..BRANCH --oneline` on each. Zero commits means safe to delete. Non-zero commits means look at what's there.

**Exit:** branch list is `main`, `v1-portfolio-release`, `v1.1-extension`, plus any `claude/*` survivors.

---

## Phase B: Finish v1 scenario work

### Task 4: Scan scenarios for leakage

**What:** find every scenario where `turn_2_user` contains a substring from the expected answer keys.

**How:** a short script that loads `benchmark/v1/scenarios.json` and `benchmark/v1/expected_answers.json`, and for each scenario checks whether any token in `current_answers` or `prior_answers` appears word-boundary-matched in `turn_2_user`.

**Recommendation:** commit the script as `scripts/scan_leakage.py`. Reasoning: reusable audit tool; future editors can re-run it before merging changes. Also serves as a regression guard.

**Exit:** a list of flagged scenario IDs and the leaked tokens per scenario.

### Task 5: Run the automated leakage check

**What:** the harder test. Hide `turn_1_user` and the scene, have the model try to answer from `turn_2_user` alone. Score.

**How:** Claude Sonnet 4-6 at temperature 0, three runs per scenario, majority vote, with `turn_1_user` and both image fields masked. Score using the current substring scoring (since that's what ships). Flag any scenario scoring more than chance plus 10 percentage points. Chance baselines: 33% for current and prior, 50% for clarify and abstain.

**Recommendation:** combine with Task 4 into one pass. Report both signals per scenario. Reasoning: both tests find overlapping failure modes; one combined report is easier to act on than two separate ones.

**Exit:** combined list of leakage-flagged scenarios.

### Task 6: Fix the flagged scenarios

**What:** for each flagged scenario, rewrite `turn_2_user` to use deictics ("this one," "it," "that") without naming the referent.

**How:** spawn one category-specialist agent per category (current, prior, clarify, abstain). Each agent handles only its category's flagged scenarios and writes to a per-category output file. Then merge the fixes into `scenarios.json`.

**Recommendation:** use my grounding-evals sandbox work as reference for rewrite patterns, but do not port the full content. Reasoning: my sandbox used a different schema (split-channel with separate `scene` and `user_speech` fields). Porting that schema into v1's flat schema is a big rewrite with no upside. The useful thing is the rewrite pattern (describe by properties instead of naming), which transfers.

**Exit:** every flagged scenario has a rewritten `turn_2_user`. Re-run Tasks 4 and 5 until zero scenarios flag.

### Task 7: Handle weak prior scenarios

**What:** some prior scenarios likely test short-term recall of exact strings rather than real reach-back.

**How:** read each of the 24 prior scenarios. Ask "can a model answer this by substring-matching turn_1_user text?" If yes, add to a limits list.

**Recommendation:** document rather than rewrite. Reasoning: rewriting each weak prior scenario is expensive and can drift from the scenario's original intent. A release-notes paragraph acknowledging the limit is honest and ships faster. v1.1 can strengthen them properly.

**Exit:** a short list of weak prior scenario IDs ready to reference in release notes.

### Task 8: Validate updated scenarios

**What:** re-run QA on any scenario touched in Task 6.

**How:** one validator sub-agent, 4-part QA (quality, requirements, natural language, visual context).

**Recommendation:** keep this validator lean. Reasoning: you are validating scenarios that were just patched by other agents. A heavy re-grade would duplicate audit work already done in my sandbox. Scope: confirm the patches landed clean and didn't introduce new leakage.

**Exit:** every touched scenario passes validation or is queued for another fix pass.

---

## Phase C: Finish release machinery

### Task 9: Author and freeze the judge rubric prompt (deferred to v1.1)

**What:** a prompt template for LLM-as-judge scoring.

**Recommendation:** defer to v1.1. Reasoning: substring scoring is already built and will work for v1.0. Authoring and piloting an LLM judge is a multi-hour task that should go through human validation, which v1.0 defers anyway. Add to `v1.1-extension` branch backlog.

**Exit:** a note in the v1.1-extension branch README listing this as planned work.

### Task 10: Document the scoring rules

**What:** write down how scoring works so reviewers can reproduce it.

**How:** add a "Scoring" section to `docs/benchmark_spec.md`. Cover:
- Main score: substring containment against `expected_answers.{current_answers|prior_answers}`, per scenario, averaged per category, main score is the macro average across the 4 categories.
- Clarify and abstain: a response counts as correct if it contains any of the `clarify_indicators` or `abstain_indicators` tokens respectively, plus does not produce a confident wrong answer.
- Recovery after correction: for scenarios with a non-empty `turn_3_repair_anchor`, compute the metric as "fraction of scenarios where the model's turn-3 response scores correct given that its turn-2 response scored incorrect." Report per category.
- Clarify vs abstain rule: use `clarify` when some context is present but the referent is ambiguous; use `abstain` when the needed info is not available.

**Recommendation:** use macro-averaging for the main score. Reasoning: prevents larger categories (current at 50, prior at 24) from dominating the number. Keeps clarify and abstain visible.

**Exit:** `docs/benchmark_spec.md` has a complete Scoring section.

### Task 11: Verify prompt variants

**What:** `interventions.json` already has 3 variants authored. Verify they match what release notes will claim.

**How:** read `benchmark/v1/interventions.json`, confirm each has `name`, `description`, `system_prompt`, `token_count`. Confirm the names align with what the runner expects.

**Recommendation:** keep as-is, do not add a fourth variant. Reasoning: three is already more than many benchmarks ship with. Adding more without a clear purpose adds maintenance cost.

**Exit:** `interventions.json` is the frozen source of prompt variants.

### Task 12: Write schema documentation

**What:** document every field in `scenarios.json` and `expected_answers.json`.

**How:** save as `docs/schema.md`. For each field, cover: type, required or optional, meaning, example.

**Recommendation:** include a note that `variant` is currently only populated on sc-06. Reasoning: a reader will wonder about the field. A one-line explanation saves them an investigation.

**Exit:** `docs/schema.md` exists and is accurate.

### Task 13: Add or verify the dataset card

**What:** Hugging Face-compliant metadata.

**How:** check if `dataset_card.md` exists. If yes, verify fields. If not, author one at `benchmark/v1/dataset_card.md` with YAML frontmatter: `license`, `language`, `pretty_name`, `task_categories`, `task_ids`, `tags`, `size_categories`, `features`, `splits`.

**Recommendation:** place at `benchmark/v1/dataset_card.md` (not repo root). Reasoning: the dataset is specifically the v1 bundle; the repo root card would imply the whole repo is the dataset, which it is not.

**Exit:** dataset card exists and validates against HF schema.

### Task 14: Run the full test suite

**What:** all tests green.

**How:** `pytest` from repo root. The `tests/test_terminology.py` guardrail added in c01faf3 must pass.

**Recommendation:** run locally first, then push and let CI confirm. Reasoning: if the terminology test fails because of something in Task 1 (doc edits), catching it locally is faster.

**Exit:** all tests pass locally and on CI.

### Task 15: Regenerate the baseline

**What:** run the benchmark against the final scenario set to produce `benchmark/v1/runs/v1-baseline/`.

**How:** `python benchmark/v1/run.py --mode baseline` or equivalent.

**Recommendation:** regenerate automatically after Task 6 (leakage fixes) completes. Reasoning: if scenarios changed, the existing baseline is stale. Regeneration is deterministic and cheap.

**Exit:** baseline output files match the final scenario set.

### Task 16: Write v1.0 release notes

**What:** a single file at the repo root.

**How:** `RELEASE_NOTES_v1.0.md`. Cover: benchmark purpose, scoring method, scenario counts, known limits, what shipped, what didn't, links to docs.

**Recommendation:** keep under 500 words. Reasoning: release notes are an index, not a manual. Detailed specs live in `docs/benchmark_spec.md`.

**Exit:** release notes exist and are reviewed.

---

## Phase D: Ship

### Task 17: Open the PR

**What:** one PR from `v1-portfolio-release` into `main`.

**How:**

```
gh pr create --base main --head v1-portfolio-release \
  --title "release: v1.0 portfolio release" \
  --body-file RELEASE_NOTES_v1.0.md
```

**Recommendation:** paste release notes into the PR description directly too, not just the file link. Reasoning: reviewers shouldn't have to open a second tab.

**Exit:** PR is open.

### Task 18: Review and merge

**What:** CI green, self-review, merge.

**How:** after CI passes, `gh pr merge --merge` or use the GitHub UI.

**Recommendation:** use a merge commit, not squash. Reasoning: preserves the task-by-task commit history as a reviewable record. Squash loses that.

**Exit:** `v1-portfolio-release` is merged into `main`.

### Task 19: Tag v1.0.0 on main

**What:** an annotated git tag on the merge commit.

**How:**

```
git checkout main
git pull
git tag -a v1.0.0 -m "v1.0.0 — Wearable Assistant Context Benchmark portfolio release"
git push origin v1.0.0
```

**Recommendation:** use an annotated tag (`-a`), not a lightweight one. Reasoning: annotated tags carry the tagger's name, date, and message. Lightweight tags are just pointers. Annotated is the convention for release tags.

**Exit:** `v1.0.0` tag exists locally and on origin.

### Task 20: Publish the GitHub Release

**What:** a GitHub Release tied to the v1.0.0 tag.

**How:**

```
gh release create v1.0.0 --title "v1.0.0" --notes-file RELEASE_NOTES_v1.0.md
```

**Recommendation:** include a note in the Release body linking to the LICENSE, CITATION, and dataset card. Reasoning: external users arriving at the Release page should see everything they need in one view.

**Exit:** release is live on GitHub.

---

## Phase E: Post-release cleanup

### Task 21: Delete the release branch

**What:** `v1-portfolio-release` is merged; delete it locally and on origin.

**How:**

```
git branch -d v1-portfolio-release
git push origin --delete v1-portfolio-release
```

**Recommendation:** use `-d` (safe delete), not `-D`. Reasoning: `-d` fails if the branch has unmerged commits, which would mean something unexpected happened. Safer fallback.

**Exit:** branch is gone locally and on origin.

### Task 22: Final repo state check

**What:** confirm the repo is in the intended final state.

**How:**

```
git status            # should be clean
git log main -5       # should show the merge commit at the tip
git tag --list        # should include v1.0.0
git branch -a         # should be main, v1.1-extension, origin/main, origin/v1.1-extension
```

**Recommendation:** run all four commands and paste the output into your notes. Reasoning: a written snapshot of the post-release state makes future debugging ("when did we tag?" "what was in v1.0?") immediate.

**Exit:** `main` is the source of truth, `v1.0.0` is tagged, branch list is minimal, only intentional branches remain.

---

## Summary

22 tasks across 5 phases.

- **Phase A** (branch hygiene): 3 tasks, ~1 hour. Manual.
- **Phase B** (scenario work): 5 tasks, ~1 day. Agent-driven.
- **Phase C** (release machinery): 8 tasks, ~half day. Mostly writing and verification.
- **Phase D** (ship): 4 tasks, ~1 hour.
- **Phase E** (cleanup): 2 tasks, ~15 minutes.

**Total effort:** 2 to 3 focused days. Phase B is the main time sink.

**Biggest defer:** LLM-as-judge scoring (Task 9) and human validation (v1.1 items) both push to the `v1.1-extension` branch.

**Biggest risk:** sc-01 and probably many others leak the answer in `turn_2_user`. Tasks 4 through 6 are the critical path. Everything else is packaging around that core fix.
