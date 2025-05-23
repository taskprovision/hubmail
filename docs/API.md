# HubMail - API Reference

## Service Endpoints

### Elasticsearch (Port: 9200)

#### Search Emails
```bash
GET /emails/_search
```
**Example:**
```bash
curl "http://localhost:9200/emails/_search?q=subject:meeting&size=10"
```

#### Get Email by ID
```bash
GET /emails/_doc/{id}
```
**Example:**
```bash
curl "http://localhost:9200/emails/_doc/email-12345"
```

#### Index New Email
```bash
POST /emails/_doc
Content-Type: application/json
```
**Example:**
```bash
curl -X POST "http://localhost:9200/emails/_doc" \
  -H "Content-Type: application/json" \
  -d '{
    "from": "sender@example.com",
    "to": "recipient@example.com",
    "subject": "Meeting Request",
    "body": "Can we schedule a meeting for tomorrow?",
    "date": "2024-01-20T10:30:00Z"
  }'
```

#### Search with Query
```bash
POST /emails/_search
Content-Type: application/json
```
**Example:**
```bash
curl -X POST "http://localhost:9200/emails/_search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": {
      "bool": {
        "must": [
          {"match": {"subject": "meeting"}},
          {"range": {"date": {"gte": "2024-01-01T00:00:00Z"}}}
        ]
      }
    },
    "sort": [{"date": {"order": "desc"}}]
  }'
```

### Node-RED (Port: 1880)

#### Get All Flows
```bash
GET /flows
```
**Example:**
```bash
curl "http://localhost:1880/flows"
```

#### Deploy Flows
```bash
POST /flows
Content-Type: application/json
```
**Example:**
```bash
curl -X POST "http://localhost:1880/flows" \
  -H "Content-Type: application/json" \
  -d @flows.json
```

#### Trigger Email Processing
```bash
POST /inject/{node-id}
```
**Example:**
```bash
curl -X POST "http://localhost:1880/inject/email-processor"
```

### Ollama AI (Port: 11435)

#### List Available Models
```bash
GET /api/tags
```
**Example:**
```bash
curl "http://localhost:11435/api/tags"
```

#### Generate Email Analysis
```bash
POST /api/generate
Content-Type: application/json
```
**Example:**
```bash
curl -X POST "http://localhost:11435/api/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama2:13b",
    "prompt": "Analyze this email: Subject: Urgent Meeting, From: boss@company.com, Body: We need to discuss the project status immediately. Classify as URGENT/BUSINESS/SPAM/PERSONAL.",
    "stream": false
  }'
```

#### Pull Model
```bash
POST /api/pull
Content-Type: application/json
```
**Example:**
```bash
curl -X POST "http://localhost:11435/api/pull" \
  -H "Content-Type: application/json" \
  -d '{"name": "llama2:7b"}'
```

### Prometheus (Port: 9090)

#### Query Metrics
```bash
GET /api/v1/query
```
**Example:**
```bash
curl "http://localhost:9090/api/v1/query?query=node_red_emails_processed_total"
```

#### Range Query
```bash
GET /api/v1/query_range
```
**Example:**
```bash
curl "http://localhost:9090/api/v1/query_range?query=node_red_emails_processed_total&start=2024-01-01T00:00:00Z&end=2024-01-02T00:00:00Z&step=1h"
```

### Grafana (Port: 3000)

#### Get Dashboards
```bash
GET /api/dashboards
Authorization: Bearer API_KEY
```
**Example:**
```bash
curl "http://localhost:3000/api/dashboards" \
  -H "Authorization: Bearer eyJrIjoiT0tTcG1pUlY2RnVKZTFVaDFsNFZXdE9ZWmNrMkZYbk"
```

#### Export Dashboard
```bash
GET /api/dashboards/uid/{uid}
Authorization: Bearer API_KEY
```
**Example:**
```bash
curl "http://localhost:3000/api/dashboards/uid/email-metrics" \
  -H "Authorization: Bearer eyJrIjoiT0tTcG1pUlY2RnVKZTFVaDFsNFZXdE9ZWmNrMkZYbk"
```

### Redis (Port: 6379)

#### Redis CLI Examples
```bash
# Get all keys
redis-cli -h localhost -p 6379 KEYS "*"

# Get email statistics
redis-cli -h localhost -p 6379 HGETALL "email:stats"

# Get classification counts
redis-cli -h localhost -p 6379 HGETALL "email:classifications"
```

## Custom API Endpoints

### Email Processing API

#### Trigger Email Check
```bash
POST /api/email/check
Content-Type: application/json
```
**Example:**
```bash
curl -X POST "http://localhost:1880/api/email/check" \
  -H "Content-Type: application/json" \
  -d '{
    "force": true
  }'
```

