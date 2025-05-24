"""
Taskinity - Inteligentny Framework do Orkiestracji Zadań.

Taskinity to nowoczesny framework do definiowania, zarządzania i monitorowania przepływów zadań
za pomocą intuicyjnego języka DSL i dekoratorów Python.
"""

__version__ = "0.1.0"

# Core functionality
from taskinity.flow_dsl import task, flow, run_flow_from_dsl, parse_dsl, save_dsl, load_dsl, list_dsl_files, list_flows
from taskinity.parallel_executor import run_parallel_flow_from_dsl, ParallelFlowExecutor

# Visualization and monitoring
from taskinity.flow_visualizer import generate_mermaid_from_dsl, generate_ascii_diagram, visualize_flow

# Scheduling and automation
from taskinity.flow_scheduler import FlowSchedule, create_schedule, list_schedules, delete_schedule, start_scheduler, stop_scheduler, FlowScheduler

# Notifications
from taskinity.notification_service import notify_flow_status, configure_notifications, test_notification

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
from taskinity.utils import timed_execution, retry, cache_result, setup_logger
from taskinity.examples import list_examples, list_templates, create_examples_directory, create_templates_directory

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
    "list_examples",
    "list_templates",
    "create_examples_directory",
    "create_templates_directory",
]
