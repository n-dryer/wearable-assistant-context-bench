# 2026-04-22 Canonical v1 Scenario Audit

This report summarizes a full one-by-one audit of the 101 canonical v1 scenarios.

The full per-scenario audit lives in `2026-04-22-scenario-audit.jsonl`.
The CSV export in `2026-04-22-scenario-audit.csv` is the sortable review view.

## Research basis

- [BetterBench](https://betterbench.stanford.edu/methodology.html): benchmark quality, transparency, and evaluation hygiene
- [HELM](https://crfm.stanford.edu/2022/11/17/helm.html): taxonomy clarity and bounded benchmark claims
- [OpenEQA](https://open-eqa.github.io/assets/pdfs/paper.pdf): product-relevant embodied question design
- [MUCAR](https://aclanthology.org/2025.emnlp-main.760/): single intended interpretation under multimodal ambiguity
- [Clarify When Necessary](https://arxiv.org/abs/2311.09469): when to ask clarifying questions under ambiguity
- [AbstentionBench](https://arxiv.org/abs/2506.09038): when abstention is preferable to a guessed answer
- [Relevant Context for DST](https://arxiv.org/abs/1904.02800): context selection under dialogue shifts

## Audit rubric

1. Single intended interpretation
2. Answerable from the release as shipped
3. Correct target label
4. Product alignment
5. Minimal leakage
6. Answer-key specificity
7. Distinctiveness

## Bank-level findings

- Scenarios audited: **101**
- `current` scenarios with `visual_required` and null image payloads: **0**
- `prior` scenarios marked `text_sufficient`: **24 of 24**
- Auxiliary `clarify` + `abstain` scenarios: **27**

### Counts by scenario action

- `keep`: **101**

### Counts by answer-key action

- `keep`: **99**
- `rewrite`: **2**

### Counts by alignment

- `auxiliary-aligned`: **27**
- `core-aligned`: **74**

### Counts by evidence status

- `answerable-from-release`: **74**
- `unanswerable-by-design`: **12**
- `underspecified-by-design`: **15**

### Most common issue types

- `text_recall_too_easy`: **11**
- `turn_2_too_open_ended`: **6**
- `repair_anchor_leak`: **3**
- `clarify_vs_abstain_blur`: **3**
- `answer_key_misaligned`: **2**
- `answer_key_too_generic`: **2**

## Residual issue families

- `prior` scenarios that are answerable by literal Turn 1 text recall, which measures short-term memory more than contextual reach-back.
- `current` scenarios where Turn 2 is broad enough that multiple reasonable answers could pass without proving the intended context selection.
- Turn 3 repair anchors that restate the Turn 2 answer and could leak the target.
- Auxiliary scenarios where the line between `clarify` and `abstain` is thin and could be scored inconsistently.
- A small number of answer keys that still reward vague pivot language rather than a substantively correct answer.

## Known follow-ups

- Rebalance the `prior` bank away from literal Turn 1 text lookup toward stronger contextual reach-back.
- Tighten open-ended Turn 2 phrasing so only the intended referent can score as correct.
- Rewrite Turn 3 repair anchors that restate the target so the anchor points at the referent without revealing the answer.
- Sharpen the distinguishing cue on `clarify` vs `abstain` boundary scenarios.

## High-priority scenario rows

| Scenario | Action | Severity | Issues |
| --- | --- | --- | --- |
