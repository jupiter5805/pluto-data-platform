with base as (
    select *
    from {{ ref('stg_transactions') }}
    where customer_name is not null
),

aggregated as (
    select
        md5(lower(trim(customer_name))) as customer_id,
        customer_name,
        min(transaction_date) as first_transaction_date,
        max(transaction_date) as last_transaction_date,
        count(*) as transaction_count,
        sum(amount_due) as total_amount_due,
        sum(amount_received) as total_amount_received,
        sum(amount_due) - sum(amount_received) as current_balance
    from base
    group by customer_name
)

select *
from aggregated
