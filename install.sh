#!/bin/bash
set -e

echo "🚀 Installing HubMail - Email Automation System..."

# Check requirements
command -v docker >/dev/null 2>&1 || { echo "Docker required but not installed. Aborting." >&2; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo "Docker Compose required but not installed. Aborting." >&2; exit 1; }

# Create directories with proper permissions
echo "📁 Creating project structure..."
mkdir -p config/{prometheus,grafana/{datasources,dashboards},node-red}
mkdir -p data/{prometheus,grafana,node-red,ollama,redis}

# Set ownership of data directories to current user
echo "🔑 Setting up permissions (may require sudo)..."
if [ -w /usr/bin/sudo ]; then
    sudo chown -R ${DOCKER_UID:-1000}:${DOCKER_GID:-1000} data/ 2>/dev/null || true
else
    chown -R ${DOCKER_UID:-1000}:${DOCKER_GID:-1000} data/ 2>/dev/null || true
fi

# Set directory permissions
chmod 775 data/grafana 2>/dev/null || true
chmod 775 data/prometheus 2>/dev/null || true
chmod 775 data/redis 2>/dev/null || true

# Copy example env file if it doesn't exist
if [ ! -f .env ]; then
    cp .env.example .env
    echo "📝 Please edit .env file with your email credentials"
    echo "   You can use: nano .env"
    exit 1
fi

# Load environment variables safely
echo "🔍 Loading environment variables..."
if [ -f .env ]; then
    # Create a clean temporary file with only valid variable assignments
    grep -v '^[[:space:]]*$' .env | grep -v '^[[:space:]]*#' | \
    grep -E '^[a-zA-Z_][a-zA-Z0-9_]*=' > .env.clean
    
    # Source the clean environment file
    while IFS= read -r line; do
        # Export each variable individually
        export "$line" 2>/dev/null || echo "Skipping problematic line: $line"
    done < .env.clean
    
    rm -f .env.clean
else
    echo "⚠️  Warning: .env file not found. Using default values."
fi

echo "✅ Project structure created!"

echo "🔧 Starting services..."

# Start the services
docker-compose up -d

echo "⏳ Waiting for services to start..."
sleep 10

# Setup Ollama models if OLLAMA_ENABLED is true
if [ "${OLLAMA_ENABLED:-true}" = "true" ]; then
    echo "🤖 Setting up AI models..."
    docker-compose exec -T ollama ollama pull ${LLM_MODEL:-llama2:7b} || \
        echo "⚠️  Warning: Failed to pull Ollama model. Continuing anyway..."
else
    echo "ℹ️  Ollama setup skipped (OLLAMA_ENABLED=false)"
fi

# Setup Grafana if ENABLE_GRAFANA is true
if [ "${ENABLE_GRAFANA:-true}" = "true" ]; then
    echo "📊 Setting up monitoring dashboard..."
    if [ -f "scripts/setup.sh" ]; then
        chmod +x scripts/setup.sh
        ./scripts/setup.sh || \
            echo "⚠️  Warning: Failed to setup Grafana dashboard. Continuing anyway..."
    else
        echo "ℹ️  Grafana setup script not found. Skipping..."
    fi
else
    echo "ℹ️  Grafana setup skipped (ENABLE_GRAFANA=false)"
fi

echo ""
echo "✅ HubMail Email Automation System is ready!"
echo ""
echo "🎉 Access your services:"
echo "   • Dashboard: http://localhost:${UI_PORT:-8501}"
echo "   • API: http://localhost:${API_PORT:-3001}"
echo "   • Grafana: http://localhost:${GRAFANA_PORT:-3000} (admin/${GRAFANA_ADMIN_PASSWORD:-admin})"
echo "   • Prometheus: http://localhost:${PROMETHEUS_PORT:-9090}"
echo ""
echo "🧪 Test the system: make test"
echo "📜 View logs: make logs"
echo "🔍 Open dashboard: make ui"