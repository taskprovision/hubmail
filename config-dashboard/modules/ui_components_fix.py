#!/usr/bin/env python3
# Improved fix for the Docker container issues

import streamlit as st
import os
import subprocess
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

# Function to get logs directly using subprocess
def get_docker_logs(container_name, lines=100):
    try:
        # Check if container exists
        check_result = subprocess.run(
            ['docker', 'ps', '-a', '--filter', f'name={container_name}', '--format', '{{.Names}}'],
            capture_output=True,
            text=True
        )
        
        if container_name not in check_result.stdout:
            return f"Container '{container_name}' not found.", datetime.now()
        
        # Get logs
        result = subprocess.run(
            ['docker', 'logs', '--tail', str(lines), container_name],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            return result.stdout, datetime.now()
        else:
            return f"Error getting logs: {result.stderr}", datetime.now()
    except Exception as e:
        return f"Error: {str(e)}", datetime.now()

# Function to find Docker Compose files
def find_docker_compose_files(base_dir="/home/tom/github/taskprovision/hubmail"):
    try:
        # Use find command to locate all docker-compose files
        result = subprocess.run(
            ['find', base_dir, '-name', 'docker-compose.yml', '-o', '-name', 'docker-compose.yaml'],
            capture_output=True,
            text=True
        )
        
        files = [f for f in result.stdout.strip().split('\n') if f]
        
        # If no files found, check if docker-compose.yml exists in the base directory
        if not files and os.path.exists(os.path.join(base_dir, 'docker-compose.yml')):
            files = [os.path.join(base_dir, 'docker-compose.yml')]
            
        return files
    except Exception as e:
        st.error(f"Error finding Docker Compose files: {str(e)}")
        return []

# Improved service card renderer
def render_service_card(service_name: str, status: Dict[str, Any], *args, **kwargs):
    """Render a service card with status information"""
    # Ensure container_name exists
    container_name = status.get('container_name', service_name)
    
    # Make sure required keys exist in the status dictionary
    if 'status' not in status:
        status['status'] = 'unknown'
    if 'health_status' not in status:
        status['health_status'] = 'unknown'
    if 'resource_usage' not in status:
        status['resource_usage'] = {'cpu': 'N/A', 'memory': 'N/A'}
    if 'port_mappings' not in status:
        status['port_mappings'] = {}
    
    # Create a card with status information
    st.markdown(f"""
    <div style="background-color: #1e1e1e; border-radius: 8px; border: 1px solid #444; padding: 15px; margin-bottom: 20px;">
        <h3 style="color: #00a3ff;">{service_name}</h3>
        <p><strong style="color: #00a3ff;">Container:</strong> {container_name}</p>
        <p><strong style="color: #00a3ff;">Status:</strong> {status['status'].upper()}</p>
        <p><strong style="color: #00a3ff;">Health:</strong> {status['health_status']}</p>
    """, unsafe_allow_html=True)
    
    # Add port information if available
    if status['port_mappings']:
        port_html = "<p><strong style='color: #00a3ff;'>Ports:</strong></p><ul>"
        for port, mapping in status['port_mappings'].items():
            port_html += f"<li>{port} → {mapping}</li>"
        port_html += "</ul>"
        st.markdown(port_html, unsafe_allow_html=True)
    
    # Add resource usage information
    st.markdown(f"""
        <p><strong style="color: #00a3ff;">Resource Usage:</strong></p>
        <ul>
            <li>CPU: {status['resource_usage'].get('cpu', 'N/A')}</li>
            <li>Memory: {status['resource_usage'].get('memory', 'N/A')}</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Add a button to view logs if the container is running
    if status['status'] == 'running':
        # Create a unique key for this container's logs
        log_key = f"show_logs_{container_name}"
        
        # Initialize the session state for this container if it doesn't exist
        if log_key not in st.session_state:
            st.session_state[log_key] = False
        
        # Add a button to toggle log visibility
        if st.button(f"View Logs for {container_name}"):
            # Get logs directly
            logs, timestamp = get_docker_logs(container_name, 100)
            
            # Display logs
            st.text_area(f"Logs for {container_name} (Last updated: {timestamp})", 
                         logs, height=400)

# Function to display Docker Compose files
def display_docker_compose_tab():
    """Display Docker Compose files"""
    st.header("Docker Compose Files")
    
    # Find Docker Compose files
    base_dir = "/home/tom/github/taskprovision/hubmail"
    compose_files = find_docker_compose_files(base_dir)
    
    if not compose_files:
        st.warning("No Docker Compose files found in the project.")
        
        # Check if docker-compose.yml exists in the current directory
        if os.path.exists('docker-compose.yml'):
            st.success("Found docker-compose.yml in the current directory.")
            compose_files = ['docker-compose.yml']
        else:
            # Try to find any YAML files that might be Docker Compose files
            result = subprocess.run(
                ['find', base_dir, '-name', '*.yml', '-o', '-name', '*.yaml'],
                capture_output=True,
                text=True
            )
            yaml_files = [f for f in result.stdout.strip().split('\n') if f]
            
            if yaml_files:
                st.info(f"Found {len(yaml_files)} YAML files that might be Docker Compose files:")
                for file in yaml_files:
                    if st.button(f"View {os.path.basename(file)}"):
                        try:
                            with open(file, 'r') as f:
                                content = f.read()
                            st.code(content, language="yaml")
                        except Exception as e:
                            st.error(f"Error reading file: {str(e)}")
            else:
                st.error("No YAML files found in the project.")
        
        return
    
    # Display each Docker Compose file
    for file_path in compose_files:
        with st.expander(f"{os.path.basename(file_path)} ({os.path.dirname(file_path)})"):
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                st.code(content, language="yaml")
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")

# Print instructions
print("""
DOCKER FIX V2 INSTRUCTIONS:

1. Copy this file to the Docker container:
   docker cp docker_fix_v2.py email-config-dashboard:/app/modules/ui_components_fix.py

2. Modify the app.py file in the container to use this fixed version:
   docker exec -it email-config-dashboard bash -c "sed -i 's/from modules.ui_components import render_service_card/from modules.ui_components_fix import render_service_card, display_docker_compose_tab/' /app/app.py"

3. Update the Docker Compose tab in app.py:
   docker exec -it email-config-dashboard bash -c "sed -i 's/display_docker_compose_tabs()/display_docker_compose_tab()/' /app/app.py"

4. Restart the container:
   docker restart email-config-dashboard

This should fix both the log button and Docker Compose issues.
""")
