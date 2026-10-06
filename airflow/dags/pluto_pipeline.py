from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator

REPO = "/opt/airflow/pluto"

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
        bash_command=f"cd {REPO} && ./run_pipeline.sh",
    )

    load_postgres = BashOperator(
        task_id="incremental_postgres_load",
        bash_command=(
            f"cd {REPO} && "
            "POSTGRES_HOST=postgres "
            "python -m src.warehouse.load_postgres"
        ),
    )

    dbt_build = BashOperator(
        task_id="dbt_build",
        bash_command=(
            f"cd {REPO} && "
            "POSTGRES_HOST=postgres "
            "DBT_PROFILES_DIR=analytics_dbt "
            "dbt build --project-dir analytics_dbt"
        ),
    )

    warehouse_quality = BashOperator(
        task_id="warehouse_quality",
        bash_command=(
            f"cd {REPO} && "
            "python -m src.quality.warehouse_quality"
        ),
    )

    build_curated >> load_postgres >> dbt_build >> warehouse_quality
