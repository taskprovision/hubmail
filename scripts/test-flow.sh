#!/bin/bash

echo "🧪 Testing Email Processing System..."

# Check if API is running
echo "Checking API health..."
API_HEALTH=$(curl -s http://localhost:${API_PORT:-3001}/health)

if [[ $API_HEALTH == *"status":"ok"* ]]; then
  echo "✅ API is running correctly"
else
  echo "❌ API is not responding correctly. Please check the logs with 'make app-logs'"
  exit 1
fi

# Test 1: Urgent Email
echo "Testing urgent email classification..."
curl -X POST http://localhost:${API_PORT:-3001}/api/test-analysis \
  -H "Content-Type: application/json" \
  -d '{
    "from_address": "server-alerts@company.com",
    "subject": "CRITICAL: Production Server Down",
    "body": "Our main production server has crashed and is unresponsive. Multiple services are affected. Immediate attention required."
  }' | jq .

sleep 2

# Test 2: Business Email
echo "Testing business email classification..."
curl -X POST http://localhost:${API_PORT:-3001}/api/test-analysis \
  -H "Content-Type: application/json" \
  -d '{
    "from_address": "client@example.com",
    "subject": "Quote Request for Q2 Project",
    "body": "Hi, we would like to request a quote for our upcoming project. Please send us your pricing information."
  }' | jq .

sleep 2

# Test 3: Spam Email
echo "Testing spam email classification..."
curl -X POST http://localhost:${API_PORT:-3001}/api/test-analysis \
  -H "Content-Type: application/json" \
  -d '{
    "from_address": "winner@lottery.spam",
    "subject": "You have won $1,000,000!!!",
    "body": "Congratulations! You are our lucky winner. Click here to claim your prize. Limited time offer!"
  }' | jq .

# Trigger a manual email check
echo "Triggering manual email check..."
curl -X POST http://localhost:${API_PORT:-3001}/api/check-emails | jq .

echo "✅ Tests completed! Check the application logs for results."
echo "📊 Grafana: http://localhost:${GRAFANA_PORT:-3000}"
echo "🚀 API: http://localhost:${API_PORT:-3001}/health"
echo "📈 Dashboard: http://localhost:${UI_PORT:-8501}"