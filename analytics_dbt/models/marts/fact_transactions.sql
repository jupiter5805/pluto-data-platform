with tx as (
    select *
    from {{ ref('stg_transactions') }}
),

customers as (
    select
        customer_id,
        customer_name
    from {{ ref('dim_customer') }}
)

select
    tx.transaction_id,
    customers.customer_id,
    case
        when tx.transaction_date is not null
         and tx.date_status = 'VALID'
        then to_char(tx.transaction_date, 'YYYYMMDD')::integer
    end as date_id,
    tx.transaction_date,
    tx.reference_number,
    tx.description,
    tx.category,
    tx.quantity,
    tx.weight_kg,
    tx.tax,
    tx.rate,
    tx.amount_due,
    tx.amount_received,
    tx.amount_due - tx.amount_received as net_ledger_movement,
    tx.transaction_type,
    tx.is_realized_transaction,
    tx.ledger_effect,
    tx.source_workbook,
    tx.source_sheet,
    tx.source_row
from tx
left join customers
    on tx.customer_name = customers.customer_name
