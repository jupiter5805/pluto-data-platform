import pandas as pd

from src.transform.customer_dimension import (
    generate_customer_id,
    build_customer_dimension,
)


def test_customer_id_is_deterministic():
    first = generate_customer_id(
        "ALFATAH"
    )

    second = generate_customer_id(
        "ALFATAH"
    )

    assert first == second


def test_customer_id_ignores_case_and_spaces():
    first = generate_customer_id(
        " ALFATAH "
    )

    second = generate_customer_id(
        "alfatah"
    )

    assert first == second


def test_builds_one_row_per_customer():
    df = pd.DataFrame(
        [
            {
                "customer_name": "ALFATAH",
                "transaction_date":
                    pd.Timestamp(
                        "2025-01-01"
                    ),
                "amount_due": 1000,
                "amount_received": None,
            },
            {
                "customer_name": "ALFATAH",
                "transaction_date":
                    pd.Timestamp(
                        "2025-02-01"
                    ),
                "amount_due": None,
                "amount_received": 500,
            },
            {
                "customer_name": "VICTORIA",
                "transaction_date":
                    pd.Timestamp(
                        "2025-03-01"
                    ),
                "amount_due": 2000,
                "amount_received": None,
            },
        ]
    )

    result = build_customer_dimension(
        df
    )

    assert len(result) == 2


def test_customer_transaction_count():
    df = pd.DataFrame(
        [
            {
                "customer_name": "ALFATAH",
                "transaction_date":
                    pd.Timestamp(
                        "2025-01-01"
                    ),
                "amount_due": 1000,
                "amount_received": None,
            },
            {
                "customer_name": "ALFATAH",
                "transaction_date":
                    pd.Timestamp(
                        "2025-02-01"
                    ),
                "amount_due": None,
                "amount_received": 500,
            },
        ]
    )

    result = build_customer_dimension(
        df
    )

    assert (
        result.iloc[0][
            "transaction_count"
        ]
        == 2
    )


def test_customer_current_balance():
    df = pd.DataFrame(
        [
            {
                "customer_name": "ALFATAH",
                "transaction_date":
                    pd.Timestamp(
                        "2025-01-01"
                    ),
                "amount_due": 1000,
                "amount_received": None,
            },
            {
                "customer_name": "ALFATAH",
                "transaction_date":
                    pd.Timestamp(
                        "2025-02-01"
                    ),
                "amount_due": None,
                "amount_received": 400,
            },
        ]
    )

    result = build_customer_dimension(
        df
    )

    assert (
        result.iloc[0][
            "current_balance"
        ]
        == 600
    )
