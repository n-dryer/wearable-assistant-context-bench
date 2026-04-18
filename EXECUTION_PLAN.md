# Grounding Evals: v5 Final Plan (Optimized for Demonstration of Understanding)

**Goal:** Ship a public GitHub repo that demonstrates your understanding of eval frameworks and your ability to build and run evals.

**Total time:** 5-7 hours across 1 weekend
**Total cost:** $5-10 in API credits
**Final deliverable:** Public GitHub repo at github.com/n-dryer/grounding-evals

---

## What v5 Is

v5 = Option B (v3 core + 2 pulls from v4) + 3 demonstration-of-understanding adjustments + documented deferred roadmap.

**v3 core (20 fixes from the 32-issue audit):**
Three-pillar structure, 5 D's, three-tier design, pass@1/pass^3, hybrid scoring, grader calibration, 30+ transcripts, equal weights with justification, trivial + cross-model baseline, persistence question type, limitations doc, refusal handling, honest cost estimate, decontamination, three sequential agent prompts, validation script, question-based findings, broken task detection, post-generation edits log, honest README.

**v4 pulls (2 small additions):**
- Fix L: Model version pinning for reproducibility
- Fix M: Temperature=0 for determinism

**v5 demonstration-of-understanding adjustments:**
- Expanded Related Work section
- docs/design_decisions.md
- 5-minute Loom walkthrough

**Explicitly deferred (documented as planned experiments):**
- Fix A: Cross-judge validation → exp_002
- Fix D: Paraphrase sensitivity → exp_003
- Fix Q: Construct validity → exp_004
- Fix S: Response length analysis → exp_005
- Fix K: Rubric validation vs naive judge → exp_006

---

## Phase 0: Prerequisites + Scenario Seeds (15 min)

### Step 0.1: Environment check

```bash
which git python3 gh node
git --version && python3 --version && gh --version
gh auth status
```

If `gh auth status` fails: `gh auth login`

### Step 0.2: Write scenario seeds

```bash
mkdir -p ~/Development/projects/grounding-evals
cd ~/Development/projects/grounding-evals
mkdir -p .agent-prompts

cat > .agent-prompts/SCENARIO_SEEDS.md << 'EOF'
# Scenario Seeds

Each seed is a real-world pattern the author has observed. The agent expands
each into a full scenario with scenarios.json schema.

## Seed 1 (Tier 1, technical)
A portfolio site migrated from React with Tailwind to Svelte with vanilla CSS
in early 2026. Deployment target changed from Vercel to Cloudflare Pages.
Same domain, same solo team.

## Seed 2 (Tier 1, technical)
Dev environment shifted from VS Code Insiders to Cursor with Composer in
February 2026. Same Mac Mini M2 Pro, same project structure.

## Seed 3 (Tier 1, professional_services)
A consulting engagement with fictional Acme Labs shifted mid-sprint from
user research to product strategy. Same client, same 4-week SOW.

## Seed 4 (Tier 1, personal)
Smart home setup moved from IFTTT to Home Assistant on a Raspberry Pi.
Same Philips Hue bulbs and Sonos speakers.

## Seed 5 (Tier 2, technical)
Fictional Meridian Systems pivoted from AWS Lambda Python to Cloudflare
Workers TypeScript in March 2026. Same product requirements, same user base.

## Seed 6 (Tier 2, professional_services)
Fictional Helix Partners engagement expanded scope in week 3. Interview
cadence shifted from 3 founders/week to 2 founders + 1 sales leader/week.
Same project lead.

## Seed 7 (Tier 2, personal)
Exercise routine shifted from morning HIIT to evening strength training in
March 2026. Same gym, same diet approach.

## Seed 8 (Tier 2, technical)
Fictional Beacon Research swapped LangChain for LlamaIndex in February 2026,
migrated Pinecone to Qdrant, kept OpenAI embeddings.

## Seed 9 (Tier 2, professional_services)
Fictional Cascade Labs pivoted from chatbot UX to voice agents mid-Q1.
PM role unchanged, feature scope entirely different.

## Seed 10 (Tier 2, personal)
Reading habit moved from physical books to Kindle Paperwhite in 2026.
PM books remained primary genre, audiobook consumption dropped to zero.

## Seed 11 (Tier 3, multi_domain)
Fictional Northstar Digital (rebranded to Polaris Digital) simultaneously
changed Apex Retail from weekly retainer to project-based engagement.
Account team unchanged, internal manager changed.

## Seed 12 (Tier 3, subtle_detail)
Single medication adjustment: sertraline 50mg to 100mg daily. All other
medications and behavioral recommendations unchanged.
EOF
```

**Review this file. Replace fictional examples with real patterns from YOUR work.** 15 minutes. More specific = better Demonstrative principle.

---

## Phase 1: Directory Scaffold (15 min)

### Step 1.1: Initialize

```bash
cd ~/Development/projects/grounding-evals
git init
git branch -m main
```

### Step 1.2: Create directories

```bash
mkdir -p core experiments/exp_001_conversation_staleness/transcripts docs tests
```

### Step 1.3: Create file placeholders

```bash
# Top-level
touch README.md METHODOLOGY.md LICENSE requirements.txt .gitignore .env.example CONTRIBUTING.md

# Core module
touch core/__init__.py core/scoring.py core/llm_judge.py core/models.py core/report.py

# Experiment files
touch experiments/README.md
touch experiments/exp_001_conversation_staleness/README.md
touch experiments/exp_001_conversation_staleness/scenarios.json
touch experiments/exp_001_conversation_staleness/expected_answers.json
touch experiments/exp_001_conversation_staleness/run.py
touch experiments/exp_001_conversation_staleness/validate_results.py
touch experiments/exp_001_conversation_staleness/findings.md

# Docs (v5 includes design_decisions.md and deferred_roadmap.md)
touch docs/scoring_rubric.md docs/calibration_notes.md docs/limitations.md
touch docs/design_decisions.md docs/deferred_roadmap.md

# Agent prompts
touch .agent-prompts/01_core_infrastructure.md
touch .agent-prompts/02_experiment_content.md
touch .agent-prompts/03_validation_and_review.md

# Tests
touch tests/test_scoring.py tests/test_llm_judge.py
```

### Step 1.4: Verify

```bash
find . -type f -not -path './.git/*' | sort | wc -l
# Expected: 25
```

---

## Phase 2: Write Top-Level Files (30 min)

### Step 2.1: LICENSE

