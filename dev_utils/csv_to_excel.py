import os
import csv
import pandas as pd
from openpyxl.styles import Alignment

INPUT_DIR = '../scripts/inputs'
OUTPUT_EXCEL = 'gripic_data.xlsx'

def convert_all_csvs_to_excel():
    base_path = INPUT_DIR if os.path.exists(INPUT_DIR) else '.'
    csv_files = [f for f in os.listdir(base_path) if f.endswith('.csv')]

    if not csv_files:
        print("No CSV files found.")
        return

    print(f"CSV files detected: {sorted(csv_files)}")

    with pd.ExcelWriter(OUTPUT_EXCEL, engine='openpyxl') as writer:
        for csv_file in sorted(csv_files):
            file_path = os.path.join(base_path, csv_file)
            sheet_name = os.path.splitext(csv_file)[0][:31]
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f, delimiter=';', quotechar='"')
                    rows = [r for r in reader if any(r)]
                
                if rows:
                    header = rows[0]
                    expected_cols = len(header)
                    
                    # Pad short rows with empty strings so no data is discarded
                    data = []
                    for r in rows[1:]:
                        if len(r) < expected_cols:
                            r = r + [''] * (expected_cols - len(r))
                        elif len(r) > expected_cols:
                            r = r[:expected_cols]
                        data.append(r)

                    df = pd.DataFrame(data, columns=header)
                else:
                    df = pd.DataFrame()

                df.to_excel(writer, sheet_name=sheet_name, index=False)
                
                # Auto-adjust column widths and enable text wrapping
                worksheet = writer.sheets[sheet_name]
                for col in worksheet.columns:
                    max_length = 0
                    col_letter = col[0].column_letter
                    
                    for cell in col:
                        cell.alignment = Alignment(wrap_text=True, vertical='top')
                        if cell.value is not None:
                            first_line = str(cell.value).split('\n')[0]
                            max_length = max(max_length, len(first_line))
                    
                    adjusted_width = min(max(max_length + 3, 12), 60)
                    worksheet.column_dimensions[col_letter].width = adjusted_width

                print(f"Successfully added sheet '{sheet_name}' ({len(df)} rows)")
            except Exception as e:
                print(f"Error processing {csv_file}: {e}")

    print(f"\nSuccess! Excel file '{OUTPUT_EXCEL}' generated correctly.")

if __name__ == '__main__':
    convert_all_csvs_to_excel()