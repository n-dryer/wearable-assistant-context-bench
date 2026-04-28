"""Repo text checks for public terminology and archival boundaries.

These tests guard the v1 framing across public-facing docs. They
enforce both forbidden vocabulary (legacy pre-rebuild design terms)
and required vocabulary (the wearable, camera channel, four-label
framing the v1 release commits to).
"""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
# Public surface checked by these terminology tests:
PUBLIC_PATHS = (
    "README.md",
    "docs/benchmark_spec.md",
    "docs/benchmark_notes.md",
    "docs/benchmark_card.html",
    "CITATION.cff",
    "CONTRIBUTING.md",
)


def _read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def test_public_docs_avoid_legacy_reference_state_language() -> None:
    """Legacy pre-rebuild design terms must not appear in public docs.

    These terms predate the rebuild and have no place in the new
    framing. The check is timeless: even after Step 6 lands, these
    forbidden terms stay forbidden.
    """
    forbidden = (
        "reference-state",
        "reference-state selection",
        "v1 runnable slice",
        "sub-capability",
        "deictic grounding",
        "referent arbitration",
        "context-policy arbitration",
        "multimodal situational grounding",
        "post-shift",
        "implicit context tracking",
        "with-prior-q",
    )
    for path in PUBLIC_PATHS:
        lowered = _read(path).lower()
        for term in forbidden:
            assert term not in lowered, f"{path} still contains {term!r}"


def test_public_docs_use_v1_framing() -> None:
    """The four main framing docs must carry the v1 framing language:

    - The product scope is an AI wearable assistant the user is
      actively engaging with for advice or coaching.
    - The camera channel uses scene descriptions.
    - The four judge labels (`current`, `prior`, `clarify`, `abstain`).

    This is a positive check — if a future edit drops the wearable
    framing, the camera channel, or the four-label vocabulary, this
    test fails.
    """
    required = (
        "wearable",
        "camera",
        "scene description",
        "current",
        "prior",
        "clarify",
        "abstain",
    )
    framing_docs = (
        "README.md",
        "docs/benchmark_spec.md",
        "docs/benchmark_notes.md",
        "docs/benchmark_card.html",
    )
    for path in framing_docs:
        lowered = _read(path).lower()
        for phrase in required:
            assert phrase in lowered, f"{path} is missing required phrase {phrase!r}"
        # At least one of the active-use framing terms must appear so
        # the reader knows this is for in-the-moment advice or
        # coaching, not background or passive assistants.
        active_use_terms = ("advice or coaching", "advice or coach", "in-the-moment", "actively")
        assert any(term in lowered for term in active_use_terms), (
            f"{path} is missing an active-use framing term "
            f"(one of {active_use_terms!r})"
        )


def test_public_docs_state_product_purpose_and_transcript_proxy_scope() -> None:
    """Public docs must state three things plainly:

    1. The product purpose — this is a model-selection benchmark for a
       wearable assistant. Tested via per-file required phrases below.
    2. The video-proxy scope — the camera channel uses perceptual
       text descriptions as a stand-in for real video, and real video
       is explicitly outside what the benchmark measures.
    3. The audio-proxy scope — the user's spoken turns are
       represented as text transcripts, not raw audio. Acoustic
       grounding, speaker attribution, and ambient audio cues are
       out of scope.

    Per-file phrase sets are used because the docs split these
    topics across different surfaces (README and card lead with
    purpose; notes and spec carry the proxy/non-goal language).
    """
    purpose_and_proxy = {
        "README.md": (
            "wearable",
            "model-selection",
            "context tracking",
            "scene description",
            "as a proxy",
            "real video",
            "text transcripts",
            "raw audio",
        ),
        "docs/benchmark_spec.md": (
            "wearable",
            "scene description",
            "real video",
            "does not measure",
            "text transcripts",
            "raw audio",
        ),
        "docs/benchmark_notes.md": (
            "wearable",
            "context tracking",
            "scene descriptions in text",
            "as a proxy",
            "real video",
            "does not measure",
            "text transcripts",
            "raw audio",
        ),
        "docs/benchmark_card.html": (
            "wearable",
            "model-selection",
            "context tracking",
            "scene description",
            "as a proxy",
            "real video",
            "text transcripts",
        ),
    }
    for path, phrases in purpose_and_proxy.items():
        lowered = _read(path).lower()
        for phrase in phrases:
            assert phrase in lowered, (
                f"{path} is missing required phrase {phrase!r}"
            )


def test_public_docs_do_not_present_alternate_path_as_active_surface() -> None:
    """The repo's directory layout keeps `benchmark/v1/` as the active
    track. Public docs must not advertise `benchmark/v2/` as an active
    path.
    """
    for path in PUBLIC_PATHS:
        lowered = _read(path).lower()
        assert "benchmark/v2/" not in lowered, (
            f"{path} should not reference benchmark/v2 as an active public track"
        )


def test_root_agents_is_archival_notice_only() -> None:
    # AGENTS.md is gitignored (local-only file). Skip gracefully when absent.
    agents_path = REPO_ROOT / "AGENTS.md"
    if not agents_path.exists():
        return
    body = agents_path.read_text(encoding="utf-8").lower()
    assert "historical archive" in body
    for forbidden in (
        "probe study",
        "four-policy",
        "policy cell",
        "open coding",
        "golden set",
        "stale-context drift",
    ):
        assert forbidden not in body, f"AGENTS.md still contains {forbidden!r}"
