#!/usr/bin/env python3
"""
Prosty dashboard webowy do monitorowania przepływów Prefect i logów.
"""
import os
import re
import json
import time
import glob
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional

import uvicorn
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from dotenv import load_dotenv
import httpx

# Ładowanie zmiennych środowiskowych
load_dotenv()

# Konfiguracja
PREFECT_API_URL = os.getenv("PREFECT_API_URL", "http://localhost:4201/api")
DASHBOARD_PORT = int(os.getenv("DASHBOARD_PORT", 8090))
LOG_DIR = os.getenv("LOG_DIR", "./logs")

# Inicjalizacja aplikacji FastAPI
app = FastAPI(
    title="HubMail Flow Dashboard",
    description="Prosty dashboard do monitorowania przepływów i logów",
    version="1.0.0"
)

# Tworzenie katalogów dla statycznych plików i szablonów
os.makedirs("static", exist_ok=True)
os.makedirs("templates", exist_ok=True)

# Konfiguracja statycznych plików i szablonów
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Modele danych
class LogEntry(BaseModel):
    timestamp: str
    level: str
    message: str

class FlowRun(BaseModel):
    id: str
    name: str
    status: str
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    duration: Optional[float] = None

# Menedżer połączeń WebSocket
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

# Funkcje pomocnicze
def parse_log_file(log_file, max_entries=100):
    """Parsowanie pliku logów"""
    entries = []
    
    try:
        with open(log_file, 'r') as f:
            for line in f:
                # Prosty parser logów
                match = re.match(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \| (\w+) \| (.+)', line)
                if match:
                    timestamp, level, message = match.groups()
                    entries.append({
                        "timestamp": timestamp,
                        "level": level,
                        "message": message
                    })
                else:
                    # Próba parsowania logów Docker
                    docker_match = re.match(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z) (\w+) (.+)', line)
                    if docker_match:
                        timestamp, level, message = docker_match.groups()
                        # Konwersja czasu UTC na lokalny
                        try:
                            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                            timestamp = dt.strftime('%Y-%m-%d %H:%M:%S')
                        except:
                            pass
                        
                        entries.append({
                            "timestamp": timestamp,
                            "level": level.upper(),
                            "message": message
                        })
                    else:
                        # Dodanie nieparsowanej linii jako wpisu INFO
                        entries.append({
                            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            "level": "INFO",
                            "message": line.strip()
                        })
    except Exception as e:
        print(f"Błąd podczas parsowania logów: {str(e)}")
    
    # Zwracamy tylko ostatnie wpisy
    return entries[-max_entries:] if entries else []

async def get_flow_runs():
    """Pobieranie przepływów z Prefect API"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{PREFECT_API_URL}/flow_runs?limit=20")
            if response.status_code == 200:
                data = response.json()
                flow_runs = []
                
                for run in data.get("flow_runs", []):
                    # Obliczanie czasu trwania
                    duration = None
                    if run.get("start_time") and run.get("end_time"):
                        start = datetime.fromisoformat(run["start_time"].replace("Z", "+00:00"))
                        end = datetime.fromisoformat(run["end_time"].replace("Z", "+00:00"))
                        duration = (end - start).total_seconds()
                    
                    flow_runs.append({
                        "id": run.get("id"),
                        "name": run.get("name"),
                        "status": run.get("state", {}).get("name", "Unknown"),
                        "start_time": run.get("start_time"),
                        "end_time": run.get("end_time"),
                        "duration": duration
                    })
                
                return flow_runs
            else:
                print(f"Błąd podczas pobierania przepływów: {response.status_code}")
                return []
    except Exception as e:
        print(f"Błąd podczas pobierania przepływów: {str(e)}")
        return []

def get_latest_log_file():
    """Pobieranie najnowszego pliku logów"""
    log_files = glob.glob(f"{LOG_DIR}/email_flow_*.log")
    if not log_files:
        return None
    return max(log_files, key=os.path.getctime)

def get_docker_logs(container_name=None, lines=100):
    """Pobieranie logów z kontenerów Docker"""
    import subprocess
    
    try:
        if container_name:
            # Pobieranie logów z konkretnego kontenera
            cmd = ["docker", "logs", "--tail", str(lines), container_name]
        else:
            # Pobieranie logów ze wszystkich kontenerów
            cmd = ["docker", "compose", "logs", "--tail", str(lines)]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.splitlines()
        else:
            print(f"Błąd podczas pobierania logów Docker: {result.stderr}")
            return []
    except Exception as e:
        print(f"Błąd podczas pobierania logów Docker: {str(e)}")
        return []

# Endpointy API
@app.get("/", response_class=HTMLResponse)
async def get_dashboard(request: Request):
    """Strona główna dashboardu"""
    try:
        flow_runs = await get_flow_runs()
        
        # Pobieranie logów z plików
        log_file = get_latest_log_file()
        file_logs = parse_log_file(log_file) if log_file else []
        
        # Pobieranie logów z Docker
        docker_logs = []
        docker_lines = get_docker_logs(lines=50)
        for line in docker_lines:
            # Dodanie nieparsowanej linii jako wpisu INFO
            docker_logs.append({
                "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "level": "INFO",
                "message": line.strip()
            })
        
        # Pobieranie listy kontenerów
        import subprocess
        containers = []
        try:
            result = subprocess.run(["docker", "ps", "--format", "{{.Names}}"], capture_output=True, text=True)
            if result.returncode == 0:
                containers = [name.strip() for name in result.stdout.splitlines() if name.strip()]
        except Exception as e:
            print(f"Błąd podczas pobierania listy kontenerów: {str(e)}")
        
        return templates.TemplateResponse(
            "dashboard.html", 
            {
                "request": request, 
                "title": "HubMail Flow Dashboard",
                "flow_runs": flow_runs,
                "file_logs": file_logs,
                "docker_logs": docker_logs,
                "containers": containers
            }
        )
    except Exception as e:
        import traceback
        return HTMLResponse(
            content=f"<html><body><h1>Błąd serwera</h1><p>{str(e)}</p><pre>{traceback.format_exc()}</pre></body></html>",
            status_code=500
        )

@app.get("/api/flows", response_model=List[FlowRun])
async def get_flows():
    """Endpoint API do pobierania przepływów"""
    return await get_flow_runs()

@app.get("/api/logs", response_model=List[LogEntry])
async def get_logs(limit: int = 100, source: str = "file", container: str = None):
    """Endpoint API do pobierania logów"""
    if source == "docker":
        # Pobieranie logów z Docker
        docker_logs = get_docker_logs(container, limit)
        # Parsowanie logów
        entries = []
        for line in docker_logs:
            # Dodanie nieparsowanej linii jako wpisu INFO
            entries.append({
                "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "level": "INFO",
                "message": line.strip()
            })
        return entries[-limit:] if entries else []
    else:
        # Pobieranie logów z pliku
        log_file = get_latest_log_file()
        if not log_file:
            return []
        return parse_log_file(log_file, limit)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Endpoint WebSocket do przesyłania aktualizacji w czasie rzeczywistym"""
    await manager.connect(websocket)
    try:
        while True:
            # Pobieranie danych
            flow_runs = await get_flow_runs()
            
            # Pobieranie logów z plików
            log_file = get_latest_log_file()
            file_logs = parse_log_file(log_file, 20) if log_file else []
            
            # Pobieranie logów z Docker
            docker_logs = []
            docker_lines = get_docker_logs(lines=20)
            for line in docker_lines:
                # Dodanie nieparsowanej linii jako wpisu INFO
                docker_logs.append({
                    "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "level": "INFO",
                    "message": line.strip()
                })
            
            # Przygotowanie danych do wysłania
            data = {
                "flow_runs": flow_runs,
                "file_logs": file_logs,
                "docker_logs": docker_logs,
                "timestamp": datetime.now().isoformat()
            }
            
            # Wysyłanie danych
            await websocket.send_json(data)
            
            # Oczekiwanie przed kolejnym odświeżeniem
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Funkcja do generowania szablonu HTML
def generate_template():
    """Generowanie szablonu HTML dla dashboardu"""
    
    dashboard_html = """
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            padding-top: 20px;
            background-color: #f5f5f5;
        }
        .card {
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .card-header {
            font-weight: bold;
        }
        .status-badge {
            font-size: 0.9rem;
        }
        .log-container {
            height: 400px;
            overflow-y: auto;
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 0.25rem;
            padding: 10px;
            font-family: monospace;
        }
        .log-entry {
            margin-bottom: 5px;
            padding: 5px;
            border-radius: 3px;
        }
        .log-INFO {
            background-color: #d1ecf1;
        }
        .log-WARNING {
            background-color: #fff3cd;
        }
        .log-ERROR {
            background-color: #f8d7da;
        }
        .flow-table {
            font-size: 0.9rem;
        }
        .flow-COMPLETED {
            background-color: #d4edda;
        }
        .flow-RUNNING {
            background-color: #cce5ff;
        }
        .flow-FAILED {
            background-color: #f8d7da;
        }
        .flow-PENDING {
            background-color: #e2e3e5;
        }
        .nav-tabs .nav-link {
            cursor: pointer;
        }
        .container-selector {
            margin-bottom: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="mb-4">HubMail Flow Dashboard</h1>
        
        <!-- Przepływy -->
        <div class="card">
            <div class="card-header d-flex justify-content-between align-items-center">
                Przepływy Prefect
                <button id="refresh-flows" class="btn btn-sm btn-primary">Odśwież</button>
            </div>
            <div class="card-body">
                <div class="table-responsive">
                    <table class="table table-striped table-hover flow-table">
                        <thead>
                            <tr>
                                <th>Nazwa</th>
                                <th>Status</th>
                                <th>Czas rozpoczęcia</th>
                                <th>Czas zakończenia</th>
                                <th>Czas trwania</th>
                            </tr>
                        </thead>
                        <tbody id="flow-table-body">
                            {% for flow in flow_runs %}
                            <tr class="flow-{{ flow.status }}">
                                <td>{{ flow.name }}</td>
                                <td>
                                    {% if flow.status == "COMPLETED" %}
                                    <span class="badge bg-success status-badge">{{ flow.status }}</span>
                                    {% elif flow.status == "RUNNING" %}
                                    <span class="badge bg-primary status-badge">{{ flow.status }}</span>
                                    {% elif flow.status == "FAILED" %}
                                    <span class="badge bg-danger status-badge">{{ flow.status }}</span>
                                    {% else %}
                                    <span class="badge bg-secondary status-badge">{{ flow.status }}</span>
                                    {% endif %}
                                </td>
                                <td>{{ flow.start_time }}</td>
                                <td>{{ flow.end_time }}</td>
                                <td>{{ flow.duration }} s</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        
        <!-- Logi -->
        <div class="card">
            <div class="card-header d-flex justify-content-between align-items-center">
                Logi
                <button id="refresh-logs" class="btn btn-sm btn-primary">Odśwież</button>
            </div>
            <div class="card-body">
                <!-- Zakładki źródeł logów -->
                <ul class="nav nav-tabs" id="logTabs" role="tablist">
                    <li class="nav-item" role="presentation">
                        <a class="nav-link active" id="file-logs-tab" data-bs-toggle="tab" data-bs-target="#file-logs" type="button" role="tab" aria-controls="file-logs" aria-selected="true">Logi plików</a>
                    </li>
                    <li class="nav-item" role="presentation">
                        <a class="nav-link" id="docker-logs-tab" data-bs-toggle="tab" data-bs-target="#docker-logs" type="button" role="tab" aria-controls="docker-logs" aria-selected="false">Logi Docker</a>
                    </li>
                </ul>
                
                <!-- Zawartość zakładek -->
                <div class="tab-content" id="logTabsContent">
                    <!-- Logi plików -->
                    <div class="tab-pane fade show active" id="file-logs" role="tabpanel" aria-labelledby="file-logs-tab">
                        <div id="file-log-container" class="log-container mt-3">
                            {% for log in file_logs %}
                            <div class="log-entry log-{{ log.level }}">
                                <strong>{{ log.timestamp }}</strong> [{{ log.level }}] {{ log.message }}
                            </div>
                            {% endfor %}
                        </div>
                    </div>
                    
                    <!-- Logi Docker -->
                    <div class="tab-pane fade" id="docker-logs" role="tabpanel" aria-labelledby="docker-logs-tab">
                        <!-- Selektor kontenerów -->
                        <div class="container-selector mt-3">
                            <select id="container-selector" class="form-select">
                                <option value="all">Wszystkie kontenery</option>
                                {% for container in containers %}
                                <option value="{{ container }}">{{ container }}</option>
                                {% endfor %}
                            </select>
                        </div>
                        
                        <div id="docker-log-container" class="log-container">
                            {% for log in docker_logs %}
                            <div class="log-entry log-{{ log.level }}">
                                <strong>{{ log.timestamp }}</strong> [{{ log.level }}] {{ log.message }}
                            </div>
                            {% endfor %}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
    
    <script>
        // Funkcja do formatowania daty
        function formatDate(dateString) {
            if (!dateString) return '';
            const date = new Date(dateString);
            return date.toLocaleString();
        }
        
        // Funkcja do aktualizacji tabeli przepływów
        function updateFlowTable(flows) {
            const tableBody = document.getElementById('flow-table-body');
            tableBody.innerHTML = '';
            
            flows.forEach(flow => {
                const row = document.createElement('tr');
                row.className = `flow-${flow.status}`;
                
                // Nazwa
                const nameCell = document.createElement('td');
                nameCell.textContent = flow.name;
                row.appendChild(nameCell);
                
                // Status
                const statusCell = document.createElement('td');
                const statusBadge = document.createElement('span');
                statusBadge.className = 'badge status-badge';
                
                if (flow.status === 'COMPLETED') {
                    statusBadge.className += ' bg-success';
                } else if (flow.status === 'RUNNING') {
                    statusBadge.className += ' bg-primary';
                } else if (flow.status === 'FAILED') {
                    statusBadge.className += ' bg-danger';
                } else {
                    statusBadge.className += ' bg-secondary';
                }
                
                statusBadge.textContent = flow.status;
                statusCell.appendChild(statusBadge);
                row.appendChild(statusCell);
                
                // Czas rozpoczęcia
                const startTimeCell = document.createElement('td');
                startTimeCell.textContent = formatDate(flow.start_time);
                row.appendChild(startTimeCell);
                
                // Czas zakończenia
                const endTimeCell = document.createElement('td');
                endTimeCell.textContent = formatDate(flow.end_time);
                row.appendChild(endTimeCell);
                
                // Czas trwania
                const durationCell = document.createElement('td');
                durationCell.textContent = flow.duration ? `${flow.duration} s` : '';
                row.appendChild(durationCell);
                
                tableBody.appendChild(row);
            });
        }
        
        // Funkcja do aktualizacji logów plików
        function updateFileLogs(logs) {
            const logContainer = document.getElementById('file-log-container');
            logContainer.innerHTML = '';
            
            logs.forEach(log => {
                const logEntry = document.createElement('div');
                logEntry.className = `log-entry log-${log.level}`;
                logEntry.innerHTML = `<strong>${log.timestamp}</strong> [${log.level}] ${log.message}`;
                logContainer.appendChild(logEntry);
            });
            
            // Przewijanie do najnowszych logów
            logContainer.scrollTop = logContainer.scrollHeight;
        }
        
        // Funkcja do aktualizacji logów Docker
        function updateDockerLogs(logs) {
            const logContainer = document.getElementById('docker-log-container');
            logContainer.innerHTML = '';
            
            logs.forEach(log => {
                const logEntry = document.createElement('div');
                logEntry.className = `log-entry log-${log.level}`;
                logEntry.innerHTML = `<strong>${log.timestamp}</strong> [${log.level}] ${log.message}`;
                logContainer.appendChild(logEntry);
            });
            
            // Przewijanie do najnowszych logów
            logContainer.scrollTop = logContainer.scrollHeight;
        }
        
        // Funkcja do pobierania przepływów
        function fetchFlows() {
            fetch('/api/flows')
                .then(response => response.json())
                .then(flows => {
                    updateFlowTable(flows);
                })
                .catch(error => console.error('Błąd podczas pobierania przepływów:', error));
        }
        
        // Funkcja do pobierania logów plików
        function fetchFileLogs() {
            fetch('/api/logs?source=file')
                .then(response => response.json())
                .then(logs => {
                    updateFileLogs(logs);
                })
                .catch(error => console.error('Błąd podczas pobierania logów plików:', error));
        }
        
        // Funkcja do pobierania logów Docker
        function fetchDockerLogs() {
            const containerSelector = document.getElementById('container-selector');
            const container = containerSelector.value;
            
            let url = '/api/logs?source=docker';
            if (container !== 'all') {
                url += `&container=${container}`;
            }
            
            fetch(url)
                .then(response => response.json())
                .then(logs => {
                    updateDockerLogs(logs);
                })
                .catch(error => console.error('Błąd podczas pobierania logów Docker:', error));
        }
        
        // Inicjalizacja WebSocket
        const ws = new WebSocket(`ws://${window.location.host}/ws`);
        
        ws.onmessage = function(event) {
            const data = JSON.parse(event.data);
            
            // Aktualizacja przepływów
            updateFlowTable(data.flow_runs);
            
            // Aktualizacja logów
            if (data.file_logs) {
                updateFileLogs(data.file_logs);
            }
            
            if (data.docker_logs) {
                updateDockerLogs(data.docker_logs);
            }
        };
        
        // Obsługa przycisków odświeżania
        document.getElementById('refresh-flows').addEventListener('click', fetchFlows);
        document.getElementById('refresh-logs').addEventListener('click', function() {
            // Sprawdzenie aktywnej zakładki
            const activeTab = document.querySelector('#logTabs .nav-link.active');
            if (activeTab.id === 'file-logs-tab') {
                fetchFileLogs();
            } else if (activeTab.id === 'docker-logs-tab') {
                fetchDockerLogs();
            }
        });
        
        // Obsługa zmiany kontenera
        document.getElementById('container-selector').addEventListener('change', fetchDockerLogs);
        
        // Obsługa zmiany zakładki
        document.querySelectorAll('#logTabs .nav-link').forEach(tab => {
            tab.addEventListener('click', function() {
                // Ustawienie aktywnej zakładki
                document.querySelectorAll('#logTabs .nav-link').forEach(t => t.classList.remove('active'));
                this.classList.add('active');
                
                // Ukrycie wszystkich zakładek
                document.querySelectorAll('#logTabsContent .tab-pane').forEach(pane => {
                    pane.classList.remove('show', 'active');
                });
                
                // Pokazanie wybranej zakładki
                const target = this.getAttribute('data-bs-target');
                document.querySelector(target).classList.add('show', 'active');
                
                // Odświeżenie logów
                if (this.id === 'file-logs-tab') {
                    fetchFileLogs();
                } else if (this.id === 'docker-logs-tab') {
                    fetchDockerLogs();
                }
            });
        });
        
        // Inicjalne pobranie danych
        fetchFlows();
        fetchFileLogs();
        fetchDockerLogs();
    </script>
</body>
</html>
    """
    
    # Zapisywanie szablonu
    os.makedirs("templates", exist_ok=True)
    with open("templates/dashboard.html", "w") as f:
        f.write(dashboard_html)
    
    print("Wygenerowano szablon HTML")

# Uruchomienie aplikacji
def main():
    """Główna funkcja uruchamiająca dashboard"""
    import sys
    import argparse
    
    # Parsowanie argumentów
    parser = argparse.ArgumentParser(description="Dashboard webowy do monitorowania przepływów i logów")
    parser.add_argument("--port", type=int, default=DASHBOARD_PORT, help="Port, na którym uruchomić dashboard")
    args = parser.parse_args()
    
    # Generowanie szablonu
    generate_template()
    
    # Tworzenie katalogu na logi, jeśli nie istnieje
    os.makedirs(LOG_DIR, exist_ok=True)
    
    # Uruchomienie serwera
    port = args.port
    print(f"Uruchamianie dashboardu na porcie {port}...")
    uvicorn.run("dashboard:app", host="0.0.0.0", port=port, reload=False)

if __name__ == "__main__":
    main()
