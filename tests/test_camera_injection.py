"""Tests for the [Camera:] injection format used by the runner.

These tests exercise the message-construction helpers in benchmark.v1.run
directly. They confirm:
  * `[Camera: ...]` is prepended to the user message when an image is set
  * No camera block is added when the image field is null
  * `context_image` is injected as a separate user-only camera message
    that precedes Turn 1
  * The judge user prompt includes a GROUND TRUTH section when
    `ground_truth_context` is provided
"""

from __future__ import annotations

from typing import Any

import pytest

from benchmark.v1 import run as run_module
from benchmark.v1.run import (
    AnswerSet,
    Scenario,
    _build_context_image_message,
    _build_message,
)
from core.llm_judge import _build_user_prompt


def _make_scenario(
    *,
    scenario_id: str = "sc-test",
    target_context: str = "current",
    cue_type: str = "object_in_hand",
    activity_domain: str = "workshop",
    cognitive_load: str = "single_referent",
    difficulty_tier: str = "easy",
    turn_1_image: str | None = "Hand on a thin metal handle.",
    turn_1_user: str = "How do I use this?",
    turn_2_image: str | None = "Hand on a wooden grip with a heavy head.",
    turn_2_user: str = "What about now?",
    turn_3_repair_anchor: str = "I mean the object I'm holding now.",
    context_image: str | None = None,
) -> Scenario:
    return Scenario(
        scenario_id=scenario_id,
        target_context=target_context,
        cue_type=cue_type,
        activity_domain=activity_domain,
        cognitive_load=cognitive_load,
        difficulty_tier=difficulty_tier,
        turn_1_image=turn_1_image or "",
        turn_1_user=turn_1_user,
        turn_2_image=turn_2_image or "",
        turn_2_user=turn_2_user,
        turn_3_repair_anchor=turn_3_repair_anchor,
        context_image=context_image,
    )


# ---------------------------------------------------------------------------
# _build_message — direct unit tests
# ---------------------------------------------------------------------------


def test_camera_block_present_when_image_set() -> None:
    """When an image is provided, the user content must start with `[Camera:`
    and contain the spoken text on a separate line."""
    msg = _build_message(
        role="user",
        text="Am I doing this right?",
        image="Hand wrapped around a wooden handle. Heavy metal head with a flat striking face.",
    )
    assert msg["role"] == "user"
    content = msg["content"]
    assert content.startswith("[Camera: "), (
        f"camera block missing or not at start: {content!r}"
    )
    assert content.endswith("Am I doing this right?")
    # Camera block and spoken text are separated by exactly one newline.
    assert "]\nAm I doing this right?" in content


def test_no_camera_block_when_image_null() -> None:
    """When no image is provided, the message content must be the plain user
    text only — no `[Camera:` prefix, no leading newline."""
    msg = _build_message(role="user", text="Where do I start?", image=None)
    assert msg == {"role": "user", "content": "Where do I start?"}


def test_no_camera_block_when_image_empty_string() -> None:
    """An empty-string image is falsy and treated the same as null."""
    msg = _build_message(role="user", text="Just a question.", image="")
    assert msg == {"role": "user", "content": "Just a question."}


def test_camera_block_format_is_exact() -> None:
    """The format must be exactly `[Camera: {image}]\\n{text}` per schema."""
    msg = _build_message(
        role="user",
        text="USER TEXT",
        image="IMAGE TEXT",
    )
    assert msg["content"] == "[Camera: IMAGE TEXT]\nUSER TEXT"


def test_context_image_message_is_user_only_camera_block() -> None:
    """`context_image` is injected as a `user` message containing only the
    `[Camera: ...]` block — no spoken text."""
    msg = _build_context_image_message("A workbench with several tools laid out.")
    assert msg["role"] == "user"
    assert msg["content"] == "[Camera: A workbench with several tools laid out.]"
    # No spoken text after the camera block.
    assert "\n" not in msg["content"]


# ---------------------------------------------------------------------------
# Runner-level injection — context_image precedes Turn 1
# ---------------------------------------------------------------------------


