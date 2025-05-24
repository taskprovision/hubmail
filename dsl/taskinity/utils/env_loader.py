"""
Environment variable loader for Taskinity.

This module provides utilities for loading and accessing environment variables
in a consistent way across Taskinity examples and projects.
"""
import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Union, List

# Check if dotenv is available
try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False


class EnvLoader:
    """Utility for loading and accessing environment variables."""
    
    def __init__(self, env_file: Optional[str] = None, load_from_file: bool = True):
        """
        Initialize the environment loader.
        
        Args:
            env_file: Path to .env file (optional)
            load_from_file: Whether to load variables from .env file (default: True)
        """
        self.logger = logging.getLogger(__name__)
        self.env_vars: Dict[str, str] = {}
        
        # Load environment variables from file if requested
        if load_from_file:
            self._load_from_file(env_file)
        
        # Load environment variables from os.environ
        self._load_from_environ()
    
    def _load_from_file(self, env_file: Optional[str] = None) -> None:
        """
        Load environment variables from .env file.
        
        Args:
            env_file: Path to .env file (optional)
        """
        if not DOTENV_AVAILABLE:
            self.logger.warning("python-dotenv is not installed. Environment variables will not be loaded from file.")
            self.logger.warning("Install with: pip install python-dotenv")
            return
        
        # Find .env file
        if env_file is None:
            # Look for .env file in current directory and parent directories
            current_dir = Path.cwd()
            env_path = current_dir / ".env"
            
            while not env_path.exists() and current_dir != current_dir.parent:
                current_dir = current_dir.parent
                env_path = current_dir / ".env"
            
            if env_path.exists():
                env_file = str(env_path)
        
        # Load environment variables from file
        if env_file is not None and Path(env_file).exists():
            load_dotenv(env_file)
            self.logger.info(f"Loaded environment variables from {env_file}")
        else:
            self.logger.warning(f"Environment file not found: {env_file}")
    
    def _load_from_environ(self) -> None:
        """Load environment variables from os.environ."""
        self.env_vars = dict(os.environ)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get environment variable value.
        
        Args:
            key: Environment variable name
            default: Default value if not found (optional)
            
        Returns:
            Environment variable value or default
        """
        return self.env_vars.get(key, default)
    
    def get_required(self, key: str) -> str:
        """
        Get required environment variable value.
        
        Args:
            key: Environment variable name
            
        Returns:
            Environment variable value
            
        Raises:
            ValueError: If environment variable is not set
        """
        value = self.get(key)
        if value is None:
            raise ValueError(f"Required environment variable not set: {key}")
        return value
    
    def get_int(self, key: str, default: Optional[int] = None) -> Optional[int]:
        """
        Get environment variable as integer.
        
        Args:
            key: Environment variable name
            default: Default value if not found or not convertible to int (optional)
            
        Returns:
            Environment variable value as integer or default
        """
        value = self.get(key)
        if value is None:
            return default
        
        try:
            return int(value)
        except ValueError:
            self.logger.warning(f"Environment variable {key} is not a valid integer: {value}")
            return default
    
    def get_float(self, key: str, default: Optional[float] = None) -> Optional[float]:
        """
        Get environment variable as float.
        
        Args:
            key: Environment variable name
            default: Default value if not found or not convertible to float (optional)
            
        Returns:
            Environment variable value as float or default
        """
        value = self.get(key)
        if value is None:
            return default
        
        try:
            return float(value)
        except ValueError:
            self.logger.warning(f"Environment variable {key} is not a valid float: {value}")
            return default
    
    def get_bool(self, key: str, default: Optional[bool] = None) -> Optional[bool]:
        """
        Get environment variable as boolean.
        
        Args:
            key: Environment variable name
            default: Default value if not found (optional)
            
        Returns:
            Environment variable value as boolean or default
        """
        value = self.get(key)
        if value is None:
            return default
        
        return value.lower() in ("true", "yes", "1", "y", "t")
    
    def get_list(self, key: str, separator: str = ",", default: Optional[List[str]] = None) -> Optional[List[str]]:
        """
        Get environment variable as list.
        
        Args:
            key: Environment variable name
            separator: Separator for list items (default: ",")
            default: Default value if not found (optional)
            
        Returns:
            Environment variable value as list or default
        """
        value = self.get(key)
        if value is None:
            return default
        
        return [item.strip() for item in value.split(separator)]
    
    def set(self, key: str, value: str) -> None:
        """
        Set environment variable.
        
        Args:
            key: Environment variable name
            value: Environment variable value
        """
        os.environ[key] = value
        self.env_vars[key] = value
    
    def as_dict(self) -> Dict[str, str]:
        """
        Get all environment variables as dictionary.
        
        Returns:
            Dictionary of environment variables
        """
        return self.env_vars.copy()


# Global environment loader instance
_env_loader = None


def load_env(env_file: Optional[str] = None) -> EnvLoader:
    """
    Load environment variables.
    
    Args:
        env_file: Path to .env file (optional)
        
    Returns:
        Environment loader instance
    """
    global _env_loader
    
    if _env_loader is None:
        _env_loader = EnvLoader(env_file=env_file)
    
    return _env_loader


def get_env(key: str, default: Any = None) -> Any:
    """
    Get environment variable value.
    
    Args:
        key: Environment variable name
        default: Default value if not found (optional)
        
    Returns:
        Environment variable value or default
    """
    return load_env().get(key, default)


def get_required_env(key: str) -> str:
    """
    Get required environment variable value.
    
    Args:
        key: Environment variable name
        
    Returns:
        Environment variable value
        
    Raises:
        ValueError: If environment variable is not set
    """
    return load_env().get_required(key)


def get_int_env(key: str, default: Optional[int] = None) -> Optional[int]:
    """
    Get environment variable as integer.
    
    Args:
        key: Environment variable name
        default: Default value if not found or not convertible to int (optional)
        
    Returns:
        Environment variable value as integer or default
    """
    return load_env().get_int(key, default)


def get_float_env(key: str, default: Optional[float] = None) -> Optional[float]:
    """
    Get environment variable as float.
    
    Args:
        key: Environment variable name
        default: Default value if not found or not convertible to float (optional)
        
    Returns:
        Environment variable value as float or default
    """
    return load_env().get_float(key, default)


def get_bool_env(key: str, default: Optional[bool] = None) -> Optional[bool]:
    """
    Get environment variable as boolean.
    
    Args:
        key: Environment variable name
        default: Default value if not found (optional)
        
    Returns:
        Environment variable value as boolean or default
    """
    return load_env().get_bool(key, default)


def get_list_env(key: str, separator: str = ",", default: Optional[List[str]] = None) -> Optional[List[str]]:
    """
    Get environment variable as list.
    
    Args:
        key: Environment variable name
        separator: Separator for list items (default: ",")
        default: Default value if not found (optional)
        
    Returns:
        Environment variable value as list or default
    """
    return load_env().get_list(key, separator, default)


def set_env(key: str, value: str) -> None:
    """
    Set environment variable.
    
    Args:
        key: Environment variable name
        value: Environment variable value
    """
    load_env().set(key, value)


def env_as_dict() -> Dict[str, str]:
    """
    Get all environment variables as dictionary.
    
    Returns:
        Dictionary of environment variables
    """
    return load_env().as_dict()
