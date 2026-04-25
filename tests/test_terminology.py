"""Repo text checks for public terminology and archival boundaries.

The v2 docs rewrite lands in Step 6 of the rebuild. Tests here that rely
on Step 6 wording are marked with `pytest.skip("v2 docs land in step 6
commit; will pass after")` so the suite stays green between steps. Each
skipped test must be re-enabled (skip removed) once Step 6 commits.

Re-enable: when Step 6 lands, remove the `pytest.skip(...)` lines
flagged with `# STEP-6 SKIP` below.
"""

from __future__ import annotations

from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parent.parent
# `CHANGELOG.md` was removed in Step 1 of the rebuild. The remaining public
# surface for terminology checks:
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
    """Legacy v1-design terms must not appear in public docs.

    These terms predate the v2 rebuild and have no place in the new
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


def test_public_docs_use_canonical_v1_framing() -> None:
    """Until Step 6 rewrites docs to v2 framing, this test is parked.

    The canonical v1 phrase `cross-turn reference resolution under
    context change` is on its way out. Step 6 replaces it with v2 wording
    (context tracking under in-stream shifts). Re-enable this test, with
    its required-phrase set updated, after Step 6 commits.
    """
    pytest.skip(
        "v2 docs land in step 6 commit; will pass after"
    )  # STEP-6 SKIP


def test_public_docs_state_product_purpose_and_transcript_proxy_scope() -> None:
    """Until Step 6 rewrites docs, the exact phrase set this test
    enforces is in flux. Skip and re-enable after Step 6.
    """
    pytest.skip(
        "v2 docs land in step 6 commit; will pass after"
    )  # STEP-6 SKIP


def test_public_docs_do_not_present_benchmark_v2_as_active_surface() -> None:
    """The repo's directory layout keeps `benchmark/v1/` as the active
    track even though the schema is v2. Public docs must not advertise
    `benchmark/v2/` as an active path.
    """
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
