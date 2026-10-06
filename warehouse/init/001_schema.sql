CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS analytics;

CREATE TABLE IF NOT EXISTS raw.customer_transactions (
    source_key TEXT PRIMARY KEY,
    record_hash TEXT NOT NULL,
    transaction_date DATE,
    customer_name TEXT,
    reference_number TEXT,
    description TEXT,
    category TEXT,
    quantity NUMERIC,
    weight_kg NUMERIC,
    tax NUMERIC,
    rate NUMERIC,
    amount_due NUMERIC,
    amount_received NUMERIC,
    balance NUMERIC,
    source_workbook TEXT,
    source_sheet TEXT,
    source_row INTEGER,
    ingested_at TIMESTAMPTZ,
    transaction_type TEXT,
    classification_reason TEXT,
    date_status TEXT,
    quality_flags TEXT,
    is_realized_transaction BOOLEAN,
    ledger_effect TEXT,
    loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS raw.pipeline_runs (
    run_id BIGSERIAL PRIMARY KEY,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    finished_at TIMESTAMPTZ,
    source_rows INTEGER,
    inserted_or_updated_rows INTEGER,
    unchanged_rows INTEGER,
    status TEXT NOT NULL,
    message TEXT
);

CREATE INDEX IF NOT EXISTS idx_raw_customer_name
    ON raw.customer_transactions(customer_name);

CREATE INDEX IF NOT EXISTS idx_raw_transaction_date
    ON raw.customer_transactions(transaction_date);

CREATE INDEX IF NOT EXISTS idx_raw_transaction_type
    ON raw.customer_transactions(transaction_type);
