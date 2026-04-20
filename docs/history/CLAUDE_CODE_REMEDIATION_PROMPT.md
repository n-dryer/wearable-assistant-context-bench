# Claude Code Remediation Prompt (v0.2.1, framing-reset) — SUPERSEDED

> **Superseded 2026-04-19 by the v0.3.0 benchmark-reset pass.**
> This prompt is retained for history. It is **no longer the
> active source of truth** and should not be used to drive work
> on the repo. The superseding prompt lives at
> `grounding-evals/CLAUDE_CODE_REMEDIATION_PROMPT_v0.3.0.md`.
> Any conflict between this file and the v0.3.0 prompt is
> resolved in favor of the v0.3.0 prompt and the repo's current
> doc set (`README.md`, `docs/concept_v0_2.md`, `CLAUDE.md`).

Paste everything below the `---` divider into Claude Code. It is self-contained; no prior-session context required beyond the repo itself.

---

## Context

You are working on `grounding-evals`. A Cowork session just completed a framing reset. This prompt captures the work to bring the repo into alignment with the new framing.

The repo's canonical v1 identity is:

- A **visual-context selection benchmark** for live-assistant AI systems.
- It measures whether a model picks the **right visual context** when answering a question.
- It scores **context selection**, not visual recognition. Visual recognition is assumed.
- The core decision is whether the answer anchors to the **prior visual context** (object or place from a prior frame) or the **current visual context** (object or place from the current frame).
- It is used **internally** to compare candidate model releases and choose which one ships in a wearable live-assistant camera product.
- It is not a paper, not a leaderboard service, and no longer framed as a "probe study."

The repo is public on GitHub so readers can inspect the framework and verify the author's claims. The benchmark inside it is internal-use.

## Ground rules

1. **Generic product language only.** The product is a "wearable live-assistant camera product" or "egocentric camera system" or "assistant that answers questions about what it is seeing now or what it saw moments earlier." Do **not** use concrete product names or company branding anywhere in committed files. Phase 1 enforces this.

2. **Drop the probe-study framing entirely.** No top-level doc uses `probe study` as the project identity. No top-level doc says `not a benchmark`, `not a model ranking`, or similar hedges. Maturity is stated honestly as maturity, not as a category downgrade.

3. **v1 scored surface = `prior` vs `current` only.** `clarify` and `abstain` become future extensions, not part of v1 identity. The 4-policy taxonomy may stay in code (`core/llm_judge.py`) for compatibility, but project-facing docs describe the scored decision as prior-vs-current visual context. `clarify` and `abstain` are mentioned as reserved tags the judge can still emit, not as project identity.

4. **Two official benchmark variants:**
   - **With-prior-Q** (implemented): Turn 1 establishes a referent; Turn 2 shifts visual context and requires overriding the Turn 1 anchor.
   - **Without-prior-Q** (planned next): the stale anchoring would come from prior visual state alone, without Turn 1 establishing a language-level anchor.
   Both are documented as official parts of the benchmark definition. Without-prior-Q not being implemented yet is a coverage note, not a framing question.

5. **Current runner = v1's first runnable slice**, not a separate conceptual artifact. The repo no longer has a "forward-looking concept vs active artifact" split. There is one benchmark; the current implementation is its first slice.

6. **Salvage over delete.** Preserve `EXECUTION_PLAN.md`, all `framework-audit-*`, `claude-code-handoff-*`, `triage-*`, `audit/research/*`, `PILOT_CORPUS_INVENTORY.md`, `FAILURE_MODES.md`, `SCENARIO_SEEDS.md`, and all `.agent-prompts/*` files. Do not delete historical artifacts.

7. **Checkpoint at phase boundaries.** Stop and ask if any judgment call needs synthesis beyond the pilot corpus, or if a ground rule conflicts with an existing file.

8. **Do not run experiments.** No `run.py` invocations with real API keys. Tests only.

## Phase 1: Anonymization audit and scrub

Goal: safe-for-public-push content state.

### 1a. Full-repo scan

Run case-insensitive searches across all tracked files for:

- The concrete product name (any anonymized codename and common casing variants thereof).
- Personal research folder names (any product-specific folder names and casing variants).
- Absolute path fragments: any personal dev path.
- Real author-name attributions (quote attributions tied to an individual).
- Production-stack references tied to the concrete product (for example, specific model-family names tied to the product). Generic literature citations to model families can stay.
- Company-branded phrasing, including any placeholder company names — those are also too branding-forward for this pass.

