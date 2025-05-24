#!/usr/bin/env python3
"""
Basic parallel execution example with Taskinity.
This example demonstrates how to run tasks in parallel using Taskinity.
"""
import os
import time
import random
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Import Taskinity components
from taskinity import task, flow, run_flow_from_dsl, ParallelFlowExecutor

# Load environment variables
load_dotenv()

# Configure paths
BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Define the parallel flow DSL
PARALLEL_FLOW_DSL = """
flow BasicParallelDemo:
    description: "Basic demonstration of parallel task execution"
    
    task DataGeneration:
        description: "Generate sample data for processing"
        code: |
            import random
            import time
            from datetime import datetime
            
            print("Generating sample data...")
            start_time = time.time()
            
            # Simulate data generation
            data_size = 1000
            data = [random.randint(1, 100) for _ in range(data_size)]
            
            # Simulate some processing time
            time.sleep(1)
            
            end_time = time.time()
            print(f"Generated {data_size} data points in {end_time - start_time:.2f} seconds")
            
            return {
                "data": data,
                "timestamp": datetime.now().isoformat(),
                "data_size": data_size
            }
    
    task ProcessChunk1:
        description: "Process first chunk of data"
        code: |
            import time
            
            print("Processing chunk 1...")
            start_time = time.time()
            
            # Get input data from previous task
            data = inputs["DataGeneration"]["data"]
            data_size = inputs["DataGeneration"]["data_size"]
            
            # Determine chunk size (25% of data)
            chunk_size = data_size // 4
            chunk_start = 0
            chunk_end = chunk_size
            
            # Extract chunk
            chunk = data[chunk_start:chunk_end]
            
            # Process chunk (square each number)
            processed_data = [x ** 2 for x in chunk]
            
            # Simulate processing time
            time.sleep(2)
            
            end_time = time.time()
            print(f"Processed chunk 1 ({len(chunk)} items) in {end_time - start_time:.2f} seconds")
            
            return {
                "processed_data": processed_data,
                "chunk_size": len(chunk),
                "processing_time": end_time - start_time
            }
    
    task ProcessChunk2:
        description: "Process second chunk of data"
        code: |
            import time
            
            print("Processing chunk 2...")
            start_time = time.time()
            
            # Get input data from previous task
            data = inputs["DataGeneration"]["data"]
            data_size = inputs["DataGeneration"]["data_size"]
            
            # Determine chunk size (25% of data)
            chunk_size = data_size // 4
            chunk_start = chunk_size
            chunk_end = chunk_size * 2
            
            # Extract chunk
            chunk = data[chunk_start:chunk_end]
            
            # Process chunk (cube each number)
            processed_data = [x ** 3 for x in chunk]
            
            # Simulate processing time (slightly different to show variability)
            time.sleep(2.2)
            
            end_time = time.time()
            print(f"Processed chunk 2 ({len(chunk)} items) in {end_time - start_time:.2f} seconds")
            
            return {
                "processed_data": processed_data,
                "chunk_size": len(chunk),
                "processing_time": end_time - start_time
            }
    
    task ProcessChunk3:
        description: "Process third chunk of data"
        code: |
            import time
            
            print("Processing chunk 3...")
            start_time = time.time()
            
            # Get input data from previous task
            data = inputs["DataGeneration"]["data"]
            data_size = inputs["DataGeneration"]["data_size"]
            
            # Determine chunk size (25% of data)
            chunk_size = data_size // 4
            chunk_start = chunk_size * 2
            chunk_end = chunk_size * 3
            
            # Extract chunk
            chunk = data[chunk_start:chunk_end]
            
            # Process chunk (multiply by 10)
            processed_data = [x * 10 for x in chunk]
            
            # Simulate processing time
            time.sleep(1.8)
            
            end_time = time.time()
            print(f"Processed chunk 3 ({len(chunk)} items) in {end_time - start_time:.2f} seconds")
            
            return {
                "processed_data": processed_data,
                "chunk_size": len(chunk),
                "processing_time": end_time - start_time
            }
    
    task ProcessChunk4:
        description: "Process fourth chunk of data"
        code: |
            import time
            
            print("Processing chunk 4...")
            start_time = time.time()
            
            # Get input data from previous task
            data = inputs["DataGeneration"]["data"]
            data_size = inputs["DataGeneration"]["data_size"]
            
            # Determine chunk size (25% of data)
            chunk_size = data_size // 4
            chunk_start = chunk_size * 3
            chunk_end = data_size
            
            # Extract chunk
            chunk = data[chunk_start:chunk_end]
            
            # Process chunk (add 100)
            processed_data = [x + 100 for x in chunk]
            
            # Simulate processing time
            time.sleep(2.5)
            
            end_time = time.time()
            print(f"Processed chunk 4 ({len(chunk)} items) in {end_time - start_time:.2f} seconds")
            
            return {
                "processed_data": processed_data,
                "chunk_size": len(chunk),
                "processing_time": end_time - start_time
            }
    
    task AggregateResults:
        description: "Aggregate results from all chunks"
        code: |
            import time
            import json
            from pathlib import Path
            
            print("Aggregating results...")
            start_time = time.time()
            
            # Get processed data from all chunks
            chunk1_data = inputs["ProcessChunk1"]["processed_data"]
            chunk2_data = inputs["ProcessChunk2"]["processed_data"]
            chunk3_data = inputs["ProcessChunk3"]["processed_data"]
            chunk4_data = inputs["ProcessChunk4"]["processed_data"]
            
            # Combine all processed data
            all_processed_data = chunk1_data + chunk2_data + chunk3_data + chunk4_data
            
            # Calculate some statistics
            total_items = len(all_processed_data)
            avg_value = sum(all_processed_data) / total_items if total_items > 0 else 0
            max_value = max(all_processed_data) if all_processed_data else 0
            min_value = min(all_processed_data) if all_processed_data else 0
            
            # Calculate processing times
            chunk1_time = inputs["ProcessChunk1"]["processing_time"]
            chunk2_time = inputs["ProcessChunk2"]["processing_time"]
            chunk3_time = inputs["ProcessChunk3"]["processing_time"]
            chunk4_time = inputs["ProcessChunk4"]["processing_time"]
            
            # Calculate total and max processing time
            total_processing_time = chunk1_time + chunk2_time + chunk3_time + chunk4_time
            max_processing_time = max(chunk1_time, chunk2_time, chunk3_time, chunk4_time)
            
            # Calculate parallel vs sequential speedup
            parallel_time = max_processing_time  # In parallel, time is determined by the slowest task
            sequential_time = total_processing_time  # In sequential, time is the sum of all tasks
            speedup = sequential_time / parallel_time if parallel_time > 0 else 0
            
            # Create results summary
            results = {
                "statistics": {
                    "total_items": total_items,
                    "average_value": avg_value,
                    "max_value": max_value,
                    "min_value": min_value
                },
                "performance": {
                    "chunk1_time": chunk1_time,
                    "chunk2_time": chunk2_time,
                    "chunk3_time": chunk3_time,
                    "chunk4_time": chunk4_time,
                    "parallel_time": parallel_time,
                    "sequential_time": sequential_time,
                    "speedup": speedup
                }
            }
            
            # Save results to file
            output_dir = Path("output")
            os.makedirs(output_dir, exist_ok=True)
            
            results_file = output_dir / "parallel_results.json"
            with open(results_file, "w") as f:
                json.dump(results, f, indent=2)
            
            end_time = time.time()
            print(f"Aggregated results in {end_time - start_time:.2f} seconds")
            print(f"Results saved to {results_file}")
            print(f"Parallel speedup: {speedup:.2f}x (parallel: {parallel_time:.2f}s vs sequential: {sequential_time:.2f}s)")
            
            return {
                "results": results,
                "results_file": str(results_file)
            }
    
    # Define task dependencies
    DataGeneration -> ProcessChunk1
    DataGeneration -> ProcessChunk2
    DataGeneration -> ProcessChunk3
    DataGeneration -> ProcessChunk4
    ProcessChunk1 -> AggregateResults
    ProcessChunk2 -> AggregateResults
    ProcessChunk3 -> AggregateResults
    ProcessChunk4 -> AggregateResults
"""


