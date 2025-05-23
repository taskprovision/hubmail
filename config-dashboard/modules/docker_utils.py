#!/usr/bin/env python3
# docker_utils.py - Docker-related utility functions

import json
import subprocess
import streamlit as st
from typing import Dict, List, Any, Optional, Tuple

def get_container_logs(container_name: str, lines: int = 100) -> str:
    """Get logs from a specific container"""
    try:
        # Run docker logs command
        result = subprocess.run(
            ['docker', 'logs', '--tail', str(lines), container_name],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error getting logs: {e.stderr}"
    except Exception as e:
        return f"Error: {str(e)}"

def get_container_ports(container_name: str) -> Dict[str, str]:
    """Get port mappings for a specific container"""
    port_mappings = {}
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
                    container_port_part, host_part = line.split('->')
                    container_port = container_port_part.strip().split('/')[0]  # Remove protocol (tcp/udp)
                    host_ip, host_port = host_part.strip().split(':')
                    
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
        st.sidebar.error(f"Error getting port mappings: {str(e)}")
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
        st.sidebar.error(f"Error getting resource usage: {str(e)}")
        return {}
