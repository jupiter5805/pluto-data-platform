from pathlib import Path

import pandas as pd


INPUT_FILE = Path(
    "data/processed/stg_customer_transactions.parquet"
)

OUTPUT_CSV = Path(
    "data/processed/cur_customer_transactions.csv"
)

OUTPUT_PARQUET = Path(
    "data/processed/cur_customer_transactions.parquet"
)

COMPANY_START_DATE = pd.Timestamp("2020-01-01")


def normalise_text(value):
    if pd.isna(value):
        return ""

    return str(value).strip().lower()


def classify_transaction(row):
    """
    Return both the transaction classification
    and the reason used to classify it.
    """

    category = normalise_text(
        row.get("category")
    )

    description = normalise_text(
        row.get("description")
    )

    combined = f"{category} {description}"

    amount_due = row.get("amount_due")
    amount_received = row.get(
        "amount_received"
    )

    due = (
        0
        if pd.isna(amount_due)
        else float(amount_due)
    )

    received = (
        0
        if pd.isna(amount_received)
        else float(amount_received)
    )

    if any(
        word in combined
        for word in [
            "rejection",
            "rejected",
            "return",
            "returned",
            "damaged",
        ]
    ):
        return (
            "RETURN_REJECTION",
            "return_or_rejection_keyword",
        )

    if any(
        word in combined
        for word in [
            "tax",
            "wht",
            "withheld",
            "with held",
            "gst",
        ]
    ):
        return (
            "TAX",
            "tax_keyword",
        )

    if "advance" in combined:
        return (
            "ADVANCE",
            "advance_keyword",
        )

    if "discount" in combined:
        return (
            "ADJUSTMENT",
            "adjustment_keyword",
        )

    if any(
        word in combined
        for word in [
            "income",
            "payment",
            "cash",
            "cheque",
            "online",
            "received",
            "recvd",
            "recovered",
            "deposit",
            "meezan",
        ]
    ):
        if received > 0:
            return (
                "PAYMENT",
                "payment_keyword_and_received_amount",
            )

    if any(
        word in category
        for word in [
            "sale",
            "sales",
            "credit sales",
        ]
    ):
        return (
            "SALE",
            "explicit_sales_category",
        )

    if received > 0 and due == 0:
        return (
            "PAYMENT",
            "received_amount_fallback",
        )

    if due > 0 and received == 0:
        return (
            "SALE",
            "due_amount_fallback",
        )

    if due > 0 and received > 0:
        return (
            "ADJUSTMENT",
            "both_due_and_received",
        )

    return (
        "UNKNOWN",
        "unclassified",
    )


def get_date_status(
    transaction_date,
    as_of_date,
):
    if pd.isna(transaction_date):
        return "MISSING_DATE"

    transaction_date = pd.Timestamp(
        transaction_date
    )

    if transaction_date < COMPANY_START_DATE:
        return "PRE_COMPANY_DATE"

    if transaction_date > as_of_date:
        return "FUTURE_DATED"

    return "VALID"


def build_quality_flags(
    row,
    as_of_date,
):
    flags = []

    date_status = get_date_status(
        row.get("transaction_date"),
        as_of_date,
    )

    if date_status != "VALID":
        flags.append(date_status)

    due = row.get("amount_due")
    received = row.get(
        "amount_received"
    )

    if (
        pd.notna(due)
        and float(due) < 0
    ):
        flags.append(
            "NEGATIVE_DUE"
        )

    if (
        pd.notna(received)
        and float(received) < 0
    ):
        flags.append(
            "NEGATIVE_RECEIVED"
        )

    if (
        pd.notna(due)
        and pd.notna(received)
        and float(due) != 0
        and float(received) != 0
    ):
        flags.append(
            "BOTH_DUE_AND_RECEIVED"
        )

    if not flags:
        return "OK"

    return "|".join(flags)


def transform_customer_transactions(
    dataframe,
    as_of_date=None,
):
    df = dataframe.copy()

    if as_of_date is None:
        as_of_date = (
            pd.Timestamp.today()
            .normalize()
        )
    else:
        as_of_date = pd.Timestamp(
            as_of_date
        )

    classifications = df.apply(
        classify_transaction,
        axis=1,
    )

    df["transaction_type"] = (
        classifications.apply(
            lambda result: result[0]
        )
    )

    df["classification_reason"] = (
        classifications.apply(
            lambda result: result[1]
        )
    )

    df["date_status"] = df[
        "transaction_date"
    ].apply(
        lambda date: get_date_status(
            date,
            as_of_date,
        )
    )

    df["quality_flags"] = df.apply(
        lambda row: build_quality_flags(
            row,
            as_of_date,
        ),
        axis=1,
    )

    df["is_realized_transaction"] = (
        df["date_status"] == "VALID"
    )

    df["ledger_effect"] = (
        df["amount_due"].fillna(0)
        - df["amount_received"].fillna(0)
    )

    return df


def run_transformation():
    df = pd.read_parquet(
        INPUT_FILE
    )

    curated = (
        transform_customer_transactions(
            df
        )
    )

    curated.to_csv(
        OUTPUT_CSV,
        index=False,
    )

    curated.to_parquet(
        OUTPUT_PARQUET,
        index=False,
    )

    print(
        "\nPLUTO CURATED TRANSACTION LAYER"
    )
    print(
        "--------------------------------"
    )

    print(
        f"Transactions: {len(curated)}"
    )

    print("\nTRANSACTION TYPES")
    print(
        curated[
            "transaction_type"
        ]
        .value_counts()
        .to_string()
    )

    print(
        "\nCLASSIFICATION REASONS"
    )
    print(
        curated[
            "classification_reason"
        ]
        .value_counts()
        .to_string()
    )

    print("\nDATE STATUS")
    print(
        curated[
            "date_status"
        ]
        .value_counts()
        .to_string()
    )

    print("\nQUALITY FLAGS")
    print(
        curated[
            "quality_flags"
        ]
        .value_counts()
        .head(20)
        .to_string()
    )

    print(
        "\nRealized transactions:"
    )
    print(
        curated[
            "is_realized_transaction"
        ].sum()
    )

    print(
        "\nCurated dataset:"
    )
    print(
        OUTPUT_PARQUET
    )


if __name__ == "__main__":
    run_transformation()
