import pandas as pd

from src.transform.customer_transactions import (
    classify_transaction,
    get_date_status,
    transform_customer_transactions,
)


def test_classifies_sale():
    row = pd.Series(
        {
            "category": "C.sales",
            "description": "red & white 18x18",
            "amount_due": 250000,
            "amount_received": None,
        }
    )

    assert (
        classify_transaction(row)
        == "SALE"
    )


def test_classifies_payment():
    row = pd.Series(
        {
            "category": "income cash",
            "description": "cash received",
            "amount_due": None,
            "amount_received": 100000,
        }
    )

    assert (
        classify_transaction(row)
        == "PAYMENT"
    )


def test_classifies_tax():
    row = pd.Series(
        {
            "category": "TAX",
            "description": "Tax With Held",
            "amount_due": None,
            "amount_received": 33802,
        }
    )

    assert (
        classify_transaction(row)
        == "TAX"
    )


def test_classifies_rejection():
    row = pd.Series(
        {
            "category": "rejection",
            "description": "Bags damaged and rejected",
            "amount_due": None,
            "amount_received": None,
        }
    )

    assert (
        classify_transaction(row)
        == "RETURN_REJECTION"
    )


def test_classifies_advance():
    row = pd.Series(
        {
            "category": "advance",
            "description": "advance",
            "amount_due": None,
            "amount_received": 50000,
        }
    )

    assert (
        classify_transaction(row)
        == "ADVANCE"
    )


def test_pre_company_date_flag():
    result = get_date_status(
        pd.Timestamp("1900-01-28"),
        pd.Timestamp("2026-10-03"),
    )

    assert result == "PRE_COMPANY_DATE"


def test_future_date_flag():
    result = get_date_status(
        pd.Timestamp("2026-10-29"),
        pd.Timestamp("2026-10-03"),
    )

    assert result == "FUTURE_DATED"


def test_valid_date():
    result = get_date_status(
        pd.Timestamp("2025-01-01"),
        pd.Timestamp("2026-10-03"),
    )

    assert result == "VALID"


def test_transform_does_not_mutate_input():
    original = pd.DataFrame(
        [
            {
                "transaction_date":
                    pd.Timestamp(
                        "2025-01-01"
                    ),
                "category": "sales",
                "description": "bags",
                "amount_due": 1000,
                "amount_received": None,
            }
        ]
    )

    copy = original.copy(
        deep=True
    )

    transform_customer_transactions(
        original,
        as_of_date="2026-10-03",
    )

    pd.testing.assert_frame_equal(
        original,
        copy,
    )
