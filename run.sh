#!/bin/bash

# Stop execution if any command fails
set -e

# Store the repository root path
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "1. Entering scripts/ and converting Excel to CSV..."
cd "$REPO_ROOT/scripts"
python excel_to_csv.py

echo "2. Cleaning previous data folder completely..."
cd "$REPO_ROOT"
# Borramos de forma agresiva y aseguramos que Git detecte el borrado limpio
if [ -d "data" ]; then
    rm -rf data
    git add -A data
fi

echo "3. Generating Markdown files from CSV..."
cd "$REPO_ROOT/scripts"
python init_files_from_csv.py

# Pausa generosa para asegurar que el sistema de archivos de Windows/Linux escriba todo
sleep 3

echo "4. Staging all fresh changes cleanly..."
cd "$REPO_ROOT"
git add -A

# Comprobar si hay cambios reales
if git diff-index --quiet HEAD --; then
    echo "No changes detected. Creating an empty commit to trigger a build..."
    git commit --allow-empty -m "trigger: re-run build"
else
    COMMIT_MSG="${1:-update data from excel}"
    git commit -m "$COMMIT_MSG"
fi

echo "5. Pushing changes to GitHub..."
git push

echo "Pipeline executed successfully and cleanly!"