#!/usr/bin/env python3
"""
Mini Dashboard dla taskinity - prosty interfejs do monitorowania przepływów.
"""
import os
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

# Import funkcji do wizualizacji
from flow_visualizer import generate_mermaid_from_dsl, generate_mermaid_from_flow_history

# Importy z taskinity
from flow_dsl import (
    parse_dsl, load_dsl, list_dsl_files, list_flows, 
    run_flow_from_dsl, save_dsl
)

# Import nowych modułów (jeśli są dostępne)
try:
    from notification_service import load_config as load_notification_config, save_config as save_notification_config
    NOTIFICATIONS_AVAILABLE = True
except ImportError:
    NOTIFICATIONS_AVAILABLE = False

try:
    from parallel_executor import run_parallel_flow_from_dsl
    PARALLEL_AVAILABLE = True
except ImportError:
    PARALLEL_AVAILABLE = False

try:
    from flow_scheduler import (
        list_schedules, create_schedule, update_schedule, delete_schedule,
        start_scheduler, stop_scheduler, load_schedule
    )
    SCHEDULER_AVAILABLE = True
except ImportError:
    SCHEDULER_AVAILABLE = False

# Inicjalizacja aplikacji FastAPI
app = FastAPI(title="taskinity Mini Dashboard")

# Katalogi
BASE_DIR = Path(__file__).parent
FLOWS_DIR = BASE_DIR / "flows"
LOGS_DIR = BASE_DIR / "logs"
DSL_DIR = BASE_DIR / "dsl_definitions"

# Szablony HTML
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Tworzenie katalogu na szablony, jeśli nie istnieje
os.makedirs(BASE_DIR / "templates", exist_ok=True)

