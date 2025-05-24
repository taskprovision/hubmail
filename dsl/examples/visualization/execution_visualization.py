#!/usr/bin/env python3
"""
Przykład wizualizacji wykonania przepływów Taskinity.
"""
import os
import json
import time
import random
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

# Import funkcji z Taskinity
from taskinity import task, flow, run_flow_from_dsl, save_dsl
from taskinity import visualize_execution, generate_execution_report

# Ładowanie zmiennych środowiskowych
load_dotenv()

# Konfiguracja ścieżek
BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output"
DSL_DIR = BASE_DIR / "dsl"

# Upewniamy się, że katalogi istnieją
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(DSL_DIR, exist_ok=True)

# Przykładowy przepływ do wizualizacji wykonania
EXECUTION_DEMO_DSL = """
flow ExecutionVisualizationDemo:
    description: "Przepływ demonstracyjny wizualizacji wykonania"
    
    task DataIngestion:
        description: "Pobieranie danych z różnych źródeł"
        code: |
            import time
            import random
            
            print("Pobieranie danych z różnych źródeł...")
            
            # Symulacja czasu wykonania
            execution_time = random.uniform(1.0, 3.0)
            time.sleep(execution_time)
            
            # Symulacja pobranych danych
            data_sources = ["API", "Database", "File", "Stream"]
            data_records = {}
            
            for source in data_sources:
                record_count = random.randint(100, 1000)
                data_records[source] = {
                    "count": record_count,
                    "size_mb": round(record_count * 0.01, 2),
                    "status": "success"
                }
                print(f"Pobrano {record_count} rekordów z {source}")
            
            print(f"Zakończono pobieranie danych w {execution_time:.2f}s")
            return {
                "data_records": data_records,
                "execution_time": execution_time,
                "total_records": sum(data["count"] for data in data_records.values())
            }
    
    task DataCleaning:
        description: "Czyszczenie i walidacja danych"
        code: |
            import time
            import random
            
            print("Czyszczenie i walidacja danych...")
            
            # Symulacja czasu wykonania
            execution_time = random.uniform(2.0, 4.0)
            time.sleep(execution_time)
            
            data_records = inputs["DataIngestion"]["data_records"]
            cleaned_records = {}
            
            for source, data in data_records.items():
                # Symulacja czyszczenia danych
                original_count = data["count"]
                invalid_count = random.randint(0, int(original_count * 0.1))
                cleaned_count = original_count - invalid_count
                
                cleaned_records[source] = {
                    "original_count": original_count,
                    "cleaned_count": cleaned_count,
                    "invalid_count": invalid_count,
                    "validity_rate": round((cleaned_count / original_count) * 100, 2)
                }
                
                print(f"Wyczyszczono dane z {source}: {invalid_count} nieprawidłowych rekordów usunięto")
            
            print(f"Zakończono czyszczenie danych w {execution_time:.2f}s")
            return {
                "cleaned_records": cleaned_records,
                "execution_time": execution_time,
                "total_cleaned": sum(data["cleaned_count"] for data in cleaned_records.values()),
                "total_invalid": sum(data["invalid_count"] for data in cleaned_records.values())
            }
    
    task DataProcessing:
        description: "Przetwarzanie danych"
        code: |
            import time
            import random
            
            print("Przetwarzanie danych...")
            
            # Symulacja czasu wykonania
            execution_time = random.uniform(3.0, 6.0)
            time.sleep(execution_time)
            
            cleaned_records = inputs["DataCleaning"]["cleaned_records"]
            processed_records = {}
            
            for source, data in cleaned_records.items():
                # Symulacja przetwarzania danych
                processed_count = data["cleaned_count"]
                
                processed_records[source] = {
                    "input_count": processed_count,
                    "output_count": processed_count,
                    "processing_time": round(random.uniform(0.5, 2.0), 2)
                }
                
                print(f"Przetworzono {processed_count} rekordów z {source}")
            
            print(f"Zakończono przetwarzanie danych w {execution_time:.2f}s")
            return {
                "processed_records": processed_records,
                "execution_time": execution_time,
                "total_processed": sum(data["output_count"] for data in processed_records.values())
            }
    
    task DataAggregation:
        description: "Agregacja danych"
        code: |
            import time
            import random
            
            print("Agregacja danych...")
            
            # Symulacja czasu wykonania
            execution_time = random.uniform(1.5, 3.5)
            time.sleep(execution_time)
            
            processed_records = inputs["DataProcessing"]["processed_records"]
            
            # Symulacja agregacji danych
            total_records = sum(data["output_count"] for data in processed_records.values())
            aggregation_result = {
                "total_records": total_records,
                "aggregation_count": len(processed_records),
                "average_per_source": round(total_records / len(processed_records), 2),
                "aggregation_time": round(execution_time, 2)
            }
            
            print(f"Zagregowano dane z {len(processed_records)} źródeł, łącznie {total_records} rekordów")
            print(f"Zakończono agregację danych w {execution_time:.2f}s")
            return {
                "aggregation_result": aggregation_result,
                "execution_time": execution_time
            }
    
    task ReportGeneration:
        description: "Generowanie raportu z wykonania"
        code: |
            import time
            import random
            import json
            from pathlib import Path
            from datetime import datetime
            
            print("Generowanie raportu z wykonania...")
            
            # Symulacja czasu wykonania
            execution_time = random.uniform(0.5, 1.5)
            time.sleep(execution_time)
            
            # Zbieranie danych z poprzednich zadań
            ingestion_data = inputs["DataIngestion"]
            cleaning_data = inputs["DataCleaning"]
            processing_data = inputs["DataProcessing"]
            aggregation_data = inputs["DataAggregation"]
            
            # Tworzenie raportu
            report = {
                "summary": {
                    "timestamp": datetime.now().isoformat(),
                    "total_execution_time": round(
                        ingestion_data["execution_time"] +
                        cleaning_data["execution_time"] +
                        processing_data["execution_time"] +
                        aggregation_data["execution_time"] +
                        execution_time,
                        2
                    ),
                    "total_records_processed": aggregation_data["aggregation_result"]["total_records"],
                    "data_sources": list(ingestion_data["data_records"].keys()),
                    "invalid_records": cleaning_data["total_invalid"]
                },
                "details": {
                    "ingestion": ingestion_data,
                    "cleaning": cleaning_data,
                    "processing": processing_data,
                    "aggregation": aggregation_data
                }
            }
            
            # Zapisanie raportu
            output_dir = Path("output")
            os.makedirs(output_dir, exist_ok=True)
            
            report_file = output_dir / "execution_report.json"
            with open(report_file, "w") as f:
                json.dump(report, f, indent=2)
            
            print(f"Zapisano raport do: {report_file}")
            print(f"Zakończono generowanie raportu w {execution_time:.2f}s")
            return {
                "report_file": str(report_file),
                "report": report,
                "execution_time": execution_time
            }
    
    DataIngestion -> DataCleaning -> DataProcessing -> DataAggregation -> ReportGeneration
"""

