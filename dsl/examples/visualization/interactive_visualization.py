#!/usr/bin/env python3
"""
Przykład interaktywnej wizualizacji przepływów Taskinity.
"""
import os
import json
import webbrowser
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from threading import Thread
from dotenv import load_dotenv

# Import funkcji z Taskinity
from taskinity import task, flow, run_flow_from_dsl, save_dsl
from taskinity import generate_mermaid_from_dsl, visualize_flow

# Ładowanie zmiennych środowiskowych
load_dotenv()

# Konfiguracja ścieżek
BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output"
DSL_DIR = BASE_DIR / "dsl"

# Upewniamy się, że katalogi istnieją
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(DSL_DIR, exist_ok=True)

# Przykładowy przepływ do wizualizacji
INTERACTIVE_DEMO_DSL = """
flow InteractiveVisualizationDemo:
    description: "Przepływ demonstracyjny interaktywnej wizualizacji"
    
    task DataCollection:
        description: "Zbieranie danych z różnych źródeł"
        code: |
            import random
            
            print("Zbieranie danych z różnych źródeł...")
            
            # Symulacja zbierania danych z różnych źródeł
            sources = ["API", "Database", "File", "Sensor"]
            collected_data = {}
            
            for source in sources:
                # Symulacja danych z każdego źródła
                data_points = random.randint(10, 50)
                collected_data[source] = {
                    "count": data_points,
                    "status": "success",
                    "timestamp": "2023-01-01T12:00:00Z"
                }
                print(f"Zebrano {data_points} punktów danych z {source}")
            
            return {"collected_data": collected_data}
    
    task DataValidation:
        description: "Walidacja zebranych danych"
        code: |
            print("Walidacja zebranych danych...")
            
            collected_data = inputs["DataCollection"]["collected_data"]
            validation_results = {}
            
            for source, data in collected_data.items():
                # Symulacja walidacji danych
                is_valid = data["count"] >= 20
                validation_results[source] = {
                    "is_valid": is_valid,
                    "message": "OK" if is_valid else "Za mało punktów danych"
                }
                print(f"Walidacja {source}: {'Sukces' if is_valid else 'Błąd'}")
            
            return {"validation_results": validation_results}
    
    task DataTransformation:
        description: "Transformacja danych"
        code: |
            print("Transformacja danych...")
            
            collected_data = inputs["DataCollection"]["collected_data"]
            validation_results = inputs["DataValidation"]["validation_results"]
            
            transformed_data = {}
            
            for source, data in collected_data.items():
                if validation_results[source]["is_valid"]:
                    # Symulacja transformacji danych
                    transformed_data[source] = {
                        "original_count": data["count"],
                        "transformed_count": data["count"] * 2,
                        "transformation": "multiplication"
                    }
                    print(f"Transformowano dane z {source}")
                else:
                    print(f"Pominięto transformację danych z {source} (nieważne dane)")
            
            return {"transformed_data": transformed_data}
    
    task DataAnalysis:
        description: "Analiza danych"
        code: |
            print("Analiza danych...")
            
            transformed_data = inputs["DataTransformation"]["transformed_data"]
            
            analysis_results = {
                "total_original": sum(data["original_count"] for data in transformed_data.values()),
                "total_transformed": sum(data["transformed_count"] for data in transformed_data.values()),
                "average_original": sum(data["original_count"] for data in transformed_data.values()) / len(transformed_data) if transformed_data else 0,
                "average_transformed": sum(data["transformed_count"] for data in transformed_data.values()) / len(transformed_data) if transformed_data else 0,
                "sources_count": len(transformed_data)
            }
            
            print(f"Przeanalizowano dane z {analysis_results['sources_count']} źródeł")
            return {"analysis_results": analysis_results}
    
    task ReportGeneration:
        description: "Generowanie raportu"
        code: |
            import json
            from pathlib import Path
            
            print("Generowanie raportu...")
            
            # Zbieranie danych z poprzednich zadań
            collected_data = inputs["DataCollection"]["collected_data"]
            validation_results = inputs["DataValidation"]["validation_results"]
            transformed_data = inputs["DataTransformation"]["transformed_data"]
            analysis_results = inputs["DataAnalysis"]["analysis_results"]
            
            # Tworzenie raportu
            report = {
                "summary": {
                    "total_sources": len(collected_data),
                    "valid_sources": len(transformed_data),
                    "total_original_data_points": analysis_results["total_original"],
                    "total_transformed_data_points": analysis_results["total_transformed"]
                },
                "details": {
                    "collected_data": collected_data,
                    "validation_results": validation_results,
                    "transformed_data": transformed_data,
                    "analysis_results": analysis_results
                }
            }
            
            # Zapisanie raportu
            output_dir = Path("output")
            os.makedirs(output_dir, exist_ok=True)
            
            report_file = output_dir / "interactive_report.json"
            with open(report_file, "w") as f:
                json.dump(report, f, indent=2)
            
            print(f"Zapisano raport do: {report_file}")
            return {"report_file": str(report_file), "report": report}
    
    DataCollection -> DataValidation -> DataTransformation -> DataAnalysis -> ReportGeneration
"""