# Tworzenie głównego szablonu HTML
with open(BASE_DIR / "templates" / "mini.html", "w") as f:
    f.write("""<!DOCTYPE html>
<html>
<head>
    <title>taskinity Mini Dashboard</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <style>
        :root {
            --bg-color: #1e1e1e;
            --text-color: #e0e0e0;
            --header-bg: #2d2d2d;
            --header-text: #ffffff;
            --content-bg: #2d2d2d;
            --card-bg: #383838;
            --btn-bg: #0078d4;
            --btn-hover: #0063b1;
            --status-completed: #4caf50;
            --status-failed: #f44336;
            --status-running: #2196f3;
            --box-shadow: rgba(0, 0, 0, 0.3);
        }
        
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: var(--bg-color);
            color: var(--text-color);
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 10px;
        }
        .header {
            background-color: var(--header-bg);
            color: var(--header-text);
            padding: 10px;
            text-align: center;
            border-radius: 5px 5px 0 0;
            margin-bottom: 20px;
        }
        .content {
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
        }
        .flow-list {
            flex: 1;
            min-width: 300px;
        }
        .flow-details {
            flex: 2;
            min-width: 500px;
            background-color: var(--content-bg);
            padding: 15px;
            border-radius: 5px;
            box-shadow: 0 2px 5px var(--box-shadow);
        }
        .flow-item {
            background-color: var(--card-bg);
            padding: 10px;
            margin-bottom: 10px;
            border-radius: 5px;
            cursor: pointer;
            transition: background-color 0.2s;
        }
        .flow-item:hover {
            background-color: #4a4a4a;
        }
        .flow-item h3 {
            margin: 0 0 5px 0;
        }
        .flow-item p {
            margin: 5px 0;
            font-size: 0.9em;
        }
        .status-completed {
            color: var(--status-completed);
            font-weight: bold;
        }
        .status-failed {
            color: var(--status-failed);
            font-weight: bold;
        }
        .status-running {
            color: var(--status-running);
            font-weight: bold;
        }
        .btn {
            background-color: var(--btn-bg);
            color: white;
            border: none;
            padding: 8px 12px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            margin-right: 5px;
        }
        .btn:hover {
            background-color: var(--btn-hover);
        }
        .mermaid {
            background-color: var(--card-bg);
            padding: 15px;
            border-radius: 5px;
            margin: 15px 0;
            transform: scale(0.9);
            transform-origin: top left;
        }
        .logs {
            background-color: var(--card-bg);
            padding: 10px;
            border-radius: 5px;
            margin-top: 15px;
            max-height: 300px;
            overflow-y: auto;
            font-family: monospace;
            font-size: 0.9em;
            white-space: pre-wrap;
        }
        .task-list {
            margin-top: 15px;
        }
        .task-item {
            background-color: var(--card-bg);
            padding: 10px;
            margin-bottom: 5px;
            border-radius: 5px;
        }
        .edit-diagram {
            margin-top: 10px;
            margin-bottom: 20px;
        }
        .edit-diagram pre {
            width: 100%;
            max-height: 300px;
            background-color: #1e1e2e;
            color: #f8f8f2;
            border: 1px solid #4a4a4a;
            border-radius: 5px;
            padding: 10px;
            font-family: monospace;
            margin-bottom: 10px;
            overflow: auto;
        }
        .edit-diagram [contenteditable] {
            outline: none;
        }
        .code-editor-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background-color: #2d2d2d;
            padding: 8px 12px;
            border-top-left-radius: 5px;
            border-top-right-radius: 5px;
            border: 1px solid #4a4a4a;
            border-bottom: none;
        }
        .editor-buttons {
            display: flex;
            gap: 8px;
        }
        .svg-container {
            background-color: var(--card-bg);
            padding: 15px;
            border-radius: 5px;
            margin: 15px 0;
            overflow: auto;
            max-height: 400px;
        }
        .svg-container svg {
            transform: scale(0.9);
            transform-origin: top left;
            margin: 0 auto;
            display: block;
        }
        /* Style dla kolorowania logów */
        .log-error {
            color: #f44336;
            font-weight: bold;
        }
        .log-warning {
            color: #ff9800;
            font-weight: bold;
        }
        .log-info {
            color: #2196f3;
        }
        .log-success {
            color: #4caf50;
            font-weight: bold;
        }
        .log-date {
            color: #9e9e9e;
            font-style: italic;
        }
        /* Style dla powiadomień */
        .notification {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 20px;
            border-radius: 4px;
            color: white;
            font-weight: bold;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            z-index: 1000;
            opacity: 1;
            transition: opacity 0.3s ease;
        }
        .notification-hide {
            opacity: 0;
        }
        .notification-success {
            background-color: #4caf50;
        }
        .notification-error {
            background-color: #f44336;
        }
        .notification-info {
            background-color: #2196f3;
        }
        .notification-warning {
            background-color: #ff9800;
        }
        .search-bar {
            margin-bottom: 15px;
        }
        .search-bar input {
            width: 100%;
            padding: 8px;
            background-color: var(--card-bg);
            color: var(--text-color);
            border: 1px solid #4a4a4a;
            border-radius: 5px;
        }
        .filter-buttons {
            display: flex;
            gap: 10px;
            margin-bottom: 15px;
        }
        .filter-btn {
            background-color: var(--card-bg);
            color: var(--text-color);
            border: 1px solid #4a4a4a;
            border-radius: 5px;
            padding: 5px 10px;
            cursor: pointer;
        }
        .filter-btn.active {
            background-color: var(--btn-bg);
            color: white;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>taskinity Mini Dashboard</h1>
        </div>
        
        <div class="content">
            <div class="flow-list">
                <div class="search-bar">
                    <input type="text" id="search-input" placeholder="Szukaj przepływów..." onkeyup="filterFlows()">
                </div>
                
                <div class="filter-buttons">
                    <button class="filter-btn active" onclick="setFilter('all')">Wszystkie</button>
                    <button class="filter-btn" onclick="setFilter('completed')">Ukończone</button>
                    <button class="filter-btn" onclick="setFilter('failed')">Błędy</button>
                    <button class="filter-btn" onclick="setFilter('running')">Uruchomione</button>
                </div>
                
                <div id="flows-container"></div>
            </div>
            
            <div class="flow-details" id="flow-details">
                <p>Wybierz przepływ z listy, aby zobaczyć szczegóły.</p>
            </div>
        </div>
    </div>
    
    <script>
        // Inicjalizacja Mermaid
        mermaid.initialize({ startOnLoad: true });
        
        // Globalny stan
        let currentFlowId = null;
        let currentFilter = 'all';
        let flows = [];
        
        // Pobieranie listy przepływów
        function loadFlows() {
            fetch('/api/flows')
                .then(response => response.json())
                .then(data => {
                    flows = data;
                    renderFlowsList();
                })
                .catch(error => {
                    console.error('Błąd pobierania przepływów:', error);
                    document.getElementById('flows-container').innerHTML = '<p>Błąd pobierania przepływów</p>';
                });
        }
        
        // Renderowanie listy przepływów
        function renderFlowsList() {
            const container = document.getElementById('flows-container');
            container.innerHTML = '';
            
            const searchText = document.getElementById('search-input').value.toLowerCase();
            
            const filteredFlows = flows.filter(flow => {
                const matchesSearch = flow.name.toLowerCase().includes(searchText) || 
                                     (flow.flow_id && flow.flow_id.toLowerCase().includes(searchText));
                
                const matchesFilter = currentFilter === 'all' || 
                                     (currentFilter === 'completed' && flow.status === 'COMPLETED') ||
                                     (currentFilter === 'failed' && flow.status === 'FAILED') ||
                                     (currentFilter === 'running' && flow.status === 'RUNNING');
                
                return matchesSearch && matchesFilter;
            });
            
            if (filteredFlows.length === 0) {
                container.innerHTML = '<p>Brak przepływów spełniających kryteria</p>';
                return;
            }
            
            filteredFlows.forEach(flow => {
                const flowItem = document.createElement('div');
                flowItem.className = 'flow-item';
                flowItem.onclick = () => loadFlowDetails(flow.flow_id);
                
                let statusClass = '';
                if (flow.status === 'COMPLETED') {
                    statusClass = 'status-completed';
                } else if (flow.status === 'FAILED') {
                    statusClass = 'status-failed';
                } else if (flow.status === 'RUNNING') {
                    statusClass = 'status-running';
                }
                
                flowItem.innerHTML = `
                    <h3>${flow.name}</h3>
                    <p><span class="${statusClass}">${flow.status}</span></p>
                    <p>ID: ${flow.flow_id}</p>
                    <p>Czas: ${flow.start_time}</p>
                `;
                
                container.appendChild(flowItem);
            });
        }
        
        // Filtrowanie przepływów
        function filterFlows() {
            renderFlowsList();
        }
        
        // Ustawienie filtra
        function setFilter(filter) {
            currentFilter = filter;
            
            // Aktualizacja aktywnego przycisku
            document.querySelectorAll('.filter-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            
            document.querySelector(`.filter-btn[onclick="setFilter('${filter}')"]`).classList.add('active');
            
            renderFlowsList();
        }
        
        // Ładowanie szczegółów przepływu
        function loadFlowDetails(flowId) {
            currentFlowId = flowId;
            
            fetch(`/api/flows/${flowId}`)
                .then(response => response.json())
                .then(data => {
                    renderFlowDetails(data);
                })
                .catch(error => {
                    console.error('Błąd pobierania szczegółów przepływu:', error);
                    document.getElementById('flow-details').innerHTML = '<p>Błąd pobierania szczegółów przepływu</p>';
                });
        }
        
        // Renderowanie szczegółów przepływu
        function renderFlowDetails(flow) {
            let statusClass = '';
            if (flow.status === 'COMPLETED') {
                statusClass = 'status-completed';
            } else if (flow.status === 'FAILED') {
                statusClass = 'status-failed';
            } else if (flow.status === 'RUNNING') {
                statusClass = 'status-running';
            }
            
            // Upewnij się, że mamy domyślny diagram, jeśli nie ma w przepływie
            if (!flow.mermaid_diagram || flow.mermaid_diagram.trim() === '') {
                flow.mermaid_diagram = `graph TD\n    A[${flow.name}] --> B[Brak szczegółów diagramu]`;
            }
            
            let html = `
                <h2>${flow.name}</h2>
                <p><strong>Status:</strong> <span class="${statusClass}">${flow.status}</span></p>
                <p><strong>ID:</strong> ${flow.flow_id}</p>
                <p><strong>Czas rozpoczęcia:</strong> ${flow.start_time}</p>
                <p><strong>Czas zakończenia:</strong> ${flow.end_time || 'N/A'}</p>
                <p><strong>Czas trwania:</strong> ${flow.duration ? flow.duration.toFixed(2) + 's' : 'N/A'}</p>
            `;
            
            if (flow.error) {
                html += `<p><strong>Błąd:</strong> ${flow.error}</p>`;
            }
            
            // Dodanie logów (domyślnie otwarte)
            html += `
                <h3>Logi</h3>
                <button class="btn" id="toggle-logs-btn" onclick="toggleLogs('${flow.flow_id}')">Ukryj logi</button>
                <div id="logs-container" class="logs">Wczytywanie logów...</div>
            `;
            
            // Dodanie listy zadań
            if (flow.tasks && flow.tasks.length > 0) {
                html += '<h3>Zadania</h3><div class="task-list">';
                
                flow.tasks.forEach(task => {
                    let taskStatusClass = '';
                    if (task.status === 'COMPLETED') {
                        taskStatusClass = 'status-completed';
                    } else if (task.status === 'FAILED') {
                        taskStatusClass = 'status-failed';
                    } else if (task.status === 'RUNNING') {
                        taskStatusClass = 'status-running';
                    }
                    
                    html += `
                        <div class="task-item">
                            <p><strong>${task.name}</strong> <span class="${taskStatusClass}">${task.status}</span></p>
                            <p>Czas trwania: ${task.duration ? task.duration.toFixed(2) + 's' : 'N/A'}</p>
                        </div>
                    `;
                });
                
                html += '</div>';
            }
            
            // Dodanie diagramu Mermaid
            if (flow.mermaid_diagram) {
                const diagramId = `mermaid-diagram-${Date.now()}`;
                html += `
                    <h3>Diagram przepływu (Mermaid)</h3>
                    <div class="mermaid" id="${diagramId}">${flow.mermaid_diagram}</div>
                    <button class="btn" onclick="editDiagram('${diagramId}')">Edytuj diagram</button>
                    <button class="btn" onclick="saveSvg('${diagramId}', '${flow.name}_diagram.svg')">Pobierz SVG</button>
                    <div id="edit-diagram-container" class="edit-diagram" style="display: none;">
                        <div class="code-editor-header">
                            <span>Edycja diagramu</span>
                            <div class="editor-buttons">
                                <button class="btn" onclick="updateDiagram('${diagramId}')">Aktualizuj</button>
                                <button class="btn" onclick="cancelEdit()">Anuluj</button>
                            </div>
                        </div>
                        <pre><code class="language-mermaid" id="diagram-code" contenteditable="true">${flow.mermaid_diagram}</code></pre>
                    </div>
                `;
                
                // Dodanie SVG poniżej
                html += `
                    <h3>Diagram przepływu (SVG)</h3>
                    <div id="svg-container-${diagramId}" class="svg-container"></div>
                `;
            }
            
            document.getElementById('flow-details').innerHTML = html;
            
            // Inicjalizacja diagramu Mermaid
            if (flow.mermaid_diagram) {
                mermaid.init(undefined, document.querySelectorAll('.mermaid'));
                
                // Generowanie SVG po zainicjowaniu diagramu
                setTimeout(() => {
                    const diagramId = document.querySelector('.mermaid').id;
                    const svgElement = document.getElementById(diagramId).querySelector('svg');
                    if (svgElement) {
                        const svgContainer = document.getElementById(`svg-container-${diagramId}`);
                        svgContainer.innerHTML = '';
                        const svgClone = svgElement.cloneNode(true);
                        svgContainer.appendChild(svgClone);
                    }
                }, 500);
            }
            
            // Automatyczne ładowanie logów
            loadLogs(flow.flow_id);
        }
        
        // Edycja diagramu
        function editDiagram(diagramId) {
            const diagramContainer = document.getElementById(diagramId);
            const diagramCode = diagramContainer.innerHTML;
            document.getElementById('diagram-code').textContent = diagramCode;
            document.getElementById('edit-diagram-container').style.display = 'block';
            
            // Dodanie podświetlania składni
            highlightSyntax();
        }
        
        // Aktualizacja diagramu
        function updateDiagram(diagramId) {
            const newDiagramCode = document.getElementById('diagram-code').textContent;
            const diagramContainer = document.getElementById(diagramId);
            diagramContainer.innerHTML = newDiagramCode;
            
            try {
                // Inicjalizacja diagramu Mermaid
                mermaid.init(undefined, document.querySelectorAll('.mermaid'));
                
                // Aktualizacja SVG po zainicjowaniu diagramu
                setTimeout(() => {
                    const svgElement = document.getElementById(diagramId).querySelector('svg');
                    if (svgElement) {
                        const svgContainer = document.getElementById(`svg-container-${diagramId}`);
                        svgContainer.innerHTML = '';
                        const svgClone = svgElement.cloneNode(true);
                        svgContainer.appendChild(svgClone);
                    }
                }, 500);
                
                // Ukrycie edytora
                document.getElementById('edit-diagram-container').style.display = 'none';
                
                // Powiadomienie o sukcesie
                showNotification('Diagram zaktualizowany pomyślnie', 'success');
            } catch (error) {
                console.error('Błąd aktualizacji diagramu:', error);
                showNotification('Błąd aktualizacji diagramu: ' + error.message, 'error');
            }
        }
        
        // Anulowanie edycji
        function cancelEdit() {
            document.getElementById('edit-diagram-container').style.display = 'none';
        }
        
        // Podświetlanie składni Mermaid
        function highlightSyntax() {
            const codeElement = document.getElementById('diagram-code');
            const content = codeElement.textContent;
            
            // Proste podświetlanie składni Mermaid
            let highlighted = content
                // Kolorowanie słów kluczowych
                .replace(/(graph|flowchart|subgraph|end|classDef|class|click|style|linkStyle)\b/g, '<span style="color: #ff79c6;">$1</span>')
                // Kolorowanie kierunków
                .replace(/\b(TB|TD|BT|RL|LR)\b/g, '<span style="color: #bd93f9;">$1</span>')
                // Kolorowanie strzałek
        
        // Ładowanie logów
        function loadLogs(flowId) {
            const logsContainer = document.getElementById('logs-container');
            logsContainer.innerHTML = 'Ładowanie logów...';
            
            fetch(`/api/logs/${flowId}`)
                .then(response => response.json())
                .then(data => {
                    if (!data.content || data.content.trim() === '') {
                        // Pokaż przykładowe logi, gdy nie ma prawdziwych logów
                        const exampleLogs = `2025-05-24 00:58:00 INFO Rozpoczynam przepływ ${flowId.split('_')[0]}
` +
                            `2025-05-24 00:58:01 INFO Zadanie fetch_emails rozpoczęte
` +
                            `2025-05-24 00:58:02 INFO Zadanie fetch_emails zakończone
` +
                            `2025-05-24 00:58:03 INFO Zadanie classify_emails rozpoczęte
` +
                            `2025-05-24 00:58:04 WARNING Znaleziono wiadomości bez tematu
` +
                            `2025-05-24 00:58:05 INFO Zadanie classify_emails zakończone
` +
                            `2025-05-24 00:58:06 INFO Zadanie process_urgent_emails rozpoczęte
` +
                            `2025-05-24 00:58:07 INFO Zadanie process_urgent_emails zakończone
` +
                            `2025-05-24 00:58:08 INFO Zadanie process_regular_emails rozpoczęte
` +
                            `2025-05-24 00:58:09 ERROR Błąd przetwarzania wiadomości: Nieprawidłowy format
` +
                            `2025-05-24 00:58:10 INFO Zadanie process_regular_emails zakończone
` +
                            `2025-05-24 00:58:11 INFO Zadanie send_responses rozpoczęte
` +
                            `2025-05-24 00:58:12 SUCCESS Zadanie send_responses zakończone
` +
                            `2025-05-24 00:58:13 INFO Przepływ ${flowId.split('_')[0]} zakończony`;
                            
                        const formattedLogs = formatLogs(exampleLogs);
                        logsContainer.innerHTML = `<p><i>Brak rzeczywistych logów - wyświetlam przykładowe logi:</i></p>${formattedLogs}`;
                    } else {
                        // Formatowanie logów z kolorowaniem
                        const formattedLogs = formatLogs(data.content);
                        logsContainer.innerHTML = formattedLogs;
                    }
                })
                .catch(error => {
                    console.error('Błąd pobierania logów:', error);
                    logsContainer.innerHTML = 'Błąd pobierania logów';
                });
        }
        
        // Przełączanie widoczności logów
        function toggleLogs(flowId) {
            const logsContainer = document.getElementById('logs-container');
            const toggleButton = document.getElementById('toggle-logs-btn');
            
            if (logsContainer.style.display === 'none') {
                logsContainer.style.display = 'block';
                toggleButton.textContent = 'Ukryj logi';
                loadLogs(flowId);
            } else {
                logsContainer.style.display = 'none';
                toggleButton.textContent = 'Pokaż logi';
            }
        }
        
        // Formatowanie logów z kolorowaniem
        function formatLogs(logContent) {
            // Kolorowanie błędów na czerwono
            logContent = logContent.replace(/\b(ERROR|CRITICAL|FAILED|Exception|Error|Błąd|Wyjątek)\b/g, '<span class="log-error">$1</span>');
            
            // Kolorowanie ostrzeżeń na żółto
            logContent = logContent.replace(/\b(WARNING|WARN|Ostrzeżenie)\b/g, '<span class="log-warning">$1</span>');
            
            // Kolorowanie informacji na niebiesko
            logContent = logContent.replace(/\b(INFO|INFORMATION|Informacja)\b/g, '<span class="log-info">$1</span>');
            
            // Kolorowanie sukcesów na zielono
            logContent = logContent.replace(/\b(SUCCESS|COMPLETED|Sukces|Zakończono)\b/g, '<span class="log-success">$1</span>');
            
            // Kolorowanie dat i czasów
            logContent = logContent.replace(/(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2})/g, '<span class="log-date">$1</span>');
            
            // Dodanie nowych linii
            logContent = logContent.replace(/\n/g, '<br>');
            
            return logContent;
        }
        }
        
        // Inicjalizacja
        document.addEventListener('DOMContentLoaded', function() {
            loadFlows();
            
            // Odświeżanie co 10 sekund
            setInterval(loadFlows, 10000);
        });
    </script>
</body>
</html>""")

