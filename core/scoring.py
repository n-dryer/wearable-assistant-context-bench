"""Code-based scoring utilities.

These functions implement the deterministic half of the scoring flow.
Callers combine the returned signals with a judge verdict
(`core.llm_judge`) to reach a final pass/fail decision.

`has_stale` is kept only as a deprecated compatibility alias for older
callers. The preferred signal name is `has_prior`, which reflects that
the response followed the earlier context. `score_response` still
returns the deprecated `has_stale` keys so older code keeps working,
but new transcript output should not surface them.

The contrastive-pattern suppressor (see `_CONTRASTIVE_RE`) demotes
`has_prior` to False when the response explicitly contrasts an earlier
state with the current one. The pre-suppression value is preserved as
`has_prior_raw` for audit trails.
"""

from __future__ import annotations

import re
import warnings
from functools import lru_cache

import spacy
from rapidfuzz import fuzz


_SPACY_MODEL = "en_core_web_sm"


@lru_cache(maxsize=1)
def _nlp() -> spacy.language.Language:
    """Load and cache the spaCy English pipeline."""
    return spacy.load(_SPACY_MODEL)


_CONTRASTIVE_RE = re.compile(
    r"\b(earlier|was|used to be|previously)\b.*?\b(now|currently|is)\b",
    re.IGNORECASE | re.DOTALL,
)


_REFUSAL_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\bi\s+cannot\b", re.IGNORECASE),
    re.compile(r"\bi\s*can'?t\b", re.IGNORECASE),
    re.compile(r"\bi'?m\s+unable\b", re.IGNORECASE),
    re.compile(r"\bi\s+am\s+unable\b", re.IGNORECASE),
    re.compile(r"\bi'?m\s+not\s+able\b", re.IGNORECASE),
    re.compile(r"\bi\s+am\s+not\s+able\b", re.IGNORECASE),
    re.compile(r"\bi\s+don'?t\s+have\s+enough\s+information\b", re.IGNORECASE),
    re.compile(r"\bi\s+do\s+not\s+have\s+enough\s+information\b", re.IGNORECASE),
    re.compile(r"\bi\s+don'?t\s+know\b", re.IGNORECASE),
    re.compile(r"\bi\s+do\s+not\s+know\b", re.IGNORECASE),
    re.compile(r"\bnot\s+enough\s+(information|context)\b", re.IGNORECASE),
    re.compile(r"\binsufficient\s+(information|context)\b", re.IGNORECASE),
)


def extract_entities(text: str) -> list[str]:
    """Extract noun phrases, named entities, and numeric tokens from text.

    Returned strings are lowercased and de-duplicated while preserving the
    first-seen order. This is used upstream of fuzzy matching when a caller
    wants to pre-process a response into matchable chunks.

    Args:
        text: Arbitrary input text.

    Returns:
        Ordered list of unique entity strings. Empty list for empty input.
    """
    if not text or not text.strip():
        return []

    doc = _nlp()(text)
    seen: set[str] = set()
    out: list[str] = []

    for chunk in doc.noun_chunks:
        value = chunk.text.strip().lower()
        if value and value not in seen:
            seen.add(value)
            out.append(value)

    for ent in doc.ents:
        value = ent.text.strip().lower()
        if value and value not in seen:
            seen.add(value)
            out.append(value)

    for token in doc:
        if token.like_num:
            value = token.text.strip().lower()
            if value and value not in seen:
                seen.add(value)
                out.append(value)

    return out


def fuzzy_match(response: str, targets: list[str], threshold: int = 85) -> bool:
    """Return True if any target fuzzy-matches the response.

    Uses rapidfuzz partial_ratio so a short target that appears inside a
    longer response still scores highly.

    Args:
        response: The model response being scored.
        targets: Candidate answer strings to look for.
        threshold: Minimum partial_ratio (0-100) to count as a match.

    Returns:
        True if at least one target scores at or above threshold.
    """
    if not response or not targets:
        return False
    haystack = response.lower()
    for target in targets:
        if not target:
            continue
        score = fuzz.partial_ratio(target.lower(), haystack)
        if score >= threshold:
            return True
    return False


