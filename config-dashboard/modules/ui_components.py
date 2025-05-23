#!/usr/bin/env python3
# ui_components.py - UI components for the dashboard

import streamlit as st
import os
import time
import html
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from modules.docker_utils import get_container_logs
from modules.env_loader import load_env_vars

# Load environment variables
env_vars = load_env_vars()

def create_log_viewer_html(container_name, logs):
    """Create HTML for a log viewer popup"""
    # Escape any HTML in the logs to prevent rendering issues
    escaped_logs = html.escape(logs) if logs else "No logs available"
    
    return f"""
    <div id="log-popup-{container_name}" class="log-popup" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.8); z-index: 1000; overflow: auto; padding: 20px;">
        <div class="log-content" style="background-color: #1e1e1e; margin: 10% auto; padding: 20px; width: 80%; max-width: 800px; border-radius: 8px; position: relative; max-height: 70vh; overflow: auto;">
            <span class="close-button" onclick="document.getElementById('log-popup-{container_name}').style.display='none'" style="position: absolute; top: 10px; right: 20px; font-size: 24px; cursor: pointer; color: #aaa;">&times;</span>
            <h3 style="color: #00a3ff; margin-top: 0;">Logs for {container_name}</h3>
            <pre style="background-color: #2d2d2d; color: #ddd; padding: 15px; border-radius: 5px; overflow: auto; max-height: 50vh; white-space: pre-wrap;">{escaped_logs}</pre>
        </div>
    </div>
    """

def render_log_viewer_button(container_name: str):
    """Render a button to view logs for a container"""
    # Create a unique ID for this button
    button_id = f"view-logs-{container_name}"
    
    # Create a button with an onclick event
    button_html = f"""
    <button id="{button_id}" style="background-color: rgba(0, 163, 255, 0.2); border: none; color: #aaaaaa; padding: 5px 10px; margin-top: 5px; cursor: pointer; border-radius: 4px;">
        View Logs
    </button>
    <script>
        // Add click event listener after the DOM is fully loaded
        document.addEventListener('DOMContentLoaded', function() {{
            var button = document.getElementById('{button_id}');
            if (button) {{
                button.addEventListener('click', function() {{
                    var popup = document.getElementById('log-popup-{container_name}');
                    if (popup) {{
                        popup.style.display = 'block';
                    }} else {{
                        console.error('Log popup for {container_name} not found');
                    }}
                }});
            }} else {{
                console.error('Log button for {container_name} not found');
            }}
        }});
    </script>
    """
    
    return button_html

def get_module_background_color(service_name):
    """Get a background color based on the module type"""
    service_name_lower = service_name.lower()
    
    if 'api' in service_name_lower:
        return "rgba(0, 128, 255, 0.05)"  # Light blue for API services
    elif 'ui' in service_name_lower or 'web' in service_name_lower:
        return "rgba(0, 255, 128, 0.05)"  # Light green for UI services
    elif 'db' in service_name_lower or 'postgres' in service_name_lower:
        return "rgba(255, 128, 0, 0.05)"   # Light orange for database services
    elif 'email' in service_name_lower:
        return "rgba(255, 0, 255, 0.05)"   # Light purple for email services
    elif 'ollama' in service_name_lower or 'llm' in service_name_lower:
        return "rgba(255, 255, 0, 0.05)"   # Light yellow for AI/LLM services
    else:
        return "rgba(128, 128, 128, 0.05)" # Light gray for other services

