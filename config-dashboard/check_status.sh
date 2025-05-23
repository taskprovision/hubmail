#!/bin/bash
# Enhanced script to check the status of all containers

# Set colors for output
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
RED="\033[0;31m"
NC="\033[0m" # No Color

echo -e "${YELLOW}===== HubMail Container Status =====${NC}"
echo 

# Check if docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Error: Docker is not running or you don't have permission to access it.${NC}"
    exit 1
fi

# Get all containers (including stopped ones)
containers=$(docker ps -a --format "{{.Names}}|{{.Status}}|{{.Image}}|{{.Ports}}|{{.RunningFor}}|{{.ID}}")

if [ -z "$containers" ]; then
    echo -e "${YELLOW}No containers found.${NC}"
    exit 0
fi

# Print header
printf "%-25s %-15s %-30s %-10s\n" "CONTAINER NAME" "STATUS" "IMAGE" "UPTIME"
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
    printf "%-25s ${status_color}%-15s${NC} %-30s %-10s\n" "$name" "$status_text" "${image:0:30}" "$uptime"
done

echo 

# Show resource usage
echo -e "${YELLOW}===== Resource Usage =====${NC}"
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"

echo 
echo -e "${YELLOW}For more details, run: docker ps -a${NC}"