def run_parallel_flow():
    """Run the parallel flow with the ParallelFlowExecutor."""
    print("\n" + "="*80)
    print("Running parallel flow with ParallelFlowExecutor")
    print("="*80)
    
    # Create a parallel executor with 4 workers
    executor = ParallelFlowExecutor(max_workers=4)
    
    # Measure execution time
    start_time = time.time()
    
    # Run the flow
    result = run_flow_from_dsl(PARALLEL_FLOW_DSL, executor=executor)
    
    # Calculate total execution time
    end_time = time.time()
    total_time = end_time - start_time
    
    print("\nParallel Flow Results:")
    print(f"Total execution time: {total_time:.2f} seconds")
    
    # Extract performance metrics from the result
    performance = result["AggregateResults"]["results"]["performance"]
    print(f"Parallel processing time: {performance['parallel_time']:.2f} seconds")
    print(f"Sequential processing time: {performance['sequential_time']:.2f} seconds")
    print(f"Speedup: {performance['speedup']:.2f}x")
    
    return result, total_time


def run_sequential_flow():
    """Run the same flow sequentially for comparison."""
    print("\n" + "="*80)
    print("Running sequential flow (for comparison)")
    print("="*80)
    
    # Create a sequential executor with 1 worker
    executor = ParallelFlowExecutor(max_workers=1)
    
    # Measure execution time
    start_time = time.time()
    
    # Run the flow
    result = run_flow_from_dsl(PARALLEL_FLOW_DSL, executor=executor)
    
    # Calculate total execution time
    end_time = time.time()
    total_time = end_time - start_time
    
    print("\nSequential Flow Results:")
    print(f"Total execution time: {total_time:.2f} seconds")
    
    return result, total_time


