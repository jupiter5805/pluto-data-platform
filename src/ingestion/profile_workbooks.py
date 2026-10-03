from pathlib import Path
from datetime import datetime
import json

import pandas as pd


RAW_DIR = Path("data/raw")
OUTPUT_FILE = Path("data/processed/workbook_profile.json")


def first_non_empty_row(df):
    """Return the index of the first row containing any data."""
    for index, row in df.iterrows():
        if row.notna().any():
            return int(index)
    return None


def clean_preview_value(value):
    """Convert values into JSON-safe readable values."""
    if pd.isna(value):
        return None

    if isinstance(value, pd.Timestamp):
        return value.isoformat()

    return str(value).strip()


def profile_sheet(excel_file, sheet_name):
    df = pd.read_excel(
        excel_file,
        sheet_name=sheet_name,
        header=None,
    )

    # Remove completely empty rows/columns only for profiling counts.
    populated = df.dropna(how="all").dropna(axis=1, how="all")

    header_row = first_non_empty_row(df)

    preview = []

    if header_row is not None:
        preview_df = df.iloc[header_row:header_row + 5]

        for _, row in preview_df.iterrows():
            preview.append(
                [clean_preview_value(value) for value in row.tolist()]
            )

    return {
        "sheet_name": sheet_name,
        "rows_with_data": int(populated.shape[0]),
        "columns_with_data": int(populated.shape[1]),
        "first_non_empty_row": header_row,
        "preview": preview,
    }


def profile_workbooks():
    profile = {
        "generated_at": datetime.now().isoformat(),
        "workbooks": [],
    }

    excel_files = sorted(RAW_DIR.glob("*.xlsx"))

    if not excel_files:
        raise FileNotFoundError(
            f"No Excel workbooks found in {RAW_DIR}"
        )

    for filepath in excel_files:
        print(f"\nProfiling: {filepath.name}")

        excel_file = pd.ExcelFile(filepath)

        workbook_profile = {
            "workbook": filepath.name,
            "sheet_count": len(excel_file.sheet_names),
            "sheets": [],
        }

        for sheet_name in excel_file.sheet_names:
            print(f"  → {sheet_name}")

            try:
                sheet_profile = profile_sheet(
                    excel_file,
                    sheet_name,
                )

                workbook_profile["sheets"].append(
                    sheet_profile
                )

            except Exception as error:
                workbook_profile["sheets"].append(
                    {
                        "sheet_name": sheet_name,
                        "error": str(error),
                    }
                )

        profile["workbooks"].append(workbook_profile)

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            profile,
            file,
            indent=2,
            ensure_ascii=False,
        )

    return profile


if __name__ == "__main__":
    result = profile_workbooks()

    total_workbooks = len(result["workbooks"])

    total_sheets = sum(
        workbook["sheet_count"]
        for workbook in result["workbooks"]
    )

    print("\n------------------------------")
    print("PLUTO DATA PROFILE COMPLETE")
    print("------------------------------")
    print(f"Workbooks profiled: {total_workbooks}")
    print(f"Sheets profiled: {total_sheets}")
    print(f"Profile saved to: {OUTPUT_FILE}")
