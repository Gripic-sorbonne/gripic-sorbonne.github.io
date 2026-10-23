import csv
import os
import pandas as pd

EXCEL_FILE = './gripic_data.xlsx'
OUTPUT_DIR = './inputs/'


def format_date_cell(val):
    """
    Converts any date value from Excel (serial numbers, strings)
    to the consistent DD/MM/YYYY format.
    """
    if pd.isna(val) or str(val).strip() == '':
        return ''

    val_str = str(val).strip().lstrip("'")

    if '/' in val_str and len(val_str.split('/')) == 3:
        return val_str

    try:
        parsed_dt = pd.to_datetime(val_str, dayfirst=True, errors='coerce')
        if not pd.isna(parsed_dt):
            return parsed_dt.strftime('%d/%m/%Y')
    except Exception:
        pass

    return val_str


def convert_excel_to_csvs():
    if not os.path.exists(EXCEL_FILE):
        print(f"Error: File '{EXCEL_FILE}' not found.")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    xls = pd.ExcelFile(EXCEL_FILE)

    print(f"Excel sheets detected: {xls.sheet_names}")

    for sheet_name in xls.sheet_names:
        # 1. Read cells while preserving text types
        df = pd.read_excel(xls, sheet_name=sheet_name, dtype=str)

        # 2. Remove accidentally added rows that are completely empty
        df = df.dropna(how='all')

        # 3. Clean quotation marks and whitespace
        for col in df.columns:
            df[col] = (
                df[col]
                .fillna('')
                .astype(str)
                .str.replace("'", "", regex=False)
                .str.strip()
            )

            # Automatically format date columns
            if 'date' in col.lower():
                df[col] = df[col].apply(format_date_cell)

        # 4. Filter out rows where the primary identifier is empty
        if 'Titre' in df.columns:
            df = df[df['Titre'] != '']
        elif 'nom' in df.columns:
            df = df[df['nom'] != '']

        csv_filename = f"{sheet_name}.csv"
        csv_path = os.path.join(OUTPUT_DIR, csv_filename)

        encoding_type = 'utf-8-sig' if sheet_name == 'calendar' else 'utf-8'

        df.to_csv(
            csv_path,
            sep=';',
            index=False,
            encoding=encoding_type,
            quoting=csv.QUOTE_MINIMAL
        )

        print(f"Generated: '{csv_filename}' ({len(df)} rows processed).")

    print("\nExcel-to-CSV conversion completed successfully!")


if __name__ == '__main__':
    convert_excel_to_csvs()