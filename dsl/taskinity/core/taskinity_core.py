#!/usr/bin/env python3
"""
Taskinity Core - A simple framework for defining workflows using decorators and DSL.
Allows easy connection of functions into flows and monitoring their execution.
"""
import functools
import inspect
import json
import logging
import os
import re
import time
import traceback
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Type, Union

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("taskinity")

# Directories for logs and flow data
FLOW_DIR = os.getenv("FLOW_DIR", os.path.join(os.path.dirname(__file__), "..", "..", "flows"))
LOG_DIR = os.getenv("LOG_DIR", os.path.join(os.path.dirname(__file__), "..", "..", "logs"))
os.makedirs(FLOW_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

# Flow status types
class FlowStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"

# Registry of all registered functions
REGISTRY = {}

# Flow execution history
FLOW_HISTORY = []

def task(name: Optional[str] = None, 
         description: Optional[str] = None, 
         validate_input: Optional[Callable] = None,
         validate_output: Optional[Callable] = None):
    """
    Decorator for registering functions as tasks in a flow.
    
    Args:
        name: Optional task name (default: function name)
        description: Optional task description
        validate_input: Optional function for input data validation
        validate_output: Optional function for output data validation
    """
    def decorator(func):
        task_name = name or func.__name__
        task_desc = description or func.__doc__ or ""
        
        # Register function in the global registry
        REGISTRY[func.__name__] = {
            "name": task_name,
            "description": task_desc,
            "function": func,
            "signature": inspect.signature(func),
            "validate_input": validate_input,
            "validate_output": validate_output,
        }
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            task_id = f"{func.__name__}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
            logger.info(f"Starting task: {task_name}")
            
            # Save information about task start
            task_info = {
                "task_id": task_id,
                "name": task_name,
                "start_time": datetime.now().isoformat(),
                "status": FlowStatus.RUNNING,
                "args": str(args),
                "kwargs": str(kwargs),
            }
            
            # Input data validation
            if validate_input:
                try:
                    validate_input(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Input data validation error: {str(e)}")
                    task_info["status"] = FlowStatus.FAILED
                    task_info["error"] = str(e)
                    task_info["end_time"] = datetime.now().isoformat()
                    task_info["duration"] = time.time() - start_time
                    FLOW_HISTORY.append(task_info)
                    raise ValueError(f"Input data validation error: {str(e)}")
            
            # Execute function
            try:
                result = func(*args, **kwargs)
                
                # Output data validation
                if validate_output:
                    try:
                        validate_output(result)
                    except Exception as e:
                        logger.error(f"Output data validation error: {str(e)}")
                        task_info["status"] = FlowStatus.FAILED
                        task_info["error"] = str(e)
                        task_info["end_time"] = datetime.now().isoformat()
                        task_info["duration"] = time.time() - start_time
                        FLOW_HISTORY.append(task_info)
                        raise ValueError(f"Output data validation error: {str(e)}")
                
                # Save information about task completion
                task_info["status"] = FlowStatus.COMPLETED
                task_info["end_time"] = datetime.now().isoformat()
                task_info["duration"] = time.time() - start_time
                FLOW_HISTORY.append(task_info)
                
                logger.info(f"Task completed: {task_name} (duration: {task_info['duration']:.2f}s)")
                return result
            except Exception as e:
                # Save information about task failure
                task_info["status"] = FlowStatus.FAILED
                task_info["error"] = str(e)
                task_info["traceback"] = traceback.format_exc()
                task_info["end_time"] = datetime.now().isoformat()
                task_info["duration"] = time.time() - start_time
                FLOW_HISTORY.append(task_info)
                
                logger.error(f"Task failed: {task_name} - {str(e)}")
                raise
        
        return wrapper
    
    return decorator

def flow(name: Optional[str] = None, description: Optional[str] = None):
    """
    Decorator for defining a flow.
    
    Args:
        name: Optional flow name (default: function name)
        description: Optional flow description
    """
    def decorator(func):
        flow_name = name or func.__name__
        flow_desc = description or func.__doc__ or ""
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            flow_id = f"{flow_name}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
            logger.info(f"Starting flow: {flow_name}")
            
            # Save information about flow start
            flow_info = {
                "flow_id": flow_id,
                "name": flow_name,
                "description": flow_desc,
                "start_time": datetime.now().isoformat(),
                "status": FlowStatus.RUNNING,
                "args": str(args),
                "kwargs": str(kwargs),
                "tasks": [],
            }
            
            try:
                result = func(*args, **kwargs)
                
                # Save information about flow completion
                flow_info["status"] = FlowStatus.COMPLETED
                flow_info["end_time"] = datetime.now().isoformat()
                flow_info["duration"] = (
                    datetime.fromisoformat(flow_info["end_time"]) - 
                    datetime.fromisoformat(flow_info["start_time"])
                ).total_seconds()
                
                # Save flow tasks
                flow_info["tasks"] = [
                    task for task in FLOW_HISTORY 
                    if "start_time" in task and 
                    datetime.fromisoformat(task["start_time"]) >= datetime.fromisoformat(flow_info["start_time"])
                ]
                
                save_flow(flow_info)
                logger.info(f"Flow completed: {flow_name} (duration: {flow_info['duration']:.2f}s)")
                return result
            except Exception as e:
                # Save information about flow failure
                flow_info["status"] = FlowStatus.FAILED
                flow_info["error"] = str(e)
                flow_info["traceback"] = traceback.format_exc()
                flow_info["end_time"] = datetime.now().isoformat()
                flow_info["duration"] = (
                    datetime.fromisoformat(flow_info["end_time"]) - 
                    datetime.fromisoformat(flow_info["start_time"])
                ).total_seconds()
                
                # Save flow tasks
                flow_info["tasks"] = [
                    task for task in FLOW_HISTORY 
                    if "start_time" in task and 
                    datetime.fromisoformat(task["start_time"]) >= datetime.fromisoformat(flow_info["start_time"])
                ]
                
                save_flow(flow_info)
                logger.error(f"Flow failed: {flow_name} - {str(e)}")
                raise
        
        return wrapper
    
    return decorator

def save_flow(flow_info: Dict[str, Any]):
    """
    Save flow information to a JSON file.
    
    Args:
        flow_info: Flow information
    """
    flow_file = os.path.join(FLOW_DIR, f"{flow_info['flow_id']}.json")
    with open(flow_file, "w") as f:
        json.dump(flow_info, f, indent=2)

def load_flow(flow_id: str) -> Dict[str, Any]:
    """
    Load flow information from a JSON file.
    
    Args:
        flow_id: Flow identifier
    
    Returns:
        Flow information
    """
    flow_file = os.path.join(FLOW_DIR, f"{flow_id}.json")
    with open(flow_file, "r") as f:
        return json.load(f)

def list_flows() -> List[Dict[str, Any]]:
    """
    Return a list of all flows.
    
    Returns:
        List of flows
    """
    flows = []
    if os.path.exists(FLOW_DIR):
        for filename in os.listdir(FLOW_DIR):
            if filename.endswith(".json"):
                flow_id = filename.replace(".json", "")
                try:
                    flow_info = load_flow(flow_id)
                    flows.append(flow_info)
                except Exception as e:
                    logger.error(f"Error loading flow {flow_id}: {str(e)}")
    
    # Sort by start time (newest first)
    flows.sort(key=lambda x: x.get("start_time", ""), reverse=True)
    return flows

def parse_dsl(dsl_text: str) -> Dict[str, Any]:
    """
    Parse DSL text into a flow structure.
    
    Example DSL:
    ```
    flow EmailProcessing:
        description: "Email Processing"
        fetch_emails -> classify_emails
        classify_emails -> [urgent_emails, regular_emails]
        urgent_emails -> send_urgent_response
        regular_emails -> send_regular_response
    ```
    
    Args:
        dsl_text: DSL text
    
    Returns:
        Flow structure
    """
    lines = dsl_text.strip().split("\n")
    flow_structure = {
        "name": "",
        "description": "",
        "tasks": {},
        "connections": []
    }
    
    # Parse flow name
    flow_match = re.match(r"flow\s+(\w+):", lines[0])
    if flow_match:
        flow_structure["name"] = flow_match.group(1)
    
    # Parse flow description and connections
    for line in lines[1:]:
        line = line.strip()
        if not line:
            continue
        
        # Description
        desc_match = re.match(r'\s*description:\s*"([^"]*)"', line)
        if desc_match:
            flow_structure["description"] = desc_match.group(1)
            continue
        
        # Connection
        conn_match = re.match(r'\s*(\w+)\s*->\s*(\[.*\]|\w+)', line)
        if conn_match:
            source = conn_match.group(1)
            target_str = conn_match.group(2)
            
            # Multiple targets
            if target_str.startswith("[") and target_str.endswith("]"):
                targets = [t.strip() for t in target_str[1:-1].split(",")]
            else:
                targets = [target_str]
            
            for target in targets:
                flow_structure["connections"].append({
                    "source": source,
                    "target": target
                })
    
    # Build task list
    tasks = set()
    for conn in flow_structure["connections"]:
        tasks.add(conn["source"])
        tasks.add(conn["target"])
    
    # Add task information from registry
    for task_name in tasks:
        if task_name in REGISTRY:
            task_info = REGISTRY[task_name]
            flow_structure["tasks"][task_name] = {
                "name": task_info["name"],
                "description": task_info["description"]
            }
        else:
            flow_structure["tasks"][task_name] = {
                "name": task_name,
                "description": ""
            }
    
    return flow_structure

def run_flow_from_dsl(dsl_text: str, input_data: Dict[str, Any] = None, executor=None) -> Any:
    """
    Run a flow defined in DSL.
    
    Args:
        dsl_text: DSL text
        input_data: Input data for the flow
        executor: Optional executor for parallel execution
    
    Returns:
        Flow results
    """
    if input_data is None:
        input_data = {}
    
    flow_structure = parse_dsl(dsl_text)
    flow_name = flow_structure["name"]
    flow_desc = flow_structure["description"]
    
    # Create a flow ID
    flow_id = f"{flow_name}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    
    # Save information about flow start
    flow_info = {
        "flow_id": flow_id,
        "name": flow_name,
        "description": flow_desc,
        "start_time": datetime.now().isoformat(),
        "status": FlowStatus.RUNNING,
        "input_data": str(input_data),
        "tasks": [],
        "dsl": dsl_text
    }
    
    logger.info(f"Starting flow from DSL: {flow_name}")
    
    # Build dependency graph
    dependencies = {}
    for task_name in flow_structure["tasks"]:
        dependencies[task_name] = []
    
    for conn in flow_structure["connections"]:
        source = conn["source"]
        target = conn["target"]
        dependencies[target].append(source)
    
    # Check if all tasks are registered
    missing_tasks = []
    for task_name in flow_structure["tasks"]:
        if task_name not in REGISTRY:
            missing_tasks.append(task_name)
    
    if missing_tasks:
        error_msg = f"Missing task implementations: {', '.join(missing_tasks)}"
        logger.error(error_msg)
        
        # Save information about flow failure
        flow_info["status"] = FlowStatus.FAILED
        flow_info["error"] = error_msg
        flow_info["end_time"] = datetime.now().isoformat()
        flow_info["duration"] = (
            datetime.fromisoformat(flow_info["end_time"]) - 
            datetime.fromisoformat(flow_info["start_time"])
        ).total_seconds()
        
        save_flow(flow_info)
        raise ValueError(error_msg)
    
    # Execute flow
    def execute_flow():
        # Initialize task results
        results = {}
        
        # Find tasks with no dependencies (entry points)
        entry_points = [task for task, deps in dependencies.items() if not deps]
        
        if not entry_points:
            error_msg = "No entry points found in the flow"
            logger.error(error_msg)
            
            # Save information about flow failure
            flow_info["status"] = FlowStatus.FAILED
            flow_info["error"] = error_msg
            flow_info["end_time"] = datetime.now().isoformat()
            flow_info["duration"] = (
                datetime.fromisoformat(flow_info["end_time"]) - 
                datetime.fromisoformat(flow_info["start_time"])
            ).total_seconds()
            
            save_flow(flow_info)
            raise ValueError(error_msg)
        
        # Execute entry points with input data
        for entry_point in entry_points:
            task_func = REGISTRY[entry_point]["function"]
            sig = REGISTRY[entry_point]["signature"]
            
            # Prepare arguments
            kwargs = {}
            for param_name, param in sig.parameters.items():
                if param_name in input_data:
                    kwargs[param_name] = input_data[param_name]
            
            # Execute task
            try:
                results[entry_point] = task_func(**kwargs)
            except Exception as e:
                logger.error(f"Error executing task {entry_point}: {str(e)}")
                
                # Save information about flow failure
                flow_info["status"] = FlowStatus.FAILED
                flow_info["error"] = f"Error executing task {entry_point}: {str(e)}"
                flow_info["traceback"] = traceback.format_exc()
                flow_info["end_time"] = datetime.now().isoformat()
                flow_info["duration"] = (
                    datetime.fromisoformat(flow_info["end_time"]) - 
                    datetime.fromisoformat(flow_info["start_time"])
                ).total_seconds()
                
                # Save flow tasks
                flow_info["tasks"] = [
                    task for task in FLOW_HISTORY 
                    if "start_time" in task and 
                    datetime.fromisoformat(task["start_time"]) >= datetime.fromisoformat(flow_info["start_time"])
                ]
                
                save_flow(flow_info)
                raise
        
        # Remove entry points from dependencies
        for entry_point in entry_points:
            del dependencies[entry_point]
        
        # Execute remaining tasks in topological order
        while dependencies:
            # Find tasks whose dependencies are all executed
            executable_tasks = []
            for task_name, deps in list(dependencies.items()):
                if all(dep in results for dep in deps):
                    executable_tasks.append(task_name)
            
            if not executable_tasks:
                error_msg = "Circular dependency detected or missing tasks"
                logger.error(error_msg)
                
                # Save information about flow failure
                flow_info["status"] = FlowStatus.FAILED
                flow_info["error"] = error_msg
                flow_info["end_time"] = datetime.now().isoformat()
                flow_info["duration"] = (
                    datetime.fromisoformat(flow_info["end_time"]) - 
                    datetime.fromisoformat(flow_info["start_time"])
                ).total_seconds()
                
                # Save flow tasks
                flow_info["tasks"] = [
                    task for task in FLOW_HISTORY 
                    if "start_time" in task and 
                    datetime.fromisoformat(task["start_time"]) >= datetime.fromisoformat(flow_info["start_time"])
                ]
                
                save_flow(flow_info)
                raise ValueError(error_msg)
            
            # Execute tasks
            for task_name in executable_tasks:
                task_func = REGISTRY[task_name]["function"]
                sig = REGISTRY[task_name]["signature"]
                
                # Prepare arguments
                kwargs = {}
                for param_name, param in sig.parameters.items():
                    # Check if parameter is in input data
                    if param_name in input_data:
                        kwargs[param_name] = input_data[param_name]
                    
                    # Check if parameter is in results of dependencies
                    for dep in dependencies[task_name]:
                        if dep in results:
                            # If dependency result is a dictionary, check for matching keys
                            if isinstance(results[dep], dict) and param_name in results[dep]:
                                kwargs[param_name] = results[dep][param_name]
                            # If parameter name matches dependency name, use dependency result
                            elif param_name == dep:
                                kwargs[param_name] = results[dep]
                
                # Execute task
                try:
                    results[task_name] = task_func(**kwargs)
                except Exception as e:
                    logger.error(f"Error executing task {task_name}: {str(e)}")
                    
                    # Save information about flow failure
                    flow_info["status"] = FlowStatus.FAILED
                    flow_info["error"] = f"Error executing task {task_name}: {str(e)}"
                    flow_info["traceback"] = traceback.format_exc()
                    flow_info["end_time"] = datetime.now().isoformat()
                    flow_info["duration"] = (
                        datetime.fromisoformat(flow_info["end_time"]) - 
                        datetime.fromisoformat(flow_info["start_time"])
                    ).total_seconds()
                    
                    # Save flow tasks
                    flow_info["tasks"] = [
                        task for task in FLOW_HISTORY 
                        if "start_time" in task and 
                        datetime.fromisoformat(task["start_time"]) >= datetime.fromisoformat(flow_info["start_time"])
                    ]
                    
                    save_flow(flow_info)
                    raise
                
                # Remove task from dependencies
                del dependencies[task_name]
        
        # Save information about flow completion
        flow_info["status"] = FlowStatus.COMPLETED
        flow_info["end_time"] = datetime.now().isoformat()
        flow_info["duration"] = (
            datetime.fromisoformat(flow_info["end_time"]) - 
            datetime.fromisoformat(flow_info["start_time"])
        ).total_seconds()
        
        # Save flow tasks
        flow_info["tasks"] = [
            task for task in FLOW_HISTORY 
            if "start_time" in task and 
            datetime.fromisoformat(task["start_time"]) >= datetime.fromisoformat(flow_info["start_time"])
        ]
        
        save_flow(flow_info)
        logger.info(f"Flow completed: {flow_name} (duration: {flow_info['duration']:.2f}s)")
        
        # Return results of the last task
        if results:
            last_task = list(results.keys())[-1]
            return results[last_task]
        return None
    
    # Execute flow with optional executor
    if executor:
        # If an executor is provided, use it for parallel execution
        from taskinity.parallel_executor import run_parallel_flow
        return run_parallel_flow(flow_structure, input_data, executor)
    else:
        # Otherwise, execute sequentially
        return execute_flow()

def save_dsl(dsl_text: str, filename: str):
    """
    Save DSL text to a file.
    
    Args:
        dsl_text: DSL text
        filename: Filename
    """
    dsl_dir = os.path.join(os.path.dirname(__file__), "..", "..", "dsl_definitions")
    os.makedirs(dsl_dir, exist_ok=True)
    
    file_path = os.path.join(dsl_dir, filename)
    with open(file_path, "w") as f:
        f.write(dsl_text)

def load_dsl(filename: str) -> str:
    """
    Load DSL text from a file.
    
    Args:
        filename: Filename
    
    Returns:
        DSL text
    """
    # Check if the path is absolute
    if os.path.isabs(filename):
        if os.path.exists(filename):
            with open(filename, "r") as f:
                return f.read()
    else:
        # Check in the dsl_definitions directory
        dsl_dir = os.path.join(os.path.dirname(__file__), "..", "..", "dsl_definitions")
        dsl_path = os.path.join(dsl_dir, filename)
        
        if os.path.exists(dsl_path):
            with open(dsl_path, "r") as f:
                return f.read()
    
    raise FileNotFoundError(f"DSL file not found: {filename}")

def list_dsl_files() -> List[str]:
    """
    Return a list of all DSL files.
    
    Returns:
        List of DSL files
    """
    dsl_dir = os.path.join(os.path.dirname(__file__), "..", "..", "dsl_definitions")
    os.makedirs(dsl_dir, exist_ok=True)
    
    return [f for f in os.listdir(dsl_dir) if not f.startswith(".")]

# Example usage:
if __name__ == "__main__":
    # Example tasks
    @task(name="Fetch Emails", description="Fetches emails from IMAP server")
    def fetch_emails(server: str, username: str, password: str) -> List[Dict[str, Any]]:
        """Fetches emails from IMAP server."""
        logger.info(f"Fetching emails from {server} for user {username}")
        # Simulate fetching emails
        time.sleep(1)
        return [
            {"id": "1", "subject": "Important message", "body": "Content of important message", "urgent": True},
            {"id": "2", "subject": "Regular message", "body": "Content of regular message", "urgent": False},
        ]
    
    @task(name="Classify Emails", description="Classifies emails as urgent or regular")
    def classify_emails(emails: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Classifies emails as urgent or regular."""
        logger.info(f"Classifying {len(emails)} emails")
        # Simulate classification
        time.sleep(0.5)
        urgent = [email for email in emails if email.get("urgent", False)]
        regular = [email for email in emails if not email.get("urgent", False)]
        return {"urgent_emails": urgent, "regular_emails": regular}
    
    @task(name="Process Urgent Emails", description="Processes urgent emails")
    def process_urgent_emails(urgent_emails: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Processes urgent emails."""
        logger.info(f"Processing {len(urgent_emails)} urgent emails")
        # Simulate processing
        time.sleep(0.5)
        return [{"id": email["id"], "response": f"Urgent response to: {email['subject']}"} for email in urgent_emails]
    
    @task(name="Process Regular Emails", description="Processes regular emails")
    def process_regular_emails(regular_emails: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Processes regular emails."""
        logger.info(f"Processing {len(regular_emails)} regular emails")
        # Simulate processing
        time.sleep(0.5)
        return [{"id": email["id"], "response": f"Regular response to: {email['subject']}"} for email in regular_emails]
    
    # Example DSL flow
    dsl_text = """
    flow EmailProcessing:
        description: "Email Processing Flow"
        fetch_emails -> classify_emails
        classify_emails -> [process_urgent_emails, process_regular_emails]
    """
    
    # Save DSL to file
    save_dsl(dsl_text, "email_processing.dsl")
    
    # Run flow
    input_data = {
        "server": "imap.example.com",
        "username": "test@example.com",
        "password": "password123",
    }
    
    results = run_flow_from_dsl(dsl_text, input_data)
    print("Flow results:", results)
    
    # Display flow history
    flows = list_flows()
    print(f"Number of executed flows: {len(flows)}")
    for flow_info in flows:
        print(f"Flow: {flow_info['name']} (status: {flow_info['status']})")
