from pathlib import Path
from datetime import datetime
import re

import pandas as pd


SOURCE_FILE = Path("data/raw/PLUTO TRADING COMPANY.xlsx")

OUTPUT_CSV = Path(
    "data/processed/stg_customer_transactions.csv"
)

OUTPUT_PARQUET = Path(
    "data/processed/stg_customer_transactions.parquet"
)


# These sheets have different structures and will
# get their own ingestion jobs later.
EXCLUDED_SHEETS = {
    "P n L",
    "SALES",
    "UK ORDERS",
    "Cheque details",
}


COLUMN_ALIASES = {
    "date": {
        "DATE",
    },

    "reference_number": {
        "SR #",
        "SR#",
        "INVOICE #",
        "INVOICE#",
        "INV #",
        "INV#",
    },

    "description": {
        "DESCRIPTION",
    },

    "category": {
        "CATEGORY",
        "CAT",
    },

    "quantity": {
        "QTY",
        "PCS",
    },

    "weight_kg": {
        "KG",
    },

    "tax": {
        "TAX",
    },

    "rate": {
        "RATE",
    },

    "amount_due": {
        "DUE",
        "AMOUNT DUE",
    },

    "amount_received": {
        "REC",
        "RECVD",
        "RECV",
        "RECV",
        "RECEIVED",
        "AMOUNT REC",
        "AMOUNT RECEIVED",
    },

    "balance": {
        "BALANCE",
        "BAL",
    },
}


def normalise_header(value):
    """
    Convert inconsistent Excel column names into
    comparable uppercase strings.
    """

    if pd.isna(value):
        return ""

    value = str(value).strip().upper()

    value = re.sub(
        r"\s+",
        " ",
        value,
    )

    return value


def find_header_row(df):
    """
    Search the first few rows for the transaction header.

    Most Pluto customer sheets contain DESCRIPTION,
    RATE and a balance column in the header.
    """

    search_limit = min(
        10,
        len(df),
    )

    for row_index in range(search_limit):

        headers = {
            normalise_header(value)
            for value in df.iloc[row_index]
        }

        has_description = (
            "DESCRIPTION" in headers
        )

        has_rate = (
            "RATE" in headers
        )

        has_balance = (
            "BALANCE" in headers
            or "BAL" in headers
        )

        if (
            has_description
            and has_rate
            and has_balance
        ):
            return row_index

    return None


def build_column_map(header_row):
    """
    Map the original Excel columns onto our
    standard transaction schema.
    """

    column_map = {}

    for column_index, raw_header in enumerate(
        header_row
    ):

        header = normalise_header(
            raw_header
        )

        for standard_name, aliases in (
            COLUMN_ALIASES.items()
        ):

            if (
                header in aliases
                and standard_name not in column_map
            ):
                column_map[
                    standard_name
                ] = column_index

    return column_map


def looks_like_date_column(series):
    """
    Some sheets contain transaction dates but the
    DATE header itself is blank.

    Detect a likely Excel serial-date column.
    """

    values = series.dropna()

    if values.empty:
        return False

    for value in values.head(20):

        if isinstance(
            value,
            (int, float),
        ):
            if 30000 <= value <= 60000:
                return True

    return False


def parse_date(value):
    """
    Convert Excel serial dates or text dates into
    pandas timestamps.
    """

    if pd.isna(value):
        return pd.NaT

    if isinstance(
        value,
        (int, float),
    ):

        if 30000 <= value <= 60000:

            return pd.to_datetime(
                value,
                unit="D",
                origin="1899-12-30",
                errors="coerce",
            )

    return pd.to_datetime(
        value,
        errors="coerce",
        dayfirst=True,
    )


def clean_number(value):
    """
    Convert numeric-looking values into numbers.
    """

    if pd.isna(value):
        return None

    if isinstance(
        value,
        (int, float),
    ):
        return float(value)

    cleaned = (
        str(value)
        .replace(",", "")
        .replace("Rs.", "")
        .replace("Rs", "")
        .strip()
    )

    number = pd.to_numeric(
        cleaned,
        errors="coerce",
    )

    if pd.isna(number):
        return None

    return float(number)


def clean_text(value):
    """
    Clean text values while preserving their meaning.
    """

    if pd.isna(value):
        return None

    value = str(value).strip()

    if not value:
        return None

    return value


def get_value(
    row,
    column_map,
    field,
):
    """
    Safely retrieve a value from a mapped column.
    """

    column_index = column_map.get(
        field
    )

    if column_index is None:
        return None

    return row.iloc[
        column_index
    ]