Produce a file-by-file list with line numbers. Report before scrubbing.

### 1b. Replacement terminology

- Product name → "the wearable live-assistant camera product", "the wearable", or "the egocentric camera system" depending on context.
- Fuller noun phrase when needed: "an assistant that answers questions about what it is seeing now or what it saw moments earlier."
- Product-specific issue identifiers → generic anonymous forms (for example, `FB-NN`), or drop if the surrounding prose doesn't need them.
- Absolute paths → relative paths or abstract descriptions (for example, "pilot feedback report 02").
- Author self-attributions ("reviewing PM (Me)") → "reviewing PM". Quoted individual names → "the author" or drop.
- Production model family tied to the product → "a non-Claude production model family" or drop, depending on context.
- Any placeholder company name → drop. Keep the product generic without company framing.

### 1c. Verify

Re-run the Phase 1a scan. Report any remaining hits. Stop and ask on any ambiguous case where anonymization would destroy meaning.

## Phase 2: Framing reset in docs

Goal: every top-level doc reflects the new benchmark identity.

### 2a. `README.md` rewrite

- Rewrite the opening paragraph to define the repo as **an internal visual-context selection benchmark for a wearable live-assistant camera product**.
- Remove the "active artifact vs forward-looking concept" split. There is one benchmark; the current implementation is its first slice.
- Remove the public-strength-label subsection and any "probe study" language.
- Add a clear "**What it is / what it is not**" section:
  - It is a benchmark.
  - It is internal-use.
  - It measures prior-vs-current visual-context selection.
  - It is used for model selection.
  - It is **not** a visual-recognition test.
  - It is **not** a paper or leaderboard service.
- Define the two variants: with-prior-Q (implemented) and without-prior-Q (planned).
- Define the two contexts:
  - **prior visual context** = object or place from a prior frame.
  - **current visual context** = object or place from the current frame.
- Add a "**How to use for model selection**" section: how to invoke the runner with a new model (`python experiments/exp_001/run.py --model <model_id> --judge-model <model_id>`), what the output looks like, and what decisions it informs.
- Keep install, verification, and key-docs sections. Update key-docs links if any target changes.

### 2b. `docs/concept_v0_2.md` rewrite

- Replace the external probe-study framing with an internal benchmark spec.
- Remove §"Why the public framing is a probe study."
- Add sections:
  - **Benchmark definition**: what is scored (prior-vs-current visual context selection), what is not scored (visual recognition).
  - **Prior and current visual contexts**: the two-context definition.
  - **Variants**: with-prior-Q and without-prior-Q, with implementation status.
  - **Shipping-use purpose**: how the benchmark informs model selection for the wearable live-assistant camera product.
- Keep the Judge and Scoring section but update it to reflect cross-family judge as default (see Phase 3b).
- Keep the Related Literature Positioning section but trim it; it's supporting context, not top-level identity.
- Update the Conflict of Interest section with anonymized language.

### 2c. `docs/methodology.md` rewrite

- Describe the current implementation as **benchmark v1's first runnable slice**.
- Define the scored task in benchmark language: prior-vs-current visual-context selection.
- Replace `current-vs-stale` benchmark-facing terminology with `prior-vs-current visual context`. The `has_stale` deprecated alias in `core/scoring.py` can remain as a code-level compatibility name; update the methodology prose to use the benchmark terminology.
- Update CLI invocation examples to show `--model` and `--judge-model` flags.
- State the text-proxy caveat explicitly: v1 is text-only, visual inputs are planned, the current implementation is a proxy for the real benchmark task.

### 2d. `docs/limitations.md` rewrite

Keep only **real** limitations. Delete hedges that fight the benchmark identity.

Keep:
- Small v1 seed set.
- Scenarios derived from feedback on one model.
- Text-proxy caveat (v1 is text; visual inputs planned).
- Partial variant coverage (with-prior-Q implemented; without-prior-Q planned).
- Judge-family caveat (only if not resolved by Phase 3b; if cross-family judge is default, the caveat becomes "same-family comparison mode is available but carries self-preference risk").

Delete:
- "This experiment is not a benchmark."
- "Not a model ranking."
- "Not a claim about all reference-resolution behaviors" in its current hedging form. Keep a tighter version that says the benchmark scopes to visual-context selection, not reference resolution broadly.

