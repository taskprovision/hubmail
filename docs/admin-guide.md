# HubMail - Administrator Guide

## System Administration

### Docker Management

#### Service Status
```bash
# Check all services
docker-compose ps

# Check specific service
docker-compose ps node-red

# View resource usage
docker stats
```

#### Logs Management
```bash
# View all logs
docker-compose logs

# Follow specific service logs
docker-compose logs -f node-red
docker-compose logs -f ollama

# Last 100 lines
docker-compose logs --tail=100 grafana
```

#### Service Control
```bash
# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart node-red

# Stop and remove everything
docker-compose down

# Full rebuild
docker-compose down -v
docker-compose up -d --build
```

### Configuration Management

#### Environment Variables (.env)
```bash
# Core ports
NODE_RED_PORT=1880
OLLAMA_PORT=11435
PROMETHEUS_PORT=9090
GRAFANA_PORT=3000
REDIS_PORT=6379

# Email settings
EMAIL_SERVER=imap.example.com
EMAIL_USER=your-email@example.com
EMAIL_PASS=your-secure-password
EMAIL_PORT=993
EMAIL_SECURE=true
EMAIL_CHECK_INTERVAL=300

# AI settings
LLM_MODEL=llama2:7b
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=2048

# Processing limits
EMAIL_BATCH_SIZE=50
EMAIL_PROCESSING_THREADS=4
```

#### Performance Tuning
```bash
# Node-RED memory
NODE_RED_MAX_OLD_SPACE_SIZE=2048

# Redis configuration
REDIS_MAXMEMORY=1gb
REDIS_MAXMEMORY_POLICY=allkeys-lru

# Enable swap if needed
sudo swapon /swapfile
```

### Data Management

#### Backup Strategy
```bash
# Create backup directory
mkdir -p backups/$(date +%Y%m%d)

# Backup Node-RED flows
curl "http://localhost:1880/flows" > backups/$(date +%Y%m%d)/flows.json

# Backup Redis data
docker-compose exec redis redis-cli SAVE
cp data/redis/dump.rdb backups/$(date +%Y%m%d)/

# Backup configuration
cp .env backups/$(date +%Y%m%d)/
cp -r config/ backups/$(date +%Y%m%d)/
```

#### Storage Cleanup
```bash
# Clean old emails (if using custom retention)
curl -X POST "http://localhost:1880/api/email/cleanup?older_than=90days"

# Clean Docker system
docker system prune -f

# Clean old logs
docker-compose logs --since="24h" > /tmp/recent.log
```

### Security Configuration

#### Network Security
```bash
# Bind services to localhost only (production)
NODE_RED_HOST=127.0.0.1
GRAFANA_HOST=127.0.0.1
```

#### Access Control
```bash
# Node-RED security
NODERED_ADMIN_USER=admin
NODERED_ADMIN_PASSWORD=strong-password-here
NODE_RED_CREDENTIAL_SECRET=your-secret-key

# Grafana security
GF_SECURITY_ADMIN_USER=admin
GF_SECURITY_ADMIN_PASSWORD=strong-password-here
```

#### Email Security
```bash
# OAuth2 for email (more secure than password)
EMAIL_AUTH_TYPE=oauth2
EMAIL_OAUTH_CLIENT_ID=your-client-id
EMAIL_OAUTH_CLIENT_SECRET=your-client-secret
EMAIL_OAUTH_REFRESH_TOKEN=your-refresh-token
EMAIL_OAUTH_ACCESS_TOKEN=your-access-token
EMAIL_OAUTH_EXPIRES=1234567890
```

### Monitoring Setup

#### Health Checks
```bash
# Node-RED status
curl "http://localhost:1880/status"

# Prometheus targets
curl "http://localhost:9090/api/v1/targets"

# Redis ping
docker-compose exec redis redis-cli PING
```

#### Performance Metrics
```bash
# Email processing stats
curl "http://localhost:1880/api/email/stats"

# System metrics
curl "http://localhost:9090/api/v1/query?query=up"

# Email classification distribution
curl "http://localhost:9090/api/v1/query?query=email_classification_count"
```

### Troubleshooting

#### Common Issues

**Node-RED won't start**
```bash
# Check disk space
df -h

# Check memory
free -h

# Fix permissions
sudo chown -R 1000:1000 data/node-red/
```

