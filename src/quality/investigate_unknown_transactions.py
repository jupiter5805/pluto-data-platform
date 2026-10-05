from pathlib import Path

import pandas as pd


INPUT_FILE = Path(
    "data/processed/cur_customer_transactions.parquet"
)

OUTPUT_FILE = Path(
    "data/processed/unknown_transactions_report.csv"
)


def normalise_text(value):
    if pd.isna(value):
        return "NULL"

    text = str(value).strip().lower()

    if not text:
        return "NULL"

    return text


def investigate_unknown_transactions(
    dataframe,
):
    """
    Return transactions that could not be
    classified by the transformation layer.
    """

    unknown = dataframe[
        dataframe["transaction_type"]
        == "UNKNOWN"
    ].copy()

    unknown[
        "normalised_category"
    ] = unknown["category"].apply(
        normalise_text
    )

    unknown[
        "normalised_description"
    ] = unknown["description"].apply(
        normalise_text
    )

    return unknown


def run_investigation():
    df = pd.read_parquet(
        INPUT_FILE
    )

    unknown = (
        investigate_unknown_transactions(
            df
        )
    )

    report_columns = [
        "transaction_date",
        "customer_name",
        "reference_number",
        "description",
        "category",
        "amount_due",
        "amount_received",
        "balance",
        "normalised_category",
        "normalised_description",
        "source_sheet",
        "source_row",
    ]

    report = unknown[
        report_columns
    ]

    report.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    print(
        "\nUNKNOWN TRANSACTION INVESTIGATION"
    )
    print(
        "---------------------------------"
    )

    print(
        f"Unknown transactions: "
        f"{len(report)}"
    )

    print(
        "\nUNKNOWN BY CUSTOMER"
    )

    print(
        report[
            "customer_name"
        ]
        .value_counts()
        .to_string()
    )

    print(
        "\nUNKNOWN CATEGORIES"
    )

    print(
        report[
            "normalised_category"
        ]
        .value_counts()
        .to_string()
    )

    print(
        "\nUNKNOWN DESCRIPTIONS"
    )

    print(
        report[
            "normalised_description"
        ]
        .value_counts()
        .head(50)
        .to_string()
    )

    print(
        "\nDETAILED UNKNOWN RECORDS"
    )

    print(
        report[
            [
                "customer_name",
                "transaction_date",
                "description",
                "category",
                "amount_due",
                "amount_received",
                "source_row",
            ]
        ]
        .to_string(
            index=False
        )
    )

    print(
        f"\nReport saved to: "
        f"{OUTPUT_FILE}"
    )

    return report


if __name__ == "__main__":
    run_investigation()
