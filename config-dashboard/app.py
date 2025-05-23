import os
import re
import yaml
import streamlit as st
import pandas as pd
import plotly.express as px
from dotenv import dotenv_values
from typing import Dict, List, Any, Optional, Tuple

# Set page config
st.set_page_config(
    page_title="HubMail Configuration Dashboard",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Styles
st.markdown("""
<style>
    .service-card {
        padding: 20px;
        border-radius: 5px;
        margin-bottom: 20px;
        background-color: #f0f2f6;
    }
    .env-section {
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 10px;
        background-color: #e6f3ff;
    }
    .highlight {
        background-color: #ffffcc;
        padding: 2px 5px;
        border-radius: 3px;
    }
</style>
""", unsafe_allow_html=True)

# Functions to parse configuration files
def parse_env_file(file_path: str) -> Dict[str, str]:
    """Parse .env file and return variables as dictionary"""
    if not os.path.exists(file_path):
        st.sidebar.error(f"File not found: {file_path}")
        return {}
    
    try:
        return dotenv_values(file_path)
    except Exception as e:
        st.sidebar.error(f"Error parsing .env file: {str(e)}")
        return {}

def parse_docker_compose(file_path: str) -> Dict[str, Any]:
    """Parse docker-compose.yml file and return as dictionary"""
    if not os.path.exists(file_path):
        st.sidebar.error(f"File not found: {file_path}")
        return {}
    
    try:
        with open(file_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        st.sidebar.error(f"Error parsing docker-compose.yml: {str(e)}")
        return {}

def find_env_vars_in_compose(compose_data: Dict[str, Any]) -> List[str]:
    """Find all environment variables referenced in docker-compose.yml"""
    env_vars = set()
    
    # Convert to string to find all ${VAR} patterns
    compose_str = str(compose_data)
    
    # Find all ${VAR} or ${VAR:-default} patterns
    matches = re.findall(r'\${([A-Za-z0-9_]+)(?::-[^}]*)?}', compose_str)
    env_vars.update(matches)
    
    return sorted(list(env_vars))

def get_service_ports(compose_data: Dict[str, Any]) -> Dict[str, List[str]]:
    """Extract port mappings for each service"""
    ports = {}
    
    if 'services' not in compose_data:
        return ports
    
    for service_name, service_config in compose_data['services'].items():
        if 'ports' in service_config:
            service_ports = []
            for port in service_config['ports']:
                if isinstance(port, str):
                    service_ports.append(port)
                elif isinstance(port, dict) and 'published' in port and 'target' in port:
                    service_ports.append(f"{port['published']}:{port['target']}")
            ports[service_name] = service_ports
    
    return ports

def get_service_environment(compose_data: Dict[str, Any]) -> Dict[str, List[str]]:
    """Extract environment variables for each service"""
    environments = {}
    
    if 'services' not in compose_data:
        return environments
    
    for service_name, service_config in compose_data['services'].items():
        if 'environment' in service_config:
            env_vars = []
            env_config = service_config['environment']
            
            if isinstance(env_config, list):
                env_vars = env_config
            elif isinstance(env_config, dict):
                for key, value in env_config.items():
                    env_vars.append(f"{key}={value}")
                    
            environments[service_name] = env_vars
    
    return environments

def get_service_volumes(compose_data: Dict[str, Any]) -> Dict[str, List[str]]:
    """Extract volume mappings for each service"""
    volumes = {}
    
    if 'services' not in compose_data:
        return volumes
    
    for service_name, service_config in compose_data['services'].items():
        if 'volumes' in service_config:
            service_volumes = []
            for volume in service_config['volumes']:
                if isinstance(volume, str):
                    service_volumes.append(volume)
                elif isinstance(volume, dict) and 'source' in volume and 'target' in volume:
                    service_volumes.append(f"{volume['source']}:{volume['target']}")
            volumes[service_name] = service_volumes
    
    return volumes

def get_service_dependencies(compose_data: Dict[str, Any]) -> Dict[str, List[str]]:
    """Extract dependencies for each service"""
    dependencies = {}
    
    if 'services' not in compose_data:
        return dependencies
    
    for service_name, service_config in compose_data['services'].items():
        service_deps = []
        
        # Check 'depends_on' field
        if 'depends_on' in service_config:
            deps = service_config['depends_on']
            if isinstance(deps, list):
                service_deps.extend(deps)
            elif isinstance(deps, dict):
                service_deps.extend(deps.keys())
                
        dependencies[service_name] = service_deps
    
    return dependencies

def render_env_value(key: str, value: str, env_vars: Dict[str, str]) -> str:
    """Render environment variable with actual values"""
    # Find ${VAR} or ${VAR:-default} patterns
    def replace_var(match):
        var_name = match.group(1)
        default_value = match.group(3) if match.group(3) else ""
        
        if var_name in env_vars:
            return env_vars[var_name]
        return default_value
    
    # Pattern to match ${VAR} or ${VAR:-default}
    pattern = r'\${([A-Za-z0-9_]+)(:-([^}]*))?}'
    
    return re.sub(pattern, replace_var, value)

def categorize_env_vars(env_vars: Dict[str, str]) -> Dict[str, Dict[str, str]]:
    """Categorize environment variables by prefix"""
    categories = {}
    
    for key, value in env_vars.items():
        # Find category based on prefix (before first _)
        parts = key.split('_', 1)
        if len(parts) > 1:
            category = parts[0]
        else:
            category = "OTHER"
            
        if category not in categories:
            categories[category] = {}
            
        categories[category][key] = value
    
    return categories

def main():
    # Header
    st.title("⚙️ HubMail Configuration Dashboard")
    st.markdown("Visualize all your configuration settings in one place")
    
    # Sidebar
    st.sidebar.title("Configuration Files")
    
    # File paths
    env_path = st.sidebar.text_input(".env file path", value="/app/.env")
    compose_path = st.sidebar.text_input("docker-compose.yml path", value="/app/docker-compose.yml")
    
    # Debug info
    with st.sidebar.expander("Debug Info"):
        st.write(f"Current working directory: {os.getcwd()}")
        st.write(f"Files in current directory: {os.listdir('.')}")
        st.write(f"Files in /app directory (if exists): {os.listdir('/app') if os.path.exists('/app') else 'Directory not found'}")
    
    # Load files
    env_vars = parse_env_file(env_path)
    compose_data = parse_docker_compose(compose_path)
    
    # Check if files were loaded
    files_loaded = len(env_vars) > 0 and len(compose_data) > 0
    
    if not files_loaded:
        st.warning("⚠️ Could not load configuration files. Please check the file paths.")
        return
    
    # Extract data
    env_vars_in_compose = find_env_vars_in_compose(compose_data)
    service_ports = get_service_ports(compose_data)
    service_environment = get_service_environment(compose_data)
    service_volumes = get_service_volumes(compose_data)
    service_dependencies = get_service_dependencies(compose_data)
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "🔧 Services", "🔍 Environment Variables"])
    
    # Dashboard tab
    with tab1:
        st.header("System Overview")
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Services", len(compose_data.get('services', {})))
        
        with col2:
            st.metric("Environment Variables", len(env_vars))
        
        with col3:
            st.metric("Volumes", len(compose_data.get('volumes', {})))
        
        with col4:
            st.metric("Networks", len(compose_data.get('networks', {})))
        
        # Service dependency graph
        st.subheader("Service Dependencies")
        
        if service_dependencies:
            # Create a graph using Plotly
            edges = []
            for service, deps in service_dependencies.items():
                for dep in deps:
                    edges.append((service, dep))
            
            if edges:
                import networkx as nx
                
                # Create a directed graph
                G = nx.DiGraph()
                
                # Add all services as nodes
                for service in compose_data.get('services', {}).keys():
                    G.add_node(service)
                
                # Add edges for dependencies
                for source, target in edges:
                    G.add_edge(source, target)
                
                # Get positions
                pos = nx.spring_layout(G)
                
                # Create edge trace
                edge_x = []
                edge_y = []
                for edge in G.edges():
                    x0, y0 = pos[edge[0]]
                    x1, y1 = pos[edge[1]]
                    edge_x.extend([x0, x1, None])
                    edge_y.extend([y0, y1, None])
                
                # Create node trace
                node_x = []
                node_y = []
                node_text = []
                for node in G.nodes():
                    x, y = pos[node]
                    node_x.append(x)
                    node_y.append(y)
                    node_text.append(node)
                
                # Create figure
                import plotly.graph_objects as go
                
                fig = go.Figure()
                
                # Add edges
                fig.add_trace(go.Scatter(
                    x=edge_x, y=edge_y,
                    line=dict(width=1, color='#888'),
                    hoverinfo='none',
                    mode='lines'
                ))
                
                # Add nodes
                fig.add_trace(go.Scatter(
                    x=node_x, y=node_y,
                    mode='markers+text',
                    text=node_text,
                    textposition="top center",
                    marker=dict(
                        size=20,
                        color='#007BFF',
                        line=dict(width=2, color='#000')
                    ),
                    hoverinfo='text',
                    hovertext=node_text
                ))
                
                # Update layout
                fig.update_layout(
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=20, l=5, r=5, t=40),
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No service dependencies found")
        else:
            st.info("No service dependencies found")
        
        # Environment variable categories
        st.subheader("Environment Variables by Category")
        
        categories = categorize_env_vars(env_vars)
        
        # Create data for pie chart
        category_counts = {category: len(vars) for category, vars in categories.items()}
        
        if category_counts:
            fig = px.pie(
                values=list(category_counts.values()),
                names=list(category_counts.keys()),
                title="Environment Variables by Category"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No environment variables found")
    
    # Services tab
    with tab2:
        st.header("Services Configuration")
        
        # Get all services
        services = compose_data.get('services', {})
        
        if not services:
            st.warning("No services found in docker-compose.yml")
        else:
            # Create a section for each service
            for service_name, service_config in services.items():
                with st.expander(f"Service: {service_name}", expanded=True):
                    # Service details
                    cols = st.columns(3)
                    
                    with cols[0]:
                        st.markdown(f"**Image:** `{service_config.get('image', 'Custom build')}`")
                    
                    with cols[1]:
                        st.markdown(f"**Container Name:** `{service_config.get('container_name', service_name)}`")
                    
                    with cols[2]:
                        st.markdown(f"**Restart Policy:** `{service_config.get('restart', 'no')}`")
                    
                    # Ports
                    if service_name in service_ports:
                        st.markdown("**Ports:**")
                        for port in service_ports[service_name]:
                            # Render with actual values
                            rendered_port = render_env_value("port", port, env_vars)
                            st.code(f"{port} → {rendered_port}")
                    
                    # Environment variables
                    if service_name in service_environment:
                        st.markdown("**Environment Variables:**")
                        env_df = []
                        
                        for env_var in service_environment[service_name]:
                            if "=" in env_var:
                                key, value = env_var.split("=", 1)
                                rendered_value = render_env_value(key, value, env_vars)
                                env_df.append({
                                    "Variable": key,
                                    "Value": value,
                                    "Rendered Value": rendered_value
                                })
                            else:
                                env_df.append({
                                    "Variable": env_var,
                                    "Value": "",
                                    "Rendered Value": ""
                                })
                        
                        if env_df:
                            st.dataframe(pd.DataFrame(env_df), hide_index=True)
                    
                    # Volumes
                    if service_name in service_volumes:
                        st.markdown("**Volumes:**")
                        for volume in service_volumes[service_name]:
                            # Render with actual values
                            rendered_volume = render_env_value("volume", volume, env_vars)
                            st.code(f"{volume} → {rendered_volume}")
                    
                    # Dependencies
                    if service_name in service_dependencies and service_dependencies[service_name]:
                        st.markdown("**Depends On:**")
                        st.write(", ".join(f"`{dep}`" for dep in service_dependencies[service_name]))
    
    # Environment Variables tab
    with tab3:
        st.header("Environment Variables")
        
        # Create a search box
        search = st.text_input("Search for variables", "")
        
        # Show variables used in docker-compose.yml
        st.subheader("Variables Used in docker-compose.yml")
        
        used_vars = []
        for var in env_vars_in_compose:
            value = env_vars.get(var, "Not set")
            used_vars.append({
                "Variable": var,
                "Value": value
            })
        
        if used_vars:
            # Filter by search term
            if search:
                filtered_vars = [v for v in used_vars if search.lower() in v["Variable"].lower() or search.lower() in v["Value"].lower()]
            else:
                filtered_vars = used_vars
                
            st.dataframe(pd.DataFrame(filtered_vars), hide_index=True)
        else:
            st.info("No environment variables found in docker-compose.yml")
        
        # Show all environment variables
        st.subheader("All Environment Variables")
        
        all_vars = []
        for var, value in env_vars.items():
            all_vars.append({
                "Variable": var,
                "Value": value,
                "Used in Compose": var in env_vars_in_compose
            })
        
        if all_vars:
            # Filter by search term
            if search:
                filtered_all_vars = [v for v in all_vars if search.lower() in v["Variable"].lower() or search.lower() in v["Value"].lower()]
            else:
                filtered_all_vars = all_vars
                
            st.dataframe(pd.DataFrame(filtered_all_vars), hide_index=True)
        else:
            st.info("No environment variables found")

if __name__ == "__main__":
    main()
