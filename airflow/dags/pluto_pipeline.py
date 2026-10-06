from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator


REPO = "/opt/pluto"
PYTHON = "/home/airflow/pluto-venv/bin/python"
PYTEST = "/home/airflow/pluto-venv/bin/pytest"
DBT = "/home/airflow/dbt-venv/bin/dbt"


with DAG(
    dag_id="pluto_data_platform",
    description="End-to-end Pluto data engineering pipeline",
    start_date=datetime(2026, 1, 1),
    schedule="0 2 * * *",
    catchup=False,
    tags=["pluto", "data-engineering"],
) as dag:

    build_curated = BashOperator(
        task_id="build_curated_data",
        bash_command=f"""
        set -e
        cd {REPO}

        {PYTHON} -m src.ingestion.profile_workbooks
        {PYTHON} -m src.ingestion.customer_transactions
        {PYTHON} -m src.transform.customer_transactions
        {PYTHON} -m src.quality.investigate_unknown_transactions
        {PYTHON} -m src.quality.data_quality_report
        {PYTHON} -m src.transform.customer_dimension

        PYTHONPATH={REPO} {PYTEST} -q
        {PYTHON} -m src.quality.final_validation
        """,
    )

    load_postgres = BashOperator(
        task_id="incremental_postgres_load",
        bash_command=f"""
        set -e
        cd {REPO}
        POSTGRES_HOST=postgres \
        POSTGRES_PORT=5432 \
        POSTGRES_DB="${{POSTGRES_DB:-pluto}}" \
        POSTGRES_USER="${{POSTGRES_USER:-pluto}}" \
        POSTGRES_PASSWORD="${{POSTGRES_PASSWORD:-pluto_dev_password}}" \
        PYTHONPATH={REPO} \
        {PYTHON} -m src.warehouse.load_postgres
        """,
    )

    dbt_build = BashOperator(
        task_id="dbt_build",
        bash_command=f"""
        set -e
        cd {REPO}
        POSTGRES_HOST=postgres \
        POSTGRES_PORT=5432 \
        POSTGRES_DB="${{POSTGRES_DB:-pluto}}" \
        POSTGRES_USER="${{POSTGRES_USER:-pluto}}" \
        POSTGRES_PASSWORD="${{POSTGRES_PASSWORD:-pluto_dev_password}}" \
        DBT_PROFILES_DIR={REPO}/analytics_dbt \
        {DBT} build \
          --project-dir {REPO}/analytics_dbt \
          --profiles-dir {REPO}/analytics_dbt
        """,
    )

    warehouse_quality = BashOperator(
        task_id="warehouse_quality",
        bash_command=f"""
        set -e
        cd {REPO}
        PYTHONPATH={REPO} \
        {PYTHON} -m src.quality.warehouse_quality
        """,
    )

    build_curated >> load_postgres >> dbt_build >> warehouse_quality
