"""Repo text checks for public terminology and archival boundaries."""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
PUBLIC_PATHS = (
    "README.md",
    "docs/benchmark_spec.md",
    "docs/benchmark_notes.md",
    "docs/benchmark_card.html",
    "CITATION.cff",
    "CONTRIBUTING.md",
    "CHANGELOG.md",
)


def _read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def test_public_docs_avoid_legacy_reference_state_language() -> None:
    forbidden = (
        "reference-state",
        "reference-state selection",
        "v1 runnable slice",
        "slice",
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


def test_public_docs_use_canonical_v1_framing() -> None:
    required_paths = (
        "README.md",
        "docs/benchmark_spec.md",
        "docs/benchmark_notes.md",
        "docs/benchmark_card.html",
    )
    required_phrase = "cross-turn reference resolution under context change"
    for path in required_paths:
        lowered = _read(path).lower()
        assert required_phrase in lowered, (
            f"{path} should describe the canonical v1 measured task"
        )


def test_public_docs_state_product_purpose_and_transcript_proxy_scope() -> None:
    readme = _read("README.md").lower()
    spec = _read("docs/benchmark_spec.md").lower()
    notes = _read("docs/benchmark_notes.md").lower()
    combined = "\n".join((readme, spec, notes))

    assert "product benchmark" in combined
    assert "model-selection" in combined or "model selection" in combined
    assert "user feedback" in combined or "product testing" in combined
    assert "transcript prox" in combined
    assert "raw acoustic grounding" in combined
    assert "speaker attribution" in combined
    assert "ambient audio cues" in combined


def test_public_docs_do_not_present_benchmark_v2_as_active_surface() -> None:
    for path in PUBLIC_PATHS:
        lowered = _read(path).lower()
        assert "benchmark/v2/" not in lowered, (
            f"{path} should not reference benchmark/v2 as an active public track"
        )


def test_root_agents_is_archival_notice_only() -> None:
    # AGENTS.md is gitignored (local Claude Code file). Skip gracefully when absent.
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
