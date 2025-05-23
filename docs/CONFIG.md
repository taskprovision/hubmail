# HubMail - Configuration Reference

## Environment Variables (.env)

### Network & Project Settings
```bash
# Project identification
COMPOSE_PROJECT_NAME=hubmail
NETWORK_NAME=hub-net

# Docker network settings
DOCKER_NETWORK_SUBNET=172.20.0.0/16
DOCKER_NETWORK_GATEWAY=172.20.0.1
```

### Service Ports
```bash
# Core services
NODERED_PORT=1880
PROMETHEUS_PORT=9090
GRAFANA_PORT=3000

# AI & cache
OLLAMA_PORT=11435
REDIS_PORT=6379
```

### Email Server Configuration
```bash
# Email server settings
EMAIL_SERVER=imap.gmail.com
EMAIL_USER=your-email@gmail.com
EMAIL_PASS=your-app-password
EMAIL_PORT=993
EMAIL_SSL=true

# Email processing
EMAIL_CHECK_INTERVAL=60
EMAIL_MAX_MESSAGES=100
EMAIL_FOLDER=INBOX
EMAIL_PROCESSED_FOLDER=Processed
EMAIL_ERROR_FOLDER=Error

# Filters
EMAIL_SUBJECT_FILTER=
EMAIL_FROM_FILTER=
EMAIL_TO_FILTER=
```

### Node-RED Configuration
```bash
# Server settings
NODERED_TZ=Europe/Warsaw
NODERED_ENABLE_PROJECTS=true
NODERED_UI_HOST=0.0.0.0
NODERED_UI_PORT=1880
NODERED_CREDENTIAL_SECRET=your-secret-key-here

# Security
NODERED_ADMIN_AUTH=true
NODERED_ADMIN_USER=admin
NODERED_ADMIN_PASSWORD=admin123

# Features
NODERED_ENABLE_TOURS=false
NODERED_ENABLE_SAFE_MODE=false
```

### AI & LLM Configuration
```bash
# Model settings
OLLAMA_HOST=ollama
OLLAMA_CONTAINER_PORT=11434
OLLAMA_ORIGINS=*
LLM_MODEL=llama2:13b
LLM_TEMPERATURE=0.1
LLM_TOP_P=0.9
LLM_TOP_K=40

# Analysis thresholds
CONFIDENCE_THRESHOLD=0.8
CLASSIFICATION_THRESHOLD=0.7
SENTIMENT_THRESHOLD=0.6

# Model management
LLM_AUTO_PULL_MODELS=true
LLM_MODEL_CACHE_DIR=/models
LLM_MAX_CONTEXT_LENGTH=4096
```

### Redis Configuration
```bash
# Connection
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0

# Performance
REDIS_MAXMEMORY=256mb
REDIS_MAXMEMORY_POLICY=allkeys-lru
REDIS_SAVE_FREQUENCY=900 1
```

### Prometheus Configuration
```bash
# Basic settings
PROMETHEUS_RETENTION=30d
PROMETHEUS_STORAGE_PATH=/prometheus
PROMETHEUS_CONFIG_PATH=/etc/prometheus

# Scrape intervals
PROMETHEUS_SCRAPE_INTERVAL=15s
PROMETHEUS_EVALUATION_INTERVAL=15s

# Targets
PROMETHEUS_TARGETS=node-red:1880,ollama:11434,redis:6379
```

### Grafana Configuration
```bash
# Authentication
GRAFANA_ADMIN_PASSWORD=admin
GRAFANA_ALLOW_SIGN_UP=false

# Features
GRAFANA_PLUGINS=grafana-piechart-panel
GRAFANA_DASHBOARDS_PATH=/etc/grafana/provisioning/dashboards
GRAFANA_DATASOURCES_PATH=/etc/grafana/provisioning/datasources

# UI settings
GRAFANA_DEFAULT_THEME=dark
GRAFANA_HOME_DASHBOARD=email-metrics
```

### Email Classification Settings
```bash
# Classification categories
EMAIL_CATEGORIES=URGENT,BUSINESS,PERSONAL,SPAM

# Classification rules
URGENT_KEYWORDS=urgent,asap,immediately,emergency
BUSINESS_KEYWORDS=invoice,contract,meeting,proposal
PERSONAL_KEYWORDS=family,personal,private,holiday
SPAM_KEYWORDS=offer,discount,sale,limited time

# Processing options
AUTO_CLASSIFICATION=true
AUTO_REPLY=true
AUTO_ROUTING=true
```