```bash
cat > LICENSE << 'EOF'
MIT License

Copyright (c) 2026 Nate Dryer

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOF
```

### Step 2.2: .gitignore

```bash
cat > .gitignore << 'EOF'
.env
.venv/
venv/
__pycache__/
*.py[cod]
.Python
build/
dist/
*.egg-info/
.cache/
.pytest_cache/
.DS_Store
.vscode/
.idea/
experiments/*/results.json
experiments/*/transcripts/
experiments/*/run_log.txt
experiments/*/calibration_review.md
EOF
```

### Step 2.3: .env.example

```bash
cat > .env.example << 'EOF'
ANTHROPIC_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
EOF
```

### Step 2.4: requirements.txt

```bash
cat > requirements.txt << 'EOF'
anthropic>=0.39.0
openai>=1.50.0
spacy>=3.7.0
rapidfuzz>=3.5.0
sentence-transformers>=2.5.0
numpy>=1.24.0
python-dotenv>=1.0.0
pytest>=7.4.0
EOF
```

### Step 2.5: README.md with expanded Related Work

```bash
cat > README.md << 'EOF'
# Grounding Evals

A starter eval framework measuring whether AI systems correctly ground answers in current context when conditions change over time.

## Status

**v0.1** — Initial scaffold applying 2026 eval best practices. Experiment complete, findings documented. Roadmap for future experiments in [docs/deferred_roadmap.md](./docs/deferred_roadmap.md).

## What This Measures

When AI systems process sequential input (conversations, documents, sessions), they sometimes reference stale context instead of current state. This repo measures that failure mode across 12 scenarios using hybrid scoring (code-based + LLM-as-judge) with transcript review and grader calibration.

## What This Is NOT

- A comprehensive benchmark suite (12 scenarios is MVP scope, not production)
- A replacement for DeepEval, Braintrust, or LangSmith (see Related Work below)
- Validated against human perception (no user studies conducted)
- Statistically significant (small sample, wide confidence intervals)
- A component-level eval (tests end-to-end only)

## Current Experiments

| ID | Domain | Status | Claude Sonnet 4.6 | GPT-4o |
|----|--------|--------|-------------------|--------|
| exp_001 | Multi-turn conversation staleness | Complete | [pending] | [pending] |

## Quick Start

```bash
git clone https://github.com/n-dryer/grounding-evals
cd grounding-evals
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
cp .env.example .env
# Add API keys to .env
cd experiments/exp_001_conversation_staleness
python run.py
```

## Expected Cost

Approximately $5-10 per full run:
- 288 evaluation queries (Claude + GPT-4o) at ~$0.006 each = ~$1.70
- 288 LLM-judge queries (Claude) at ~$0.010 each = ~$2.90
- 48 trivial baseline queries = ~$0.20
- Buffer for retries and iteration: ~$1-5

Re-running with identical inputs costs $0 due to disk caching.

## Related Work

This framework builds on established 2026 eval methodology. Readers looking for production-ready tooling should consider:

- **[DeepEval](https://github.com/confident-ai/deepeval)** — Implements G-Eval and 50+ research-backed metrics with pytest integration. The right choice for production eval pipelines. I considered using it directly and chose to build from scratch because my goal was to demonstrate eval design thinking, not to solve a production problem.

- **[Braintrust](https://www.braintrust.dev/)** — Combines offline eval with production observability. Useful for teams iterating during development and monitoring quality in production.

- **[LangSmith](https://docs.langchain.com/langsmith/evaluation)** — Tracing, offline/online evals, and dataset management with LangChain integration. Good fit for LangChain-based stacks.

- **[OpenAI Evals](https://github.com/openai/evals)** — Open-source framework with eval registry. Good for teams wanting a foundation without building from scratch.

- **[Harbor](https://harborframework.com/)** — Containerized eval infrastructure for running agents at scale. Recommended by Anthropic for agent evaluation.

### Why I Built This From Scratch

I deliberately didn't use an existing framework because the point was to demonstrate I understand the underlying design decisions. A framework user shows they can configure tools. A framework builder shows they understand the tradeoffs those tools encode. For a portfolio artifact, the second is more valuable than the first. For production work, I'd use DeepEval or Braintrust.

The methodology here follows:
- [Anthropic's "Demystifying Evals for AI Agents" (January 2026)](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
- ["A Practical Guide for Evaluating LLMs and LLM-Reliant Systems" (arxiv 2025)](https://arxiv.org/html/2506.13023v1)
- [G-Eval methodology](https://arxiv.org/abs/2303.16634) for LLM-as-judge scoring

## Methodology

See [METHODOLOGY.md](./METHODOLOGY.md) for the three-pillar approach (Datasets, Metrics, Methodology) and [docs/design_decisions.md](./docs/design_decisions.md) for key choices and rationales.

## Walkthrough Video

A 5-minute walkthrough explaining the design is available at [link after recording].

## Why I Built This

I spend a lot of my work talking to language models across multiple sessions. I kept noticing a specific failure: I'd update my project context (new stack, changed scope, different goal), and the model would continue referencing the old state as if nothing had changed.

I wanted to know how often this happens and under what conditions. Public benchmarks don't measure this directly, so I built something that does. The framework is designed to grow through real experiments as new failure modes emerge.

## How This Was Built

The scaffold was generated by three sequential agent prompts in [.agent-prompts/](./.agent-prompts/). The prompts encode my methodology decisions so others can reproduce or critique the approach. Post-generation edits are documented in each prompt's header.

## Repo Structure

```
grounding-evals/
├── README.md, METHODOLOGY.md, LICENSE, CONTRIBUTING.md
├── core/                # Reusable scoring primitives
├── experiments/         # Numbered, self-contained experiments
├── docs/                # Rubric, calibration, limitations, design decisions, roadmap
├── tests/               # Unit tests
└── .agent-prompts/      # Generation prompts with post-edit logs
```

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for how to add new experiments.

## Author

**Nate Dryer** — Senior AI/ML Product Manager
[natedryer.com](https://natedryer.com) | [github.com/n-dryer](https://github.com/n-dryer)
EOF
```

### Step 2.6: CONTRIBUTING.md

