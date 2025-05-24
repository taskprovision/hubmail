#!/usr/bin/env python3
"""
Narzędzie do wizualizacji przepływów taskinity z wykorzystaniem Mermaid.
"""
import os
import json
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional

from flow_dsl import parse_dsl, load_dsl, list_dsl_files, list_flows

def generate_mermaid_from_dsl(dsl_text: str) -> str:
    """
    Generuje kod Mermaid na podstawie tekstu DSL.
    
    Args:
        dsl_text: Tekst DSL
        
    Returns:
        Kod Mermaid
    """
    # Parsowanie DSL
    flow_def = parse_dsl(dsl_text)
    flow_name = flow_def["name"]
    connections = flow_def["connections"]
    description = flow_def.get("description", "")
    
    # Generowanie kodu Mermaid
    mermaid = "graph TD\n"
    
    # Dodanie tytułu
    mermaid += f"    %% {flow_name}: {description}\n"
    
    # Dodanie węzłów i krawędzi
    for conn in connections:
        source = conn["source"]
        target = conn["target"]
        mermaid += f"    {source}[{source}] --> {target}[{target}]\n"
    
    return mermaid

def generate_mermaid_from_flow_history(flow_id: str) -> str:
    """
    Generuje kod Mermaid na podstawie historii wykonania przepływu.
    
    Args:
        flow_id: ID przepływu
        
    Returns:
        Kod Mermaid
    """
    # Ścieżka do pliku przepływu
    flow_dir = os.path.join(os.path.dirname(__file__), "flows")
    flow_file = os.path.join(flow_dir, f"{flow_id}.json")
    
    if not os.path.exists(flow_file):
        return f"graph TD\n    A[Nie znaleziono przepływu {flow_id}]"
    
    # Wczytanie danych przepływu
    with open(flow_file, "r") as f:
        flow_data = json.load(f)
    
    flow_name = flow_data.get("name", flow_id)
    flow_status = flow_data.get("status", "UNKNOWN")
    flow_duration = flow_data.get("duration", 0)
    
    # Generowanie kodu Mermaid
    mermaid = "graph TD\n"
    
    # Dodanie tytułu
    mermaid += f"    %% {flow_name} (Status: {flow_status}, Czas: {flow_duration:.2f}s)\n"
    
    # Wczytanie zadań
    tasks = flow_data.get("tasks", [])
    task_details = {}
    connections = []
    
    for task_id in tasks:
        task_file = os.path.join(flow_dir, f"{task_id}.json")
        if os.path.exists(task_file):
            with open(task_file, "r") as f:
                task_data = json.load(f)
                task_name = task_data.get("name", task_id)
                task_status = task_data.get("status", "UNKNOWN")
                task_duration = task_data.get("duration", 0)
                
                # Dodanie stylu w zależności od statusu
                style = ""
                if task_status == "COMPLETED":
                    style = "fill:#9f9,stroke:#6c6"
                elif task_status == "FAILED":
                    style = "fill:#f99,stroke:#c66"
                elif task_status == "RUNNING":
                    style = "fill:#9cf,stroke:#69c"
                else:
                    style = "fill:#eee,stroke:#999"
                
                task_details[task_id] = {
                    "name": task_name,
                    "status": task_status,
                    "duration": task_duration,
                    "style": style
                }
                
                # Dodanie połączeń na podstawie zależności
                for dep_id in task_data.get("depends_on", []):
                    connections.append((dep_id, task_id))
    
    # Dodanie węzłów
    for task_id, details in task_details.items():
        node_label = f"{details['name']}\\n({details['status']}, {details['duration']:.2f}s)"
        mermaid += f"    {task_id}[\"{node_label}\"]:::status{details['status']}\n"
    
    # Dodanie krawędzi
    for source, target in connections:
        if source in task_details and target in task_details:
            mermaid += f"    {source} --> {target}\n"
    
    # Dodanie stylów
    mermaid += "    classDef statusCOMPLETED fill:#9f9,stroke:#6c6;\n"
    mermaid += "    classDef statusFAILED fill:#f99,stroke:#c66;\n"
    mermaid += "    classDef statusRUNNING fill:#9cf,stroke:#69c;\n"
    mermaid += "    classDef statusPENDING fill:#eee,stroke:#999;\n"
    
    return mermaid

