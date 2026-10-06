from __future__ import annotations

import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from sqlalchemy import create_engine, text

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://pluto:pluto_dev_password@localhost:5432/pluto",
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

app = FastAPI(
    title="Pluto Data Platform API",
    version="2.0.0",
    description="Read-only API for Pluto analytics warehouse data.",
)


def fetch_all(query: str, params: dict | None = None):
    with engine.connect() as conn:
        result = conn.execute(text(query), params or {})
        return [dict(row._mapping) for row in result]


@app.get("/")
def root():
    return {
        "service": "Pluto Data Platform API",
        "version": "2.0.0",
    }


@app.get("/health")
def health():
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return {"status": "ok"}


@app.get("/customers")
def customers(
    limit: int = Query(50, ge=1, le=500),
):
    return fetch_all(
        """
        SELECT *
        FROM analytics.dim_customer
        ORDER BY total_amount_due DESC NULLS LAST
        LIMIT :limit
        """,
        {"limit": limit},
    )


@app.get("/customers/{customer_id}")
def customer(customer_id: str):
    rows = fetch_all(
        """
        SELECT *
        FROM analytics.dim_customer
        WHERE customer_id = :customer_id
        """,
        {"customer_id": customer_id},
    )

    if not rows:
        raise HTTPException(status_code=404, detail="Customer not found")

    return rows[0]


@app.get("/transactions")
def transactions(
    limit: int = Query(100, ge=1, le=1000),
):
    return fetch_all(
        """
        SELECT *
        FROM analytics.fact_transactions
        ORDER BY transaction_date DESC NULLS LAST
        LIMIT :limit
        """,
        {"limit": limit},
    )


@app.get("/metrics/summary")
def summary():
    rows = fetch_all(
        """
        SELECT
            COUNT(*) AS transaction_count,
            COUNT(DISTINCT customer_id) AS customer_count,
            COALESCE(SUM(amount_due), 0) AS total_amount_due,
            COALESCE(SUM(amount_received), 0) AS total_amount_received,
            COALESCE(SUM(amount_due - amount_received), 0) AS outstanding_balance
        FROM analytics.fact_transactions
        """
    )
    return rows[0]
