# Parallel Tasks Usage Guide

This example demonstrates how to use Taskinity's parallel execution capabilities to improve workflow performance.

## Setup

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

2. Make sure you have the latest version of Taskinity installed:

```bash
pip install -e ..
```

## Basic Parallel Execution

### Understanding the Example

The `basic_parallel.py` file demonstrates:
- How to define tasks that can run in parallel
- How to use the parallel executor
- How to compare sequential vs. parallel execution

### Running the Example

To run the basic parallel example:

```bash
python basic_parallel.py
```

This will execute the same flow in both sequential and parallel modes and display performance metrics.

## Advanced Parallel Features

### Thread Pool Executor

The example uses Python's `ThreadPoolExecutor` for parallel execution:

```python
from concurrent.futures import ThreadPoolExecutor
from taskinity import run_parallel_flow_from_dsl

# Create a thread pool executor with 4 workers
executor = ThreadPoolExecutor(max_workers=4)

# Run the flow with parallel execution
result = run_parallel_flow_from_dsl(FLOW_DSL, input_data, executor=executor)
```

### Process Pool Executor

For CPU-bound tasks, you can use `ProcessPoolExecutor` instead:

```python
from concurrent.futures import ProcessPoolExecutor
from taskinity import run_parallel_flow_from_dsl

# Create a process pool executor with 4 workers
executor = ProcessPoolExecutor(max_workers=4)

# Run the flow with parallel execution
result = run_parallel_flow_from_dsl(FLOW_DSL, input_data, executor=executor)
```

## Creating Your Own Parallel Flows

1. Define your tasks as usual with the `@task` decorator:

```python
from taskinity import task

@task()
def process_item(item):
    # Process a single item
    return processed_item
```

2. Create a flow DSL with parallel branches:

```python
PARALLEL_FLOW_DSL = """
flow DataProcessing:
    description: "Parallel data processing flow"
    fetch_data -> split_data
    split_data -> [process_batch_1, process_batch_2, process_batch_3]
    process_batch_1 -> merge_results
    process_batch_2 -> merge_results
    process_batch_3 -> merge_results
"""
```

3. Run the flow with a parallel executor:

```python
from concurrent.futures import ThreadPoolExecutor
from taskinity import run_parallel_flow_from_dsl

executor = ThreadPoolExecutor(max_workers=4)
result = run_parallel_flow_from_dsl(PARALLEL_FLOW_DSL, input_data, executor=executor)
```

## Best Practices

1. **Task Granularity**: Define tasks with appropriate granularity - too fine-grained tasks may have overhead, while too coarse-grained tasks limit parallelism.

2. **Resource Consideration**: Consider the nature of your tasks:
   - I/O-bound tasks: Use `ThreadPoolExecutor`
   - CPU-bound tasks: Use `ProcessPoolExecutor`

3. **Worker Count**: Set an appropriate number of workers based on:
   - Available CPU cores
   - Memory requirements
   - I/O constraints

4. **Shared Resources**: Be careful with tasks that access shared resources (databases, files) to avoid contention.

5. **Error Handling**: Implement proper error handling for parallel tasks to prevent silent failures.

## Performance Monitoring

The example includes performance monitoring code:

```python
import time

start_time = time.time()
result = run_parallel_flow_from_dsl(FLOW_DSL, input_data, executor=executor)
end_time = time.time()

print(f"Execution time: {end_time - start_time:.2f} seconds")
```

For more advanced monitoring, use the benchmarking utilities in `taskinity.utils.benchmarks`.

<!-- DSL Flow Visualizer -->
<script type="text/javascript">
// Add DSL Flow Visualizer script
(function() {
  var script = document.createElement('script');
  script.src = '/hubmail/dsl/static/js/dsl-flow-visualizer.js';
  script.async = true;
  script.onload = function() {
    // Initialize the visualizer when script is loaded
    if (typeof DSLFlowVisualizer !== 'undefined') {
      new DSLFlowVisualizer();
    }
  };
  document.head.appendChild(script);
  
  // Add CSS styles
  var style = document.createElement('style');
  style.textContent = `
    .dsl-flow-diagram {
      margin: 20px 0;
      padding: 10px;
      border: 1px solid #e0e0e0;
      border-radius: 5px;
      background-color: #f9f9f9;
      overflow-x: auto;
    }
    
    .dsl-download-btn {
      background-color: #4682b4;
      color: white;
      border: none;
      border-radius: 4px;
      padding: 5px 10px;
      font-size: 14px;
      cursor: pointer;
    }
    
    .dsl-download-btn:hover {
      background-color: #36648b;
    }
  `;
  document.head.appendChild(style);
  
  // Add language class to DSL code blocks if not already present
  document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('pre code').forEach(function(codeBlock) {
      var content = codeBlock.textContent.trim();
      if (content.startsWith('flow ') && !codeBlock.classList.contains('language-dsl')) {
        codeBlock.classList.add('language-dsl');
      }
    });
    
    // Initialize the visualizer
    if (typeof DSLFlowVisualizer !== 'undefined') {
      new DSLFlowVisualizer();
    }
  });
})();
</script>
