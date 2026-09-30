import os
import pandas as pd

EXCEL_FILE = './gripic_data.xlsx'
OUTPUT_DIR = './inputs/'


def convert_excel_to_csvs():
    if not os.path.exists(EXCEL_FILE):
        print(f"Error: File '{EXCEL_FILE}' was not found.")
        return

    # Read all sheets from the Excel workbook
    xls = pd.ExcelFile(EXCEL_FILE)
    print(f"Sheets found in the Excel file: {xls.sheet_names}")

    for sheet_name in xls.sheet_names:
        # Read the data from the current sheet
        df = pd.read_excel(xls, sheet_name=sheet_name)

        # Define the output CSV file path
        csv_filename = f"{sheet_name}.csv"
        csv_path = os.path.join(OUTPUT_DIR, csv_filename)

        # Export to CSV using ';' as the separator and UTF-8 encoding
        # index=False prevents pandas from including the row numbers
        df.to_csv(
            csv_path,
            sep=';',
            index=False,
            encoding='utf-8'
        )

        print(
            f"Generated/Replaced: '{csv_filename}' "
            f"({len(df)} rows)"
        )

    print(
        "\nProcess completed successfully! "
        "All CSV files have been updated."
    )


if __name__ == '__main__':
    convert_excel_to_csvs()