```bash
cat > CONTRIBUTING.md << 'EOF'
# Contributing

This framework is designed to grow through numbered experiments. Each new experiment is self-contained and reuses core/ primitives.

## Adding a New Experiment

### Step 1: Create the directory

```bash
mkdir -p experiments/exp_NNN_short_name/transcripts
cd experiments/exp_NNN_short_name
```

Where `NNN` is the next number (exp_002, exp_003, etc.) and `short_name` describes what's tested.

### Step 2: Create standard files

```bash
touch README.md scenarios.json expected_answers.json run.py validate_results.py findings.md
```

### Step 3: Write README.md

Document what the experiment tests, why it matters, and how it relates to prior experiments. If this experiment was motivated by a finding from a previous one, cite it explicitly.

### Step 4: Write scenarios.json

Use the same schema as exp_001. If the experiment requires new fields, document them in the experiment's README.

### Step 5: Write run.py

Import from `core/` — do not copy-paste primitives. The point of the core/ module is reuse.

```python
import sys
sys.path.insert(0, '../..')
from core.scoring import extract_entities, match_against_manifest
from core.llm_judge import judge_response
from core.models import ClaudeAdapter, OpenAIAdapter, ModelInput
```

### Step 6: Write findings.md using the question-based template

Do not invent findings. Use evidence from results.json. Cite scenario IDs.

### Step 7: Update experiments/README.md

Add your experiment to the index table and mark its status.

### Step 8: Update top-level README.md

Add a row to the Current Experiments table.

## Design Principles for New Experiments

- **Self-contained:** Everything needed to run the experiment lives in its folder
- **Reusable:** Import from core/, never copy code
- **Documented:** README explains the question, findings.md answers with evidence
- **Honest:** Limitations section required
- **Numbered:** Sequential numbering makes the growth visible

## Planned Experiments

See [docs/deferred_roadmap.md](./docs/deferred_roadmap.md) for the prioritized list of experiments that would address known limitations.
EOF
```

### Step 2.7: docs/limitations.md

```bash
cat > docs/limitations.md << 'EOF'
# Known Limitations

## Scope

- **End-to-end only:** tests complete model responses, not individual components
- **Synthetic scenarios:** constructed from real seeds, not production logs
- **Small sample:** 12 scenarios × 3 trials × 2 models gives limited statistical power
- **Author-biased domain mix:** skews toward PM/technical/personal contexts

## Methodology

- **Single judge model:** primary judge is Claude Sonnet 4.6, which is also a model being evaluated. Self-preference bias is possible. Mitigation (cross-judge validation) is scheduled for exp_002 — see docs/deferred_roadmap.md.
- **Rubric subjectivity:** rubric is author-designed, not externally validated. Planned exp_006 tests rubric vs naive judgment.
- **Prompt sensitivity:** each scenario uses one prompt formulation. Planned exp_003 tests sensitivity via paraphrased variants.
- **Model version pinning:** exact snapshots (claude-sonnet-4-6-20250929, gpt-4o) used. Model updates invalidate historical comparisons.
- **Determinism settings:** temperature=0 reduces stochastic variance but also reduces natural sampling diversity.

## Measurement Artifacts

- **Response length:** GPT-4o may produce longer responses than Claude, potentially inflating entity-match counts. Length is logged per query. Planned exp_005 analyzes whether length correlates with score.
- **Refusal handling:** refusals scored separately. Inflation possible if models refuse disproportionately.

## What Scores Mean

A composite of 70/100 means: "70% of the time, across 3 trials per question across 12 scenarios, the model's response was judged as grounded in current context by both the code-based and LLM-based graders, using the rubric specified in docs/scoring_rubric.md."

It does NOT mean "70% as useful to users" or "7 out of 10 quality."

## What Would Make This More Rigorous

See docs/deferred_roadmap.md for the specific experiments planned to address each limitation.
EOF
```

### Step 2.8: docs/design_decisions.md

```bash
cat > docs/design_decisions.md << 'EOF'
# Design Decisions

This document captures the key choices made in v0.1 and the reasoning behind each. The goal is to make design tradeoffs explicit so readers can critique or reproduce them.

## Scenario Count: 12 (not 50+)

**Choice:** 12 scenarios in exp_001.

**Reasoning:** Anthropic's eval guide recommends 20-50 as a starting range for mature agents. For an MVP focused on demonstrating methodology, 12 is slightly below that range but sufficient to show:
- Tier distribution (4/6/2)
- Four domains
- Four question types per scenario (48 question instances)
- 3 trials per question (144 per model)

**Tradeoff:** Smaller sample = wider confidence intervals. Addressed by acknowledging statistical limits in findings.md and limitations.md.

## Scoring Weights: Equal (not weighted)

**Choice:** 25 points per question type (grounding, denial, attribute, persistence).

**Reasoning:** No dimension is privileged because all four failure modes represent equivalent product risks. A model that nails grounding but fails persistence incorrectly discards valid context. A model that handles denials but fails attributes gives plausible-sounding wrong answers.

**Tradeoff:** Equal weights don't reflect domain-specific risk profiles. A clinical eval might weight denial higher than attribute. For a general framework, equal weighting is defensible.

## Judge Model: Claude Sonnet 4.6 (not GPT-4o)

**Choice:** Primary judge is Claude Sonnet 4.6.

**Reasoning:** Claude Sonnet 4.6 has strong instruction-following and chain-of-thought reasoning capabilities suitable for rubric-based judgment. It's also the model the author is most familiar with, which reduces rubric design errors.

**Tradeoff:** Self-preference bias risk. Claude judging Claude responses may inflate Claude scores. Mitigation: exp_002 will add cross-judge validation using GPT-4o as secondary judge on Tier 1 and Tier 3 scenarios.

## Trial Count: 3 (not 5 or 10)

**Choice:** 3 trials per question.

**Reasoning:** 3 is the minimum viable for computing pass@1 and pass^3 with meaningful variance measurement. Cost scales linearly with trial count; 3 trials keeps total cost under $10 per full run.

**Tradeoff:** Wide confidence intervals. A 67% pass^3 with n=3 could mean the true rate is anywhere from 30% to 95%. For directional signal, 3 is adequate. For publication-grade findings, 10+ would be needed.

## Temperature: 0 (not default)

**Choice:** Both evaluation and judge models run at temperature=0.

**Reasoning:** Removes one source of non-determinism so variance across trials reflects cache misses or API-side randomness rather than sampling variance.

**Tradeoff:** Loses some information about model behavior distribution. Production users typically run at temperature > 0, so temperature=0 evals don't perfectly represent production conditions.

## Model Version Pinning

**Choice:** Exact snapshot IDs pinned (claude-sonnet-4-6-20250929, gpt-4o).

**Reasoning:** Model updates silently change behavior. Pinning makes results reproducible over time.

**Tradeoff:** Pinned models become stale. This framework records when the pinning was set; future runs with newer models should be treated as separate experiments (exp_002+) rather than direct comparisons.

## Scoring Approach: Hybrid Code + LLM-Judge

**Choice:** Every response scored by both code-based grader and LLM-as-judge.

**Reasoning:** Code-based is fast, cheap, deterministic but brittle to phrasing variations. LLM-as-judge captures nuance but is slower, costs money, and non-deterministic. The combination catches what each misses alone.

**Tradeoff:** Doubles API cost per question. Mitigated by caching. Also introduces the grader-agreement metric as a diagnostic: if code and judge agree, the score is robust; if they disagree, the response needs manual review.

## Expected Answers: Human-Written (not Agent-Generated)

**Choice:** expected_answers.json is written by hand, not by the agent that generated scenarios.

**Reasoning:** If the agent generates both scenarios and expected answers, the broken-task-detection check is circular. Separating them ensures a real human validates that each scenario is solvable.

**Tradeoff:** ~1 hour of manual writing. Worth it for construct validity.

## Why Not DeepEval or Braintrust

**Choice:** Built from scratch instead of adopting an existing framework.

**Reasoning:** The purpose of this repo is to demonstrate understanding of eval design, not to solve a production problem. Using DeepEval or Braintrust would show tool familiarity but hide design reasoning. Building from scratch forces every design decision to be explicit.

**Tradeoff:** Less production-ready than DeepEval. More code to maintain. For production work, DeepEval or Braintrust would be the correct choice.
EOF
```

