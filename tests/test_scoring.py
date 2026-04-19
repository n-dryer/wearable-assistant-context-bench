"""Unit tests for core.scoring."""

from __future__ import annotations

from core.scoring import (
    detect_refusal,
    extract_entities,
    fuzzy_match,
    score_response,
)


def test_extract_entities_pulls_nouns_and_numbers() -> None:
    entities = extract_entities(
        "Sarah bought 3 apples at the farmers market in Brooklyn."
    )
    lowered = [e.lower() for e in entities]
    joined = " ".join(lowered)
    assert "sarah" in joined
    assert "brooklyn" in joined
    assert any("apple" in e for e in lowered)
    assert "3" in entities


def test_fuzzy_match_true_on_close_match() -> None:
    assert fuzzy_match(
        "The meeting has been rescheduled to 3pm sharp.",
        targets=["rescheduled to 3pm"],
    )


def test_fuzzy_match_false_on_non_match() -> None:
    assert not fuzzy_match(
        "The weather is sunny today.",
        targets=["database migration failed"],
    )


def test_detect_refusal_catches_common_phrasings() -> None:
    assert detect_refusal("I cannot answer that question.")
    assert detect_refusal("I'm unable to determine the current state.")
    assert detect_refusal("I don't have enough information to say.")
    assert detect_refusal("I don't know the answer.")
    assert detect_refusal("I'm not able to provide that.")
    assert not detect_refusal("The answer is 42.")


def test_score_response_pass_case() -> None:
    result = score_response(
        response="I can see a toothbrush and a mirror on the counter.",
        current_answers=["toothbrush", "mirror"],
        stale_answers=["stove", "kettle"],
    )
    assert result["has_current"] is True
    assert result["has_stale"] is False
    assert result["is_refusal"] is False


def test_score_response_fail_case_with_stale() -> None:
    result = score_response(
        response="On the counter there is a stove and a kettle.",
        current_answers=["toothbrush", "mirror"],
        stale_answers=["stove", "kettle"],
    )
    assert result["has_current"] is False
    assert result["has_stale"] is True


def test_score_response_refusal_case() -> None:
    result = score_response(
        response="I'm unable to determine what is on the counter.",
        current_answers=["toothbrush", "mirror"],
        stale_answers=["stove", "kettle"],
    )
    assert result["is_refusal"] is True


def test_score_response_both_current_and_stale() -> None:
    result = score_response(
        response=(
            "Earlier you mentioned a stove, but now I can see a "
            "toothbrush on the bathroom counter."
        ),
        current_answers=["toothbrush"],
        stale_answers=["stove"],
    )
    assert result["has_current"] is True
    assert result["has_stale"] is False
    assert result["has_stale_raw"] is True
    assert result["is_refusal"] is False


def test_score_response_token_length_is_positive_integer() -> None:
    result = score_response(
        response="one two three four five",
        current_answers=[],
        stale_answers=[],
    )
    assert isinstance(result["response_length_tokens"], int)
    assert result["response_length_tokens"] > 0


def test_score_response_contrastive_phrasing_suppresses_has_stale() -> None:
    result = score_response(
        response="Earlier there were 12 photos; now there are 13",
        current_answers=["13"],
        stale_answers=["12"],
    )
    assert result["has_current"] is True
    assert result["has_stale"] is False
    assert result["has_stale_raw"] is True


def test_score_response_no_trigger_verb_leaves_has_stale_true() -> None:
    result = score_response(
        response="The album had 12 photos, it now has 13",
        current_answers=["13"],
        stale_answers=["12"],
    )
    assert result["has_current"] is True
    assert result["has_stale"] is True
    assert result["has_stale_raw"] is True


def test_score_response_no_match_baseline_unchanged() -> None:
    result = score_response(
        response="The counter has a toothbrush on it.",
        current_answers=["toothbrush"],
        stale_answers=["stove"],
    )
    assert result["has_current"] is True
    assert result["has_stale"] is False
    assert result["has_stale_raw"] is False
