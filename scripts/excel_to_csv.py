# import csv
# import os
# import pandas as pd

# EXCEL_FILE = './gripic_data.xlsx'
# OUTPUT_DIR = './inputs/'


# def convert_excel_to_csvs():
#     if not os.path.exists(EXCEL_FILE):
#         print(f"Error: File '{EXCEL_FILE}' was not found.")
#         return

#     if not os.path.exists(OUTPUT_DIR):
#         os.makedirs(OUTPUT_DIR, exist_ok=True)

#     xls = pd.ExcelFile(EXCEL_FILE)
#     print(f"Sheets found: {xls.sheet_names}")

#     for sheet_name in xls.sheet_names:
#         # dtype=str lee el texto exacto sin alterar las fechas
#         df = pd.read_excel(xls, sheet_name=sheet_name, dtype=str)
#         df = df.fillna('')

#         csv_filename = f"{sheet_name}.csv"
#         csv_path = os.path.join(OUTPUT_DIR, csv_filename)

#         # SOLO calendar.csv requiere utf-8-sig para incluir el BOM '\ufeff'
#         # Las demás pestañas (como categories) requieren 'utf-8' estándar
#         encoding_type = 'utf-8-sig' if sheet_name == 'calendar' else 'utf-8'

#         df.to_csv(
#             csv_path,
#             sep=';',
#             index=False,
#             encoding=encoding_type,
#             quoting=csv.QUOTE_MINIMAL
#         )

#         print(f"Generated: '{csv_filename}' using {encoding_type} ({len(df)} rows)")

#     print("\n¡Completado con éxito!")


# if __name__ == '__main__':
#     convert_excel_to_csvs()
import csv
import os
import pandas as pd

EXCEL_FILE = './gripic_data.xlsx'
OUTPUT_DIR = './inputs/'


def format_date_cell(val):
    """
    Converts any date value from Excel
    (serial numbers, empty dates, strings) to DD/MM/YYYY format.
    """
    if pd.isna(val) or str(val).strip() == '':
        return ''

    val_str = str(val).strip().lstrip("'")

    # If it already has the DD/MM/YYYY format
    if '/' in val_str and len(val_str.split('/')) == 3:
        return val_str

    # If Excel automatically converted it to a Python timestamp/date
    try:
        parsed_dt = pd.to_datetime(
            val_str,
            dayfirst=True,
            errors='coerce'
        )

        if not pd.isna(parsed_dt):
            return parsed_dt.strftime('%d/%m/%Y')

    except Exception:
        pass

    return val_str


def convert_excel_to_csvs():
    if not os.path.exists(EXCEL_FILE):
        print(f"Error: '{EXCEL_FILE}' was not found.")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    xls = pd.ExcelFile(EXCEL_FILE)

    for sheet_name in xls.sheet_names:
        # 1. Read all cells
        df = pd.read_excel(
            xls,
            sheet_name=sheet_name,
            dtype=str
        )

        # 2. Remove accidental empty rows from Excel
        df = df.dropna(how='all')

        # 3. General text and quote cleanup
        for col in df.columns:
            df[col] = (
                df[col]
                .fillna('')
                .astype(str)
                .str.replace("'", "", regex=False)
                .str.strip()
            )

            # Automatically format date columns to avoid split('/') errors
            if 'date' in col.lower():
                df[col] = df[col].apply(format_date_cell)

        # 4. Remove rows where the main field (Title / name / etc.) is empty
        if 'Titre' in df.columns:
            df = df[df['Titre'] != '']
        elif 'nom' in df.columns:
            df = df[df['nom'] != '']

        csv_filename = f"{sheet_name}.csv"
        csv_path = os.path.join(OUTPUT_DIR, csv_filename)

        encoding_type = (
            'utf-8-sig'
            if sheet_name == 'calendar'
            else 'utf-8'
        )

        df.to_csv(
            csv_path,
            sep=';',
            index=False,
            encoding=encoding_type,
            quoting=csv.QUOTE_MINIMAL
        )

        print(
            f"Generated: '{csv_filename}' "
            f"with {len(df)} rows processed."
        )

    print("\nCompleted successfully!")


if __name__ == '__main__':
    convert_excel_to_csvs()