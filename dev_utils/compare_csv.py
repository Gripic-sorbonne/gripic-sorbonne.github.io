import os
import pandas as pd

ORIGINAL_DIR = '../scripts/inputs/save'  # Directory with original CSVs
GENERATED_DIR = '../scripts/inputs/'        # Directory with CSVs exported from Excel

CSV_FILES = [
    'calendar.csv',
    'categories.csv',
    'formations.csv',
    'international.csv',
    'members.csv',
    'publications.csv',
]


def normalize_cell(value):
    """Normalize text encoding and line breaks without altering content."""
    if pd.isna(value):
        return ''
    # Standardize line endings (\r\n -> \n) and remove trailing whitespace
    return str(value).replace('\r\n', '\n').strip()


def verify_csv_roundtrip():
    print("=== Round-Trip Data Integrity Check ===\n")
    all_passed = True

    for filename in CSV_FILES:
        orig_path = os.path.join(ORIGINAL_DIR, filename)
        gen_path = os.path.join(GENERATED_DIR, filename)

        if not os.path.exists(orig_path):
            print(f"⚠️ Original file missing: '{orig_path}'")
            continue

        if not os.path.exists(gen_path):
            print(f"❌ Generated file missing: '{gen_path}'")
            all_passed = False
            continue

        # Load both CSVs with Python engine to handle multi-line strings correctly
        df_orig = pd.read_csv(
            orig_path, sep=';', engine='python', dtype=str
        ).fillna('')
        df_gen = pd.read_csv(
            gen_path, sep=';', engine='python', dtype=str
        ).fillna('')

        # 1. Compare shape (row & column counts)
        if df_orig.shape != df_gen.shape:
            print(
                f"❌ [{filename}] Dimension mismatch! "
                f"Original: {df_orig.shape} vs Generated: {df_gen.shape}"
            )
            all_passed = False
            continue

        # 2. Compare content cell by cell
        total_mismatches = 0
        for col in df_orig.columns:
            if col not in df_gen.columns:
                print(f"❌ [{filename}] Missing column: '{col}'")
                total_mismatches += 1
                continue

            orig_col = df_orig[col].apply(normalize_cell)
            gen_col = df_gen[col].apply(normalize_cell)

            mismatches = (orig_col != gen_col).sum()
            if mismatches > 0:
                print(
                    f"  -> Field '{col}' has {mismatches} differences."
                )
                total_mismatches += mismatches

        if total_mismatches == 0:
            print(
                f"✓ [{filename}] PASSED! Integrity 100% intact "
                f"({len(df_orig)} rows, {len(df_orig.columns)} cols)"
            )
        else:
            print(
                f"❌ [{filename}] FAILED with {total_mismatches} total content differences."
            )
            all_passed = False

    print("\n=======================================")
    if all_passed:
        print(
            "🎉 SUCCESS: The round-trip is completely lossless. No data was corrupted."
        )
    else:
        print(
            "⚠️ WARNING: Data corruption or mismatches found between original and generated CSVs."
        )


if __name__ == '__main__':
    verify_csv_roundtrip()