### 2e. `experiments/exp_001/README.md` rewrite

- Position `exp_001` as **benchmark v1's implemented slice**.
- State explicitly that it currently covers the **with-prior-Q** variant.
- Remove any "narrower current-vs-stale framing" language that sets up a v1/v2 conceptual split.

### 2f. `CLAUDE.md`

- Update the "What This Project Is" section to reflect the benchmark identity. Draft: "A visual-context selection benchmark for live-assistant AI systems. Internal-use tool for ranking candidate models that ship in a wearable live-assistant camera product. Measures whether a model anchors its answer to the prior visual context (a prior frame) or the current visual context (the right-now frame). The current implementation is benchmark v1's first runnable slice, covering the with-prior-Q variant."
- Update run-volume language if needed to match the new scenario set.
- Ensure all product references use Phase 1b anonymized terminology.

## Phase 3: Make the benchmark actually pick models

### 3a. `--model` flag on the runner

File: `experiments/exp_001/run.py`.

- Current state: `CONFIG["model_id"] = "claude-sonnet-4-6"` hardcoded at line 41.
- Add a `main()` that parses argparse flags and passes them into `run()` via the existing `config` override path.
- Flags: `--model <id>`, `--judge-model <id>`, `--judge-family <claude|openai>`, `--trials <int>`, `--output-dir <path>`. All optional; missing flags fall back to CONFIG defaults.
- The `if __name__ == "__main__": run()` block becomes `if __name__ == "__main__": main()`.
- No behavior change when no flags are passed.

### 3b. Cross-family judge support

Current state: `core/llm_judge.py` pins judge at `claude-sonnet-4-6` (line 28). Same-family as the model under test.

- Add `openai` to `requirements.txt`.
- Add `OPENAI_API_KEY` to `.env.example` with a comment explaining it is required for the default cross-family judge.
- Introduce a judge-adapter abstraction. Two acceptable shapes:
  1. Thin `JudgeAdapterBase` with `ClaudeJudgeAdapter` and `OpenAIJudgeAdapter` subclasses, each exposing a `query(messages, system, config)` method compatible with the existing `ClaudeAdapter.query` signature.
  2. A single adapter factory that returns a Claude-shaped or OpenAI-shaped client based on a `judge_family` parameter.
- Default judge family: **`openai`**, with a current GPT-4 or GPT-4o variant. **Verify the exact model string against OpenAI's current API before pinning.** Do not guess. If unsure which variant to pin, stop and ask.
- Keep the Claude Sonnet judge usable as a same-family comparison mode. The `--judge-family claude` flag should route to it.
- The 4-policy rubric inside the judge prompt stays as-is. The project-facing documentation describes the scored decision as prior-vs-current, while the judge internals still emit one of four tags. v1 pass/fail remains `selected_policy == target_policy`, and target_policy for v1 scenarios is always `prior` or `current`.
- Update `docs/limitations.md` §Judge reliability: cross-family is default; same-family fallback carries self-preference caveat.
- Update `docs/concept_v0_2.md` §Judge and Scoring.

### 3c. Replace sc-01 and sc-02

Current state: `experiments/exp_001/scenarios.json` contains four scenarios. sc-01 and sc-02 are retrieval/abstain-shaped (user asks about previously uploaded videos; model denies access). These do not match the v1 scored surface (prior-vs-current visual-context selection). sc-03 (library reach-back) and sc-04 (desk → kitchen current-anchor) stay.

Replace sc-01 with a **holding-an-object context-selection scenario**:

- Turn 1 user: describes holding a screwdriver with a specific task context; asks a question about the screwdriver grip or use.
- Turn 2 user: has switched to holding a hammer; asks "am I holding this correctly?" (ambiguous referent; current-anchor is correct).
- Target policy: `current`.
- `authoring_basis: extended_from_pilot`.
- `source_example_id: ex-09` (flagship current-policy quote in the inventory).
- `surface: wearable_live_frame`.
- Turn 3 repair anchor: "I mean, the hammer I'm holding now, not the screwdriver."

Replace sc-02 with a **room-shift context-selection scenario**:

- Turn 1 user: in the bedroom; asks a question about a bedroom-context referent (e.g., what picture should hang above the bed).
- Turn 2 user: has walked to the kitchen; asks "what art should we hang in here?" (ambiguous referent; current-anchor is correct).
- Target policy: `current`.
- `authoring_basis: extended_from_pilot`.
- `source_example_id: ex-09`.
- `surface: wearable_live_frame`.
- Turn 3 repair anchor: "I mean, the kitchen walls I'm looking at now, not the bedroom."

