# HubMail - Quick Start Guide

## 5-Minute Setup

### 1. Prerequisites
```bash
# Check if Docker is installed
docker --version
docker-compose --version

# If not installed:
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

### 2. Download & Configure
```bash
# Clone or download HubMail
git clone https://github.com/taskprovision/hubmail.git
cd hubmail

# Copy configuration
cp .env.example .env

# Quick setup (Linux/macOS)
./quick-setup.sh
```

### 3. Start System
```bash
# Start all services
docker-compose up -d

# Wait for startup (important!)
sleep 60
```

### 4. Verify Installation
```bash
# Check services
curl http://localhost:1880  # Node-RED Dashboard
curl http://localhost:11435 # Ollama API
curl http://localhost:9090  # Prometheus
curl http://localhost:3000  # Grafana
curl http://localhost:6379  # Redis (use redis-cli)
```

### 5. Test Email Processing
```bash
# Send test email (requires configuration)
curl -X POST "http://localhost:1880/api/email/process" \
  -H "Content-Type: application/json" \
  -d '{
    "from": "test@example.com",
    "to": "system@hubmail.local",
    "subject": "Test Email",
    "body": "This is a test email for HubMail system."
  }'

# Check processing (wait a few seconds)
curl "http://localhost:1880/api/email/stats"
```

## Access Points

| Service | URL | Purpose |
|---------|-----|---------|
| **Main Dashboard** | http://localhost:1880 | Email processing workflows |
| **Metrics** | http://localhost:3000 | Grafana dashboards for monitoring |
| **AI Models** | http://localhost:11435 | Ollama API for email classification |
| **Monitoring** | http://localhost:9090 | Prometheus metrics |

## First Steps

### Configure Email Access
```bash
# Edit .env file with your email credentials
# Example:
EMAIL_SERVER=imap.example.com
EMAIL_USER=your-email@example.com
EMAIL_PASS=your-secure-password
EMAIL_PORT=993
EMAIL_SECURE=true
```

### View Results
```bash
# Check email processing statistics
curl "http://localhost:1880/api/email/stats"

# Or use Grafana dashboard
# Open http://localhost:3000
# Login with default credentials (admin/admin)
# Navigate to the Email Processing dashboard
```

### Monitor Processing
```bash
# View Node-RED dashboard
open http://localhost:1880

# Check processing logs
docker-compose logs -f node-red
```

## Common Commands

### System Control
```bash
# Start system
docker-compose up -d

# Stop system
docker-compose down

# Restart system
docker-compose restart

# View status
docker-compose ps
```

### Troubleshooting
```bash
# Check all services
docker-compose ps

# View logs
docker-compose logs

# Restart specific service
docker-compose restart node-red

