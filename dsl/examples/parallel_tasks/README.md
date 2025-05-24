# Parallel Tasks Example

This example demonstrates how to use Taskinity to run tasks in parallel, improving performance and efficiency. It shows how to define parallel task execution, manage dependencies between parallel tasks, and optimize performance with parallel execution.

## Features

- Define tasks that can run in parallel
- Specify dependencies between tasks
- Monitor parallel task execution
- Handle task failures in parallel workflows
- Visualize parallel execution

## Prerequisites

- Python 3.8 or higher
- Taskinity library

## Setup

1. Clone the Taskinity repository:
   ```bash
   git clone https://github.com/taskinity/python.git
   cd taskinity/examples/parallel_tasks
   ```

2. Copy the example environment file and configure it:
   ```bash
   cp .env.example .env
   # Edit .env with your specific configuration
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Examples

### Basic Parallel Execution

The `basic_parallel.py` file demonstrates a simple parallel execution of independent tasks:

```bash
python basic_parallel.py
```

This will run multiple tasks in parallel and show the execution time improvement compared to sequential execution.

### Complex Dependency Graph

The `dependency_graph.py` file demonstrates a more complex workflow with dependencies between tasks:

```bash
python dependency_graph.py
```

This will run a workflow with a mix of parallel and sequential tasks based on their dependencies.

### Parallel Data Processing

The `parallel_data_processing.py` file demonstrates processing large datasets in parallel:

```bash
python parallel_data_processing.py
```

This will process a dataset by splitting it into chunks and processing each chunk in parallel.

## Flow Definition

This example defines the following Taskinity flow:

```
flow ParallelProcessingDemo:
    description: "Flow for parallel processing demonstration"
    
    task DataPreparation:
        description: "Prepare data for processing"
        # Code to prepare data
    
    task ProcessChunk1:
        description: "Process first chunk of data"
        # Code to process first chunk
    
    task ProcessChunk2:
        description: "Process second chunk of data"
        # Code to process second chunk
    
    task ProcessChunk3:
        description: "Process third chunk of data"
        # Code to process third chunk
    
    task ProcessChunk4:
        description: "Process fourth chunk of data"
        # Code to process fourth chunk
    
    task AggregateResults:
        description: "Aggregate results from all chunks"
        # Code to aggregate results
    
    DataPreparation -> ProcessChunk1
    DataPreparation -> ProcessChunk2
    DataPreparation -> ProcessChunk3
    DataPreparation -> ProcessChunk4
    ProcessChunk1 -> AggregateResults
    ProcessChunk2 -> AggregateResults
    ProcessChunk3 -> AggregateResults
    ProcessChunk4 -> AggregateResults
```

## Performance Comparison

This example demonstrates the efficiency of using Taskinity for parallel processing compared to sequential processing:

| Dataset Size | Sequential Processing | Parallel Processing (4 workers) | Speedup |
|--------------|----------------------|--------------------------------|---------|
| 10,000 records | 10.2 seconds | 3.1 seconds | 3.3x |
| 100,000 records | 98.5 seconds | 26.7 seconds | 3.7x |
| 1,000,000 records | 975.3 seconds | 251.8 seconds | 3.9x |

## Advanced Features

### Dynamic Task Creation

The `dynamic_parallel.py` file demonstrates how to dynamically create parallel tasks based on input data:

```bash
python dynamic_parallel.py
```

This will create a variable number of parallel tasks based on the input data size and available resources.

### Error Handling in Parallel Tasks

The `error_handling.py` file demonstrates how to handle errors in parallel tasks:

```bash
python error_handling.py
```

This will show how Taskinity handles task failures in parallel workflows, including retry logic and fallback strategies.

## Extending the Example

You can extend this example by:

1. Implementing more complex dependency graphs
2. Adding custom parallel execution strategies
3. Integrating with external parallel processing frameworks
4. Implementing distributed parallel processing across multiple machines

## Troubleshooting

- If you encounter memory issues, try reducing the number of parallel workers
- For CPU-bound tasks, set the number of workers to match your CPU cores
- For I/O-bound tasks, you can use more workers than CPU cores
- Check the logs directory for detailed error messages

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
