#!/usr/bin/env python
"""
Interfejs wiersza poleceń dla Taskinity.
"""

import argparse
import sys
from pathlib import Path
from typing import Dict, Any, Optional

from taskinity.flow_dsl import run_flow_from_dsl, load_dsl
from taskinity.parallel_executor import run_parallel_flow_from_dsl
from taskinity.flow_visualizer import visualize_flow
from taskinity.flow_scheduler import FlowScheduler


def main() -> int:
    """Główna funkcja CLI."""
    parser = argparse.ArgumentParser(description="Taskinity - Inteligentny Framework do Orkiestracji Zadań")
    subparsers = parser.add_subparsers(dest="command", help="Dostępne komendy")

    # Komenda run
    run_parser = subparsers.add_parser("run", help="Uruchom przepływ")
    run_parser.add_argument("flow_file", help="Ścieżka do pliku z definicją przepływu")
    run_parser.add_argument("--input", "-i", help="Dane wejściowe w formacie JSON", default="{}")
    run_parser.add_argument("--parallel", "-p", action="store_true", help="Uruchom w trybie równoległym")
    
    # Komenda visualize
    viz_parser = subparsers.add_parser("visualize", help="Wizualizuj przepływ")
    viz_parser.add_argument("flow_file", help="Ścieżka do pliku z definicją przepływu")
    viz_parser.add_argument("--output", "-o", help="Ścieżka do pliku wyjściowego")
    viz_parser.add_argument("--format", "-f", choices=["png", "svg", "pdf"], default="svg", 
                           help="Format pliku wyjściowego")
    
    # Komenda scheduler
    sched_parser = subparsers.add_parser("scheduler", help="Zarządzaj harmonogramem przepływów")
    sched_subparsers = sched_parser.add_subparsers(dest="scheduler_command", help="Komendy harmonogramu")
    
    # Komenda scheduler start
    sched_start = sched_subparsers.add_parser("start", help="Uruchom harmonogram")
    sched_start.add_argument("--daemon", "-d", action="store_true", help="Uruchom jako daemon")
    
    # Komenda scheduler stop
    sched_subparsers.add_parser("stop", help="Zatrzymaj harmonogram")
    
    # Komenda scheduler list
    sched_subparsers.add_parser("list", help="Wyświetl zaplanowane przepływy")
    
    # Komenda scheduler add
    sched_add = sched_subparsers.add_parser("add", help="Dodaj przepływ do harmonogramu")
    sched_add.add_argument("flow_file", help="Ścieżka do pliku z definicją przepływu")
    sched_add.add_argument("--interval", "-i", type=int, help="Interwał w minutach")
    sched_add.add_argument("--daily", "-d", help="Czas codzienny (format HH:MM)")
    sched_add.add_argument("--input", help="Dane wejściowe w formacie JSON", default="{}")
    
    # Komenda scheduler remove
    sched_remove = sched_subparsers.add_parser("remove", help="Usuń przepływ z harmonogramu")
    sched_remove.add_argument("schedule_id", help="ID harmonogramu")
    
    # Komenda dashboard
    dash_parser = subparsers.add_parser("dashboard", help="Uruchom dashboard")
    dash_parser.add_argument("--port", "-p", type=int, default=8501, help="Port dla dashboardu")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        if args.command == "run":
            return handle_run_command(args)
        elif args.command == "visualize":
            return handle_visualize_command(args)
        elif args.command == "scheduler":
            return handle_scheduler_command(args)
        elif args.command == "dashboard":
            return handle_dashboard_command(args)
    except Exception as e:
        print(f"Błąd: {str(e)}", file=sys.stderr)
        return 1
    
    return 0


