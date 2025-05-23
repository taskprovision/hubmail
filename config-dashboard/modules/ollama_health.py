#!/usr/bin/env python3
# Fix for Ollama health check in the dashboard

import streamlit as st
import subprocess
import json
from datetime import datetime

def check_ollama_health(container_name="email-ollama", port="11434"):
    """Check the health of the Ollama service"""
    try:
        # First check if the container is running
        result = subprocess.run(
            ['docker', 'ps', '--filter', f'name={container_name}', '--format', '{{.Status}}'],
            capture_output=True,
            text=True
        )
        
        if not result.stdout.strip():
            return {
                "status": "stopped",
                "health_status": "Container not running",
                "error": f"Container '{container_name}' not found or not running."
            }
        
        # Check if the container is healthy
        if "Up" in result.stdout and "(healthy)" not in result.stdout and "(unhealthy)" not in result.stdout:
            # Container is running but no health check defined
            # Try to connect to the Ollama API
            try:
                # Use curl to check if the API is responding
                api_check = subprocess.run(
                    ['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', f'http://localhost:{port}'],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                
                if api_check.stdout.strip() == "200":
                    return {
                        "status": "running",
                        "health_status": "healthy",
                        "message": "Ollama API is responding"
                    }
                else:
                    return {
                        "status": "running",
                        "health_status": "unhealthy",
                        "error": f"Ollama API returned status code: {api_check.stdout.strip()}"
                    }
            except Exception as e:
                return {
                    "status": "running",
                    "health_status": "unhealthy",
                    "error": f"Failed to connect to Ollama API: {str(e)}"
                }
        elif "(healthy)" in result.stdout:
            return {
                "status": "running",
                "health_status": "healthy",
                "message": "Container health check passed"
            }
        elif "(unhealthy)" in result.stdout:
            return {
                "status": "running",
                "health_status": "unhealthy",
                "error": "Container health check failed"
            }
        else:
            return {
                "status": "unknown",
                "health_status": "unknown",
                "error": f"Unexpected container status: {result.stdout.strip()}"
            }
    except Exception as e:
        return {
            "status": "unknown",
            "health_status": "unknown",
            "error": f"Error checking Ollama health: {str(e)}"
        }

# Print instructions
print("""
OLLAMA HEALTH CHECK FIX INSTRUCTIONS:

1. Copy this file to the Docker container:
   docker cp fix_ollama_health.py email-config-dashboard:/app/modules/ollama_health.py

2. Modify the service_status.py file in the container to use this health check:
   docker exec -it email-config-dashboard bash -c "echo 'from modules.ollama_health import check_ollama_health' >> /app/modules/service_status.py"

3. Update the check_service_status function to use the Ollama-specific health check:
   docker exec -it email-config-dashboard bash -c "sed -i '/def check_service_status/,/return status/ s/if container_name == \"email-ollama\":/if container_name == \"email-ollama\":\\n        ollama_health = check_ollama_health(container_name)\\n        status.update(ollama_health)\\n        return status\\n    elif False:/' /app/modules/service_status.py"

4. Restart the container:
   docker restart email-config-dashboard

This should fix the Ollama health check issue.
""")