def ingest_customer_sheet(
    excel_file,
    sheet_name,
):
    """
    Convert one Pluto customer ledger into the
    standard staging schema.
    """

    df = pd.read_excel(
        excel_file,
        sheet_name=sheet_name,
        header=None,
    )

    header_index = find_header_row(
        df
    )

    if header_index is None:

        print(
            f"WARNING: Header not found: "
            f"{sheet_name}"
        )

        return pd.DataFrame()

    header_row = df.iloc[
        header_index
    ]

    column_map = build_column_map(
        header_row
    )

    # Some sheets, such as JILANI STORE,
    # contain dates in column A but the DATE
    # header is blank.
    if "date" not in column_map:

        for column_index in range(
            len(df.columns)
        ):

            data_below_header = df.iloc[
                header_index + 1:,
                column_index,
            ]

            if looks_like_date_column(
                data_below_header
            ):

                column_map[
                    "date"
                ] = column_index

                break

    records = []

    data_rows = df.iloc[
        header_index + 1:
    ]

    for dataframe_index, row in (
        data_rows.iterrows()
    ):

        description = clean_text(
            get_value(
                row,
                column_map,
                "description",
            )
        )

        category = clean_text(
            get_value(
                row,
                column_map,
                "category",
            )
        )

        reference = clean_text(
            get_value(
                row,
                column_map,
                "reference_number",
            )
        )

        quantity = clean_number(
            get_value(
                row,
                column_map,
                "quantity",
            )
        )

        weight_kg = clean_number(
            get_value(
                row,
                column_map,
                "weight_kg",
            )
        )

        rate = clean_number(
            get_value(
                row,
                column_map,
                "rate",
            )
        )

        tax = clean_number(
            get_value(
                row,
                column_map,
                "tax",
            )
        )

        amount_due = clean_number(
            get_value(
                row,
                column_map,
                "amount_due",
            )
        )

        amount_received = clean_number(
            get_value(
                row,
                column_map,
                "amount_received",
            )
        )

        balance = clean_number(
            get_value(
                row,
                column_map,
                "balance",
            )
        )

        raw_date = get_value(
            row,
            column_map,
            "date",
        )

        transaction_date = parse_date(
            raw_date
        )

        # Ignore spreadsheet rows containing only
        # copied formulas / running balances.
        meaningful_values = [
            description,
            category,
            reference,
            quantity,
            weight_kg,
            rate,
            tax,
            amount_due,
            amount_received,
        ]

        if all(
            value is None
            for value in meaningful_values
        ):
            continue

        records.append(
            {
                "transaction_date":
                    transaction_date,

                "customer_name":
                    sheet_name.strip(),

                "reference_number":
                    reference,

                "description":
                    description,

                "category":
                    category,

                "quantity":
                    quantity,

                "weight_kg":
                    weight_kg,

                "tax":
                    tax,

                "rate":
                    rate,

                "amount_due":
                    amount_due,

                "amount_received":
                    amount_received,

                "balance":
                    balance,

                "source_workbook":
                    SOURCE_FILE.name,

                "source_sheet":
                    sheet_name,

                "source_row":
                    dataframe_index + 1,

                "ingested_at":
                    datetime.now(),
            }
        )

    return pd.DataFrame(
        records
    )


def ingest_customer_transactions():
    """
    Consolidate all Pluto customer ledgers into
    one staging dataset.
    """

    excel_file = pd.ExcelFile(
        SOURCE_FILE
    )

    customer_sheets = [
        sheet
        for sheet in excel_file.sheet_names
        if sheet not in EXCLUDED_SHEETS
    ]

    datasets = []

    print(
        "\nPLUTO CUSTOMER TRANSACTION INGESTION"
    )

    print(
        "----------------------------------"
    )

    for sheet_name in customer_sheets:

        dataset = ingest_customer_sheet(
            excel_file,
            sheet_name,
        )

        print(
            f"{sheet_name:<25} "
            f"{len(dataset):>5} transactions"
        )

        if not dataset.empty:
            datasets.append(
                dataset
            )

    if not datasets:
        raise ValueError(
            "No customer transaction data found."
        )

    combined = pd.concat(
        datasets,
        ignore_index=True,
    )

    combined = combined.sort_values(
        by=[
            "transaction_date",
            "customer_name",
        ],
        na_position="last",
    )

    combined.reset_index(
        drop=True,
        inplace=True,
    )

    OUTPUT_CSV.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    combined.to_csv(
        OUTPUT_CSV,
        index=False,
    )

    combined.to_parquet(
        OUTPUT_PARQUET,
        index=False,
    )

    print(
        "\n----------------------------------"
    )

    print(
        f"Customer sheets processed: "
        f"{len(customer_sheets)}"
    )

    print(
        f"Transactions extracted: "
        f"{len(combined)}"
    )

    print(
        f"Unique customers: "
        f"{combined['customer_name'].nunique()}"
    )

    print(
        f"CSV: {OUTPUT_CSV}"
    )

    print(
        f"Parquet: {OUTPUT_PARQUET}"
    )

    return combined


if __name__ == "__main__":
    ingest_customer_transactions()
