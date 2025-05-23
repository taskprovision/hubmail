#!/usr/bin/env python3
# Enhanced log viewer functionality for all containers

import streamlit as st
import subprocess
from datetime import datetime
import time
import os

def get_container_logs(container_name, lines=100, timeout_seconds=5):
    """Get logs from a specific container with timeout and error handling"""
    try:
        # Check if container exists and is running
        check_cmd = ['docker', 'ps', '--filter', f'name={container_name}', '--format', '{{.Names}}']
        result = subprocess.run(check_cmd, capture_output=True, text=True, timeout=2)
        
        if not result.stdout.strip():
            return f"Container '{container_name}' not found or not running.", datetime.now()
        
        # Get logs with timeout
        cmd = ['docker', 'logs', '--tail', str(lines), container_name]
        start_time = time.time()
        
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        
        logs = []
        while time.time() - start_time < timeout_seconds:
            if process.poll() is not None:
                break
            
            line = process.stdout.readline()
            if not line:
                time.sleep(0.1)
                continue
                
            logs.append(line)
        
        # If process is still running after timeout, terminate it
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=1)
            except subprocess.TimeoutExpired:
                process.kill()
            
            if not logs:
                return f"Timeout getting logs for '{container_name}' after {timeout_seconds} seconds.", datetime.now()
        
        # Get any remaining output
        remaining_output, _ = process.communicate()
        if remaining_output:
            logs.append(remaining_output)
        
        if not logs:
            return f"No logs available for '{container_name}'.", datetime.now()
            
        return ''.join(logs), datetime.now()
        
    except Exception as e:
        return f"Error retrieving logs for '{container_name}': {str(e)}", datetime.now()

def render_log_viewer(container_name):
    """Render a log viewer for a specific container"""
    st.subheader(f"Logs for {container_name}")
    
    # Get the number of lines from environment or use default
    log_lines = os.environ.get('LOG_LINES', '100')
    try:
        log_lines = int(log_lines)
    except ValueError:
        log_lines = 100
    
    # Get the timeout from environment or use default
    log_timeout = os.environ.get('LOG_TIMEOUT_SECONDS', '5')
    try:
        log_timeout = int(log_timeout)
    except ValueError:
        log_timeout = 5
    
    # Add a refresh button
    col1, col2 = st.columns([1, 5])
    with col1:
        refresh = st.button("🔄 Refresh", key=f"refresh_{container_name}")
    
    with col2:
        # Add a slider for the number of lines
        log_lines = st.slider("Number of lines", 10, 500, log_lines, key=f"lines_{container_name}")
    
    # Get logs
    logs, timestamp = get_container_logs(container_name, log_lines, log_timeout)
    
    # Display logs in a text area with monospace font
    st.text_area(
        f"Last updated: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
        logs,
        height=400,
        key=f"logs_{container_name}",
        help="Logs are displayed in reverse chronological order (newest first)"
    )
    
    # Add a download button
    st.download_button(
        label="Download Logs",
        data=logs,
        file_name=f"{container_name}_logs_{timestamp.strftime('%Y%m%d_%H%M%S')}.txt",
        mime="text/plain",
        key=f"download_{container_name}"
    )

def add_log_viewer_to_service_card(container_name):
    """Add a log viewer toggle button to a service card"""
    show_logs = st.toggle(f"View Logs for {container_name}", key=f"toggle_logs_{container_name}")
    if show_logs:
        render_log_viewer(container_name)

# Print instructions
print("""
LOG VIEWER FIX INSTRUCTIONS:

1. Copy this file to the Docker container:
   docker cp log_viewer_fix.py email-config-dashboard:/app/modules/log_viewer.py

2. Modify the ui_components_fix.py file in the container to use this log viewer:
   docker exec -it email-config-dashboard bash -c "sed -i '/def render_service_card/,/return html/ s/# Add log viewer button.*$/# Add log viewer toggle\\n    from modules.log_viewer import add_log_viewer_to_service_card\\n    add_log_viewer_to_service_card(container_name)/' /app/modules/ui_components_fix.py"

3. Restart the container:
   docker restart email-config-dashboard

This should enable log viewing for all containers.
""")
