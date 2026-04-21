"""LLM-as-judge with cross-family support.

The judge labels each Turn 2 response with exactly one policy from the
four-policy taxonomy: `current`, `prior`, `clarify`, `abstain`. v1's
scored surface is `prior` vs `current`; `clarify` and `abstain` remain
emittable tags for diagnostic visibility but count as wrong for the
primary score (see docs/benchmark_spec.md).

A `JudgeAdapter` abstraction lets the judge run against either the
Claude or OpenAI Messages/Chat APIs. The CLI's default
`--judge-family auto` resolves to a family **different** from the
candidate's (see `resolve_judge_family` and `infer_candidate_family`).
Explicit `--judge-family claude|openai` overrides the cross-family
default.
"""

from __future__ import annotations

import json
import os
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from core.models import ClaudeAdapter, ModelConfig


JUDGE_MODEL_ID_CLAUDE = "claude-sonnet-4-6"
JUDGE_MODEL_ID_OPENAI = "gpt-5.4"
JUDGE_MODEL_ID_GEMINI = "gemini-2.5-flash"
JUDGE_TEMPERATURE = 0.0
JUDGE_MAX_TOKENS = 1024
JUDGE_PROMPT_VERSION = "v1.0.0"


ALLOWED_POLICIES: tuple[str, ...] = ("current", "prior", "clarify", "abstain")


JUDGE_SYSTEM_PROMPT = """You are an evaluator labeling an AI assistant's \
response with exactly one reference-state policy.

The four policies are defined as follows. Each scored response is \
labeled with exactly one:

- `current`: answer from the newest relevant state.
- `prior`: answer from an earlier state on purpose.
- `clarify`: ask a question because the intended reference state is \
ambiguous.
- `abstain`: decline because the available evidence is insufficient.

You will be given:
1. A brief description of the scenario and the state shift that \
occurred between Turn 1 and Turn 2.
2. The Turn 2 user message.
3. The assistant's Turn 2 response being labeled.
4. Four reference answer lists for the scenario (CURRENT, PRIOR, \
CLARIFY indicators, ABSTAIN indicators). These are provided so you can \
see which concrete tokens anchor each policy for this scenario. They \
are not a scoring shortcut: a response can match tokens from one list \
and still be better described by another policy.

Reason briefly about which policy best describes the response, grounded \
in the definitions above.

Then emit a single JSON object on the final line with this exact shape:
{"selected_policy": "<current|prior|clarify|abstain>", \
"rationale": "<one-sentence justification>"}

Output no text after the JSON object. `selected_policy` MUST be exactly \
one of the four policy names."""


@dataclass
class JudgeVerdict:
    """Structured verdict returned by the LLM judge.

    Attributes:
        selected_policy: One of `current`, `prior`, `clarify`, `abstain`.
        rationale: One-sentence justification from the judge.
    """

    selected_policy: str
    rationale: str


class JudgeAdapterBase(ABC):
    """Abstract judge adapter. Implementations wrap a single chat API call."""

    family: str

    @abstractmethod
    def call(self, *, system: str, user: str, model_id: str) -> str:
        """Send a single-shot system+user chat and return raw text."""


class ClaudeJudgeAdapter(JudgeAdapterBase):
    """Claude-backed judge adapter."""

    family = "claude"

    def __init__(
        self,
        adapter: ClaudeAdapter | None = None,
        temperature: float = JUDGE_TEMPERATURE,
        max_tokens: int = JUDGE_MAX_TOKENS,
    ) -> None:
        self._adapter = adapter if adapter is not None else ClaudeAdapter()
        self._temperature = temperature
        self._max_tokens = max_tokens

    def call(self, *, system: str, user: str, model_id: str) -> str:
        config = ModelConfig(
            model_id=model_id,
            temperature=self._temperature,
            max_tokens=self._max_tokens,
        )
        return self._adapter.query(
            messages=[{"role": "user", "content": user}],
            system=system,
            config=config,
        )


class GeminiJudgeAdapter(JudgeAdapterBase):
    """Gemini-backed judge adapter (smoke-test scaffold)."""

    family = "gemini"

    def __init__(
        self,
        adapter: Any | None = None,
        temperature: float = JUDGE_TEMPERATURE,
        max_tokens: int = JUDGE_MAX_TOKENS,
    ) -> None:
        from core.gemini_adapter import GeminiAdapter

        self._adapter = adapter if adapter is not None else GeminiAdapter()
        self._temperature = temperature
        self._max_tokens = max_tokens

    def call(self, *, system: str, user: str, model_id: str) -> str:
        config = ModelConfig(
            model_id=model_id,
            temperature=self._temperature,
            max_tokens=self._max_tokens,
        )
        return self._adapter.query(
            messages=[{"role": "user", "content": user}],
            system=system,
            config=config,
        )


