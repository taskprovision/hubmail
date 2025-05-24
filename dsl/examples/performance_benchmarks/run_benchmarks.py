#!/usr/bin/env python
"""
Performance Benchmarks for Taskinity.

This script runs performance benchmarks for Taskinity and compares it with
other workflow frameworks like Prefect, Airflow, and Luigi.
"""
import os
import sys
import time
import logging
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Callable

# Add project root to sys.path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from taskinity import task, flow, run_flow_from_dsl
from taskinity.utils.env_loader import load_env, get_env, get_list_env, get_int_env, get_bool_env
from taskinity.utils.benchmarks import PerformanceBenchmark, benchmark


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("benchmark.log")
    ]
)
logger = logging.getLogger(__name__)


# Load environment variables
env = load_env()
ITERATIONS = get_int_env("ITERATIONS", 10)
WARMUP_ITERATIONS = get_int_env("WARMUP_ITERATIONS", 2)
COMPARE_WITH_FRAMEWORKS = get_bool_env("COMPARE_WITH_FRAMEWORKS", True)
GENERATE_PLOTS = get_bool_env("GENERATE_PLOTS", True)
FRAMEWORKS_TO_COMPARE = get_list_env("FRAMEWORKS_TO_COMPARE", ["prefect", "airflow", "luigi"])
BENCHMARK_DIR = get_env("BENCHMARK_DIR", "benchmarks")


# Create benchmark directory if it doesn't exist
Path(BENCHMARK_DIR).mkdir(parents=True, exist_ok=True)


# Define sample tasks for benchmarking
@task(name="Process Data")
def process_data(data):
    """Process data by filtering and transforming."""
    # Simulate processing
    processed = []
    for item in data:
        if item % 2 == 0:  # Filter even numbers
            processed.append(item * 2)  # Transform
    return processed


@task(name="Analyze Data")
def analyze_data(data):
    """Analyze processed data."""
    # Simulate analysis
    total = sum(data)
    average = total / len(data) if data else 0
    minimum = min(data) if data else 0
    maximum = max(data) if data else 0
    return {
        "total": total,
        "average": average,
        "minimum": minimum,
        "maximum": maximum
    }


@task(name="Generate Report")
def generate_report(analysis):
    """Generate a report from the analysis."""
    # Simulate report generation
    report = []
    report.append(f"Total: {analysis['total']}")
    report.append(f"Average: {analysis['average']:.2f}")
    report.append(f"Minimum: {analysis['minimum']}")
    report.append(f"Maximum: {analysis['maximum']}")
    return "\n".join(report)


# Define sample flow DSL
SAMPLE_FLOW_DSL = """
flow DataProcessingFlow:
    description: "Sample data processing flow for benchmarking"
    process_data -> analyze_data
    analyze_data -> generate_report
"""


def run_taskinity_flow(data_size=1000):
    """Run a Taskinity flow for benchmarking."""
    # Generate sample data
    data = list(range(data_size))
    
    # Run flow
    result = run_flow_from_dsl(SAMPLE_FLOW_DSL, {"data": data})
    return result


# Mock implementations for other frameworks (for comparison)
def run_prefect_flow(data_size=1000):
    """Mock Prefect flow for benchmarking."""
    try:
        import prefect
        from prefect import task as prefect_task, Flow
        
        @prefect_task
        def prefect_process_data(data):
            processed = []
            for item in data:
                if item % 2 == 0:
                    processed.append(item * 2)
            return processed
        
        @prefect_task
        def prefect_analyze_data(data):
            total = sum(data)
            average = total / len(data) if data else 0
            minimum = min(data) if data else 0
            maximum = max(data) if data else 0
            return {
                "total": total,
                "average": average,
                "minimum": minimum,
                "maximum": maximum
            }
        
        @prefect_task
        def prefect_generate_report(analysis):
            report = []
            report.append(f"Total: {analysis['total']}")
            report.append(f"Average: {analysis['average']:.2f}")
            report.append(f"Minimum: {analysis['minimum']}")
            report.append(f"Maximum: {analysis['maximum']}")
            return "\n".join(report)
        
        with Flow("DataProcessingFlow") as flow:
            data = list(range(data_size))
            processed = prefect_process_data(data)
            analysis = prefect_analyze_data(processed)
            report = prefect_generate_report(analysis)
        
        result = flow.run()
        return result.result[report].result
    
    except ImportError:
        logger.warning("Prefect is not installed. Using mock implementation.")
        # Mock implementation
        data = list(range(data_size))
        processed = process_data(data)
        analysis = analyze_data(processed)
        report = generate_report(analysis)
        return report


