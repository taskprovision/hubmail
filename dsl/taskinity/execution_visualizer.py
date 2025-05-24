"""
Execution Visualizer for Taskinity.

This module provides tools for visualizing the execution of Taskinity flows,
including task status, execution time, and dependencies.
"""
import os
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

# Check if optional dependencies are installed
try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


def visualize_execution(
    flow_data: Union[str, Dict, Path],
    output_file: Optional[str] = None,
    format: str = "html"
) -> str:
    """
    Visualize the execution of a Taskinity flow.
    
    Args:
        flow_data: Flow execution data as a JSON string, dictionary, or file path
        output_file: Path to save the visualization (optional)
        format: Output format (html, svg, png, pdf)
        
    Returns:
        Path to the saved visualization or HTML content as string
    """
    # Load flow data
    execution_data = _load_execution_data(flow_data)
    
    # Generate visualization based on format
    if format.lower() == "html":
        return _generate_html_visualization(execution_data, output_file)
    elif format.lower() in ["svg", "png", "pdf"]:
        if not MATPLOTLIB_AVAILABLE:
            raise ImportError("Matplotlib is required for SVG/PNG/PDF visualization. "
                             "Install with: pip install matplotlib")
        return _generate_matplotlib_visualization(execution_data, output_file, format)
    else:
        raise ValueError(f"Unsupported format: {format}. Supported formats: html, svg, png, pdf")


