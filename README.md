# Pluto Data Platform

An end-to-end Data Engineering project built around real operational data from **Pluto Packaging**, a manufacturing business producing woven and non-woven packaging products.

The project converts fragmented Excel-based business records into structured, validated and analytics-ready datasets.

Real commercial data is deliberately excluded from this public repository.

---

## Why I Built This

Pluto Packaging has accumulated operational data across multiple Excel workbooks covering:

- customers and sales
- payments and receivables
- suppliers
- purchases and payables
- fabric inventory
- production
- printing
- cutting
- wages
- banking and cash transactions

The spreadsheets were created for day-to-day business use rather than analytics, so structures, column names, dates and transaction categories are not always consistent.

The aim of this project is to turn that operational data into a reliable Data Engineering platform.

---

## Current Pipeline

```text
Operational Excel Workbooks
            ↓
    Workbook Profiling
            ↓
     Python Ingestion
            ↓
       Staging Layer
            ↓
Validation & Standardisation
            ↓
 Transaction Classification
            ↓
     Data Quality Checks
            ↓
       Curated Layer
            ↓
  Dimensional Data Models
            ↓
        PostgreSQL
            ↓
         Power BI
```

PostgreSQL and Power BI are the next major stages of development.

---

## Current Progress

The pipeline currently processes:

- **4 operational Excel workbooks**
- **61 worksheets**
- **27 customer ledgers containing transactions**
- **897 standardised customer transactions**

Implemented so far:

- automated workbook and worksheet profiling
- dynamic Excel ingestion
- inconsistent column-name handling
- Excel date conversion
- staging datasets
- CSV and Parquet output
- transaction classification
- explainable classification rules
- data-quality flags
- unknown-transaction investigation
- automated data-quality reporting
- deterministic customer IDs
- customer dimension generation
- automated pytest coverage

---

## Transaction Classification

Customer ledger entries are classified into business transaction types such as:

```text
SALE
PAYMENT
RETURN_REJECTION
TAX
ADVANCE
ADJUSTMENT
UNKNOWN
```

The pipeline also records the reason used for each classification so that transformation logic remains auditable.

Examples include:

```text
explicit_sales_category
payment_keyword_and_received_amount
tax_keyword
return_or_rejection_keyword
advance_keyword
due_amount_fallback
received_amount_fallback
unclassified
```

---

## Data Quality

The pipeline preserves questionable source data rather than silently correcting it.

Current checks include:

- missing transaction dates
- dates before the company's operating period
- future-dated transactions
- negative receivable values
- rows containing both due and received values
- unclassified transactions

Quality issues are surfaced through flags and reports for investigation.

---

## Customer Dimension

The project also generates an analytics-ready customer dimension containing:

```text
customer_id
customer_name
first_transaction_date
last_transaction_date
transaction_count
total_amount_due
total_amount_received
current_balance
```

Customer IDs are generated deterministically so the same customer receives the same identifier on every pipeline run.

---

## Technology

**Data Engineering**

Python · Pandas · SQL · PostgreSQL · Parquet · Excel

**Testing**

pytest

**Planned Platform**

PostgreSQL · Power BI · AWS · Terraform · CI/CD

---

## Repository Structure

```text
pluto-data-platform/
│
├── data/
│   ├── raw/
│   ├── bronze/
│   ├── processed/
│   └── sample/
│
├── src/
│   ├── ingestion/
│   ├── transform/
│   ├── quality/
│   └── load/
│
├── tests/
├── sql/
├── dashboard/
├── docs/
│   ├── architecture.md
│   └── data_dictionary.md
│
├── config/
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Data Privacy

The source workbooks contain commercially sensitive business information.

The following are therefore excluded from version control:

```text
data/raw/
data/bronze/
data/processed/
```

The public repository contains the engineering logic and documentation only.

An anonymised sample dataset can be added separately for demonstration and testing.

---

## Next Steps

The next development stages are:

1. Load staging and curated datasets into PostgreSQL
2. Build dimensional fact and dimension tables
3. Ingest supplier and inventory data
4. Model production and manufacturing activity
5. Build Power BI dashboards
6. Automate pipeline execution
7. Add cloud infrastructure and monitoring