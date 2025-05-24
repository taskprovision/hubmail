#!/usr/bin/env python3
"""
Taskinity Flow Visualizer - Extension for visualizing Taskinity flows.
"""
import os
import json
import logging
from typing import Any, Dict, List, Optional, Union

# Import core functionality
from taskinity.core.taskinity_core import parse_dsl, load_dsl, list_dsl_files

logger = logging.getLogger("taskinity.visualizer")

def convert_to_mermaid(flow_structure: Union[str, Dict[str, Any]]) -> str:
    """
    Convert a flow structure to Mermaid diagram code.
    
    Args:
        flow_structure: Flow structure or DSL text
    
    Returns:
        Mermaid diagram code
    """
    # If input is DSL text, parse it
    if isinstance(flow_structure, str):
        flow_structure = parse_dsl(flow_structure)
    
    # Create Mermaid diagram
    mermaid_code = ["graph TD"]
    
    # Add flow title
    mermaid_code.append(f"    title[{flow_structure['name']}]")
    mermaid_code.append("    classDef title fill:#f9f,stroke:#333,stroke-width:2px")
    mermaid_code.append("    class title title")
    
    # Add tasks
    for task_name, task_info in flow_structure["tasks"].items():
        task_label = task_info.get("name", task_name)
        task_desc = task_info.get("description", "")
        if task_desc:
            mermaid_code.append(f"    {task_name}[\"{task_label}<br><small>{task_desc}</small>\"]")
        else:
            mermaid_code.append(f"    {task_name}[\"{task_label}\"]")
    
    # Add connections
    for conn in flow_structure["connections"]:
        source = conn["source"]
        target = conn["target"]
        mermaid_code.append(f"    {source} --> {target}")
    
    # Add styling
    mermaid_code.append("    classDef default fill:#f9f9f9,stroke:#333,stroke-width:1px")
    
    return "\n".join(mermaid_code)

def export_as_svg(mermaid_code: str, output_file: str) -> str:
    """
    Export Mermaid diagram to SVG file.
    
    Args:
        mermaid_code: Mermaid diagram code
        output_file: Output file path
    
    Returns:
        Path to the generated SVG file
    """
    try:
        # Check if mmdc (Mermaid CLI) is installed
        import subprocess
        
        # Create a temporary file for the Mermaid code
        temp_file = os.path.join(os.path.dirname(output_file), "temp_mermaid.mmd")
        with open(temp_file, "w") as f:
            f.write(mermaid_code)
        
        # Run mmdc to generate SVG
        subprocess.run(["mmdc", "-i", temp_file, "-o", output_file], check=True)
        
        # Remove temporary file
        os.remove(temp_file)
        
        logger.info(f"Exported diagram to {output_file}")
        return output_file
    except Exception as e:
        logger.error(f"Error exporting diagram: {str(e)}")
        
        # Fallback: save Mermaid code to file
        with open(output_file.replace(".svg", ".mmd"), "w") as f:
            f.write(mermaid_code)
        
        logger.info(f"Saved Mermaid code to {output_file.replace('.svg', '.mmd')}")
        return output_file.replace(".svg", ".mmd")

def visualize_flow(flow_dsl: str, output_file: Optional[str] = None) -> str:
    """
    Visualize a flow and export it to a file.
    
    Args:
        flow_dsl: Flow DSL text
        output_file: Optional output file path
    
    Returns:
        Path to the generated file
    """
    # Parse flow
    flow_structure = parse_dsl(flow_dsl)
    
    # Generate default output file name if not provided
    if output_file is None:
        output_dir = os.path.join(os.path.dirname(__file__), "..", "..", "visualizations")
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f"{flow_structure['name']}.svg")
    
    # Convert to Mermaid
    mermaid_code = convert_to_mermaid(flow_structure)
    
    # Export to file
    return export_as_svg(mermaid_code, output_file)

def list_visualizations() -> List[str]:
    """
    List all visualization files.
    
    Returns:
        List of visualization files
    """
    viz_dir = os.path.join(os.path.dirname(__file__), "..", "..", "visualizations")
    os.makedirs(viz_dir, exist_ok=True)
    
    return [f for f in os.listdir(viz_dir) if f.endswith((".svg", ".png", ".mmd"))]

def visualize_all_flows(output_dir: Optional[str] = None) -> List[str]:
    """
    Visualize all flows in the DSL definitions directory.
    
    Args:
        output_dir: Optional output directory
    
    Returns:
        List of generated visualization files
    """
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), "..", "..", "visualizations")
    
    os.makedirs(output_dir, exist_ok=True)
    
    generated_files = []
    for dsl_file in list_dsl_files():
        try:
            dsl_text = load_dsl(dsl_file)
            flow_structure = parse_dsl(dsl_text)
            output_file = os.path.join(output_dir, f"{flow_structure['name']}.svg")
            
            mermaid_code = convert_to_mermaid(flow_structure)
            generated_file = export_as_svg(mermaid_code, output_file)
            generated_files.append(generated_file)
        except Exception as e:
            logger.error(f"Error visualizing flow {dsl_file}: {str(e)}")
    
    return generated_files

if __name__ == "__main__":
    # Example usage
    example_dsl = """
    flow EmailProcessing:
        description: "Email Processing Flow"
        fetch_emails -> classify_emails
        classify_emails -> [process_urgent_emails, process_regular_emails]
    """
    
    # Visualize flow
    output_file = visualize_flow(example_dsl)
    print(f"Generated visualization: {output_file}")
    
    # List all visualizations
    visualizations = list_visualizations()
    print(f"Available visualizations: {visualizations}")