def run_airflow_flow(data_size=1000):
    """Mock Airflow flow for benchmarking."""
    try:
        from airflow import DAG
        from airflow.operators.python_operator import PythonOperator
        from datetime import datetime
        
        dag = DAG(
            "data_processing_flow",
            start_date=datetime.now(),
            schedule_interval=None
        )
        
        process_task = PythonOperator(
            task_id="process_data",
            python_callable=process_data,
            op_kwargs={"data": list(range(data_size))},
            dag=dag
        )
        
        analyze_task = PythonOperator(
            task_id="analyze_data",
            python_callable=analyze_data,
            op_kwargs={"data": "{{ task_instance.xcom_pull(task_ids='process_data') }}"},
            dag=dag
        )
        
        report_task = PythonOperator(
            task_id="generate_report",
            python_callable=generate_report,
            op_kwargs={"analysis": "{{ task_instance.xcom_pull(task_ids='analyze_data') }}"},
            dag=dag
        )
        
        process_task >> analyze_task >> report_task
        
        # In a real scenario, we would execute the DAG, but for benchmarking
        # we'll just simulate the execution
        data = list(range(data_size))
        processed = process_data(data)
        analysis = analyze_data(processed)
        report = generate_report(analysis)
        return report
    
    except ImportError:
        logger.warning("Airflow is not installed. Using mock implementation.")
        # Mock implementation
        data = list(range(data_size))
        processed = process_data(data)
        analysis = analyze_data(processed)
        report = generate_report(analysis)
        return report


def run_luigi_flow(data_size=1000):
    """Mock Luigi flow for benchmarking."""
    try:
        import luigi
        
        class ProcessData(luigi.Task):
            data_size = luigi.IntParameter(default=data_size)
            
            def output(self):
                return luigi.LocalTarget("processed_data.txt")
            
            def run(self):
                data = list(range(self.data_size))
                processed = []
                for item in data:
                    if item % 2 == 0:
                        processed.append(item * 2)
                
                with self.output().open("w") as f:
                    f.write("\n".join(map(str, processed)))
        
        class AnalyzeData(luigi.Task):
            data_size = luigi.IntParameter(default=data_size)
            
            def requires(self):
                return ProcessData(data_size=self.data_size)
            
            def output(self):
                return luigi.LocalTarget("analysis.txt")
            
            def run(self):
                with self.input().open("r") as f:
                    processed = list(map(int, f.read().strip().split("\n")))
                
                total = sum(processed)
                average = total / len(processed) if processed else 0
                minimum = min(processed) if processed else 0
                maximum = max(processed) if processed else 0
                
                analysis = {
                    "total": total,
                    "average": average,
                    "minimum": minimum,
                    "maximum": maximum
                }
                
                with self.output().open("w") as f:
                    f.write(str(analysis))
        
        class GenerateReport(luigi.Task):
            data_size = luigi.IntParameter(default=data_size)
            
            def requires(self):
                return AnalyzeData(data_size=self.data_size)
            
            def output(self):
                return luigi.LocalTarget("report.txt")
            
            def run(self):
                with self.input().open("r") as f:
                    analysis = eval(f.read())
                
                report = []
                report.append(f"Total: {analysis['total']}")
                report.append(f"Average: {analysis['average']:.2f}")
                report.append(f"Minimum: {analysis['minimum']}")
                report.append(f"Maximum: {analysis['maximum']}")
                
                with self.output().open("w") as f:
                    f.write("\n".join(report))
        
        # Run Luigi task
        luigi.build([GenerateReport(data_size=data_size)], local_scheduler=True)
        
        # Read the result
        with open("report.txt", "r") as f:
            report = f.read()
        
        # Clean up temporary files
        for file in ["processed_data.txt", "analysis.txt", "report.txt"]:
            if os.path.exists(file):
                os.remove(file)
        
        return report
    
    except ImportError:
        logger.warning("Luigi is not installed. Using mock implementation.")
        # Mock implementation
        data = list(range(data_size))
        processed = process_data(data)
        analysis = analyze_data(processed)
        report = generate_report(analysis)
        return report


