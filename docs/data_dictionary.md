# Data Dictionary

## Customer Transaction Staging Layer

### `transaction_date`
Date associated with the customer-ledger transaction.

### `customer_name`
Customer name derived from the source worksheet.

### `reference_number`
Invoice, serial or transaction reference where available.

### `description`
Original transaction or product description from the source ledger.

### `category`
Original business category recorded in Excel.

### `quantity`
Recorded unit quantity where available.

### `weight_kg`
Recorded transaction weight in kilograms where applicable.

### `tax`
Tax amount where explicitly represented by the source.

### `rate`
Recorded unit rate or price.

### `amount_due`
Amount charged to the customer.

### `amount_received`
Payment or credit received from the customer.

### `balance`
Running balance supplied by the original customer ledger.

### `source_workbook`
Name of the Excel workbook from which the record was ingested.

### `source_sheet`
Name of the source worksheet.

### `source_row`
Original Excel row number used for lineage and troubleshooting.

### `ingested_at`
Timestamp recording when the pipeline ingested the record.

---

# Curated Customer Transactions

The curated layer contains all staging columns plus additional engineered fields.

### `transaction_type`
Standardised business classification.

Current values include:

```text
SALE
PAYMENT
RETURN_REJECTION
TAX
ADVANCE
ADJUSTMENT
UNKNOWN
```

### `classification_reason`
Records the rule responsible for assigning `transaction_type`.

Examples:

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

### `date_status`
Quality classification for the transaction date.

Possible values:

```text
VALID
MISSING_DATE
FUTURE_DATED
PRE_COMPANY_DATE
```

### `quality_flags`
One or more quality warnings associated with the record.

Examples:

```text
OK
MISSING_DATE
FUTURE_DATED
PRE_COMPANY_DATE
NEGATIVE_DUE
NEGATIVE_RECEIVED
BOTH_DUE_AND_RECEIVED
```

### `is_realized_transaction`
Boolean indicating whether the transaction has a currently valid realised date.

### `ledger_effect`
Calculated as:

```text
amount_due - amount_received
```

---

# Customer Dimension

## `customer_id`
Deterministic customer identifier generated from the normalised customer name.

## `customer_name`
Canonical customer name.

## `first_transaction_date`
Earliest transaction associated with the customer.

## `last_transaction_date`
Latest transaction associated with the customer.

## `transaction_count`
Number of transaction records associated with the customer.

## `total_amount_due`
Total ledger amount recorded as due.

## `total_amount_received`
Total ledger amount recorded as received.

## `current_balance`
Calculated difference between total amount due and total amount received.

```text
current_balance =
total_amount_due - total_amount_received
```

The customer dimension will later be expanded with additional commercial and segmentation attributes.