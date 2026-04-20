# Failure Modes

## v0.2 status and policy mapping

**This file is retained for provenance.** v0.2 shifts the primary
failure frame from the three v0.1 failure modes (`fm-01`, `fm-02`,
`fm-03`) to a four-policy taxonomy (`current`, `prior`, `clarify`,
`abstain`). The v0.2 source of truth for scenario construction is
`PILOT_CORPUS_INVENTORY.md`, not this file. See
`docs/concept_v0_2.md` for the v0.2 concept.

The v0.1 examples listed below map to v0.2 policy cells as follows
(per `PILOT_CORPUS_INVENTORY.md`):

| v0.1 example (fm-NN / ex-NN) | Slug                             | v0.2 policy cell        | v0.2 scope status    | Provenance-eligible |
| ---------------------------- | -------------------------------- | ----------------------- | -------------------- | ------------------- |
| ex-01 (fm-01)                | session-recap-denial             | `prior`                 | in-scope             | yes                 |
| ex-02 (fm-01)                | session-todo-denial              | `prior`                 | in-scope             | yes                 |
| ex-03 (fm-01)                | round-2-stateless-phrasing       | -                       | out-of-scope:other   | no                  |
| ex-05 (fm-02)                | background-audio-as-user-tasks   | -                       | out-of-scope:other   | no                  |
| ex-06 (fm-02)                | round-2-false-confidence-framing | -                       | out-of-scope:other   | no                  |
| ex-07 (fm-03)                | generic-speaker-labels           | -                       | out-of-scope:other   | no                  |
| ex-08 (fm-03)                | hardware-capabilities-unknown    | `prior` (part)          | in-scope (part)      | yes                 |
| ex-09 (new, post-sweep)      | instructed-to-focus-current      | `current`               | in-scope             | yes                 |

`ex-04` remains retired. `fm-02` and `fm-03` examples that do not
address state selection are tagged `out-of-scope:other` under v0.2 per
committed decision rule 6 in `PILOT_CORPUS_INVENTORY.md`; they are
retained below for historical traceability but do not drive v0.2
scenarios.

Stable identifiers (`fm-NN`, `ex-NN`) remain as cross-references. The
v0.2 policy cells (`current`, `prior`, `clarify`, `abstain`) are the
primary frame for scenario authoring and scoring.

## Vocabulary

- **Failure mode**: a category of model error. Primary reference in prose is a kebab-case slug (2-4 words). A stable ID `fm-NN` exists for cross-reference only.
- **Example**: one pilot feedback item mapped to a failure mode. Primary reference in prose is a kebab-case slug. A stable ID `ex-NN` exists for cross-reference only.
- **Stable ID**: the `fm-NN` or `ex-NN` identifier. Does not change if the slug is renamed.
- **Slug**: the kebab-case name used as the primary reference in prose.
- **Dropped IDs**: when an example is cut during clustering (fails the 2+ examples rule, or is a borderline fit per CLAUDE.md §Provenance rules), its `ex-NN` is retired and never reused. `ex-04` is currently retired. See `_phase_0a_sources.md` for the provenance trail.

## Source

Failure modes are derived from pilot feedback on a wearable live-assistant camera product, anonymized. Inputs: a canonical app-feedback register, structured round-2 pilot user feedback (JSON submissions, `pilot_role: end_user`), the annotated pilot app-feedback report, a pilot CEO report with a blocker registry, and pilot-group chat history. Scope is narrowed to examples that intersect this framework's grounding focus (scene-tracking, state-change-ignoring, hallucinating objects, now-vs-earlier confusion). Names, company names, participant identifiers, hardware codenames, and version strings are redacted. The audit file `_phase_0a_sources.md` records the provenance trail.

## fm-01: ungrounded-session-state

The assistant answers as if data or session context that the system has processed is absent, or persists an earlier turn's state over the user's current turn.

