#!/bin/bash

# DocPro Dashboard Setup Script
set -e

echo "🚀 Setting up DocPro Dashboard..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check requirements
check_requirements() {
    echo -e "\n${BLUE}🔍 Checking requirements...${NC}"

    # Check Python
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python 3 is required but not installed${NC}"
        exit 1
    fi

    # Check pip
    if ! command -v pip3 &> /dev/null; then
        echo -e "${RED}❌ pip3 is required but not installed${NC}"
        exit 1
    fi

    echo -e "${GREEN}✅ Python and pip are available${NC}"
}

# Create directory structure
create_structure() {
    echo -e "\n${BLUE}📁 Creating directory structure...${NC}"

    mkdir -p templates
    mkdir -p static/{css,js,images}

    echo -e "${GREEN}✅ Directory structure created${NC}"
}

# Install Python dependencies
install_dependencies() {
    echo -e "\n${BLUE}📦 Installing Python dependencies...${NC}"

    pip3 install -r requirements.txt

    echo -e "${GREEN}✅ Dependencies installed${NC}"
}

# Setup configuration
setup_config() {
    echo -e "\n${BLUE}⚙️ Setting up configuration...${NC}"

    # Add dashboard port to .env if not exists
    if ! grep -q "DASHBOARD_PORT" .env 2>/dev/null; then
        echo "" >> .env
        echo "# Dashboard Configuration" >> .env
        echo "DASHBOARD_PORT=8000" >> .env
        echo "DASHBOARD_HOST=0.0.0.0" >> .env
    fi

    echo -e "${GREEN}✅ Configuration updated${NC}"
}

# Start dashboard
start_dashboard() {
    echo -e "\n${BLUE}🚀 Starting dashboard...${NC}"

    # Option 1: Start as standalone Python app
    if [[ "$1" == "standalone" ]]; then
        echo -e "${YELLOW}Starting dashboard in standalone mode...${NC}"
        python3 app.py &
        DASHBOARD_PID=$!
        echo $DASHBOARD_PID > dashboard.pid

        sleep 3

        if kill -0 $DASHBOARD_PID 2>/dev/null; then
            echo -e "${GREEN}✅ Dashboard started successfully (PID: $DASHBOARD_PID)${NC}"
        else
            echo -e "${RED}❌ Dashboard failed to start${NC}"
            exit 1
        fi

    # Option 2: Start as Docker service
    elif [[ "$1" == "docker" ]]; then
        echo -e "${YELLOW}Starting dashboard as Docker service...${NC}"
        docker-compose -f docker-compose.dashboard.yml up -d

        echo -e "${GREEN}✅ Dashboard container started${NC}"

    # Option 3: Add to main docker-compose
    else
        echo -e "${YELLOW}Adding dashboard to main docker-compose...${NC}"

        # Check if dashboard service already exists in docker-compose.yml
        if grep -q "dashboard:" docker-compose.yml; then
            echo -e "${YELLOW}⚠️ Dashboard service already exists in docker-compose.yml${NC}"
        else
            # Add dashboard service to existing docker-compose.yml
            cat >> docker-compose.yml << 'EOF'

  # DocPro Dashboard
  dashboard:
    build:
      context: .
      dockerfile: Dockerfile.dashboard
    container_name: docpro-dashboard
    restart: unless-stopped
    ports:
      - "${DASHBOARD_PORT:-8000}:8000"
    volumes:
      - ./.env:/app/.env:ro
      - ./docker-compose.yml:/app/docker-compose.yml:ro
      - ./templates:/app/templates:ro
      - ./static:/app/static:ro
    environment:
      - DASHBOARD_HOST=0.0.0.0
      - DASHBOARD_PORT=8000
    networks:
      - ${NETWORK_NAME:-doc-net}
    depends_on:
      - elasticsearch
      - kibana
      - node-red
      - minio
EOF
            echo -e "${GREEN}✅ Dashboard service added to docker-compose.yml${NC}"
        fi

        # Restart docker-compose with dashboard
        docker-compose up -d dashboard

        echo -e "${GREEN}✅ Dashboard started with docker-compose${NC}"
    fi
}

