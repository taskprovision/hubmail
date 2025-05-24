#!/usr/bin/env python3
"""
Data processing flow example for Taskinity.
"""
import sys
import os
import pandas as pd

# Create data directory if it doesn't exist
os.makedirs("examples/data/output", exist_ok=True)

# Create sample data file if it doesn't exist
sample_data_path = "examples/data/sample.csv"
if not os.path.exists(sample_data_path):
    os.makedirs(os.path.dirname(sample_data_path), exist_ok=True)
    with open(sample_data_path, 'w') as f:
        f.write("id,name,value\n")
        f.write("1,Product A,100\n")
        f.write("2,Product B,200\n")
        f.write("3,Product A,150\n")
        f.write("4,Product C,300\n")
        f.write("5,Product B,250\n")

# Check if running in mock mode
if '--mock' in sys.argv:
    # Create mock task decorator
    def task(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    
    # Create mock run_flow_from_dsl function
    def run_flow_from_dsl(flow_dsl, input_data):
        print(f"Running mock data flow with input: {input_data}")
        
        # Actually process the data to show real results
        df = pd.read_csv(input_data["file_path"])
        df_clean = df.drop_duplicates()
        grouped = df_clean.groupby('name').agg({'value': ['sum', 'mean', 'count']})
        grouped.columns = ['total_value', 'avg_value', 'count']
        grouped = grouped.reset_index()
        grouped.to_csv(input_data["output_path"], index=False)
        
        return {
            "load_csv": {"dataframe": "DataFrame with 5 rows"},
            "clean_data": {"dataframe": "DataFrame with 5 rows (no duplicates found)"},
            "transform_data": {"dataframe": "DataFrame with 3 rows (grouped by name)"},
            "save_results": {"rows": len(grouped), "columns": len(grouped.columns), "path": input_data["output_path"]}
        }
else:
    # Import real Taskinity functionality
    try:
        from taskinity.core.taskinity_core import task, run_flow_from_dsl
    except ImportError:
        print("Error: Could not import Taskinity modules. Run with --mock flag for testing.")
        sys.exit(1)

@task(name="Load CSV")
def load_csv(file_path):
    print(f"Loading data from {file_path}")
    df = pd.read_csv(file_path)
    print(f"Loaded {len(df)} rows")
    return {"dataframe": df}

@task(name="Clean Data")
def clean_data(input_data):
    df = input_data["dataframe"]
    print(f"Cleaning data, initial size: {len(df)}")
    # Remove duplicates
    df = df.drop_duplicates()
    print(f"Size after cleaning: {len(df)}")
    return {"dataframe": df}

@task(name="Transform Data")
def transform_data(input_data):
    df = input_data["dataframe"]
    print(f"Transforming data")
    # Group by product name
    grouped = df.groupby('name').agg({'value': ['sum', 'mean', 'count']})
    grouped.columns = ['total_value', 'avg_value', 'count']
    grouped = grouped.reset_index()
    print(f"Transformed data has {len(grouped)} rows")
    return {"dataframe": grouped}

@task(name="Save Results")
def save_results(input_data, output_path):
    df = input_data["dataframe"]
    print(f"Saving results to {output_path}")
    df.to_csv(output_path, index=False)
    return {"rows": len(df), "columns": len(df.columns), "path": output_path}

# Define the flow DSL
flow_dsl = """
flow DataProcessing:
    description: "CSV data processing flow"
    load_csv -> clean_data
    clean_data -> transform_data
    transform_data -> save_results
"""

# Run the flow
results = run_flow_from_dsl(flow_dsl, {
    "file_path": "examples/data/sample.csv",
    "output_path": "examples/data/output/processed.csv"
})

print("\nFlow results:")
print(f"Processed records: {results['save_results']['rows']}")
print(f"Saved file: {results['save_results']['path']}")

# Display the processed file
print("\nProcessed file contents:")
processed_df = pd.read_csv("examples/data/output/processed.csv")
print(processed_df)
