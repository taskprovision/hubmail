#!/usr/bin/env python3
"""
Prosty skrypt do wizualizacji przepływów DSL.
"""
import os
import json
import argparse
from pathlib import Path
from typing import Dict, List, Any

import matplotlib.pyplot as plt
import networkx as nx

from flow_dsl import parse_dsl, load_dsl, list_dsl_files, list_flows

def visualize_dsl(dsl_text: str, output_file: str = None):
    """
    Wizualizuje przepływ zdefiniowany w DSL.
    
    Args:
        dsl_text: Tekst DSL
        output_file: Opcjonalna ścieżka do pliku wyjściowego
    """
    # Parsowanie DSL
    flow_def = parse_dsl(dsl_text)
    flow_name = flow_def["name"]
    connections = flow_def["connections"]
    
    # Tworzenie grafu
    G = nx.DiGraph()
    
    # Dodawanie węzłów i krawędzi
    for conn in connections:
        source = conn["source"]
        target = conn["target"]
        G.add_node(source)
        G.add_node(target)
        G.add_edge(source, target)
    
    # Rysowanie grafu
    plt.figure(figsize=(12, 8))
    pos = nx.spring_layout(G, seed=42)  # Pozycje węzłów
    
    # Rysowanie węzłów
    nx.draw_networkx_nodes(G, pos, node_size=2000, node_color="lightblue", alpha=0.8)
    nx.draw_networkx_labels(G, pos, font_size=12, font_weight="bold")
    
    # Rysowanie krawędzi
    nx.draw_networkx_edges(G, pos, width=2, alpha=0.7, edge_color="gray", 
                          arrowsize=20, connectionstyle="arc3,rad=0.1")
    
    # Tytuł
    plt.title(f"Przepływ: {flow_name}", fontsize=16)
    plt.axis("off")
    
    # Zapisywanie lub wyświetlanie
    if output_file:
        plt.savefig(output_file, bbox_inches="tight")
        print(f"Zapisano wizualizację do pliku: {output_file}")
    else:
        plt.show()

def visualize_flow_history(flow_id: str, output_file: str = None):
    """
    Wizualizuje historię wykonania przepływu.
    
    Args:
        flow_id: Identyfikator przepływu
        output_file: Opcjonalna ścieżka do pliku wyjściowego
    """
    # Ścieżka do pliku przepływu
    flow_dir = os.path.join(os.path.dirname(__file__), "flows")
    flow_file = os.path.join(flow_dir, f"{flow_id}.json")
    
    if not os.path.exists(flow_file):
        print(f"Nie znaleziono przepływu o ID: {flow_id}")
        return
    
    # Wczytanie danych przepływu
    with open(flow_file, "r") as f:
        flow_data = json.load(f)
    
    # Tworzenie grafu
    G = nx.DiGraph()
    
    # Dodawanie węzłów i krawędzi na podstawie historii zadań
    tasks = flow_data.get("tasks", [])
    
    # Wczytanie szczegółów zadań
    task_details = {}
    for task_id in tasks:
        task_file = os.path.join(flow_dir, f"{task_id}.json")
        if os.path.exists(task_file):
            with open(task_file, "r") as f:
                task_data = json.load(f)
                task_name = task_data.get("name", task_id)
                task_status = task_data.get("status", "UNKNOWN")
                task_duration = task_data.get("duration", 0)
                task_details[task_id] = {
                    "name": task_name,
                    "status": task_status,
                    "duration": task_duration
                }
    
    # Dodawanie węzłów
    for task_id, details in task_details.items():
        G.add_node(task_id, **details)
    
    # Dodawanie krawędzi na podstawie zależności
    # TODO: Dodać logikę odtwarzania zależności między zadaniami
    
    # Rysowanie grafu
    plt.figure(figsize=(12, 8))
    pos = nx.spring_layout(G, seed=42)  # Pozycje węzłów
    
    # Kolory węzłów w zależności od statusu
    color_map = {
        "COMPLETED": "lightgreen",
        "FAILED": "lightcoral",
        "RUNNING": "lightskyblue",
        "PENDING": "lightgray",
        "SKIPPED": "lightyellow"
    }
    
    # Rysowanie węzłów
    for status in color_map:
        nodes = [n for n, d in G.nodes(data=True) if d.get("status") == status]
        if nodes:
            nx.draw_networkx_nodes(G, pos, nodelist=nodes, node_size=2000, 
                                  node_color=color_map[status], alpha=0.8)
    
    # Rysowanie etykiet
    labels = {n: f"{d.get('name', n)}\n({d.get('duration', 0):.2f}s)" 
              for n, d in G.nodes(data=True)}
    nx.draw_networkx_labels(G, pos, labels=labels, font_size=10)
    
    # Rysowanie krawędzi
    nx.draw_networkx_edges(G, pos, width=2, alpha=0.7, edge_color="gray",
                          arrowsize=20, connectionstyle="arc3,rad=0.1")
    
    # Tytuł
    flow_name = flow_data.get("name", flow_id)
    flow_status = flow_data.get("status", "UNKNOWN")
    flow_duration = flow_data.get("duration", 0)
    plt.title(f"Przepływ: {flow_name} (Status: {flow_status}, Czas: {flow_duration:.2f}s)", 
              fontsize=16)
    plt.axis("off")
    
    # Dodanie legendy
    legend_elements = [plt.Line2D([0], [0], marker='o', color='w', 
                                 label=status, markerfacecolor=color, markersize=15)
                      for status, color in color_map.items()]
    plt.legend(handles=legend_elements, loc='upper right')
    
    # Zapisywanie lub wyświetlanie
    if output_file:
        plt.savefig(output_file, bbox_inches="tight")
        print(f"Zapisano wizualizację do pliku: {output_file}")
    else:
        plt.show()

def main():
    """Główna funkcja skryptu."""
    parser = argparse.ArgumentParser(description="Wizualizacja przepływów DSL")
    subparsers = parser.add_subparsers(dest="command", help="Komenda do wykonania")
    
    # Parser dla komendy "dsl"
    dsl_parser = subparsers.add_parser("dsl", help="Wizualizacja definicji DSL")
    dsl_parser.add_argument("--file", type=str, help="Plik DSL do wizualizacji")
    dsl_parser.add_argument("--text", type=str, help="Tekst DSL do wizualizacji")
    dsl_parser.add_argument("--output", type=str, help="Plik wyjściowy")
    
    # Parser dla komendy "flow"
    flow_parser = subparsers.add_parser("flow", help="Wizualizacja historii przepływu")
    flow_parser.add_argument("flow_id", type=str, help="ID przepływu do wizualizacji")
    flow_parser.add_argument("--output", type=str, help="Plik wyjściowy")
    
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
        
        visualize_dsl(dsl_text, args.output)
    
    elif args.command == "flow":
        visualize_flow_history(args.flow_id, args.output)
    
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