def generate_execution_report(
    flow_data: Union[str, Dict, Path],
    output_file: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate a report of the flow execution.
    
    Args:
        flow_data: Flow execution data as a JSON string, dictionary, or file path
        output_file: Path to save the report as JSON (optional)
        
    Returns:
        Report data as a dictionary
    """
    # Load flow data
    execution_data = _load_execution_data(flow_data)
    
    # Extract flow information
    flow_id = execution_data.get("flow_id", "unknown")
    flow_name = execution_data.get("name", "unknown")
    start_time = execution_data.get("start_time")
    end_time = execution_data.get("end_time")
    status = execution_data.get("status", "UNKNOWN")
    
    # Calculate duration
    duration = None
    if start_time and end_time:
        try:
            start_dt = datetime.fromisoformat(start_time)
            end_dt = datetime.fromisoformat(end_time)
            duration = (end_dt - start_dt).total_seconds()
        except (ValueError, TypeError):
            pass
    
    # Analyze tasks
    tasks = execution_data.get("tasks", {})
    task_count = len(tasks)
    completed_tasks = sum(1 for t in tasks.values() if t.get("status") == "COMPLETED")
    failed_tasks = sum(1 for t in tasks.values() if t.get("status") == "FAILED")
    
    # Calculate task durations
    task_durations = {}
    for task_id, task_data in tasks.items():
        task_start = task_data.get("start_time")
        task_end = task_data.get("end_time")
        if task_start and task_end:
            try:
                task_start_dt = datetime.fromisoformat(task_start)
                task_end_dt = datetime.fromisoformat(task_end)
                task_durations[task_id] = (task_end_dt - task_start_dt).total_seconds()
            except (ValueError, TypeError):
                task_durations[task_id] = None
    
    # Find longest and shortest tasks
    longest_task = max(task_durations.items(), key=lambda x: x[1] or 0) if task_durations else (None, None)
    shortest_task = min(task_durations.items(), key=lambda x: x[1] or float('inf')) if task_durations else (None, None)
    
    # Create report
    report = {
        "flow_summary": {
            "id": flow_id,
            "name": flow_name,
            "status": status,
            "start_time": start_time,
            "end_time": end_time,
            "duration": duration
        },
        "task_summary": {
            "total_tasks": task_count,
            "completed_tasks": completed_tasks,
            "failed_tasks": failed_tasks,
            "success_rate": (completed_tasks / task_count * 100) if task_count > 0 else 0
        },
        "performance": {
            "average_task_duration": sum(d for d in task_durations.values() if d is not None) / len(task_durations) if task_durations else None,
            "longest_task": {
                "id": longest_task[0],
                "duration": longest_task[1]
            } if longest_task[0] else None,
            "shortest_task": {
                "id": shortest_task[0],
                "duration": shortest_task[1]
            } if shortest_task[0] else None
        },
        "tasks": {
            task_id: {
                "name": task_data.get("name", task_id),
                "status": task_data.get("status", "UNKNOWN"),
                "start_time": task_data.get("start_time"),
                "end_time": task_data.get("end_time"),
                "duration": task_durations.get(task_id)
            }
            for task_id, task_data in tasks.items()
        }
    }
    
    # Save report if output_file is provided
    if output_file:
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
    
    return report


def _load_execution_data(flow_data: Union[str, Dict, Path]) -> Dict[str, Any]:
    """
    Load flow execution data from various sources.
    
    Args:
        flow_data: Flow execution data as a JSON string, dictionary, or file path
        
    Returns:
        Flow execution data as a dictionary
    """
    if isinstance(flow_data, dict):
        return flow_data
    
    if isinstance(flow_data, (str, Path)) and os.path.isfile(str(flow_data)):
        with open(flow_data, 'r') as f:
            return json.load(f)
    
    if isinstance(flow_data, str):
        try:
            return json.loads(flow_data)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON string provided for flow_data")
    
    raise ValueError("flow_data must be a dictionary, JSON string, or file path")


def _generate_html_visualization(execution_data: Dict[str, Any], output_file: Optional[str] = None) -> str:
    """
    Generate an HTML visualization of the flow execution.
    
    Args:
        execution_data: Flow execution data
        output_file: Path to save the HTML file (optional)
        
    Returns:
        HTML content as string or path to the saved file
    """
    flow_name = execution_data.get("name", "Unknown Flow")
    flow_id = execution_data.get("flow_id", "unknown")
    start_time = execution_data.get("start_time", "")
    end_time = execution_data.get("end_time", "")
    status = execution_data.get("status", "UNKNOWN")
    
    # Format timestamps
    try:
        start_dt = datetime.fromisoformat(start_time)
        formatted_start = start_dt.strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        formatted_start = start_time
    
    try:
        end_dt = datetime.fromisoformat(end_time)
        formatted_end = end_dt.strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        formatted_end = end_time
    
    # Calculate duration
    duration = ""
    if start_time and end_time:
        try:
            start_dt = datetime.fromisoformat(start_time)
            end_dt = datetime.fromisoformat(end_time)
            duration = f"{(end_dt - start_dt).total_seconds():.2f} seconds"
        except (ValueError, TypeError):
            pass
    
    # Generate task timeline
    tasks = execution_data.get("tasks", {})
    timeline_html = ""
    
    # Find the earliest start time and latest end time
    all_times = []
    for task_data in tasks.values():
        if task_data.get("start_time"):
            try:
                all_times.append(datetime.fromisoformat(task_data["start_time"]))
            except (ValueError, TypeError):
                pass
        if task_data.get("end_time"):
            try:
                all_times.append(datetime.fromisoformat(task_data["end_time"]))
            except (ValueError, TypeError):
                pass
    
    if all_times:
        min_time = min(all_times)
        max_time = max(all_times)
        total_duration = (max_time - min_time).total_seconds()
        
        for task_id, task_data in tasks.items():
            task_name = task_data.get("name", task_id)
            task_status = task_data.get("status", "UNKNOWN")
            
            # Calculate position and width for timeline
            try:
                task_start = datetime.fromisoformat(task_data.get("start_time", ""))
                task_end = datetime.fromisoformat(task_data.get("end_time", ""))
                
                start_offset = ((task_start - min_time).total_seconds() / total_duration) * 100
                task_duration = (task_end - task_start).total_seconds()
                width = (task_duration / total_duration) * 100
                
                # Determine color based on status
                color = "#9f9" if task_status == "COMPLETED" else "#f99" if task_status == "FAILED" else "#9cf"
                
                timeline_html += f"""
                <div class="timeline-bar">
                    <div class="task-bar" style="left: {start_offset:.2f}%; width: {width:.2f}%; background-color: {color};">
                        {task_name}
                    </div>
                </div>
                """
            except (ValueError, TypeError):
                # Skip tasks with invalid timestamps
                pass
    
    # Generate task details
    task_details_html = ""
    for task_id, task_data in tasks.items():
        task_name = task_data.get("name", task_id)
        task_status = task_data.get("status", "UNKNOWN")
        task_start = task_data.get("start_time", "")
        task_end = task_data.get("end_time", "")
        
        # Format timestamps
        try:
            start_dt = datetime.fromisoformat(task_start)
            task_start = start_dt.strftime("%Y-%m-%d %H:%M:%S")
        except (ValueError, TypeError):
            pass
        
        try:
            end_dt = datetime.fromisoformat(task_end)
            task_end = end_dt.strftime("%Y-%m-%d %H:%M:%S")
        except (ValueError, TypeError):
            pass
        
        # Calculate duration
        task_duration = ""
        if task_start and task_end:
            try:
                start_dt = datetime.fromisoformat(task_data.get("start_time", ""))
                end_dt = datetime.fromisoformat(task_data.get("end_time", ""))
                task_duration = f"{(end_dt - start_dt).total_seconds():.2f} seconds"
            except (ValueError, TypeError):
                pass
        
        # Determine status class
        status_class = "success" if task_status == "COMPLETED" else "failed" if task_status == "FAILED" else "running"
        
        task_details_html += f"""
        <div class="task-card">
            <div class="task-header">
                <h3>{task_name}</h3>
                <span class="task-status status-{status_class}">{task_status}</span>
            </div>
            <div class="task-time">
                <p>Start: {task_start}</p>
                <p>End: {task_end}</p>
                <p>Duration: <span class="task-duration">{task_duration}</span></p>
            </div>
        </div>
        """
    
    # Generate HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Taskinity Flow Execution: {flow_name}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        h1, h2, h3 {{
            color: #333;
        }}
        .flow-summary {{
            background-color: #f0f8ff;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}
        .task-timeline {{
            margin: 30px 0;
            position: relative;
        }}
        .timeline-bar {{
            height: 30px;
            background-color: #e0e0e0;
            border-radius: 5px;
            margin-bottom: 10px;
            position: relative;
        }}
        .task-bar {{
            height: 100%;
            border-radius: 5px;
            position: absolute;
            top: 0;
            display: flex;
            align-items: center;
            padding-left: 10px;
            color: white;
            font-weight: bold;
            box-sizing: border-box;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}
        .task-details {{
            margin-top: 30px;
        }}
        .task-card {{
            background-color: #f9f9f9;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 15px;
            border-left: 5px solid #4CAF50;
        }}
        .task-card:nth-child(odd) {{
            background-color: #f0f0f0;
        }}
        .task-header {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
        }}
        .task-status {{
            padding: 3px 8px;
            border-radius: 3px;
            color: white;
            font-size: 0.8em;
        }}
        .status-success {{
            background-color: #4CAF50;
        }}
        .status-failed {{
            background-color: #f44336;
        }}
        .status-running {{
            background-color: #2196F3;
        }}
        .task-time {{
            font-size: 0.9em;
            color: #666;
        }}
        .task-duration {{
            font-weight: bold;
            color: #333;
        }}
        .footer {{
            margin-top: 30px;
            text-align: center;
            font-size: 0.8em;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Taskinity Flow Execution Visualization</h1>
        
        <div class="flow-summary">
            <h2>Flow Summary</h2>
            <p><strong>Name:</strong> {flow_name}</p>
            <p><strong>ID:</strong> {flow_id}</p>
            <p><strong>Start Time:</strong> {formatted_start}</p>
            <p><strong>End Time:</strong> {formatted_end}</p>
            <p><strong>Duration:</strong> {duration}</p>
            <p><strong>Status:</strong> <span class="task-status status-{'success' if status == 'COMPLETED' else 'failed' if status == 'FAILED' else 'running'}">{status}</span></p>
        </div>
        
        <h2>Task Timeline</h2>
        <div class="task-timeline">
            {timeline_html}
        </div>
        
        <h2>Task Details</h2>
        <div class="task-details">
            {task_details_html}
        </div>
        
        <div class="footer">
            Generated by Taskinity Execution Visualizer
        </div>
    </div>
</body>
</html>
"""
    
    # Save to file if requested
    if output_file:
        with open(output_file, 'w') as f:
            f.write(html)
        return output_file
    
    return html


def _generate_matplotlib_visualization(
    execution_data: Dict[str, Any],
    output_file: str,
    format: str = "png"
) -> str:
    """
    Generate a visualization of the flow execution using Matplotlib.
    
    Args:
        execution_data: Flow execution data
        output_file: Path to save the visualization
        format: Output format (svg, png, pdf)
        
    Returns:
        Path to the saved visualization
    """
    if not MATPLOTLIB_AVAILABLE:
        raise ImportError("Matplotlib is required for visualization. Install with: pip install matplotlib")
    
    flow_name = execution_data.get("name", "Unknown Flow")
    tasks = execution_data.get("tasks", {})
    
    # Prepare data for Gantt chart
    task_names = []
    start_times = []
    end_times = []
    colors = []
    
    for task_id, task_data in tasks.items():
        task_name = task_data.get("name", task_id)
        task_status = task_data.get("status", "UNKNOWN")
        
        try:
            start_time = datetime.fromisoformat(task_data.get("start_time", ""))
            end_time = datetime.fromisoformat(task_data.get("end_time", ""))
            
            task_names.append(task_name)
            start_times.append(start_time)
            end_times.append(end_time)
            
            # Determine color based on status
            if task_status == "COMPLETED":
                colors.append("#4CAF50")  # Green
            elif task_status == "FAILED":
                colors.append("#f44336")  # Red
            else:
                colors.append("#2196F3")  # Blue
        except (ValueError, TypeError):
            # Skip tasks with invalid timestamps
            pass
    
    # Create figure
    fig, ax = plt.figure(figsize=(12, 8)), plt.gca()
    
    # Plot Gantt chart
    y_positions = range(len(task_names))
    
    for i, (start, end, color) in enumerate(zip(start_times, end_times, colors)):
        duration = (end - start).total_seconds() / 60  # Duration in minutes
        ax.barh(i, duration, left=mdates.date2num(start), height=0.5, 
                color=color, alpha=0.8, edgecolor="black")
    
    # Format the chart
    ax.set_yticks(y_positions)
    ax.set_yticklabels(task_names)
    ax.set_xlabel("Time")
    ax.set_title(f"Taskinity Flow Execution: {flow_name}")
    
    # Format x-axis as time
    ax.xaxis_date()
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
    
    # Add grid
    ax.grid(True, axis='x', linestyle='--', alpha=0.7)
    
    # Adjust layout
    plt.tight_layout()
    
    # Save the figure
    plt.savefig(output_file, format=format.lower())
    plt.close()
    
    return output_file
