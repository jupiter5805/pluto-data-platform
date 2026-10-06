CREATE OR REPLACE VIEW analytics.vw_executive_summary AS
SELECT
    COUNT(*) AS transaction_count,
    COUNT(DISTINCT customer_id) AS customer_count,
    COALESCE(SUM(amount_due), 0) AS total_amount_due,
    COALESCE(SUM(amount_received), 0) AS total_amount_received,
    COALESCE(SUM(amount_due - amount_received), 0) AS outstanding_balance
FROM analytics.fact_transactions;

CREATE OR REPLACE VIEW analytics.vw_monthly_performance AS
SELECT
    date_trunc('month', transaction_date)::date AS month,
    COUNT(*) AS transaction_count,
    SUM(amount_due) AS amount_due,
    SUM(amount_received) AS amount_received,
    SUM(amount_due - amount_received) AS net_movement
FROM analytics.fact_transactions
WHERE transaction_date IS NOT NULL
GROUP BY 1
ORDER BY 1;

CREATE OR REPLACE VIEW analytics.vw_customer_balances AS
SELECT
    customer_id,
    customer_name,
    transaction_count,
    total_amount_due,
    total_amount_received,
    current_balance,
    balance_status
FROM analytics.mart_customer_summary;

CREATE OR REPLACE VIEW analytics.vw_transaction_mix AS
SELECT
    transaction_type,
    COUNT(*) AS transaction_count,
    SUM(amount_due) AS amount_due,
    SUM(amount_received) AS amount_received
FROM analytics.fact_transactions
GROUP BY transaction_type
ORDER BY transaction_count DESC;