def run_benchmarks(data_sizes=None, frameworks=None):
    """
    Run benchmarks for different data sizes and frameworks.
    
    Args:
        data_sizes: List of data sizes to benchmark
        frameworks: List of frameworks to benchmark
    """
    if data_sizes is None:
        data_sizes = [100, 1000, 10000]
    
    if frameworks is None:
        frameworks = ["taskinity"]
        if COMPARE_WITH_FRAMEWORKS:
            frameworks.extend(FRAMEWORKS_TO_COMPARE)
    
    # Create benchmark instance
    benchmark = PerformanceBenchmark(
        name="taskinity_workflow_benchmark",
        output_dir=BENCHMARK_DIR
    )
    
    # Map framework names to functions
    framework_functions = {
        "taskinity": run_taskinity_flow,
        "prefect": run_prefect_flow,
        "airflow": run_airflow_flow,
        "luigi": run_luigi_flow
    }
    
    # Run benchmarks for each framework and data size
    for data_size in data_sizes:
        logger.info(f"Running benchmarks for data size: {data_size}")
        
        for framework in frameworks:
            if framework not in framework_functions:
                logger.warning(f"Unknown framework: {framework}")
                continue
            
            func = framework_functions[framework]
            label = f"{framework}_{data_size}"
            
            try:
                benchmark.benchmark(
                    func=func,
                    args=(data_size,),
                    label=label,
                    iterations=ITERATIONS,
                    warmup=WARMUP_ITERATIONS
                )
            except Exception as e:
                logger.error(f"Error benchmarking {framework} with data size {data_size}: {str(e)}")
    
    # Save benchmark results
    benchmark.save()
    
    # Generate plots if requested
    if GENERATE_PLOTS:
        for data_size in data_sizes:
            labels = [f"{framework}_{data_size}" for framework in frameworks]
            benchmark.plot(labels=labels)
        
        # Generate comparison plots for each data size
        for data_size in data_sizes:
            labels = [f"{framework}_{data_size}" for framework in frameworks]
            benchmark.plot_comparison(
                labels=labels,
                output_file=f"comparison_{data_size}.png"
            )
    
    return benchmark


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Run Taskinity benchmarks")
    parser.add_argument(
        "--data-sizes",
        type=int,
        nargs="+",
        default=[100, 1000, 10000],
        help="Data sizes to benchmark"
    )
    parser.add_argument(
        "--frameworks",
        type=str,
        nargs="+",
        default=None,
        help="Frameworks to benchmark"
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=ITERATIONS,
        help="Number of iterations for each benchmark"
    )
    parser.add_argument(
        "--warmup",
        type=int,
        default=WARMUP_ITERATIONS,
        help="Number of warmup iterations"
    )
    parser.add_argument(
        "--no-plots",
        action="store_true",
        help="Disable plot generation"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=BENCHMARK_DIR,
        help="Output directory for benchmark results"
    )
    
    args = parser.parse_args()
    
    # Override environment variables with command-line arguments
    global ITERATIONS, WARMUP_ITERATIONS, GENERATE_PLOTS, BENCHMARK_DIR
    ITERATIONS = args.iterations
    WARMUP_ITERATIONS = args.warmup
    GENERATE_PLOTS = not args.no_plots
    BENCHMARK_DIR = args.output_dir
    
    # Run benchmarks
    benchmark = run_benchmarks(
        data_sizes=args.data_sizes,
        frameworks=args.frameworks
    )
    
    # Print summary
    logger.info("Benchmark Summary:")
    for label, results in benchmark.results.items():
        result = results[-1]  # Get the latest result
        logger.info(f"{label}: {result['mean']:.6f} seconds (mean)")


if __name__ == "__main__":
    main()
