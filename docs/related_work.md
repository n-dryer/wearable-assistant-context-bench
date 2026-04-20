# Related Work

The benchmark's literature-facing anchor is **reference resolution
under context shift** in multimodal/egocentric settings. The
benchmark's internal task is prior-versus-current visual-context
selection.

This is not identical to common-ground tracking, clarificational-
exchange modeling, or egocentric streaming evaluation, but it sits
near all three. The contribution is positioning, not novelty: the
dimensions of wearable, egocentric, and streaming input already
exist in the literature.

## Main neighbor families

### Broad eval suites

- HELM
- lm-evaluation-harness
- Inspect AI

These provide baseline patterns for evaluation harness structure,
result organization, and hybrid scoring. This repo is much smaller
and does not aim to be a general suite.

### Interactive and agent-style evaluation

- SWE-bench
- τ-bench

Examples of multi-step evaluation design. The current benchmark
does not test tool use or long-horizon agent execution.

### Multimodal reference resolution and adjacent dialogue work

- Common Ground Tracking in Multimodal Dialogue
- "What are you referring to?"
- Literature on clarificational exchanges

These are the closest conceptual neighbors. They inform when a
system should resolve a reference directly, when it should ask a
follow-up, and how dialogue context keeps multiple candidate
states live at once.

### Multimodal and egocentric benchmark neighbors

- ClearVQA
- WAGIBench
- TeleEgo
- StreamingBench
- OmniMMI
- RIVER

These benchmarks cover grounded multimodal understanding, live or
streaming context, and egocentric settings. They are neighbors,
not direct precedents.

## What this project borrows

- hybrid rule-plus-judge scoring
- structured scenario definitions with pinned answer sets
- explicit limitations around judge reliability
- provenance-aware scenario construction
- a reproducibility manifest per run

## What is distinctive here

- a frozen v1 benchmark set for internal model selection
- prior-versus-current visual-context selection as the scored
  surface, with a default ranking condition and balanced Turn 2
  accuracy as the primary score
- two official variants (with-prior-Q and without-prior-Q), with
  the without-prior-Q subcases preserved even before
  implementation
- an intervention axis that is kept policy-neutral rather than
  hard-coding current-state behavior

## Reference handling

Detailed citations and benchmark-specific notes live in
`audit/research/`. The public docs keep discussion at the family
level; the goal is honest positioning, not an exhaustive survey.
