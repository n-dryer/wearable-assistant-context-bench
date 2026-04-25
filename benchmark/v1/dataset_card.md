# Dataset Card: Wearable Assistant Context Benchmark v1

## Dataset description

The Wearable Assistant Context Benchmark is a context-tracking
evaluation set for multimodal wearable assistants. It tests one
specific failure mode: when the user's situation changes between
turns, does the model respond from the current situational evidence,
or does it stay anchored to the prior context?

Each scenario is a 3-turn conversation with a deliberate context
shift between Turn 1 and Turn 2. The shift is visible only in the
camera channel — the user does not announce it in speech. The model
has to integrate scene descriptions with deictic user speech to
determine which context the question refers to. Scene descriptions
are what a vision system would say about a camera frame — shape,
material, color, motion, position — without naming the object
directly.

This is not a coaching benchmark. It does not measure advice quality,
domain expertise, or any aspect of the response other than which
context the model grounded in. See `docs/benchmark_notes.md` for the
full limitations list.

## Languages

English.

## Intended use

Model selection for multimodal wearable assistants. Specifically,
comparing candidate models on context tracking under situational
change between turns.

## Data fields

See [`docs/schema.md`](../../docs/schema.md) for the full field
reference. The bank consists of two files:

- `scenarios.json` — a flat array of 50 scenario objects with audio
  and camera channel content, plus metadata
- `expected_answers.json` — a dict keyed by `scenario_id`, each value
  containing four answer lists used by the judge

The candidate model receives the audio and camera channels; the
judge additionally receives the answer lists and a ground-truth
section naming the actual objects in frame.

## Statistics

| Statistic | Value |
|---|---|
| Total scenarios | 50 |
| Distinct activity domains | 16 |

### Shift-type distribution (`cue_type`)

| Category | Count |
|---|---|
| `object_in_hand` | 12 |
| `object_state` | 8 |
| `sequential_task` | 6 |
| `location` | 6 |
| `object_in_view` | 5 |
| `absent_referent` | 5 |
| `screen_content` | 4 |
| `pre_conversation_recall` | 4 |

### `target_context` distribution

| Label | Count |
|---|---|
| `current` | 33 |
| `prior` | 12 |
| `clarify` | 3 |
| `abstain` | 2 |

### `difficulty_tier` distribution

| Tier | Count |
|---|---|
| `easy` | 15 |
| `medium` | 20 |
| `hard` | 15 |

### Activity-domain coverage

The bank spans 16 distinct activity domains, including kitchen,
workshop, garden, art and craft, automotive, electronics, sports,
fitness, music, household, office, navigation, finance, and
communication. Coverage is broad but shallow — the benchmark does not
measure domain expertise.

## Data creation

The 50 scenarios were authored from scratch following the rules in
[`docs/scenario_authoring_rules.md`](../../docs/scenario_authoring_rules.md).
Each scenario was written within one of the eight shift-type
categories and validated against the six checks below before
inclusion.

The audio channel (user speech) uses natural deictic language without
naming objects, describing visible properties, or announcing context
shifts. The camera channel (image descriptions) describes scene-level
features — shape, material, color, motion, position — without object
names or technique evaluation. The ground-truth channel (answer keys)
is judge-only and uses object names, technique vocabulary, and state
descriptors freely.

## Validation

Every scenario passed six validation checks before being committed:

1. **Token-leakage scan** — Programmatic word-boundary check that no
   `current_answers` or `prior_answers` token appears in any
   user-speech field.
2. **Object-name scan** — Programmatic word-boundary check that no
   common object name (hammer, screwdriver, pan, etc.) appears in any
   image field.
3. **Schema and structural validation** — All required fields
   present, types correct, scenario IDs unique, category metadata
   matching, distributions matching the targets.
4. **Semantic image-identification review** — LLM-driven check that
   each image description identifies its object with high confidence
   to a fresh reader.
5. **Semantic-leakage isolation test** — LLM-driven check that the
   Turn 2 image plus Turn 2 user speech alone (without Turn 1
   context) is not sufficient to answer the question correctly. If a
   scenario passes without Turn 1 context, it is not actually testing
   context tracking.
6. **Cross-scenario duplication check** — Programmatic textual and
   structural overlap scan to surface near-duplicates.

Checks 1, 2, 3, and 6 are run on every PR via
`scripts/validate_scenarios.py`. Checks 4 and 5 are run during
authoring.

## What this benchmark does not measure

The benchmark is narrow on purpose. The following are out of scope by
design:

- **Advice quality.** The judge does not check whether the response
  is correct, safe, or domain-appropriate.
- **Multi-turn dynamics.** The conversation is 3 turns. Long
  conversations and branching dialogue are out of scope.
- **Proactive coaching.** The benchmark only scores responses to
  direct questions.
- **Domain knowledge depth.** Coverage spans 16 domains but is broad
  rather than deep.
- **Latency, cost, audio perception, speaker attribution, addressee
  detection, long-horizon memory.** All out of scope.

## Known v1 limitations and future work

These are real limitations of the v1 release that affect how the
results should be interpreted. Future versions are expected to
address them.

- **Repair-line style is named, not deictic.** The Turn 3 repair line
  explicitly names both the right and the wrong objects. This
  measures floor recoverability, not realistic user correction
  behavior. Future versions may add deictic-only repair lines.
- **Real video is approximated by scene descriptions in text.** The
  camera channel uses text scene descriptions as a stand-in for
  actual video frames. Validation against held-out video footage is
  future work.
- **Inter-annotator agreement is not measured.** All 50 scenarios
  were authored and reviewed by a single annotator using LLM-assisted
  drafting under a fixed authoring rule set. Inter-annotator
  agreement is when two or more people independently label the same
  item and you measure how often they agree; it's the standard way to
  confirm that labels reflect shared understanding rather than one
  person's opinion. Multi-rater validation is future work.
- **The v1 baseline run uses same-family judging.** The committed
  baseline runs Gemini as both candidate and judge. Same-family
  judging can introduce self-preference bias. A cross-family judge
  run is recommended as the next baseline.
- **Single-candidate baseline.** Only one candidate model has been
  run. Multi-model comparison is future work.
- **No camera-channel ablation.** The contribution of the camera
  channel to the primary score has not been quantified by running a
  controlled with-camera vs. without-camera comparison.
- **No formal variance estimation.** Multi-seed reruns to bound score
  noise have not been performed. Treat score deltas under
  approximately 3 percentage points with caution.

Score deltas between models on the same release matter more than
absolute values.

For full discussion of these limitations, see
[`docs/benchmark_notes.md`](../../docs/benchmark_notes.md).

## License

MIT, the same as the rest of the repository. See
[`../../LICENSE`](../../LICENSE).