class OpenAIJudgeAdapter(JudgeAdapterBase):
    """OpenAI-backed judge adapter using the Chat Completions API."""

    family = "openai"

    def __init__(
        self,
        client: Any | None = None,
        temperature: float = JUDGE_TEMPERATURE,
        max_tokens: int = JUDGE_MAX_TOKENS,
    ) -> None:
        self._client = client
        self._temperature = temperature
        self._max_tokens = max_tokens

    @property
    def client(self) -> Any:
        if self._client is None:
            from openai import OpenAI

            self._client = OpenAI()
        return self._client

    def call(self, *, system: str, user: str, model_id: str) -> str:
        response = self.client.chat.completions.create(
            model=model_id,
            temperature=self._temperature,
            max_tokens=self._max_tokens,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        choice = response.choices[0]
        message = getattr(choice, "message", None)
        if message is None and isinstance(choice, dict):
            message = choice.get("message")
        if message is None:
            return ""
        content = getattr(message, "content", None)
        if content is None and isinstance(message, dict):
            content = message.get("content")
        return content or ""


class LLMJudge:
    """Four-policy LLM judge. Family defaults to cross-family via `auto`.

    The judge itself does not decide the family; the runner resolves it
    with `resolve_judge_family` and instantiates the correct
    `JudgeAdapterBase` subclass. This class just formats the prompt,
    dispatches through the adapter, and parses the verdict.
    """

    def __init__(
        self,
        adapter: JudgeAdapterBase | None = None,
        model_id: str = JUDGE_MODEL_ID_CLAUDE,
        temperature: float = JUDGE_TEMPERATURE,
        max_tokens: int = JUDGE_MAX_TOKENS,
    ) -> None:
        """Construct the judge.

        Args:
            adapter: A JudgeAdapterBase instance. Defaults to a Claude
                judge adapter, matching the historical default. Tests
                inject a stub adapter.
            model_id: Judge model identifier. Must match the adapter's
                family; the runner enforces this via `resolve_judge_family`.
            temperature: Sampling temperature.
            max_tokens: Upper bound on judge response length.
        """
        self._adapter: JudgeAdapterBase = (
            adapter if adapter is not None else ClaudeJudgeAdapter(
                temperature=temperature, max_tokens=max_tokens
            )
        )
        self._model_id = model_id

    @property
    def family(self) -> str:
        return self._adapter.family

    @property
    def model_id(self) -> str:
        return self._model_id

    def label(
        self,
        response: str,
        scenario_description: str,
        turn_2_user: str,
        current_answers: list[str],
        prior_answers: list[str],
        clarify_indicators: list[str],
        abstain_indicators: list[str],
    ) -> JudgeVerdict:
        """Label the Turn 2 response with one of the four policies."""
        user_message = _build_user_prompt(
            response=response,
            scenario_description=scenario_description,
            turn_2_user=turn_2_user,
            current_answers=current_answers,
            prior_answers=prior_answers,
            clarify_indicators=clarify_indicators,
            abstain_indicators=abstain_indicators,
        )
        raw = self._adapter.call(
            system=JUDGE_SYSTEM_PROMPT,
            user=user_message,
            model_id=self._model_id,
        )
        return parse_verdict(raw)


def infer_candidate_family(model_id: str) -> str | None:
    """Infer the candidate model's family from its `--model` string.

    Returns:
        `"claude"`, `"openai"`, or `None` if the family cannot be
        inferred. The runner errors out on `None` in `--judge-family auto`.
    """
    if not model_id:
        return None
    lowered = model_id.lower()
    claude_markers = ("claude", "sonnet", "opus", "haiku")
    openai_markers = ("gpt", "o1", "o3", "o4")
    gemini_markers = ("gemini",)
    if any(marker in lowered for marker in claude_markers):
        return "claude"
    if any(marker in lowered for marker in openai_markers):
        return "openai"
    if any(marker in lowered for marker in gemini_markers):
        return "gemini"
    return None


def resolve_judge_family(
    requested: str,
    candidate_model_id: str,
) -> tuple[str, str]:
    """Resolve the judge family from the CLI flag and the candidate model.

    Args:
        requested: Value of `--judge-family`: `auto`, `claude`, or
            `openai`.
        candidate_model_id: The `--model` string for the candidate.

    Returns:
        `(resolved_family, resolution_mode)` where `resolution_mode` is
        `"explicit"` or `"auto"`. Used by the report manifest.

    Raises:
        ValueError: If `requested` is not one of the allowed values, or
            if `auto` cannot infer a family for the candidate.
    """
    if requested not in ("auto", "claude", "openai", "gemini"):
        raise ValueError(
            f"--judge-family must be auto, claude, openai, or gemini; "
            f"got {requested!r}"
        )
    if requested in ("claude", "openai", "gemini"):
        return requested, "explicit"
    candidate_family = infer_candidate_family(candidate_model_id)
    if candidate_family is None:
        raise ValueError(
            f"--judge-family auto could not infer the candidate family "
            f"from model string {candidate_model_id!r}. Pass --judge-family "
            "claude, openai, or gemini explicitly."
        )
    # Cross-family: default to openai as the other family for claude/gemini,
    # and claude for openai. (Smoke-test scaffold; the v1 release only
    # promises claude <-> openai.)
    cross = {"claude": "openai", "openai": "claude", "gemini": "openai"}
    return (cross[candidate_family], "auto")


def build_judge(
    family: str,
    model_id: str | None = None,
    adapter: JudgeAdapterBase | None = None,
) -> LLMJudge:
    """Factory: build an LLMJudge for the given family.

    Args:
        family: `"claude"` or `"openai"`.
        model_id: Optional explicit model string; defaults to the
            family's canonical judge model.
        adapter: Optional pre-built adapter (for tests).

    Returns:
        An `LLMJudge` wired to the correct adapter and model.
    """
    if family == "claude":
        resolved_model = model_id or JUDGE_MODEL_ID_CLAUDE
        adapter_ = adapter if adapter is not None else ClaudeJudgeAdapter()
    elif family == "openai":
        resolved_model = model_id or JUDGE_MODEL_ID_OPENAI
        adapter_ = adapter if adapter is not None else OpenAIJudgeAdapter()
    elif family == "gemini":
        resolved_model = model_id or JUDGE_MODEL_ID_GEMINI
        adapter_ = adapter if adapter is not None else GeminiJudgeAdapter()
    else:
        raise ValueError(f"Unknown judge family: {family!r}")
    return LLMJudge(adapter=adapter_, model_id=resolved_model)


def _build_user_prompt(
    *,
    response: str,
    scenario_description: str,
    turn_2_user: str,
    current_answers: list[str],
    prior_answers: list[str],
    clarify_indicators: list[str],
    abstain_indicators: list[str],
) -> str:
    """Format the judge user message."""
    current_block = _format_list(current_answers)
    prior_block = _format_list(prior_answers)
    clarify_block = _format_list(clarify_indicators)
    abstain_block = _format_list(abstain_indicators)
    return (
        f"SCENARIO (Turn 1 context and state shift):\n{scenario_description}\n\n"
        f"TURN 2 USER MESSAGE:\n{turn_2_user}\n\n"
        f"RESPONSE TO LABEL:\n{response}\n\n"
        f"CURRENT ANSWERS (anchors for the `current` policy):\n{current_block}\n\n"
        f"PRIOR ANSWERS (anchors for the `prior` policy):\n{prior_block}\n\n"
        f"CLARIFY INDICATORS (anchors for the `clarify` policy):\n{clarify_block}\n\n"
        f"ABSTAIN INDICATORS (anchors for the `abstain` policy):\n{abstain_block}\n\n"
        "Reason briefly, then emit the JSON verdict."
    )


def _format_list(items: list[str]) -> str:
    if not items:
        return "- (none)"
    return "\n".join(f"- {item}" for item in items)


_JSON_OBJECT_RE = re.compile(r"\{[^{}]*\"selected_policy\"[^{}]*\}", re.DOTALL)


def parse_verdict(raw: str) -> JudgeVerdict:
    """Extract a JudgeVerdict from the raw judge response text.

    The judge is instructed to end with a JSON object. We search for the
    last such object, which tolerates any step-by-step reasoning that
    precedes it.

    Raises:
        ValueError: If no JSON verdict can be parsed or the
            `selected_policy` field is missing or not in the allowed set.
    """
    matches = list(_JSON_OBJECT_RE.finditer(raw or ""))
    if not matches:
        raise ValueError(f"Judge response contained no JSON verdict: {raw!r}")

    try:
        payload: dict[str, Any] = json.loads(matches[-1].group(0))
    except json.JSONDecodeError as err:
        raise ValueError(f"Judge verdict JSON not parseable: {raw!r}") from err

    selected_policy = payload.get("selected_policy")
    if not isinstance(selected_policy, str) or selected_policy not in ALLOWED_POLICIES:
        raise ValueError(
            f"Judge verdict 'selected_policy' must be one of "
            f"{ALLOWED_POLICIES}, got {selected_policy!r}"
        )

    rationale = str(payload.get("rationale", "")).strip()

    return JudgeVerdict(selected_policy=selected_policy, rationale=rationale)


# Silence unused-import warnings when OPENAI_API_KEY isn't required.
_ = os
