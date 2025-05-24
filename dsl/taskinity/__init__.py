"""
Taskinity - Inteligentny Framework do Orkiestracji Zadań.

Taskinity to nowoczesny framework do definiowania, zarządzania i monitorowania przepływów zadań
za pomocą intuicyjnego języka DSL i dekoratorów Python.
"""

__version__ = "0.1.0"

from taskinity.flow_dsl import task, run_flow_from_dsl, parse_dsl, save_dsl, load_dsl
from taskinity.parallel_executor import run_parallel_flow_from_dsl

__all__ = [
    "task",
    "run_flow_from_dsl",
    "parse_dsl",
    "save_dsl",
    "load_dsl",
    "run_parallel_flow_from_dsl",
]