def handle_run_command(args: argparse.Namespace) -> int:
    """Obsługa komendy run."""
    import json
    
    flow_file = Path(args.flow_file)
    if not flow_file.exists():
        print(f"Błąd: Plik {flow_file} nie istnieje", file=sys.stderr)
        return 1
    
    try:
        input_data = json.loads(args.input)
    except json.JSONDecodeError:
        print("Błąd: Nieprawidłowy format JSON dla danych wejściowych", file=sys.stderr)
        return 1
    
    dsl_content = load_dsl(str(flow_file))
    
    print(f"Uruchamianie przepływu z pliku: {flow_file}")
    if args.parallel:
        print("Tryb wykonania: równoległy")
        result = run_parallel_flow_from_dsl(dsl_content, input_data)
    else:
        print("Tryb wykonania: sekwencyjny")
        result = run_flow_from_dsl(dsl_content, input_data)
    
    print("\nWynik przepływu:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


def handle_visualize_command(args: argparse.Namespace) -> int:
    """Obsługa komendy visualize."""
    flow_file = Path(args.flow_file)
    if not flow_file.exists():
        print(f"Błąd: Plik {flow_file} nie istnieje", file=sys.stderr)
        return 1
    
    dsl_content = load_dsl(str(flow_file))
    
    output_file = args.output
    if not output_file:
        output_file = flow_file.with_suffix(f".{args.format}")
    
    print(f"Generowanie wizualizacji dla przepływu: {flow_file}")
    print(f"Format wyjściowy: {args.format}")
    print(f"Plik wyjściowy: {output_file}")
    
    visualize_flow(dsl_content, output_file, args.format)
    print(f"Wizualizacja zapisana do: {output_file}")
    return 0


def handle_scheduler_command(args: argparse.Namespace) -> int:
    """Obsługa komendy scheduler."""
    if not args.scheduler_command:
        print("Błąd: Nie podano komendy dla harmonogramu", file=sys.stderr)
        return 1
    
    scheduler = FlowScheduler()
    
    if args.scheduler_command == "start":
        print("Uruchamianie harmonogramu przepływów...")
        scheduler.start(daemon=args.daemon)
        return 0
    
    elif args.scheduler_command == "stop":
        print("Zatrzymywanie harmonogramu przepływów...")
        scheduler.stop()
        return 0
    
    elif args.scheduler_command == "list":
        schedules = scheduler.list_schedules()
        if not schedules:
            print("Brak zaplanowanych przepływów")
        else:
            print("Zaplanowane przepływy:")
            for schedule in schedules:
                schedule_type = "interwał" if schedule.get("interval") else "codzienny"
                schedule_time = f"{schedule['interval']} min" if schedule.get("interval") else schedule.get("daily")
                print(f"- ID: {schedule['id']}, Typ: {schedule_type}, Czas: {schedule_time}, Plik: {schedule['dsl_file']}")
        return 0
    
    elif args.scheduler_command == "add":
        import json
        
        flow_file = Path(args.flow_file)
        if not flow_file.exists():
            print(f"Błąd: Plik {flow_file} nie istnieje", file=sys.stderr)
            return 1
        
        if not args.interval and not args.daily:
            print("Błąd: Należy podać interwał lub czas codzienny", file=sys.stderr)
            return 1
        
        try:
            input_data = json.loads(args.input)
        except json.JSONDecodeError:
            print("Błąd: Nieprawidłowy format JSON dla danych wejściowych", file=sys.stderr)
            return 1
        
        schedule_id = scheduler.add_schedule(
            str(flow_file),
            interval=args.interval,
            daily=args.daily,
            input_data=input_data
        )
        
        print(f"Dodano przepływ do harmonogramu z ID: {schedule_id}")
        return 0
    
    elif args.scheduler_command == "remove":
        success = scheduler.remove_schedule(args.schedule_id)
        if success:
            print(f"Usunięto przepływ z harmonogramu: {args.schedule_id}")
            return 0
        else:
            print(f"Błąd: Nie znaleziono harmonogramu o ID: {args.schedule_id}", file=sys.stderr)
            return 1
    
    return 1


def handle_dashboard_command(args: argparse.Namespace) -> int:
    """Obsługa komendy dashboard."""
    try:
        from taskinity.simple_dashboard import run_dashboard
        print(f"Uruchamianie dashboardu na porcie {args.port}...")
        run_dashboard(port=args.port)
        return 0
    except ImportError:
        print("Błąd: Nie można uruchomić dashboardu. Zainstaluj wymagane zależności:", file=sys.stderr)
        print("  pip install taskinity[web]", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
