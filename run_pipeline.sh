#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if [[ -z "${AIRFLOW_HOME:-}" && -z "${VIRTUAL_ENV:-}" && -f ".venv/bin/activate" ]]; then
  source .venv/bin/activate
fi

echo ""
echo "======================================"
echo " PLUTO DATA PLATFORM"
echo "======================================"

echo ""
echo "[1/7] Profiling source workbooks..."
python -m src.ingestion.profile_workbooks

echo ""
echo "[2/7] Ingesting customer transactions..."
python -m src.ingestion.customer_transactions

echo ""
echo "[3/7] Transforming and curating transactions..."
python -m src.transform.customer_transactions

echo ""
echo "[4/7] Investigating unknown transactions..."
python -m src.quality.investigate_unknown_transactions

echo ""
echo "[5/7] Producing data-quality report..."
python -m src.quality.data_quality_report

echo ""
echo "[6/7] Building customer dimension..."
python -m src.transform.customer_dimension

echo ""
echo "[7/7] Running tests and final validation..."
python -m pytest -q
python -m src.quality.final_validation

echo ""
echo "======================================"
echo " PIPELINE COMPLETED SUCCESSFULLY"
echo "======================================"
