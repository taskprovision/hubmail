#!/bin/bash

echo "🧪 Testing Email Processing Flow..."

# Test 1: Urgent Email
echo "Testing urgent email classification..."
curl -X POST http://localhost:1880/email-test \
  -H "Content-Type: application/json" \
  -d '{
    "from": "server-alerts@company.com",
    "subject": "CRITICAL: Production Server Down",
    "body": "Our main production server has crashed and is unresponsive. Multiple services are affected. Immediate attention required."
  }'

sleep 2

# Test 2: Business Email
echo "Testing business email classification..."
curl -X POST http://localhost:1880/email-test \
  -H "Content-Type: application/json" \
  -d '{
    "from": "client@example.com",
    "subject": "Quote Request for Q2 Project",
    "body": "Hi, we would like to request a quote for our upcoming project. Please send us your pricing information."
  }'

sleep 2

# Test 3: Spam Email
echo "Testing spam email classification..."
curl -X POST http://localhost:1880/email-test \
  -H "Content-Type: application/json" \
  -d '{
    "from": "winner@lottery.spam",
    "subject": "You have won $1,000,000!!!",
    "body": "Congratulations! You are our lucky winner. Click here to claim your prize. Limited time offer!"
  }'

echo "✅ Test emails sent! Check Node-RED debug panel and Grafana dashboard for results."
echo "📊 Grafana: http://localhost:3000"
echo "🔧 Node-RED: http://localhost:1880"