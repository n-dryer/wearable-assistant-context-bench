---
license: mit
language:
  - en
pretty_name: Wearable Assistant Context Benchmark v1
task_categories:
  - question-answering
  - conversational
task_ids:
  - conversational-qa
  - open-domain-qa
tags:
  - wearable
  - multimodal
  - reference-resolution
  - context-shift
  - egocentric
  - benchmark
size_categories:
  - n<1K
features:
  - name: scenario_id
    dtype: string
  - name: target_context
    dtype: string
  - name: turn_1_user
    dtype: string
  - name: turn_2_user
    dtype: string
  - name: turn_3_repair_anchor
    dtype: string
splits:
  - name: test
    num_examples: 101
---

# Wearable Assistant Context Benchmark v1

A product benchmark for comparing language models on cross-turn reference
resolution under context change in a wearable multimodal assistant.

## Task

The benchmark measures whether an assistant answers about the right thing
after the user's context changes between turns. The user may move to a new
location, swap objects, switch screens, or ask about something from
earlier in the conversation.

Each scenario is a two-turn conversation. Turn 1 establishes a reference
state. Turn 2 presents a context change and an ambiguous follow-up
question. The model must resolve the referent correctly.

## Dataset

101 scenarios in a flat JSON array at `scenarios.json`.

Distribution by target context:

| Category | Count | Description |
|---|---|---|
| `current` | 50 | Answer refers to the current context (what the user is doing now) |
| `prior` | 24 | Answer refers to an earlier context (what the user was doing before) |
| `clarify` | 15 | Question is ambiguous; model should request clarification |
| `abstain` | 12 | Needed information is absent; model should decline to answer |

## Scoring

Deterministic substring containment against `expected_answers.json`.
Main score is the macro average of per-category accuracy across all four
categories. No LLM judge required for the primary score.

See `docs/benchmark_spec.md` for the full scoring contract.

## Prompt conditions

Three system prompt variants are defined in `interventions.json`:

| Name | Description |
|---|---|
| `baseline` | Minimal system prompt. Default ranking condition. |
| `condition_a` | Policy-selection instruction for visual context disambiguation. |
| `condition_b` | Pre-answer scaffold requiring explicit context identification. |

## Known limits

- Scoring uses substring containment, which does not handle paraphrase
  well. A response with correct meaning but different wording may score
  incorrect. LLM-as-judge scoring is planned for v1.1.
- Prior scenarios test recall of explicit strings from Turn 1. Most can be
  solved by substring matching Turn 1 text. This understates the recall
  demand. Stronger prior scenarios are planned for v1.1.
- Spoken user queries are represented through transcript proxies, not raw
  audio. Audio grounding is not tested in v1.

## Citation

See `CITATION.cff` at the repo root.

## License

MIT. See `LICENSE` at the repo root.
