"""Unit tests for core.scoring (v0.2 signals)."""

from __future__ import annotations

import warnings

import pytest

from core.scoring import (
    detect_refusal,
    extract_entities,
    fuzzy_match,
    has_prior,
    has_stale,
    score_response,
    substring_match,
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


def test_substring_match_true_on_case_insensitive_hit() -> None:
    assert substring_match(
        "I don't have access to that data.",
        indicators=["don't have access"],
    )


def test_substring_match_false_on_non_match() -> None:
    assert not substring_match(
        "The meeting starts at 3pm.",
        indicators=["no videos were provided"],
    )


def test_detect_refusal_catches_common_phrasings() -> None:
    assert detect_refusal("I cannot answer that question.")
    assert detect_refusal("I'm unable to determine the current state.")
    assert detect_refusal("I don't have enough information to say.")
    assert detect_refusal("I don't know the answer.")
    assert detect_refusal("I'm not able to provide that.")
    assert not detect_refusal("The answer is 42.")


def test_has_prior_delegates_to_fuzzy_match() -> None:
    assert has_prior(
        "The meeting ran long on Monday morning.",
        prior_answers=["Monday"],
    )
    assert not has_prior(
        "The meeting ran long today.",
        prior_answers=["Friday afternoon"],
    )


def test_has_stale_is_deprecated_alias_for_has_prior() -> None:
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        result = has_stale(
            "The meeting ran long on Monday morning.",
            stale_answers=["Monday"],
        )
    assert result is True
    assert any(
        issubclass(w.category, DeprecationWarning) for w in caught
    ), "has_stale must emit DeprecationWarning"


def test_score_response_pass_case() -> None:
    result = score_response(
        response="I can see a toothbrush and a mirror on the counter.",
        current_answers=["toothbrush", "mirror"],
        prior_answers=["stove", "kettle"],
    )
    assert result["has_current"] is True
    assert result["has_prior"] is False
    assert result["is_refusal"] is False


def test_score_response_fail_case_with_prior() -> None:
    result = score_response(
        response="On the counter there is a stove and a kettle.",
        current_answers=["toothbrush", "mirror"],
        prior_answers=["stove", "kettle"],
    )
    assert result["has_current"] is False
    assert result["has_prior"] is True


def test_score_response_refusal_case() -> None:
    result = score_response(
        response="I'm unable to determine what is on the counter.",
        current_answers=["toothbrush", "mirror"],
        prior_answers=["stove", "kettle"],
    )
    assert result["is_refusal"] is True


def test_score_response_contrastive_phrasing_suppresses_has_prior() -> None:
    result = score_response(
        response="Earlier there were 12 photos; now there are 13",
        current_answers=["13"],
        prior_answers=["12"],
    )
    assert result["has_current"] is True
    assert result["has_prior"] is False
    assert result["has_prior_raw"] is True


def test_score_response_no_trigger_verb_leaves_has_prior_true() -> None:
    result = score_response(
        response="The album had 12 photos, it now has 13",
        current_answers=["13"],
        prior_answers=["12"],
    )
    assert result["has_current"] is True
    assert result["has_prior"] is True
    assert result["has_prior_raw"] is True


def test_score_response_has_clarify_signal() -> None:
    result = score_response(
        response=(
            "Do you mean the scene you just described, or the one from earlier?"
        ),
        current_answers=[],
        prior_answers=[],
        clarify_indicators=["Do you mean"],
    )
    assert result["has_clarify"] is True
    assert result["has_abstain"] is False


def test_score_response_has_abstain_signal() -> None:
    result = score_response(
        response="I'm sorry, but I don't have access to your uploaded videos.",
        current_answers=[],
        prior_answers=[],
        abstain_indicators=["don't have access"],
    )
    assert result["has_abstain"] is True
    assert result["has_clarify"] is False


def test_score_response_stale_keys_mirror_prior_keys_for_back_compat() -> None:
    result = score_response(
        response="Earlier there were 12 photos; now there are 13",
        current_answers=["13"],
        prior_answers=["12"],
    )
    assert result["has_stale"] == result["has_prior"]
    assert result["has_stale_raw"] == result["has_prior_raw"]


def test_score_response_token_length_estimate_is_positive_integer() -> None:
    result = score_response(
        response="one two three four five",
        current_answers=[],
        prior_answers=[],
    )
    assert isinstance(result["response_length_tokens_est"], int)
    assert result["response_length_tokens_est"] > 0


def test_score_response_no_match_baseline_unchanged() -> None:
    result = score_response(
        response="The counter has a toothbrush on it.",
        current_answers=["toothbrush"],
        prior_answers=["stove"],
    )
    assert result["has_current"] is True
    assert result["has_prior"] is False
    assert result["has_prior_raw"] is False


def test_score_response_indicators_default_to_empty() -> None:
    result = score_response(
        response="anything",
        current_answers=[],
        prior_answers=[],
    )
    assert result["has_clarify"] is False
    assert result["has_abstain"] is False


if __name__ == "__main__":
    pytest.main([__file__])
