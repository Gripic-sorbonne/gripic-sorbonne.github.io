import pandas as pd
import os

csv_path = './inputs/categories.csv'
if not os.path.exists(csv_path):
    csv_path = 'categories.csv'

excel_file = './gripic_data.xlsx'

try:
    df = pd.read_csv(csv_path, sep=';', encoding='utf-8')

    with pd.ExcelWriter(excel_file, engine='openpyxl', mode='w') as writer:
        df.to_excel(writer, sheet_name='categories', index=False)

    print(f"Success! '{excel_file}' has been generated with the 'categories' sheet from '{csv_path}'.")
except Exception as e:
    print(f"An error occurred while processing the file: {e}")