# DocPro - Configuration Reference

## Environment Variables (.env)

### Network & Project Settings
```bash
# Project identification
COMPOSE_PROJECT_NAME=docpro
NETWORK_NAME=doc-net

# Docker network settings
DOCKER_NETWORK_SUBNET=172.20.0.0/16
DOCKER_NETWORK_GATEWAY=172.20.0.1
```

### Service Ports
```bash
# Core services
ELASTICSEARCH_HTTP_PORT=9200
KIBANA_PORT=5601
NODE_RED_PORT=1880

# Storage & processing
MINIO_API_PORT=9000
MINIO_CONSOLE_PORT=9001
TIKA_PORT=9998
OCR_PORT=8082

# AI & cache
OLLAMA_PORT=11437
REDIS_PORT=6378
```

### Elasticsearch Configuration
```bash
# Basic settings
ELASTICSEARCH_HOST=elasticsearch
ELASTICSEARCH_PORT=9200
ELASTICSEARCH_DISCOVERY_TYPE=single-node

# Memory settings
ES_JAVA_OPTS=-Xms512m -Xmx512m

# Security
XPACK_SECURITY_ENABLED=false
ELASTICSEARCH_USERNAME=elastic
ELASTICSEARCH_PASSWORD=changeme

# Indices
ES_INDEX_DOCUMENTS=documents
ES_INDEX_ALERTS=compliance-alerts

# Performance
ELASTICSEARCH_REFRESH_INTERVAL=5s
ELASTICSEARCH_NUMBER_OF_SHARDS=1
ELASTICSEARCH_NUMBER_OF_REPLICAS=0
```

### Kibana Configuration
```bash
# Connection
KIBANA_ELASTICSEARCH_HOST=http://elasticsearch:9200
KIBANA_SERVER_NAME=kibana
KIBANA_SERVER_HOST=0.0.0.0

# Security
KIBANA_ELASTICSEARCH_USERNAME=elastic
KIBANA_ELASTICSEARCH_PASSWORD=changeme

# SSL (if enabled)
KIBANA_SERVER_SSL_ENABLED=false
KIBANA_SERVER_SSL_CERTIFICATE=/certs/kibana.crt
KIBANA_SERVER_SSL_KEY=/certs/kibana.key
```

### MinIO Storage Configuration
```bash
# Authentication
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin123

# Buckets
MINIO_BUCKET=documents
MINIO_DEFAULT_BUCKET=documents
MINIO_PROCESSED_BUCKET=processed
MINIO_TEMPLATES_BUCKET=templates

# Regional settings
MINIO_REGION=us-east-1

# Performance
MINIO_CACHE_DRIVES=/tmp/minio-cache
MINIO_CACHE_EXCLUDE="*.tmp"
```

### Document Processing Settings
```bash
# File handling
MAX_DOCUMENT_SIZE=50MB
SUPPORTED_FORMATS=pdf,docx,png,jpg,jpeg,tiff,txt,rtf,odt
PROCESSING_THREADS=4

# Timeouts
TIKA_TIMEOUT_MS=30000
OCR_TIMEOUT_MS=60000
LLM_TIMEOUT_MS=120000

# Processing options
AUTO_PROCESSING=true
BATCH_PROCESSING=false
PARALLEL_PROCESSING=true
```

### AI & LLM Configuration
```bash
# Model settings
OLLAMA_HOST=ollama
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

### OCR Configuration
```bash
# OCR service
OCR_SERVICE_URL=http://ocr:8080
OCR_LANGUAGE=eng+pol
OCR_DPI=300
OCR_PREPROCESSING=true

# Tesseract settings
TESSERACT_PSM=6
TESSERACT_OEM=3
TESSERACT_WHITELIST="0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,!?-"
```

### Node-RED Configuration
```bash
# Server settings
NODE_RED_UI_HOST=0.0.0.0
NODE_RED_UI_PORT=1880
NODE_RED_CREDENTIAL_SECRET=your-secret-key-here

# Security
NODE_RED_ADMIN_AUTH=true
NODE_RED_ADMIN_USER=admin
NODE_RED_ADMIN_PASSWORD=admin123

