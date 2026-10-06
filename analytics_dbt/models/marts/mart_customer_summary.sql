select
    c.customer_id,
    c.customer_name,
    c.first_transaction_date,
    c.last_transaction_date,
    c.transaction_count,
    c.total_amount_due,
    c.total_amount_received,
    c.current_balance,
    case
        when c.current_balance > 0 then 'OUTSTANDING'
        when c.current_balance < 0 then 'CREDIT'
        else 'SETTLED'
    end as balance_status
from {{ ref('dim_customer') }} c
