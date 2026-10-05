from pathlib import Path
import hashlib

import pandas as pd


INPUT_FILE = Path(
    "data/processed/cur_customer_transactions.parquet"
)

OUTPUT_CSV = Path(
    "data/processed/dim_customer.csv"
)

OUTPUT_PARQUET = Path(
    "data/processed/dim_customer.parquet"
)


def generate_customer_id(customer_name):
    """
    Create a deterministic customer ID from the customer name.
    """

    normalized = (
        str(customer_name)
        .strip()
        .lower()
    )

    digest = hashlib.sha256(
        normalized.encode("utf-8")
    ).hexdigest()[:10]

    return f"CUST_{digest.upper()}"


def build_customer_dimension(dataframe):
    """
    Build one analytics-ready row per customer.
    """

    df = dataframe.copy()

    df = df[
        df["customer_name"].notna()
    ].copy()

    df["customer_name"] = (
        df["customer_name"]
        .astype(str)
        .str.strip()
    )

    grouped = (
        df.groupby(
            "customer_name",
            dropna=False,
        )
        .agg(
            first_transaction_date=(
                "transaction_date",
                "min",
            ),
            last_transaction_date=(
                "transaction_date",
                "max",
            ),
            transaction_count=(
                "customer_name",
                "size",
            ),
            total_amount_due=(
                "amount_due",
                "sum",
            ),
            total_amount_received=(
                "amount_received",
                "sum",
            ),
        )
        .reset_index()
    )

    grouped["customer_id"] = (
        grouped["customer_name"]
        .apply(generate_customer_id)
    )

    grouped["current_balance"] = (
        grouped["total_amount_due"].fillna(0)
        - grouped[
            "total_amount_received"
        ].fillna(0)
    )

    columns = [
        "customer_id",
        "customer_name",
        "first_transaction_date",
        "last_transaction_date",
        "transaction_count",
        "total_amount_due",
        "total_amount_received",
        "current_balance",
    ]

    return grouped[columns]


def run_customer_dimension():
    df = pd.read_parquet(
        INPUT_FILE
    )

    customers = (
        build_customer_dimension(
            df
        )
    )

    customers.to_csv(
        OUTPUT_CSV,
        index=False,
    )

    customers.to_parquet(
        OUTPUT_PARQUET,
        index=False,
    )

    print(
        "\nPLUTO CUSTOMER DIMENSION"
    )
    print(
        "------------------------"
    )

    print(
        f"Customers: {len(customers)}"
    )

    print(
        "\nTOP CUSTOMERS BY TRANSACTION COUNT"
    )

    print(
        customers[
            [
                "customer_name",
                "transaction_count",
                "current_balance",
            ]
        ]
        .sort_values(
            "transaction_count",
            ascending=False,
        )
        .head(15)
        .to_string(
            index=False
        )
    )

    print(
        f"\nCSV: {OUTPUT_CSV}"
    )

    print(
        f"Parquet: {OUTPUT_PARQUET}"
    )

    return customers


if __name__ == "__main__":
    run_customer_dimension()
