# Claude Code Build Prompt — v0.2 Reference-State Selection Probe

Paste the block below into Claude Code from the repo root. This prompt
directs two lanes of work in a single session:

- **Lane 1.** Python-side build for the v0.2 reference-state
  selection probe (scenarios, judge, runner, report, tests).
- **Lane 2.** Instruction-file alignment: rename the task from
  `grounding-state selection` to `reference-state selection`, fix
  stale numbers and vocabulary in `CLAUDE.md`, and add a current-
  state note to `AGENTS.md`.

The build inputs in `.agent-prompts/` (SCENARIO_SEEDS, INTERVENTIONS,
PILOT_CORPUS_INVENTORY, FAILURE_MODES) are the sources of truth and
stay read-only in this pass.

---

You are implementing the v0.2 **reference-state selection** probe in
this repo. The Cowork-authored build inputs are already committed.
Your job is (1) the Python side and (2) the instruction-file
alignment. Work through Lane 1, then Lane 2, then final validation.

## Naming note (do this first)

The probe's operational task name is **reference-state selection**.
The literature-facing anchor is **multimodal reference resolution
under context shift**. An earlier draft used `grounding-state
selection`; that phrase is being retired because (a) "grounding" in
current MLLM literature usually means visual grounding on images,
and (b) the task is literally a reference-resolution problem with a
state-typed referent set (see Chandu & Bisk 2021, "Grounding
'Grounding' in NLP"; Ghaleb et al. 2025 on multimodal reference
resolution; OmniMMI 2025 on state grounding as a distinct subtask).
The repo name `grounding-evals` stays — it is a fine umbrella.

Use `reference-state selection` in prose. Keep the four-policy
labels (`current`, `prior`, `clarify`, `abstain`) unchanged.

## Read first (sources of truth)

Before writing anything:

1. `AGENTS.md` — agent-facing project context, v0.2 scope, run volume.
2. `docs/concept_v0_2.md` — four-policy taxonomy, metrics
   (per-policy pass rate, simulated repair rate, code-judge
   disagreement), corpus asymmetry, probe-vs-benchmark framing.
3. `.agent-prompts/SCENARIO_SEEDS.md` — 4 populated seeds
   (sc-01..sc-04) with `target_policy`, `source_example_id`,
   `surface`, Turn 1/Turn 2 text, answer sets, Turn 3 repair anchor.
4. `.agent-prompts/INTERVENTIONS.md` — three pinned system prompts
   (Condition 0 baseline, Condition A direct instruction,
   Condition B pre-answer scaffold). Read-only.
5. `.agent-prompts/PILOT_CORPUS_INVENTORY.md` — provenance trail.
6. `.agent-prompts/FAILURE_MODES.md` — v0.2 policy mapping.
7. `CLAUDE.md` — project rules and vocabulary.
8. Existing `core/` modules (`models.py`, `llm_judge.py`,
   `scoring.py`, `interventions.py`, `report.py`) and `tests/`.

## Edit boundary

**Read-only (do not edit):**

- `.agent-prompts/SCENARIO_SEEDS.md`
- `.agent-prompts/INTERVENTIONS.md`
- `.agent-prompts/PILOT_CORPUS_INVENTORY.md`
- `.agent-prompts/FAILURE_MODES.md`
- `audit/*`
- v0.1-framed docs the user has actively curated in this state:
  `docs/limitations.md`, `docs/methodology.md`, `docs/interventions.md`,
  `docs/deferred_roadmap.md`, `experiments/README.md`,
  `experiments/exp_001/README.md`. These describe what the current
  runner actually does. Leave them alone.

**Editable (Lane 1 and Lane 2):**

- `core/*`, `tests/*`, `experiments/exp_001/scenarios.json`,
  `experiments/exp_001/expected_answers.json`,
  `experiments/exp_001/interventions.json`,
  `experiments/exp_001/run.py`.
- For Lane 2 only: `README.md`, `AGENTS.md`, `CLAUDE.md`,
  `docs/concept_v0_2.md`, `docs/related_work.md`, and the one
  historical file `.agent-prompts/V0_2_UPDATE_PLAN.md`. Keep edits
  minimal and scoped to the rename + stated fixes.

**Model version strings** are pinned in config only, never inline.
Default `claude-sonnet-4-6`; temperature 0.

**Stop and ask** if: a seed field is ambiguous; the judge rubric
would need synthesized content the concept doc doesn't specify; a
rename would require rewriting a section rather than a phrase
substitution; you'd have to fill a content gap by guessing. Default
is ask, not assume.

---

## LANE 1: v0.2 runner build

### 1.1. `experiments/exp_001/scenarios.json`

One record per seed (`sc-01`..`sc-04`). Required fields per seed:

