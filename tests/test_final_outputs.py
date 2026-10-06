from pathlib import Path
import pandas as pd

PROCESSED = Path("data/processed")

def test_required_outputs_exist():
    required = [
        PROCESSED / "stg_customer_transactions.parquet",
        PROCESSED / "cur_customer_transactions.parquet",
        PROCESSED / "data_quality_report.json",
        PROCESSED / "unknown_transactions_report.csv",
        PROCESSED / "dim_customer.parquet",
    ]
    missing = [str(p) for p in required if not p.exists()]
    assert not missing, f"Missing required outputs: {missing}"

def test_curated_transactions_are_not_empty():
    df = pd.read_parquet(
        PROCESSED / "cur_customer_transactions.parquet"
    )
    assert not df.empty

def test_customer_dimension_is_valid():
    df = pd.read_parquet(
        PROCESSED / "dim_customer.parquet"
    )
    assert not df.empty
    assert "customer_id" in df.columns
    assert "customer_name" in df.columns
    assert df["customer_id"].is_unique
    assert df["customer_name"].is_unique