Examples: `session-recap-denial`, `session-todo-denial`, `round-2-stateless-phrasing`.

### `session-recap-denial` (ex-01, fm-01)

File: pilot CEO report (DOCX), Blocker Registry item B-013 (P0), titled "Chat Cannot Access Uploaded Videos," surface: mobile app, category: chat feature.

Verbatim user quote (reported as pilot user feedback in the blocker registry):
> "Tell me about my day yesterday → 'I'm sorry, but I don't have access to external data sources or the ability to retrieve video information.' I had 12 videos already uploaded and processed."

### `session-todo-denial` (ex-02, fm-01)

File: pilot CEO report (DOCX), Blocker Registry item B-011 (P0), titled "AI Denies Access to Videos That Exist," surface: mobile app, category: chat feature.

Verbatim user quote:
> "'Generate my to-do list' → 'No videos were provided to extract action items.' Videos exist, are visible in the app, and have already been processed for daily recaps. The AI behaves as if they don't exist."

### `round-2-stateless-phrasing` (ex-03, fm-01)

File: round-2 structured pilot feedback (JSON), pilot-user submission (`pilot_role: end_user`) on intent routing and assistant identity, `comment_what_didnt` field.

Verbatim excerpt (product name anonymized):
> "The assistant also fails to surface the app's own Daily Recap module and instead tries to process raw video data directly in chat. The agent behaves as stateless until explicitly forced onto a retrieval path, making [the product] feel like two different products depending on how the user phrases the request."

## fm-02: fabrication-from-weak-grounding

The assistant produces confident, specific output when grounding signal is sparse, ambiguous, or sourced from content that is not the user's own.

Examples: `background-audio-as-user-tasks`, `round-2-false-confidence-framing`.

### `background-audio-as-user-tasks` (ex-05, fm-02)

File: pilot CEO report (DOCX), Blocker Registry item B-016 (P0), titled "Ambient Audio Contamination," surface: mobile app, category: recaps.

Verbatim user quote:
> "Daily recap included 'takeaways' from a podcast playing in the background and dialogue from TV shows I had on. These were presented as my insights and my to-dos. I got tasks like 'Continue research on criminal behavior patterns' from a true crime podcast. The AI has no way to distinguish my voice and activity from background audio."

### `round-2-false-confidence-framing` (ex-06, fm-02)

File: round-2 structured pilot feedback (JSON), pilot-user submission (`pilot_role: end_user`) on thin-input transcripts, `comment_what_didnt` field.

Verbatim (product name anonymized):
> "When a voice note contains very weak or low-information audio, [the product] still generates a polished structured note, overstating certainty. Generated note output implies more confidence than the source supports. False confidence is more damaging than an honest partial result."

## fm-03: deployment-context-ungrounded

The assistant lacks grounded awareness of its product identity, the hardware it is paired with, the user it is assisting, or the identity of speakers in captured audio.

Examples: `generic-speaker-labels`, `hardware-capabilities-unknown`.

### `generic-speaker-labels` (ex-07, fm-03)

File: round-2 structured pilot feedback (JSON), pilot-user submission (`pilot_role: end_user`) on audio transcription, `comment_what_didnt` field. Corresponds to canonical register issue FB-17, speaker-identity portion only (the co-located transcript-readiness portion is out of scope: UI readiness, not grounding).

Verbatim excerpt (generic token names are model output):
> "Transcripts use generic tags such as SPEAKER_00 and SPEAKER_03 instead of named participants, making meeting summaries much less useful."

### `hardware-capabilities-unknown` (ex-08, fm-03)

File: pilot-group General chat, 2026-01-21, author: reviewing PM.

Verbatim excerpt (feature codename and hardware name redacted inline):
> "[voice-chat feature] doesn't have context about the [hardware] itself. I asked about capabilities and it had no idea. […] If I ask about my day or a specific situation, it should know to look at the relevant video. It needs more context about its own interface so questions get answered appropriately."