### Step 2.9: docs/deferred_roadmap.md

```bash
cat > docs/deferred_roadmap.md << 'EOF'
# Deferred Roadmap

This document lists methodology improvements considered during v0.1 design and explicitly deferred to future experiments. Each entry includes:
- What was deferred
- Why it was deferred for v0.1
- Which future experiment will address it
- What triggers prioritization

## exp_002: Cross-Judge Validation

**What:** Run the LLM judge step using a second model (GPT-4o) on Tier 1 and Tier 3 scenarios. Compare agreement between Claude-as-judge and GPT-as-judge.

**Why deferred:** Self-preference bias is a real concern for single-judge evals, but applying cross-judge validation to 12 scenarios is mature-stage practice on a starter-stage dataset. The v0.1 mitigation (documentation in limitations.md) is proportional.

**Why we'd add it:** If exp_001 findings show large gaps between Claude and GPT-4o scores, cross-judge validation would help determine whether that's a real capability difference or a judge bias artifact.

**Prioritization trigger:** Claude-GPT score gap > 15 points in exp_001.

**Research reference:** Anthropic's "Demystifying Evals" guide recommends calibrating LLM-judge graders against human experts; cross-judge is a cheaper proxy.

---

## exp_003: Prompt Sensitivity Analysis

**What:** For 2-4 scenarios, generate paraphrased variants of the grounding question. Run each variant through both models. Measure score variance across variants.

**Why deferred:** Testing 2 scenarios with 2 variants adds ~48 API calls and a new scoring dimension. For v0.1 demonstration, acknowledging prompt sensitivity in limitations.md is sufficient.

**Why we'd add it:** Production evals must account for prompt variations because real users phrase questions differently. If v0.1 scores cluster tightly but production usage shows wild variation, prompt sensitivity is likely the cause.

**Prioritization trigger:** Findings from production deployment of an evaluated model show variance that v0.1 didn't predict.

**Research reference:** 2025 arxiv "Practical Guide" explicitly flags prompt sensitivity as a core methodology concern.

---

## exp_004: Construct Validity Check

**What:** For each question type, test whether trivially-correct responses (e.g., just mentioning the current keyword) achieve high scores. If yes, the question isn't isolating the failure mode it claims to measure.

**Why deferred:** Construct validity is standard research practice but requires additional test responses and human analysis. For v0.1, the four question types are designed with construct validity in mind (denial questions can't be pattern-matched, persistence tests the inverse of grounding).

**Why we'd add it:** If grader disagreement patterns in v0.1 suggest that the code grader is over-rewarding keyword presence, construct validity tests would confirm or refute that.

**Prioritization trigger:** Code grader consistently scores higher than LLM judge on grounding questions by > 20 points, suggesting keyword gaming.

**Research reference:** Classical psychometric construct validity theory; application to LLM evals is nascent.

---

## exp_005: Response Length Confound Analysis

**What:** Measure correlation between response length (characters or tokens) and composite score. If GPT-4o produces systematically longer responses AND longer responses score higher, that's a measurement artifact not a capability signal.

**Why deferred:** v0.1 logs response length per query but doesn't analyze it. Analysis requires findings from a complete run to see if length correlates with score.

**Why we'd add it:** If exp_001 findings show GPT-4o outperforming Claude, length analysis would determine whether that's real capability or just more keywords per response.

**Prioritization trigger:** GPT-4o scores higher than Claude by > 10 points AND GPT-4o average response length exceeds Claude by > 50%.

**Research reference:** LLM-as-judge research has documented length bias (longer responses often score higher regardless of quality).

---

## exp_006: Rubric Ablation (Rubric vs Naive Judge)

**What:** Pick 5 responses. Score each with the full rubric-guided judge AND a naive judge (no rubric, just "score 1-5"). Compare. If rubric scores don't differ from naive scores, the rubric isn't adding value.

**Why deferred:** Non-standard practice. Most eval frameworks trust their rubric by construction. Testing rubric ablation is a methodology refinement that matters more as the framework matures.

**Why we'd add it:** If grader calibration spot-checks reveal that automated scores are systematically off in ways the rubric should prevent, the rubric itself may be flawed.

**Prioritization trigger:** Calibration agreement rate < 70%, suggesting the rubric isn't capturing the right dimensions.

**Research reference:** This is non-standard; I invented the experiment design. A more standard approach would be validating rubric against human expert scores.

---

## Experiments Without Direct v0.1 Motivation

These experiments extend the framework rather than address v0.1 limitations:

### exp_007: Multi-Turn Distance Effect

Does staleness increase with more turns between initial and updated context? Current v0.1 tests 2-state transitions; production use often involves longer histories.

### exp_008: System Prompt Variation

Does an explicit "prioritize current context" instruction in the system prompt improve grounding? This is a product design question, not a model capability question.

### exp_009: Visual Context Grounding

Adapt the methodology to video: DisocclusionBench pattern where the user moves between scenes. Tests whether the methodology transfers to modalities beyond text.

### exp_010: Cross-Session Persona Consistency

Does the model maintain consistent persona across sessions when explicit style preferences are provided? Extension to conversational AI products.

---

## How to Prioritize

When adding a new experiment, ask:
1. Does this address a finding from a prior experiment? (highest priority)
2. Does this test a specific hypothesis I have about model behavior?
3. Does this extend the framework to a new modality or use case?
4. Does this add research-grade rigor without a specific motivating question? (lowest priority)

Category 4 experiments should be deferred indefinitely unless the framework is being used for research purposes. For portfolio or product-informed evaluation, categories 1-3 are sufficient.
EOF
```

