import pandas as pd

from src.quality.data_quality_report import (
    build_quality_report,
)


def test_build_quality_report():
    df = pd.DataFrame(
        [
            {
                "quality_flags": "OK",
                "transaction_type": "SALE",
                "date_status": "VALID",
            },
            {
                "quality_flags": "MISSING_DATE",
                "transaction_type": "UNKNOWN",
                "date_status": "MISSING_DATE",
            },
            {
                "quality_flags": "FUTURE_DATED",
                "transaction_type": "PAYMENT",
                "date_status": "FUTURE_DATED",
            },
        ]
    )

    result = build_quality_report(
        df
    )

    assert result["total_rows"] == 3
    assert result["clean_rows"] == 1
    assert result["flagged_rows"] == 2
    assert result["unknown_transactions"] == 1
    assert result["missing_dates"] == 1
    assert result["future_dated_transactions"] == 1


def test_quality_percentages():
    df = pd.DataFrame(
        [
            {
                "quality_flags": "OK",
                "transaction_type": "SALE",
                "date_status": "VALID",
            },
            {
                "quality_flags": "OK",
                "transaction_type": "PAYMENT",
                "date_status": "VALID",
            },
            {
                "quality_flags": "MISSING_DATE",
                "transaction_type": "UNKNOWN",
                "date_status": "MISSING_DATE",
            },
            {
                "quality_flags": "FUTURE_DATED",
                "transaction_type": "PAYMENT",
                "date_status": "FUTURE_DATED",
            },
        ]
    )

    result = build_quality_report(
        df
    )

    assert result["clean_percentage"] == 50.0
    assert result["flagged_percentage"] == 50.0


def test_empty_dataframe():
    df = pd.DataFrame(
        columns=[
            "quality_flags",
            "transaction_type",
            "date_status",
        ]
    )

    result = build_quality_report(
        df
    )

    assert result["total_rows"] == 0
    assert result["clean_percentage"] == 0.0
    assert result["flagged_percentage"] == 0.0