def compare_results(parallel_time, sequential_time):
    """Compare the results of parallel and sequential execution."""
    print("\n" + "="*80)
    print("Performance Comparison")
    print("="*80)
    
    speedup = sequential_time / parallel_time if parallel_time > 0 else 0
    time_saved = sequential_time - parallel_time
    efficiency = (speedup / 4) * 100  # Efficiency relative to 4 workers
    
    print(f"Parallel execution time:   {parallel_time:.2f} seconds")
    print(f"Sequential execution time: {sequential_time:.2f} seconds")
    print(f"Time saved:                {time_saved:.2f} seconds")
    print(f"Speedup:                   {speedup:.2f}x")
    print(f"Parallel efficiency:       {efficiency:.2f}%")
    
    # Save comparison to file
    comparison = {
        "parallel_time": parallel_time,
        "sequential_time": sequential_time,
        "time_saved": time_saved,
        "speedup": speedup,
        "efficiency": efficiency,
        "timestamp": datetime.now().isoformat()
    }
    
    comparison_file = OUTPUT_DIR / "performance_comparison.json"
    with open(comparison_file, "w") as f:
        import json
        json.dump(comparison, f, indent=2)
    
    print(f"Comparison saved to {comparison_file}")


if __name__ == "__main__":
    # Save the DSL to a file
    dsl_file = BASE_DIR / "basic_parallel.taskinity"
    with open(dsl_file, "w") as f:
        f.write(PARALLEL_FLOW_DSL)
    print(f"Saved DSL to {dsl_file}")
    
    # Run the flow in parallel
    _, parallel_time = run_parallel_flow()
    
    # Run the flow sequentially
    _, sequential_time = run_sequential_flow()
    
    # Compare the results
    compare_results(parallel_time, sequential_time)
