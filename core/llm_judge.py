"""LLM-as-judge using Claude Sonnet 4.6.

This module implements the semantic half of the hybrid scoring scheme. The
judge reads a Turn 2 response alongside the current-state and stale-state
answer lists and returns a structured verdict about whether the response
grounded on the up-to-date context.

G-Eval style prompting is used: the judge is asked to reason step by step,
then emit a JSON verdict. The judge model and temperature are fixed for
reproducibility.

Self-preference caveat: the judge and the model under test are both
Claude. Cross-family judge validation (e.g. GPT-4 judging Claude) is
deferred to exp_009 per docs/deferred_roadmap.md. Interpret all judge
verdicts with that limitation in mind.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

from core.models import ClaudeAdapter, ModelConfig


JUDGE_MODEL_ID = "claude-sonnet-4-6"
JUDGE_TEMPERATURE = 0.0
JUDGE_MAX_TOKENS = 1024


JUDGE_SYSTEM_PROMPT = """You are an evaluator scoring an AI assistant's \
response against ground-truth answer lists.

You will be given:
1. A brief description of the scenario and the state change that occurred.
2. The assistant's response being evaluated.
3. A list of CURRENT answers that reflect the up-to-date state.
4. A list of STALE answers that reflect the earlier, overridden state.

Your job: decide whether the response is grounded on the current state.

Reason step by step:
- Which pieces of the response match items in the current list?
- Which pieces match items in the stale list?
- Does the response refuse or hedge instead of answering?
- Is the overall answer consistent with the current state or the stale state?

Then emit a single JSON object on the final line with this exact shape:
{"passed": <true|false>, "reasoning": "<one-paragraph rationale>", \
"confidence": <float in [0, 1]>}

passed=true means the response reflects the current state and does not \
assert the stale state. passed=false means it asserts stale state, \
refuses, or is otherwise ungrounded. Output no text after the JSON object."""


@dataclass
class JudgeVerdict:
    """Structured verdict returned by the LLM judge.

    Attributes:
        passed: Whether the response reflects current state (not stale).
        reasoning: One-paragraph rationale from the judge.
        confidence: Judge self-reported confidence in [0.0, 1.0].
    """

    passed: bool
    reasoning: str
    confidence: float


class LLMJudge:
    """G-Eval style LLM judge backed by Claude Sonnet 4.6.

    Self-preference caveat: both the judge and the model under test are
    Claude family. Agreement between them may be inflated by shared
    training-data priors. Cross-family judge validation is tracked in
    docs/deferred_roadmap.md as exp_009.
    """

    def __init__(
        self,
        adapter: ClaudeAdapter | None = None,
        model_id: str = JUDGE_MODEL_ID,
        temperature: float = JUDGE_TEMPERATURE,
        max_tokens: int = JUDGE_MAX_TOKENS,
    ) -> None:
        """Construct the judge.

        Args:
            adapter: A ClaudeAdapter instance. If None, a default adapter
                is created. Tests inject a stub adapter.
            model_id: Judge model identifier. Pinned to Sonnet 4.6 family.
            temperature: Sampling temperature. Fixed at 0 for reproducibility.
            max_tokens: Upper bound on judge response length.
        """
        self._adapter = adapter if adapter is not None else ClaudeAdapter()
        self._config = ModelConfig(
            model_id=model_id,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    def judge(
        self,
        response: str,
        current_answers: list[str],
        stale_answers: list[str],
        scenario_description: str,
    ) -> JudgeVerdict:
        """Return a verdict on whether the response grounded on current state.

        Args:
            response: The Turn 2 assistant response being scored.
            current_answers: Strings reflecting up-to-date state.
            stale_answers: Strings reflecting earlier, overridden state.
            scenario_description: Brief context so the judge understands the
                state change that occurred between Turn 1 and Turn 2.

        Returns:
            JudgeVerdict with passed, reasoning, and confidence.
        """
        user_message = _build_user_prompt(
            response=response,
            current_answers=current_answers,
            stale_answers=stale_answers,
            scenario_description=scenario_description,
        )

        raw = self._adapter.query(
            messages=[{"role": "user", "content": user_message}],
            system=JUDGE_SYSTEM_PROMPT,
            config=self._config,
        )

        return _parse_verdict(raw)


def _build_user_prompt(
    *,
    response: str,
    current_answers: list[str],
    stale_answers: list[str],
    scenario_description: str,
) -> str:
    """Format the judge user message."""
    current_block = "\n".join(f"- {a}" for a in current_answers) or "- (none)"
    stale_block = "\n".join(f"- {a}" for a in stale_answers) or "- (none)"
    return (
        f"SCENARIO:\n{scenario_description}\n\n"
        f"RESPONSE TO EVALUATE:\n{response}\n\n"
        f"CURRENT ANSWERS (should be reflected):\n{current_block}\n\n"
        f"STALE ANSWERS (should NOT be asserted):\n{stale_block}\n\n"
        "Reason step by step, then emit the JSON verdict."
    )


_JSON_OBJECT_RE = re.compile(r"\{[^{}]*\"passed\"[^{}]*\}", re.DOTALL)


def _parse_verdict(raw: str) -> JudgeVerdict:
    """Extract a JudgeVerdict from the raw judge response text.

    The judge is instructed to end with a JSON object. We search for the
    last such object in the response, which tolerates any step-by-step
    reasoning that precedes it.

    Raises:
        ValueError: If no JSON verdict can be parsed.
    """
    matches = list(_JSON_OBJECT_RE.finditer(raw))
    if not matches:
        raise ValueError(f"Judge response contained no JSON verdict: {raw!r}")

    payload: dict[str, Any] = json.loads(matches[-1].group(0))
    passed_raw = payload.get("passed")
    if not isinstance(passed_raw, bool):
        raise ValueError(f"Judge verdict 'passed' must be bool, got {passed_raw!r}")

    reasoning = str(payload.get("reasoning", "")).strip()

    confidence_raw = payload.get("confidence", 0.0)
    try:
        confidence = float(confidence_raw)
    except (TypeError, ValueError) as err:
        raise ValueError(
            f"Judge verdict 'confidence' not parseable as float: {confidence_raw!r}"
        ) from err
    confidence = max(0.0, min(1.0, confidence))

    return JudgeVerdict(passed=passed_raw, reasoning=reasoning, confidence=confidence)