class _CapturingAdapter:
    """Records every call's `messages` list verbatim so tests can inspect
    the conversation history that was constructed."""

    def __init__(self) -> None:
        self.calls: list[list[dict[str, str]]] = []

    def query(self, messages: list[dict], system: str, config: Any) -> str:
        self.calls.append([dict(m) for m in messages])
        return "STUB_RESPONSE"


class _PassingJudge:
    """Always labels the target_context, so no Turn 3 is fired."""

    family = "stub"
    model_id = "stub-model"

    def label(
        self,
        response: str,
        scenario_description: str,
        turn_2_user: str,
        current_answers: list[str],
        prior_answers: list[str],
        clarify_indicators: list[str],
        abstain_indicators: list[str],
        ground_truth_context: str | None = None,
    ) -> Any:
        from core.llm_judge import JudgeVerdict

        return JudgeVerdict(selected_policy="current", rationale="stub")


def test_context_image_injected_as_separate_message_before_t1() -> None:
    """When `scenario.context_image` is set, the runner must inject a leading
    user-only camera message before Turn 1."""
    scenario = _make_scenario(
        context_image="A long workbench with a vise on the left and several "
        "tools laid out on a pegboard above.",
    )
    answers = AnswerSet(
        current_answers=["a", "b", "c"],
        prior_answers=[],
        clarify_indicators=[],
        abstain_indicators=[],
    )
    from core.interventions import PromptCondition
    from core.models import ModelConfig

    condition = PromptCondition(
        name="test", description="d", system_prompt="sys", token_count=0
    )
    adapter = _CapturingAdapter()
    judge = _PassingJudge()

    run_module._run_one_trial(
        scenario=scenario,
        answers=answers,
        condition=condition,
        trial=0,
        adapter=adapter,
        judge=judge,
        model_config=ModelConfig(model_id="stub", temperature=0.0),
    )

    # First adapter call is Turn 1. Its messages should be:
    #   [0] context_image-only camera message
    #   [1] Turn 1 user message with [Camera:] block
    turn_1_messages = adapter.calls[0]
    assert len(turn_1_messages) == 2, (
        f"expected context_image + T1 (2 messages), got {len(turn_1_messages)}"
    )
    leading = turn_1_messages[0]
    assert leading["role"] == "user"
    assert leading["content"].startswith("[Camera: ")
    assert leading["content"] == (
        "[Camera: A long workbench with a vise on the left and several "
        "tools laid out on a pegboard above.]"
    )
    # No spoken text follows the camera block in the leading message.
    assert "\n" not in leading["content"]

    # The T1 message itself should include both the camera block and the
    # spoken text.
    t1_user = turn_1_messages[1]
    assert t1_user["role"] == "user"
    assert t1_user["content"].startswith("[Camera: ")
    assert t1_user["content"].endswith(scenario.turn_1_user)


def test_no_context_image_message_when_field_is_null() -> None:
    """When `context_image` is null, the leading user-only camera message is
    omitted; Turn 1 is the very first message."""
    scenario = _make_scenario(context_image=None)
    answers = AnswerSet(
        current_answers=["a", "b", "c"],
        prior_answers=[],
        clarify_indicators=[],
        abstain_indicators=[],
    )
    from core.interventions import PromptCondition
    from core.models import ModelConfig

    condition = PromptCondition(
        name="test", description="d", system_prompt="sys", token_count=0
    )
    adapter = _CapturingAdapter()
    judge = _PassingJudge()

    run_module._run_one_trial(
        scenario=scenario,
        answers=answers,
        condition=condition,
        trial=0,
        adapter=adapter,
        judge=judge,
        model_config=ModelConfig(model_id="stub", temperature=0.0),
    )

    turn_1_messages = adapter.calls[0]
    # No context-image preface; the T1 user message is the only one.
    assert len(turn_1_messages) == 1, (
        f"expected only T1 message (no context_image preface), got "
        f"{len(turn_1_messages)}"
    )
    assert turn_1_messages[0]["role"] == "user"
    assert turn_1_messages[0]["content"].startswith("[Camera: ")


