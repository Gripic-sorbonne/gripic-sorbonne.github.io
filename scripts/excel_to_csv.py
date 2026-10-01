import csv
import os
import pandas as pd

EXCEL_FILE = './gripic_data.xlsx'  # Cambia por el nombre exacto de tu archivo Excel si es otro
OUTPUT_DIR = './inputs/'


def format_dates_in_df(df: pd.DataFrame) -> pd.DataFrame:
    """Convierte todas las columnas con fechas al formato DD/MM/YYYY sin hora."""
    for col in df.columns:
        if 'date' in col.lower():
            # Convertir a datetime forzando día primero (DD/MM/YYYY)
            parsed = pd.to_datetime(df[col], dayfirst=True, errors='coerce')
            # Formatear estrictamente a DD/MM/YYYY
            df[col] = parsed.dt.strftime('%d/%m/%Y').fillna(df[col])
    return df


def convert_excel_to_csvs():
    if not os.path.exists(EXCEL_FILE):
        print(f"Error: File '{EXCEL_FILE}' was not found.")
        return

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR, exist_ok=True)

    xls = pd.ExcelFile(EXCEL_FILE)
    print(f"Sheets found: {xls.sheet_names}")

    for sheet_name in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet_name)

        df = format_dates_in_df(df)

        csv_filename = f"{sheet_name}.csv"
        csv_path = os.path.join(OUTPUT_DIR, csv_filename)

        df.to_csv(
            csv_path,
            sep=';',
            index=False,
            encoding='utf-8',
            quoting=csv.QUOTE_MINIMAL  # O QUOTE_ALL si tu sistema lo requiere
        )

        print(f"Generated: '{csv_filename}' ({len(df)} rows)")

    print("\n¡Listo! El CSV se generó sin horas extra en las fechas.")


if __name__ == '__main__':
    convert_excel_to_csvs()