### Step 2.10: Commit checkpoint

```bash
git add .
git commit -m "Phase 0-2: directory scaffold, top-level docs, deferred roadmap"
```

---

## Phase 3: Write Agent Prompts (25 min)

Three sequential prompts to reduce agent confusion.

### Step 3.1: Prompt 1 (core infrastructure)

```bash
cat > .agent-prompts/01_core_infrastructure.md << 'PROMPT_EOF'
# Prompt 1 of 3: Core Infrastructure

## Post-Generation Edits Log
- Date executed: [fill in]
- Agent used: [Claude Code / Cursor / other]
- Human edits after agent run: [list or "none"]

## Context

You are scaffolding an LLM eval framework. This is prompt 1 of 3. Focus only on what's specified below.

## About

- Author: Nate Dryer, Senior AI/ML Product Manager
- Repo: github.com/n-dryer/grounding-evals
- Models to test: claude-sonnet-4-6-20250929 and gpt-4o
- All API calls at temperature=0

## Scope

Build METHODOLOGY.md, core/ module, and tests. Do NOT build scenarios or runner (that's prompt 2).

## Files

### METHODOLOGY.md

Required sections (verified by grep):
```
# Grounding Evals Methodology
## Pillar 1: Datasets
## Pillar 2: Metrics
## Pillar 3: Methodology
## What This Does NOT Claim
```

**Intro:** Reference Anthropic's "Demystifying Evals for AI Agents" (Jan 2026), 2025 arxiv "A Practical Guide for Evaluating LLMs," and G-Eval methodology as foundational.

**Pillar 1: Datasets**

5 D's with 2-3 sentences each on this repo's approach:
- Demonstrative: built from real-world seeds in .agent-prompts/SCENARIO_SEEDS.md
- Diverse: 3 tiers × 4 domains
- Decontaminated: fictional names, 2026 dates, unusual combinations
- Dynamic: growth through numbered experiments (see CONTRIBUTING.md)
- Defined scope: explicit in README's "What This Is NOT" section

Three-tier design:
- Tier 1 regression (4 scenarios, expected 90%+)
- Tier 2 capability (6 scenarios, expected 50-70%)
- Tier 3 stretch (2 scenarios, expected <40%)

**Pillar 2: Metrics**

Four question types (2-3 sentences each):
1. Grounding
2. Denial
3. Attribute
4. Persistence

Equal 25-point weighting with this verbatim justification: "No dimension is privileged because all four failure modes represent equivalent product risks. A model that nails grounding but fails persistence incorrectly discards valid context. A model that handles denials but fails attributes gives plausible-sounding wrong answers."

Hybrid scoring:
- Code-based first pass (spaCy NER + rapidfuzz + dependency parsing)
- LLM-judge second pass (G-Eval methodology, Claude Sonnet 4.6)
- Refusal detection runs first; refusals scored separately
- Final score: average of code and judge (excluding refusals)
- Divergence > 0.2 flagged for manual review

Note: cross-judge validation deferred to exp_002 per docs/deferred_roadmap.md.

**Pillar 3: Methodology**

Non-determinism:
- 3 trials per question at temperature=0
- pass@1 and pass^3 reported
- Acknowledge wide CIs at n=3

Grader calibration:
- Manual review of 58 responses (20% of 288)
- Report agreement rates
- Document disagreement patterns

Transcript review:
- All responses saved to transcripts/
- Read at least 30 transcripts
- Tag as correct / incorrect / ambiguous / unexpected

Capability vs regression:
- Tier 1 = regression (catches backsliding)
- Tier 2-3 = capability (shows ceiling)

Broken task detection:
- expected_answers.json written by human before run
- 0% pass rates flagged for manual review

Saturation awareness:
- Discussed in findings if Tier 1 > 95% or Tier 3 < 5%
- Automated detection deferred (not critical for v0.1)

**What This Does NOT Claim** — reference docs/limitations.md

### core/__init__.py

Empty.

### core/scoring.py

Functions:
- `extract_entities(text: str) -> list[str]` — spaCy NER + noun chunks, dedup, filter <3 chars
- `@dataclass GroundingResult` with current_matches, stale_matches, unmatched, extracted, score property
- `match_against_manifest(extracted, current_manifest, stale_manifest, threshold=75) -> GroundingResult` using rapidfuzz
- `detect_denial(text: str) -> Optional[bool]` using spaCy dependency parsing
- `detect_refusal(text: str) -> bool` — regex against refusal patterns
- `extract_attribute(text, vocabulary) -> list[str]`
- `semantic_similarity(text_a, text_b) -> float` — lazy-loaded sentence-transformers
- `measure_response_length(text: str) -> dict` — returns `{chars, tokens_est}` where tokens_est = chars / 4

Type hints, docstrings, edge case handling throughout.

### core/llm_judge.py

G-Eval style:
- `judge_response(question_type, question, response, context, judge_model="claude-sonnet-4-6-20250929") -> dict` returning `{score, rationale, raw_score, is_refusal}`
- Module constant `RUBRIC_PROMPTS` keyed by question_type
- CoT reasoning, structured JSON output, 2 retries
- Temperature=0
- Refusal short-circuit

Judge system prompt:
```
You are an expert evaluator. Score a model's response to a question about whether it correctly grounds in CURRENT context rather than referencing STALE context.

Use chain-of-thought reasoning. Analyze against the rubric, then output a score.

If the response refuses to answer or cites insufficient information, return is_refusal: true without scoring.

