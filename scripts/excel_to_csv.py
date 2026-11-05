import csv
import os
import pandas as pd

EXCEL_FILE = './gripic_data.xlsx'
OUTPUT_DIR = './inputs/'


def format_date_cell(val):
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

    # 1. Mapeo de nombres normalizados/cortados hacia el nombre oficial completo
    categories_map = {}
    if 'categories' in xls.sheet_names:
        cat_df = pd.read_excel(xls, sheet_name='categories', dtype=str)
        nom_col = next((col for col in cat_df.columns if col.lower() == 'nom'), None)
        if nom_col:
            for val in cat_df[nom_col].dropna():
                full_name = str(val).strip()
                clean_full = full_name.lower()
                
                # Mapeamos nombre completo exacto
                categories_map[clean_full] = full_name
                
                # Mapeamos la base sin paréntesis o truncated
                base_name = clean_full.split('(')[0].strip()
                if base_name and base_name not in categories_map:
                    categories_map[base_name] = full_name

    system_sheets = {'categories', 'calendar'}

    for sheet_name in xls.sheet_names:
        sheet_clean = sheet_name.strip()
        sheet_lower = sheet_clean.lower()
        sheet_base = sheet_lower.split('(')[0].strip()

        # Determinar el nombre oficial final del CSV
        target_name = sheet_clean
        matched = False

        if sheet_lower in system_sheets:
            matched = True
        elif sheet_lower in categories_map:
            target_name = categories_map[sheet_lower]
            matched = True
        elif sheet_base in categories_map:
            target_name = categories_map[sheet_base]
            matched = True

        if not matched:
            print(f"Ignoring sheet '{sheet_name}' (does not match any submenu in categories).")
            continue

        # 1. Leer celdas
        df = pd.read_excel(xls, sheet_name=sheet_name, dtype=str)

        # Eliminar columnas sin cabecera
        unnamed_cols = [col for col in df.columns if str(col).startswith('Unnamed: ') or str(col).strip() == '']
        if unnamed_cols:
            df = df.drop(columns=unnamed_cols)

        # 2. Eliminar filas vacías
        df = df.dropna(how='all')

        # 3. Limpieza de comillas y formato de fecha
        for col in df.columns:
            df[col] = (
                df[col]
                .fillna('')
                .astype(str)
                .str.replace("'", "", regex=False)
                .str.strip()
            )

            if 'date' in col.lower():
                df[col] = df[col].apply(format_date_cell)

        # 4. Filtrar filas vacías según identificador
        if 'Titre' in df.columns:
            df = df[df['Titre'] != '']
        elif 'nom' in df.columns:
            df = df[df['nom'] != '']

        # Usar el nombre completo restaurado para el CSV
        csv_filename = f"{target_name}.csv"
        csv_path = os.path.join(OUTPUT_DIR, csv_filename)

        encoding_type = 'utf-8-sig' if 'calendar' in sheet_lower else 'utf-8'

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