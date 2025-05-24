"""
Taskinity - Intelligent Task Orchestration Framework.

Taskinity is a modern framework for defining, managing, and monitoring task flows
using an intuitive DSL and Python decorators. It provides tools for workflow visualization,
parallel execution, scheduling, and integration with external systems.
"""

__version__ = "0.1.0"

# Core functionality
from taskinity.core.taskinity_core import task, flow, run_flow_from_dsl, parse_dsl, save_dsl, load_dsl, list_dsl_files, list_flows, FlowStatus, REGISTRY
from taskinity.parallel_executor import run_parallel_flow_from_dsl, ParallelFlowExecutor

# Visualization and monitoring
from taskinity.flow_visualizer import generate_mermaid_from_dsl, generate_ascii_diagram, visualize_flow
from taskinity.execution_visualizer import visualize_execution, generate_execution_report

# Scheduling and automation
from taskinity.flow_scheduler import FlowSchedule, create_schedule, list_schedules, delete_schedule, start_scheduler, stop_scheduler, FlowScheduler

# Notifications
from taskinity.notification_service import notify_flow_status, configure_notifications, test_notification

# Data processing
from taskinity.data_processors import DataProcessor, CSVProcessor, JSONProcessor, DatabaseProcessor
from taskinity.data_transformers import DataTransformer, FilterTransformer, MapTransformer, ReduceTransformer

# API integration
from taskinity.api_client import APIClient, RESTClient, GraphQLClient, WebSocketClient

# API and web interface
try:
    from taskinity.api import TaskinityAPI, expose_flow, unexpose_flow, run_api_server
except ImportError:
    pass  # FastAPI not installed

try:
    from taskinity.dashboard import run_dashboard
except ImportError:
    pass  # Streamlit not installed

# Utils and examples
from taskinity.utils import timed_execution, retry, cache_result, setup_logger, validate_json, validate_schema
from taskinity.examples import list_examples, list_templates, create_examples_directory, create_templates_directory

# Extensions
try:
    from taskinity.extensions.mermaid_converter import convert_to_mermaid, export_as_svg, export_as_png
except ImportError:
    pass  # Optional dependencies not installed

try:
    from taskinity.extensions.code_converter import convert_code_to_taskinity, analyze_code_structure
except ImportError:
    pass  # Optional dependencies not installed

__all__ = [
    # Core
    "task",
    "flow",
    "run_flow_from_dsl",
    "parse_dsl",
    "save_dsl",
    "load_dsl",
    "list_dsl_files",
    "list_flows",
    "run_parallel_flow_from_dsl",
    "ParallelFlowExecutor",
    
    # Visualization
    "generate_mermaid_from_dsl",
    "generate_ascii_diagram",
    "visualize_flow",
    "visualize_execution",
    "generate_execution_report",
    
    # Scheduling
    "FlowSchedule",
    "create_schedule",
    "list_schedules",
    "delete_schedule",
    "start_scheduler",
    "stop_scheduler",
    "FlowScheduler",
    
    # Notifications
    "notify_flow_status",
    "configure_notifications",
    "test_notification",
    
    # Data Processing
    "DataProcessor",
    "CSVProcessor",
    "JSONProcessor",
    "DatabaseProcessor",
    "DataTransformer",
    "FilterTransformer",
    "MapTransformer",
    "ReduceTransformer",
    
    # API Integration
    "APIClient",
    "RESTClient",
    "GraphQLClient",
    "WebSocketClient",
    
    # API and Web
    "TaskinityAPI",
    "expose_flow",
    "unexpose_flow",
    "run_api_server",
    "run_dashboard",
    
    # Utils and Examples
    "timed_execution",
    "retry",
    "cache_result",
    "setup_logger",
    "validate_json",
    "validate_schema",
    "list_examples",
    "list_templates",
    "create_examples_directory",
    "create_templates_directory",
    
    # Extensions
    "convert_to_mermaid",
    "export_as_svg",
    "export_as_png",
    "convert_code_to_taskinity",
    "analyze_code_structure",
]
