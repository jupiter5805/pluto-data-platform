import pandas as pd

from src.quality.warehouse_quality import build_report


def test_missing_dates_are_reported_but_not_treated_as_malformed():
    df = pd.DataFrame(
        [
            {
                "source_workbook": "book.xlsx",
                "source_sheet": "Sheet1",
                "source_row": 1,
                "customer_name": "Alpha",
                "transaction_date": "2026-01-01",
                "transaction_type": "SALE",
                "date_status": "VALID",
            },
            {
                "source_workbook": "book.xlsx",
                "source_sheet": "Sheet1",
                "source_row": 2,
                "customer_name": "Alpha",
                "transaction_date": None,
                "transaction_type": "PAYMENT",
                "date_status": "MISSING",
            },
        ]
    )

    report = build_report(df)

    assert report["missing_dates"] == 1
    assert report["invalid_date_rows"] == 0
    assert report["checks"]["malformed_dates_below_1_percent"] is True


def test_invalid_date_status_fails_quality_gate():
    rows = []
    for i in range(100):
        rows.append(
            {
                "source_workbook": "book.xlsx",
                "source_sheet": "Sheet1",
                "source_row": i,
                "customer_name": "Alpha",
                "transaction_date": None if i == 0 else "2026-01-01",
                "transaction_type": "SALE",
                "date_status": "INVALID" if i == 0 else "VALID",
            }
        )

    report = build_report(pd.DataFrame(rows))

    assert report["invalid_date_rows"] == 1
    assert report["checks"]["malformed_dates_below_1_percent"] is False
