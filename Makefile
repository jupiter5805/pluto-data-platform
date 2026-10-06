.PHONY: test v1 up down load dbt quality api v2 airflow-up airflow-down terraform-validate

test:
	python -m pytest -q

v1:
	./run_pipeline.sh

up:
	docker compose up -d postgres

down:
	docker compose down

load:
	python -m src.warehouse.load_postgres

dbt:
	DBT_PROFILES_DIR=analytics_dbt dbt build --project-dir analytics_dbt

quality:
	python -m src.quality.warehouse_quality

api:
	docker compose up -d --build api

v2:
	./run_platform_v2.sh

airflow-up:
	docker compose -f docker-compose.yml -f docker-compose.airflow.yml up -d

airflow-down:
	docker compose -f docker-compose.yml -f docker-compose.airflow.yml down

terraform-validate:
	cd infra/terraform && terraform init -backend=false && terraform validate
