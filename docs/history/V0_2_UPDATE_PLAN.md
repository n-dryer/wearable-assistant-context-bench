# v0.2 Update Plan

> Historical. Terminology has since flipped from grounding-state selection to reference-state selection (see CLAUDE_CODE_BUILD_PROMPT.md).

This file tracks the forward-looking repo update around the newer
concept language.

## Core framing

- **Public umbrella term**: multimodal reference resolution under
  context shift
- **Internal task term**: reference-state selection
- **Internal policy labels**: `current`, `prior`, `clarify`, `abstain`
- **Metric name**: simulated repair rate
- **Public strength label while thin cells persist**: probe study

## Current boundary

The repo intentionally has two layers:

- **Active experiment files** keep the narrower current-vs-stale
  framing because that is what `exp_001` actually does.
- **Umbrella and planning files** use the newer reference-resolution
  language and the four-policy schema.
- **Historical records** stay historical and are not normalized for
  style consistency.

## Locked rules

- Replace active uses of `grounding-state selection`.
- Use `reference-state selection` for the internal four-policy schema.
- Use `multimodal reference resolution under context shift` in
  literature-facing or concept-level prose.
- Treat common ground tracking as an adjacent influence, not the task
  identity.
- Keep comparison cases outside core v0.2 scope.
- Keep probe-study framing while `current`, `clarify`, and `abstain`
  remain thin in the pilot inventory.

## Validation checklist

- no active file still uses `grounding-state selection`
- umbrella docs use `reference resolution` in public framing
- umbrella docs use `reference-state selection` for the internal schema
- active `exp_001` docs still describe the current-vs-stale Turn 2 task
- no cosmetic rewrites to historical files
