"""
Performance benchmarking utilities for Taskinity.

This module provides tools for measuring and comparing the performance of
Taskinity flows and tasks.
"""
import time
import json
import logging
import statistics
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Callable, Tuple
from functools import wraps
import matplotlib.pyplot as plt
import numpy as np


class PerformanceBenchmark:
    """Utility for benchmarking Taskinity flows and tasks."""
    
    def __init__(
        self,
        name: str,
        output_dir: str = "benchmarks",
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize the performance benchmark.
        
        Args:
            name: Benchmark name
            output_dir: Directory to store benchmark results
            logger: Logger instance (optional)
        """
        self.name = name
        self.output_dir = output_dir
        self.logger = logger or logging.getLogger(__name__)
        self.results: Dict[str, List[Dict[str, Any]]] = {}
        
        # Create output directory if it doesn't exist
        Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    def benchmark(
        self,
        func: Callable,
        args: Tuple = (),
        kwargs: Dict[str, Any] = None,
        label: Optional[str] = None,
        iterations: int = 10,
        warmup: int = 1
    ) -> Dict[str, Any]:
        """
        Benchmark a function.
        
        Args:
            func: Function to benchmark
            args: Arguments to pass to the function
            kwargs: Keyword arguments to pass to the function
            label: Label for the benchmark (default: function name)
            iterations: Number of iterations to run (default: 10)
            warmup: Number of warmup iterations (default: 1)
            
        Returns:
            Benchmark results
        """
        if kwargs is None:
            kwargs = {}
        
        label = label or func.__name__
        self.logger.info(f"Benchmarking {label} ({iterations} iterations, {warmup} warmup)")
        
        # Perform warmup iterations
        for _ in range(warmup):
            func(*args, **kwargs)
        
        # Perform benchmark iterations
        times = []
        for i in range(iterations):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            elapsed_time = end_time - start_time
            times.append(elapsed_time)
            self.logger.debug(f"Iteration {i+1}/{iterations}: {elapsed_time:.6f} seconds")
        
        # Calculate statistics
        benchmark_result = {
            "label": label,
            "iterations": iterations,
            "times": times,
            "min": min(times),
            "max": max(times),
            "mean": statistics.mean(times),
            "median": statistics.median(times),
            "stdev": statistics.stdev(times) if len(times) > 1 else 0,
            "timestamp": time.time()
        }
        
        # Store results
        if label not in self.results:
            self.results[label] = []
        
        self.results[label].append(benchmark_result)
        
        self.logger.info(f"Benchmark {label} completed: {benchmark_result['mean']:.6f} seconds (mean)")
        return benchmark_result
    
    def compare(self, labels: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Compare benchmark results.
        
        Args:
            labels: Labels to compare (default: all labels)
            
        Returns:
            Comparison results
        """
        if not self.results:
            self.logger.warning("No benchmark results to compare")
            return {}
        
        if labels is None:
            labels = list(self.results.keys())
        
        comparison = {}
        for label in labels:
            if label not in self.results:
                self.logger.warning(f"Label {label} not found in benchmark results")
                continue
            
            # Get the latest benchmark result
            result = self.results[label][-1]
            comparison[label] = {
                "mean": result["mean"],
                "median": result["median"],
                "min": result["min"],
                "max": result["max"],
                "stdev": result["stdev"]
            }
        
        # Calculate relative performance
        if len(comparison) > 1:
            baseline = min(comparison.items(), key=lambda x: x[1]["mean"])
            baseline_label, baseline_result = baseline
            
            for label, result in comparison.items():
                if label != baseline_label:
                    result["relative"] = result["mean"] / baseline_result["mean"]
                    result["percent_slower"] = (result["relative"] - 1) * 100
        
        return comparison
    
    def save(self, filename: Optional[str] = None) -> str:
        """
        Save benchmark results to a file.
        
        Args:
            filename: Output filename (default: {name}_benchmark.json)
            
        Returns:
            Path to the output file
        """
        if not self.results:
            self.logger.warning("No benchmark results to save")
            return ""
        
        if filename is None:
            filename = f"{self.name}_benchmark.json"
        
        output_path = Path(self.output_dir) / filename
        
        with open(output_path, "w") as f:
            json.dump(self.results, f, indent=2)
        
        self.logger.info(f"Benchmark results saved to {output_path}")
        return str(output_path)
    
    def load(self, filename: str) -> bool:
        """
        Load benchmark results from a file.
        
        Args:
            filename: Input filename
            
        Returns:
            True if results were loaded successfully, False otherwise
        """
        input_path = Path(filename)
        if not input_path.exists():
            self.logger.error(f"Benchmark file not found: {filename}")
            return False
        
        try:
            with open(input_path, "r") as f:
                self.results = json.load(f)
            
            self.logger.info(f"Benchmark results loaded from {input_path}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error loading benchmark results: {str(e)}")
            return False
    
    def plot(
        self,
        labels: Optional[List[str]] = None,
        metric: str = "mean",
        output_file: Optional[str] = None,
        show: bool = False
    ) -> Optional[str]:
        """
        Plot benchmark results.
        
        Args:
            labels: Labels to plot (default: all labels)
            metric: Metric to plot (mean, median, min, max, stdev)
            output_file: Output filename (default: {name}_benchmark_{metric}.png)
            show: Whether to show the plot (default: False)
            
        Returns:
            Path to the output file or None if no results
        """
        if not self.results:
            self.logger.warning("No benchmark results to plot")
            return None
        
        if labels is None:
            labels = list(self.results.keys())
        
        if metric not in ["mean", "median", "min", "max", "stdev"]:
            self.logger.warning(f"Invalid metric: {metric}, using mean")
            metric = "mean"
        
        if output_file is None:
            output_file = f"{self.name}_benchmark_{metric}.png"
        
        output_path = Path(self.output_dir) / output_file
        
        # Extract data for plotting
        plot_data = []
        for label in labels:
            if label not in self.results:
                self.logger.warning(f"Label {label} not found in benchmark results")
                continue
            
            # Get the latest benchmark result
            result = self.results[label][-1]
            plot_data.append((label, result[metric]))
        
        if not plot_data:
            self.logger.warning("No data to plot")
            return None
        
        # Sort data by metric value
        plot_data.sort(key=lambda x: x[1])
        
        # Create plot
        fig, ax = plt.subplots(figsize=(10, 6))
        
        labels = [item[0] for item in plot_data]
        values = [item[1] for item in plot_data]
        
        # Create bar chart
        bars = ax.bar(labels, values)
        
        # Add values on top of bars
        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                height + 0.001,
                f"{height:.6f}",
                ha="center",
                va="bottom",
                rotation=0
            )
        
        # Add labels and title
        ax.set_xlabel("Function")
        ax.set_ylabel(f"Time (seconds) - {metric}")
        ax.set_title(f"{self.name} Benchmark - {metric}")
        
        # Rotate x-axis labels for better readability
        plt.xticks(rotation=45, ha="right")
        
        # Adjust layout
        plt.tight_layout()
        
        # Save plot
        plt.savefig(output_path)
        self.logger.info(f"Benchmark plot saved to {output_path}")
        
        # Show plot if requested
        if show:
            plt.show()
        else:
            plt.close()
        
        return str(output_path)
    
    def plot_comparison(
        self,
        labels: Optional[List[str]] = None,
        output_file: Optional[str] = None,
        show: bool = False
    ) -> Optional[str]:
        """
        Plot benchmark comparison.
        
        Args:
            labels: Labels to compare (default: all labels)
            output_file: Output filename (default: {name}_benchmark_comparison.png)
            show: Whether to show the plot (default: False)
            
        Returns:
            Path to the output file or None if no results
        """
        comparison = self.compare(labels)
        
        if not comparison:
            self.logger.warning("No benchmark results to compare")
            return None
        
        if output_file is None:
            output_file = f"{self.name}_benchmark_comparison.png"
        
        output_path = Path(self.output_dir) / output_file
        
        # Create plot with multiple subplots
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        axes = axes.flatten()
        
        # Extract data for plotting
        labels = list(comparison.keys())
        means = [result["mean"] for result in comparison.values()]
        medians = [result["median"] for result in comparison.values()]
        mins = [result["min"] for result in comparison.values()]
        maxs = [result["max"] for result in comparison.values()]
        
        # Sort data by mean time
        sorted_indices = np.argsort(means)
        labels = [labels[i] for i in sorted_indices]
        means = [means[i] for i in sorted_indices]
        medians = [medians[i] for i in sorted_indices]
        mins = [mins[i] for i in sorted_indices]
        maxs = [maxs[i] for i in sorted_indices]
        
        # Plot mean times
        axes[0].bar(labels, means)
        axes[0].set_title("Mean Execution Time")
        axes[0].set_ylabel("Time (seconds)")
        axes[0].tick_params(axis="x", rotation=45)
        
        # Plot median times
        axes[1].bar(labels, medians)
        axes[1].set_title("Median Execution Time")
        axes[1].set_ylabel("Time (seconds)")
        axes[1].tick_params(axis="x", rotation=45)
        
        # Plot min times
        axes[2].bar(labels, mins)
        axes[2].set_title("Minimum Execution Time")
        axes[2].set_ylabel("Time (seconds)")
        axes[2].tick_params(axis="x", rotation=45)
        
        # Plot max times
        axes[3].bar(labels, maxs)
        axes[3].set_title("Maximum Execution Time")
        axes[3].set_ylabel("Time (seconds)")
        axes[3].tick_params(axis="x", rotation=45)
        
        # Add overall title
        fig.suptitle(f"{self.name} Benchmark Comparison", fontsize=16)
        
        # Adjust layout
        plt.tight_layout()
        plt.subplots_adjust(top=0.9)
        
        # Save plot
        plt.savefig(output_path)
        self.logger.info(f"Benchmark comparison plot saved to {output_path}")
        
        # Show plot if requested
        if show:
            plt.show()
        else:
            plt.close()
        
        return str(output_path)


