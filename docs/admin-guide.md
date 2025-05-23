# DocPro - Administrator Guide

## System Administration

### Docker Management

#### Service Status
```bash
# Check all services
docker-compose ps

# Check specific service
docker-compose ps elasticsearch

# View resource usage
docker stats
```

#### Logs Management
```bash
# View all logs
docker-compose logs

# Follow specific service logs
docker-compose logs -f node-red
docker-compose logs -f elasticsearch

# Last 100 lines
docker-compose logs --tail=100 kibana
```

#### Service Control
```bash
# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart elasticsearch

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
ELASTICSEARCH_HTTP_PORT=9200
KIBANA_PORT=5601
NODE_RED_PORT=1880
MINIO_CONSOLE_PORT=9001
TIKA_PORT=9998
OLLAMA_PORT=11437

# AI settings
LLM_MODEL=llama2:13b
CONFIDENCE_THRESHOLD=0.8

# Processing limits
MAX_DOCUMENT_SIZE=50MB
PROCESSING_THREADS=4
```

#### Performance Tuning
```bash
# Elasticsearch memory
ES_JAVA_OPTS=-Xms2g -Xmx2g

# Enable swap if needed
sudo swapon /swapfile
```

### Data Management

#### Backup Strategy
```bash
# Create backup directory
mkdir -p backups/$(date +%Y%m%d)

# Backup Elasticsearch data
docker-compose exec elasticsearch curl -X PUT "localhost:9200/_snapshot/backup"

# Backup MinIO data
tar -czf backups/minio-$(date +%Y%m%d).tar.gz data/minio/

# Backup configuration
cp .env backups/
cp -r config/ backups/
```

#### Storage Cleanup
```bash
# Clean old Elasticsearch indices
curl -X DELETE "localhost:9200/documents-$(date -d '30 days ago' +%Y.%m.%d)"

# Clean Docker system
docker system prune -f

# Clean old logs
docker-compose logs --since="24h" > /tmp/recent.log
```

### Security Configuration

#### Network Security
```bash
# Bind services to localhost only (production)
ELASTICSEARCH_HOST=127.0.0.1
KIBANA_HOST=127.0.0.1
```

#### Access Control
```bash
# MinIO access
MINIO_ROOT_USER=admin
MINIO_ROOT_PASSWORD=strong-password-here

# Node-RED security
NODE_RED_CREDENTIAL_SECRET=your-secret-key
```

### Monitoring Setup

#### Health Checks
```bash
# Elasticsearch cluster health
curl "localhost:9200/_cluster/health?pretty"

# Kibana status
curl "localhost:5601/api/status"

# MinIO health
curl "localhost:9000/minio/health/live"
```

#### Performance Metrics
```bash
# Elasticsearch stats
curl "localhost:9200/_stats?pretty"

# Node stats
curl "localhost:9200/_nodes/stats?pretty"

# Document count
curl "localhost:9200/documents/_count"
```

### Troubleshooting

#### Common Issues

**Elasticsearch won't start**
```bash
# Check disk space
df -h

# Check memory
free -h

# Fix permissions
sudo chown -R 1000:1000 data/elasticsearch/
```

**MinIO access denied**
```bash
# Reset MinIO
docker-compose restart minio

# Check credentials
echo $MINIO_ROOT_USER
echo $MINIO_ROOT_PASSWORD
```

**Node-RED flows not working**
```bash
# Check Node-RED logs
docker-compose logs node-red

# Restart Node-RED
docker-compose restart node-red

# Check flows file
ls -la data/node-red/
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

### Maintenance Tasks

#### Daily Tasks
- Check service status
- Monitor disk usage
- Review error logs
- Verify backup completion

#### Weekly Tasks
- Clean old indices
- Update documentation
- Review performance metrics
- Test disaster recovery

#### Monthly Tasks
- Security updates
- Configuration review
- Capacity planning
- User access audit