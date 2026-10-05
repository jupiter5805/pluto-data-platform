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

    result = classify_transaction(row)

    assert result == (
        "SALE",
        "explicit_sales_category",
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

    result = classify_transaction(row)

    assert result == (
        "PAYMENT",
        "payment_keyword_and_received_amount",
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

    result = classify_transaction(row)

    assert result == (
        "TAX",
        "tax_keyword",
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

    result = classify_transaction(row)

    assert result == (
        "RETURN_REJECTION",
        "return_or_rejection_keyword",
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

    result = classify_transaction(row)

    assert result == (
        "ADVANCE",
        "advance_keyword",
    )


def test_due_amount_fallback():
    row = pd.Series(
        {
            "category": None,
            "description": "custom order",
            "amount_due": 50000,
            "amount_received": None,
        }
    )

    result = classify_transaction(row)

    assert result == (
        "SALE",
        "due_amount_fallback",
    )


def test_received_amount_fallback():
    row = pd.Series(
        {
            "category": None,
            "description": "transfer",
            "amount_due": None,
            "amount_received": 50000,
        }
    )

    result = classify_transaction(row)

    assert result == (
        "PAYMENT",
        "received_amount_fallback",
    )


def test_unknown_transaction():
    row = pd.Series(
        {
            "category": None,
            "description": None,
            "amount_due": None,
            "amount_received": None,
        }
    )

    result = classify_transaction(row)

    assert result == (
        "UNKNOWN",
        "unclassified",
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


def test_transform_adds_classification_reason():
    df = pd.DataFrame(
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

    result = (
        transform_customer_transactions(
            df,
            as_of_date="2026-10-03",
        )
    )

    assert (
        result.iloc[0][
            "transaction_type"
        ]
        == "SALE"
    )

    assert (
        result.iloc[0][
            "classification_reason"
        ]
        == "explicit_sales_category"
    )


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
