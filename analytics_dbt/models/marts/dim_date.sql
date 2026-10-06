with bounds as (
    select
        min(transaction_date) as min_date,
        max(transaction_date) as max_date
    from {{ ref('stg_transactions') }}
    where transaction_date is not null
      and date_status = 'VALID'
),

dates as (
    select
        generate_series(
            min_date,
            max_date,
            interval '1 day'
        )::date as date_day
    from bounds
)

select
    to_char(date_day, 'YYYYMMDD')::integer as date_id,
    date_day,
    extract(year from date_day)::integer as year,
    extract(quarter from date_day)::integer as quarter,
    extract(month from date_day)::integer as month,
    to_char(date_day, 'Mon') as month_name,
    extract(week from date_day)::integer as week_of_year,
    extract(day from date_day)::integer as day_of_month,
    trim(to_char(date_day, 'Day')) as day_name
from dates