# Zapisanie definicji DSL
def save_dsl_definition():
    """Zapisuje definicję DSL do pliku."""
    dsl_file = DSL_DIR / "execution_visualization.taskinity"
    with open(dsl_file, "w") as f:
        f.write(EXECUTION_DEMO_DSL)
    print(f"Zapisano definicję DSL do: {dsl_file}")
    return str(dsl_file)


# Symulacja wykonania przepływu
def simulate_flow_execution():
    """Symuluje wykonanie przepływu i generuje dane wykonania."""
    print("Symulacja wykonania przepływu...")
    
    # Czas rozpoczęcia
    start_time = datetime.now()
    
    # Symulacja danych wykonania
    execution_data = {
        "flow_id": "execution-demo-" + start_time.strftime("%Y%m%d-%H%M%S"),
        "flow_name": "ExecutionVisualizationDemo",
        "start_time": start_time.isoformat(),
        "end_time": None,
        "status": "running",
        "tasks": {}
    }
    
    # Zadania w przepływie
    tasks = ["DataIngestion", "DataCleaning", "DataProcessing", "DataAggregation", "ReportGeneration"]
    
    # Symulacja wykonania zadań
    current_time = start_time
    
    for task_name in tasks:
        # Symulacja czasu wykonania
        task_duration = random.uniform(1.0, 5.0)
        task_start_time = current_time
        
        # Symulacja wykonania zadania
        print(f"Wykonywanie zadania {task_name}...")
        time.sleep(0.5)  # Krótka pauza dla symulacji
        
        # Aktualizacja czasu
        current_time += timedelta(seconds=task_duration)
        
        # Dodanie danych zadania
        execution_data["tasks"][task_name] = {
            "task_id": f"{task_name.lower()}-{start_time.strftime('%Y%m%d-%H%M%S')}",
            "task_name": task_name,
            "start_time": task_start_time.isoformat(),
            "end_time": current_time.isoformat(),
            "duration": task_duration,
            "status": "success",
            "inputs": {},
            "outputs": {
                "execution_time": task_duration,
                "records_processed": random.randint(100, 1000)
            }
        }
        
        print(f"Zadanie {task_name} zakończone w {task_duration:.2f}s")
    
    # Aktualizacja danych przepływu
    execution_data["end_time"] = current_time.isoformat()
    execution_data["status"] = "success"
    execution_data["duration"] = (current_time - start_time).total_seconds()
    
    print(f"Przepływ zakończony w {execution_data['duration']:.2f}s")
    
    # Zapisanie danych wykonania
    execution_file = OUTPUT_DIR / "execution_data.json"
    with open(execution_file, "w") as f:
        json.dump(execution_data, f, indent=2)
    
    print(f"Zapisano dane wykonania do: {execution_file}")
    return str(execution_file)