# Modele danych
class DSLRun(BaseModel):
    dsl: str
    input_data: Optional[Dict[str, Any]] = None
    use_file: bool = False
    use_parallel: bool = False

class NotificationConfig(BaseModel):
    enabled: bool = False
    email: Dict[str, Any] = {}
    slack: Dict[str, Any] = {}
    notification_rules: Dict[str, bool] = {}

class ScheduleCreate(BaseModel):
    dsl_path: str
    schedule_type: str = "interval"
    interval_minutes: int = 60
    cron_expression: Optional[str] = None
    input_data: Optional[Dict[str, Any]] = None
    enabled: bool = True
    use_parallel: bool = False
    description: Optional[str] = None

class ScheduleUpdate(BaseModel):
    schedule_type: Optional[str] = None
    interval_minutes: Optional[int] = None
    cron_expression: Optional[str] = None
    input_data: Optional[Dict[str, Any]] = None
    enabled: Optional[bool] = None
    use_parallel: Optional[bool] = None
    description: Optional[str] = None
    input_data: Dict[str, Any] = {}

# Endpoint główny - strona HTML
@app.get("/", response_class=HTMLResponse)
async def get_dashboard(request: Request):
    return templates.TemplateResponse("mini.html", {"request": request})

# API - lista przepływów
@app.get("/api/flows")
async def api_flows():
    flows = list_flows()
    return flows

