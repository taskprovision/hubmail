#!/usr/bin/env python3
"""
HubMail Configuration Dashboard
A streamlit app to visualize and manage HubMail configurations and container status
"""

import streamlit as st
import os
import time
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

# Import our modules
from modules.docker_utils import get_container_logs, get_container_ports, get_resource_usage
from modules.ui_components import render_service_card
from modules.service_status import check_service_status, get_all_service_statuses, load_services_config
from modules.config_utils import load_config_files, categorize_config_files

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
    
    # Load configuration files
    config_files = load_config_files(config_dir)
    
    # Categorize configuration files
    categories = categorize_config_files(config_files)
    
    # Display configuration files by category
    for category, files in categories.items():
        if files:
            st.sidebar.subheader(category)
            for filename in sorted(files):
                if st.sidebar.button(filename, key=f"config_{filename}"):
                    st.session_state.selected_config = filename
                    st.session_state.config_data = config_files[filename]

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
    """Display configuration viewer tab"""
    if 'selected_config' in st.session_state and 'config_data' in st.session_state:
        st.subheader(f"Configuration: {st.session_state.selected_config}")
        
        # Display configuration data
        st.json(st.session_state.config_data)
    else:
        st.info("Select a configuration file from the sidebar to view its contents.")

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
    
    # Configuration directory
    config_dir = "../python_app/config"
    
    # Display sidebar with configuration files
    display_config_sidebar(config_dir)
    
    # Create tabs
    tab1, tab2 = st.tabs(["Service Status", "Configuration Viewer"])
    
    # Load services configuration
    services_config = load_services_config()
    
    # Display content based on selected tab
    with tab1:
        display_service_status_tab(services_config)
    
    with tab2:
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
