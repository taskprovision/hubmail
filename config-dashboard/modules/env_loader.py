#!/usr/bin/env python3
# env_loader.py - Load environment variables from .env file

import os
import dotenv
from typing import Dict, Any, Optional

def load_env_vars(env_file: str = "config.env") -> Dict[str, str]:
    """Load environment variables from .env file"""
    # Load environment variables from .env file
    dotenv.load_dotenv(env_file)
    
    # Return a dictionary of environment variables
    env_vars = {
        # Server settings
        "DASHBOARD_PORT": os.getenv("DASHBOARD_PORT", "8502"),
        "API_PORT": os.getenv("API_PORT", "8000"),
        "UI_PORT": os.getenv("UI_PORT", "8501"),
        "API_HOST": os.getenv("API_HOST", "localhost"),
        "UI_HOST": os.getenv("UI_HOST", "localhost"),
        
        # Log settings
        "LOG_LINES": os.getenv("LOG_LINES", "100"),
        "LOG_TIMEOUT_SECONDS": os.getenv("LOG_TIMEOUT_SECONDS", "10"),
        
        # Docker settings
        "DOCKER_NETWORK": os.getenv("DOCKER_NETWORK", "hubmail_network"),
        
        # Service names
        "EMAIL_SERVICE_CONTAINER": os.getenv("EMAIL_SERVICE_CONTAINER", "email-app"),
        "API_SERVICE_CONTAINER": os.getenv("API_SERVICE_CONTAINER", "api-app"),
        "UI_SERVICE_CONTAINER": os.getenv("UI_SERVICE_CONTAINER", "ui-app"),
        "DB_SERVICE_CONTAINER": os.getenv("DB_SERVICE_CONTAINER", "postgres-db"),
        "OLLAMA_SERVICE_CONTAINER": os.getenv("OLLAMA_SERVICE_CONTAINER", "ollama"),
        
        # Config paths
        "CONFIG_DIR": os.getenv("CONFIG_DIR", "../python_app/config")
    }
    
    return env_vars
