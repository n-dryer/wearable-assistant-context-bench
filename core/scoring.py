"""Code-based scoring utilities.

These functions implement the deterministic half of the hybrid scoring
scheme. Callers combine the returned signals with an LLM judge verdict
(see core.llm_judge) to reach a final pass/fail decision.

The pass rule is documented in docs/METHODOLOGY.md and is applied by the
experiment runner, not encoded here:

    pass = has_current=True AND has_stale=False AND is_refusal=False

A contrastive-pattern suppressor (see _CONTRASTIVE_RE) demotes has_stale
to False when the response explicitly contrasts an earlier state with
the current one. The pre-suppression value is preserved as
has_stale_raw in the returned dict for audit purposes.
"""

from __future__ import annotations

import re
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


def score_response(
    response: str,
    current_answers: list[str],
    stale_answers: list[str],
) -> dict:
    """Compute code-based scoring signals for a single response.

    The caller combines these with a judge verdict to compute a final
    pass/fail. This function does not encode the pass rule itself.

    Args:
        response: The model response text (typically the Turn 2 assistant
            reply).
        current_answers: Strings that reflect the up-to-date state. A match
            indicates the model grounded on the most recent context.
        stale_answers: Strings that reflect the earlier, overridden state.
            A match indicates the model failed to update.

    Returns:
        Dict with keys:
            has_current (bool): Fuzzy match against any current answer.
            has_stale (bool): Fuzzy match against any stale answer, after
                the contrastive-pattern suppressor demotes it to False
                when the response explicitly contrasts earlier with
                current state.
            has_stale_raw (bool): Pre-suppression fuzzy-match value,
                preserved for audit trails.
            is_refusal (bool): Whether the response refuses or hedges.
            response_length_tokens (int): Approximate token count, rounded.
    """
    has_current = fuzzy_match(response, current_answers)
    has_stale_raw = fuzzy_match(response, stale_answers)
    has_stale = has_stale_raw
    if has_stale and _CONTRASTIVE_RE.search(response or ""):
        has_stale = False
    is_refusal = detect_refusal(response)

    word_count = len(response.split()) if response else 0
    response_length_tokens = int(round(word_count * 1.3))

    return {
        "has_current": has_current,
        "has_stale": has_stale,
        "has_stale_raw": has_stale_raw,
        "is_refusal": is_refusal,
        "response_length_tokens": response_length_tokens,
    }