# API - szczegóły przepływu
@app.get("/api/flows/{flow_id}")
async def api_flow_details(flow_id: str):
    flow_file = FLOWS_DIR / f"{flow_id}.json"
    
    if not flow_file.exists():
        raise HTTPException(status_code=404, detail="Przepływ nie znaleziony")
    
    with open(flow_file, "r") as f:
        flow_data = json.load(f)
    
    # Dodanie informacji o zadaniach
    tasks = []
    for task_id in flow_data.get("tasks", []):
        task_file = FLOWS_DIR / f"{task_id}.json"
        if task_file.exists():
            with open(task_file, "r") as f:
                task_data = json.load(f)
                tasks.append(task_data)
    
    flow_data["tasks"] = tasks
    
    # Generowanie diagramu Mermaid dla przepływu
    mermaid_code = generate_mermaid_from_flow_history(flow_id)
    flow_data["mermaid_diagram"] = mermaid_code
    
    return flow_data

# API - logi dla przepływu
@app.get("/api/logs/{flow_id}")
async def api_flow_logs(flow_id: str):
    # Próba znalezienia pliku logu dla przepływu
    log_file = LOGS_DIR / f"{flow_id}.log"
    
    content = ""
    if log_file.exists():
        with open(log_file, "r") as f:
            content = f.read()
    else:
        # Jeśli nie ma dedykowanego pliku logu, spróbuj znaleźć wpisy w głównym pliku logu
        main_log_file = LOGS_DIR / "flow.log"
        if main_log_file.exists():
            with open(main_log_file, "r") as f:
                log_content = f.read()
                # Filtrowanie linii zawierających ID przepływu
                content = "\n".join([line for line in log_content.split("\n") if flow_id in line])
    
    return {"flow_id": flow_id, "content": content}

