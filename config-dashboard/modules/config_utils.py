#!/usr/bin/env python3
# config_utils.py - Configuration file handling utilities

import os
import yaml
import json
import streamlit as st
from typing import Dict, List, Any, Optional, Tuple
from modules.env_loader import load_env_vars

# Load environment variables
env_vars = load_env_vars()

def load_config_files(directory_path: str) -> Dict[str, Dict[str, Any]]:
    """Load all configuration files from a directory"""
    config_files = {}
    
    # Check if directory exists
    if not os.path.exists(directory_path):
        return config_files
    
    # List all files in the directory
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        
        # Skip directories
        if os.path.isdir(file_path):
            continue
        
        # Process based on file extension
        if filename.endswith('.yaml') or filename.endswith('.yml'):
            try:
                with open(file_path, 'r') as file:
                    config_data = yaml.safe_load(file)
                    config_files[filename] = config_data
            except Exception as e:
                st.sidebar.error(f"Error loading {filename}: {str(e)}")
        
        elif filename.endswith('.json'):
            try:
                with open(file_path, 'r') as file:
                    config_data = json.load(file)
                    config_files[filename] = config_data
            except Exception as e:
                st.sidebar.error(f"Error loading {filename}: {str(e)}")
        
        # Add other file types as needed
    
    return config_files

def categorize_config_files(config_files: Dict[str, Dict[str, Any]]) -> Dict[str, List[str]]:
    """Categorize configuration files based on their content or name"""
    categories = {
        "Docker": [],
        "Services": [],
        "Databases": [],
        "Other": []
    }
    
    for filename, config_data in config_files.items():
        # Categorize based on filename
        if 'docker' in filename.lower():
            categories["Docker"].append(filename)
        elif any(service in filename.lower() for service in ['service', 'app', 'api']):
            categories["Services"].append(filename)
        elif any(db in filename.lower() for db in ['db', 'database', 'sql', 'mongo']):
            categories["Databases"].append(filename)
        else:
            # Try to categorize based on content
            if isinstance(config_data, dict):
                if 'services' in config_data:
                    categories["Docker"].append(filename)
                elif 'database' in config_data or 'db' in config_data:
                    categories["Databases"].append(filename)
                else:
                    categories["Other"].append(filename)
            else:
                categories["Other"].append(filename)
    
    return categories