# Generowanie wizualizacji wykonania
def generate_execution_visualization(execution_file):
    """Generuje wizualizację wykonania przepływu."""
    print("Generowanie wizualizacji wykonania...")
    
    # Wczytanie danych wykonania
    with open(execution_file, "r") as f:
        execution_data = json.load(f)
    
    # Generowanie wizualizacji
    visualization_file = OUTPUT_DIR / "execution_visualization.html"
    
    # Symulacja funkcji wizualizacji wykonania
    visualize_execution_html = """<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Wizualizacja Wykonania Taskinity</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        h1, h2, h3 {
            color: #333;
        }
        .flow-summary {
            background-color: #f0f8ff;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .task-timeline {
            margin: 30px 0;
            position: relative;
        }
        .timeline-bar {
            height: 30px;
            background-color: #e0e0e0;
            border-radius: 5px;
            margin-bottom: 10px;
            position: relative;
        }
        .task-bar {
            height: 100%;
            background-color: #4CAF50;
            border-radius: 5px;
            position: absolute;
            top: 0;
            display: flex;
            align-items: center;
            padding-left: 10px;
            color: white;
            font-weight: bold;
            box-sizing: border-box;
        }
        .task-details {
            margin-top: 30px;
        }
        .task-card {
            background-color: #f9f9f9;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 15px;
            border-left: 5px solid #4CAF50;
        }
        .task-header {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
        }
        .task-status {
            padding: 3px 8px;
            border-radius: 3px;
            color: white;
            font-size: 0.8em;
        }
        .status-success {
            background-color: #4CAF50;
        }
        .status-failed {
            background-color: #f44336;
        }
        .status-running {
            background-color: #2196F3;
        }
        .task-time {
            font-size: 0.9em;
            color: #666;
        }
        .task-duration {
            font-weight: bold;
            color: #333;
        }
        .task-io {
            margin-top: 10px;
            font-size: 0.9em;
        }
        .footer {
            margin-top: 30px;
            text-align: center;
            font-size: 0.8em;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Wizualizacja Wykonania Przepływu Taskinity</h1>
        
        <div class="flow-summary">
            <h2>Podsumowanie Przepływu</h2>
            <p><strong>Nazwa przepływu:</strong> {flow_name}</p>
            <p><strong>ID przepływu:</strong> {flow_id}</p>
            <p><strong>Czas rozpoczęcia:</strong> {start_time}</p>
            <p><strong>Czas zakończenia:</strong> {end_time}</p>
            <p><strong>Całkowity czas wykonania:</strong> {duration} sekund</p>
            <p><strong>Status:</strong> <span class="task-status status-{status_class}">{status}</span></p>
        </div>
        
        <h2>Oś Czasu Wykonania</h2>
        <div class="task-timeline">
            {timeline_html}
        </div>
        
        <h2>Szczegóły Zadań</h2>
        <div class="task-details">
            {task_details_html}
        </div>
        
        <div class="footer">
            Wygenerowano przez Taskinity Execution Visualizer
        </div>
    </div>
</body>
</html>
"""
    
    # Formatowanie daty
    def format_datetime(dt_str):
        dt = datetime.fromisoformat(dt_str)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    
    # Generowanie HTML dla osi czasu
    start_time = datetime.fromisoformat(execution_data["start_time"])
    end_time = datetime.fromisoformat(execution_data["end_time"])
    total_duration = (end_time - start_time).total_seconds()
    
    timeline_html = ""
    for task_name, task_data in execution_data["tasks"].items():
        task_start = datetime.fromisoformat(task_data["start_time"])
        task_end = datetime.fromisoformat(task_data["end_time"])
        
        start_offset = (task_start - start_time).total_seconds() / total_duration * 100
        duration_percent = task_data["duration"] / total_duration * 100
        
        timeline_html += f"""
        <div class="timeline-bar">
            <div class="task-bar" style="left: {start_offset}%; width: {duration_percent}%;">
                {task_name}
            </div>
        </div>
        """
    
    # Generowanie HTML dla szczegółów zadań
    task_details_html = ""
    for task_name, task_data in execution_data["tasks"].items():
        status_class = task_data["status"].lower()
        task_details_html += f"""
        <div class="task-card">
            <div class="task-header">
                <h3>{task_name}</h3>
                <span class="task-status status-{status_class}">{task_data["status"]}</span>
            </div>
            <div class="task-time">
                <p>Rozpoczęcie: {format_datetime(task_data["start_time"])}</p>
                <p>Zakończenie: {format_datetime(task_data["end_time"])}</p>
                <p>Czas wykonania: <span class="task-duration">{task_data["duration"]:.2f} sekund</span></p>
            </div>
            <div class="task-io">
                <p><strong>Przetworzone rekordy:</strong> {task_data["outputs"]["records_processed"]}</p>
            </div>
        </div>
        """
    
    # Wypełnienie szablonu
    html_content = visualize_execution_html.format(
        flow_name=execution_data["flow_name"],
        flow_id=execution_data["flow_id"],
        start_time=format_datetime(execution_data["start_time"]),
        end_time=format_datetime(execution_data["end_time"]),
        duration=f"{execution_data['duration']:.2f}",
        status=execution_data["status"],
        status_class=execution_data["status"].lower(),
        timeline_html=timeline_html,
        task_details_html=task_details_html
    )
    
    # Zapisanie HTML
    with open(visualization_file, "w") as f:
        f.write(html_content)
    
    print(f"Zapisano wizualizację wykonania do: {visualization_file}")
    return str(visualization_file)


