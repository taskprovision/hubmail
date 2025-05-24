#!/usr/bin/env python3
"""
Complex dependency graph example with Taskinity.
This example demonstrates how to create and execute a complex workflow
with a mix of parallel and sequential tasks based on their dependencies.
"""
import os
import time
import random
import json
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

# Define the complex dependency graph DSL
DEPENDENCY_GRAPH_DSL = """
flow ComplexDependencyDemo:
    description: "Demonstration of a complex dependency graph with parallel and sequential tasks"
    
    task InitializeWorkflow:
        description: "Initialize the workflow and prepare configuration"
        code: |
            import time
            import random
            import json
            from datetime import datetime
            
            print("Initializing workflow...")
            start_time = time.time()
            
            # Simulate initialization
            time.sleep(0.5)
            
            # Generate configuration
            config = {
                "workflow_id": f"workflow-{int(time.time())}",
                "timestamp": datetime.now().isoformat(),
                "parameters": {
                    "data_size": 1000,
                    "chunk_size": 200,
                    "processing_level": "medium",
                    "include_validation": True,
                    "output_format": "json"
                }
            }
            
            end_time = time.time()
            print(f"Workflow initialized in {end_time - start_time:.2f} seconds")
            
            return {
                "config": config,
                "start_time": start_time
            }
    
    task FetchDataA:
        description: "Fetch data from source A"
        code: |
            import time
            import random
            
            print("Fetching data from source A...")
            start_time = time.time()
            
            # Get configuration
            config = inputs["InitializeWorkflow"]["config"]
            data_size = config["parameters"]["data_size"] // 2
            
            # Simulate data fetching
            time.sleep(1.5)
            
            # Generate sample data
            data_a = [random.randint(1, 100) for _ in range(data_size)]
            
            end_time = time.time()
            print(f"Fetched {len(data_a)} records from source A in {end_time - start_time:.2f} seconds")
            
            return {
                "data": data_a,
                "source": "A",
                "record_count": len(data_a),
                "fetch_time": end_time - start_time
            }
    
    task FetchDataB:
        description: "Fetch data from source B"
        code: |
            import time
            import random
            
            print("Fetching data from source B...")
            start_time = time.time()
            
            # Get configuration
            config = inputs["InitializeWorkflow"]["config"]
            data_size = config["parameters"]["data_size"] // 2
            
            # Simulate data fetching (slightly longer than A)
            time.sleep(2.0)
            
            # Generate sample data
            data_b = [random.randint(50, 150) for _ in range(data_size)]
            
            end_time = time.time()
            print(f"Fetched {len(data_b)} records from source B in {end_time - start_time:.2f} seconds")
            
            return {
                "data": data_b,
                "source": "B",
                "record_count": len(data_b),
                "fetch_time": end_time - start_time
            }
    
    task ValidateDataA:
        description: "Validate data from source A"
        code: |
            import time
            
            print("Validating data from source A...")
            start_time = time.time()
            
            # Get data and configuration
            data_a = inputs["FetchDataA"]["data"]
            config = inputs["InitializeWorkflow"]["config"]
            
            # Check if validation is enabled
            if not config["parameters"]["include_validation"]:
                print("Validation skipped as per configuration")
                return {
                    "validated_data": data_a,
                    "validation_time": 0,
                    "invalid_records": 0,
                    "is_valid": True
                }
            
            # Simulate validation
            time.sleep(0.8)
            
            # Filter out invalid data (for this example, values < 10 are "invalid")
            valid_data = [x for x in data_a if x >= 10]
            invalid_count = len(data_a) - len(valid_data)
            
            # Determine if data is valid overall (less than 5% invalid)
            is_valid = (invalid_count / len(data_a)) < 0.05 if len(data_a) > 0 else True
            
            end_time = time.time()
            print(f"Validated data from source A: {invalid_count} invalid records found")
            print(f"Validation completed in {end_time - start_time:.2f} seconds")
            
            return {
                "validated_data": valid_data,
                "validation_time": end_time - start_time,
                "invalid_records": invalid_count,
                "is_valid": is_valid
            }
    
    task ValidateDataB:
        description: "Validate data from source B"
        code: |
            import time
            
            print("Validating data from source B...")
            start_time = time.time()
            
            # Get data and configuration
            data_b = inputs["FetchDataB"]["data"]
            config = inputs["InitializeWorkflow"]["config"]
            
            # Check if validation is enabled
            if not config["parameters"]["include_validation"]:
                print("Validation skipped as per configuration")
                return {
                    "validated_data": data_b,
                    "validation_time": 0,
                    "invalid_records": 0,
                    "is_valid": True
                }
            
            # Simulate validation
            time.sleep(1.0)
            
            # Filter out invalid data (for this example, values > 140 are "invalid")
            valid_data = [x for x in data_b if x <= 140]
            invalid_count = len(data_b) - len(valid_data)
            
            # Determine if data is valid overall (less than 5% invalid)
            is_valid = (invalid_count / len(data_b)) < 0.05 if len(data_b) > 0 else True
            
            end_time = time.time()
            print(f"Validated data from source B: {invalid_count} invalid records found")
            print(f"Validation completed in {end_time - start_time:.2f} seconds")
            
            return {
                "validated_data": valid_data,
                "validation_time": end_time - start_time,
                "invalid_records": invalid_count,
                "is_valid": is_valid
            }
    
    task MergeData:
        description: "Merge validated data from both sources"
        code: |
            import time
            
            print("Merging data from sources A and B...")
            start_time = time.time()
            
            # Get validated data
            data_a = inputs["ValidateDataA"]["validated_data"]
            data_b = inputs["ValidateDataB"]["validated_data"]
            
            # Check if both sources are valid
            is_valid_a = inputs["ValidateDataA"]["is_valid"]
            is_valid_b = inputs["ValidateDataB"]["is_valid"]
            
            if not is_valid_a or not is_valid_b:
                print("Warning: One or more data sources failed validation")
            
            # Merge data
            merged_data = data_a + data_b
            
            # Simulate merging process
            time.sleep(0.7)
            
            end_time = time.time()
            print(f"Merged {len(data_a)} records from source A and {len(data_b)} records from source B")
            print(f"Total merged records: {len(merged_data)}")
            print(f"Merging completed in {end_time - start_time:.2f} seconds")
            
            return {
                "merged_data": merged_data,
                "merge_time": end_time - start_time,
                "total_records": len(merged_data),
                "source_a_records": len(data_a),
                "source_b_records": len(data_b)
            }
    
    task ProcessChunkA:
        description: "Process first chunk of merged data"
        code: |
            import time
            
            print("Processing chunk A...")
            start_time = time.time()
            
            # Get merged data
            merged_data = inputs["MergeData"]["merged_data"]
            
            # Determine chunk size (1/3 of data)
            total_records = len(merged_data)
            chunk_size = total_records // 3
            chunk_a = merged_data[:chunk_size]
            
            # Process chunk (multiply by 2)
            processed_data = [x * 2 for x in chunk_a]
            
            # Simulate processing
            time.sleep(1.2)
            
            end_time = time.time()
            print(f"Processed chunk A ({len(chunk_a)} records) in {end_time - start_time:.2f} seconds")
            
            return {
                "processed_data": processed_data,
                "processing_time": end_time - start_time,
                "record_count": len(processed_data),
                "chunk_id": "A"
            }
    
    task ProcessChunkB:
        description: "Process second chunk of merged data"
        code: |
            import time
            
            print("Processing chunk B...")
            start_time = time.time()
            
            # Get merged data
            merged_data = inputs["MergeData"]["merged_data"]
            
            # Determine chunk size (1/3 of data)
            total_records = len(merged_data)
            chunk_size = total_records // 3
            chunk_b = merged_data[chunk_size:chunk_size*2]
            
            # Process chunk (add 10)
            processed_data = [x + 10 for x in chunk_b]
            
            # Simulate processing
            time.sleep(1.5)
            
            end_time = time.time()
            print(f"Processed chunk B ({len(chunk_b)} records) in {end_time - start_time:.2f} seconds")
            
            return {
                "processed_data": processed_data,
                "processing_time": end_time - start_time,
                "record_count": len(processed_data),
                "chunk_id": "B"
            }
    
    task ProcessChunkC:
        description: "Process third chunk of merged data"
        code: |
            import time
            
            print("Processing chunk C...")
            start_time = time.time()
            
            # Get merged data
            merged_data = inputs["MergeData"]["merged_data"]
            
            # Determine chunk size (1/3 of data)
            total_records = len(merged_data)
            chunk_size = total_records // 3
            chunk_c = merged_data[chunk_size*2:]
            
            # Process chunk (square)
            processed_data = [x ** 2 for x in chunk_c]
            
            # Simulate processing
            time.sleep(1.8)
            
            end_time = time.time()
            print(f"Processed chunk C ({len(chunk_c)} records) in {end_time - start_time:.2f} seconds")
            
            return {
                "processed_data": processed_data,
                "processing_time": end_time - start_time,
                "record_count": len(processed_data),
                "chunk_id": "C"
            }
    
    task AggregateResults:
        description: "Aggregate results from all processed chunks"
        code: |
            import time
            import json
            from pathlib import Path
            
            print("Aggregating results from all chunks...")
            start_time = time.time()
            
            # Get processed data from all chunks
            chunk_a_data = inputs["ProcessChunkA"]["processed_data"]
            chunk_b_data = inputs["ProcessChunkB"]["processed_data"]
            chunk_c_data = inputs["ProcessChunkC"]["processed_data"]
            
            # Combine all processed data
            all_processed_data = chunk_a_data + chunk_b_data + chunk_c_data
            
            # Calculate some statistics
            total_items = len(all_processed_data)
            avg_value = sum(all_processed_data) / total_items if total_items > 0 else 0
            max_value = max(all_processed_data) if all_processed_data else 0
            min_value = min(all_processed_data) if all_processed_data else 0
            
            # Simulate aggregation
            time.sleep(0.8)
            
            end_time = time.time()
            print(f"Aggregated {total_items} processed records in {end_time - start_time:.2f} seconds")
            
            return {
                "aggregated_data": all_processed_data,
                "statistics": {
                    "total_items": total_items,
                    "average_value": avg_value,
                    "max_value": max_value,
                    "min_value": min_value
                },
                "aggregation_time": end_time - start_time
            }
    
    task GenerateReport:
        description: "Generate final report with results and performance metrics"
        code: |
            import time
            import json
            from pathlib import Path
            from datetime import datetime
            
            print("Generating final report...")
            start_time = time.time()
            
            # Get workflow start time
            workflow_start_time = inputs["InitializeWorkflow"]["start_time"]
            
            # Get configuration
            config = inputs["InitializeWorkflow"]["config"]
            
            # Get statistics from aggregation
            statistics = inputs["AggregateResults"]["statistics"]
            
            # Collect performance metrics from all tasks
            performance_metrics = {
                "FetchDataA": inputs["FetchDataA"]["fetch_time"],
                "FetchDataB": inputs["FetchDataB"]["fetch_time"],
                "ValidateDataA": inputs["ValidateDataA"]["validation_time"],
                "ValidateDataB": inputs["ValidateDataB"]["validation_time"],
                "MergeData": inputs["MergeData"]["merge_time"],
                "ProcessChunkA": inputs["ProcessChunkA"]["processing_time"],
                "ProcessChunkB": inputs["ProcessChunkB"]["processing_time"],
                "ProcessChunkC": inputs["ProcessChunkC"]["processing_time"],
                "AggregateResults": inputs["AggregateResults"]["aggregation_time"]
            }
            
            # Calculate total workflow time
            workflow_end_time = time.time()
            total_workflow_time = workflow_end_time - workflow_start_time
            
            # Calculate critical path time (sequential execution time)
            sequential_time = sum(performance_metrics.values())
            
            # Calculate parallel speedup
            speedup = sequential_time / total_workflow_time if total_workflow_time > 0 else 0
            
            # Create report
            report = {
                "workflow_id": config["workflow_id"],
                "timestamp": datetime.now().isoformat(),
                "execution_summary": {
                    "start_time": datetime.fromtimestamp(workflow_start_time).isoformat(),
                    "end_time": datetime.fromtimestamp(workflow_end_time).isoformat(),
                    "total_duration": total_workflow_time,
                    "sequential_duration": sequential_time,
                    "speedup": speedup
                },
                "data_summary": {
                    "source_a_records": inputs["MergeData"]["source_a_records"],
                    "source_b_records": inputs["MergeData"]["source_b_records"],
                    "total_processed_records": statistics["total_items"],
                    "invalid_records_a": inputs["ValidateDataA"]["invalid_records"],
                    "invalid_records_b": inputs["ValidateDataB"]["invalid_records"]
                },
                "results": statistics,
                "performance_metrics": performance_metrics,
                "configuration": config
            }
            
            # Save report to file
            output_dir = Path("output")
            os.makedirs(output_dir, exist_ok=True)
            
            report_file = output_dir / "dependency_graph_report.json"
            with open(report_file, "w") as f:
                json.dump(report, f, indent=2)
            
            end_time = time.time()
            print(f"Generated report in {end_time - start_time:.2f} seconds")
            print(f"Report saved to {report_file}")
            print(f"Total workflow time: {total_workflow_time:.2f} seconds")
            print(f"Sequential execution time would be: {sequential_time:.2f} seconds")
            print(f"Parallel speedup: {speedup:.2f}x")
            
            return {
                "report": report,
                "report_file": str(report_file),
                "total_workflow_time": total_workflow_time,
                "sequential_time": sequential_time,
                "speedup": speedup
            }
    
    # Define task dependencies
    InitializeWorkflow -> FetchDataA
    InitializeWorkflow -> FetchDataB
    FetchDataA -> ValidateDataA
    FetchDataB -> ValidateDataB
    ValidateDataA -> MergeData
    ValidateDataB -> MergeData
    MergeData -> ProcessChunkA
    MergeData -> ProcessChunkB
    MergeData -> ProcessChunkC
    ProcessChunkA -> AggregateResults
    ProcessChunkB -> AggregateResults
    ProcessChunkC -> AggregateResults
    AggregateResults -> GenerateReport
"""


