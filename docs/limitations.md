# Limitations

These limitations apply to the **v1 runnable slice** of the
benchmark.

## Small v1 seed set

The v1 set has 11 scenarios. That is a maturity constraint, not a
category downgrade: the benchmark is real, but small. Results on 11
scenarios are directional and still sensitive to which scenarios
are included.

The set will continue to grow through explicit version extensions
(v2, etc.) under the governance rule in
[docs/concept_v0_2.md](concept_v0_2.md). v1 itself is frozen.

## Scenario-balance caveat

v1's runnable composition is **8 `current` / 3 `prior`**. On that
skew, a trivial "always current" policy would score about 73% raw
accuracy. The primary score is therefore **balanced Turn 2 accuracy**
(mean of per-class accuracy), not raw accuracy. See
[docs/concept_v0_2.md](concept_v0_2.md#primary-benchmark-score).

A future version with closer class balance may revert to raw mean
Turn 2 accuracy.

## Scenarios derived from feedback on one model

The initial scenario seeds come from pilot feedback on a single
production model family. That is the authoring source, not the
benchmark boundary (see the governance rule). But candidate-model
results inherit whatever distributional biases come with that
authoring source.

## Text-proxy caveat

v1 is text. Scenario turns describe scenes rather than delivering
camera frames. The `Scenario` dataclass has `turn_1_image` and
`turn_2_image` slots for future image inputs, but no v1 scenario
uses them. Treat v1 results as a text-proxy for a camera-grounded
task; image-enabled results may differ.

## Partial variant coverage

The benchmark definition has two official variants:
**with-prior-Q** (implemented) and **without-prior-Q** (planned).
v1 only covers with-prior-Q. The three without-prior-Q subcases
(soft, unrelated-prior-question, pure no-Turn-1) are tracked in
[docs/deferred_roadmap.md](deferred_roadmap.md).

## Judge-family caveat

The judge family defaults to `auto`, which assigns the judge to a
different family from the candidate to reduce same-family bias.
That reduces but does not eliminate judge-preference risk.

Cross-family resolution relies on string inference; unknown
candidate families force an explicit `--judge-family` choice. The
same-family Claude-judge path is still available via
`--judge-family claude` but carries the usual self-preference risk.

No human-rater calibration is bundled with v1. That check lives in
[docs/deferred_roadmap.md](deferred_roadmap.md).

## Corpus asymmetry

The pilot corpus is asymmetric:
`current=1`, `prior=3`, `clarify=0`, `abstain=0`. The v1 runnable
set has intentionally dropped the retrieval-shaped `prior` examples
(ex-01, ex-02) because they do not match the v1 scored surface of
prior-vs-current visual-context selection. The two retained
in-scope pilot anchors are ex-08 part 2 (`prior`, retained as sc-03)
and ex-09 (`current`, which the sc-01, sc-02, sc-04 family of
scenarios extends into concrete runnable items).

v1 therefore does not directly test the retrieval-shaped `prior`
failure pattern from the original pilot. That pattern remains a
**valid corpus finding** and is listed as an excluded class; it is
not a benchmark member.

## Adjacent excluded failure classes

Several pilot failure classes are deliberately outside the v1
scored surface:

- retrieval-shaped prior-reach (ex-01, ex-02)
- intent routing / stateless phrasing (ex-03)
- weak-grounding fabrication / false confidence (ex-06)
- background audio leakage into recaps (ex-05)
- speaker identity / diarization (ex-07)

These are tracked in
[docs/deferred_roadmap.md](deferred_roadmap.md) and remain valid
corpus findings even though they are not v1 benchmark members.

## Sample size

Two trials per `(scenario, condition)` cell at temperature `0.0`
support basic stability checking but not strong statistical claims.

## Provenance and anonymization

Pilot feedback sources are private and manually anonymized. Public
docs and the provenance inventory cite the traced examples, but
outside readers cannot independently inspect the raw source corpus.

## Conflict of interest

The author works with the maker of the wearable live-assistant
camera product that generated the pilot corpus on a contract
research basis. The production assistant runs on a non-Claude
production model family. The benchmark is used internally to
compare candidate models for shipping; it is not a leaderboard or
a public ranking of production assistants.
