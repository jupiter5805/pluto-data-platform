# Pluto Data Platform

An end-to-end Data Engineering platform built for Pluto Packaging, a manufacturing business producing woven and non-woven packaging products.

The project consolidates fragmented operational data covering sales, customers, suppliers, inventory and production into a structured analytics platform.

## Business Problem

Operational data is currently distributed across multiple Excel workbooks and individual customer, supplier, inventory and production worksheets.

The objective of this project is to build a reliable automated data pipeline that standardises this information and makes it available for analytics and business intelligence.

## Architecture

Excel Business Data
→ Python Ingestion
→ Raw/Bronze Layer
→ Data Validation & Transformation
→ PostgreSQL
→ Analytics Models
→ Power BI

## Data Domains

- Sales and customer receivables
- Supplier purchases and payables
- Fabric inventory movements
- Production and printing activity
- Financial and operational reporting

## Technology

Python · SQL · PostgreSQL · Pandas · Pytest · Power BI

The platform will subsequently be extended using AWS, Terraform, automated orchestration, monitoring and CI/CD.

## Data Privacy

Real Pluto Packaging commercial datasets are excluded from version control.

Only anonymised sample datasets and pipeline code are stored in this repository.