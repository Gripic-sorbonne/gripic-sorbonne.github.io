import csv
import os
import pandas as pd

EXCEL_FILE = './gripic_data.xlsx'
OUTPUT_DIR = './inputs/'


def format_dates_in_df(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure all datetime columns are formatted as DD/MM/YYYY."""
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.strftime('%d/%m/%Y')
        elif 'date' in col.lower():
            parsed_dates = pd.to_datetime(df[col], errors='coerce')
            if not parsed_dates.isna().all():
                df[col] = parsed_dates.dt.strftime('%d/%m/%Y').fillna(df[col])
    return df


def convert_excel_to_csvs():
    if not os.path.exists(EXCEL_FILE):
        print(f"Error: File '{EXCEL_FILE}' was not found.")
        return

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR, exist_ok=True)

    xls = pd.ExcelFile(EXCEL_FILE)
    print(f"Sheets found in the Excel file: {xls.sheet_names}")

    for sheet_name in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet_name)

        df = format_dates_in_df(df)

        csv_filename = f"{sheet_name}.csv"
        csv_path = os.path.join(OUTPUT_DIR, csv_filename)

        # Force QUOTE_ALL to enclose every cell in quotes
        df.to_csv(
            csv_path,
            sep=';',
            index=False,
            encoding='utf-8',
            quoting=csv.QUOTE_ALL
        )

        print(
            f"Generated/Replaced: '{csv_filename}' "
            f"({len(df)} rows)"
        )

    print(
        "\nProcess completed successfully! "
        "All CSV files have been updated with enclosed quotes."
    )


if __name__ == '__main__':
    convert_excel_to_csvs()