def generate_html(mermaid_code: str, title: str = "Wizualizacja przepływu") -> str:
    """
    Generuje kod HTML z osadzonym diagramem Mermaid.
    
    Args:
        mermaid_code: Kod Mermaid
        title: Tytuł strony
        
    Returns:
        Kod HTML
    """
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
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
        h1 {{
            color: #4a86e8;
            text-align: center;
        }}
        .mermaid {{
            text-align: center;
        }}
        pre {{
            background-color: #f8f8f8;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{title}</h1>
        <div class="mermaid">
{mermaid_code}
        </div>
        <h2>Kod Mermaid</h2>
        <pre>{mermaid_code}</pre>
    </div>
    <script>
        mermaid.initialize({{ startOnLoad: true }});
    </script>
</body>
</html>"""
    return html

def save_html(html_code: str, output_file: str):
    """
    Zapisuje kod HTML do pliku.
    
    Args:
        html_code: Kod HTML
        output_file: Ścieżka do pliku wyjściowego
    """
    with open(output_file, "w") as f:
        f.write(html_code)
    print(f"Zapisano wizualizację do pliku: {output_file}")

def generate_ascii_diagram(dsl_text: str) -> str:
    """
    Generuje diagram ASCII na podstawie tekstu DSL.
    
    Args:
        dsl_text: Tekst DSL
        
    Returns:
        Diagram ASCII
    """
    # Parsowanie DSL
    flow_def = parse_dsl(dsl_text)
    flow_name = flow_def["name"]
    connections = flow_def["connections"]
    
    # Budowanie grafu
    nodes = set()
    edges = []
    
    for conn in connections:
        source = conn["source"]
        target = conn["target"]
        nodes.add(source)
        nodes.add(target)
        edges.append((source, target))
    
    # Sortowanie węzłów
    nodes = sorted(list(nodes))
    
    # Generowanie diagramu ASCII
    ascii_diagram = f"=== {flow_name} ===\n\n"
    
    # Dodanie węzłów
    for node in nodes:
        ascii_diagram += f"[{node}]\n"
    
    ascii_diagram += "\nPołączenia:\n"
    
    # Dodanie krawędzi
    for source, target in edges:
        ascii_diagram += f"{source} --> {target}\n"
    
    return ascii_diagram

def main():
    """Główna funkcja skryptu."""
    parser = argparse.ArgumentParser(description="Wizualizacja przepływów taskinity")
    subparsers = parser.add_subparsers(dest="command", help="Komenda do wykonania")
    
    # Parser dla komendy "dsl"
    dsl_parser = subparsers.add_parser("dsl", help="Wizualizacja definicji DSL")
    dsl_parser.add_argument("--file", type=str, help="Plik DSL do wizualizacji")
    dsl_parser.add_argument("--text", type=str, help="Tekst DSL do wizualizacji")
    dsl_parser.add_argument("--output", type=str, help="Plik wyjściowy HTML")
    dsl_parser.add_argument("--ascii", action="store_true", help="Generuj diagram ASCII zamiast HTML")
    
    # Parser dla komendy "flow"
    flow_parser = subparsers.add_parser("flow", help="Wizualizacja historii przepływu")
    flow_parser.add_argument("flow_id", type=str, help="ID przepływu do wizualizacji")
    flow_parser.add_argument("--output", type=str, help="Plik wyjściowy HTML")
    flow_parser.add_argument("--ascii", action="store_true", help="Generuj diagram ASCII zamiast HTML")
    
    # Parser dla komendy "list"
    list_parser = subparsers.add_parser("list", help="Wyświetlenie listy dostępnych przepływów")
    list_parser.add_argument("--dsl", action="store_true", help="Wyświetl definicje DSL")
    list_parser.add_argument("--flows", action="store_true", help="Wyświetl historię przepływów")
    
    args = parser.parse_args()
    
    if args.command == "dsl":
        if args.file:
            dsl_text = load_dsl(args.file)
        elif args.text:
            dsl_text = args.text
        else:
            print("Musisz podać plik lub tekst DSL")
            return
        
        if args.ascii:
            ascii_diagram = generate_ascii_diagram(dsl_text)
            if args.output:
                with open(args.output, "w") as f:
                    f.write(ascii_diagram)
                print(f"Zapisano diagram ASCII do pliku: {args.output}")
            else:
                print(ascii_diagram)
        else:
            mermaid_code = generate_mermaid_from_dsl(dsl_text)
            html_code = generate_html(mermaid_code, f"Wizualizacja DSL")
            
            if args.output:
                save_html(html_code, args.output)
            else:
                print(html_code)
    
    elif args.command == "flow":
        if args.ascii:
            # TODO: Implementacja diagramu ASCII dla historii przepływu
            print("Generowanie diagramu ASCII dla historii przepływu nie jest jeszcze zaimplementowane")
        else:
            mermaid_code = generate_mermaid_from_flow_history(args.flow_id)
            html_code = generate_html(mermaid_code, f"Wizualizacja przepływu {args.flow_id}")
            
            if args.output:
                save_html(html_code, args.output)
            else:
                print(html_code)
    
    elif args.command == "list":
        if args.dsl:
            dsl_files = list_dsl_files()
            print("Dostępne definicje DSL:")
            for i, dsl_file in enumerate(dsl_files, 1):
                print(f"{i}. {dsl_file}")
        
        if args.flows:
            flows = list_flows()
            print("Historia przepływów:")
            for i, flow in enumerate(flows, 1):
                flow_id = flow.get("flow_id", "")
                flow_name = flow.get("name", "")
                flow_status = flow.get("status", "")
                flow_time = flow.get("start_time", "")
                print(f"{i}. {flow_name} (ID: {flow_id}, Status: {flow_status}, Czas: {flow_time})")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
