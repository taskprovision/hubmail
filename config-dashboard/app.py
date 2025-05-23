#!/usr/bin/env python3
"""
HubMail Configuration Dashboard
A streamlit app to visualize and manage HubMail configurations and container status
"""

import streamlit as st
import os
import time
import json
import yaml
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

# Import our modules
from modules.env_loader import load_env_vars
from modules.docker_utils import get_container_logs, get_container_ports, get_resource_usage
from modules.ui_components_fix import render_service_card
from modules.service_status import check_service_status, get_all_service_statuses, load_services_config
from modules.config_utils import load_config_files, categorize_config_files
from modules.ui_components_fix import render_service_card, display_docker_compose_tab
from modules.docker_compose_finder import get_all_services, find_docker_compose_files

# Load environment variables
env_vars = load_env_vars()

# Set page config
st.set_page_config(
    page_title="HubMail Configuration Dashboard",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS
def apply_custom_css():
    """Apply custom CSS for dark theme and other styling"""
    st.markdown("""
    <style>
    .main {
        background-color: #121212;
        color: white;
    }
    .stApp {
        background-color: #121212;
    }
    .sidebar .sidebar-content {
        background-color: #1e1e1e;
    }
    h1, h2, h3 {
        color: white;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
        background-color: #1e1e1e;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #2d2d2d;
        color: white;
        border-radius: 4px 4px 0 0;
        padding: 10px 20px;
        border: none;
    }
    .stTabs [aria-selected="true"] {
        background-color: #00a3ff;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

def display_config_sidebar(config_dir: str):
    """Display configuration files in the sidebar"""
    st.sidebar.title("Configuration Files")
    
    # Use environment variable for config directory
    config_dir = env_vars.get('CONFIG_DIR', config_dir)
    
    # Handle relative paths
    if not os.path.isabs(config_dir):
        # Convert relative path to absolute path
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_dir = os.path.join(base_dir, config_dir.lstrip('../'))
    
    # Check if directory exists
    if not os.path.exists(config_dir):
        st.sidebar.warning(f"Config directory not found: {config_dir}")
        # Create a dummy config file for demonstration
        if 'config_files' not in st.session_state:
            st.session_state.config_files = {
                'docker-compose.yml': {
                    'version': '3',
                    'services': {
                        'email-app': {
                            'image': 'hubmail/email-service:latest',
                            'ports': ['3001:3001'],
                            'environment': ['API_PORT=3001', 'DEBUG=true']
                        },
                        'api-app': {
                            'image': 'hubmail/api-service:latest',
                            'ports': ['8000:8000'],
                            'environment': ['API_PORT=8000', 'DEBUG=true']
                        }
                    }
                },
                'config.json': {
                    'api': {
                        'port': 8000,
                        'host': 'localhost',
                        'debug': True
                    },
                    'ui': {
                        'port': 8501,
                        'host': 'localhost'
                    },
                    'database': {
                        'host': 'postgres-db',
                        'port': 5432,
                        'user': 'postgres'
                    }
                }
            }
    else:
        # Load configuration files
        if 'config_files' not in st.session_state:
            st.session_state.config_files = load_config_files(config_dir)
    
    # Categorize configuration files
    categories = categorize_config_files(st.session_state.config_files)
    
    # Display configuration files by category
    for category, files in categories.items():
        if files:
            st.sidebar.subheader(category)
            for filename in sorted(files):
                if st.sidebar.button(filename, key=f"config_{filename}"):
                    st.session_state.selected_config = filename
                    st.session_state.config_data = st.session_state.config_files[filename]

def display_service_status_tab(services_config: Dict[str, Dict[str, Any]]):
    """Display service status tab with service cards"""
    # Get status for all services
    service_statuses = get_all_service_statuses(services_config)
    
    # Get resource usage for all containers
    resource_usage = get_resource_usage()
    
    # Create columns for service cards
    col1, col2 = st.columns(2)
    
    # Display service cards in columns
    for i, (service_name, status) in enumerate(service_statuses.items()):
        # Alternate between columns
        if i % 2 == 0:
            with col1:
                render_service_card(service_name, status, i, resource_usage)
        else:
            with col2:
                render_service_card(service_name, status, i, resource_usage)

def display_config_viewer_tab():
    """Display configuration viewer tab with interactive elements"""
    if 'selected_config' in st.session_state and 'config_data' in st.session_state:
        filename = st.session_state.selected_config
        config_data = st.session_state.config_data
        
        # Display file information
        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader(f"Configuration: {filename}")
        with col2:
            # Add a refresh button
            if st.button("🔄 Refresh", key="refresh_config"):
                if 'config_files' in st.session_state:
                    # Reload the configuration file
                    config_dir = env_vars.get('CONFIG_DIR', "../python_app/config")
                    if os.path.exists(config_dir):
                        st.session_state.config_files = load_config_files(config_dir)
                        if filename in st.session_state.config_files:
                            st.session_state.config_data = st.session_state.config_files[filename]
                            st.experimental_rerun()
        
        # Determine file type and display appropriate editor
        file_extension = os.path.splitext(filename)[1].lower()
        
        # Add a description based on the file type
        if file_extension in ['.yml', '.yaml']:
            st.markdown("**YAML Configuration File**")
            st.markdown("This file defines services, networks, and volumes for Docker Compose.")
        elif file_extension == '.json':
            st.markdown("**JSON Configuration File**")
            st.markdown("This file contains application settings in JSON format.")
        elif file_extension == '.env':
            st.markdown("**Environment Variables File**")
            st.markdown("This file contains environment variables for the application.")
        else:
            st.markdown(f"**Configuration File: {file_extension}**")
        
        # Show file content in different formats
        tabs = st.tabs(["Formatted", "Raw", "Tree View"])
        
        with tabs[0]:
            # Display formatted configuration data
            st.json(config_data)
        
        with tabs[1]:
            # Display raw configuration data
            if file_extension in ['.yml', '.yaml']:
                raw_content = yaml.dump(config_data, default_flow_style=False)
            else:
                raw_content = json.dumps(config_data, indent=2)
            
            st.code(raw_content, language="yaml" if file_extension in ['.yml', '.yaml'] else "json")
        
        with tabs[2]:
            # Display tree view of configuration
            def display_tree(data, prefix=""):
                if isinstance(data, dict):
                    for key, value in data.items():
                        if isinstance(value, (dict, list)):
                            st.markdown(f"{prefix}**{key}**")
                            display_tree(value, prefix + "&nbsp;&nbsp;&nbsp;&nbsp;")
                        else:
                            st.markdown(f"{prefix}**{key}**: `{value}`")
                elif isinstance(data, list):
                    for i, item in enumerate(data):
                        if isinstance(item, (dict, list)):
                            st.markdown(f"{prefix}**[{i}]**")
                            display_tree(item, prefix + "&nbsp;&nbsp;&nbsp;&nbsp;")
                        else:
                            st.markdown(f"{prefix}**[{i}]**: `{item}`")
            
            display_tree(config_data)
    else:
        st.info("Select a configuration file from the sidebar to view its contents.")
        
        # Display some example configuration options
        st.markdown("### Available Configuration Files")
        st.markdown("The following configuration files are typically available in HubMail:")
        
        st.markdown("""  
        - **docker-compose.yml**: Defines all services and their configurations
        - **config.json**: Application settings and parameters
        - **.env**: Environment variables for the application
        - **nginx.conf**: Web server configuration
        """)
        
        # Show a tip
        st.info("💡 Tip: Click on a configuration file in the sidebar to view its contents.")
        
        # Add a dummy visualization
        st.markdown("### Configuration Structure")
        st.markdown("HubMail uses a hierarchical configuration structure:")
        
        # Simple ASCII art tree
        st.code("""
        hubmail/
        ├── docker-compose.yml
        ├── .env
        ├── python_app/
        │   ├── config/
        │   │   ├── config.json
        │   │   └── services.yml
        │   └── .env
        └── config-dashboard/
            ├── app.py
            └── config.env
        """, language="bash")
        
        # Add a note about environment variables
        st.markdown("### Environment Variables")
        st.markdown("HubMail uses the following key environment variables:")
        
        # Create a small table of environment variables
        env_data = {
            "Variable": ["API_PORT", "UI_PORT", "API_HOST", "UI_HOST", "LOG_TIMEOUT_SECONDS"],
            "Default": ["8000", "8501", "localhost", "localhost", "10"],
            "Description": [
                "Port for the API service",
                "Port for the UI service",
                "Host for the API service",
                "Host for the UI service",
                "Timeout for log retrieval in seconds"
            ]
        }
        
        st.dataframe(env_data)

def clean_error_messages():
    """Clean up error messages that have exceeded the timeout"""
    if 'error_messages' not in st.session_state:
        return
    
    # Get the error timeout from environment variables
    error_timeout = int(env_vars.get('LOG_TIMEOUT_SECONDS', 10))
    current_time = datetime.now()
    
    # Check each error message
    keys_to_remove = []
    for key, error_data in st.session_state.error_messages.items():
        if (current_time - error_data['timestamp']).total_seconds() > error_timeout:
            keys_to_remove.append(key)
    
    # Remove expired error messages
    for key in keys_to_remove:
        del st.session_state.error_messages[key]

def main():
    """Main function to run the dashboard"""
    # Apply custom CSS
    apply_custom_css()
    
    # Header
    st.title("⚙️ HubMail Configuration Dashboard")
    st.markdown("Visualize all your configuration settings in one place")
    
    # Create a session state for storing container logs
    if 'container_logs' not in st.session_state:
        st.session_state.container_logs = {}
    
    # Create a session state for tracking which container's logs to show
    if 'show_logs_for' not in st.session_state:
        st.session_state.show_logs_for = None
        
    # Create a session state for error messages
    if 'error_messages' not in st.session_state:
        st.session_state.error_messages = {}
    
    # Clean up expired error messages
    clean_error_messages()
    
    # Configuration directory
    config_dir = "../python_app/config"
    
    # Display sidebar with configuration files
    display_config_sidebar(config_dir)
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["Service Status", "Docker Compose Files", "Configuration Viewer"])
    
    # Load services configuration
    services_config = load_services_config()
    
    # Display content based on selected tab
    with tab1:
        display_service_status_tab(services_config)
    
    with tab2:
        display_docker_compose_tab()
    
    with tab3:
        display_config_viewer_tab()
    
    # Add JavaScript for fixing popup behavior and ensuring all components work properly
    st.markdown("""
    <script>
    // This script ensures all popups and interactive elements work correctly
    document.addEventListener('DOMContentLoaded', function() {
        // Function to initialize all popups and clickable elements
        function initializeUI() {
            // Make all headers with popup functionality clickable
            const headers = document.querySelectorAll('[id^="header_"]');
            headers.forEach(header => {
                const containerId = header.id.replace('header_', '');
                header.onclick = function() {
                    const popup = document.getElementById('popup_' + containerId);
                    if (popup) {
                        popup.style.display = 'block';
                    }
                };
            });
            
            // Make sure popups can be closed by clicking outside
            const popups = document.querySelectorAll('.modal');
            popups.forEach(popup => {
                popup.onclick = function(event) {
                    if (event.target === popup) {
                        popup.style.display = 'none';
                    }
                };
            });
        }
        
        // Initialize UI immediately
        initializeUI();
        
        // Also initialize after a short delay to ensure all elements are loaded
        setTimeout(initializeUI, 1000);
        
        // Set up a mutation observer to detect when new elements are added to the DOM
        const observer = new MutationObserver(function(mutations) {
            initializeUI();
        });
        
        // Start observing the document with the configured parameters
        observer.observe(document.body, { childList: true, subtree: true });
    });
    </script>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
