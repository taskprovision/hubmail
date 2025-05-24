"""
Mermaid Converter Extension for Taskinity.

This extension provides functionality to convert Taskinity flows to Mermaid diagrams
and export them in various formats like SVG, PNG, and PDF.
"""
import os
import json
import base64
import tempfile
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

# Check if optional dependencies are installed
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    from cairosvg import svg2png, svg2pdf
    CAIROSVG_AVAILABLE = True
except ImportError:
    CAIROSVG_AVAILABLE = False


def convert_to_mermaid(flow_definition: Union[str, Dict], theme: str = "default", direction: str = "TD") -> str:
    """
    Convert a Taskinity flow definition to Mermaid diagram code.
    
    Args:
        flow_definition: Either a DSL string or a parsed flow definition dictionary
        theme: Mermaid theme (default, forest, dark, neutral)
        direction: Diagram direction (TD: top-down, LR: left-right, RL: right-left, BT: bottom-top)
        
    Returns:
        Mermaid diagram code as a string
    """
    from taskinity import parse_dsl, generate_mermaid_from_dsl
    
    # If flow_definition is a string, assume it's DSL text
    if isinstance(flow_definition, str):
        dsl_text = flow_definition
    else:
        # Convert dictionary to DSL format
        # This is a simplified implementation - a real one would be more complex
        flow_name = flow_definition.get("name", "UnnamedFlow")
        description = flow_definition.get("description", "")
        tasks = flow_definition.get("tasks", {})
        connections = flow_definition.get("connections", [])
        
        dsl_text = f"flow {flow_name}:\n"
        if description:
            dsl_text += f"    description: \"{description}\"\n"
        
        # Add tasks
        for task_name, task_info in tasks.items():
            task_desc = task_info.get("description", "")
            dsl_text += f"    task {task_name}:\n"
            if task_desc:
                dsl_text += f"        description: \"{task_desc}\"\n"
        
        # Add connections
        for source, target in connections:
            dsl_text += f"    {source} -> {target}\n"
    
    # Generate Mermaid code
    mermaid_code = generate_mermaid_from_dsl(dsl_text)
    
    # Add theme and direction
    if theme != "default" or direction != "TD":
        theme_directive = f"%%{{ init: {{'theme': '{theme}', 'flowchart': {{'defaultRenderer': 'dagre', 'curve': 'basis', 'direction': '{direction}'}} }} }}%%\n"
        mermaid_code = theme_directive + mermaid_code
    
    return mermaid_code


def export_as_svg(mermaid_code: str, output_file: Optional[str] = None) -> str:
    """
    Export Mermaid diagram as SVG.
    
    Args:
        mermaid_code: Mermaid diagram code
        output_file: Path to save the SVG file (optional)
        
    Returns:
        SVG content as a string or path to the saved file
    """
    svg_content = _render_mermaid_to_svg(mermaid_code)
    
    if output_file:
        with open(output_file, 'w') as f:
            f.write(svg_content)
        return output_file
    
    return svg_content


def export_as_png(mermaid_code: str, output_file: str, width: int = 800, height: int = 600) -> str:
    """
    Export Mermaid diagram as PNG.
    
    Args:
        mermaid_code: Mermaid diagram code
        output_file: Path to save the PNG file
        width: Image width in pixels
        height: Image height in pixels
        
    Returns:
        Path to the saved PNG file
    """
    if not CAIROSVG_AVAILABLE:
        raise ImportError("CairoSVG is required for PNG export. Install with: pip install cairosvg")
    
    # First convert to SVG
    svg_content = _render_mermaid_to_svg(mermaid_code)
    
    # Then convert SVG to PNG
    svg2png(bytestring=svg_content.encode('utf-8'), write_to=output_file, 
            output_width=width, output_height=height)
    
    return output_file


def _render_mermaid_to_svg(mermaid_code: str) -> str:
    """
    Render Mermaid diagram to SVG using either the Mermaid CLI or the online API.
    
    Args:
        mermaid_code: Mermaid diagram code
        
    Returns:
        SVG content as a string
    """
    # Try using local Mermaid CLI if available
    try:
        return _render_with_mermaid_cli(mermaid_code)
    except (subprocess.SubprocessError, FileNotFoundError):
        pass
    
    # Fall back to online API
    if REQUESTS_AVAILABLE:
        return _render_with_online_api(mermaid_code)
    
    raise RuntimeError("Failed to render Mermaid diagram. Install either the Mermaid CLI or the requests package.")


def _render_with_mermaid_cli(mermaid_code: str) -> str:
    """
    Render Mermaid diagram using the Mermaid CLI.
    
    Args:
        mermaid_code: Mermaid diagram code
        
    Returns:
        SVG content as a string
    """
    with tempfile.NamedTemporaryFile(suffix='.mmd', mode='w', delete=False) as f:
        f.write(mermaid_code)
        input_file = f.name
    
    output_file = input_file + '.svg'
    
    try:
        # Run mmdc (Mermaid CLI)
        subprocess.run(['mmdc', '-i', input_file, '-o', output_file], 
                      check=True, capture_output=True)
        
        # Read the output SVG
        with open(output_file, 'r') as f:
            svg_content = f.read()
        
        return svg_content
    finally:
        # Clean up temporary files
        if os.path.exists(input_file):
            os.unlink(input_file)
        if os.path.exists(output_file):
            os.unlink(output_file)


def _render_with_online_api(mermaid_code: str) -> str:
    """
    Render Mermaid diagram using the Mermaid Live Editor API.
    
    Args:
        mermaid_code: Mermaid diagram code
        
    Returns:
        SVG content as a string
    """
    if not REQUESTS_AVAILABLE:
        raise ImportError("Requests package is required for online rendering. Install with: pip install requests")
    
    # Prepare the payload
    payload = {
        "code": mermaid_code,
        "mermaid": {
            "theme": "default"
        },
        "updateEditor": False,
        "autoSync": True,
        "updateDiagram": False
    }
    
    # Make the request to the Mermaid Live Editor API
    response = requests.post(
        "https://mermaid.live/api/render",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code != 200:
        raise RuntimeError(f"Failed to render Mermaid diagram: {response.text}")
    
    # Extract SVG from response
    result = response.json()
    return result.get("svg", "")