Output valid JSON only: {"reasoning": "<analysis>", "score": <1-5>, "is_refusal": <boolean>}
```

### core/models.py

Model adapters with disk caching and version pinning:
- `@dataclass ModelInput(text, system_prompt=None)`
- `@dataclass ModelOutput(text, model_id, length_chars, length_tokens_est)`
- `ModelAdapter` abstract base
- Cache key = sha256(f"{model_id}|{system_prompt}|{text}|temp=0")[:24]
- `ClaudeAdapter(model_id="claude-sonnet-4-6-20250929", temperature=0)`
- `OpenAIAdapter(model_id="gpt-4o", temperature=0)`
- Exponential backoff (max 3 retries)
- Response length recorded

### core/report.py

`generate_report(results_path, output_path)` — reads results.json, produces markdown with per-tier, per-question-type, per-model breakdown, pass@1/pass^3, grader agreements.

### tests/test_scoring.py

Minimum 12 test cases covering extract_entities, detect_denial, detect_refusal, match_against_manifest, measure_response_length.

### tests/test_llm_judge.py

Minimum 4 tests covering rubric prompts present, refusal short-circuit.

## Quality Standards

- Type hints everywhere
- Docstrings with examples on public functions
- Edge case handling
- Professional prose, no emoji

## After Completion

Summary:
1. LOC per file
2. Ambiguities resolved
3. Recommendations before prompt 2
PROMPT_EOF
```

### Step 3.2: Prompt 2 (experiment content)

```bash
cat > .agent-prompts/02_experiment_content.md << 'PROMPT_EOF'
# Prompt 2 of 3: Experiment Content

## Post-Generation Edits Log
- Date executed: [fill in]
- Agent used: [fill in]
- Human edits: [list or "none"]

## Context

Prompt 1 complete. Build experiment content using seeds from .agent-prompts/SCENARIO_SEEDS.md.

## Already Built

- core/ module (scoring, llm_judge, models, report)
- METHODOLOGY.md
- tests/

## Files to Build

### experiments/README.md

Index table with exp_001 plus "Planned Experiments" section referencing docs/deferred_roadmap.md.

### experiments/exp_001_conversation_staleness/README.md

Document:
- What it tests
- How scenarios were built (from SCENARIO_SEEDS.md)
- Tier distribution (4/6/2)
- 4 question types per scenario (48 total)
- 3 trials per question
- Models with exact snapshot IDs
- Run command

### experiments/exp_001_conversation_staleness/scenarios.json

**Build from SCENARIO_SEEDS.md.** Read each seed, expand into full scenario. Use seed's tier, domain, facts verbatim. Do not invent new scenarios.

Decontamination: fictional names from seeds, 2026 dates, unusual combinations.

Schema:

```json
{
  "case_id": "snake_case_NN",
  "tier": 1|2|3,
  "type": "full_change|partial_update|subtle_detail|multi_transition",
  "domain": "technical|professional_services|personal|multi_domain",
  "seed_reference": "Seed N",
  "decontamination_notes": "specific explanation",
  "initial_context": {
    "description": "2-3 sentences",
    "facts": [{"key": "...", "value": "..."}]
  },
  "updated_context": {
    "description": "2-3 sentences",
    "facts": [{"key": "...", "value": "..."}]
  },
  "persistent_facts": [{"key": "...", "value": "..."}],
  "questions": [
    {"id": "q1_grounding", "type": "grounding", "text": "...", "current_answers": [...], "stale_answers": [...]},
    {"id": "q2_denial", "type": "denial", "text": "...", "expected_denial": true, "trap_fact": "..."},
    {"id": "q3_attribute", "type": "attribute", "text": "...", "current_answer": "...", "stale_answer": "...", "attribute_vocab": [...]},
    {"id": "q4_persistence", "type": "persistence", "text": "...", "expected_denial": true, "persistent_fact": "..."}
  ]
}
```

DO NOT include expected_human_answer. Human writes expected_answers.json separately.

### experiments/exp_001_conversation_staleness/run.py

Runner:

1. Load scenarios.json and expected_answers.json
2. For each scenario:
   - For each model (Claude, GPT-4o):
     - For each of 4 questions:
       - For each of 3 trials:
         - Build prompt: system + initial context + updated context + question
         - Query at temperature=0 via core/models.py
         - Save to transcripts/{scenario_id}_{model}_{question_id}_trial_{n}.md
         - Record response_length_chars
         - Check refusal
         - If not refusal: score with code grader AND LLM judge
3. Trivial baseline: 12 × 4 = 48 queries with no context
4. Compute aggregates:
   - pass@1, pass^3 per question
   - Per-tier, per-question-type, per-model composites
   - Grader agreement (code vs judge)
   - Refusal rates per model
   - Length analysis (avg per model)
5. Checkpointing: save partial results.json after each scenario
6. Save final results.json
7. Print progress

System prompt:
```
You are an assistant helping a user with an ongoing project. Below is the project history. The user's situation has evolved from their initial state to their current state. Answer questions based on the user's CURRENT state, not past states. If something was true before but is no longer true, do not reference it as current.
```

### experiments/exp_001_conversation_staleness/validate_results.py

Validates results.json completeness:
- 288 main entries (12 × 2 × 4 × 3)
- 48 baseline entries
- Prints any missing entries
- Returns pass/fail

### experiments/exp_001_conversation_staleness/findings.md

Question-based skeleton (no pre-written findings):

```markdown
# Experiment 001 Findings

## Run Context
- Date: [fill in]
- Models: claude-sonnet-4-6-20250929, gpt-4o
- Settings: temperature=0, trials=3
- Scenarios: 12

## The Five Questions

Answer each with evidence from results.json. Cite specific scenario IDs.

### 1. Which question type had the highest failure rate?
[evidence-based]

### 2. Systematic difference between Claude and GPT-4o?
[evidence-based]

### 3. Did pass^3 differ from pass@1?
[evidence-based]

### 4. Where did code grader and LLM judge disagree most?
[evidence-based]

### 5. Most surprising transcript?
[pick one specific]

## Transcript Review Summary
Read [N] transcripts (target 30+). Tags:
- Correct: [count]
- Incorrect: [count]
- Ambiguous: [count]
- Unexpected: [count]

## Grader Calibration
Manual review of [N]/288 (target 58):
- Code agreement: [%]
- Judge agreement: [%]
- Patterns: [list]

## Saturation Check
- Tier 1: [composite] — [interpretation]
- Tier 2: [composite]
- Tier 3: [composite]

## Open Questions for Future Experiments
Reference docs/deferred_roadmap.md and prioritize which experiment to run next based on observations.

## Limitations Observed During This Run
Beyond docs/limitations.md, any run-specific issues.
```

## Quality Standards

Same as prompt 1.

## After Completion

Summary:
1. Files produced with LOC
2. Scenarios came from which seeds (should be 12/12)
3. Scenarios flagged for human review
4. Recommendations before prompt 3
PROMPT_EOF
```

