#!/bin/bash
# Post-v1.0.0 branch and tag cleanup.
# Run from repo root: bash cleanup_post_v1.sh
# Guard hook blocks git branch -d via Claude -- run this manually.

set -e
cd "$(git rev-parse --show-toplevel)"

echo "=== Local branch cleanup ==="

# Safe-delete merged branches
for b in v1-portfolio-release v1-completion v2-expansion v1-language-pass; do
  if git show-ref --verify --quiet refs/heads/$b; then
    git branch -d "$b" && echo "deleted local: $b" || echo "SKIPPED (unmerged): $b"
  else
    echo "not found locally: $b"
  fi
done

# codex/ branch
if git show-ref --verify --quiet refs/heads/codex/gemini-deep-research-prompt; then
  git branch -d codex/gemini-deep-research-prompt && echo "deleted local: codex/gemini-deep-research-prompt" || echo "SKIPPED (unmerged): codex/gemini-deep-research-prompt"
fi

# Delete all claude/* worktree branches except the active session
ACTIVE="claude/vigorous-euclid-838f2c"
echo ""
echo "=== claude/* worktree branches ==="
for b in $(git for-each-ref --format '%(refname:short)' refs/heads/claude/); do
  if [ "$b" = "$ACTIVE" ]; then
    echo "keeping active: $b"
  else
    git branch -D "$b" && echo "deleted: $b" || echo "FAILED: $b"
  fi
done

echo ""
echo "=== Remote branch cleanup ==="
git push origin --delete v1-portfolio-release 2>/dev/null && echo "deleted remote: v1-portfolio-release" || echo "already gone or failed: v1-portfolio-release"
git push origin --delete v2-expansion 2>/dev/null && echo "deleted remote: v2-expansion" || echo "already gone or failed: v2-expansion"

echo ""
echo "=== Tag cleanup ==="
if git tag --list | grep -q '^v1$'; then
  git tag -d v1 && echo "deleted local tag: v1"
else
  echo "local tag v1 not found"
fi
git push origin :refs/tags/v1 2>/dev/null && echo "deleted remote tag: v1" || echo "remote tag v1 already gone or failed"

echo ""
echo "=== Done. Remaining branches: ==="
git branch -a
