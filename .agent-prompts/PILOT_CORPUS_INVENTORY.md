# Pilot Corpus Inventory (v0.2)

Status: sweep complete. Final counts computed.

Last updated: 2026-04-19 (sweep complete). Supersession notes
applied 2026-04-19 in the v0.3.0 benchmark-reset pass.

## v0.3.0 supersession note

The v0.2 probe-study framing elsewhere in this file is superseded
by the v0.3.0 **benchmark reset**. The repo's canonical identity is
now an internal **visual-context selection benchmark** (see
`docs/concept_v0_2.md`, `README.md`, and `CLAUDE.md`). This
inventory remains valid as a **corpus finding** record, including
its counts and provenance trail, but two distinctions matter
going forward:

- **Valid corpus finding ≠ runnable v1 benchmark member.** A
  pilot example can be provenance-eligible (strong quote with a
  cited source) and still not be part of the frozen v1 benchmark
  set if it does not match the v1 scored surface of prior-vs-
  current visual-context selection.
- **Runnable v1 scenarios.** sc-03 (ex-08 part 2) and sc-04
  (ex-09) remain pilot-grounded v1 members. sc-01 and sc-02 have
  been **replaced** during the v0.3.0 pass by holding-an-object
  and room-shift scenarios, both `extended_from_pilot`
  extensions of **ex-09**. The old runnable shapes of sc-01 and
  sc-02 were retrieval-shaped (`abstain` when `prior` was
  correct); they did not match the v1 scored surface.
- **ex-01 and ex-02 remain valid corpus findings.** They are
  explicitly **excluded from runnable v1 benchmark membership**
  because they are retrieval-shaped and not visual-context
  selection. They remain recorded in this inventory.

The unchanged v0.2 counts and write-up follow below for
historical reference.

## Intent

Catalog every candidate quote from the pilot corpus against the v0.2 reference-state selection policy taxonomy. The broader concept-level framing for this inventory is multimodal reference resolution under context shift.

Related files:

- `_phase_0a_sources.md` (prior source audit under the old taxonomy)
- `FAILURE_MODES.md` (prior failure mode taxonomy; fm-01, fm-02, fm-03)

This file does not replace `_phase_0a_sources.md`. It adds a v0.2 cross-map and extends with new quotes from the fresh sweep.

## v0.2 Policy Taxonomy (the cells we are testing against)

- `current`: answer from the newest visual state (live frame)
- `prior`: answer from an earlier in-session visual state (reach-back)
- `clarify`: ask a clarifying question because the reference is ambiguous
- `abstain`: decline or say insufficient evidence

Out-of-scope tags:

- `out-of-scope:comparison`: requires integrating current + prior states ("is this the same as before?")
- `out-of-scope:other`: does not concern state selection (speaker ID, hardware capabilities, confidence calibration on single-state input, intent routing, etc.)
- `review-needed`: quote surrounding context insufficient to adjudicate

## Schema

Each quote entry has:

- `source`: file path, author, timestamp where available
- `quote`: verbatim excerpt, anonymized per Phase 0a conventions at public-release step
- `policy_tag`: one of `current`, `prior`, `clarify`, `abstain`, null
- `scope_status`: `in-scope`, `out-of-scope:comparison`, `out-of-scope:other`, `review-needed`
- `ambiguity_type`: `state-selection`, `referent-selection`, `comparison`, `insufficient-context`, null
- `evidence_strength`: `strong`, `usable_with_context`, `weak`
- `clarification_required`: boolean or null when out-of-scope
- `provenance_eligible`: boolean. True when verbatim, located at a cited path, concrete enough to support scenario construction under the 2+ rule
- `notes`: disambiguation, edge-case flags, scope questions

## Clarification-required rubric (v0 draft)

Clarification is required when both:

1. Two or more plausible grounding states OR two or more plausible referents are live in the surrounding dialogue.
2. Neither linguistic cues ("the one I just held", "what I'm looking at now") nor recent dialogue context make one clearly dominant.

Clarification is NOT required when the query is explicitly anchored or only one plausible referent exists in the last turn.

Tag as `review-needed` when the quote itself lacks enough surrounding turns to judge.

## Committed decision rules

Defaults are pre-committed so the inventory doesn't stall on marginal cases:

