#!/usr/bin/env python3
# ui_components.py - UI components for the dashboard

import streamlit as st
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from modules.docker_utils import get_container_logs

def create_log_viewer_html(container_name, logs):
    """Create HTML for a log viewer popup"""
    # Escape any special characters in the logs
    escaped_logs = logs.replace("'", "\\'").replace('"', '\\"').replace('\n', '\\n')
    
    # Create a unique ID for this popup
    popup_id = f"popup_{container_name.replace('-', '_')}"
    
    # Create the HTML for the popup
    html = f"""
    <div id="{popup_id}" class="modal" style="display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; overflow: auto; background-color: rgba(0,0,0,0.7);">
        <div class="modal-content" style="background-color: #121212; margin: 5% auto; padding: 20px; border: 2px solid #00a3ff; border-radius: 8px; width: 80%; max-width: 800px; max-height: 80vh; overflow: auto; color: white;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; border-bottom: 1px solid #333; padding-bottom: 10px;">
                <h2 style="margin: 0; color: #00a3ff;">Logs: {container_name}</h2>
                <span class="close" onclick="document.getElementById('{popup_id}').style.display='none'" style="color: #aaa; float: right; font-size: 28px; font-weight: bold; cursor: pointer;">&times;</span>
            </div>
            <pre style="background-color: #1e1e1e; padding: 15px; border-radius: 5px; overflow: auto; white-space: pre-wrap; font-family: monospace; color: #e0e0e0; max-height: 60vh;">{escaped_logs}</pre>
            <div style="text-align: right; margin-top: 15px;">
                <button onclick="document.getElementById('{popup_id}').style.display='none'" style="background-color: #333; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer;">Close</button>
            </div>
        </div>
    </div>
    """
    
    return html

def render_service_card(service_name, status, col_index, resource_usage):
    """Render a service card with status and resource usage"""
    # Determine status color and text
    status_code = status.get('status_code', 0)
    status_text = status.get('status', 'Unknown')
    
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
    
    # Create a card with dark theme
    with st.container():
        st.markdown(f'''
        <style>
        .service-card-{col_index} {{
            background-color: #1e1e1e;
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
        
        # Fetch and store logs
        logs = get_container_logs(container_name)
        
        # Create the log viewer popup
        log_viewer_html = create_log_viewer_html(container_name, logs)
        st.markdown(log_viewer_html, unsafe_allow_html=True)
        
        # No need for additional JavaScript since we added the onclick directly to the div
        
        # Service info section with padding
        url_links = ""
        if status['port_mappings']:
            url_links = "<div style='margin-top: 5px;'>"
            for port, url in status['port_mappings'].items():
                # Extract just the port number from the URL for cleaner display
                url_display = url.split('//')[1] if '//' in url else url
                url_links += f"<a href='{url}' target='_blank' style='display: inline-block; margin-right: 10px; background-color: rgba(0,163,255,0.2); padding: 3px 8px; border-radius: 4px; color: #4da6ff; text-decoration: none;'><span style='color: white;'>Port {port}:</span> {url_display}</a>"
            url_links += "</div>"
        
        st.markdown(f"""
        <div style="padding: 0 15px 15px 15px;">
            <p><strong style='color: #00a3ff;'>Container:</strong> {status['container_name']}</p>
            <p><strong style='color: #00a3ff;'>URL:</strong> {url_links if status['port_mappings'] else '<span style="color: #666;">No URLs available</span>'}</p>
            <p><strong style='color: #00a3ff;'>Port:</strong> {status['port'] if status['port'] else 'N/A'}</p>
            <p><strong style='color: #00a3ff;'>Last Checked:</strong> {status['last_checked']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Resource usage section
        st.markdown(f"""
        <div style="background-color: #252525; padding: 10px 15px; border-top: 1px solid #333; border-radius: 0 0 8px 8px;">
            <h4 style="color: #00a3ff; margin-top: 0;">Resource Usage</h4>
            <p><strong style='color: #00a3ff;'>CPU:</strong> <span style='color: white;'>{cpu_usage}</span></p>
            <p><strong style='color: #00a3ff;'>Memory:</strong> <span style='color: white;'>{memory_usage} ({memory_percent})</span></p>
        </div>
        """, unsafe_allow_html=True)
