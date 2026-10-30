#!/bin/bash

# Stop execution if any command fails
set -e

# Store the repository root path
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "1. Cleaning previous data folder completely..."
cd "$REPO_ROOT"
if [ -d "data" ]; then
    rm -rf data
fi

echo "2. Entering scripts/ and converting Excel to CSV..."
cd "$REPO_ROOT/scripts"
python excel_to_csv.py

echo "3. Generating Markdown files from CSV..."
cd "$REPO_ROOT/scripts"
python init_files_from_csv.py

sleep 2

echo "4. Staging and committing primary changes..."
cd "$REPO_ROOT"
git add -A

if git diff-index --quiet HEAD --; then
    echo "No changes detected."
else
    COMMIT_MSG="${1:-update data}"
    git commit -m "$COMMIT_MSG"
fi

echo "5. Pushing changes to GitHub..."
git push

echo "¡Pipeline ejecutado y sincronizado exitosamente!"