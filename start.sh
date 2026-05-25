#!/bin/bash
set -e

source .venv/bin/activate

API_HOST="127.0.0.1"
API_PORT="${API_PORT:-8004}"
STREAMLIT_PORT="${STREAMLIT_PORT:-8504}"
export API_BASE_URL="http://${API_HOST}:${API_PORT}"

uvicorn app.main:app --host "${API_HOST}" --port "${API_PORT}" &
API_PID=$!

cleanup() {
  kill "${API_PID}" 2>/dev/null || true
}
trap cleanup EXIT

streamlit run streamlit_app.py --server.address "${API_HOST}" --server.port "${STREAMLIT_PORT}"

