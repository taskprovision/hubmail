#!/usr/bin/env python3
"""
Prosty dashboard do monitorowania przepływów e-mail.
Zapewnia interfejs webowy do śledzenia statusu, logów i statystyk.
"""
import os
import re
import json
import time
import yaml
import glob
import uvicorn
import asyncio
from datetime import datetime, timedelta
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

# Ładowanie konfiguracji
def load_config():
    try:
        with open('config.yaml', 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Błąd podczas ładowania konfiguracji: {str(e)}")
        return {}

config = load_config()

# Inicjalizacja aplikacji FastAPI
app = FastAPI(
    title="HubMail Dashboard",
    description="Dashboard do monitorowania przepływów e-mail",
    version="1.0.0"
)

# Tworzenie katalogów dla statycznych plików i szablonów
os.makedirs("static", exist_ok=True)
os.makedirs("templates", exist_ok=True)

# Konfiguracja statycznych plików i szablonów
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Klasy dla API
class LogEntry(BaseModel):
    timestamp: str
    level: str
    message: str

class FlowStats(BaseModel):
    total_emails: int
    urgent_emails: int
    report_emails: int
    regular_emails: int
    attachments: int
    errors: int

class FlowStatus(BaseModel):
    status: str
    last_check: str
    next_check: str
    stats: FlowStats

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
                # Prosty parser logów - dostosuj do formatu Twoich logów
                match = re.match(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \| (\w+) \| (.+)', line)
                if match:
                    timestamp, level, message = match.groups()
                    entries.append({
                        "timestamp": timestamp,
                        "level": level,
                        "message": message
                    })
    except Exception as e:
        print(f"Błąd podczas parsowania logów: {str(e)}")
    
    # Zwracamy tylko ostatnie wpisy
    return entries[-max_entries:] if entries else []

def get_flow_stats():
    """Pobieranie statystyk przepływów"""
    # W rzeczywistej implementacji te dane byłyby pobierane z bazy danych lub logów
    # Tutaj używamy przykładowych danych
    return {
        "total_emails": 120,
        "urgent_emails": 15,
        "report_emails": 25,
        "regular_emails": 80,
        "attachments": 45,
        "errors": 3
    }

def get_flow_status():
    """Pobieranie statusu przepływów"""
    # W rzeczywistej implementacji te dane byłyby pobierane z systemu
    # Tutaj używamy przykładowych danych
    now = datetime.now()
    check_interval = config['email']['imap']['check_interval']
    
    return {
        "status": "running",
        "last_check": (now - timedelta(seconds=30)).strftime("%Y-%m-%d %H:%M:%S"),
        "next_check": (now + timedelta(seconds=check_interval - 30)).strftime("%Y-%m-%d %H:%M:%S"),
        "stats": get_flow_stats()
    }

def get_latest_log_file():
    """Pobieranie najnowszego pliku logów"""
    log_files = glob.glob("logs/email_flow_*.log")
    if not log_files:
        return None
    return max(log_files, key=os.path.getctime)

# Endpointy API
@app.get("/", response_class=HTMLResponse)
async def get_dashboard(request: Request):
    """Strona główna dashboardu"""
    return templates.TemplateResponse(
        "dashboard.html", 
        {
            "request": request, 
            "title": "HubMail Dashboard",
            "status": get_flow_status()
        }
    )

@app.get("/api/logs", response_model=List[LogEntry])
async def get_logs(limit: int = 100):
    """Endpoint API do pobierania logów"""
    log_file = get_latest_log_file()
    if not log_file:
        return []
    return parse_log_file(log_file, limit)

@app.get("/api/status", response_model=FlowStatus)
async def get_status():
    """Endpoint API do pobierania statusu"""
    return get_flow_status()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Endpoint WebSocket do przesyłania aktualizacji w czasie rzeczywistym"""
    await manager.connect(websocket)
    try:
        while True:
            # Wysyłanie aktualizacji statusu co 5 sekund
            await websocket.send_json(get_flow_status())
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Funkcja do generowania przykładowych szablonów HTML
def generate_templates():
    """Generowanie szablonów HTML dla dashboardu"""
    
    # Tworzenie szablonu dashboard.html
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
            font-size: 1rem;
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
        .stats-value {
            font-size: 1.5rem;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="mb-4">HubMail Dashboard</h1>
        
        <!-- Status -->
        <div class="card">
            <div class="card-header d-flex justify-content-between align-items-center">
                Status systemu
                <span id="status-badge" class="badge bg-success status-badge">Aktywny</span>
            </div>
            <div class="card-body">
                <div class="row">
                    <div class="col-md-4">
                        <p><strong>Ostatnie sprawdzenie:</strong> <span id="last-check">{{ status.last_check }}</span></p>
                    </div>
                    <div class="col-md-4">
                        <p><strong>Następne sprawdzenie:</strong> <span id="next-check">{{ status.next_check }}</span></p>
                    </div>
                    <div class="col-md-4">
                        <p><strong>Interwał sprawdzania:</strong> {{ config.email.imap.check_interval }} sekund</p>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Statystyki -->
        <div class="card">
            <div class="card-header">Statystyki</div>
            <div class="card-body">
                <div class="row">
                    <div class="col-md-2">
                        <div class="text-center">
                            <div id="total-emails" class="stats-value">{{ status.stats.total_emails }}</div>
                            <div>Wszystkie e-maile</div>
                        </div>
                    </div>
                    <div class="col-md-2">
                        <div class="text-center">
                            <div id="urgent-emails" class="stats-value text-danger">{{ status.stats.urgent_emails }}</div>
                            <div>Pilne</div>
                        </div>
                    </div>
                    <div class="col-md-2">
                        <div class="text-center">
                            <div id="report-emails" class="stats-value text-primary">{{ status.stats.report_emails }}</div>
                            <div>Raporty</div>
                        </div>
                    </div>
                    <div class="col-md-2">
                        <div class="text-center">
                            <div id="regular-emails" class="stats-value text-secondary">{{ status.stats.regular_emails }}</div>
                            <div>Zwykłe</div>
                        </div>
                    </div>
                    <div class="col-md-2">
                        <div class="text-center">
                            <div id="attachments" class="stats-value text-info">{{ status.stats.attachments }}</div>
                            <div>Załączniki</div>
                        </div>
                    </div>
                    <div class="col-md-2">
                        <div class="text-center">
                            <div id="errors" class="stats-value text-warning">{{ status.stats.errors }}</div>
                            <div>Błędy</div>
                        </div>
                    </div>
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
                <div id="log-container" class="log-container">
                    <!-- Tutaj będą wyświetlane logi -->
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Funkcja do aktualizacji logów
        function updateLogs() {
            fetch('/api/logs')
                .then(response => response.json())
                .then(logs => {
                    const logContainer = document.getElementById('log-container');
                    logContainer.innerHTML = '';
                    
                    logs.forEach(log => {
                        const logEntry = document.createElement('div');
                        logEntry.className = `log-entry log-${log.level}`;
                        logEntry.innerHTML = `<strong>${log.timestamp}</strong> [${log.level}] ${log.message}`;
                        logContainer.appendChild(logEntry);
                    });
                    
                    // Przewijanie do najnowszych logów
                    logContainer.scrollTop = logContainer.scrollHeight;
                })
                .catch(error => console.error('Błąd podczas pobierania logów:', error));
        }
        
        // Funkcja do aktualizacji statusu
        function updateStatus() {
            fetch('/api/status')
                .then(response => response.json())
                .then(status => {
                    // Aktualizacja statusu
                    const statusBadge = document.getElementById('status-badge');
                    if (status.status === 'running') {
                        statusBadge.className = 'badge bg-success status-badge';
                        statusBadge.textContent = 'Aktywny';
                    } else {
                        statusBadge.className = 'badge bg-danger status-badge';
                        statusBadge.textContent = 'Nieaktywny';
                    }
                    
                    // Aktualizacja czasów
                    document.getElementById('last-check').textContent = status.last_check;
                    document.getElementById('next-check').textContent = status.next_check;
                    
                    // Aktualizacja statystyk
                    document.getElementById('total-emails').textContent = status.stats.total_emails;
                    document.getElementById('urgent-emails').textContent = status.stats.urgent_emails;
                    document.getElementById('report-emails').textContent = status.stats.report_emails;
                    document.getElementById('regular-emails').textContent = status.stats.regular_emails;
                    document.getElementById('attachments').textContent = status.stats.attachments;
                    document.getElementById('errors').textContent = status.stats.errors;
                })
                .catch(error => console.error('Błąd podczas pobierania statusu:', error));
        }
        
        // Inicjalizacja WebSocket
        const ws = new WebSocket(`ws://${window.location.host}/ws`);
        
        ws.onmessage = function(event) {
            const status = JSON.parse(event.data);
            
            // Aktualizacja statusu
            const statusBadge = document.getElementById('status-badge');
            if (status.status === 'running') {
                statusBadge.className = 'badge bg-success status-badge';
                statusBadge.textContent = 'Aktywny';
            } else {
                statusBadge.className = 'badge bg-danger status-badge';
                statusBadge.textContent = 'Nieaktywny';
            }
            
            // Aktualizacja czasów
            document.getElementById('last-check').textContent = status.last_check;
            document.getElementById('next-check').textContent = status.next_check;
            
            // Aktualizacja statystyk
            document.getElementById('total-emails').textContent = status.stats.total_emails;
            document.getElementById('urgent-emails').textContent = status.stats.urgent_emails;
            document.getElementById('report-emails').textContent = status.stats.report_emails;
            document.getElementById('regular-emails').textContent = status.stats.regular_emails;
            document.getElementById('attachments').textContent = status.stats.attachments;
            document.getElementById('errors').textContent = status.stats.errors;
        };
        
        // Obsługa przycisku odświeżania logów
        document.getElementById('refresh-logs').addEventListener('click', updateLogs);
        
        // Inicjalne pobranie logów
        updateLogs();
        
        // Automatyczne odświeżanie logów co 10 sekund
        setInterval(updateLogs, 10000);
    </script>
</body>
</html>
    """
    
    # Zapisywanie szablonu
    os.makedirs("templates", exist_ok=True)
    with open("templates/dashboard.html", "w") as f:
        f.write(dashboard_html)
    
    print("Wygenerowano szablony HTML")

# Uruchomienie aplikacji
def main():
    """Główna funkcja uruchamiająca dashboard"""
    # Generowanie szablonów
    generate_templates()
    
    # Uruchomienie serwera
    port = config.get('monitoring', {}).get('dashboard_port', 8000)
    print(f"Uruchamianie dashboardu na porcie {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
