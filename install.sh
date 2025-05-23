#!/bin/bash
set -e

echo "🚀 Installing Email Intelligence Hub..."

# Check requirements
command -v docker >/dev/null 2>&1 || { echo "Docker required but not installed. Aborting." >&2; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo "Docker Compose required but not installed. Aborting." >&2; exit 1; }

# Create directories
mkdir -p {config/{prometheus,grafana/{datasources,dashboards},node-red,ollama},data/{prometheus,grafana,node-red,ollama},scripts}

# Copy example env file
if [ ! -f .env ]; then
    cp .env.example .env
    echo "📝 Please edit .env file with your email credentials"
fi

# Set permissions
chmod 777 data/grafana
chmod 777 data/prometheus

echo "✅ Project structure created!"
echo "🔧 Starting services..."

docker-compose up -d

echo "⏳ Waiting for services to start..."
sleep 30

# Setup Ollama models
echo "🤖 Setting up AI models..."
docker-compose exec -T ollama ollama pull llama2:7b

# Import Grafana dashboard
echo "📊 Setting up monitoring dashboard..."
./scripts/setup.sh

echo "✅ Email Intelligence Hub is ready!"
echo ""
echo "🎉 Access your services:"
echo "   • Node-RED: http://localhost:1880"
echo "   • Grafana: http://localhost:3000 (admin/admin)"
echo "   • Prometheus: http://localhost:9090"
echo ""
echo "🧪 Test the system: ./scripts/test-flow.sh"