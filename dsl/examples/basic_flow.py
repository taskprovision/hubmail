#!/usr/bin/env python3
"""
Basic flow example for Taskinity.
"""
import sys

# Check if running in mock mode
if '--mock' in sys.argv:
    # Create mock task decorator
    def task(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    
    # Create mock run_flow_from_dsl function
    def run_flow_from_dsl(flow_dsl, input_data):
        print(f"Running mock flow with input: {input_data}")
        return {
            "task1": {"result": input_data + " - processed by task1"},
            "task2": {"result": input_data + " - processed by task1 - processed by task2"},
            "task3": {"result": input_data + " - processed by task1 - processed by task2 - processed by task3"}
        }
else:
    # Import real Taskinity functionality
    try:
        from taskinity.core.taskinity_core import task, run_flow_from_dsl
    except ImportError:
        print("Error: Could not import Taskinity modules. Run with --mock flag for testing.")
        sys.exit(1)

@task(name="Task 1")
def task1(input_data):
    print("Executing task 1")
    return {"result": input_data + " - processed by task1"}

@task(name="Task 2")
def task2(input_data):
    print("Executing task 2")
    return {"result": input_data["result"] + " - processed by task2"}

@task(name="Task 3")
def task3(input_data):
    print("Executing task 3")
    return {"result": input_data["result"] + " - processed by task3"}

# Define the flow DSL
flow_dsl = """
flow BasicFlow:
    description: "Simple sequential flow"
    task1 -> task2 -> task3
"""

# Run the flow
result = run_flow_from_dsl(flow_dsl, "Input data")
print("\nFlow results:")
print(result)
print("\nFinal result:")
print(result["task3"]["result"])