1. **Thin-cell default.** If any core policy cell (`current`, `prior`, `clarify`, `abstain`) stays under 2 provenance-eligible quotes after cross-map + Jan 22 fetch + full sweep, the v0.2 concept doc defaults to **probe study framing**, not **benchmark**.
2. **Comparison-heavy default.** If `out-of-scope:comparison` is a large share of evidence, call out as **next-phase expansion** in the concept doc. Do not absorb into v0.2.
3. **Abstain scrutiny.** Tag `abstain` only when the quote supports "the right behavior is to say there is not enough information." Do not use `abstain` as a sink for fabrication or confidence-calibration failures.
4. **Split citations when a quote has mixed content.** If one verbatim passage covers both an in-scope and an out-of-scope clause, note both and cite the in-scope clause at the scenario level.
5. **Surface scope (resolved default).** v0.2 scope includes mobile-app-chat surfaces when the failure pattern is reference-state selection. The policy taxonomy is surface-agnostic even if the primary deployment context is wearable or egocentric. Flag surface in notes.
6. **Abstain-adjacent treatment (resolved default).** Quotes about fabrication from weak grounding or confidence calibration on single-state input are tagged `out-of-scope:other`, not `abstain`, per rule 3. Retained for v0.3 consideration.

## Index (after cross-map + Jan 22 fetch)

| ID    | Slug                             | Policy  | Scope              | Strength          | PE?   |
| ----- | -------------------------------- | ------- | ------------------ | ----------------- | ----- |
| ex-01 | session-recap-denial             | prior   | in-scope           | strong            | yes   |
| ex-02 | session-todo-denial              | prior   | in-scope           | strong            | yes   |
| ex-03 | round-2-stateless-phrasing       | null    | out-of-scope:other | weak              | no    |
| ex-05 | background-audio-as-user-tasks   | null    | out-of-scope:other | strong            | no    |
| ex-06 | round-2-false-confidence-framing | null    | out-of-scope:other | usable_w_context  | no    |
| ex-07 | generic-speaker-labels           | null    | out-of-scope:other | strong            | no    |
| ex-08 | hardware-capabilities-unknown    | prior   | in-scope (part)    | usable_w_context  | yes   |
| ex-09 | instructed-to-focus-current      | current | in-scope           | strong            | yes   |

PE = provenance_eligible for v0.2 scenario construction. ex-04 is retired per `_phase_0a_sources.md`.

## Cross-map entries (existing audit)

### ex-01 `session-recap-denial`

- **source**: pilot CEO report (DOCX), Blocker Registry item B-013 (P0), "Chat Cannot Access Uploaded Videos." Surface: mobile app. Category: chat feature.
- **quote**: "Tell me about my day yesterday → 'I'm sorry, but I don't have access to external data sources or the ability to retrieve video information.' I had 12 videos already uploaded and processed."
- **policy_tag**: `prior` (user asks about yesterday; correct policy is reach-back to stored videos)
- **scope_status**: `in-scope` (surface default applied per decision rule 5)
- **ambiguity_type**: `state-selection`
- **evidence_strength**: `strong`
- **clarification_required**: false
- **provenance_eligible**: yes
- **notes**: `prior`-policy failure where the model applied `abstain` when `prior` was correct. Mobile-app chat surface. Included per surface default (decision rule 5). Flag surface in scenario construction.

### ex-02 `session-todo-denial`

- **source**: pilot CEO report (DOCX), Blocker Registry item B-011 (P0), "AI Denies Access to Videos That Exist." Surface: mobile app. Category: chat feature.
- **quote**: "'Generate my to-do list' → 'No videos were provided to extract action items.' Videos exist, are visible in the app, and have already been processed for daily recaps. The AI behaves as if they don't exist."
- **policy_tag**: `prior`
- **scope_status**: `in-scope` (surface default applied)
- **ambiguity_type**: `state-selection`
- **evidence_strength**: `strong`
- **clarification_required**: false
- **provenance_eligible**: yes
- **notes**: Same pattern as ex-01. Mobile-app chat surface.

### ex-03 `round-2-stateless-phrasing`

- **source**: round-2 structured pilot feedback (JSON), pilot-user submission, `comment_what_didnt` field. Timestamp: 2026-03-11.
- **quote**: "The assistant also fails to surface the app's own Daily Recap module and instead tries to process raw video data directly in chat. The agent behaves as stateless until explicitly forced onto a retrieval path, making [the product] feel like two different products depending on how the user phrases the request."
- **policy_tag**: null
- **scope_status**: `out-of-scope:other`
- **ambiguity_type**: null
- **evidence_strength**: `weak`
- **clarification_required**: null
- **provenance_eligible**: no
- **notes**: Pattern observation, not a turn-level example. Concerns intent routing / retrieval-path invocation, not visual-context selection between prior and current frames.