# API - uruchomienie przepływu
@app.post("/api/run")
async def api_run_flow(run_data: DSLRun):
    try:
        if run_data.use_file:
            dsl_file = DSL_DIR / run_data.dsl
            if not dsl_file.exists():
                raise HTTPException(status_code=404, detail="Definicja DSL nie znaleziona")
            dsl_content = load_dsl(str(dsl_file))
        else:
            dsl_content = run_data.dsl
            
        # Wybierz odpowiednią metodę uruchomienia (równoległa lub standardowa)
        if run_data.use_parallel and PARALLEL_AVAILABLE:
            logger.info("Uruchamianie przepływu w trybie równoległym")
            result = run_parallel_flow_from_dsl(dsl_content, run_data.input_data)
        else:
            logger.info("Uruchamianie przepływu w trybie standardowym")
            result = run_flow_from_dsl(dsl_content, run_data.input_data)
        
        # Parsowanie DSL, aby uzyskać nazwę przepływu
        flow_def = parse_dsl(dsl_content)
        flow_name = flow_def.get("name", "UnknownFlow")
        
        # Upewniamy się, że wszystkie zadania istnieją
        tasks_exist = True
        missing_tasks = []
        
        for conn in flow_def.get("connections", []):
            source = conn.get("source")
            target = conn.get("target")
            
            # Sprawdzamy, czy zadania są zarejestrowane w flow_dsl
            from flow_dsl import _REGISTERED_TASKS
            
            if source not in _REGISTERED_TASKS:
                tasks_exist = False
                missing_tasks.append(source)
            
            if target not in _REGISTERED_TASKS:
                tasks_exist = False
                missing_tasks.append(target)
        
        if not tasks_exist:
            return {
                "error": f"Brakujące zadania: {', '.join(set(missing_tasks))}. Upewnij się, że wszystkie zadania są zaimportowane i zarejestrowane."
            }
        
        # Uruchomienie przepływu
        result = run_flow_from_dsl(dsl_content, run_data.input_data)
        
        # Znalezienie ID przepływu (ostatni uruchomiony przepływ o tej nazwie)
        flows = list_flows()
        flow_id = None
        for flow in reversed(flows):  # Szukamy od najnowszego
            if flow.get("name") == flow_name:
                flow_id = flow.get("flow_id")
                break
        
        return {
            "flow_id": flow_id,
            "name": flow_name,
            "result": result
        }
    except Exception as e:
        import traceback
        traceback_str = traceback.format_exc()
        print(f"Błąd podczas uruchamiania przepływu: {str(e)}\n{traceback_str}")
        return {"error": str(e)}

