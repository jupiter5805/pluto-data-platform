from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

import pandas as pd
import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import execute_values

INPUT_PATH = Path("data/processed/cur_customer_transactions.parquet")

COLUMNS = [
    "source_key",
    "record_hash",
    "transaction_date",
    "customer_name",
    "reference_number",
    "description",
    "category",
    "quantity",
    "weight_kg",
    "tax",
    "rate",
    "amount_due",
    "amount_received",
    "balance",
    "source_workbook",
    "source_sheet",
    "source_row",
    "ingested_at",
    "transaction_type",
    "classification_reason",
    "date_status",
    "quality_flags",
    "is_realized_transaction",
    "ledger_effect",
]


def _normalise(value: Any) -> Any:
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass

    if isinstance(value, pd.Timestamp):
        return value.to_pydatetime()

    if isinstance(value, (dict, list, tuple, set)):
        return json.dumps(value, default=str, sort_keys=True)

    if hasattr(value, "item"):
        try:
            return value.item()
        except Exception:
            pass

    return value


def make_source_key(row: pd.Series) -> str:
    parts = [
        str(_normalise(row.get("source_workbook")) or ""),
        str(_normalise(row.get("source_sheet")) or ""),
        str(_normalise(row.get("source_row")) or ""),
    ]
    basis = "|".join(parts)

    if basis == "||":
        basis = "|".join(
            str(_normalise(row.get(col)) or "")
            for col in [
                "transaction_date",
                "customer_name",
                "reference_number",
                "description",
                "amount_due",
                "amount_received",
            ]
        )

    return hashlib.sha256(basis.encode("utf-8")).hexdigest()


def make_record_hash(row: pd.Series) -> str:
    payload = {
        col: str(_normalise(row.get(col)) or "")
        for col in row.index
        if col not in {"ingested_at"}
    }
    body = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def prepare_records(df: pd.DataFrame) -> list[tuple[Any, ...]]:
    work = df.copy()

    for col in COLUMNS:
        if col not in work.columns and col not in {"source_key", "record_hash"}:
            work[col] = None

    work["source_key"] = work.apply(make_source_key, axis=1)
    work["record_hash"] = work.apply(make_record_hash, axis=1)

    for col in ["transaction_date", "ingested_at"]:
        work[col] = pd.to_datetime(work[col], errors="coerce")

    for col in [
        "quantity",
        "weight_kg",
        "tax",
        "rate",
        "amount_due",
        "amount_received",
        "balance",
        "source_row",
    ]:
        work[col] = pd.to_numeric(work[col], errors="coerce")

    records = []
    for _, row in work[COLUMNS].iterrows():
        records.append(tuple(_normalise(row[col]) for col in COLUMNS))
    return records


def get_connection():
    load_dotenv()
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        dbname=os.getenv("POSTGRES_DB", "pluto"),
        user=os.getenv("POSTGRES_USER", "pluto"),
        password=os.getenv("POSTGRES_PASSWORD", "pluto_dev_password"),
    )


def ensure_schema(conn) -> None:
    sql = Path("warehouse/init/001_schema.sql").read_text()
    with conn.cursor() as cur:
        cur.execute(sql)
    conn.commit()


def load_incrementally() -> None:
    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Missing curated input: {INPUT_PATH}. Run ./run_pipeline.sh first."
        )

    df = pd.read_parquet(INPUT_PATH)
    records = prepare_records(df)

    conn = get_connection()
    try:
        ensure_schema(conn)

        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO raw.pipeline_runs
                    (source_rows, inserted_or_updated_rows, unchanged_rows, status)
                VALUES (%s, 0, 0, 'RUNNING')
                RETURNING run_id
                """,
                (len(records),),
            )
            run_id = cur.fetchone()[0]
        conn.commit()

        sql = f"""
            INSERT INTO raw.customer_transactions (
                {", ".join(COLUMNS)}
            ) VALUES %s
            ON CONFLICT (source_key) DO UPDATE SET
                record_hash = EXCLUDED.record_hash,
                transaction_date = EXCLUDED.transaction_date,
                customer_name = EXCLUDED.customer_name,
                reference_number = EXCLUDED.reference_number,
                description = EXCLUDED.description,
                category = EXCLUDED.category,
                quantity = EXCLUDED.quantity,
                weight_kg = EXCLUDED.weight_kg,
                tax = EXCLUDED.tax,
                rate = EXCLUDED.rate,
                amount_due = EXCLUDED.amount_due,
                amount_received = EXCLUDED.amount_received,
                balance = EXCLUDED.balance,
                source_workbook = EXCLUDED.source_workbook,
                source_sheet = EXCLUDED.source_sheet,
                source_row = EXCLUDED.source_row,
                ingested_at = EXCLUDED.ingested_at,
                transaction_type = EXCLUDED.transaction_type,
                classification_reason = EXCLUDED.classification_reason,
                date_status = EXCLUDED.date_status,
                quality_flags = EXCLUDED.quality_flags,
                is_realized_transaction = EXCLUDED.is_realized_transaction,
                ledger_effect = EXCLUDED.ledger_effect,
                loaded_at = NOW()
            WHERE raw.customer_transactions.record_hash
                IS DISTINCT FROM EXCLUDED.record_hash
        """

        with conn.cursor() as cur:
            execute_values(
                cur,
                sql,
                records,
                page_size=500,
            )
            affected = cur.rowcount

        unchanged = max(len(records) - affected, 0)

        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE raw.pipeline_runs
                SET finished_at = NOW(),
                    inserted_or_updated_rows = %s,
                    unchanged_rows = %s,
                    status = 'SUCCESS',
                    message = 'Incremental upsert completed'
                WHERE run_id = %s
                """,
                (affected, unchanged, run_id),
            )
        conn.commit()

        print()
        print("POSTGRES INCREMENTAL LOAD")
        print("-------------------------")
        print(f"Source rows          : {len(records):,}")
        print(f"Inserted / updated   : {affected:,}")
        print(f"Unchanged            : {unchanged:,}")
        print("Status               : SUCCESS")

    except Exception as exc:
        conn.rollback()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE raw.pipeline_runs
                    SET finished_at = NOW(),
                        status = 'FAILED',
                        message = %s
                    WHERE run_id = %s
                    """,
                    (str(exc), run_id),
                )
            conn.commit()
        except Exception:
            conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    load_incrementally()