# Test dashboard
test_dashboard() {
    echo -e "\n${BLUE}🧪 Testing dashboard...${NC}"

    local port=${DASHBOARD_PORT:-8000}
    local max_attempts=30
    local attempt=1

    while [ $attempt -le $max_attempts ]; do
        if curl -s http://localhost:$port/api/services > /dev/null; then
            echo -e "${GREEN}✅ Dashboard is responding on port $port${NC}"
            break
        else
            echo -e "${YELLOW}Waiting for dashboard... (attempt $attempt/$max_attempts)${NC}"
            sleep 2
            ((attempt++))
        fi
    done

    if [ $attempt -gt $max_attempts ]; then
        echo -e "${RED}❌ Dashboard failed to respond after ${max_attempts} attempts${NC}"
        exit 1
    fi
}

# Show access information
show_access_info() {
    echo -e "\n${GREEN}🎉 Dashboard setup complete!${NC}"
    echo -e "\n${BLUE}📊 Access Information:${NC}"
    echo -e "   • Dashboard URL: ${GREEN}http://localhost:${DASHBOARD_PORT:-8000}${NC}"
    echo -e "   • API Endpoint: ${GREEN}http://localhost:${DASHBOARD_PORT:-8000}/api/services${NC}"
    echo -e "   • Health Check: ${GREEN}http://localhost:${DASHBOARD_PORT:-8000}/api/stats${NC}"

    echo -e "\n${BLUE}🔧 Management Commands:${NC}"

    if [[ "$1" == "standalone" ]]; then
        echo -e "   • Stop Dashboard: ${YELLOW}kill \$(cat dashboard.pid)${NC}"
        echo -e "   • View Logs: ${YELLOW}tail -f dashboard.log${NC}"
    elif [[ "$1" == "docker" ]]; then
        echo -e "   • Stop Dashboard: ${YELLOW}docker-compose -f docker-compose.dashboard.yml down${NC}"
        echo -e "   • View Logs: ${YELLOW}docker-compose -f docker-compose.dashboard.yml logs -f${NC}"
        echo -e "   • Restart: ${YELLOW}docker-compose -f docker-compose.dashboard.yml restart${NC}"
    else
        echo -e "   • Stop Dashboard: ${YELLOW}docker-compose stop dashboard${NC}"
        echo -e "   • View Logs: ${YELLOW}docker-compose logs -f dashboard${NC}"
        echo -e "   • Restart: ${YELLOW}docker-compose restart dashboard${NC}"
    fi

    echo -e "\n${BLUE}📱 Features:${NC}"
    echo -e "   • Real-time service monitoring"
    echo -e "   • Auto-refresh every 30 seconds"
    echo -e "   • Click service cards to open in new tab"
    echo -e "   • Ctrl+R to refresh manually"
    echo -e "   • Ctrl+I for system information"
    echo -e "   • Ctrl+Click service for health test"
}

# Cleanup function
cleanup() {
    echo -e "\n${YELLOW}🧹 Cleaning up...${NC}"

    if [[ -f dashboard.pid ]]; then
        PID=$(cat dashboard.pid)
        if kill -0 $PID 2>/dev/null; then
            kill $PID
            echo -e "${GREEN}✅ Dashboard process stopped${NC}"
        fi
        rm -f dashboard.pid
    fi
}

# Main function
main() {
    local mode=${1:-integrated}

    echo -e "${BLUE}📊 DocPro Dashboard Setup${NC}"
    echo -e "${BLUE}=========================${NC}"

    case $mode in
        "standalone")
            echo -e "${YELLOW}Mode: Standalone Python application${NC}"
            ;;
        "docker")
            echo -e "${YELLOW}Mode: Separate Docker container${NC}"
            ;;
        "integrated"|*)
            echo -e "${YELLOW}Mode: Integrated with main docker-compose${NC}"
            mode="integrated"
            ;;
    esac

    check_requirements
    create_structure
    install_dependencies
    setup_config
    start_dashboard $mode
    test_dashboard
    show_access_info $mode

    # Set up cleanup on script exit
    trap cleanup EXIT
}

# Help function
show_help() {
    echo "DocPro Dashboard Setup Script"
    echo ""
    echo "Usage: $0 [MODE]"
    echo ""
    echo "Modes:"
    echo "  standalone    - Run as standalone Python application"
    echo "  docker        - Run as separate Docker container"
    echo "  integrated    - Integrate with main docker-compose (default)"
    echo ""
    echo "Examples:"
    echo "  $0                    # Use integrated mode"
    echo "  $0 standalone        # Run standalone"
    echo "  $0 docker           # Use separate container"
    echo ""
}

# Parse command line arguments
case "${1:-}" in
    "-h"|"--help"|"help")
        show_help
        exit 0
        ;;
    *)
        main "$@"
        ;;
esac