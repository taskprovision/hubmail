# Performance Benchmarks for Taskinity

This example demonstrates how to benchmark Taskinity workflows and compare them with other workflow frameworks like Prefect, Airflow, and Luigi.

## Overview

The performance benchmarking example includes:

1. A benchmarking utility for measuring execution time
2. Sample workflows implemented in Taskinity and other frameworks
3. Tools for generating comparison plots and reports
4. Command-line interface for customizing benchmark parameters

## Setup

1. Copy the environment configuration file:
   ```bash
   cp .env.example .env
   ```

2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. If you want to compare with other frameworks, install them:
   ```bash
   # For Prefect comparison
   pip install prefect==1.4.1
   
   # For Airflow comparison
   pip install apache-airflow==2.5.1
   
   # For Luigi comparison
   pip install luigi==3.1.1
   ```

## Running Benchmarks

### Basic Usage

Run the benchmarks with default settings:

```bash
python run_benchmarks.py
```

This will:
- Run benchmarks for Taskinity and any installed frameworks
- Test with data sizes of 100, 1000, and 10000 elements
- Perform 10 iterations with 2 warmup iterations
- Generate comparison plots in the `benchmarks` directory

### Custom Configuration

You can customize the benchmark parameters:

```bash
python run_benchmarks.py --data-sizes 500 5000 50000 --frameworks taskinity prefect --iterations 20 --warmup 5
```

Available options:
- `--data-sizes`: List of data sizes to benchmark
- `--frameworks`: List of frameworks to benchmark (taskinity, prefect, airflow, luigi)
- `--iterations`: Number of iterations for each benchmark
- `--warmup`: Number of warmup iterations
- `--no-plots`: Disable plot generation
- `--output-dir`: Output directory for benchmark results

## Benchmark Results

The benchmarks generate several outputs:

1. **JSON Results**: Complete benchmark data in JSON format
2. **Bar Charts**: Comparison of mean execution times for each framework
3. **Comparison Plots**: Multi-metric comparison (mean, median, min, max)
4. **Log File**: Detailed benchmark log in `benchmark.log`

Example output:

```
Benchmark Summary:
taskinity_100: 0.000532 seconds (mean)
prefect_100: 0.001245 seconds (mean)
airflow_100: 0.002134 seconds (mean)
luigi_100: 0.003521 seconds (mean)
taskinity_1000: 0.004532 seconds (mean)
prefect_1000: 0.009245 seconds (mean)
airflow_1000: 0.012134 seconds (mean)
luigi_1000: 0.023521 seconds (mean)
```

## Interpreting Results

The benchmark results show the execution time for each framework and data size. Lower values indicate better performance.

Key metrics:
- **Mean**: Average execution time across all iterations
- **Median**: Middle value of execution times (less affected by outliers)
- **Min/Max**: Fastest and slowest execution times
- **Standard Deviation**: Variation in execution times

## Extending Benchmarks

You can extend the benchmarks by:

1. Adding new workflow patterns to benchmark
2. Implementing additional frameworks for comparison
3. Creating custom metrics beyond execution time
4. Benchmarking specific components of your workflows

## Performance Optimization Tips

Based on benchmark results, consider these optimization strategies:

1. **Task Granularity**: Find the right balance between too many small tasks and too few large tasks
2. **Data Passing**: Minimize large data transfers between tasks
3. **Resource Usage**: Monitor CPU and memory usage during execution
4. **Parallelism**: Use parallel execution for independent tasks
5. **Caching**: Implement caching for expensive operations

## Troubleshooting

- **Missing Frameworks**: If a framework is not installed, the benchmark will use a mock implementation
- **Memory Issues**: For large data sizes, you may need to increase available memory
- **Plot Generation Errors**: Ensure matplotlib is installed with `pip install matplotlib`

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


<!-- Markdown Enhancements -->

<!-- Taskinity Markdown Enhancements -->
<!-- Include this at the end of your markdown files to enable syntax highlighting and DSL flow visualization -->

<!-- Prism.js for syntax highlighting -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism.min.css">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/plugins/line-numbers/prism-line-numbers.min.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/prism.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/plugins/line-numbers/prism-line-numbers.min.js"></script>

<!-- Load common language components -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-python.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-bash.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-javascript.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-yaml.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-json.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-markdown.min.js"></script>

<!-- Taskinity custom scripts -->
<script src="../../static/js/dsl-flow-visualizer.js"></script>
<script src="../../static/js/markdown-syntax-highlighter.js"></script>

<script>
  // Initialize both scripts when the page loads
  document.addEventListener('DOMContentLoaded', () => {
    // Initialize syntax highlighter
    window.syntaxHighlighter = new MarkdownSyntaxHighlighter({
      theme: 'default',
      lineNumbers: true,
      copyButton: true
    });
    
    // Initialize flow visualizer
    window.flowVisualizer = new DSLFlowVisualizer({
      codeBlockSelector: 'pre code.language-dsl, pre code.language-flow'
    });
  });
</script>

<!-- Custom styles for better markdown rendering -->
<style>
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
    line-height: 1.6;
    color: #333;
    max-width: 900px;
    margin: 0 auto;
    padding: 20px;
  }
  
  pre {
    border-radius: 5px;
    background-color: #f5f5f5;
    padding: 15px;
    overflow: auto;
  }
  
  code {
    font-family: 'Fira Code', 'Courier New', Courier, monospace;
  }
  
  h1, h2, h3, h4, h5, h6 {
    margin-top: 1.5em;
    margin-bottom: 0.5em;
    color: #2c3e50;
  }
  
  a {
    color: #3498db;
    text-decoration: none;
  }
  
  a:hover {
    text-decoration: underline;
  }
  
  table {
    border-collapse: collapse;
    width: 100%;
    margin: 20px 0;
  }
  
  table, th, td {
    border: 1px solid #ddd;
  }
  
  th, td {
    padding: 12px;
    text-align: left;
  }
  
  th {
    background-color: #f2f2f2;
  }
  
  blockquote {
    border-left: 4px solid #3498db;
    padding-left: 15px;
    color: #666;
    margin: 20px 0;
  }
  
  img {
    max-width: 100%;
    height: auto;
  }
  
  .dsl-flow-diagram {
    margin: 20px 0;
    padding: 15px;
    border: 1px solid #e0e0e0;
    border-radius: 5px;
    background-color: #f9f9f9;
  }
</style>