def substring_match(response: str, indicators: list[str]) -> bool:
    """Return True if any indicator appears as a case-insensitive substring.

    Used for clarify/abstain indicators, which are phrase-level rather
    than entity-level and benefit from a looser check than fuzzy_match.

    Args:
        response: The model response being scored.
        indicators: Candidate phrase strings to look for.

    Returns:
        True if at least one indicator is a substring of the response.
    """
    if not response or not indicators:
        return False
    haystack = response.lower()
    for indicator in indicators:
        if not indicator:
            continue
        if indicator.lower() in haystack:
            return True
    return False


def detect_refusal(response: str) -> bool:
    """Return True if the response reads as a refusal or uncertainty hedge.

    The heuristic matches common English refusal phrasings. It is
    intentionally conservative: expressions like "I think" or "I'm not sure"
    alone do not count; only phrases that explicitly decline to answer.

    Args:
        response: The model response being scored.

    Returns:
        True if any refusal pattern matches.
    """
    if not response:
        return False
    return any(pattern.search(response) for pattern in _REFUSAL_PATTERNS)


def has_prior(response: str, prior_answers: list[str]) -> bool:
    """Return True if the response fuzzy-matches any prior-state answer.

    This is the preferred signal name for answers grounded in the
    earlier context.

    Args:
        response: The model response being scored.
        prior_answers: Strings reflecting the earlier context.

    Returns:
        True if any prior_answer fuzzy-matches the response.
    """
    return fuzzy_match(response, prior_answers)


def has_stale(response: str, stale_answers: list[str]) -> bool:
    """Deprecated alias for `has_prior`. Emits `DeprecationWarning` on call.

    Kept only so older callers and doc snippets continue to work. New
    code should use `has_prior`.
    """
    warnings.warn(
        "scoring.has_stale is deprecated; use scoring.has_prior "
        "(the code signal now corresponds to the `prior` policy in v0.2).",
        DeprecationWarning,
        stacklevel=2,
    )
    return has_prior(response, stale_answers)


def score_response(
    response: str,
    current_answers: list[str],
    prior_answers: list[str],
    clarify_indicators: list[str] | None = None,
    abstain_indicators: list[str] | None = None,
) -> dict:
    """Compute code-based scoring signals for a single response.

    The caller combines these with a judge verdict to compute a final
    pass/fail. Code signals are audit-only; the judge verdict is the
    source of truth for the benchmark score.

    Args:
        response: The model response text (typically the Turn 2 assistant
            reply).
        current_answers: Strings that reflect the up-to-date state. A match
            indicates the model grounded in the most recent context.
        prior_answers: Strings that reflect the earlier context. A
            match indicates the model answered from an earlier state.
        clarify_indicators: Phrases that signal a clarifying question was
            asked. Optional; defaults to empty list.
        abstain_indicators: Phrases that signal the model declined to
            answer. Optional; defaults to empty list.

    Returns:
        Dict with keys:
            has_current (bool): Fuzzy match against any current answer.
            has_prior (bool): Fuzzy match against any prior answer, after
                the contrastive-pattern suppressor demotes it to False
                when the response explicitly contrasts earlier with
                current state.
            has_prior_raw (bool): Pre-suppression fuzzy-match value,
                preserved for audit trails.
            has_clarify (bool): Substring match against any
                clarify_indicators.
            has_abstain (bool): Substring match against any
                abstain_indicators.
            is_refusal (bool): Whether the response refuses or hedges.
            response_length_tokens_est (int): Approximate token count,
                rounded.
            has_stale (bool): Deprecated alias of `has_prior`.
            has_stale_raw (bool): Deprecated alias of `has_prior_raw`.
    """
    has_current = fuzzy_match(response, current_answers)
    has_prior_raw = fuzzy_match(response, prior_answers)
    has_prior_value = has_prior_raw
    if has_prior_value and _CONTRASTIVE_RE.search(response or ""):
        has_prior_value = False
    has_clarify_value = substring_match(response, clarify_indicators or [])
    has_abstain_value = substring_match(response, abstain_indicators or [])
    is_refusal = detect_refusal(response)

    word_count = len(response.split()) if response else 0
    response_length_tokens_est = int(round(word_count * 1.3))

    return {
        "has_current": has_current,
        "has_prior": has_prior_value,
        "has_prior_raw": has_prior_raw,
        "has_clarify": has_clarify_value,
        "has_abstain": has_abstain_value,
        "is_refusal": is_refusal,
        "response_length_tokens_est": response_length_tokens_est,
        "has_stale": has_prior_value,
        "has_stale_raw": has_prior_raw,
    }
