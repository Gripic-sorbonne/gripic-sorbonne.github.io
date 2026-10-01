#!/bin/bash

# Stop execution if any command fails
set -e

# Store the repository root path
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "1. Entering scripts/ and converting Excel to CSV..."
cd "$REPO_ROOT/scripts"
python excel_to_csv.py

echo "2. Cleaning previous data folder..."
cd "$REPO_ROOT"
rm -rf data

echo "3. Generating Markdown files from CSV..."
cd "$REPO_ROOT/scripts"
python init_files_from_csv.py

echo "4. Returning to the repository root and staging Git changes..."
cd "$REPO_ROOT"
git add .

# Check whether there are any changes to commit
if git diff-index --quiet HEAD --; then
    echo "No changes detected. Creating an empty commit to force a build..."
    git commit --allow-empty -m "trigger: re-run build"
else
    # Request a commit message from the user or use a default message
    COMMIT_MSG="${1:-update data from excel}"
    git commit -m "$COMMIT_MSG"
fi

echo "5. Pushing changes to GitHub..."
git push

echo "Pipeline executed successfully!"