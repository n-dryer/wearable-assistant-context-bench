# Design Decisions

A short rationale log for the v1 release. Each entry covers a load-bearing design choice and the alternatives considered, so future contributors can tell which choices are deliberate and which are accidental.

For the contract these decisions implement, see [`benchmark_spec.md`](benchmark_spec.md).
For score interpretation, see [`benchmark_notes.md`](benchmark_notes.md).

---

## Why a fixed-content 50-scenario bank plus an adversarial subset

**Decision.** v1 ships 50 scenarios as the Scenario Bank, with a separately-tagged adversarial pack of distractor-rich scenarios as a fourth published configuration.

**Why not 100+ scenarios?** Authoring is the bottleneck. Every scenario passes a 10-point checklist (see [`scenario_authoring_rules.md`](scenario_authoring_rules.md)) plus four programmatic checks (token leakage, object-name leakage, schema, duplication). 50 scenarios authored to that bar buys editorial control; 5,000 noisier scenarios would buy statistical generalization at the cost of editorial quality. The adversarial subset exists because frontier models can ceiling out at the top of a balanced bank. A separately-tagged distractor pack discriminates at the high end without forcing a re-authoring of the core 50.

**Tradeoff acknowledged.** With 50 scenarios and 5 trials per cell, N=250 eval points per condition. CIs catch most of the small-delta noise but the bank itself is small. Future work could grow the bank.

---

## Why eight shift-type categories

**Decision.** `cue_type` ∈ {`object_in_hand`, `object_state`, `sequential_task`, `location`, `object_in_view`, `absent_referent`, `screen_content`, `pre_conversation_recall`}. Distribution: 12 / 8 / 6 / 6 / 5 / 5 / 4 / 4.

**Why these eight?** They cover the failure modes seen in product testing on multimodal coaching assistants (wearable and handheld). `object_in_hand` is the dominant case (the hammer→screwdriver example); `object_state` covers cooking-progress-style shifts; `sequential_task` covers procedural drift; `location` covers room changes; `object_in_view` covers attention shifts within a static scene; `absent_referent` covers the question-about-something-no-longer-visible case; `screen_content` covers tablet/phone shifts that real users hit constantly; `pre_conversation_recall` covers the user asking about state from before the assistant was listening.

**Why not collapse to four or five?** The distribution between current and prior responses is not uniform across categories. A flat collapse would hide which kinds of shifts a candidate handles versus drops. Eight is fine-grained enough to surface that, coarse enough that each category has at least four scenarios.

---

## Why cross-family judging by default + a fixed ranking judge

**Decision.** Per-run primary scores use a cross-family judge auto-resolved from the candidate's family. Cross-candidate ranking uses a single fixed judge across all candidates so candidate quality is isolated from judge strictness.

**Why two layers?** Cross-family judging removes self-preference bias within each run (see JudgeBench, MT-Bench). But it does not isolate candidate from judge across runs: if Run A is "Gemini candidate, GPT judge" and Run B is "GPT candidate, Gemini judge," the 7.2 pp gap between the runs is partly the candidates and partly the judges. The fixed ranking judge fixes that. Every published run also reports a verdict from one constant judge, and that verdict is what the ranking comparison uses.

**Why not just use a single judge?** A single judge can have self-preference bias against candidates from a different family. The dual-judge surface gives both signals: per-run integrity (cross-family) and cross-run comparability (fixed ranking judge).

---

## Why class-balanced primary metric across `current` and `prior` only

**Decision.** Primary score is the mean of `current` accuracy and `prior` accuracy under the `baseline` prompt. `clarify` and `abstain` are reported as auxiliary, not folded into the headline.

**Why balanced?** `current` is 33/50 of the bank (66%); `prior` is 12/50 (24%). A simple hit rate would let a model that always answers from the current frame score ≥66% by ignoring `prior` entirely, exactly the failure mode the benchmark exists to detect. Balancing forces the model to handle both classes.

**Why drop `clarify` (3) and `abstain` (2) from the headline?** Per-class accuracy on 3 or 2 scenarios is too noisy to be ranking-grade. They surface as auxiliary diagnostic rows because clarify-vs-hallucinate and abstain-vs-confabulate failures have different product implications, but they do not enter the headline number.

---

## Why text transcripts and scene descriptions, not raw audio and real video

**Decision.** Audio channel is text transcripts. Camera channel is text scene descriptions. The benchmark does not test acoustic grounding, speaker attribution, ambient audio, or real-video performance.

**Why proxies?** The v1 measurement is **context tracking under a cross-turn situation shift** — whether the model uses the latest perceptual frame or stays anchored to an earlier one. (In standard ML and dialog terminology this is reference resolution under cross-turn context shift.) That measurement is meaningfully testable from text-form transcripts and scene descriptions. Real audio and real video introduce variability in the perceptual front-end that obscures the context-tracking signal. Proxies isolate the measurement.