### Step 3.3: Prompt 3 (validation)

```bash
cat > .agent-prompts/03_validation_and_review.md << 'PROMPT_EOF'
# Prompt 3 of 3: Validation and Review

## Post-Generation Edits Log
- Date executed: [fill in]
- Agent used: [fill in]
- Human edits: [list or "none"]

## Context

Prompts 1 and 2 complete. Validate everything and fill remaining docs.

## Files to Build

### docs/scoring_rubric.md

Full LLM-judge rubric. For each of grounding, denial, attribute, persistence:
- What the judge evaluates
- What 5/3/1 responses look like with examples
- How to handle refusals and ambiguity

Include CoT format.

### docs/calibration_notes.md

Template for grader calibration:
- Why calibration matters
- Target agreement rate (>= 80%)
- How to perform calibration (58 random, read, score 0/1, compare, categorize)
- Template table: scenario_id, question_id, model, trial, code_score, judge_score, my_score, notes
- Example disagreement patterns

### Dry-Run Validation

Without API:
1. Validate scenarios.json schema
2. Verify 12 scenarios, tiers 4/6/2, four domains
3. Verify each scenario has 4 question types
4. Verify seed references exist
5. Syntax check Python files
6. Run pytest on tests/

### Final Readiness Report

Output:
1. Files with LOC
2. Test results
3. Validation results
4. Estimated run cost ($5-10)
5. Estimated run time (45-60 min)
6. Remaining issues for author
7. Readiness: push to GitHub? run eval? what first?
PROMPT_EOF
```

### Step 3.4: Commit

```bash
git add .
git commit -m "Phase 3: Three sequential agent prompts"
```

---

## Phase 4: Execute Agent Prompts (2 hours)

### Step 4.1: Prompt 1

```bash
cd ~/Development/projects/grounding-evals
cat .agent-prompts/01_core_infrastructure.md | pbcopy
claude
```

Paste, wait 15-30 min.

### Step 4.2: Verify prompt 1

```bash
# Three pillars verified
PILLARS=$(grep -c "^## Pillar" METHODOLOGY.md)
[ "$PILLARS" = "3" ] && echo "OK: Pillars" || echo "FAIL: Expected 3, got $PILLARS"

# 5 D's mentioned
grep -c "Demonstrative\|Diverse\|Decontaminated\|Dynamic\|Defined" METHODOLOGY.md

# Python compiles
python3 -m py_compile core/*.py tests/*.py && echo "OK: Python"

# Tests pass
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
pytest tests/ -v
```

### Step 4.3: Update post-edit log and commit

```bash
# Edit .agent-prompts/01_core_infrastructure.md, fill in Post-Generation Edits Log
git add .
git commit -m "Phase 4.1: Core infrastructure"
```

### Step 4.4: Prompt 2

```bash
cat .agent-prompts/02_experiment_content.md | pbcopy
claude
```

Wait 20-30 min.

### Step 4.5: Verify scenarios

```bash
python3 << 'EOF'
import json

data = json.load(open('experiments/exp_001_conversation_staleness/scenarios.json'))
assert len(data) == 12, f"Expected 12, got {len(data)}"

tiers = {}
for s in data: tiers[s['tier']] = tiers.get(s['tier'], 0) + 1
assert tiers == {1: 4, 2: 6, 3: 2}, f"Wrong tiers: {tiers}"

for s in data:
    assert 'seed_reference' in s
    assert 'decontamination_notes' in s
    assert len(s['questions']) == 4
    types = {q['type'] for q in s['questions']}
    assert types == {'grounding', 'denial', 'attribute', 'persistence'}

print("All scenarios valid")
EOF
```

### Step 4.6: Write expected_answers.json by hand

```bash
python3 << 'EOF'
import json

scenarios = json.load(open('experiments/exp_001_conversation_staleness/scenarios.json'))

expected = {
    "metadata": {
        "author_written": True,
        "description": "Human-written expected grounding answers for broken task detection.",
        "date_written": "[fill in]"
    },
    "expected_grounding_answers": []
}

for s in scenarios:
    grounding_q = next(q for q in s['questions'] if q['type'] == 'grounding')
    expected['expected_grounding_answers'].append({
        "scenario_id": s['case_id'],
        "question": grounding_q['text'],
        "expected_answer": "[HUMAN WRITES - your correct answer based on updated_context]",
        "notes": ""
    })

with open('experiments/exp_001_conversation_staleness/expected_answers.json', 'w') as f:
    json.dump(expected, f, indent=2)

print(f"Skeleton created. Fill in {len(expected['expected_grounding_answers'])} answers.")
EOF
```

**Open expected_answers.json and write each expected_answer by hand.** 60 minutes total.

### Step 4.7: Broken task check

```bash
python3 << 'EOF'
import json

expected = json.load(open('experiments/exp_001_conversation_staleness/expected_answers.json'))

problems = []
for e in expected['expected_grounding_answers']:
    if '[HUMAN WRITES' in e['expected_answer'] or len(e['expected_answer']) < 10:
        problems.append(e['scenario_id'])

if problems:
    print(f"BROKEN: {problems}")
else:
    print("All scenarios have human-written expected answers")
EOF
```

### Step 4.8: Commit

```bash
git add .
git commit -m "Phase 4.5: Scenarios + human-written expected answers"
```

### Step 4.9: Prompt 3

```bash
cat .agent-prompts/03_validation_and_review.md | pbcopy
claude
```

Wait 15 min. Review readiness report.

### Step 4.10: Commit

```bash
git add .
git commit -m "Phase 4.9: Scoring rubric, calibration notes, validation"
```

---

## Phase 5: Publish to GitHub (10 min)

```bash
gh repo create n-dryer/grounding-evals --public --source=. --remote=origin \
  --description "Eval framework for context grounding in LLMs. 2026 best practices: three-pillar framework, hybrid scoring, pass@k metrics."

git push -u origin main

gh repo edit n-dryer/grounding-evals \
  --add-topic "llm-evaluation" \
  --add-topic "ai-product-management" \
  --add-topic "context-grounding" \
  --add-topic "eval-framework"

gh repo view n-dryer/grounding-evals --web
```

**Checkpoint: Repo live. Scaffold complete. Shareable.**

---

## Phase 6: Run Experiment (60 min, $5-10)

### Step 6.1: Environment

```bash
cd ~/Development/projects/grounding-evals
source .venv/bin/activate
cp .env.example .env
nano .env   # Add real keys
```

### Step 6.2: Smoke test

