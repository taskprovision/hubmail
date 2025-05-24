"""
Pytest configuration for Taskinity tests.

This module contains fixtures and configuration for Taskinity tests.
"""
import os
import sys
import pytest
import tempfile
import logging
from pathlib import Path
from typing import Dict, Any, Generator, Tuple

# Add project root to sys.path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """
    Create a temporary directory for tests.
    
    Yields:
        Path to temporary directory
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def temp_env_file(temp_dir: Path) -> Tuple[Path, Dict[str, str]]:
    """
    Create a temporary .env file for tests.
    
    Args:
        temp_dir: Temporary directory
        
    Returns:
        Tuple of (path to .env file, environment variables dictionary)
    """
    env_vars = {
        "LOG_LEVEL": "DEBUG",
        "LOG_DIR": str(temp_dir / "logs"),
        "OUTPUT_DIR": str(temp_dir / "output"),
        "REPORT_FORMAT": "json,txt",
        "DB_TYPE": "sqlite",
        "DB_NAME": str(temp_dir / "test.db"),
        "API_TIMEOUT": "10",
        "API_RETRIES": "2",
        "TEST_INT": "42",
        "TEST_FLOAT": "3.14",
        "TEST_BOOL": "true",
        "TEST_LIST": "item1,item2,item3"
    }
    
    env_file = temp_dir / ".env"
    with open(env_file, "w") as f:
        for key, value in env_vars.items():
            f.write(f"{key}={value}\n")
    
    return env_file, env_vars


@pytest.fixture
def sample_dsl() -> str:
    """
    Create a sample DSL for tests.
    
    Returns:
        Sample DSL string
    """
    return """
flow TestFlow:
    description: "Test flow for unit tests"
    task1 -> task2
    task1 -> task3
    task2 -> task4
    task3 -> task4
"""


@pytest.fixture
def sample_flow_data() -> Dict[str, Any]:
    """
    Create sample flow data for tests.
    
    Returns:
        Sample flow data dictionary
    """
    return {
        "name": "TestFlow",
        "description": "Test flow for unit tests",
        "tasks": {
            "task1": {
                "name": "task1",
                "description": "Task 1",
                "inputs": [],
                "outputs": ["task2", "task3"]
            },
            "task2": {
                "name": "task2",
                "description": "Task 2",
                "inputs": ["task1"],
                "outputs": ["task4"]
            },
            "task3": {
                "name": "task3",
                "description": "Task 3",
                "inputs": ["task1"],
                "outputs": ["task4"]
            },
            "task4": {
                "name": "task4",
                "description": "Task 4",
                "inputs": ["task2", "task3"],
                "outputs": []
            }
        }
    }


@pytest.fixture
def mock_api_server(monkeypatch) -> None:
    """
    Mock API server for testing API clients.
    
    Args:
        monkeypatch: Pytest monkeypatch fixture
    """
    class MockResponse:
        def __init__(self, status_code=200, json_data=None, text="", headers=None):
            self.status_code = status_code
            self._json_data = json_data or {}
            self.text = text
            self.headers = headers or {"content-type": "application/json"}
        
        def json(self):
            return self._json_data
        
        def raise_for_status(self):
            if self.status_code >= 400:
                raise Exception(f"HTTP Error: {self.status_code}")
    
    def mock_request(*args, **kwargs):
        return MockResponse(json_data={"success": True, "data": {"test": "data"}})
    
    # Mock requests.request and requests.Session.request
    if "requests" in sys.modules:
        monkeypatch.setattr(sys.modules["requests"], "request", mock_request)
        monkeypatch.setattr(sys.modules["requests"].Session, "request", mock_request)


@pytest.fixture
def disable_logging() -> None:
    """Disable logging during tests."""
    logging.disable(logging.CRITICAL)
    yield
    logging.disable(logging.NOTSET)


@pytest.fixture
def clean_env(monkeypatch) -> None:
    """
    Clean environment variables for tests.
    
    Args:
        monkeypatch: Pytest monkeypatch fixture
    """
    # Save original environment
    original_environ = dict(os.environ)
    
    # Clear environment variables used in tests
    test_vars = [
        "LOG_LEVEL", "LOG_DIR", "OUTPUT_DIR", "REPORT_FORMAT",
        "DB_TYPE", "DB_NAME", "API_TIMEOUT", "API_RETRIES",
        "TEST_INT", "TEST_FLOAT", "TEST_BOOL", "TEST_LIST"
    ]
    
    for var in test_vars:
        monkeypatch.delenv(var, raising=False)
    
    yield
    
    # Restore original environment
    for var in test_vars:
        if var in original_environ:
            monkeypatch.setenv(var, original_environ[var])
        else:
            monkeypatch.delenv(var, raising=False)