- `scenario_id` (e.g. `sc-01`)
- `target_policy` (one of `current`, `prior`, `clarify`, `abstain`)
- `authoring_basis` (`pilot`)
- `source_example_id` (e.g. `ex-01`)
- `surface` (`wearable_live_frame` | `mobile_app_chat`)
- `turn_1_user` (verbatim from seeds file)
- `turn_2_user` (verbatim from seeds file)
- `turn_3_repair_anchor` (the "I mean, ..." template)
- `notes` (optional, copied from seeds file)

### 1.2. `experiments/exp_001/expected_answers.json`

One record per seed, keyed by `scenario_id`. Required fields:
`current_answers`, `prior_answers`, `clarify_indicators`,
`abstain_indicators`. Copy token lists verbatim from seeds file. Do
not add, remove, or paraphrase tokens.

### 1.3. `experiments/exp_001/interventions.json`

One record per condition (`baseline`, `condition_a`, `condition_b`).
Pull exact system prompt strings via `core/interventions.py`. Do not
mutate prompt text.

### 1.4. `core/scoring.py`

- Rename `has_stale` → `has_prior` throughout (code, docstrings,
  tests). The code signal now corresponds to the `prior` policy,
  not "stale."
- Keep `has_stale` as a thin deprecated alias that delegates to
  `has_prior` (one-line wrapper, `DeprecationWarning` on call).
  Rationale: `docs/methodology.md` is v0.1-curated and read-only
  in this PR; it still documents `has_stale`. The alias lets that
  description stay accurate until the doc-alignment PR lands.
- Add `has_clarify` (True if response contains any
  `clarify_indicators` substring) and `has_abstain` (True if
  response contains any `abstain_indicators` substring).
- Retain the contrastive-pattern suppressor unchanged; only the
  output field name shifts.
- Code signals are **audit-only** in v0.2. Judge is pass authority.

### 1.5. `core/llm_judge.py`

Judge returns one label per Turn 2 response:
`{current, prior, clarify, abstain}`.

Judge input:

- Turn 2 user message
- Turn 2 assistant response
- scenario's `target_policy` (for the rubric; not given as a hint)
- short scenario description derived from `turn_1_user`
- the four answer-set lists

Judge output (structured):

```json
{
  "selected_policy": "current",
  "rationale": "one-sentence justification"
}
```

A pass is `selected_policy == target_policy`.

Rubric text should mirror `docs/concept_v0_2.md §Policy taxonomy`
definitions verbatim where possible. Do not editorialize.

Keep the same-family judge caveat in the module docstring (cites
`docs/limitations.md §Judge reliability`).

### 1.6. `experiments/exp_001/run.py`

Readable loop (prose-style):

```
for scenario in scenarios:
    for condition in conditions:
        for trial in range(TRIALS):
            t1 = call_model(system=condition.prompt,
                            turn_1=scenario.turn_1_user)
            t2 = call_model(system=condition.prompt,
                            history=[t1], turn_2=scenario.turn_2_user)
            code_signals = scoring.score(t2, scenario.answers)
            judge_verdict = judge.label(t2, scenario, t1)
            passed = judge_verdict.selected_policy == scenario.target_policy
            if not passed:
                t3 = call_model(system=condition.prompt,
                                history=[t1, t2],
                                turn_3=scenario.turn_3_repair_anchor)
                repair_verdict = judge.label(t3, scenario,
                                             prior_turns=[t1, t2])
                repair_success = (repair_verdict.selected_policy
                                  == scenario.target_policy)
            transcripts.write(...)
```

Config dict at top:

```python
CONFIG = {
    "model_id": "claude-sonnet-4-6",
    "judge_model_id": "claude-sonnet-4-6",
    "temperature": 0.0,
    "trials_per_cell": 2,
    "output_dir": "experiments/exp_001/transcripts/",
}
```

Emit per-trial transcripts as JSONL with `scenario_id`,
`condition_id`, `trial`, `turn`, request, response, code signals,
judge verdict, pass boolean.

### 1.7. `core/report.py`

Generate `experiments/exp_001/findings.md` with:

1. **Per-policy pass rate by condition** — 4 rows × 3 columns.
   `clarify` and `abstain` rows carry a "no corpus-backed
   scenarios; unscored in v0.2" note, not a number.
2. **Simulated repair rate** — per condition, fraction of Turn 2
   failures rescued by Turn 3 anchor. Numerator and denominator
   explicit.
3. **Code-judge disagreement** — per-scenario count where code
   signals disagree with judge `selected_policy`. Log, do not
   auto-resolve.
4. **Scenario-by-condition matrix** — 4 × 3 grid showing
   pass/fail/repair-pass/repair-fail per trial.

Do **not** emit an aggregate pass rate across policy rows.

### 1.8. Tests (`tests/`)

- `test_scoring.py`: `has_prior` rename, `has_clarify` and
  `has_abstain` new signals, suppressor unchanged.
- `test_judge.py`: four-policy label parsing, malformed-output
  fallback.
- `test_interventions.py`: three conditions load cleanly; prompt
  text is not mutated.
- `test_report.py`: per-policy grid renders with unscored-row
  notes; simulated repair rate numerator/denominator correct; no
  aggregate cross-row pass rate emitted.
