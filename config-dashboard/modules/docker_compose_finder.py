#!/usr/bin/env python3
# docker_compose_finder.py - Find Docker Compose files in the project

import os
import subprocess
import yaml
import streamlit as st
from typing import Dict, List, Any, Optional, Tuple

def find_docker_compose_files(base_dir: str = "/home/tom/github/taskprovision/hubmail") -> List[str]:
    """Find all Docker Compose files in the project"""
    docker_compose_files = []
    
    try:
        # Use glob to find docker-compose files instead of the find command
        import glob
        
        # Find all docker-compose.yml files
        yml_files = glob.glob(f"{base_dir}/**/docker-compose*.yml", recursive=True)
        
        # Find all docker-compose.yaml files
        yaml_files = glob.glob(f"{base_dir}/**/docker-compose*.yaml", recursive=True)
        
        # Combine the results
        docker_compose_files = yml_files + yaml_files
        
        # If we didn't find any files, check just the base directory
        if not docker_compose_files:
            # Check for docker-compose.yml in the base directory
            if os.path.exists(os.path.join(base_dir, 'docker-compose.yml')):
                docker_compose_files.append(os.path.join(base_dir, 'docker-compose.yml'))
            
            # Check for docker-compose.yaml in the base directory
            if os.path.exists(os.path.join(base_dir, 'docker-compose.yaml')):
                docker_compose_files.append(os.path.join(base_dir, 'docker-compose.yaml'))
        
        return docker_compose_files
    except Exception as e:
        st.sidebar.error(f"Error finding Docker Compose files: {str(e)}")
        return []

def load_docker_compose_file(file_path: str) -> Dict[str, Any]:
    """Load a Docker Compose file and return its contents"""
    try:
        with open(file_path, 'r') as file:
            return yaml.safe_load(file)
    except Exception as e:
        st.sidebar.error(f"Error loading Docker Compose file {file_path}: {str(e)}")
        return {}

def get_services_from_compose_file(file_path: str) -> Dict[str, Dict[str, Any]]:
    """Get services defined in a Docker Compose file"""
    compose_data = load_docker_compose_file(file_path)
    services = {}
    
    if compose_data and 'services' in compose_data:
        for service_name, service_config in compose_data['services'].items():
            container_name = service_config.get('container_name', service_name)
            
            # Extract port mappings
            ports = []
            if 'ports' in service_config:
                ports = service_config['ports']
            
            # Extract environment variables
            environment = []
            if 'environment' in service_config:
                environment = service_config['environment']
            
            # Extract health check
            healthcheck = None
            if 'healthcheck' in service_config:
                healthcheck = service_config['healthcheck']
            
            # Create service config
            services[service_name] = {
                'container_name': container_name,
                'image': service_config.get('image', 'N/A'),
                'ports': ports,
                'environment': environment,
                'healthcheck': healthcheck,
                'depends_on': service_config.get('depends_on', []),
                'networks': service_config.get('networks', []),
                'volumes': service_config.get('volumes', []),
                'source_file': file_path
            }
    
    return services

def get_all_services() -> Dict[str, Dict[str, Any]]:
    """Get all services from all Docker Compose files"""
    base_dir = "/home/tom/github/taskprovision/hubmail"
    docker_compose_files = find_docker_compose_files(base_dir)
    
    all_services = {}
    for file_path in docker_compose_files:
        services = get_services_from_compose_file(file_path)
        for service_name, service_config in services.items():
            # If service already exists, update with the new config
            if service_name in all_services:
                all_services[f"{service_name} ({os.path.basename(file_path)})"] = service_config
            else:
                all_services[service_name] = service_config
    
    return all_services

def display_docker_compose_tabs():
    """Display tabs for each Docker Compose file"""
    try:
        base_dir = "/home/tom/github/taskprovision/hubmail"
        docker_compose_files = find_docker_compose_files(base_dir)
        
        if not docker_compose_files:
            st.warning("No Docker Compose files found in the project.")
            st.info("Checking for docker-compose.yml in the base directory...")
            
            # Check if docker-compose.yml exists in the base directory
            if os.path.exists(os.path.join(base_dir, 'docker-compose.yml')):
                docker_compose_files = [os.path.join(base_dir, 'docker-compose.yml')]
                st.success("Found docker-compose.yml in the base directory.")
            else:
                st.error("No Docker Compose files found in the project.")
                return
        
        # Create tabs for each Docker Compose file
        tab_names = [os.path.basename(file_path) for file_path in docker_compose_files]
        tabs = st.tabs(tab_names)
        
        # Display services for each Docker Compose file
        for i, file_path in enumerate(docker_compose_files):
            with tabs[i]:
                try:
                    st.subheader(f"Services in {os.path.basename(file_path)}")
                    st.caption(f"File path: {file_path}")
                    
                    # Check if file exists and is readable
                    if not os.path.exists(file_path):
                        st.error(f"File not found: {file_path}")
                        continue
                    
                    # Load services from the Docker Compose file
                    services = get_services_from_compose_file(file_path)
                    
                    if not services:
                        st.warning(f"No services found in {os.path.basename(file_path)}.")
                        
                        # Show the raw Docker Compose file even if no services found
                        with st.expander("View Raw Docker Compose File"):
                            try:
                                with open(file_path, 'r') as file:
                                    st.code(file.read(), language="yaml")
                            except Exception as e:
                                st.error(f"Error reading file: {str(e)}")
                        continue
                    
                    # Display services in a table
                    service_data = []
                    for service_name, service_config in services.items():
                        try:
                            ports = service_config.get('ports', [])
                            ports_str = ", ".join([str(p) for p in ports]) if ports else "None"
                            
                            service_data.append({
                                "Service": service_name,
                                "Container": service_config.get('container_name', service_name),
                                "Image": service_config.get('image', 'N/A'),
                                "Ports": ports_str,
                                "Health Check": "Yes" if service_config.get('healthcheck') else "No"
                            })
                        except Exception as e:
                            st.error(f"Error processing service {service_name}: {str(e)}")
                    
                    if service_data:
                        st.table(service_data)
                    else:
                        st.warning("Failed to process any services.")
                    
                    # Show the raw Docker Compose file
                    with st.expander("View Raw Docker Compose File"):
                        try:
                            with open(file_path, 'r') as file:
                                st.code(file.read(), language="yaml")
                        except Exception as e:
                            st.error(f"Error reading file: {str(e)}")
                except Exception as e:
                    st.error(f"Error processing tab {os.path.basename(file_path)}: {str(e)}")
    except Exception as e:
        st.error(f"Error displaying Docker Compose tabs: {str(e)}")
        st.info("Try refreshing the page or check if Docker Compose files are accessible.")
        return