def benchmark(
    iterations: int = 10,
    warmup: int = 1,
    label: Optional[str] = None
) -> Callable:
    """
    Decorator for benchmarking functions.
    
    Args:
        iterations: Number of iterations to run (default: 10)
        warmup: Number of warmup iterations (default: 1)
        label: Label for the benchmark (default: function name)
        
    Returns:
        Decorated function
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            func_label = label or func.__name__
            logger = logging.getLogger(__name__)
            logger.info(f"Benchmarking {func_label} ({iterations} iterations, {warmup} warmup)")
            
            # Perform warmup iterations
            for _ in range(warmup):
                func(*args, **kwargs)
            
            # Perform benchmark iterations
            times = []
            for i in range(iterations):
                start_time = time.time()
                result = func(*args, **kwargs)
                end_time = time.time()
                elapsed_time = end_time - start_time
                times.append(elapsed_time)
                logger.debug(f"Iteration {i+1}/{iterations}: {elapsed_time:.6f} seconds")
            
            # Calculate statistics
            benchmark_result = {
                "label": func_label,
                "iterations": iterations,
                "times": times,
                "min": min(times),
                "max": max(times),
                "mean": statistics.mean(times),
                "median": statistics.median(times),
                "stdev": statistics.stdev(times) if len(times) > 1 else 0
            }
            
            logger.info(f"Benchmark {func_label} completed: {benchmark_result['mean']:.6f} seconds (mean)")
            
            # Attach benchmark result to the function result
            if hasattr(result, "__dict__"):
                result.__dict__["__benchmark__"] = benchmark_result
            
            return result
        
        return wrapper
    
    return decorator
