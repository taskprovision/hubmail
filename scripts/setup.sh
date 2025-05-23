#!/bin/bash

echo "🔧 Setting up Email Intelligence Hub..."

# Wait for Grafana to be ready
until curl -f http://admin:admin@localhost:3000/api/health; do
    echo "Waiting for Grafana..."
    sleep 5
done

# Import dashboard
curl -X POST \
  http://admin:admin@localhost:3000/api/dashboards/db \
  -H "Content-Type: application/json" \
  -d @config/grafana/dashboards/email-dashboard.json

echo "✅ Dashboard imported successfully!"