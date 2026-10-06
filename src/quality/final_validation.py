from pathlib import Path
import json
import pandas as pd

PROCESSED = Path("data/processed")
CURATED = PROCESSED / "cur_customer_transactions.parquet"
CUSTOMERS = PROCESSED / "dim_customer.parquet"
QUALITY = PROCESSED / "data_quality_report.json"
UNKNOWN = PROCESSED / "unknown_transactions_report.csv"

def main():
    required = [CURATED, CUSTOMERS, QUALITY, UNKNOWN]
    missing = [str(p) for p in required if not p.exists()]
    if missing:
        raise FileNotFoundError(
            "Missing required output files:\n" + "\n".join(missing)
        )

    curated = pd.read_parquet(CURATED)
    customers = pd.read_parquet(CUSTOMERS)

    if curated.empty:
        raise AssertionError("Curated transaction dataset is empty.")
    if customers.empty:
        raise AssertionError("Customer dimension is empty.")

    for col in ("customer_id", "customer_name"):
        if col not in customers.columns:
            raise AssertionError(f"Missing customer dimension column: {col}")

    if not customers["customer_id"].is_unique:
        raise AssertionError("customer_id is not unique.")
    if not customers["customer_name"].is_unique:
        raise AssertionError("customer_name is not unique.")

    with QUALITY.open() as f:
        quality_report = json.load(f)

    unknown_count = 0
    if "transaction_type" in curated.columns:
        unknown_count = (
            curated["transaction_type"]
            .astype(str)
            .str.upper()
            .eq("UNKNOWN")
            .sum()
        )

    realized_count = None
    if "is_realized_transaction" in curated.columns:
        realized_count = (
            curated["is_realized_transaction"]
            .fillna(False)
            .astype(bool)
            .sum()
        )

    print()
    print("PLUTO DATA PLATFORM - FINAL VALIDATION")
    print("======================================")
    print(f"Curated transactions : {len(curated):,}")
    print(f"Customer dimension   : {len(customers):,}")
    if realized_count is not None:
        print(f"Realized transactions: {realized_count:,}")
    print(f"UNKNOWN transactions : {unknown_count:,}")
    print(f"Quality report keys  : {len(quality_report):,}")
    print()
    print("All final validation checks PASSED.")

if __name__ == "__main__":
    main()
