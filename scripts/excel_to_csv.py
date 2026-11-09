import csv
import os
import pandas as pd
import unicodedata
import re

EXCEL_FILE = './gripic_data.xlsx'
OUTPUT_DIR = './inputs/'


def normalize_text(s: str) -> str:
    if not s:
        return ""
    s = unicodedata.normalize('NFD', s)
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    return re.sub(r'[^a-z0-9]', '', s.lower())


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

    # 1. Mapeo inteligente desde la hoja 'categories'
    categories_map = {}
    if 'categories' in xls.sheet_names:
        cat_df = pd.read_excel(xls, sheet_name='categories', dtype=str)
        nom_col = next((col for col in cat_df.columns if col.lower() == 'nom'), None)
        if nom_col:
            for val in cat_df[nom_col].dropna():
                full_name = str(val).strip()
                norm_full = normalize_text(full_name)
                if norm_full:
                    categories_map[norm_full] = full_name

    system_sheets = {'categories', 'calendar'}

    for sheet_name in xls.sheet_names:
        sheet_clean = sheet_name.strip()
        sheet_lower = sheet_clean.lower()
        sheet_norm = normalize_text(sheet_clean)

        target_name = sheet_clean
        matched = False

        if sheet_lower in system_sheets or sheet_norm in system_sheets:
            matched = True
        else:
            # Matching inmune al corte de 31 caracteres de Excel usando prefijos normalizados
            for cat_norm, full_name in categories_map.items():
                min_len = min(len(sheet_norm), len(cat_norm), 25) # Compara los primeros 25 caracteres normalizados
                if min_len > 0 and sheet_norm[:min_len] == cat_norm[:min_len]:
                    target_name = full_name
                    matched = True
                    break

        if not matched:
            print(f"Ignoring sheet '{sheet_name}' (does not match any submenu in categories).")
            continue

        # 2. Leer celdas de la hoja de forma completamente aislada
        df = pd.read_excel(xls, sheet_name=sheet_name, dtype=str)

        # Limpieza estricta de cabeceras y eliminación de columnas vacías o fantasma (.1)
        df.columns = [str(col).strip() for col in df.columns]
        df = df.loc[:, ~df.columns.str.startswith('Unnamed')]
        df = df.loc[:, df.columns != '']
        df = df.loc[:, ~df.columns.duplicated()]

        # 3. Eliminar filas vacías
        df = df.dropna(how='all')

        # 4. Rellenar nulos y formatear fechas conservando apóstrofes
        df = df.fillna('')
        for col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            if 'date' in col.lower():
                df[col] = df[col].apply(format_date_cell)

        # 5. Filtrar filas vacías según el título principal
        title_col = next((col for col in df.columns if col.lower() in ['_title', 'title', 'titre']), None)
        if title_col:
            df = df[df[title_col] != '']

        # Escribir el CSV limpio
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

        print(f"Generated cleanly: '{csv_filename}' ({len(df)} rows processed).")

    print("\nExcel-to-CSV conversion completed successfully!")


if __name__ == '__main__':
    convert_excel_to_csvs()