# #!/bin/bash

# # Stop execution if any coimport pandas as pd
# import os

# csv_path = './inputs/categories.csv'
# if not os.path.exists(csv_path):
#     csv_path = 'categories.csv' 

# excel_file = './gripic_data.xlsx'

# try:
#     df = pd.read_csv(csv_path, sep=';', encoding='utf-8')
    
#     with pd.ExcelWriter(excel_file, engine='openpyxl', mode='w') as writer:
#         df.to_excel(writer, sheet_name='categories', index=False)
        
#     print(f"¡Éxito! Se ha generado '{excel_file}' con la pestaña 'categories' a partir de '{csv_path}'.")
# except Exception as e:
#     print(f"Ocurrió un error al procesar el archivo: {e}")mmand fails
# set -e

# # Store the repository root path
# REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# # echo "1. Entering scripts/ and converting Excel to CSV..."
# # cd "$REPO_ROOT/scripts"
# # python excel_to_csv.py

# echo "2. Cleaning previous data folder..."
# cd "$REPO_ROOT"
# rm -rf data

# echo "3. Generating Markdown files from CSV..."
# cd "$REPO_ROOT/scripts"
# python init_files_from_csv.py

# # Pequeña pausa de 2 segundos para asegurar que el sistema de archivos escriba todo correctamente
# sleep 2

# echo "4. Returning to the repository root and staging Git changes..."
# cd "$REPO_ROOT"
# git add .

# # Check whether there are any changes to commit
# if git diff-index --quiet HEAD --; then
#     echo "No changes detected. Creating an empty commit to force a build..."
#     git commit --allow-empty -m "trigger: re-run build"
# else
#     # Request a commit message from the user or use a default message
#     COMMIT_MSG="${1:-doing pipeline from xlsx}"
#     git commit -m "$COMMIT_MSG"
# fi

# echo "5. Pushing changes to GitHub..."
# git push

# echo "Pipeline executed successfully!"

#!/bin/bash

# Stop execution if any command fails
set -e

# Store the repository root path
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# If you want the script to also convert Excel to CSV automatically,
# you can uncomment these lines:
echo "1. Entering scripts/ and converting Excel to CSV..."
cd "$REPO_ROOT/scripts"
python excel_to_csv.py

echo "2. Cleaning previous data folder..."
cd "$REPO_ROOT"
rm -rf data

echo "3. Generating Markdown files from CSV..."
cd "$REPO_ROOT/scripts"
python init_files_from_csv.py

# Brief 2-second pause to ensure the filesystem has finished writing everything correctly
sleep 2

echo "4. Returning to the repository root and staging Git changes..."
cd "$REPO_ROOT"
git add .

# Check whether there are any changes to commit
if git diff-index --quiet HEAD --; then
    echo "No changes detected. Creating an empty commit to trigger a build..."
    git commit --allow-empty -m "trigger: re-run build"
else
    # Request a commit message from the user or use a default message
    COMMIT_MSG="${1:- solving new image structure bug}"
    git commit -m "$COMMIT_MSG"
fi

echo "5. Pushing changes to GitHub..."
git push

echo "Pipeline executed successfully!"