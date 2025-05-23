#!/bin/bash
set -e

# Start Prefect agent in the background
echo "Starting Prefect agent..."
prefect agent start &

# Start FastAPI in the background
echo "Starting FastAPI application..."
uvicorn api.main:app --host 0.0.0.0 --port 3001 &

# Start Streamlit
echo "Starting Streamlit dashboard..."
streamlit run ui/dashboard.py --server.port 8501 --server.address 0.0.0.0

# Keep container running
wait