### Auto-Reply Templates
```bash
# Template settings
TEMPLATE_URGENT=templates/urgent-reply.txt
TEMPLATE_BUSINESS=templates/business-reply.txt
TEMPLATE_PERSONAL=templates/personal-reply.txt
TEMPLATE_OUT_OF_OFFICE=templates/out-of-office.txt

# Signature
EMAIL_SIGNATURE=templates/signature.html
EMAIL_REPLY_FROM=your-email@gmail.com
EMAIL_REPLY_NAME=HubMail Auto-Reply
```

### Monitoring & Logging
```bash
# Log levels
LOG_LEVEL=INFO
NODERED_LOG_LEVEL=INFO
OLLAMA_LOG_LEVEL=INFO
REDIS_LOG_LEVEL=WARN

# Metrics
METRICS_ENABLED=true
METRICS_RETENTION_DAYS=30

# Health checks
HEALTH_CHECK_INTERVAL=30s
HEALTH_CHECK_TIMEOUT=10s
HEALTH_CHECK_RETRIES=3
```

### Notification Settings
```bash
# Email notifications
NOTIFICATION_EMAIL=admin@example.com
NOTIFICATION_LEVEL=ERROR
NOTIFICATION_INTERVAL=3600

# Webhook notifications
WEBHOOK_URL=https://hooks.slack.com/services/your-webhook-url
WEBHOOK_ENABLED=false
WEBHOOK_FORMAT=json
```

### Volume Paths
```bash
# Data storage
VOLUME_NODE_RED=./data/node-red
VOLUME_OLLAMA=./data/ollama
VOLUME_PROMETHEUS=./data/prometheus
VOLUME_GRAFANA=./data/grafana
VOLUME_REDIS=./data/redis

# Configuration
CONFIG_NODE_RED=./config/node-red
CONFIG_PROMETHEUS=./config/prometheus
CONFIG_GRAFANA=./config/grafana
```

### Backup Settings
```bash
# Backup settings
BACKUP_ENABLED=true
BACKUP_SCHEDULE="0 2 * * *"
BACKUP_RETENTION_DAYS=30
BACKUP_PATH=./backups
BACKUP_INCLUDE_DATA=true
BACKUP_INCLUDE_CONFIG=true
BACKUP_COMPRESS=true
```

### Security Settings
```bash
# Docker security
DOCKER_UID=1000
DOCKER_GID=1000
DOCKER_RESTART_POLICY=unless-stopped

# Network security
EXPOSE_PORTS_EXTERNALLY=true
USE_HTTPS=false
SSL_CERT_PATH=./certs/server.crt
SSL_KEY_PATH=./certs/server.key
```

## Configuration Files

### Node-RED Flow Configuration
Location: `config/node-red/flows.json`

This file contains all the Node-RED flows for email processing:
- Email retrieval flow
- Classification flow
- Auto-reply flow
- Routing flow
- Metrics collection flow

### Prometheus Configuration
Location: `config/prometheus/prometheus.yml`

Example configuration:
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'node-red'
    static_configs:
      - targets: ['node-red:1880']
  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']
```

### Grafana Dashboards
Location: `config/grafana/dashboards/email-metrics.json`

This dashboard includes:
- Email volume metrics
- Classification distribution
- Processing time statistics
- Error rate monitoring
- System resource usage

### Email Templates
Location: `config/templates/`

Templates for auto-replies based on email classification:
- `urgent-reply.txt`: For urgent emails
- `business-reply.txt`: For business emails
- `personal-reply.txt`: For personal emails
- `out-of-office.txt`: For out-of-office periods
- `signature.html`: Email signature template

## Advanced Configuration

### Custom Classification Logic
You can modify the classification logic in Node-RED by editing the function node:

```javascript
// Example classification function
function classifyEmail(email) {
  const subject = email.subject.toLowerCase();
  const body = email.body.toLowerCase();
  const from = email.from.toLowerCase();
  
  // Check for urgent patterns
  if (subject.includes('urgent') || subject.includes('asap')) {
    return 'URGENT';
  }
  
  // Check for business patterns
  if (subject.includes('invoice') || subject.includes('meeting')) {
    return 'BUSINESS';
  }
  
  // Default to AI classification
  return classifyWithAI(email);
}
```

### Custom Prompts for AI Classification
Edit the AI prompt template in `config/node-red/settings.js`:

```javascript
module.exports = {
  // ... other settings
  functionGlobalContext: {
    classificationPrompt: `
      Analyze this email and classify it as one of the following:
      - URGENT: Time-sensitive matters requiring immediate attention
      - BUSINESS: Work-related but not urgent
      - PERSONAL: Non-work related personal communications
      - SPAM: Unwanted or marketing emails
      
      Email:
      Subject: {{subject}}
      From: {{from}}
      Body: {{body}}
      
      Classification:
    `
  }
}
```

### Performance Tuning
Adjust resource limits in `docker-compose.yml`:

```yaml
services:
  node-red:
    # ...
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 1G
  ollama:
    # ...
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
```