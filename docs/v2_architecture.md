# Pluto Data Platform V2

## Architecture

```text
Pluto operational Excel workbooks
            |
            v
Python ingestion / profiling
            |
            v
Staging + curated Parquet/CSV
            |
            v
Incremental PostgreSQL loader
       (source key + record hash)
            |
            v
        raw schema
            |
            v
           dbt
     staging -> marts
            |
            +-------------------+
            |                   |
            v                   v
     Star schema           Power BI views
 dim_customer                  |
 dim_date                      v
 fact_transactions       Business dashboard
            |
            +-------------------+
            |
            v
         FastAPI
            |
            v
      downstream apps

Orchestration: Apache Airflow
Quality: pytest + warehouse quality gates + dbt tests
CI/CD: GitHub Actions
Local runtime: Docker Compose
Cloud baseline: AWS S3 + RDS + Secrets Manager + CloudWatch via Terraform
```

## V2 capabilities

- PostgreSQL warehouse
- incremental/idempotent loading
- star-schema modelling
- dbt transformations and tests
- BI-ready SQL views
- FastAPI data-serving layer
- Apache Airflow DAG
- Docker local environment
- automated data-quality gates
- GitHub Actions CI
- AWS Terraform infrastructure baseline

## Local quick start

```bash
./run_platform_v2.sh
```

## Useful URLs

- API Swagger: http://localhost:8000/docs
- API health: http://localhost:8000/health
- Airflow: http://localhost:8080
