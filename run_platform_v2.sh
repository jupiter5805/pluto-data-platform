#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if [[ -z "${VIRTUAL_ENV:-}" && -f ".venv/bin/activate" ]]; then
  source .venv/bin/activate
fi

if [[ -f .env ]]; then
  set -a
  source .env
  set +a
fi

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker Desktop is required."
  exit 1
fi

if ! docker info >/dev/null 2>&1; then
  echo "Docker Desktop is installed but not running."
  exit 1
fi

echo ""
echo "[1/8] Building V1 curated datasets..."
./run_pipeline.sh

echo ""
echo "[2/8] Starting PostgreSQL..."
docker compose up -d postgres

echo "Waiting for PostgreSQL..."
for i in {1..40}; do
  if docker exec pluto-postgres \
      pg_isready \
      -U "${POSTGRES_USER:-pluto}" \
      -d "${POSTGRES_DB:-pluto}" >/dev/null 2>&1; then
    break
  fi
  sleep 2
done

docker exec pluto-postgres \
  pg_isready \
  -U "${POSTGRES_USER:-pluto}" \
  -d "${POSTGRES_DB:-pluto}"

echo ""
echo "[3/8] Incremental warehouse load..."
python -m src.warehouse.load_postgres

echo ""
echo "[4/8] dbt star schema and tests..."
export DBT_PROFILES_DIR="$(pwd)/analytics_dbt"
dbt build --project-dir analytics_dbt

echo ""
echo "[5/8] Creating BI views..."
docker exec -i pluto-postgres \
  psql \
  -v ON_ERROR_STOP=1 \
  -U "${POSTGRES_USER:-pluto}" \
  -d "${POSTGRES_DB:-pluto}" \
  < bi/dashboard_queries.sql

echo ""
echo "[6/8] Warehouse quality checks..."
python -m src.quality.warehouse_quality

echo ""
echo "[7/8] Starting API..."
docker compose up -d --build api

echo "Waiting for API..."
for i in {1..40}; do
  if curl -fsS http://localhost:8000/health >/dev/null 2>&1; then
    break
  fi
  sleep 2
done

echo ""
echo "[8/8] Final verification..."
python -m pytest -q

curl -fsS http://localhost:8000/health
echo
curl -fsS http://localhost:8000/metrics/summary
echo

echo ""
echo "=================================================="
echo " PLUTO DATA PLATFORM V2 IS RUNNING"
echo "=================================================="
echo "PostgreSQL : ${POSTGRES_HOST:-127.0.0.1}:${POSTGRES_PORT:-5433}"
echo "API docs   : http://localhost:8000/docs"
echo "API health : http://localhost:8000/health"
echo "=================================================="
