# Power BI layer

Connect Power BI Desktop to PostgreSQL:

- Server: `localhost`
- Database: `pluto`
- Username: `pluto`
- Password: value from `.env`

Recommended views:

- `analytics.vw_executive_summary`
- `analytics.vw_monthly_performance`
- `analytics.vw_customer_balances`
- `analytics.vw_transaction_mix`

Suggested dashboard pages:

1. Executive overview
2. Customer balances / receivables
3. Monthly sales and receipts
4. Transaction classification
5. Customer drill-through

The SQL views are created automatically by `run_platform_v2.sh`.
