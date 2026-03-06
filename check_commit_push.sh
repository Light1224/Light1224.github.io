#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Error: not inside a git repository."
  exit 1
fi

COMMIT_MSG="${1:-Update site content}"
BRANCH="$(git rev-parse --abbrev-ref HEAD)"

if [[ "$BRANCH" == "HEAD" ]]; then
  echo "Error: detached HEAD. Check out a branch before pushing."
  exit 1
fi

echo "Checking git status on branch: $BRANCH"
if [[ -n "$(git status --porcelain)" ]]; then
  echo "Changes detected. Staging and committing..."
  git add -A
  git commit -m "$COMMIT_MSG"
else
  echo "No local changes to commit."
fi

echo "Pushing to origin/$BRANCH..."
git push origin "$BRANCH"

echo "Done."