def run_dependency_graph_flow():
    """Run the complex dependency graph flow with the ParallelFlowExecutor."""
    print("\n" + "="*80)
    print("Running complex dependency graph flow")
    print("="*80)
    
    # Create a parallel executor with 4 workers
    executor = ParallelFlowExecutor(max_workers=4)
    
    # Measure execution time
    start_time = time.time()
    
    # Run the flow
    result = run_flow_from_dsl(DEPENDENCY_GRAPH_DSL, executor=executor)
    
    # Calculate total execution time
    end_time = time.time()
    total_time = end_time - start_time
    
    print("\nFlow Results:")
    print(f"Total execution time: {total_time:.2f} seconds")
    
    # Extract performance metrics from the result
    report = result["GenerateReport"]["report"]
    print(f"Parallel execution time: {report['execution_summary']['total_duration']:.2f} seconds")
    print(f"Sequential execution time: {report['execution_summary']['sequential_duration']:.2f} seconds")
    print(f"Speedup: {report['execution_summary']['speedup']:.2f}x")
    
    return result, total_time


def visualize_dependency_graph():
    """Generate a visualization of the dependency graph."""
    print("\n" + "="*80)
    print("Generating dependency graph visualization")
    print("="*80)
    
    # This is a placeholder for actual visualization code
    # In a real implementation, this would generate a graphical representation
    # of the task dependencies using a library like graphviz
    
    # For this example, we'll just print a text representation
    dependencies = [
        ("InitializeWorkflow", "FetchDataA"),
        ("InitializeWorkflow", "FetchDataB"),
        ("FetchDataA", "ValidateDataA"),
        ("FetchDataB", "ValidateDataB"),
        ("ValidateDataA", "MergeData"),
        ("ValidateDataB", "MergeData"),
        ("MergeData", "ProcessChunkA"),
        ("MergeData", "ProcessChunkB"),
        ("MergeData", "ProcessChunkC"),
        ("ProcessChunkA", "AggregateResults"),
        ("ProcessChunkB", "AggregateResults"),
        ("ProcessChunkC", "AggregateResults"),
        ("AggregateResults", "GenerateReport")
    ]
    
    print("\nTask Dependencies:")
    for source, target in dependencies:
        print(f"  {source} -> {target}")
    
    # Create a simple ASCII visualization
    print("\nDependency Graph (ASCII):")
    print("  InitializeWorkflow")
    print("    |")
    print("    |-----> FetchDataA ------> ValidateDataA ---+")
    print("    |                                           |")
    print("    |-----> FetchDataB ------> ValidateDataB ---+---> MergeData")
    print("                                                       |")
    print("                                                       |-----> ProcessChunkA ---+")
    print("                                                       |                        |")
    print("                                                       |-----> ProcessChunkB ---+---> AggregateResults ---> GenerateReport")
    print("                                                       |                        |")
    print("                                                       |-----> ProcessChunkC ---+")
    
    # In a real implementation, we would save the visualization to a file
    # For this example, we'll just create a dummy file
    visualization_file = OUTPUT_DIR / "dependency_graph.txt"
    with open(visualization_file, "w") as f:
        f.write("Dependency Graph Visualization\n\n")
        f.write("Task Dependencies:\n")
        for source, target in dependencies:
            f.write(f"  {source} -> {target}\n")
    
    print(f"\nVisualization saved to {visualization_file}")
    return str(visualization_file)