# Features
NODE_RED_ENABLE_PROJECTS=true
NODE_RED_ENABLE_TOURS=false
NODE_RED_ENABLE_SAFE_MODE=false
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

### Monitoring & Logging
```bash
# Log levels
LOG_LEVEL=INFO
ELASTICSEARCH_LOG_LEVEL=WARN
KIBANA_LOG_LEVEL=INFO
NODE_RED_LOG_LEVEL=INFO

# Metrics
METRICS_ENABLED=true
PROMETHEUS_PORT=9090
GRAFANA_PORT=3000

# Health checks
HEALTH_CHECK_INTERVAL=30s
HEALTH_CHECK_TIMEOUT=10s
HEALTH_CHECK_RETRIES=3
```

### Notification Settings
```bash
# Email notifications
EMAIL_ENABLED=false
EMAIL_SMTP_HOST=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_SMTP_USER=your-email@gmail.com
EMAIL_SMTP_PASSWORD=your-app-password
EMAIL_FROM=docpro@company.com
EMAIL_TO_ADMIN=admin@company.com

# Slack integration
SLACK_ENABLED=false
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
SLACK_CHANNEL=#document-alerts
SLACK_USERNAME=DocPro Bot

# Microsoft Teams
TEAMS_ENABLED=false
TEAMS_WEBHOOK_URL=https://outlook.office.com/webhook/YOUR/TEAMS/WEBHOOK
```

### Compliance & Business Rules
```bash
# Compliance monitoring
COMPLIANCE_ENABLED=true
COMPLIANCE_STRICT_MODE=false

# Business thresholds
INVOICE_AMOUNT_THRESHOLD=10000
CONTRACT_RISK_ALERT=true
COR_VALIDITY_CHECK=true
COR_EXPIRY_WARNING_DAYS=30

# Workflow settings
AUTO_APPROVAL_LIMIT=1000
MANUAL_REVIEW_THRESHOLD=50000
ESCALATION_TIMEOUT_HOURS=24
```

### Security Settings
```bash
# Authentication
AUTH_ENABLED=false
JWT_SECRET=your-jwt-secret-key-here
SESSION_TIMEOUT=3600
API_RATE_LIMIT=100

# SSL/TLS
SSL_ENABLED=false
SSL_CERT_PATH=/certs/server.crt
SSL_KEY_PATH=/certs/server.key
SSL_CA_PATH=/certs/ca.crt

# CORS
CORS_ENABLED=true
CORS_ORIGINS=http://localhost:*,https://localhost:*
CORS_METHODS=GET,POST,PUT,DELETE
```

### Backup & Retention
```bash
# Backup settings
BACKUP_ENABLED=true
BACKUP_SCHEDULE="0 2 * * *"
BACKUP_RETENTION_DAYS=30
BACKUP_DESTINATION=/backups

# Data retention
DOCUMENT_RETENTION_DAYS=365
LOG_RETENTION_DAYS=90
METRICS_RETENTION_DAYS=30
ELASTICSEARCH_INDEX_RETENTION=90d
```

### Performance Tuning
```bash
# General performance
WORKER_PROCESSES=4
MAX_CONNECTIONS=1000
KEEPALIVE_TIMEOUT=65

# Elasticsearch performance
ES_REFRESH_INTERVAL=5s
ES_FLUSH_THRESHOLD_SIZE=512mb
ES_MERGE_POLICY_MAX_MERGE_AT_ONCE=10

# Processing performance
BULK_SIZE=100
BULK_FLUSH_INTERVAL=5s
PROCESSING_QUEUE_SIZE=1000
```

### Development Settings
```bash
# Development mode
DEVELOPMENT_MODE=false
DEBUG_ENABLED=false
VERBOSE_LOGGING=false

# Testing
TEST_MODE=false
MOCK_SERVICES=false
DISABLE_AUTH=false

# Hot reload
HOT_RELOAD=false
WATCH_FILES=false
```

## Configuration Files