#### Get Email Statistics
```bash
GET /api/email/stats
```
**Example:**
```bash
curl "http://localhost:1880/api/email/stats"
```
**Response:**
```json
{
  "total_processed": 1250,
  "classifications": {
    "URGENT": 125,
    "BUSINESS": 850,
    "PERSONAL": 200,
    "SPAM": 75
  },
  "processing_time_avg_ms": 1200,
  "last_check": "2024-01-20T10:30:00Z"
}
```

#### Submit Email for Processing
```bash
POST /api/email/process
Content-Type: application/json
```
**Example:**
```bash
curl -X POST "http://localhost:1880/api/email/process" \
  -H "Content-Type: application/json" \
  -d '{
    "from": "sender@example.com",
    "to": "recipient@example.com",
    "subject": "Meeting Request",
    "body": "Can we schedule a meeting for tomorrow?",
    "date": "2024-01-20T10:30:00Z"
  }'
```
**Response:**
```json
{
  "id": "email-12345",
  "classification": "BUSINESS",
  "confidence": 0.92,
  "processing_time_ms": 850,
  "auto_reply": true,
  "timestamp": "2024-01-20T10:30:05Z"
}
```

#### Get Email by ID
```bash
GET /api/email/{id}
```
**Example:**
```bash
curl "http://localhost:1880/api/email/email-12345"
```

#### Update Email Classification
```bash
PUT /api/email/{id}/classification
Content-Type: application/json
```
**Example:**
```bash
curl -X PUT "http://localhost:1880/api/email/email-12345/classification" \
  -H "Content-Type: application/json" \
  -d '{
    "classification": "URGENT",
    "reason": "Time-sensitive content"
  }'
```

### System Management API

#### Get System Status
```bash
GET /api/system/status
```
**Example:**
```bash
curl "http://localhost:1880/api/system/status"
```
**Response:**
```json
{
  "status": "healthy",
  "services": {
    "node-red": "running",
    "ollama": "running",
    "redis": "running",
    "prometheus": "running",
    "grafana": "running"
  },
  "uptime": 86400,
  "version": "1.2.0",
  "last_update": "2024-01-15T00:00:00Z"
}
```

#### Restart Service
```bash
POST /api/system/service/{service}/restart
```
**Example:**
```bash
curl -X POST "http://localhost:1880/api/system/service/node-red/restart"
```

#### Get System Metrics
```bash
GET /api/system/metrics
```
**Example:**
```bash
curl "http://localhost:1880/api/system/metrics"
```
**Response:**
```json
{
  "cpu_usage": 25.5,
  "memory_usage": 1250000000,
  "disk_usage": 45.2,
  "network": {
    "rx_bytes": 1024000,
    "tx_bytes": 512000
  },
  "timestamp": "2024-01-20T10:30:00Z"
}
```

## Webhook Integration

### Slack Notifications

#### Configure Slack Webhook
In `.env`:
```bash
WEBHOOK_URL=https://hooks.slack.com/services/your-webhook-url
WEBHOOK_ENABLED=true
```

#### Example Payload
```json
{
  "text": "New URGENT email received",
  "blocks": [
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "*New URGENT email received*\nFrom: sender@example.com\nSubject: Critical Issue"
      }
    },
    {
      "type": "actions",
      "elements": [
        {
          "type": "button",
          "text": {
            "type": "plain_text",
            "text": "View Email"
          },
          "url": "http://localhost:1880/email/view/email-12345"
        }
      ]
    }
  ]
}
```

## Client Libraries

### Node.js Client

```javascript
const axios = require('axios');

class HubMailClient {
  constructor(baseUrl = 'http://localhost:1880') {
    this.baseUrl = baseUrl;
  }

  async getEmailStats() {
    const response = await axios.get(`${this.baseUrl}/api/email/stats`);
    return response.data;
  }

  async processEmail(emailData) {
    const response = await axios.post(`${this.baseUrl}/api/email/process`, emailData);
    return response.data;
  }

  async getSystemStatus() {
    const response = await axios.get(`${this.baseUrl}/api/system/status`);
    return response.data;
  }
}

module.exports = HubMailClient;
```

### Python Client

```python
import requests

class HubMailClient:
    def __init__(self, base_url='http://localhost:1880'):
        self.base_url = base_url
        
    def get_email_stats(self):
        response = requests.get(f"{self.base_url}/api/email/stats")
        return response.json()
    
    def process_email(self, email_data):
        response = requests.post(
            f"{self.base_url}/api/email/process",
            json=email_data
        )
        return response.json()
    
    def get_system_status(self):
        response = requests.get(f"{self.base_url}/api/system/status")
        return response.json()
```