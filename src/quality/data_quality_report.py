from pathlib import Path
import json

import pandas as pd


INPUT_FILE = Path(
    "data/processed/cur_customer_transactions.parquet"
)

OUTPUT_FILE = Path(
    "data/processed/data_quality_report.json"
)


def build_quality_report(dataframe):
    total_rows = len(dataframe)

    quality_counts = (
        dataframe["quality_flags"]
        .value_counts()
        .to_dict()
    )

    transaction_counts = (
        dataframe["transaction_type"]
        .value_counts()
        .to_dict()
    )

    clean_rows = int(
        (dataframe["quality_flags"] == "OK").sum()
    )

    flagged_rows = total_rows - clean_rows

    clean_percentage = (
        round(
            (clean_rows / total_rows) * 100,
            2,
        )
        if total_rows > 0
        else 0.0
    )

    flagged_percentage = (
        round(
            (flagged_rows / total_rows) * 100,
            2,
        )
        if total_rows > 0
        else 0.0
    )

    unknown_transactions = int(
        (
            dataframe["transaction_type"]
            == "UNKNOWN"
        ).sum()
    )

    missing_dates = int(
        (
            dataframe["date_status"]
            == "MISSING_DATE"
        ).sum()
    )

    future_dated = int(
        (
            dataframe["date_status"]
            == "FUTURE_DATED"
        ).sum()
    )

    pre_company_dates = int(
        (
            dataframe["date_status"]
            == "PRE_COMPANY_DATE"
        ).sum()
    )

    return {
        "total_rows": total_rows,
        "clean_rows": clean_rows,
        "flagged_rows": flagged_rows,
        "clean_percentage": clean_percentage,
        "flagged_percentage": flagged_percentage,
        "unknown_transactions":
            unknown_transactions,
        "missing_dates": missing_dates,
        "future_dated_transactions":
            future_dated,
        "pre_company_dates":
            pre_company_dates,
        "quality_flag_counts":
            quality_counts,
        "transaction_type_counts":
            transaction_counts,
    }


def run_report():
    df = pd.read_parquet(
        INPUT_FILE
    )

    report = build_quality_report(
        df
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            report,
            file,
            indent=2,
        )

    print(
        "\nPLUTO DATA QUALITY REPORT"
    )
    print(
        "-------------------------"
    )

    print(
        f"Total rows: "
        f"{report['total_rows']}"
    )

    print(
        f"Clean rows: "
        f"{report['clean_rows']}"
    )

    print(
        f"Flagged rows: "
        f"{report['flagged_rows']}"
    )

    print(
        f"Clean percentage: "
        f"{report['clean_percentage']}%"
    )

    print(
        f"Flagged percentage: "
        f"{report['flagged_percentage']}%"
    )

    print(
        f"Unknown transactions: "
        f"{report['unknown_transactions']}"
    )

    print(
        f"Missing dates: "
        f"{report['missing_dates']}"
    )

    print(
        f"Future dated: "
        f"{report['future_dated_transactions']}"
    )

    print(
        f"Pre-company dates: "
        f"{report['pre_company_dates']}"
    )

    print(
        f"\nReport saved to: "
        f"{OUTPUT_FILE}"
    )

    return report


if __name__ == "__main__":
    run_report()
