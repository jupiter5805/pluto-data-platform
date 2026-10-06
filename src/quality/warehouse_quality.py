from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

INPUT = Path("data/processed/cur_customer_transactions.parquet")
OUTPUT = Path("data/processed/warehouse_quality_report.json")


def build_report(df: pd.DataFrame) -> dict:
    rows = len(df)

    source_cols = [
        col
        for col in ["source_workbook", "source_sheet", "source_row"]
        if col in df.columns
    ]

    duplicate_source_rows = (
        int(df.duplicated(source_cols).sum())
        if len(source_cols) == 3
        else 0
    )

    missing_customer = (
        int(df["customer_name"].isna().sum())
        if "customer_name" in df.columns
        else rows
    )

    # Missing dates are reported separately from malformed/invalid dates.
    # Some operational ledger rows can legitimately be undated, so missing
    # dates are not treated as a hard platform failure by themselves.
    if "transaction_date" in df.columns:
        raw_dates = df["transaction_date"]
        missing_dates = int(raw_dates.isna().sum())
        parsed_dates = pd.to_datetime(raw_dates, errors="coerce")
        invalid_non_null_dates = int(
            (raw_dates.notna() & parsed_dates.isna()).sum()
        )
    else:
        missing_dates = rows
        invalid_non_null_dates = rows

    # If the curated layer already classified date quality, honour that
    # semantic classification as well.
    invalid_date_status = 0
    if "date_status" in df.columns:
        invalid_date_status = int(
            df["date_status"]
            .astype("string")
            .str.contains("invalid", case=False, na=False)
            .sum()
        )

    invalid_date_rows = max(
        invalid_non_null_dates,
        invalid_date_status,
    )

    unknown_transactions = (
        int(
            df["transaction_type"]
            .astype(str)
            .str.upper()
            .eq("UNKNOWN")
            .sum()
        )
        if "transaction_type" in df.columns
        else 0
    )

    unknown_rate = (
        unknown_transactions / rows
        if rows
        else 0.0
    )

    invalid_date_rate = (
        invalid_date_rows / rows
        if rows
        else 1.0
    )

    checks = {
        "dataset_not_empty": rows > 0,
        "duplicate_source_rows_zero": duplicate_source_rows == 0,
        "missing_customer_below_5_percent": (
            (missing_customer / rows) < 0.05
            if rows
            else False
        ),
        "malformed_dates_below_1_percent": (
            invalid_date_rate < 0.01
        ),
        "unknown_rate_below_10_percent": unknown_rate < 0.10,
    }

    return {
        "row_count": rows,
        "duplicate_source_rows": duplicate_source_rows,
        "missing_customer": missing_customer,
        "missing_dates": missing_dates,
        "invalid_non_null_dates": invalid_non_null_dates,
        "invalid_date_status": invalid_date_status,
        "invalid_date_rows": invalid_date_rows,
        "invalid_date_rate": round(invalid_date_rate, 4),
        "unknown_transactions": unknown_transactions,
        "unknown_rate": round(unknown_rate, 4),
        "checks": checks,
        "passed": all(checks.values()),
    }


def main():
    if not INPUT.exists():
        raise FileNotFoundError(f"Missing input: {INPUT}")

    df = pd.read_parquet(INPUT)
    report = build_report(df)

    OUTPUT.write_text(
        json.dumps(report, indent=2)
    )

    print()
    print("WAREHOUSE DATA QUALITY")
    print("----------------------")
    print(f"Rows                  : {report['row_count']:,}")
    print(f"Missing dates         : {report['missing_dates']:,}")
    print(f"Invalid date rows     : {report['invalid_date_rows']:,}")
    print(f"UNKNOWN transactions  : {report['unknown_transactions']:,}")
    print()

    for name, passed in report["checks"].items():
        print(
            f"{name:<38} "
            f"{'PASS' if passed else 'FAIL'}"
        )

    print(f"\nReport: {OUTPUT}")

    if not report["passed"]:
        raise SystemExit(
            "Warehouse quality checks failed."
        )


if __name__ == "__main__":
    main()
