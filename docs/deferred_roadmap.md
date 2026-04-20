# Deferred Roadmap

These items are outside the frozen v1 benchmark set. Each is a
candidate for a later version extension or a separate evaluation.
v1 stays frozen under the governance rule in
[docs/concept_v0_2.md](concept_v0_2.md).

## Benchmark extensions

### ext_without_prior_q: add the without-prior-Q variant

Add the three without-prior-Q subcases (soft, unrelated-prior-
question, pure no-Turn-1) as a new runnable slice. The
without-prior-Q variant is part of the official benchmark
definition but is not yet implemented.

### ext_rebalance_future: rebalance the scenario set in a future version

The v1 runnable set is 8 `current` / 3 `prior`. The primary score
is balanced Turn 2 accuracy specifically because of this skew. If
additional naturally-grounded `prior`-visual-context scenarios can
be authored (for example, from a later pilot cohort), a closer-
balanced set becomes possible in a future version, and the primary
score may revert to raw mean Turn 2 accuracy at that point.

### ext_v2_scenarios: candidate v2 scenario shapes

A non-exhaustive list of scenario shapes that belong in a future
versioned set, not in v1. Each is authored from pilot-corpus
evidence or from a named cue family, never invented to pad a
score.

- **Multi-hop context shift.** Three or more frames before Turn 2,
  where the correct anchor is two frames back rather than the
  immediately-prior frame. Tests whether candidates default to
  recency.
- **Partial-occlusion return.** An object leaves frame and returns
  partially occluded; the follow-up refers to it. Tests
  departure/return cues with a visual-recognition confound that
  the candidate should resist leaning on.
- **Speaker-shift deixis.** A second speaker enters and uses
  "this" or "here" with a different referent than the primary
  user. Tests whether context-selection tracks the speaker, not
  the latest utterance.
- **Time-of-day temporal shift.** Same room, hours later, lighting
  and contents changed. Tests the temporal cue family without a
  spatial move.
- **Nested prior reference.** Turn 2 refers to "the other one"
  from a prior frame that itself contained two candidates. Tests
  whether the model picks the referent the user actually anchored
  on in Turn 1, not the more salient distractor.

### ext_image_inputs: image-enabled slice

v1 is a text-proxy slice. The `Scenario` dataclass has
`turn_1_image` and `turn_2_image` seams. A later slice can populate
them and route images through the message payload so the benchmark
evaluates against actual camera frames instead of scene
descriptions.

### ext_more_trials: larger trial counts

v1 runs two trials per `(scenario, condition)` cell as a stability
check. A future slice can run more trials per cell to quantify
per-cell variance for a confidence-style summary.

## Judge and scoring

### ext_human_rater_calibration: human-rater policy calibration

Have human raters assign `current` / `prior` / `clarify` /
`abstain` on a subset of Turn 2 responses and use that as a
calibration check for the LLM judge. The `auto` cross-family judge
reduces same-family bias but does not replace human calibration.

### ext_human_pass_fail_calibration: human pass/fail calibration

Parallel to policy-label calibration: collect human pass/fail
judgments for a subset of responses and compare them to the judge
verdict.

### ext_judge_led_authority: judge-led pass authority

Move pass authority more fully to the judge once human calibration
evidence is strong enough to justify it.

## Intervention families

### ext_more_interventions: broader intervention families

- few-shot examples
- explicit clarify-or-abstain instructions
- retrieval-style context injection
- tool-mediated state summaries

Each is a separate intervention family and should be measured
against the benchmark if a production wrapper adopts it.

### ext_retrieval_tools: retrieval and tool-use interventions

Test whether externalizing prior or current visual context through
a retrieval step or a tool call changes context-selection
behavior.

## Adjacent excluded failure classes

The following pilot failure classes are not part of the v1 scored
surface but remain valid corpus findings. Each is a candidate for
its own evaluation.

### ext_retrieval_prior_reach: retrieval-shaped prior-reach

Covers the original ex-01 and ex-02 shapes where the model fails
to reach into stored session videos when asked about yesterday or
a processed session. Measured as retrieval behavior, not
visual-context selection.

### ext_intent_routing: intent routing / stateless phrasing

Covers ex-03: the assistant fails to route first-person questions
through known context and falls back to a generic answer.

### ext_fabrication_from_weak_grounding: weak-grounding fabrication

Covers ex-06: the assistant emits a confident summary from
low-information input, overstating certainty.

### ext_speaker_identity: speaker identity and diarization

Covers ex-07: transcripts use generic speaker tags instead of
named participants.

### ext_ambient_audio_leakage: background-audio leakage into recaps

Covers ex-05: daily recaps treat background audio as user-
attributable content.

### ext_comparison_reference_integration: current-plus-prior
integration

"Is this the same as before?" style questions that require
integrating current and prior visual contexts in a single answer.
Deliberately outside core v1 scope.

## Generalization and drift

### ext_cross_model: cross-model extension

Re-run the benchmark on additional model families beyond the
currently shipped one. This is a generalization check, not a
leaderboard.

### ext_longitudinal_drift: longitudinal model-version drift

Re-run the benchmark across future releases of each candidate
family to see whether context-selection behavior drifts.

### ext_construct_validity_holdout: construct-validity hold-out

Hold out pilot feedback during taxonomy construction, then test
whether the same prior/current visual-context categories still
fit the held-out material.

## Not on the roadmap

- public leaderboard hosting
- automated scenario generation that weakens provenance discipline
- using this repo as a release gate for a production assistant
  external to the owning team's internal model-selection process
