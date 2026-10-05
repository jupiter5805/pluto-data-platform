import pandas as pd

from src.quality.investigate_unknown_transactions import (
    investigate_unknown_transactions,
)


def test_returns_only_unknown_transactions():
    df = pd.DataFrame(
        [
            {
                "transaction_type": "SALE",
                "category": "sales",
                "description": "bags",
            },
            {
                "transaction_type": "UNKNOWN",
                "category": None,
                "description": "misc entry",
            },
        ]
    )

    result = (
        investigate_unknown_transactions(
            df
        )
    )

    assert len(result) == 1

    assert (
        result.iloc[0][
            "transaction_type"
        ]
        == "UNKNOWN"
    )


def test_normalises_unknown_category():
    df = pd.DataFrame(
        [
            {
                "transaction_type": "UNKNOWN",
                "category": " Misc ",
                "description": "Entry",
            }
        ]
    )

    result = (
        investigate_unknown_transactions(
            df
        )
    )

    assert (
        result.iloc[0][
            "normalised_category"
        ]
        == "misc"
    )


def test_handles_missing_text():
    df = pd.DataFrame(
        [
            {
                "transaction_type": "UNKNOWN",
                "category": None,
                "description": None,
            }
        ]
    )

    result = (
        investigate_unknown_transactions(
            df
        )
    )

    assert (
        result.iloc[0][
            "normalised_category"
        ]
        == "NULL"
    )

    assert (
        result.iloc[0][
            "normalised_description"
        ]
        == "NULL"
    )
