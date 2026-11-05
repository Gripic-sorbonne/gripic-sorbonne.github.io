#!/bin/bash

# Stop execution if any command fails
set -e

# Store the repository root path
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"


echo "1. Staging and committing primary changes..."
cd "$REPO_ROOT"
git add -A


COMMIT_MSG="${1:-render}"
git commit --allow-empty -m "$COMMIT_MSG"

echo "5. Pushing changes to GitHub..."
git push

echo "pipeline done!"