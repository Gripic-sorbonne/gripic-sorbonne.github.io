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


def convert_excel_to_csvs():
    if not os.path.exists(EXCEL_FILE):
        print(f"Error: No se encontró '{EXCEL_FILE}'")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    xls = pd.ExcelFile(EXCEL_FILE)

    for sheet_name in xls.sheet_names:
        # Lee la hoja respetando lo que el usuario escribió
        df = pd.read_excel(xls, sheet_name=sheet_name, dtype=str).fillna('')

        # LIMPIEZA AUTOMÁTICA:
        # Remueve cualquier comilla oculta que Excel agregue y limpia espacios
        for col in df.columns:
            df[col] = df[col].astype(str).str.replace("'", "", regex=False).str.strip()

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

        print(f"Generado: '{csv_filename}' de forma transparente.")


if __name__ == '__main__':
    convert_excel_to_csvs()