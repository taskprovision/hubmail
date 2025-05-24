"""
Tests for the environment variable loader utility.
"""
import os
import pytest
from pathlib import Path
from taskinity.utils.env_loader import (
    EnvLoader,
    load_env,
    get_env,
    get_required_env,
    get_int_env,
    get_float_env,
    get_bool_env,
    get_list_env,
    set_env
)


class TestEnvLoader:
    """Tests for the EnvLoader class."""
    
    def test_init_without_file(self, clean_env):
        """Test initialization without env file."""
        loader = EnvLoader(load_from_file=False)
        assert isinstance(loader.env_vars, dict)
    
    def test_load_from_file(self, temp_env_file, clean_env):
        """Test loading environment variables from file."""
        env_file, env_vars = temp_env_file
        
        # Load environment variables from file
        loader = EnvLoader(env_file=str(env_file))
        
        # Check if environment variables were loaded
        for key, value in env_vars.items():
            assert loader.get(key) == value
    
    def test_get(self, temp_env_file, clean_env):
        """Test getting environment variables."""
        env_file, env_vars = temp_env_file
        loader = EnvLoader(env_file=str(env_file))
        
        # Test getting existing variable
        assert loader.get("LOG_LEVEL") == "DEBUG"
        
        # Test getting non-existent variable
        assert loader.get("NON_EXISTENT") is None
        
        # Test getting non-existent variable with default
        assert loader.get("NON_EXISTENT", "default") == "default"
    
    def test_get_required(self, temp_env_file, clean_env):
        """Test getting required environment variables."""
        env_file, env_vars = temp_env_file
        loader = EnvLoader(env_file=str(env_file))
        
        # Test getting existing variable
        assert loader.get_required("LOG_LEVEL") == "DEBUG"
        
        # Test getting non-existent variable
        with pytest.raises(ValueError):
            loader.get_required("NON_EXISTENT")
    
    def test_get_int(self, temp_env_file, clean_env):
        """Test getting environment variables as integers."""
        env_file, env_vars = temp_env_file
        loader = EnvLoader(env_file=str(env_file))
        
        # Test getting existing variable
        assert loader.get_int("TEST_INT") == 42
        
        # Test getting non-existent variable
        assert loader.get_int("NON_EXISTENT") is None
        
        # Test getting non-existent variable with default
        assert loader.get_int("NON_EXISTENT", 100) == 100
        
        # Test getting variable with invalid integer value
        set_env("INVALID_INT", "not_an_int")
        assert loader.get_int("INVALID_INT", 100) == 100
    
    def test_get_float(self, temp_env_file, clean_env):
        """Test getting environment variables as floats."""
        env_file, env_vars = temp_env_file
        loader = EnvLoader(env_file=str(env_file))
        
        # Test getting existing variable
        assert loader.get_float("TEST_FLOAT") == 3.14
        
        # Test getting non-existent variable
        assert loader.get_float("NON_EXISTENT") is None
        
        # Test getting non-existent variable with default
        assert loader.get_float("NON_EXISTENT", 2.71) == 2.71
        
        # Test getting variable with invalid float value
        set_env("INVALID_FLOAT", "not_a_float")
        assert loader.get_float("INVALID_FLOAT", 2.71) == 2.71
    
    def test_get_bool(self, temp_env_file, clean_env):
        """Test getting environment variables as booleans."""
        env_file, env_vars = temp_env_file
        loader = EnvLoader(env_file=str(env_file))
        
        # Test getting existing variable
        assert loader.get_bool("TEST_BOOL") is True
        
        # Test getting non-existent variable
        assert loader.get_bool("NON_EXISTENT") is None
        
        # Test getting non-existent variable with default
        assert loader.get_bool("NON_EXISTENT", False) is False
        
        # Test different boolean values
        boolean_values = {
            "true": True,
            "True": True,
            "TRUE": True,
            "yes": True,
            "Yes": True,
            "YES": True,
            "1": True,
            "y": True,
            "Y": True,
            "t": True,
            "T": True,
            "false": False,
            "False": False,
            "FALSE": False,
            "no": False,
            "No": False,
            "NO": False,
            "0": False,
            "n": False,
            "N": False,
            "f": False,
            "F": False
        }
        
        for value, expected in boolean_values.items():
            set_env("TEST_BOOL", value)
            assert loader.get_bool("TEST_BOOL") is expected
    
    def test_get_list(self, temp_env_file, clean_env):
        """Test getting environment variables as lists."""
        env_file, env_vars = temp_env_file
        loader = EnvLoader(env_file=str(env_file))
        
        # Test getting existing variable
        assert loader.get_list("TEST_LIST") == ["item1", "item2", "item3"]
        
        # Test getting non-existent variable
        assert loader.get_list("NON_EXISTENT") is None
        
        # Test getting non-existent variable with default
        assert loader.get_list("NON_EXISTENT", ["default"]) == ["default"]
        
        # Test with different separators
        set_env("TEST_LIST_SEMICOLON", "item1;item2;item3")
        assert loader.get_list("TEST_LIST_SEMICOLON", separator=";") == ["item1", "item2", "item3"]
        
        # Test with empty list
        set_env("TEST_LIST_EMPTY", "")
        assert loader.get_list("TEST_LIST_EMPTY") == [""]
    
    def test_set(self, clean_env):
        """Test setting environment variables."""
        loader = EnvLoader(load_from_file=False)
        
        # Set environment variable
        loader.set("TEST_SET", "test_value")
        
        # Check if environment variable was set
        assert loader.get("TEST_SET") == "test_value"
        assert os.environ.get("TEST_SET") == "test_value"
    
    def test_as_dict(self, temp_env_file, clean_env):
        """Test getting all environment variables as dictionary."""
        env_file, env_vars = temp_env_file
        loader = EnvLoader(env_file=str(env_file))
        
        # Get environment variables as dictionary
        env_dict = loader.as_dict()
        
        # Check if all environment variables are in the dictionary
        for key, value in env_vars.items():
            assert env_dict.get(key) == value


