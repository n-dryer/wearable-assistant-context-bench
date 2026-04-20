# Deixis-Bench

`Deixis-Bench` is an internal benchmark for **situated reference
resolution** in a wearable live-assistant camera product. It
measures whether a candidate model uses common-sense inference over
situational cues — the user's words, the object they just picked
up, the room they just walked into, what they said a minute ago —
to pick the right visual context when answering an
ambiguously-referenced question.

Object recognition is assumed. What is scored is the
reference-resolution decision, operationalized as a binary label:
does the Turn 2 answer anchor to the **prior** visual context (a
prior frame) or the **current** visual context (the right-now
frame)? "Prior vs. current" is the scoring axis; the underlying
task is **reference resolution under context shift**, the same
phenomenon linguists call deixis.

## What it is / what it is not

**It is:**

- a benchmark for visual-context selection
- internal-use: it compares candidate model releases for shipping
- a measurement of prior-versus-current visual-context selection
- used for model selection

**It is not:**

- a visual-recognition benchmark (object recognition is assumed)
- a paper
- a public leaderboard service

The v1 set is small; the benchmark is real. Size is a maturity
constraint, not a category downgrade.

## Scoring axis: prior vs. current

The scoring axis is binary, but the cues that determine the right
answer are plural: spatial shifts (walking from one room to
another), object-reference shifts (putting down A and picking up
B), temporal state changes (same scene after time passes), object
departure or return, and verbal or deictic cues ("this", "here",
"the new one").

- **prior visual context**: an object or place from a prior frame
- **current visual context**: an object or place from the current,
  right-now frame

A correct answer anchors to the visual context the question actually
refers to. Sometimes that is the current frame; sometimes it is a
prior frame.

## Two official benchmark variants

1. **With-prior-Q** (implemented in v1). Turn 1 asks about the prior
   frame in a way that establishes an explicit referent. Turn 2
   shifts visual context and asks an ambiguously-referenced
   follow-up. The model must override the Turn 1 anchor.
2. **Without-prior-Q** (planned next). The user's visual context
   shifts after the model has analyzed a prior frame, but Turn 1 did
   not create the anchor the model needs to override. Correct
   behavior is to default to the current frame.

The without-prior-Q variant covers three subcases, all preserved in
the benchmark definition even though none is implemented yet:

- **Soft case**: descriptive prior-frame question, then a new-room
  follow-up.
- **Unrelated-prior-question case**: prior frame was seen, but the
  prior question was unrelated.
- **Pure no-Turn-1 case**: prior frame was analyzed, but the user had
  not asked any prior question at all.

## Benchmark governance

- Pilot feedback from one model is the **authoring source** for the
  initial scenario seeds.
- That source does not define the benchmark boundary.
- The v1 scenario set is **frozen** after this pass. Future candidate
  models are evaluated on the same frozen v1 set.
- Benchmark growth happens by creating **new versioned benchmark
  sets** or explicit version extensions, not by silently changing the
  meaning of v1 after results have already been compared.

The v1 runnable set lands at 8 `current` / 3 `prior` scenarios. See
`docs/concept_v0_2.md` for the full set inventory and the rationale
for the balanced-accuracy primary score below.

## Primary score

The v1 primary score is **balanced Turn 2 accuracy under the
ranking condition**. Balanced means the mean of per-class accuracy
over the two scored policy classes (`prior` and `current`):

```
primary_score = (prior_class_accuracy + current_class_accuracy) / 2
```

Within a class, accuracy is the mean across all Turn 2 trial outcomes
under the ranking condition. Balanced accuracy prevents a trivial
"always current" policy from scoring roughly 73% on the 8/3 skew.

**Default ranking condition** is `baseline`. Until another production
wrapper is explicitly designated, ship decisions are made from
balanced accuracy under `baseline`. Condition sensitivity
(baseline vs. `condition_a` vs. `condition_b`) is reported
secondarily.

The judge may emit `clarify` or `abstain` tags for diagnostic
visibility. On v1, any trial labeled `clarify` or `abstain` is
**counted as wrong for the primary score**, and those tags are
rendered as separate diagnostic rows in the report grid.

## How to use for model selection

Run the benchmark against a candidate model:

```bash
python experiments/exp_001/run.py \
    --model <candidate_model_id> \
    --judge-model <judge_model_id>
```

Flags:

- `--model` — candidate model string. Required when comparing a new
  release.
- `--judge-model` — judge model string.
- `--judge-family` — `auto`, `claude`, or `openai`. Default `auto`
  picks a family different from the candidate's, inferred from the
  candidate string. Errors out if the candidate family cannot be
  inferred.
- `--trials` — trials per `(scenario, condition)` cell.
- `--output-dir` — output path for transcripts and the generated
  findings file for this run.

The runner writes a findings report with:

- the benchmark-summary section naming `v1 with-prior-Q slice` and
  the primary score under the ranking condition
- per-class accuracy (prior, current) and per-condition sensitivity
- per-scenario and per-condition detail
- a **reproducibility manifest** with scenario, intervention, and
  judge-prompt SHAs, model strings, temperature, trial count, and
  the resolved ranking condition

## Install

Requires Python 3.11+.

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

Set API keys as needed:

- `ANTHROPIC_API_KEY` is required when the candidate or judge is a
  Claude-family model.
- `OPENAI_API_KEY` is required when the resolved judge family is
  `openai`.

See `.env.example`.

## Verification

```bash
.venv/bin/python -m pytest tests/
```

The suite runs without real API keys; the adapter and judge are
stubbed in tests.

## Key docs

- [docs/methodology.md](docs/methodology.md): benchmark v1 runnable
  slice methodology
- [docs/concept_v0_2.md](docs/concept_v0_2.md): benchmark definition,
  variants, governance, and primary score
- [docs/interventions.md](docs/interventions.md): intervention axis
  framing
- [docs/limitations.md](docs/limitations.md): honest limitations of
  the v1 set
- [docs/related_work.md](docs/related_work.md): literature neighbors
- [docs/deferred_roadmap.md](docs/deferred_roadmap.md): planned
  benchmark extensions
- [.agent-prompts/PILOT_CORPUS_INVENTORY.md](.agent-prompts/PILOT_CORPUS_INVENTORY.md):
  corpus provenance inventory