### docker-compose.yml Override
```yaml
# docker-compose.override.yml
version: '3.8'
services:
  elasticsearch:
    environment:
      - "ES_JAVA_OPTS=-Xms2g -Xmx2g"
    volumes:
      - /custom/path:/usr/share/elasticsearch/data
  
  node-red:
    volumes:
      - ./custom-flows:/data/flows
```

### Node-RED Settings
```javascript
// config/node-red/settings.js
module.exports = {
    uiPort: process.env.NODE_RED_PORT || 1880,
    httpAdminRoot: '/admin',
    httpNodeRoot: '/api',
    userDir: '/data',
    
    adminAuth: {
        type: "credentials",
        users: [{
            username: process.env.NODE_RED_ADMIN_USER,
            password: process.env.NODE_RED_ADMIN_PASSWORD_HASH,
            permissions: "*"
        }]
    },
    
    functionGlobalContext: {
        elasticsearch: require('elasticsearch'),
        moment: require('moment'),
        _: require('lodash')
    }
}
```

### Elasticsearch Configuration
```yaml
# config/elasticsearch/elasticsearch.yml
cluster.name: ${COMPOSE_PROJECT_NAME}-cluster
node.name: es-node-1

path.data: /usr/share/elasticsearch/data
path.logs: /usr/share/elasticsearch/logs

network.host: 0.0.0.0
http.port: 9200

discovery.type: single-node

xpack.security.enabled: ${XPACK_SECURITY_ENABLED}
xpack.monitoring.collection.enabled: false
```

### Kibana Configuration
```yaml
# config/kibana/kibana.yml
server.name: ${KIBANA_SERVER_NAME}
server.host: ${KIBANA_SERVER_HOST}
server.port: ${KIBANA_PORT}

elasticsearch.hosts: [${KIBANA_ELASTICSEARCH_HOST}]
elasticsearch.requestTimeout: 90000

xpack.security.enabled: ${XPACK_SECURITY_ENABLED}
```

## Environment-Specific Configurations

### Development Environment
```bash
# .env.development
LOG_LEVEL=DEBUG
DEVELOPMENT_MODE=true
HOT_RELOAD=true
ES_JAVA_OPTS=-Xms512m -Xmx512m
LLM_MODEL=llama2:7b
PROCESSING_THREADS=2
METRICS_ENABLED=false
```

### Production Environment
```bash
# .env.production
LOG_LEVEL=WARN
DEVELOPMENT_MODE=false
ES_JAVA_OPTS=-Xms4g -Xmx4g
LLM_MODEL=llama2:13b
PROCESSING_THREADS=8
BACKUP_ENABLED=true
SSL_ENABLED=true
AUTH_ENABLED=true
```

### Testing Environment
```bash
# .env.testing
LOG_LEVEL=INFO
TEST_MODE=true
ELASTICSEARCH_HTTP_PORT=9201
KIBANA_PORT=5602
NODE_RED_PORT=1881
MOCK_SERVICES=true
```

## Validation & Best Practices

### Configuration Validation
```bash
# Validate .env file
python3 scripts/validate-config.py

# Check port conflicts
netstat -tulpn | grep -E "(9200|5601|1880|9001)"

# Validate Docker compose
docker-compose config
```

### Security Best Practices
```bash
# Strong passwords
MINIO_ROOT_PASSWORD=$(openssl rand -base64 32)
NODE_RED_CREDENTIAL_SECRET=$(openssl rand -hex 32)
JWT_SECRET=$(openssl rand -hex 64)

# Restrict network access
ELASTICSEARCH_HOST=127.0.0.1
KIBANA_HOST=127.0.0.1

# Enable authentication
AUTH_ENABLED=true
XPACK_SECURITY_ENABLED=true
```

### Performance Best Practices
```bash
# Memory allocation (total system memory / 2)
ES_JAVA_OPTS=-Xms4g -Xmx4g

# SSD storage for Elasticsearch
# Map data directory to SSD
./data/elasticsearch -> /mnt/ssd/elasticsearch

# CPU allocation
PROCESSING_THREADS=$(nproc)
```

---

**Configuration Templates Available:**
- `.env.development` - Development settings
- `.env.production` - Production settings  
- `.env.testing` - Testing environment
- `docker-compose.override.yml` - Custom overrides