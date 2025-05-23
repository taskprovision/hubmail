#!/bin/bash
set -e

# Load environment variables from .env file if it exists
if [ -f ".env" ]; then
    echo "Loading environment variables from .env file..."
    export $(grep -v '^#' .env | xargs)
fi

# Set default values if environment variables are not set
API_HOST=${API_HOST:-0.0.0.0}
API_PORT=${API_PORT:-3001}
UI_PORT=${UI_PORT:-8501}
UI_HOST=${UI_HOST:-0.0.0.0}

# Start Prefect agent in the background
echo "Starting Prefect agent..."
prefect agent start &

# Start FastAPI in the background
echo "Starting FastAPI application on ${API_HOST}:${API_PORT}..."
uvicorn api.main:app --host "${API_HOST}" --port "${API_PORT}" &

# Start Streamlit
echo "Starting Streamlit dashboard on ${UI_HOST}:${UI_PORT}..."
streamlit run ui/dashboard.py --server.port "${UI_PORT}" --server.address "${UI_HOST}"

# Keep container running
wait