# Generowanie raportu z wykonania
def generate_execution_report(execution_file):
    """Generuje raport z wykonania przepływu."""
    print("Generowanie raportu z wykonania...")
    
    # Wczytanie danych wykonania
    with open(execution_file, "r") as f:
        execution_data = json.load(f)
    
    # Generowanie raportu
    report = {
        "flow_summary": {
            "name": execution_data["flow_name"],
            "id": execution_data["flow_id"],
            "start_time": execution_data["start_time"],
            "end_time": execution_data["end_time"],
            "duration": execution_data["duration"],
            "status": execution_data["status"],
            "task_count": len(execution_data["tasks"])
        },
        "task_summary": {
            "total_tasks": len(execution_data["tasks"]),
            "successful_tasks": sum(1 for task in execution_data["tasks"].values() if task["status"] == "success"),
            "failed_tasks": sum(1 for task in execution_data["tasks"].values() if task["status"] == "failed"),
            "average_task_duration": sum(task["duration"] for task in execution_data["tasks"].values()) / len(execution_data["tasks"]),
            "longest_task": max(execution_data["tasks"].items(), key=lambda x: x[1]["duration"])[0],
            "shortest_task": min(execution_data["tasks"].items(), key=lambda x: x[1]["duration"])[0]
        },
        "task_details": {
            task_name: {
                "duration": task_data["duration"],
                "status": task_data["status"],
                "records_processed": task_data["outputs"]["records_processed"]
            } for task_name, task_data in execution_data["tasks"].items()
        }
    }
    
    # Zapisanie raportu
    report_file = OUTPUT_DIR / "execution_report_summary.json"
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"Zapisano raport z wykonania do: {report_file}")
    return str(report_file)


if __name__ == "__main__":
    # Zapisanie definicji DSL
    dsl_file = save_dsl_definition()
    
    # Symulacja wykonania przepływu
    execution_file = simulate_flow_execution()
    
    # Generowanie wizualizacji wykonania
    visualization_file = generate_execution_visualization(execution_file)
    
    # Generowanie raportu z wykonania
    report_file = generate_execution_report(execution_file)
    
    print("\nWygenerowane pliki:")
    print(f"- Definicja DSL: {dsl_file}")
    print(f"- Dane wykonania: {execution_file}")
    print(f"- Wizualizacja wykonania: {visualization_file}")
    print(f"- Raport z wykonania: {report_file}")
    
    # Otwieranie wizualizacji w przeglądarce
    open_viz = input("\nCzy chcesz otworzyć wizualizację w przeglądarce? (t/n): ").lower() == 't'
    
    if open_viz:
        import webbrowser
        webbrowser.open(f"file://{visualization_file}")
        
    print("\nZakończono wizualizację wykonania.")