if __name__ == "__main__":
    # Save the DSL to a file
    dsl_file = BASE_DIR / "dependency_graph.taskinity"
    with open(dsl_file, "w") as f:
        f.write(DEPENDENCY_GRAPH_DSL)
    print(f"Saved DSL to {dsl_file}")
    
    # Generate a visualization of the dependency graph
    visualization_file = visualize_dependency_graph()
    
    # Run the flow
    result, total_time = run_dependency_graph_flow()
    
    # Print summary
    print("\n" + "="*80)
    print("Summary")
    print("="*80)
    print(f"Complex dependency graph flow completed in {total_time:.2f} seconds")
    print(f"Report saved to {result['GenerateReport']['report_file']}")
    print(f"Visualization saved to {visualization_file}")
    
    # Print the critical path
    print("\nCritical Path Analysis:")
    performance_metrics = result["GenerateReport"]["report"]["performance_metrics"]
    
    # Sort tasks by execution time to identify bottlenecks
    sorted_tasks = sorted(performance_metrics.items(), key=lambda x: x[1], reverse=True)
    
    print("\nTask Execution Times (descending):")
    for task, time_taken in sorted_tasks:
        print(f"  {task}: {time_taken:.2f} seconds")
    
    print("\nBottleneck Task: " + sorted_tasks[0][0])
    print(f"Bottleneck Time: {sorted_tasks[0][1]:.2f} seconds")
    
    # Suggest optimization
    print("\nOptimization Suggestion:")
    print(f"Focus on optimizing the '{sorted_tasks[0][0]}' task to improve overall workflow performance.")
