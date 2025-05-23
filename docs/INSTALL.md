# DocPro - Installation Guide

## System Requirements

### Hardware Requirements
- **CPU**: 4+ cores recommended
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 50GB free disk space
- **Network**: Internet connection for Docker images

### Software Requirements
- **Docker**: Version 20.0+ 
- **Docker Compose**: Version 2.0+
- **Operating System**: Linux, macOS, or Windows with WSL2
- **Python**: 3.8+ (for documentation generator)

## Pre-Installation

### 1. Install Docker
```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# macOS (with Homebrew)
brew install --cask docker

# Windows
# Download Docker Desktop from docker.com
```

### 2. Install Docker Compose
```bash
# Linux
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker --version
docker-compose --version
```

### 3. System Configuration
```bash
# Linux: Increase memory map limit for Elasticsearch
echo "vm.max_map_count=262144" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p

# Check available memory
free -h
```

## Installation Steps

### 1. Download DocPro
```bash
# Clone repository
git clone https://github.com/your-org/docpro.git
cd docpro

# Or download and extract zip
wget https://github.com/your-org/docpro/archive/main.zip
unzip main.zip
cd docpro-main
```

### 2. Configuration Setup
```bash
# Copy environment template
cp .env.example .env

# Edit configuration
nano .env
```

### 3. Key Configuration Settings

#### Port Configuration
```bash
# Adjust ports if conflicts exist
ELASTICSEARCH_HTTP_PORT=9200
KIBANA_PORT=5601
NODE_RED_PORT=1880
MINIO_CONSOLE_PORT=9001
TIKA_PORT=9998
OLLAMA_PORT=11437
```

#### Storage Configuration
```bash
# MinIO credentials
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin123

# Document processing
MAX_DOCUMENT_SIZE=50MB
SUPPORTED_FORMATS=pdf,docx,png,jpg,jpeg,tiff
```

#### AI Configuration
```bash
# AI model settings
LLM_MODEL=llama2:13b
LLM_TEMPERATURE=0.1
CONFIDENCE_THRESHOLD=0.8
```

### 4. Directory Structure Setup
```bash
# Create required directories
mkdir -p data/{elasticsearch,minio,node-red,ollama,input,processed}
mkdir -p config docs web

# Set permissions
chmod 755 data/input
chmod 777 data/elasticsearch  # Required for Elasticsearch
```

### 5. Start Services
```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View startup logs
docker-compose logs -f
```

### 6. Wait for Services
```bash
# Wait for Elasticsearch (important!)
echo "Waiting for Elasticsearch..."
until curl -f http://localhost:9200/_cluster/health; do
  echo "Still waiting..."
  sleep 10
done

# Wait for all services
sleep 60
```

### 7. Initialize System
```bash
# Create Elasticsearch indices
curl -X PUT "localhost:9200/documents" -H 'Content-Type: application/json' -d'
{
  "mappings": {
    "properties": {
      "filename": {"type": "keyword"},
      "document_type": {"type": "keyword"},
      "content": {"type": "text"},
      "timestamp": {"type": "date"}
    }
  }
}'

# Download AI models
docker-compose exec ollama ollama pull llama2:7b
```

### 8. Generate Documentation
```bash
# Install Python requirements
pip3 install requests

# Generate dashboard
python3 docs/generate-dashboard.py --output web/

# Open dashboard
open web/index.html
```

## Verification

### 1. Service Health Check
```bash
# Check all ports
for port in 9200 5601 1880 9001 9998 11437; do
  if curl -s http://localhost:$port > /dev/null; then
    echo "Port $port: ✅ OK"
  else
    echo "Port $port: ❌ FAIL"
  fi
done
```

### 2. Test Document Processing
```bash
# Create test document
echo "This is a test invoice document" > data/input/test-invoice.txt

# Wait for processing
sleep 30

# Check if processed
curl "http://localhost:9200/documents/_search?q=test"
```

### 3. Access Services
- **Dashboard**: http://localhost:1880
- **Kibana**: http://localhost:5601
- **MinIO Console**: http://localhost:9001 (minioadmin/minioadmin123)
- **Elasticsearch**: http://localhost:9200

## Post-Installation

### 1. Security Configuration
```bash
# Change default passwords
MINIO_ROOT_PASSWORD=your-secure-password

# Enable authentication if needed
NODE_RED_CREDENTIAL_SECRET=your-secret-key
```

### 2. Backup Setup
```bash
# Create backup script
cat > backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d)
mkdir -p backups/$DATE
tar -czf backups/$DATE/docpro-data.tar.gz data/
cp .env backups/$DATE/
EOF

chmod +x backup.sh
```

### 3. Monitoring Setup
```bash
# Add to crontab for daily backup
echo "0 2 * * * /path/to/docpro/backup.sh" | crontab -
```

## Customization

### 1. Node-RED Flows
1. Open http://localhost:1880
2. Import custom flows from `config/node-red/`
3. Configure email/Slack notifications
4. Deploy changes

### 2. AI Models
```bash
# Download additional models
docker-compose exec ollama ollama pull mistral:7b
docker-compose exec ollama ollama pull codellama:7b

# List available models
docker-compose exec ollama ollama list
```

### 3. Elasticsearch Templates
```bash
# Create document template
curl -X PUT "localhost:9200/_template/documents" -H 'Content-Type: application/json' -d'
{
  "index_patterns": ["documents*"],
  "settings": {
    "number_of_shards": 1,
    "number_of_replicas": 0
  }
}'
```

## Troubleshooting Installation

### Common Issues

#### Port Conflicts
```bash
# Check what's using ports
sudo netstat -tulpn | grep 9200

# Change ports in .env
ELASTICSEARCH_HTTP_PORT=9201
```

#### Memory Issues
```bash
# Check available memory
free -h

# Reduce Elasticsearch memory
ES_JAVA_OPTS=-Xms512m -Xmx1g
```

#### Permission Errors
```bash
# Fix Elasticsearch permissions
sudo chown -R 1000:1000 data/elasticsearch/

# Fix general permissions
sudo chown -R $USER:$USER data/
```

### Docker Issues
```bash
# Clean Docker system
docker system prune -f

# Restart Docker service
sudo systemctl restart docker

# Check Docker logs
sudo journalctl -u docker.service
```

### Network Issues
```bash
# Restart with fresh network
docker-compose down
docker network prune -f
docker-compose up -d
```

## Uninstallation

### Complete Removal
```bash
# Stop all services
docker-compose down -v

# Remove data (CAUTION: Irreversible)
sudo rm -rf data/

# Remove Docker images
docker rmi $(docker images -q)
```