**Why not both?** Cost and reproducibility. Real-video benchmarks need actual video footage, multimodal API plumbing for video-frame input, and a vision pipeline whose behavior may differ across model families. Text proxies make the benchmark cheap and reproducible across model families with very different perceptual stacks. Future work could add a real-video validation subset to estimate the gap; that's documented as the highest-priority follow-up in [`benchmark_notes.md`](benchmark_notes.md).

---

## Why `--trials 5` with 95% confidence intervals

**Decision.** Every cell runs 5 trials; findings report 95% Wilson confidence intervals on every score.

**Why not 2 or 3?** With 50 scenarios and 2 trials, N=100 per condition. CIs at that N are wide enough to make most sub-5-percentage-point claims indefensible. Bumping to 5 trials brings N to 250 per condition; 95% CIs at that N are narrow enough to interpret most published deltas without hand-waving "treat under 3 pp as noise."

**Why not 10 or more?** Cost. 5 trials × 4 published configurations × 3 conditions × ~70 scenarios (including the adversarial pack) × 2 judges (auto-resolved + fixed ranking) ≈ 8400 trials per published configuration. 10 trials doubles that.

---

## Why named *and* deictic repair anchors

**Decision.** Visible-referent scenarios ship two Turn 3 repair lines: the named anchor (most explicit clarification, the floor on recoverability) and a deictic anchor (pointing-style clarification, the realistic-recovery signal).

**Why both?** Named repair (`"I mean the soldering iron I just picked up, not the multimeter probe"`) measures floor recoverability: given a maximally specific user correction, can the model recover? Deictic repair (`"no, this, what I'm holding now"`) measures realistic recovery, since when users repair, they typically start with deictic emphasis and only escalate to explicit naming after a deictic attempt fails. Reporting both surfaces the gap between floor recoverability and realistic recovery.

**Why name the named anchor as the floor metric?** Floor recoverability is what a candidate must clear to be viable at all. A model that cannot pass the named repair is unrecoverable. Deictic recovery measures the conversational quality on top of that floor.

---

## Why four of the five Scenario Bank runs use same-family judging

**Decision.** The v1 release publishes four same-family Gemini Scenario Bank runs (`baseline`, `baseline-alt`, `ablation-no-camera`, `baseline-deictic-repair`) plus one cross-family Scenario Bank run (`baseline-qwen-cross-family`, Qwen3-VL-Plus candidate with Gemini judge) and one cross-family adversarial run.

**Why?** Cross-family judging is the integrity-preserving default. It removes self-preference bias by ensuring the judge isn't from the same model family as the candidate. The original plan was to run all Scenario Bank configurations cross-family. In practice, API budget exhausted across multiple providers (OpenRouter, OpenAI direct, HF Inference Providers Pro) before all the Scenario Bank runs landed, leaving Gemini-direct via LiteLLM as the only viable transport for the bulk of the Scenario Bank work. Four of those runs ended up Gemini-judging-Gemini, which admits self-preference bias.

**How v1 handles the gap.** The `baseline-qwen-cross-family` run is the cross-family integrity reference for the Scenario Bank: same scenarios, same scoring rules, but a non-Gemini candidate paired with the Gemini judge. The 6.4 percentage-point gap between same-family `baseline` (60.6%) and cross-family `baseline-qwen-cross-family` (54.2%) is the visible self-preference signal. Same-family scoring may be inflated by that much, though candidate quality differs between the two runs and explains some of the gap as well. The Caveats sections in the README, benchmark notes, and dataset card all flag this directly.

**v1.0.x follow-up.** Re-run the four Gemini Scenario Bank configurations under the cross-family judge so the published numbers don't carry the same-family caveat.

---

## Why deferred items are deferred

**Future follow-ups, in priority order:**

1. **Human inter-annotator agreement** on a 25% sample of judge outputs, with Cohen's kappa reported. v1 ships cross-LLM judge agreement only. Human IAA is the strongest defensibility move; it is deferred because it requires recruiting a second labeler and time to label.
2. **Real-video validation** on a held-out sample of scenarios, candidates run with both text-proxy and real video, gap reported as a generalization estimate. Deferred because it requires recording or sourcing real video footage and significant multimodal infrastructure.
3. **Beyond-5-trial multi-seed generalization** at higher trial counts. Deferred because 5 trials with CIs is sufficient for the v1 publication; deeper noise-floor characterization is research-grade.
4. **Full omnimodal stack** (live audio in/out, real-time streaming, interruption handling). Out of scope for the v1 measurement; this is a separate benchmark question.

These are documented in [`benchmark_notes.md`](benchmark_notes.md) under "Open limitations (future follow-ups)" and are mirrored in [`benchmark/v1/dataset_card.md`](../benchmark/v1/dataset_card.md).