### ex-05 `background-audio-as-user-tasks`

- **source**: pilot CEO report (DOCX), Blocker Registry item B-016 (P0), "Ambient Audio Contamination." Surface: mobile app. Category: recaps.
- **quote**: "Daily recap included 'takeaways' from a podcast playing in the background and dialogue from TV shows I had on. These were presented as my insights and my to-dos. I got tasks like 'Continue research on criminal behavior patterns' from a true crime podcast. The AI has no way to distinguish my voice and activity from background audio."
- **policy_tag**: null
- **scope_status**: `out-of-scope:other`
- **ambiguity_type**: `referent-selection`
- **evidence_strength**: `strong`
- **clarification_required**: null
- **provenance_eligible**: no
- **notes**: Referent selection within a single state (which audio source), not state selection between states. Abstain-adjacent per decision rule 3 but not `abstain` per the abstain-scrutiny rule. Retain for v0.3 consideration.

### ex-06 `round-2-false-confidence-framing`

- **source**: round-2 structured pilot feedback (JSON), pilot-user submission, `comment_what_didnt` field. Timestamp: 2026-03-10.
- **quote**: "When a voice note contains very weak or low-information audio, [the product] still generates a polished structured note, overstating certainty. Generated note output implies more confidence than the source supports. False confidence is more damaging than an honest partial result."
- **policy_tag**: null
- **scope_status**: `out-of-scope:other`
- **ambiguity_type**: `insufficient-context`
- **evidence_strength**: `usable_with_context`
- **clarification_required**: null
- **provenance_eligible**: no
- **notes**: Confidence calibration on thin input. Not state selection.

### ex-07 `generic-speaker-labels`

- **source**: round-2 structured pilot feedback (JSON), pilot-user submission, `comment_what_didnt` field. Timestamp: 2026-03-11. Corresponds to canonical register issue FB-17.
- **quote**: "Transcripts use generic tags such as SPEAKER_00 and SPEAKER_03 instead of named participants, making meeting summaries much less useful."
- **policy_tag**: null
- **scope_status**: `out-of-scope:other`
- **ambiguity_type**: null
- **evidence_strength**: `strong`
- **clarification_required**: null
- **provenance_eligible**: no
- **notes**: Speaker diarization / identity. Fully out of v0.2.

### ex-08 `hardware-capabilities-unknown`

- **source**: pilot-group General chat export. Timestamp: 2026-01-21 01:39:07 -08:00. Author: reviewing PM.
- **quote**: "[voice-chat feature] doesn't have context about the [hardware] itself. I asked about capabilities and it had no idea. […] If I ask about my day or a specific situation, it should know to look at the relevant video. It needs more context about its own interface so questions get answered appropriately."
- **policy_tag**: `prior` (for the "look at the relevant video" clause)
- **scope_status**: `in-scope` (part 2 only; part 1 on hardware capabilities is out-of-scope)
- **ambiguity_type**: `state-selection`
- **evidence_strength**: `usable_with_context`
- **clarification_required**: false
- **provenance_eligible**: yes (for the v0.2-relevant clause if split)
- **notes**: Mixed-content quote. Per decision rule 4, split the citation at the scenario level to isolate "it should know to look at the relevant video." Part 1 (hardware capabilities) stays in fm-03 but does not carry v0.2 weight.

## New quotes from fresh sweep

### ex-09 `instructed-to-focus-current`

