#!/usr/bin/env python3
# docker_utils.py - Docker-related utility functions

import json
import subprocess
import streamlit as st
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from modules.env_loader import load_env_vars

# Load environment variables
env_vars = load_env_vars()

def get_container_logs(container_name: str, lines: Optional[int] = None, timestamp: Optional[datetime] = None) -> Tuple[str, datetime]:
    """Get logs from a specific container with timeout"""
    # Use environment variables for log lines if not specified
    if lines is None:
        lines = int(env_vars.get('LOG_LINES', 100))
    
    # Get current timestamp if not provided
    current_time = datetime.now()
    
    # Calculate timeout
    log_timeout = int(env_vars.get('LOG_TIMEOUT_SECONDS', 10))
    
    # If timestamp is provided and it's within the timeout period, return empty logs
    if timestamp and (current_time - timestamp).total_seconds() < log_timeout:
        return "Logs are rate limited. Please try again later.", timestamp
    
    # Check if container exists first
    if not check_container_exists(container_name):
        return f"Container '{container_name}' does not exist or is not running.", current_time
    
    try:
        # Run docker logs command with a timeout to prevent hanging
        process = subprocess.Popen(
            ['docker', 'logs', '--tail', str(lines), container_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for the process to complete with a timeout
        try:
            stdout, stderr = process.communicate(timeout=log_timeout)
            if process.returncode != 0:
                return f"Error getting logs: {stderr}", current_time
            return stdout if stdout else "No logs available for this container.", current_time
        except subprocess.TimeoutExpired:
            # Kill the process if it times out
            process.kill()
            return "Log retrieval timed out. The container might be producing too many logs.", current_time
    except Exception as e:
        return f"Error retrieving logs: {str(e)}", current_time

def check_container_exists(container_name: str) -> bool:
    """Check if a Docker container exists"""
    try:
        # First try exact match
        result = subprocess.run(
            ['docker', 'container', 'inspect', container_name],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return True
            
        # If exact match fails, try to find containers with similar names
        result = subprocess.run(
            ['docker', 'ps', '-a', '--format', '{{.Names}}'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            container_names = result.stdout.strip().split('\n')
            
            # Check for exact match first
            if container_name in container_names:
                return True
                
            # Check for partial matches (e.g., 'ollama' might match 'email-ollama')
            for name in container_names:
                if container_name in name or name in container_name:
                    return True
        
        return False
    except Exception:
        return False

def get_container_ports(container_name: str) -> Dict[str, str]:
    """Get port mappings for a specific container"""
    port_mappings = {}
    
    # Check if container exists first
    if not check_container_exists(container_name):
        # Return dummy port mappings for non-existent containers
        if 'api' in container_name.lower():
            return {'8000': f'http://localhost:8000'}
        elif 'ui' in container_name.lower() or 'web' in container_name.lower():
            return {'8501': f'http://localhost:8501'}
        elif 'email' in container_name.lower():
            return {'3001': f'http://localhost:3001'}
        elif 'db' in container_name.lower() or 'postgres' in container_name.lower():
            return {'5432': f'http://localhost:5432'}
        elif 'ollama' in container_name.lower():
            return {'11434': f'http://localhost:11434'}
        return {}
    
    try:
        # First try using docker port command which is more reliable for actual port bindings
        try:
            result = subprocess.run(
                ['docker', 'port', container_name],
                capture_output=True,
                text=True,
                check=True
            )
            
            # Parse the output which is in format: container_port/protocol -> host_ip:host_port
            for line in result.stdout.strip().split('\n'):
                if '->' in line:
                    try:
                        container_port_part, host_part = line.split('->')
                        container_port = container_port_part.strip().split('/')[0]  # Remove protocol (tcp/udp)
                        
                        # Handle different formats of host_part
                        host_part = host_part.strip()
                        if ':' in host_part:
                            # Format: host_ip:host_port
                            parts = host_part.rsplit(':', 1)  # Use rsplit to handle IPv6 addresses
                            if len(parts) == 2:
                                host_ip, host_port = parts
                            else:
                                # Fallback if parsing fails
                                host_ip = 'localhost'
                                host_port = host_part
                        else:
                            # Format: host_port only
                            host_ip = 'localhost'
                            host_port = host_part
                    except Exception as e:
                        # If parsing fails, skip this line
                        continue
                    
                        # Use localhost for better browser compatibility
                        if host_ip == '0.0.0.0' or host_ip == '::':
                            host_ip = 'localhost'
                        
                        # Generate URL based on port
                        protocol = 'http'
                        if container_port in ['443', '8443']:
                            protocol = 'https'
                        
                        url = f"{protocol}://{host_ip}:{host_port}"
                        port_mappings[container_port] = url
            
            if port_mappings:
                return port_mappings
        except subprocess.CalledProcessError:
            # Fall back to docker inspect if docker port fails
            pass
        
        # Fallback: Run docker inspect command to get port mappings
        result = subprocess.run(
            ['docker', 'inspect', '--format', '{{json .NetworkSettings.Ports}}', container_name],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Parse the JSON output
        ports_data = json.loads(result.stdout)
        
        # Process each port mapping
        for container_port, host_bindings in ports_data.items():
            if host_bindings:
                for binding in host_bindings:
                    host_ip = binding.get('HostIp', '0.0.0.0')
                    host_port = binding.get('HostPort', '')
                    
                    # Format: container_port -> host_ip:host_port
                    container_port_clean = container_port.split('/')[0]  # Remove protocol (tcp/udp)
                    
                    # Use localhost for better browser compatibility
                    if host_ip == '0.0.0.0' or host_ip == '::' or host_ip == '':
                        host_ip = 'localhost'
                    
                    # Generate URL based on port
                    protocol = 'http'
                    if container_port_clean in ['443', '8443']:
                        protocol = 'https'
                    
                    url = f"{protocol}://{host_ip}:{host_port}"
                    port_mappings[container_port_clean] = url
        
        return port_mappings
    except Exception as e:
        error_msg = f"[Docker Inspect] Error getting port mappings: {str(e)}"
        error_key = f"error_port_mappings_{container_name}"
        error_time = datetime.now()
        
        # Store error message and timestamp in session state
        if 'error_messages' not in st.session_state:
            st.session_state.error_messages = {}
        
        st.session_state.error_messages[error_key] = {
            'message': error_msg,
            'timestamp': error_time
        }
        
        # Display error message
        st.sidebar.error(error_msg)
        
        return {}

def get_resource_usage() -> Dict[str, Dict[str, str]]:
    """Get resource usage information for all running containers"""
    resource_usage = {}
    try:
        # Run docker stats command with no-stream option to get current stats
        result = subprocess.run(
            ['docker', 'stats', '--no-stream', '--format', '{{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}'],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Process each line of output
        for line in result.stdout.strip().split('\n'):
            if line:
                parts = line.split('\t')
                if len(parts) >= 4:
                    container_name = parts[0]
                    cpu_usage = parts[1]
                    mem_usage = parts[2]
                    mem_perc = parts[3]
                    
                    resource_usage[container_name] = {
                        'cpu': cpu_usage,
                        'memory': mem_usage,
                        'memory_percent': mem_perc
                    }
        
        return resource_usage
    except Exception as e:
        error_msg = f"[Docker Stats] Error getting resource usage: {str(e)}"
        error_key = "error_resource_usage"
        error_time = datetime.now()
        
        # Store error message and timestamp in session state
        if 'error_messages' not in st.session_state:
            st.session_state.error_messages = {}
        
        st.session_state.error_messages[error_key] = {
            'message': error_msg,
            'timestamp': error_time
        }
        
        # Display error message
        st.sidebar.error(error_msg)
        
        return {}