def render_service_card(service_name, status, col_index, resource_usage):
    """Render a service card with status and resource usage"""
    # Determine status color and text
    status_code = status.get('status_code', 0)
    status_text = status.get('status', 'Unknown')
    error_message = status.get('error', None)
    
    # Set colors based on status
    if status_code == 2:  # Healthy
        border_color = "#00ff00"  # Bright green
        header_bg = "#1a3e1a"     # Dark green background
    elif status_code == 1:  # Running but not healthy
        border_color = "#ffff00"  # Bright yellow
        header_bg = "#3e3e1a"     # Dark yellow background
    elif status_code == -1:  # Error
        border_color = "#ff0000"  # Bright red
        header_bg = "#3e1a1a"     # Dark red background
    else:  # Unknown or stopped
        border_color = "#888888"  # Gray
        header_bg = "#2a2a2a"     # Dark gray background
        
    # Get module-specific background color
    module_bg_color = get_module_background_color(service_name)
    
    # Get resource usage if available
    container_name = status.get('container_name', service_name)
    cpu_usage = "N/A"
    memory_usage = "N/A"
    memory_percent = "N/A"
    
    if container_name in resource_usage:
        container_resources = resource_usage[container_name]
        cpu_usage = container_resources.get('cpu', 'N/A')
        memory_usage = container_resources.get('memory', 'N/A')
        memory_percent = container_resources.get('memory_percent', 'N/A')
    
    # Create a card with dark theme and module-specific background
    with st.container():
        st.markdown(f'''
        <style>
        .service-card-{col_index} {{
            background-color: #1e1e1e;
            background: linear-gradient(to bottom, #1e1e1e, {module_bg_color});
            border-radius: 8px;
            border: 1px solid {border_color};
            padding: 0;
            margin-bottom: 20px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            overflow: hidden;
        }}
        </style>
        ''', unsafe_allow_html=True)
        
        # Get container logs when button is clicked
        container_name = status['container_name']
        
        # Create a unique key for this container's button
        button_key = f"logs_{container_name}_{col_index}"
        
        # Create a clickable header for logs with a button to ensure it works
        st.markdown(f"""
        <div id="header_{container_name.replace('-', '_')}" 
             style="background-color: {header_bg}; padding: 10px; border-bottom: 2px solid {border_color}; margin-bottom: 10px;">
            <h3 style="color: white; margin: 0; text-shadow: 1px 1px 2px rgba(0,0,0,0.5);">{service_name}</h3>
            <p style="margin: 5px 0 0 0;"><strong style="color: {border_color}; font-size: 1.1em;">{status_text}</strong></p>
            <button onclick="document.getElementById('popup_{container_name.replace('-', '_')}').style.display='block';" 
                    style="background-color: rgba(0,163,255,0.2); border: none; color: #aaa; padding: 5px 10px; margin-top: 5px; cursor: pointer; border-radius: 4px;">
                View Logs
            </button>
        </div>
        """, unsafe_allow_html=True)
    
    # Add status details section to explain why a service is unhealthy or stopped
    # Make sure required keys exist in the status dictionary
    if 'status' not in status:
        status['status'] = 'unknown'
    if 'health_status' not in status:
        status['health_status'] = 'unknown'
    if 'resource_usage' not in status:
        status['resource_usage'] = {'cpu': 'N/A', 'memory': 'N/A'}
    if 'port_mappings' not in status:
        status['port_mappings'] = {}
    
    # Create status details based on service status
    if status['status'] == 'running' and status['health_status'] == 'healthy':
        status_details = f"<div style='background-color: rgba(0, 255, 0, 0.1); border-left: 4px solid #00ff00; padding: 10px; margin-bottom: 15px;'><strong style='color: #00ff00;'>Status:</strong> {status['status'].upper()} ({status['health_status'].upper()})</div>"
    elif status['status'] == 'running' and status['health_status'] == 'unhealthy':
        status_details = f"<div style='background-color: rgba(255, 0, 0, 0.1); border-left: 4px solid #ff0000; padding: 10px; margin-bottom: 15px;'><strong style='color: #ff0000;'>Status:</strong> {status['status'].upper()} ({status['health_status'].upper()})<br><span style='color: #ff6666;'>The service is running but not responding to health checks.</span></div>"
    elif status['status'] == 'stopped':
        # Check if there are alternative containers
        alternatives_html = ""
        if 'alternatives' in status and status['alternatives']:
            alternatives_list = "<ul style='margin-top: 5px; margin-bottom: 0; padding-left: 20px;'>" + \
                               "".join([f"<li style='color: #aaaaaa;'>{alt}</li>" for alt in status['alternatives']]) + \
                               "</ul>"
            alternatives_html = f"<br><span style='color: #aaaaaa;'>Similar containers found:</span>{alternatives_list}"
        
        error_message = status.get('error', status.get('health_status', 'Container not running'))
        status_details = f"<div style='background-color: rgba(128, 128, 128, 0.1); border-left: 4px solid #888888; padding: 10px; margin-bottom: 15px;'><strong style='color: #888888;'>Status:</strong> {status['status'].upper()}<br><span style='color: #aaaaaa;'>{error_message}</span>{alternatives_html}</div>"
    else:
        status_details = f"<div style='background-color: rgba(255, 165, 0, 0.1); border-left: 4px solid #ffa500; padding: 10px; margin-bottom: 15px;'><strong style='color: #ffa500;'>Status:</strong> {status['status'].upper()}<br><span style='color: #ffcc00;'>{status['health_status']}</span></div>"
    
    # Check if service is accessible in browser
    browser_check = ""
    if 'ui' in service_name.lower() or 'web' in service_name.lower():
        browser_check = f"<p><strong style='color: #00a3ff;'>Browser:</strong> <a href='http://localhost:8501/' target='_blank' style='color: #4da6ff;'>View in Browser</a> (Streamlit UI)</p>"
    elif 'api' in service_name.lower():
        browser_check = f"<p><strong style='color: #00a3ff;'>API:</strong> <a href='http://localhost:8000/docs' target='_blank' style='color: #4da6ff;'>API Documentation</a> (Swagger UI)</p>"
    
    # Add source information if available
    source_info = ""
    if 'source' in status:
        source_path = status['source']
        source_name = os.path.basename(source_path) if os.path.exists(source_path) else source_path
        source_info = f"<p><strong style='color: #00a3ff;'>Source:</strong> <span style='color: #aaa;'>{source_name}</span></p>"
    
    # Prepare URL links
    url_links = ""
    if status['port_mappings']:
        url_links = "<div style='margin-top: 5px;'>"
        for port, mapping in status['port_mappings'].items():
            host_port = mapping.split(':')[0] if ':' in mapping else mapping
            url_links += f"<a href='http://localhost:{host_port}' target='_blank' style='display: inline-block; margin-right: 10px; background-color: rgba(0,163,255,0.2); padding: 3px 8px; border-radius: 4px; color: #4da6ff; text-decoration: none;'><span style='color: white;'>Port {port}:</span> localhost:{host_port}</a>"
        url_links += "</div>"
    
    service_info_html = f"""
    <div style="padding: 0 15px 15px 15px;">
        {status_details}
        <p><strong style='color: #00a3ff;'>Container:</strong> {status['container_name']}</p>
        <p><strong style='color: #00a3ff;'>URL:</strong> {url_links if status['port_mappings'] else '<span style="color: #666;">No URLs available</span>'}</p>
        {browser_check}
        <p><strong style='color: #00a3ff;'>Port:</strong> {status['port'] if status['port'] else 'N/A'}</p>
        <p><strong style='color: #00a3ff;'>Last Checked:</strong> {status['last_checked']}</p>
        {source_info}
    </div>
    """
    st.components.v1.html(service_info_html, height=None, scrolling=False)
    
    # Resource usage section
    st.markdown(f"""
    <div style="padding: 0 15px 15px 15px; border-top: 1px solid #333;">
        <p style="margin-top: 10px;"><strong style='color: #00a3ff;'>Resource Usage:</strong></p>
        <div style="display: flex; justify-content: space-between;">
            <div style="flex: 1;">
                <p style="margin: 0; color: #aaa;">CPU: {status['resource_usage']['cpu']}</p>
            </div>
            <div style="flex: 1;">
                <p style="margin: 0; color: #aaa;">Memory: {status['resource_usage']['memory']}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Add log viewer button if the container is running
    if status['status'] == 'running':
        # Create a unique key for this container's logs
        log_key = f"show_logs_{container_name}"
        
        # Initialize the session state for this container if it doesn't exist
        if log_key not in st.session_state:
            st.session_state[log_key] = False
        
        # Add a button to toggle log visibility
        if st.button(f"View Logs for {container_name}", key=f"btn_{container_name}"):
            # Toggle the log visibility state
            st.session_state[log_key] = not st.session_state[log_key]
            # Force a rerun to update the UI
            st.experimental_rerun()
        
        # If logs should be shown, display them
        if st.session_state[log_key]:
            # Get logs for the container
            env_vars = load_env_vars()
            log_lines = env_vars.get('LOG_LINES', '100')
            log_timeout = int(env_vars.get('LOG_TIMEOUT_SECONDS', '10'))
            
            try:
                logs, timestamp = get_container_logs(container_name, int(log_lines), None)
                
                # Display logs in a Streamlit expander
                with st.expander(f"Logs for {container_name} (Last updated: {timestamp})", expanded=True):
                    # Add a close button
                    if st.button("Close Logs", key=f"close_{container_name}"):
                        st.session_state[log_key] = False
                        st.experimental_rerun()
                    
                    # Display the logs
                    st.text_area("Container Logs", logs, height=400)
            except Exception as e:
                st.error(f"Error getting logs for {container_name}: {str(e)}")
                st.session_state[log_key] = False
