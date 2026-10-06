import pandas as pd

from src.quality.warehouse_quality import build_report
from src.warehouse.load_postgres import make_source_key


def test_source_key_is_deterministic():
    row = pd.Series(
        {
            "source_workbook": "book.xlsx",
            "source_sheet": "Sheet1",
            "source_row": 12,
        }
    )
    assert make_source_key(row) == make_source_key(row)


def test_different_source_rows_have_different_keys():
    first = pd.Series(
        {
            "source_workbook": "book.xlsx",
            "source_sheet": "Sheet1",
            "source_row": 12,
        }
    )
    second = pd.Series(
        {
            "source_workbook": "book.xlsx",
            "source_sheet": "Sheet1",
            "source_row": 13,
        }
    )
    assert make_source_key(first) != make_source_key(second)


def test_quality_report_passes_clean_sample():
    df = pd.DataFrame(
        [
            {
                "source_workbook": "book.xlsx",
                "source_sheet": "Sheet1",
                "source_row": 1,
                "customer_name": "Alpha",
                "transaction_date": "2026-01-01",
                "transaction_type": "SALE",
            },
            {
                "source_workbook": "book.xlsx",
                "source_sheet": "Sheet1",
                "source_row": 2,
                "customer_name": "Beta",
                "transaction_date": "2026-01-02",
                "transaction_type": "PAYMENT",
            },
        ]
    )
    report = build_report(df)
    assert report["passed"] is True