class TestEnvLoaderFunctions:
    """Tests for the environment loader utility functions."""
    
    def test_load_env(self, temp_env_file, clean_env):
        """Test loading environment variables."""
        env_file, env_vars = temp_env_file
        
        # Load environment variables
        loader = load_env(env_file=str(env_file))
        
        # Check if environment variables were loaded
        for key, value in env_vars.items():
            assert loader.get(key) == value
    
    def test_get_env(self, temp_env_file, clean_env):
        """Test getting environment variables."""
        env_file, env_vars = temp_env_file
        load_env(env_file=str(env_file))
        
        # Test getting existing variable
        assert get_env("LOG_LEVEL") == "DEBUG"
        
        # Test getting non-existent variable
        assert get_env("NON_EXISTENT") is None
        
        # Test getting non-existent variable with default
        assert get_env("NON_EXISTENT", "default") == "default"
    
    def test_get_required_env(self, temp_env_file, clean_env):
        """Test getting required environment variables."""
        env_file, env_vars = temp_env_file
        load_env(env_file=str(env_file))
        
        # Test getting existing variable
        assert get_required_env("LOG_LEVEL") == "DEBUG"
        
        # Test getting non-existent variable
        with pytest.raises(ValueError):
            get_required_env("NON_EXISTENT")
    
    def test_get_int_env(self, temp_env_file, clean_env):
        """Test getting environment variables as integers."""
        env_file, env_vars = temp_env_file
        load_env(env_file=str(env_file))
        
        # Test getting existing variable
        assert get_int_env("TEST_INT") == 42
        
        # Test getting non-existent variable
        assert get_int_env("NON_EXISTENT") is None
        
        # Test getting non-existent variable with default
        assert get_int_env("NON_EXISTENT", 100) == 100
    
    def test_get_float_env(self, temp_env_file, clean_env):
        """Test getting environment variables as floats."""
        env_file, env_vars = temp_env_file
        load_env(env_file=str(env_file))
        
        # Test getting existing variable
        assert get_float_env("TEST_FLOAT") == 3.14
        
        # Test getting non-existent variable
        assert get_float_env("NON_EXISTENT") is None
        
        # Test getting non-existent variable with default
        assert get_float_env("NON_EXISTENT", 2.71) == 2.71
    
    def test_get_bool_env(self, temp_env_file, clean_env):
        """Test getting environment variables as booleans."""
        env_file, env_vars = temp_env_file
        load_env(env_file=str(env_file))
        
        # Test getting existing variable
        assert get_bool_env("TEST_BOOL") is True
        
        # Test getting non-existent variable
        assert get_bool_env("NON_EXISTENT") is None
        
        # Test getting non-existent variable with default
        assert get_bool_env("NON_EXISTENT", False) is False
    
    def test_get_list_env(self, temp_env_file, clean_env):
        """Test getting environment variables as lists."""
        env_file, env_vars = temp_env_file
        load_env(env_file=str(env_file))
        
        # Test getting existing variable
        assert get_list_env("TEST_LIST") == ["item1", "item2", "item3"]
        
        # Test getting non-existent variable
        assert get_list_env("NON_EXISTENT") is None
        
        # Test getting non-existent variable with default
        assert get_list_env("NON_EXISTENT", default=["default"]) == ["default"]
    
    def test_set_env(self, clean_env):
        """Test setting environment variables."""
        load_env(load_from_file=False)
        
        # Set environment variable
        set_env("TEST_SET", "test_value")
        
        # Check if environment variable was set
        assert get_env("TEST_SET") == "test_value"
        assert os.environ.get("TEST_SET") == "test_value"