def test_t2_message_contains_camera_block_when_image_set() -> None:
    """The Turn 2 message must include its own `[Camera:]` block from
    `turn_2_image`, distinct from Turn 1's image."""
    scenario = _make_scenario(
        turn_1_image="Hand on a slim cylindrical metal shaft.",
        turn_2_image="Hand on a flat plastic grip with three colored buttons.",
    )
    answers = AnswerSet(
        current_answers=["a", "b", "c"],
        prior_answers=[],
        clarify_indicators=[],
        abstain_indicators=[],
    )
    from core.interventions import PromptCondition
    from core.models import ModelConfig

    condition = PromptCondition(
        name="test", description="d", system_prompt="sys", token_count=0
    )
    adapter = _CapturingAdapter()
    judge = _PassingJudge()

    run_module._run_one_trial(
        scenario=scenario,
        answers=answers,
        condition=condition,
        trial=0,
        adapter=adapter,
        judge=judge,
        model_config=ModelConfig(model_id="stub", temperature=0.0),
    )

    # Second call is Turn 2. Last message in that call is the new user turn.
    turn_2_messages = adapter.calls[1]
    last = turn_2_messages[-1]
    assert last["role"] == "user"
    assert last["content"].startswith("[Camera: ")
    assert "Hand on a flat plastic grip" in last["content"]
    assert last["content"].endswith(scenario.turn_2_user)


# ---------------------------------------------------------------------------
# Judge ground-truth-context wiring
# ---------------------------------------------------------------------------


def test_judge_receives_ground_truth_context() -> None:
    """`_build_user_prompt` must include a GROUND TRUTH section when a
    `ground_truth_context` string is passed."""
    prompt = _build_user_prompt(
        response="The hammer should hit straight.",
        scenario_description="Object swap; target current.",
        turn_2_user="Am I doing this right?",
        current_answers=["hammer", "swing"],
        prior_answers=["screwdriver"],
        clarify_indicators=[],
        abstain_indicators=[],
        ground_truth_context=(
            "Cue type: object_in_hand. "
            "Turn 1 was a screwdriver, Turn 2 is a hammer."
        ),
    )
    assert "GROUND TRUTH" in prompt
    assert "judge-only" in prompt.lower()
    assert "Turn 1 was a screwdriver" in prompt
    assert "Turn 2 is a hammer" in prompt


def test_judge_omits_ground_truth_section_when_not_provided() -> None:
    """No GROUND TRUTH section is rendered when no ground_truth_context is supplied."""
    prompt = _build_user_prompt(
        response="The hammer should hit straight.",
        scenario_description="Object swap.",
        turn_2_user="Am I doing this right?",
        current_answers=["hammer"],
        prior_answers=["screwdriver"],
        clarify_indicators=[],
        abstain_indicators=[],
    )
    assert "GROUND TRUTH" not in prompt


def test_runner_passes_ground_truth_to_judge() -> None:
    """The runner must pass a non-empty `ground_truth_context` to the judge
    that names the actual T1 and T2 frames."""
    scenario = _make_scenario(
        turn_1_image="Hand on a slim metal shaft with a phillips tip.",
        turn_2_image="Hand wrapped around a wooden handle with a heavy steel head.",
    )
    answers = AnswerSet(
        current_answers=["a", "b", "c"],
        prior_answers=[],
        clarify_indicators=[],
        abstain_indicators=[],
    )

    from core.interventions import PromptCondition
    from core.models import ModelConfig

    captured: dict[str, Any] = {}

    class _RecordingJudge:
        family = "stub"
        model_id = "stub-model"

        def label(self, **kwargs: Any) -> Any:
            captured.update(kwargs)
            from core.llm_judge import JudgeVerdict

            return JudgeVerdict(selected_policy="current", rationale="stub")

    condition = PromptCondition(
        name="test", description="d", system_prompt="sys", token_count=0
    )
    adapter = _CapturingAdapter()
    run_module._run_one_trial(
        scenario=scenario,
        answers=answers,
        condition=condition,
        trial=0,
        adapter=adapter,
        judge=_RecordingJudge(),
        model_config=ModelConfig(model_id="stub", temperature=0.0),
    )
    assert "ground_truth_context" in captured
    gt = captured["ground_truth_context"]
    assert isinstance(gt, str) and gt
    # The ground-truth context should reference both T1 and T2 frames.
    assert "Turn 1 camera state" in gt
    assert "Turn 2 camera state" in gt
    assert scenario.turn_1_image in gt
    assert scenario.turn_2_image in gt