**Email connection issues**
```bash
# Test email server connectivity
nc -zv $EMAIL_SERVER $EMAIL_PORT

# Check credentials
echo $EMAIL_USER
echo $EMAIL_PASS | grep -o ".\{3\}$" # Show only last 3 chars for security

# Check connection logs
docker-compose logs node-red | grep "Email connection"
```

**Ollama model issues**
```bash
# Check available models
curl "http://localhost:11435/api/tags"

# Pull model again
curl -X POST "http://localhost:11435/api/pull" \
  -H "Content-Type: application/json" \
  -d '{"name": "llama2:7b"}'

# Check Ollama logs
docker-compose logs ollama
```

#### Log Analysis
```bash
# Find errors in all services
docker-compose logs | grep -i error

# Check memory issues
docker-compose logs | grep -i "out of memory"

# Monitor real-time logs
docker-compose logs -f | grep -E "(ERROR|WARN|FATAL)"
```

### Advanced Configuration

#### Custom Email Classification

Modify the classification thresholds in `.env`:
```bash
# Classification confidence thresholds
CLASSIFICATION_THRESHOLD_URGENT=0.8
CLASSIFICATION_THRESHOLD_BUSINESS=0.6
CLASSIFICATION_THRESHOLD_PERSONAL=0.7
CLASSIFICATION_THRESHOLD_SPAM=0.9
```

#### Auto-Reply Templates

Auto-reply templates are stored in Node-RED flows. To modify:
1. Open Node-RED: `http://localhost:1880`
2. Navigate to the "Auto-Reply" flow
3. Edit the template nodes for each classification
4. Deploy changes

#### Scaling for High Volume

For environments with high email volume:
```bash
# In docker-compose.yml
services:
  node-red:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
  redis:
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 1G

# In .env
EMAIL_BATCH_SIZE=100
EMAIL_PROCESSING_THREADS=8
```

### System Updates

#### Updating Services
```bash
# Pull latest images
docker-compose pull

# Update specific service
docker-compose pull node-red
docker-compose up -d --no-deps node-red

# Full system update
git pull
docker-compose down
docker-compose pull
docker-compose up -d
```

#### Version Management
```bash
# Check current versions
docker-compose exec node-red npm list
docker-compose exec ollama ollama --version

# Pin specific versions in docker-compose.yml
services:
  node-red:
    image: nodered/node-red:3.0.2
  ollama:
    image: ollama/ollama:0.1.17
```

### Disaster Recovery

#### Complete Backup
```bash
# Stop services
docker-compose down

# Backup all data
tar -czf hubmail-backup-$(date +%Y%m%d).tar.gz \
  data/ .env docker-compose.yml config/

# Restart services
docker-compose up -d
```

#### Restore from Backup
```bash
# Stop services
docker-compose down

# Extract backup
tar -xzf hubmail-backup-20240101.tar.gz

# Restart services
docker-compose up -d
```

#### Emergency Procedures
```bash
# If Node-RED is corrupted
mv data/node-red/flows.json data/node-red/flows.json.bad
cp backups/latest/flows.json data/node-red/
docker-compose restart node-red

# If Redis data is corrupted
docker-compose stop redis
rm data/redis/dump.rdb
cp backups/latest/dump.rdb data/redis/
docker-compose start redis
```

### Monitoring Alerts

#### Grafana Alert Setup
1. Open Grafana: `http://localhost:3000`
2. Navigate to Alerting > Alert rules
3. Create rules for:
   - Email processing errors
   - Service downtime
   - High CPU/memory usage
   - Urgent email processing delays

#### Notification Channels
```bash
# Slack webhook in .env
WEBHOOK_URL=https://hooks.slack.com/services/your-webhook-url
WEBHOOK_ENABLED=true
WEBHOOK_CHANNEL=#email-alerts

# Email notifications in Grafana
GF_SMTP_ENABLED=true
GF_SMTP_HOST=smtp.example.com:587
GF_SMTP_USER=alerts@example.com
GF_SMTP_PASSWORD=your-password
```

### Maintenance Schedule

#### Recommended Routine
- **Daily**: Check logs, email processing stats
- **Weekly**: Backup flows and data, update models
- **Monthly**: System updates, performance review
- **Quarterly**: Full backup, security audit

#### Automated Maintenance
Add to crontab:
```bash
# Daily log rotation
0 0 * * * find /path/to/hubmail/logs -name "*.log" -mtime +7 -delete

# Weekly backup
0 0 * * 0 cd /path/to/hubmail && ./scripts/backup.sh

# Monthly system update
0 0 1 * * cd /path/to/hubmail && ./scripts/update.sh