# API - powiadomienia
@app.get("/api/notifications/config")
async def api_get_notification_config():
    if not NOTIFICATIONS_AVAILABLE:
        return {"error": "Moduł powiadomień nie jest dostępny"}
    
    config = load_notification_config()
    return config

@app.post("/api/notifications/config")
async def api_update_notification_config(config: NotificationConfig):
    if not NOTIFICATIONS_AVAILABLE:
        return {"error": "Moduł powiadomień nie jest dostępny"}
    
    try:
        save_notification_config(config.dict())
        return {"status": "success", "message": "Konfiguracja powiadomień zaktualizowana"}
    except Exception as e:
        return {"error": str(e)}

# API - planowanie
@app.get("/api/schedules")
async def api_list_schedules():
    if not SCHEDULER_AVAILABLE:
        return {"error": "Moduł planowania nie jest dostępny"}
    
    schedules = list_schedules()
    return {"schedules": schedules}

@app.get("/api/schedules/{schedule_id}")
async def api_get_schedule(schedule_id: str):
    if not SCHEDULER_AVAILABLE:
        return {"error": "Moduł planowania nie jest dostępny"}
    
    schedule = load_schedule(schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Harmonogram nie znaleziony")
    
    return schedule.to_dict()

@app.post("/api/schedules")
async def api_create_schedule(schedule_data: ScheduleCreate):
    if not SCHEDULER_AVAILABLE:
        return {"error": "Moduł planowania nie jest dostępny"}
    
    try:
        schedule = create_schedule(
            dsl_path=schedule_data.dsl_path,
            schedule_type=schedule_data.schedule_type,
            interval_minutes=schedule_data.interval_minutes,
            cron_expression=schedule_data.cron_expression,
            input_data=schedule_data.input_data,
            enabled=schedule_data.enabled,
            use_parallel=schedule_data.use_parallel,
            description=schedule_data.description
        )
        return {"status": "success", "schedule_id": schedule.schedule_id}
    except Exception as e:
        return {"error": str(e)}

@app.put("/api/schedules/{schedule_id}")
async def api_update_schedule(schedule_id: str, schedule_data: ScheduleUpdate):
    if not SCHEDULER_AVAILABLE:
        return {"error": "Moduł planowania nie jest dostępny"}
    
    try:
        schedule = update_schedule(schedule_id, **{k: v for k, v in schedule_data.dict().items() if v is not None})
        if not schedule:
            raise HTTPException(status_code=404, detail="Harmonogram nie znaleziony")
        
        return {"status": "success", "message": "Harmonogram zaktualizowany"}
    except Exception as e:
        return {"error": str(e)}

@app.delete("/api/schedules/{schedule_id}")
async def api_delete_schedule(schedule_id: str):
    if not SCHEDULER_AVAILABLE:
        return {"error": "Moduł planowania nie jest dostępny"}
    
    if delete_schedule(schedule_id):
        return {"status": "success", "message": "Harmonogram usunięty"}
    else:
        raise HTTPException(status_code=404, detail="Harmonogram nie znaleziony")

@app.post("/api/schedules/{schedule_id}/run")
async def api_run_schedule(schedule_id: str):
    if not SCHEDULER_AVAILABLE:
        return {"error": "Moduł planowania nie jest dostępny"}
    
    schedule = load_schedule(schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Harmonogram nie znaleziony")
    
    try:
        result = schedule.run()
        return {"status": "success", "result": result}
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/scheduler/start")
async def api_start_scheduler():
    if not SCHEDULER_AVAILABLE:
        return {"error": "Moduł planowania nie jest dostępny"}
    
    try:
        start_scheduler()
        return {"status": "success", "message": "Planer uruchomiony"}
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/scheduler/stop")
async def api_stop_scheduler():
    if not SCHEDULER_AVAILABLE:
        return {"error": "Moduł planowania nie jest dostępny"}
    
    try:
        stop_scheduler()
        return {"status": "success", "message": "Planer zatrzymany"}
    except Exception as e:
        return {"error": str(e)}

def main():
    # Tworzenie katalogów, jeśli nie istnieją
    os.makedirs(FLOWS_DIR, exist_ok=True)
    os.makedirs(LOGS_DIR, exist_ok=True)
    os.makedirs(DSL_DIR, exist_ok=True)
    
    # Próba uruchomienia serwera na różnych portach
    ports = [8765, 7654, 6543, 5432, 4321, 3210, 2109, 1098]
    
    for port in ports:
        try:
            print(f"Próba uruchomienia serwera na porcie {port}...")
            uvicorn.run(app, host="0.0.0.0", port=port)
            break
        except OSError as e:
            print(f"Port {port} jest już zajęty, próbuję następny...")
            if port == ports[-1]:
                print("Wszystkie porty są zajęte. Nie można uruchomić serwera.")
                print("Sprawdź, czy nie masz już uruchomionego dashboardu lub innej aplikacji na tych portach.")
                print("Możesz również ręcznie zmodyfikować port w pliku mini_dashboard.py.")
                break

if __name__ == "__main__":
    main()
