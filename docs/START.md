# DocPro - Quick Start Guide

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
# Clone or download DocPro
git clone https://github.com/your-org/docpro.git
cd docpro

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
curl http://localhost:9200  # Elasticsearch
curl http://localhost:5601  # Kibana
curl http://localhost:1880  # Node-RED Dashboard
```

### 5. Test Document Processing
```bash
# Upload test document
echo "Test invoice document" > data/input/test.txt

# Check processing (wait 30 seconds)
curl "http://localhost:9200/documents/_search?q=test"
```

## Access Points

| Service | URL | Purpose |
|---------|-----|---------|
| **Main Dashboard** | http://localhost:1880 | Document processing workflows |
| **Analytics** | http://localhost:5601 | Search and visualize documents |
| **Storage** | http://localhost:9001 | File management (minioadmin/minioadmin123) |
| **Search API** | http://localhost:9200 | Direct Elasticsearch access |

## First Steps

### Upload Documents
```bash
# Method 1: File system (easiest)
cp your-document.pdf data/input/

# Method 2: MinIO console
# Open http://localhost:9001
# Login: minioadmin / minioadmin123
# Upload to 'documents' bucket
```

### View Results
```bash
# Search processed documents
curl "http://localhost:9200/documents/_search?pretty"

# Or use Kibana dashboard
# Open http://localhost:5601
# Go to Discover
# Select 'documents' index
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
docker-compose restart elasticsearch

# Reset everything (CAUTION: loses data)
docker-compose down -v
sudo rm -rf data/*
docker-compose up -d
```

### Health Check
```bash
# Quick health check
for port in 9200 5601 1880 9001 9998 11437; do
  curl -s http://localhost:$port > /dev/null && echo "Port $port: OK" || echo "Port $port: FAIL"
done
```

## Document Types Supported

- **PDFs**: Automatic text extraction
- **Word Documents**: .docx, .doc
- **Images**: .png, .jpg, .jpeg, .tiff (with OCR)
- **Text Files**: .txt, .rtf
- **OpenDocument**: .odt

## Basic Usage Examples

### Search Documents
```bash
# Find all invoices
curl "http://localhost:9200/documents/_search?q=document_type:INVOICE"

# Find documents from last week
curl "http://localhost:9200/documents/_search" -d '
{
  "query": {
    "range": {
      "processing_timestamp": {
        "gte": "now-7d"
      }
    }
  }
}'
```

### Process Specific Document
```bash
# Upload and wait for processing
cp important-contract.pdf data/input/
sleep 30

# Check processing result
curl "http://localhost:9200/documents/_search?q=filename:important-contract.pdf"
```

### View Analytics
1. Open Kibana: http://localhost:5601
2. Go to "Discover"
3. Select "documents*" index pattern
4. Explore your processed documents

## Configuration Quick Reference

### Key Ports (from .env)
```bash
ELASTICSEARCH_HTTP_PORT=9200
KIBANA_PORT=5601
NODE_RED_PORT=1880
MINIO_CONSOLE_PORT=9001
TIKA_PORT=9998
OLLAMA_PORT=11437
```

### Important Directories
```bash
data/input/          # Drop files here for processing
data/processed/      # Processed files output
data/elasticsearch/  # Search index data
data/minio/         # Object storage data
```

### AI Configuration
```bash
LLM_MODEL=llama2:13b         # AI model for analysis
CONFIDENCE_THRESHOLD=0.8     # Minimum confidence for results
MAX_DOCUMENT_SIZE=50MB       # Maximum file size
```

## Next Steps

1. **Read Full Documentation**
   - [INSTALLATION.md](INSTALLATION.md) - Complete setup guide
   - [USER-GUIDE.md](USER-GUIDE.md) - Detailed usage instructions
   - [API-REFERENCE.md](API-REFERENCE.md) - API documentation

2. **Customize Workflows**
   - Open Node-RED: http://localhost:1880
   - Create custom document processing flows
   - Add email/Slack notifications

3. **Set Up Monitoring**
   - Configure Kibana dashboards
   - Set up automated alerts
   - Create custom reports

4. **Security & Production**
   - Change default passwords
   - Enable SSL/TLS
   - Set up backups

## Troubleshooting Quick Fixes

### Service Won't Start
```bash
# Check ports
sudo netstat -tulpn | grep -E "(9200|5601|1880)"

# Check memory
free -h

# Restart Docker
sudo systemctl restart docker
docker-compose up -d
```

### No Documents Processing
```bash
# Check input directory
ls -la data/input/

# Check Node-RED flow
open http://localhost:1880

# Check logs
docker-compose logs node-red | grep -i error
```

### Can't Access Services
```bash
# Check if services are running
docker-compose ps

# Test connectivity
curl http://localhost:9200/_cluster/health
curl http://localhost:1880

# Restart if needed
docker-compose restart
```

## Getting Help

- **System Status**: Check http://localhost:1880 dashboard
- **Logs**: `docker-compose logs [service-name]`
- **Documentation**: See other .md files in docs/
- **Issues**: Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

**🎉 You're ready to start processing documents with DocPro!**

Drop a PDF in `data/input/` and watch it get processed automatically.