# Szablon HTML dla interaktywnej wizualizacji
INTERACTIVE_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Interaktywna Wizualizacja Taskinity</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10.0.0/dist/mermaid.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/d3@7"></script>
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
        h1, h2 {
            color: #333;
            border-bottom: 1px solid #eee;
            padding-bottom: 10px;
        }
        .mermaid {
            text-align: center;
            margin: 20px 0;
        }
        .task-details {
            display: none;
            padding: 15px;
            background-color: #f9f9f9;
            border: 1px solid #ddd;
            border-radius: 5px;
            margin-top: 10px;
        }
        .task-node {
            cursor: pointer;
            transition: fill 0.3s;
        }
        .task-node:hover {
            fill: #a7d8ff !important;
        }
        .controls {
            margin: 20px 0;
            padding: 10px;
            background-color: #eee;
            border-radius: 5px;
        }
        button {
            padding: 8px 12px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            margin-right: 10px;
        }
        button:hover {
            background-color: #45a049;
        }
        pre {
            background-color: #f5f5f5;
            padding: 10px;
            border-radius: 5px;
            overflow-x: auto;
        }
        .footer {
            margin-top: 20px;
            text-align: center;
            font-size: 0.8em;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Interaktywna Wizualizacja Przepływu Taskinity</h1>
        
        <div class="controls">
            <button id="runFlowBtn">Uruchom Przepływ</button>
            <button id="resetBtn">Resetuj</button>
            <button id="zoomInBtn">Powiększ</button>
            <button id="zoomOutBtn">Pomniejsz</button>
            <button id="downloadSvgBtn">Pobierz SVG</button>
        </div>
        
        <h2>Diagram Przepływu</h2>
        <div class="mermaid" id="flowDiagram">
            {{MERMAID_CODE}}
        </div>
        
        <div id="taskDetails" class="task-details">
            <h3 id="taskName">Nazwa zadania</h3>
            <p id="taskDescription">Opis zadania</p>
            <h4>Kod zadania:</h4>
            <pre id="taskCode">Kod zadania</pre>
        </div>
        
        <h2>Wyniki Wykonania</h2>
        <pre id="flowResults">Uruchom przepływ, aby zobaczyć wyniki...</pre>
        
        <div class="footer">
            Wygenerowano przez Taskinity Flow Visualizer
        </div>
    </div>
    
    <script>
        // Inicjalizacja Mermaid
        mermaid.initialize({ startOnLoad: true });
        
        // Dane przepływu
        const flowData = {{FLOW_DATA}};
        
        // Funkcja do wyświetlania szczegółów zadania
        function showTaskDetails(taskName) {
            const taskData = flowData.tasks[taskName];
            if (taskData) {
                document.getElementById('taskName').textContent = taskName;
                document.getElementById('taskDescription').textContent = taskData.description || 'Brak opisu';
                document.getElementById('taskCode').textContent = taskData.code || 'Brak kodu';
                document.getElementById('taskDetails').style.display = 'block';
            }
        }
        
        // Nasłuchiwanie na kliknięcia w węzły diagramu
        document.addEventListener('DOMContentLoaded', function() {
            setTimeout(() => {
                const taskNodes = document.querySelectorAll('.node');
                taskNodes.forEach(node => {
                    node.classList.add('task-node');
                    node.addEventListener('click', function() {
                        const taskName = this.id.replace('flowchart-', '');
                        showTaskDetails(taskName);
                    });
                });
            }, 1000); // Dajemy czas na renderowanie Mermaid
        });
        
        // Obsługa przycisków
        document.getElementById('runFlowBtn').addEventListener('click', function() {
            this.disabled = true;
            this.textContent = 'Uruchamianie...';
            
            // Symulacja uruchomienia przepływu
            setTimeout(() => {
                document.getElementById('flowResults').textContent = JSON.stringify(
                    {
                        "DataCollection": {
                            "collected_data": {
                                "API": {"count": 35, "status": "success"},
                                "Database": {"count": 42, "status": "success"},
                                "File": {"count": 18, "status": "success"},
                                "Sensor": {"count": 27, "status": "success"}
                            }
                        },
                        "DataValidation": {
                            "validation_results": {
                                "API": {"is_valid": true, "message": "OK"},
                                "Database": {"is_valid": true, "message": "OK"},
                                "File": {"is_valid": false, "message": "Za mało punktów danych"},
                                "Sensor": {"is_valid": true, "message": "OK"}
                            }
                        },
                        "DataTransformation": {
                            "transformed_data": {
                                "API": {"original_count": 35, "transformed_count": 70},
                                "Database": {"original_count": 42, "transformed_count": 84},
                                "Sensor": {"original_count": 27, "transformed_count": 54}
                            }
                        },
                        "DataAnalysis": {
                            "analysis_results": {
                                "total_original": 104,
                                "total_transformed": 208,
                                "average_original": 34.67,
                                "average_transformed": 69.33,
                                "sources_count": 3
                            }
                        },
                        "ReportGeneration": {
                            "report_file": "output/interactive_report.json"
                        }
                    }, null, 2);
                
                this.textContent = 'Uruchom Przepływ';
                this.disabled = false;
                
                // Kolorowanie węzłów na podstawie statusu
                const svgNodes = document.querySelectorAll('.node rect');
                svgNodes.forEach(node => {
                    const taskName = node.parentNode.id.replace('flowchart-', '');
                    if (taskName === 'DataCollection' || taskName === 'DataValidation' || 
                        taskName === 'DataTransformation' || taskName === 'DataAnalysis' || 
                        taskName === 'ReportGeneration') {
                        node.style.fill = '#9f9';
                    }
                });
            }, 2000);
        });
        
        document.getElementById('resetBtn').addEventListener('click', function() {
            document.getElementById('flowResults').textContent = 'Uruchom przepływ, aby zobaczyć wyniki...';
            document.getElementById('taskDetails').style.display = 'none';
            
            // Resetowanie kolorów węzłów
            const svgNodes = document.querySelectorAll('.node rect');
            svgNodes.forEach(node => {
                node.style.fill = '';
            });
        });
        
        // Funkcje powiększania/pomniejszania
        let zoomLevel = 1;
        
        document.getElementById('zoomInBtn').addEventListener('click', function() {
            zoomLevel *= 1.2;
            document.querySelector('.mermaid svg').style.transform = `scale(${zoomLevel})`;
        });
        
        document.getElementById('zoomOutBtn').addEventListener('click', function() {
            zoomLevel /= 1.2;
            document.querySelector('.mermaid svg').style.transform = `scale(${zoomLevel})`;
        });
        
        // Funkcja pobierania SVG
        document.getElementById('downloadSvgBtn').addEventListener('click', function() {
            const svg = document.querySelector('.mermaid svg');
            const serializer = new XMLSerializer();
            let source = serializer.serializeToString(svg);
            
            // Dodanie deklaracji XML i przestrzeni nazw
            source = '<?xml version="1.0" standalone="no"?>\r\n' + source;
            
            // Konwersja do URL danych
            const svgBlob = new Blob([source], {type: 'image/svg+xml;charset=utf-8'});
            const svgUrl = URL.createObjectURL(svgBlob);
            
            // Tworzenie linku do pobrania
            const downloadLink = document.createElement('a');
            downloadLink.href = svgUrl;
            downloadLink.download = 'taskinity_flow.svg';
            document.body.appendChild(downloadLink);
            downloadLink.click();
            document.body.removeChild(downloadLink);
        });
    </script>
</body>
</html>
"""

# Zapisanie definicji DSL
def save_dsl_definition():
    """Zapisuje definicję DSL do pliku."""
    dsl_file = DSL_DIR / "interactive_visualization.taskinity"
    with open(dsl_file, "w") as f:
        f.write(INTERACTIVE_DEMO_DSL)
    print(f"Zapisano definicję DSL do: {dsl_file}")
    return str(dsl_file)


# Generowanie interaktywnej wizualizacji
def generate_interactive_visualization():
    """Generuje interaktywną wizualizację przepływu."""
    print("Generowanie interaktywnej wizualizacji...")
    
    # Generowanie kodu Mermaid
    mermaid_code = generate_mermaid_from_dsl(INTERACTIVE_DEMO_DSL)
    
    # Parsowanie DSL do danych JSON
    flow_data = {
        "name": "InteractiveVisualizationDemo",
        "description": "Przepływ demonstracyjny interaktywnej wizualizacji",
        "tasks": {
            "DataCollection": {
                "description": "Zbieranie danych z różnych źródeł",
                "code": """import random

print("Zbieranie danych z różnych źródeł...")

# Symulacja zbierania danych z różnych źródeł
sources = ["API", "Database", "File", "Sensor"]
collected_data = {}

for source in sources:
    # Symulacja danych z każdego źródła
    data_points = random.randint(10, 50)
    collected_data[source] = {
        "count": data_points,
        "status": "success",
        "timestamp": "2023-01-01T12:00:00Z"
    }
    print(f"Zebrano {data_points} punktów danych z {source}")

return {"collected_data": collected_data}"""
            },
            "DataValidation": {
                "description": "Walidacja zebranych danych",
                "code": """print("Walidacja zebranych danych...")

collected_data = inputs["DataCollection"]["collected_data"]
validation_results = {}

for source, data in collected_data.items():
    # Symulacja walidacji danych
    is_valid = data["count"] >= 20
    validation_results[source] = {
        "is_valid": is_valid,
        "message": "OK" if is_valid else "Za mało punktów danych"
    }
    print(f"Walidacja {source}: {'Sukces' if is_valid else 'Błąd'}")

return {"validation_results": validation_results}"""
            },
            "DataTransformation": {
                "description": "Transformacja danych",
                "code": """print("Transformacja danych...")

collected_data = inputs["DataCollection"]["collected_data"]
validation_results = inputs["DataValidation"]["validation_results"]

transformed_data = {}

for source, data in collected_data.items():
    if validation_results[source]["is_valid"]:
        # Symulacja transformacji danych
        transformed_data[source] = {
            "original_count": data["count"],
            "transformed_count": data["count"] * 2,
            "transformation": "multiplication"
        }
        print(f"Transformowano dane z {source}")
    else:
        print(f"Pominięto transformację danych z {source} (nieważne dane)")

return {"transformed_data": transformed_data}"""
            },
            "DataAnalysis": {
                "description": "Analiza danych",
                "code": """print("Analiza danych...")

transformed_data = inputs["DataTransformation"]["transformed_data"]

analysis_results = {
    "total_original": sum(data["original_count"] for data in transformed_data.values()),
    "total_transformed": sum(data["transformed_count"] for data in transformed_data.values()),
    "average_original": sum(data["original_count"] for data in transformed_data.values()) / len(transformed_data) if transformed_data else 0,
    "average_transformed": sum(data["transformed_count"] for data in transformed_data.values()) / len(transformed_data) if transformed_data else 0,
    "sources_count": len(transformed_data)
}

print(f"Przeanalizowano dane z {analysis_results['sources_count']} źródeł")
return {"analysis_results": analysis_results}"""
            },
            "ReportGeneration": {
                "description": "Generowanie raportu",
                "code": """import json
from pathlib import Path

print("Generowanie raportu...")

# Zbieranie danych z poprzednich zadań
collected_data = inputs["DataCollection"]["collected_data"]
validation_results = inputs["DataValidation"]["validation_results"]
transformed_data = inputs["DataTransformation"]["transformed_data"]
analysis_results = inputs["DataAnalysis"]["analysis_results"]

# Tworzenie raportu
report = {
    "summary": {
        "total_sources": len(collected_data),
        "valid_sources": len(transformed_data),
        "total_original_data_points": analysis_results["total_original"],
        "total_transformed_data_points": analysis_results["total_transformed"]
    },
    "details": {
        "collected_data": collected_data,
        "validation_results": validation_results,
        "transformed_data": transformed_data,
        "analysis_results": analysis_results
    }
}

# Zapisanie raportu
output_dir = Path("output")
os.makedirs(output_dir, exist_ok=True)

report_file = output_dir / "interactive_report.json"
with open(report_file, "w") as f:
    json.dump(report, f, indent=2)

print(f"Zapisano raport do: {report_file}")
return {"report_file": str(report_file), "report": report}"""
            }
        },
        "connections": [
            ["DataCollection", "DataValidation"],
            ["DataValidation", "DataTransformation"],
            ["DataTransformation", "DataAnalysis"],
            ["DataAnalysis", "ReportGeneration"]
        ]
    }
    
    # Tworzenie HTML z szablonu
    html_content = INTERACTIVE_HTML_TEMPLATE.replace(
        "{{MERMAID_CODE}}", mermaid_code
    ).replace(
        "{{FLOW_DATA}}", json.dumps(flow_data)
    )
    
    # Zapisanie HTML
    html_file = OUTPUT_DIR / "interactive_visualization.html"
    with open(html_file, "w") as f:
        f.write(html_content)
    
    print(f"Zapisano interaktywną wizualizację do: {html_file}")
    return str(html_file)


# Uruchomienie serwera HTTP
def run_http_server():
    """Uruchamia lokalny serwer HTTP."""
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    print(f"Uruchamianie serwera HTTP na http://localhost:8000")
    httpd.serve_forever()


if __name__ == "__main__":
    # Zapisanie definicji DSL
    dsl_file = save_dsl_definition()
    
    # Generowanie interaktywnej wizualizacji
    html_file = generate_interactive_visualization()
    
    # Uruchomienie serwera HTTP w osobnym wątku
    server_thread = Thread(target=run_http_server)
    server_thread.daemon = True
    server_thread.start()
    
    # Otwarcie przeglądarki
    html_path = Path(html_file)
    url = f"http://localhost:8000/{OUTPUT_DIR.name}/{html_path.name}"
    print(f"Otwieranie wizualizacji w przeglądarce: {url}")
    webbrowser.open(url)
    
    print("\nNaciśnij Ctrl+C, aby zakończyć...")
    try:
        # Czekanie na zakończenie przez użytkownika
        while True:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nZakończono wizualizację.")
