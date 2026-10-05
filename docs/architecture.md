# Architecture

## Overview

Pluto Data Platform is designed to convert operational business records stored across multiple Excel workbooks into structured datasets suitable for analytics and reporting.

The architecture follows a layered approach.

```text
SOURCE
│
├── Customer ledgers
├── Supplier ledgers
├── Fabric stock
├── Production records
├── Printing records
├── Banking
└── Operational finance
        │
        ▼
INGESTION
│
├── Workbook discovery
├── Worksheet profiling
├── Dynamic header detection
├── Column standardisation
└── Source lineage capture
        │
        ▼
STAGING
│
├── Preserve source meaning
├── Standardise schemas
├── Convert data types
└── Retain source workbook/sheet/row
        │
        ▼
CURATED
│
├── Transaction classification
├── Classification reasoning
├── Date validation
├── Data-quality flags
└── Business-rule transformations
        │
        ▼
ANALYTICS
│
├── Customer dimension
├── Fact transactions
├── Supplier dimension
├── Product dimension
├── Fabric dimension
└── Date dimension
        │
        ▼
SERVING
│
├── PostgreSQL
└── Power BI
```

## Source Layer

The current source consists of four operational Excel workbooks containing 61 worksheets.

These cover customer transactions, supplier activity, fabric inventory, production, printing, banking and other operational information.

The files are intentionally treated as source systems rather than manually cleaned before ingestion.

## Ingestion Layer

Python and Pandas are used to inspect and extract data.

The ingestion layer handles:

- multiple workbooks
- multiple worksheets
- inconsistent header locations
- inconsistent column names
- Excel serial dates
- blank rows
- source lineage

Each ingested record retains information including its originating workbook, worksheet and source row.

## Staging Layer

The staging layer standardises technical structure while preserving source meaning.

For customer transactions this creates a single consolidated schema from multiple independent customer ledgers.

## Curated Layer

The curated layer applies business logic.

Current transformations include:

- transaction classification
- classification reasoning
- date-quality validation
- ledger-effect calculations
- quality flags

No suspicious source values are silently overwritten.

## Analytics Layer

Dimensional modelling is being introduced progressively.

The first dimension is `dim_customer`.

Planned models include:

```text
dim_customer
dim_supplier
dim_product
dim_fabric
dim_date

fact_customer_transactions
fact_sales
fact_purchases
fact_inventory_movements
fact_production
```

## Serving Layer

PostgreSQL will become the central analytical database.

Power BI will consume analytics-ready tables from PostgreSQL for reporting and dashboarding.

## Future Cloud Architecture

The longer-term architecture will introduce:

```text
Operational Data
      ↓
Amazon S3
      ↓
Python / AWS Lambda
      ↓
Validation & Transformation
      ↓
PostgreSQL / Analytics Layer
      ↓
Power BI

EventBridge → Scheduling
CloudWatch  → Monitoring
Terraform   → Infrastructure as Code
GitHub Actions → CI/CD
```