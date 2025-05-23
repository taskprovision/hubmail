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

def check_container_exists(container_name: str) -> bool:
    """Check if a container exists"""
    try:
        result = subprocess.run(
            ['docker', 'ps', '-a', '--format', '{{.Names}}', '--filter', f'name={container_name}'],
            capture_output=True,
            text=True,
            check=True
        )
        return container_name in result.stdout.strip().split('\n')
    except Exception:
        return False

def find_alternative_containers(container_name: str) -> List[str]:
    """Find alternative containers with similar names"""
    alternatives = []
    
    try:
        # Get all container names
        result = subprocess.run(
            ['docker', 'ps', '-a', '--format', '{{.Names}}'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            all_containers = result.stdout.strip().split('\n')
            
            # Find containers with similar names
            for name in all_containers:
                # Skip exact match
                if name == container_name:
                    continue
                    
                # Check if container_name is a substring of name or vice versa
                if container_name in name or name in container_name:
                    alternatives.append(name)
        
        return alternatives
    except Exception:
        return []

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
    
    # Check if container exists
    if container_name == "email-ollama":
        ollama_health = check_ollama_health(container_name)
        status.update(ollama_health)
        return status
    elif not check_container_exists(container_name):
        status["status"] = "stopped"
        status["status_code"] = 0
        status["error"] = "Container does not exist"
        
        # Find alternative containers
        alternatives = find_alternative_containers(container_name)
        if alternatives:
            status["alternatives"] = alternatives
        
        return status
    
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

# Import the Docker Compose finder module
import sys
import os

# Add parent directory to path to import docker_compose_finder
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.docker_compose_finder import get_all_services, find_docker_compose_files

def load_services_config() -> Dict[str, Dict[str, Any]]:
    """Load services configuration from Docker Compose files and check_status.sh script"""
    services = {}
    
    try:
        # First, try to get services from Docker Compose files
        try:
            # Find all Docker Compose files in the project
            docker_compose_files = find_docker_compose_files()
            
            if docker_compose_files:
                # Get services from all Docker Compose files
                compose_services = get_all_services()
                
                # Convert Docker Compose services to our format
                for service_name, service_info in compose_services.items():
                    container_name = service_info.get('container_name', service_name)
                    
                    # Determine port and health URL based on service configuration
                    port = None
                    health_url = None
                    
                    # Extract port from port mappings
                    ports = service_info.get('ports', [])
                    for port_mapping in ports:
                        if isinstance(port_mapping, str) and ':' in port_mapping:
                            # Format: "host_port:container_port"
                            host_port = port_mapping.split(':')[0]
                            port = host_port
                            break
                    
                    # Determine health URL based on service name and port
                    if port:
                        if 'api' in service_name.lower():
                            health_url = f"http://localhost:{port}/health"
                        elif 'ui' in service_name.lower() or 'web' in service_name.lower():
                            health_url = f"http://localhost:{port}"
                    
                    # Create service entry
                    services[service_name] = {
                        "container_name": container_name,
                        "health_url": health_url,
                        "port": port,
                        "source": service_info.get('source_file', 'Docker Compose')
                    }
                
                if services:
                    st.sidebar.success(f"Loaded services from {len(docker_compose_files)} Docker Compose files")
                    return services
        except Exception as e:
            st.sidebar.warning(f"Error loading services from Docker Compose: {str(e)}")
        
        # If Docker Compose files don't provide services, try check_status.sh
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
                    "port": service_info.get("port"),
                    "source": "check_status.sh"
                }
                
            if services:
                st.sidebar.success("Loaded services from check_status.sh")
                return services
        except Exception as e:
            # If script execution fails, fall back to hardcoded services
            st.sidebar.warning(f"Using default service configuration: {str(e)}")
        
        # Fallback: Hardcoded service definitions
        services = {
            "Email Service": {
                "container_name": "email-app",
                "health_url": "http://localhost:3001/health",
                "port": "3001",
                "source": "Default configuration"
            },
            "API Service": {
                "container_name": "api-app",
                "health_url": "http://localhost:8000/health",
                "port": "8000",
                "source": "Default configuration"
            },
            "UI Service": {
                "container_name": "ui-app",
                "health_url": "http://localhost:8501",
                "port": "8501",
                "source": "Default configuration"
            },
            "Database": {
                "container_name": "postgres-db",
                "health_url": None,
                "port": "5432",
                "source": "Default configuration"
            },
            "Ollama": {
                "container_name": "email-ollama",
                "health_url": "http://localhost:11436",
                "port": "11436",
                "source": "Default configuration"
            }
        }
        
        st.sidebar.info("Using default service configuration")
        return services
    except Exception as e:
        st.sidebar.error(f"Error loading services configuration: {str(e)}")
        return {}
from modules.ollama_health import check_ollama_health
