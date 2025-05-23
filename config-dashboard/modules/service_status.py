#!/usr/bin/env python3
# service_status.py - Service status checking functions

import json
import subprocess
import requests
import os
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import streamlit as st
from modules.docker_utils import get_container_ports

def check_service_status(service_name: str, service_config: Dict[str, Any]) -> Dict[str, Any]:
    """Check the status of a service based on its configuration"""
    # Get container name from service config or use service name as fallback
    container_name = service_config.get('container_name', service_name)
    
    # Get port mappings for this container
    port_mappings = get_container_ports(container_name)
    
    # Default status
    status = {
        "status": "unknown",
        "status_code": 0,
        "url": None,
        "port": None,
        "port_mappings": port_mappings,
        "last_checked": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "error": None,
        "container_name": container_name,
        "service_name": service_name
    }
    
    # Extract port mappings and set appropriate URLs for health checks
    try:
        # Run docker ps to check if container is running
        result = subprocess.run(
            ['docker', 'ps', '--format', '{{.Names}}\t{{.Ports}}', '--filter', f'name={container_name}'],
            capture_output=True,
            text=True,
            check=True
        )
        
        # If container is found in docker ps output
        if container_name in result.stdout:
            status["status"] = "running"
            status["status_code"] = 1
            
            # Extract port mappings
            for line in result.stdout.strip().split('\n'):
                if line.startswith(container_name):
                    parts = line.split('\t')
                    if len(parts) > 1:
                        ports_part = parts[1]
                        # Parse port mappings (e.g., "0.0.0.0:8080->80/tcp, :::8080->80/tcp")
                        for port_mapping in ports_part.split(', '):
                            if '->' in port_mapping:
                                host_part, container_part = port_mapping.split('->')
                                if ':' in host_part:
                                    host_ip, host_port = host_part.rsplit(':', 1)
                                    
                                    # Set the port information
                                    status["port"] = host_port
                                    
                                    # We'll use the port mappings from docker inspect for more accurate URLs
                                    break
        
        # Debug output
        # st.sidebar.write(f"Docker PS result for {container_name}: {result.stdout}")
        
        # Check if container is healthy
        health_result = subprocess.run(
            ['docker', 'inspect', '--format', '{{.State.Health.Status}}', container_name],
            capture_output=True,
            text=True
        )
        
        # If health check is available
        if health_result.returncode == 0 and health_result.stdout.strip():
            health_status = health_result.stdout.strip()
            if health_status == "healthy":
                status["status"] = "healthy"
                status["status_code"] = 2
            elif health_status == "unhealthy":
                status["status"] = "unhealthy"
                status["status_code"] = -1
        
        # If no health check but container is running, try to access the URL
        elif status["status_code"] == 1 and status["url"]:
            try:
                response = requests.get(status["url"], timeout=2)
                if response.status_code < 400:
                    status["status"] = "healthy"
                    status["status_code"] = 2
            except:
                # Keep as just running if we can't access the URL
                pass
    
    except subprocess.CalledProcessError as e:
        status["status"] = "error"
        status["status_code"] = -1
        status["error"] = f"Error checking container: {e.stderr}"
    
    return status

def get_all_service_statuses(services_config: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """Get status for all services defined in the configuration"""
    service_statuses = {}
    
    for service_name, service_config in services_config.items():
        service_statuses[service_name] = check_service_status(service_name, service_config)
    
    return service_statuses

def load_services_config() -> Dict[str, Dict[str, Any]]:
    """Load services configuration from check_status.sh script or use hardcoded defaults"""
    services = {}
    
    try:
        # Try to run the check_status.sh script to get service information
        try:
            result = subprocess.run(
                ['./check_status.sh', '--json'],
                capture_output=True,
                text=True,
                check=True
            )
            
            # Parse the JSON output
            services_data = json.loads(result.stdout)
            
            # Process each service
            for service_name, service_info in services_data.items():
                services[service_name] = {
                    "container_name": service_info.get("container_name", service_name),
                    "health_url": service_info.get("health_url"),
                    "port": service_info.get("port")
                }
                
            if services:
                return services
        except Exception as e:
            # If script execution fails, fall back to hardcoded services
            st.sidebar.warning(f"Using default service configuration: {str(e)}")
        
        # Fallback: Hardcoded service definitions
        services = {
            "Email Service": {
                "container_name": "email-app",
                "health_url": "http://localhost:3001/health",
                "port": "3001"
            },
            "API Service": {
                "container_name": "api-app",
                "health_url": "http://localhost:8000/health",
                "port": "8000"
            },
            "UI Service": {
                "container_name": "ui-app",
                "health_url": "http://localhost:8501",
                "port": "8501"
            },
            "Database": {
                "container_name": "postgres-db",
                "health_url": None,
                "port": "5432"
            },
            "Ollama": {
                "container_name": "ollama",
                "health_url": "http://localhost:11434",
                "port": "11434"
            }
        }
        
        return services
    except Exception as e:
        st.sidebar.error(f"Error loading services configuration: {str(e)}")
        return {}
