# HubMail - Installation Guide

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
- **Python**: 3.8+ (for dashboard generator)

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

### 1. Download HubMail
```bash
# Clone repository
git clone https://github.com/taskprovision/hubmail.git
cd hubmail

# Or download and extract zip
wget https://github.com/taskprovision/hubmail/archive/main.zip
unzip main.zip
cd hubmail-main
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
NODERED_PORT=1880
OLLAMA_PORT=11435
PROMETHEUS_PORT=9090
GRAFANA_PORT=3000
REDIS_PORT=6379
```

#### Email Configuration
```bash
# Email server credentials
EMAIL_SERVER=imap.gmail.com
EMAIL_USER=your-email@gmail.com
EMAIL_PASS=your-app-password
EMAIL_PORT=993
EMAIL_SSL=true
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
mkdir -p data/{node-red,ollama,prometheus,grafana,redis}
mkdir -p config/{node-red,prometheus,grafana}

# Set permissions
chmod 755 data/node-red
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
# Wait for all services to start
echo "Waiting for services to start..."
sleep 30

# Check if Node-RED is running
curl -f http://localhost:1880
```

### 7. Initialize System
```bash
# Download AI models
docker-compose exec ollama ollama pull llama2:7b
```

### 8. Generate Dashboard
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
for port in 1880 11435 9090 3000 6379; do
  if curl -s http://localhost:$port > /dev/null; then
    echo "Port $port: OK"
  else
    echo "Port $port: FAIL"
  fi
done
```

### 2. Test Email Processing
```bash
# Send a test email to the configured account
# Wait for processing
sleep 30

# Check if processed in Node-RED
curl "http://localhost:1880/debug"
```

## Post-Installation

### 1. Configure Email Flows
1. Open Node-RED at http://localhost:1880
2. Import the email processing flows from `config/node-red/flows.json`
3. Deploy the flows

### 2. Configure Grafana Dashboard
1. Open Grafana at http://localhost:3000
2. Login with default credentials (admin/admin)
3. Navigate to Dashboards > Import
4. Import the dashboard from `config/grafana/dashboards/email-metrics.json`

### 3. Customize AI Models
```bash
# Download additional models
docker-compose exec ollama ollama pull mistral:7b
docker-compose exec ollama ollama pull codellama:7b
```

## Troubleshooting

### Common Issues

#### Email Connection Issues
```bash
# Check email server connectivity
nc -zv imap.gmail.com 993

# Verify credentials in .env
nano .env

# Restart Node-RED
docker-compose restart node-red
```

#### AI Model Issues
```bash
# Check Ollama service
docker-compose logs ollama

# List available models
docker-compose exec ollama ollama list

# Restart Ollama
docker-compose restart ollama
```

#### Dashboard Issues
```bash
# Check if all services are running
docker-compose ps

# Restart all services
docker-compose restart

# Regenerate dashboard
python3 docs/generate-dashboard.py --output web/
```

### Logs and Debugging

#### View Logs
```bash
# All services
docker-compose logs

# Specific service
docker-compose logs node-red
docker-compose logs ollama
```

#### Debug Mode
```bash
# Enable debug mode in .env
echo "LOG_LEVEL=debug" >> .env
docker-compose restart
```

## Maintenance

### Backup and Restore

#### Backup Configuration
```bash
# Create backup directory
mkdir -p backups/$(date +%Y-%m-%d)

# Backup configuration
cp -r config/* backups/$(date +%Y-%m-%d)/
cp .env backups/$(date +%Y-%m-%d)/
```

#### Backup Data
```bash
# Backup Node-RED flows
cp -r data/node-red backups/$(date +%Y-%m-%d)/

# Backup Grafana dashboards
cp -r data/grafana backups/$(date +%Y-%m-%d)/
```

#### Restore from Backup
```bash
# Restore configuration
cp -r backups/YYYY-MM-DD/* config/
cp backups/YYYY-MM-DD/.env .

# Restart services
docker-compose down
docker-compose up -d
```

### Updates

#### Update Docker Images
```bash
# Pull latest images
docker-compose pull

# Restart with new images
docker-compose down
docker-compose up -d
```

#### Update HubMail
```bash
# Pull latest code
git pull

# Apply changes
docker-compose down
docker-compose up -d
```

## Security Considerations

### Secure Email Access
- Use app-specific passwords for Gmail
- Consider using OAuth2 for more secure authentication
- Regularly rotate passwords

### Network Security
- Use a reverse proxy with HTTPS for external access
- Limit exposed ports with firewall rules
- Consider using Docker network isolation

### Data Protection
- Encrypt sensitive data in .env files
- Implement regular backups
- Consider data retention policies for email content

## Advanced Configuration

### Custom Email Classification Rules
Edit `config/node-red/flows.json` to modify the classification logic:

```json
{
  "id": "email-classifier",
  "type": "function",
  "name": "Classify Email",
  "func": "// Custom classification logic\nconst subject = msg.payload.subject;\nif (subject.includes('URGENT')) {\n    msg.classification = 'URGENT';\n} else if (subject.includes('SPAM')) {\n    msg.classification = 'SPAM';\n} else {\n    // Use AI for classification\n}\nreturn msg;"
}
```

### Custom AI Prompts
Edit the AI prompt templates in `config/node-red/settings.js`:

```javascript
emailClassificationPrompt: `
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
