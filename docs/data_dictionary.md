# Pluto Data Platform — Data Dictionary

## Source layer

The platform ingests Pluto Packaging operational Excel workbooks from
`data/raw/` while retaining source workbook, worksheet and row lineage.

## Staging layer — `stg_customer_transactions`

Standardised transaction-level records produced from the source workbooks.

Typical fields include transaction date, customer name, reference,
description, category, quantity, weight, tax, rate, amounts, source lineage
and ingestion metadata.

## Curated layer — `cur_customer_transactions`

Analytics-ready transaction records created after cleaning, standardisation,
classification and data-quality processing.

Additional analytical fields include transaction classification,
classification reason, date status, quality flags, realised-transaction
indicator and ledger effect where available.

## Customer dimension — `dim_customer`

One analytical row per customer, with a deterministic customer identifier
and customer-level transaction metrics.

## Data lineage

Excel operational workbooks
        ↓
Workbook profiling
        ↓
Customer transaction ingestion
        ↓
Staging dataset
        ↓
Cleaning and standardisation
        ↓
Transaction classification
        ↓
Data-quality checks
        ↓
Curated transaction dataset
        ↓
Customer dimension
        ↓
Analytics-ready outputs