Update `expected_answers.json` in lockstep. For each new scenario, populate `current_answers` and `prior_answers` with concrete tokens; leave `clarify_indicators` and `abstain_indicators` empty or near-empty.

Update `PILOT_CORPUS_INVENTORY.md` to note that sc-01 and sc-02 in the prior shape are superseded, and the new scenarios use `extended_from_pilot` anchored to ex-09.

**Do not invent verbatim pilot quotes for these scenarios.** The `authoring_basis: extended_from_pilot` is the honest tag. The specific objects (hammer, art) are extensions from the pattern ex-09 describes, not from verbatim pilot content.

### 3d. Image-input seam

- Add optional `turn_1_image: str | None = None` and `turn_2_image: str | None = None` to the `Scenario` dataclass in `experiments/exp_001/run.py`.
- Update the schema docstring to document the new fields.
- Plumb the fields through `_run_one_trial` so that when images are provided (future v1.1), they can attach to the message payload. For v1, both fields stay None.
- Update `tests/test_scenarios_config.py` to accept the new optional fields.

### 3e. Deferred roadmap cleanup

File: `docs/deferred_roadmap.md`.

- `exp_009` (cross-family judge validation): now shipped as default. Either delete the entry or relabel to note cross-family is shipped; deferred work is now human-rater calibration only.
- Add an entry for the **without-prior-Q variant** as an official benchmark extension, not a speculative future experiment. Frame it as "planned v1.1 coverage extension," not "maybe someday."
- Remove language that reinforces the probe-study framing ("until the pilot inventory is thicker...", "probe study rather than benchmark").

## Phase 4: Tests and verification

1. Update tests that reference:
   - Scenario dataclass shape: add the two optional image fields.
   - Judge family: smoke test for cross-family routing if the adapter abstraction supports it.
   - CLI flag parsing: smoke test for `--model` flag.
   - `has_stale` deprecated alias: no change; continues to emit DeprecationWarning.
2. Run: `.venv/bin/python -m pytest tests/`.
3. All tests pass. No `run.py` invocation with real API keys.

## Phase 5: Framing-reset verification and checkpoint

Before reporting complete, verify the following pass criteria:

- [ ] No top-level doc uses `probe study` as the project identity.
- [ ] No top-level doc says the project is `not a benchmark`.
- [ ] No top-level doc uses the concrete product name or company branding.
- [ ] The `README.md` opening paragraph defines the repo as an internal benchmark for a wearable live-assistant camera product.
- [ ] The benchmark definition appears in `README.md` and `docs/concept_v0_2.md` and includes: what is scored, what is not scored, prior/current context definitions, with-prior-Q and without-prior-Q variants.
- [ ] The docs state that visual recognition is assumed and out of scope.
- [ ] The docs state the current runnable implementation is benchmark v1's first slice, not a separate kind of project.
- [ ] The limitations section treats the small initial seed set as a maturity constraint, not a category downgrade.
- [ ] The Phase 1a anonymization scan comes back clean.
- [ ] All tests pass.

Final actions:

1. Stage but do **not** commit. Leave the repo in a state where the human can review `git diff`.
2. Produce a short summary: what changed (by file path), what was ambiguous (with the judgment call made), what is still blocked on human input.
3. If the OpenAI SDK, API key, or model ID was a guess rather than verified against the OpenAI API, flag it explicitly.

## What not to do

- Do not run experiment commands with real API keys.
- Do not push to the remote.
- Do not edit files outside this repo.
- Do not delete `EXECUTION_PLAN.md`, any `framework-audit-*.md`, `claude-code-handoff-*.md`, `triage-*.md`, `audit/research/*.md`, `PILOT_CORPUS_INVENTORY.md`, `FAILURE_MODES.md`, `SCENARIO_SEEDS.md`, or any `.agent-prompts/*` file.
- Do not reintroduce probe-study framing anywhere in top-level docs.
- Do not use concrete product names or company branding.
- Do not promote `clarify` or `abstain` to v1 scored-surface identity.

## Report at each phase boundary

- **What changed**: bullet list of file paths with one-line descriptions.
- **What was ambiguous**: judgment calls made without strong signal.
- **What is blocked**: anything needing human input before the next phase.