- `test_scenarios_config.py` (new): every `scenarios.json` row has
  all required fields; `target_policy` in allowed set;
  `source_example_id` non-null; `turn_1_user` and `turn_2_user`
  match `SCENARIO_SEEDS.md` verbatim.

Pytest-runnable, no network. Stub model/judge calls.

---

## LANE 2: instruction-file alignment

Execute these after Lane 1 is green. Each item is a minimal,
bounded edit.

### 2.1. Rename the task: `grounding-state selection` → `reference-state selection`

Files to update (only the listed phrase; do not rewrite surrounding
prose):

- `README.md` — title sentence, overview, any other occurrences.
- `AGENTS.md` — "What This Project Is" section, any other
  occurrences.
- `docs/concept_v0_2.md` — title, Intent section, any other
  occurrences. The phrase "grounding state" used as a noun
  ("selects the grounding state an answer should be derived from")
  should become "reference state."
- `.agent-prompts/V0_2_UPDATE_PLAN.md` — this is a historical plan
  doc; prepend a one-line note `> Historical. Terminology has
  since flipped from grounding-state selection to reference-state
  selection (see CLAUDE_CODE_BUILD_PROMPT.md).` and leave the body
  alone.

Do **not** touch `.agent-prompts/PILOT_CORPUS_INVENTORY.md`
occurrences — they are internal descriptive notes in a read-only
Cowork-owned input.

Do **not** touch `docs/related_work.md`; it already uses
`reference-state selection` after a prior linter pass.

The **repo name** `grounding-evals`, the **directory** layout, and
the four-policy **labels** stay unchanged.

### 2.2. `CLAUDE.md` fixes

Three specific fixes; leave the rest of the file alone:

1. Line describing the methodology: replace the "8 scenarios, each
   a 2-turn conversation" paragraph with the v0.2 numbers from
   `AGENTS.md` (4 scenarios, 48 Turn-1/Turn-2 main calls + 24
   Turn-2 judge calls + up to 24 Turn-3 simulated-repair calls).
2. "Total runs" line: update to match the new volume.
3. File-organization line listing docs: replace `incident classes`
   with the v0.2 wording. The `docs/` subdir contains `concept_v0_2.md`,
   `methodology.md`, `limitations.md`, `interventions.md`,
   `related_work.md`, `deferred_roadmap.md`. Drop the `incident
   classes` entry.

Keep everything else in `CLAUDE.md` untouched in this PR.

### 2.3. `AGENTS.md` one-liner

Add one sentence in the "What This Project Is" section (or adjacent,
before "Core Methodology") that notes the current state of the
runner, something like:

> **Current implementation state.** `exp_001`'s Python runner is
> being wired up in this PR. Docs in `docs/` that describe the
> active runner still reflect the v0.1 current-vs-stale framing;
> that alignment pass lands after the runner produces a first real
> result.

Exact wording is yours. Keep it to one short paragraph.

---

## Final validation

Run in order:

1. `.venv/bin/python -m pytest tests/` → must be green.
2. Forbidden-term grep across the repo scope (exclude `.git/`,
   `.venv/`, `__pycache__/`, `.pytest_cache/`, `audit/`). Terms:
   - `grounding-state selection` (should be 0 hits outside
     `PILOT_CORPUS_INVENTORY.md` and the historical banner in
     `V0_2_UPDATE_PLAN.md`)
   - `incident class`, `incident_class` (0 hits)
   - `observation` used to mean pilot-feedback item (0 hits;
     "pattern observation" in the corpus inventory is a different
     usage and is fine)
3. Required-term grep:
   - Umbrella files (`README.md`, `AGENTS.md`,
     `docs/concept_v0_2.md`, `docs/related_work.md`): should
     contain `reference-state selection` and `simulated repair
     rate` and `probe study`.
   - Active experiment files (`docs/methodology.md`,
     `docs/limitations.md`, `docs/interventions.md`,
     `experiments/exp_001/README.md`, `experiments/README.md`):
     should still contain `current-vs-stale`, `current_answers`,
     `stale_answers`, `has_current`, `has_stale`. Do not rewrite
     these files to match Lane 2 vocabulary.
4. Dry-run the runner with stub model/judge fixtures. Confirm
   transcript JSONL shape.

## What to hand back

Single PR-style summary with:

- Lane 1 files created/modified.
- Lane 2 files modified (rename diff count + CLAUDE.md diff).
- Test results (pass count, any skipped).
- Forbidden/required grep results.
- Any ambiguities hit and resolutions (or a "needs Nate's input"
  block if you had to stop).
- Explicit callouts for any boundary cases (e.g. a file you
  considered editing but left alone per the edit-boundary list).

## Style rules (Python)

- Type hints everywhere; docstrings on every public function.
- No bare `except:`.
- Dataclasses for structured data; no raw dicts across module
  boundaries.
- JSON schemas in dataclass docstrings.
- Explicit loops over clever abstractions. The runner should read
  like prose.
