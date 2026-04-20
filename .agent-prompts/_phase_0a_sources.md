# Phase 0a Source Audit

## Vocabulary

- **Failure mode**: a category of model error. Primary reference in prose is a kebab-case slug (2-4 words). A stable ID `fm-NN` exists for cross-reference only.
- **Example**: one pilot feedback item mapped to a failure mode. Primary reference in prose is a kebab-case slug. A stable ID `ex-NN` exists for cross-reference only.
- **Stable ID**: the `fm-NN` or `ex-NN` identifier. Used for cross-reference between this audit and `FAILURE_MODES.md`.
- **Slug**: the kebab-case name used as the primary reference in prose.

## Intent

This file is the provenance trail for every example in `FAILURE_MODES.md`. It records sources reviewed, verbatim quotes extracted, and the failure mode each example is assigned to. It does not log rejected alternatives or deliberation.

## Corpus Reviewed

Local filesystem (pilot product repository, internal):

1. Canonical 18-item app-feedback register (CSV, v6) and companion issue-detail CSV with `expected_result`, `actual_result`, and `steps_to_reproduce` fields.
2. Annotated pilot app-feedback report (DOCX, polished version of the canonical register).
3. Structured round-2 pilot feedback (JSON, 10 pilot-user submissions; `pilot_role: end_user`, single pilot user, timestamps span 2026-03-10 to 2026-03-11).
4. Regression audit confirming the 18-issue canonical set.
5. Pilot CEO report (DOCX) containing a Blocker Registry (items B-XXX).

Pilot-program chat history (messaging platform, exports):

6. Use Cases group chat.
7. Bug Reports group chat.
8. General group chat.
9. Feature Requests group chat.

Remote (Google Drive):

10. Pilot report Google Doc (secondary; overlaps substantively with local sources 1-2).

## Anonymization Applied

Removed from public content: product brand name, product hardware codename, company name, third-party model names, competitor product names, firmware and app version strings, pilot-participant phone numbers and messaging IDs, pilot-participant full names. Preserved: structural source references (canonical register, pilot CEO report, pilot-group chat by channel) and abstracted issue identifiers (FB-XX for canonical register, B-XXX for pilot CEO report blocker registry).

## Examples and Mode Assignments

### ex-01 `session-recap-denial` → fm-01 `ungrounded-session-state`

Source file: pilot CEO report (DOCX), Blocker Registry item B-013 (P0), titled "Chat Cannot Access Uploaded Videos." Surface: mobile app. Category: chat feature.

Verbatim (reported as pilot user feedback in the blocker entry):
> "Tell me about my day yesterday → 'I'm sorry, but I don't have access to external data sources or the ability to retrieve video information.' I had 12 videos already uploaded and processed."

### ex-02 `session-todo-denial` → fm-01 `ungrounded-session-state`

Source file: pilot CEO report (DOCX), Blocker Registry item B-011 (P0), titled "AI Denies Access to Videos That Exist." Surface: mobile app. Category: chat feature.

Verbatim:
> "'Generate my to-do list' → 'No videos were provided to extract action items.' Videos exist, are visible in the app, and have already been processed for daily recaps. The AI behaves as if they don't exist."

### ex-03 `round-2-stateless-phrasing` → fm-01 `ungrounded-session-state`

Source file: round-2 structured pilot feedback (JSON), pilot-user submission (`pilot_role: end_user`), `comment_what_didnt` field. Timestamp: 2026-03-11.

Verbatim excerpt (product name redacted inline):
> "The assistant also fails to surface the app's own Daily Recap module and instead tries to process raw video data directly in chat. The agent behaves as stateless until explicitly forced onto a retrieval path, making [the product] feel like two different products depending on how the user phrases the request."

Note: the full `comment_what_didnt` field also contains material relevant to fm-03 (product identity and hardware awareness); only the fm-01-relevant excerpt is cited here.

### ex-05 `background-audio-as-user-tasks` → fm-02 `fabrication-from-weak-grounding`

Source file: pilot CEO report (DOCX), Blocker Registry item B-016 (P0), titled "Ambient Audio Contamination." Surface: mobile app. Category: recaps.

Verbatim:
> "Daily recap included 'takeaways' from a podcast playing in the background and dialogue from TV shows I had on. These were presented as my insights and my to-dos. I got tasks like 'Continue research on criminal behavior patterns' from a true crime podcast. The AI has no way to distinguish my voice and activity from background audio."

### ex-06 `round-2-false-confidence-framing` → fm-02 `fabrication-from-weak-grounding`

Source file: round-2 structured pilot feedback (JSON), pilot-user submission (`pilot_role: end_user`), `comment_what_didnt` field. Timestamp: 2026-03-10.

Verbatim `comment_what_didnt` (product name redacted inline):
> "When a voice note contains very weak or low-information audio, [the product] still generates a polished structured note, overstating certainty. Generated note output implies more confidence than the source supports. False confidence is more damaging than an honest partial result."

### ex-07 `generic-speaker-labels` → fm-03 `deployment-context-ungrounded`

Source file: round-2 structured pilot feedback (JSON), pilot-user submission (`pilot_role: end_user`), `comment_what_didnt` field. Timestamp: 2026-03-11. Corresponds to canonical register issue FB-17, speaker-identity portion only. The co-located transcript-readiness content is out of scope (UI readiness, not grounding).

Verbatim excerpt (the cited tokens are generic labels in model output):
> "Transcripts use generic tags such as SPEAKER_00 and SPEAKER_03 instead of named participants, making meeting summaries much less useful."

### ex-08 `hardware-capabilities-unknown` → fm-03 `deployment-context-ungrounded`

Source file: pilot-group General chat export. Timestamp: 2026-01-21 01:39:07 -08:00. Author: reviewing PM.

Verbatim excerpt (feature codename and hardware name redacted inline):
> "[voice-chat feature] doesn't have context about the [hardware] itself. I asked about capabilities and it had no idea. […] If I ask about my day or a specific situation, it should know to look at the relevant video. It needs more context about its own interface so questions get answered appropriately."