- **source**: pilot-group Use Cases 🎯 chat export. Timestamp: 2026-01-22 14:32:07. Author: reviewing PM.
- **quote**: "That is very exciting. I've tried to accomplish this using video mode via ChatGPT or Gemini Live, but those experiences are sub-par. I've noticed when I ask a question about whatever it is I'm doing or looking at, it often responds using context from what it looked at when I first turned it on, and then I have to remind it to focus on what I'm showing it now… which isn't very helpful."
- **policy_tag**: `current` (user's question pertains to NOW, model used THEN)
- **scope_status**: `in-scope`
- **ambiguity_type**: `state-selection`
- **evidence_strength**: `strong`
- **clarification_required**: false
- **provenance_eligible**: yes
- **notes**: Flagship quote for the `current`-policy failure and the **simulated repair rate** metric. Repair burden is explicit in the quote ("I have to remind it"). Source describes competitor-product behavior posted in a pilot chat by the reviewing PM. The wearable product's production assistant runs on a non-Claude production model family, so the failure class transfers. Anonymize competitor product names at public-release step per provenance rule 5. Surrounding context (team member calls it "multi modal speaker diarization") is noted as historical framing drift, not pilot evidence.

Sweep remaining: ~~Use Cases chat (other messages), Bug Reports chat, Feature Requests chat, General chat (beyond ex-08), pilot eval PDFs 01/02/03.~~ **Done 2026-04-19.** See §Sweep outcomes below.

## Sweep outcomes (WhatsApp + pilot eval PDFs)

WhatsApp keyword passes (`remind`, `context`, `scene`, `earlier`, `looking`, `recap`, `yesterday`, `today`, `ask`, `chat`, `AI`, `hallucinat`, `wrong`, `previous`, `voice`) across the four pilot-group chats (Use Cases 🎯, Bug Reports 🐞, Feature Requests 💡, General 👋). Findings:

- **Use Cases 🎯.** No new provenance-eligible quotes beyond ex-09. The 2026-02-01 "Pretty simple use case…accomplished my goal but there were a few minor issues with [the product's] chat" message from reviewing PM is too thin to carry a specific policy signal.
- **Bug Reports 🐞.** Two candidates, both rejected on provenance grounds.
    - 2026-02-19 "there is a recap dated Feb 18 but is from video a few weeks ago" (pilot user): data-freshness / display-labeling bug. Not a visual-context selection failure at model inference; `out-of-scope:other` if recorded.
    - 2026-01-30 "There were no errands yesterday" (pilot user, with attached image): ambiguous between fabrication and wrong-day state-selection. Image not retrievable as text quote; insufficient surrounding turns. Tagged `review-needed` informally, not entered as an example.
- **Feature Requests 💡.** No new visual-context selection quotes. Messages are feature requests (voice assistant availability, privacy opt-outs, upload controls), not turn-level failure observations.
- **General 👋.** No new quotes beyond the 2026-01-21 ex-08 message.

Pilot eval PDFs `01-best-pilot-family-cleanest-final-pdf.pdf`, `02-best-app-feedback-most-complete-v6-4-repro-steps.pdf`, `03-best-app-feedback-best-design-v6.pdf` (authoring path: redacted; pilot feedback report 02 is the primary source). PDF 02 scanned section-by-section (v6.4 has 19 anonymized `FB-NN` items). Findings:

- FB-04 "very weak transcripts still generate confident summaries" maps to ex-06 (already captured).
- FB-13 "voice assistant identity, persona, and hardware context are unstable" maps to ex-08 (already captured).
- FB-16 "intent routing and chat-to-product context bridging" maps to ex-03 stateless-phrasing (already captured). The expanded body ("first-person questions should reliably use the user's known context instead of falling back to a generic answer") is the report author's synthesis voice, not a verbatim pilot user quote, so it does not satisfy the provenance rule on its own. It corroborates the `prior`-policy failure pattern already represented by ex-01 and ex-02.
- FB-17 "speaker labels and transcript queue delays" maps to ex-07 (already captured).
- FB-18 "state presentation in chat and app UI often overstates readiness" includes the observation "the app may show 'Thinking complete' immediately before producing an 'I don't know' fallback," which is a paraphrased pattern observation, not a verbatim user quote. Corroborates the `prior`-policy failure pattern but is not itself provenance-eligible.
- FB-19 "media deletion fails to persist" is a data-persistence bug, `out-of-scope:other`.

No new provenance-eligible quotes emerged from the PDF pass. PDFs 01 and 03 are derivative presentations of the same 19-item register; the authoring path and content are the same family as PDF 02. Spot-check complete.

**Sweep conclusion.** The inventory closes with the same eight example IDs that survived cross-map + Jan 22 fetch. No new quotes were added in the fresh sweep.

## Summary counts (FINAL, after full sweep)

### In-scope counts by policy

- `current`: **1** (ex-09)
- `prior`: **3** (ex-01, ex-02, ex-08 part 2)
- `clarify`: **0**
- `abstain`: **0**

### Out-of-scope counts by reason

- `out-of-scope:comparison`: **0**
- `out-of-scope:other`: **4** (ex-03 intent routing, ex-05 fabrication, ex-06 confidence, ex-07 speaker ID)

### Review-needed count

- **0** (surface-scope default applied; abstain-adjacent default applied)

### Provenance-eligible counts by core policy

- `current`: 1
- `prior`: 3
- `clarify`: 0
- `abstain`: 0

### Ambiguity-type distribution (in-scope + adjacent)

- `state-selection`: 4 (ex-01, ex-02, ex-08, ex-09)
- `referent-selection`: 1 (ex-05, out-of-scope but type-coded)
- `insufficient-context`: 1 (ex-06, out-of-scope but type-coded)
- `comparison`: 0

### Thin cells / blocked claims

Per committed decision rule 1 (thin-cell default):

- `current` cell: **1 quote. THIN. BLOCKED**. Needs at least 1 more from the remaining sweep.
- `prior` cell: **3 quotes. PASSES 2+ threshold.**
- `clarify` cell: **0 quotes. THIN. BLOCKED.** Needs at least 2 from the remaining sweep.
- `abstain` cell: **0 quotes. THIN. BLOCKED.** Needs at least 2 from the remaining sweep.

### What this implies for v0.2 framing

**Probe-study default triggered.** Three of four core policy cells remain below the 2+ threshold after the full sweep. Per committed decision rule 1, v0.2 frames as a **probe study**, not a benchmark. `prior` is the only cell that clears the benchmark-quality threshold (3 provenance-eligible quotes). `current` has 1 provenance-eligible quote (ex-09); `clarify` and `abstain` have 0.

**Dominant corpus character:** state-selection failures between **current** live state and **prior** session state. 4 of 4 in-scope quotes share the `state-selection` ambiguity type. `referent-selection` and `insufficient-context` appear but are out of v0.2 scope. `comparison` is absent.

**Policy asymmetry note.** Pilot evidence skews toward one direction of the state-selection failure: the model answers from stored/prior state when the user's question is about the live/current state (ex-09), or the model fails to retrieve prior state when the user's question calls for it (ex-01, ex-02, ex-08 part 2). `clarify` and `abstain` cells being empty means the probe cannot test whether the assistant appropriately asks for clarification or declines when underspecified. Those policies remain theoretically motivated (from the four-policy taxonomy) but are not pilot-evidence-backed.

## Next sweep actions

All sweep actions complete as of 2026-04-19. Thin-cell default triggered; v0.2 frames as probe study.

1. ~~Jan 22 Use Cases chat flagship quote~~ done (ex-09).
2. ~~WhatsApp: remaining Use Cases chat messages~~ done. No new provenance-eligible quotes.
3. ~~WhatsApp: Bug Reports chat~~ done. Two candidates rejected on provenance or scope grounds.
4. ~~WhatsApp: Feature Requests chat~~ done. No new quotes.
5. ~~WhatsApp: General chat messages beyond ex-08~~ done. No new quotes.
6. ~~Pilot eval PDFs~~ done. No new provenance-eligible quotes; existing quotes corroborated.
7. ~~Compute final summary counts. Apply thin-cell default~~ done. Probe-study default now active.

Next-phase actions (outside the inventory scope):

- Draft `docs/concept_v0_2.md` anchored to these counts and the probe-study framing.
- Update repo-facing files per `V0_2_UPDATE_PLAN.md`.

## Change log

- 2026-04-19 (part 1): initial cross-map of existing Phase 0a audit (7 quotes from `_phase_0a_sources.md` / `FAILURE_MODES.md`). Fresh sweep pending.
- 2026-04-19 (part 2): Jan 22 flagship quote fetched (ex-09) from Use Cases 🎯 chat. Surface-scope and abstain-adjacent defaults applied to resolve pending scope questions. ex-01 and ex-02 promoted from `review-needed` to `in-scope`. Checkpoint before full sweep.
- 2026-04-19 (part 3): full sweep completed across the four pilot-group WhatsApp chats and the pilot eval PDFs. No new provenance-eligible quotes. Three of four core policy cells remain below the 2+ threshold (`current`=1, `clarify`=0, `abstain`=0). Probe-study default per committed decision rule 1 now active for v0.2 framing. `prior` cell is benchmark-quality (3 quotes). Handoff to concept-doc drafting and repo update pass.
