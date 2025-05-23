#!/bin/bash
# Enhanced script to check the status of all containers

# Load environment variables from .env file if it exists
if [ -f ".env" ]; then
    source .env
fi

# Set default values if environment variables are not set
APP_NAME=${APP_NAME:-HubMail}
DOCKER_FORMAT=${DOCKER_FORMAT:-"{{.Names}}|{{.Status}}|{{.Image}}|{{.Ports}}|{{.RunningFor}}|{{.ID}}"}

# Set colors for output
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
RED="\033[0;31m"
NC="\033[0m" # No Color

echo -e "${YELLOW}===== ${APP_NAME} Container Status =====${NC}"
echo 

# Check if docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Error: Docker is not running or you don't have permission to access it.${NC}"
    exit 1
fi

# Get all containers (including stopped ones)
containers=$(docker ps -a --format "${DOCKER_FORMAT}")

if [ -z "$containers" ]; then
    echo -e "${YELLOW}No containers found.${NC}"
    exit 0
fi

# Set column widths from environment variables or use defaults
COL_NAME_WIDTH=${COL_NAME_WIDTH:-25}
COL_STATUS_WIDTH=${COL_STATUS_WIDTH:-15}
COL_IMAGE_WIDTH=${COL_IMAGE_WIDTH:-30}
COL_UPTIME_WIDTH=${COL_UPTIME_WIDTH:-10}

# Print header
printf "%-${COL_NAME_WIDTH}s %-${COL_STATUS_WIDTH}s %-${COL_IMAGE_WIDTH}s %-${COL_UPTIME_WIDTH}s\n" "CONTAINER NAME" "STATUS" "IMAGE" "UPTIME"
echo "--------------------------------------------------------------------------------------------"

# Process each container
echo "$containers" | while IFS='|' read -r name status image ports uptime id; do
    # Determine status color
    if [[ $status == *"Up"* && $status == *"healthy"* ]]; then
        status_color="$GREEN"
        status_text="HEALTHY"
    elif [[ $status == *"Up"* ]]; then
        status_color="$YELLOW"
        status_text="RUNNING"
    else
        status_color="$RED"
        status_text="STOPPED"
    fi
    
    # Format uptime
    uptime=$(echo "$uptime" | sed 's/About a/1/' | sed 's/About an/1/')
    
    # Print container info with color
    printf "%-${COL_NAME_WIDTH}s ${status_color}%-${COL_STATUS_WIDTH}s${NC} %-${COL_IMAGE_WIDTH}s %-${COL_UPTIME_WIDTH}s\n" "$name" "$status_text" "${image:0:$COL_IMAGE_WIDTH}" "$uptime"
done

echo 

# Show resource usage
# Set stats format from environment variable or use default
STATS_FORMAT=${STATS_FORMAT:-"table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"}

echo -e "${YELLOW}===== Resource Usage =====${NC}"
docker stats --no-stream --format "${STATS_FORMAT}"

echo 
echo -e "${YELLOW}For more details, run: ${DOCKER_CMD:-docker ps -a}${NC}"