# Reset everything (CAUTION: loses data)
docker-compose down -v
sudo rm -rf data/*
docker-compose up -d
```

### Health Check
```bash
# Quick health check
for port in 1880 11435 9090 3000 6379; do
  if [ $port -eq 6379 ]; then
    redis-cli -h localhost -p $port PING | grep -q "PONG" && echo "Redis Port $port: OK" || echo "Redis Port $port: FAIL"
  else
    curl -s http://localhost:$port > /dev/null && echo "Port $port: OK" || echo "Port $port: FAIL"
  fi
done
```

## Email Features Supported

- **Classification**: Automatic categorization (URGENT, BUSINESS, PERSONAL, SPAM)
- **Auto-Reply**: Configurable templates based on email type
- **Attachments**: Processing and storage of email attachments
- **Monitoring**: Real-time metrics on email processing
- **Notifications**: Alerts for important emails via Slack or other webhooks

## Basic Usage Examples

### Search Emails
```bash
# Find all urgent emails
curl "http://localhost:1880/api/email/search?classification=URGENT"

# Find emails from last week
curl "http://localhost:1880/api/email/search" -d '
{
  "query": {
    "range": {
      "date": {
        "gte": "now-7d"
      }
    }
  }
}'
```

### Process Specific Email
```bash
# Manually process an email
curl -X POST "http://localhost:1880/api/email/process" \
  -H "Content-Type: application/json" \
  -d '{
    "from": "important@example.com",
    "to": "your-email@example.com",
    "subject": "Urgent Meeting",
    "body": "We need to discuss the project status immediately.",
    "date": "2024-01-20T10:30:00Z"
  }'

# Check processing result
curl "http://localhost:1880/api/email/search?q=subject:Urgent%20Meeting"
```

### View Analytics
1. Open Grafana: http://localhost:3000
2. Login with default credentials (admin/admin)
3. Navigate to the "Email Processing" dashboard
4. Explore your email metrics and classifications

## Configuration Quick Reference

### Key Ports (from .env)
```bash
NODE_RED_PORT=1880
OLLAMA_PORT=11435
PROMETHEUS_PORT=9090
GRAFANA_PORT=3000
REDIS_PORT=6379
```

### Important Environment Variables
```bash
# Email Server Settings
EMAIL_SERVER=imap.example.com
EMAIL_USER=your-email@example.com
EMAIL_PASS=your-secure-password
EMAIL_PORT=993
EMAIL_SECURE=true
EMAIL_CHECK_INTERVAL=300

# Node-RED Settings
NODERED_ADMIN_USER=admin
NODERED_ADMIN_PASSWORD=password

# AI Model Settings
LLM_MODEL=llama2:7b
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=2048

# Redis Settings
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=

# Notification Settings
WEBHOOK_URL=https://hooks.slack.com/services/your-webhook-url
WEBHOOK_ENABLED=true
```

## Advanced Configuration

### Email Classification Settings
Edit the `.env` file to customize classification thresholds:
```bash
# Classification confidence thresholds
CLASSIFICATION_THRESHOLD_URGENT=0.8
CLASSIFICATION_THRESHOLD_BUSINESS=0.6
CLASSIFICATION_THRESHOLD_PERSONAL=0.7
CLASSIFICATION_THRESHOLD_SPAM=0.9
```

### Auto-Reply Templates
Create custom auto-reply templates in the Node-RED flow:
1. Open Node-RED: http://localhost:1880
2. Navigate to the "Auto-Reply" flow
3. Edit the "Template" nodes for each email classification
4. Deploy your changes

### OAuth2 Email Authentication
For more secure email access, configure OAuth2:
```bash
# In .env file
EMAIL_AUTH_TYPE=oauth2
EMAIL_OAUTH_CLIENT_ID=your-client-id
EMAIL_OAUTH_CLIENT_SECRET=your-client-secret
EMAIL_OAUTH_REFRESH_TOKEN=your-refresh-token
EMAIL_OAUTH_ACCESS_TOKEN=your-access-token
EMAIL_OAUTH_EXPIRES=1234567890
```

### Scaling for High Volume
For high email volume environments:
```bash
# Increase resources in docker-compose.yml
services:
  node-red:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G

# Adjust processing settings in .env
EMAIL_BATCH_SIZE=50
EMAIL_PROCESSING_THREADS=4
```

## Troubleshooting Common Issues

### Email Connection Problems
```bash
# Check email server connectivity
nc -zv $EMAIL_SERVER $EMAIL_PORT

# View detailed connection logs
docker-compose logs node-red | grep "Email connection"

# Restart email processing
curl -X POST "http://localhost:1880/api/system/service/node-red/restart"
```

### AI Model Issues
```bash
# Check if model is loaded
curl "http://localhost:11435/api/tags"

# Pull model again if needed
curl -X POST "http://localhost:11435/api/pull" \
  -H "Content-Type: application/json" \
  -d '{"name": "llama2:7b"}'

# Restart Ollama service
docker-compose restart ollama
```

### Performance Optimization
If the system is running slowly:
```bash
# Check resource usage
docker stats

# Increase Docker resources
# Edit Docker Desktop settings or server limits

# Restart Docker
sudo systemctl restart docker
docker-compose up -d
```

## Getting Help

- **System Status**: Check http://localhost:1880 dashboard
- **Logs**: `docker-compose logs [service-name]`
- **Documentation**: See other .md files in docs/
- **Issues**: Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

**🎉 You're ready to start processing emails with HubMail!**

Send a test email to `system@hubmail.local` and watch it get processed automatically.