```bash
cd experiments/exp_001_conversation_staleness

python3 -c "
import sys
sys.path.insert(0, '../..')
from core.models import ClaudeAdapter, OpenAIAdapter, ModelInput
for Adapter in [ClaudeAdapter, OpenAIAdapter]:
    a = Adapter()
    r = a.query(ModelInput(text='Say test'))
    print(f'{a.model_id}: {r.text[:50]}')"
```

### Step 6.3: Full run

```bash
python run.py 2>&1 | tee run_log.txt
```

### Step 6.4: Validate

```bash
python validate_results.py
```

### Step 6.5: Generate report

```bash
python3 -c "
import sys
sys.path.insert(0, '../..')
from core.report import generate_report
generate_report('results.json', 'auto_report.md')"
```

---

## Phase 7: Real Findings (3 hours)

### Step 7.1: Read 30+ transcripts (1 hour)

```bash
ls transcripts/ | shuf | head -30 > _sample.txt
while read f; do
    clear
    echo "=== $f ==="
    cat "transcripts/$f"
    echo ""
    read -p "Tag [c/w/a/u/s]: " tag
    echo "$f,$tag" >> transcript_tags.csv
done < _sample.txt
```

### Step 7.2: Calibration on 58 responses (1.5 hours)

```bash
python3 << 'EOF'
import json, random, sys
sys.path.insert(0, '../..')

results = json.load(open('results.json'))
entries = []
for s in results['scenarios']:
    for model, trials in s['trials'].items():
        for trial in trials:
            if not trial.get('is_refusal'):
                entries.append({
                    'sid': s['case_id'], 'model': model,
                    'qid': trial['question_id'], 'trial': trial['trial_number'],
                    'response': trial['response'],
                    'code': trial['scores']['code_based'],
                    'judge': trial['scores']['judge_primary']
                })

random.seed(42)
sample = random.sample(entries, min(58, len(entries)))

with open('calibration_review.md', 'w') as f:
    f.write("# Manual Calibration Review\n\nRead each, apply rubric yourself (0 or 1).\n\n")
    for e in sample:
        f.write(f"## {e['sid']} / {e['model']} / {e['qid']} trial {e['trial']}\n")
        f.write(f"**Code:** {e['code']:.2f} | **Judge:** {e['judge']:.2f}\n\n")
        f.write(f"**Response:** {e['response']}\n\n**My score:** ___\n**Notes:** \n\n---\n\n")
EOF
```

### Step 7.3: Fill findings.md (30 min)

Answer all 5 questions with evidence. Reference specific scenario IDs.

### Step 7.4: Update README and commit

```bash
cd ~/Development/projects/grounding-evals
# Update Current Experiments table in README.md with actual scores
nano README.md

git add .
git commit -m "exp_001: real findings, calibration, transcript review"
git push
```

---

## Phase 8: Loom Walkthrough (30 min)

### Step 8.1: Record 5-minute walkthrough

Using Loom (free) or QuickTime:

1. Start recording with repo visible
2. 30 sec: "This is grounding-evals, a starter eval framework I built."
3. 60 sec: Walk through README highlighting "What This Is NOT," methodology summary, and Related Work
4. 90 sec: Open METHODOLOGY.md, point to three-pillar structure and 5 D's
5. 60 sec: Open docs/design_decisions.md, highlight 2-3 key choices
6. 60 sec: Open exp_001 findings.md, cite the most interesting finding
7. 30 sec: Close with deferred_roadmap.md, show what's planned next

Keep it under 5 minutes. No editing needed.

### Step 8.2: Upload and link

```bash
# After uploading to Loom, get the share URL
# Edit README.md to replace [link after recording] with actual URL
nano README.md

git add README.md
git commit -m "Add walkthrough video link"
git push
```

### Step 8.3: Interview prep

Rehearse a 90-second verbal summary:

1. "I built a starter eval framework for context grounding."
2. "Applied 2026 best practices: three-pillar framework, hybrid scoring, pass@k metrics."
3. "Most interesting finding: [specific, evidence-based]"
4. "Intentionally scoped as MVP. Deferred items like cross-judge validation are in the roadmap as planned experiments."
5. "I'd love to hear how you measure context grounding at [company]."

---

## What v5 Delivers

After execution:

- Public GitHub repo (~1800 LOC) with complete scaffold
- Three-pillar METHODOLOGY.md referencing correct sources
- 12 scenarios drawn from real seeds with decontamination
- Hybrid scoring (code + LLM-judge) with temperature=0 determinism
- Model version pinning for reproducibility
- 3 trials per question with pass@1 and pass^3
- Grader calibration on 58 responses
- 30+ transcripts read and tagged
- Honest findings with evidence
- Explicit limitations
- **Related Work section positioning you in ecosystem**
- **docs/design_decisions.md showing conscious choices**
- **docs/deferred_roadmap.md showing disciplined scope**
- **CONTRIBUTING.md showing growth plan**
- **5-minute Loom walkthrough**

## What v5 Explicitly Defers

Documented in docs/deferred_roadmap.md with triggers for prioritization:
- exp_002: Cross-judge validation (self-preference bias check)
- exp_003: Prompt sensitivity analysis
- exp_004: Construct validity check
- exp_005: Response length confound analysis
- exp_006: Rubric ablation

Each deferred item has a specific prioritization trigger, making the roadmap data-driven rather than speculative.

## Time and Cost

- Phase 0-2: 60 min (scaffold, docs)
- Phase 3: 25 min (agent prompts)
- Phase 4: 2 hours (agent execution + human expected answers)
- Phase 5: 10 min (push)
- Phase 6: 60 min (run experiment)
- Phase 7: 3 hours (findings + calibration)
- Phase 8: 30 min (Loom)

**Total: ~7 hours. Cost: $5-10.**

## Why v5 Is Optimal for Your Goal

Your goal is to demonstrate understanding of eval frameworks and execution ability.

v5 accomplishes this through:
- Applied 2026 methodology (understanding)
- Working code with real results (execution)
- Expanded Related Work (ecosystem awareness)
- Design decisions doc (conscious choice-making)
- Deferred roadmap (disciplined scope)
- Loom walkthrough (highest-leverage explanation)

v5 avoids:
- Research-grade rigor on starter dataset (would backfire as overfitted)
- Invented terminology (would reveal inexperience)
- Research-mode practices when PM judgment is being evaluated

The result is a portfolio artifact calibrated to the audience (PM hiring managers, AI/ML leaders), not to the adversary (methodology researchers critiquing your eval).
