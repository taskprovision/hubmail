# Performance Benchmarks Usage Guide

This example demonstrates how to benchmark Taskinity's performance and compare it with other workflow frameworks.

## Setup

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

2. Optional: Install comparison frameworks if you want to benchmark against them:

```bash
# For Prefect comparison
pip install prefect

# For Airflow comparison
pip install apache-airflow

# For Luigi comparison
pip install luigi
```

## Running Benchmarks

### Basic Usage

To run a simple benchmark of Taskinity's performance:

```bash
python run_benchmarks.py
```

This will execute a series of benchmark tests and display the results in the console.

### Advanced Options

The benchmark script supports several command-line arguments:

```bash
python run_benchmarks.py --iterations 100 --compare-with prefect,airflow --output-file results.json
```

Available options:

- `--iterations`: Number of iterations for each benchmark (default: 10)
- `--compare-with`: Comma-separated list of frameworks to compare with (options: prefect, airflow, luigi)
- `--output-file`: File to save benchmark results (JSON format)
- `--plot`: Generate visualization plots of the results
- `--plot-file`: File to save the plot (PNG format)

## Interpreting Results

The benchmark results include:

- **Average Execution Time**: The mean time taken to execute the workflow
- **Median Execution Time**: The median time taken to execute the workflow
- **Min/Max Execution Time**: The minimum and maximum execution times
- **Standard Deviation**: Variation in execution times
- **Memory Usage**: Peak memory consumption during execution

## Customizing Benchmarks

You can create your own custom benchmarks by modifying the `run_benchmarks.py` file:

1. Define your custom tasks:

```python
@task()
def my_custom_task(data):
    # Your task implementation
    return processed_data
```

2. Create a custom flow DSL:

```python
CUSTOM_FLOW_DSL = """
flow CustomBenchmark:
    description: "Custom benchmark flow"
    task1 -> task2
    task2 -> task3
"""
```

3. Add your benchmark to the benchmark suite:

```python
benchmark.add_test(
    name="custom_benchmark",
    func=run_taskinity_flow,
    args=(CUSTOM_FLOW_DSL, test_data)
)
```

## Comparing with Other Frameworks

To ensure fair comparison with other frameworks:

1. Implement equivalent workflows in each framework
2. Use the same input data across all frameworks
3. Run benchmarks on the same hardware
4. Execute multiple iterations to account for variability

## Visualizing Results

When using the `--plot` option, the benchmark tool will generate visualizations showing:

- Bar charts comparing execution times across frameworks
- Line charts showing execution time distribution
- Memory usage comparison

These visualizations help identify performance patterns and bottlenecks in your workflows.
