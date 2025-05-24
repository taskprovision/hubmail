#!/usr/bin/env python3
"""
Prosty dashboard do monitorowania przepływów i logów taskinity.
Minimalistyczna implementacja z użyciem FastAPI i HTML/JavaScript.
"""
import os
import json
import base64
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

import uvicorn
from fastapi import FastAPI, Request, Form, HTTPException
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

# Inicjalizacja aplikacji FastAPI
app = FastAPI(title="taskinity Dashboard")

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
with open(BASE_DIR / "templates" / "index.html", "w") as f:
    f.write("""<!DOCTYPE html>
<html>
<head>
    <title>taskinity Dashboard</title>
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
            --tab-bg: #383838;
            --tab-active: #0078d4;
            --tab-hover: #4a4a4a;
            --table-header: #383838;
            --table-border: #4a4a4a;
            --table-hover: #4a4a4a;
            --btn-bg: #0078d4;
            --btn-hover: #0063b1;
            --input-bg: #383838;
            --input-border: #4a4a4a;
            --pre-bg: #252525;
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
            padding: 20px;
        }
        .header {
            background-color: var(--header-bg);
            color: var(--header-text);
            padding: 20px;
            text-align: center;
            border-radius: 5px 5px 0 0;
        }
        .content {
            background-color: var(--content-bg);
            padding: 20px;
            border-radius: 0 0 5px 5px;
            box-shadow: 0 2px 5px var(--box-shadow);
        }
        .tab {
            overflow: hidden;
            border: 1px solid var(--table-border);
            background-color: var(--tab-bg);
            border-radius: 5px 5px 0 0;
        }
        .tab button {
            background-color: inherit;
            float: left;
            border: none;
            outline: none;
            cursor: pointer;
            padding: 14px 16px;
            transition: 0.3s;
            font-size: 16px;
            color: var(--text-color);
        }
        .tab button:hover {
            background-color: var(--tab-hover);
        }
        .tab button.active {
            background-color: var(--tab-active);
            color: white;
        }
        .tabcontent {
            display: none;
            padding: 20px;
            border: 1px solid var(--table-border);
            border-top: none;
            border-radius: 0 0 5px 5px;
            animation: fadeEffect 1s;
        }
        @keyframes fadeEffect {
            from {opacity: 0;}
            to {opacity: 1;}
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            color: var(--text-color);
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid var(--table-border);
        }
        th {
            background-color: var(--table-header);
        }
        tr:hover {
            background-color: var(--table-hover);
        }
        .card {
            background-color: var(--card-bg);
            border-radius: 5px;
            box-shadow: 0 2px 5px var(--box-shadow);
            padding: 20px;
            margin-bottom: 20px;
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
            padding: 10px 15px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
        }
        .btn:hover {
            background-color: var(--btn-hover);
        }
        textarea {
            width: 100%;
            height: 200px;
            padding: 12px;
            border: 1px solid var(--input-border);
            border-radius: 4px;
            resize: vertical;
            font-family: monospace;
            background-color: var(--input-bg);
            color: var(--text-color);
        }
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        input[type="text"], select {
            width: 100%;
            padding: 8px;
            border: 1px solid var(--input-border);
            border-radius: 4px;
            background-color: var(--input-bg);
            color: var(--text-color);
        }
        pre {
            background-color: var(--pre-bg);
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            white-space: pre-wrap;
            font-family: monospace;
            color: var(--text-color);
        }
        .flow-diagram {
            width: 100%;
            max-width: 800px;
            margin: 20px auto;
            display: block;
        }
        .mermaid {
            background-color: var(--card-bg);
            padding: 15px;
            border-radius: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>taskinity Dashboard</h1>
            <p>Prosty monitoring przepływów i logów</p>
        </div>
        
        <div class="content">
            <div class="tab">
                <button class="tablinks active" onclick="openTab(event, 'flows')">Przepływy</button>
                <button class="tablinks" onclick="openTab(event, 'dsl')">Definicje DSL</button>
                <button class="tablinks" onclick="openTab(event, 'logs')">Logi</button>
                <button class="tablinks" onclick="openTab(event, 'run')">Uruchom przepływ</button>
            </div>
            
            <div id="flows" class="tabcontent" style="display: block;">
                <h2>Historia przepływów</h2>
                <button class="btn" onclick="refreshFlows()">Odśwież</button>
                <div id="flows-list">
                    <p>Ładowanie przepływów...</p>
                </div>
            </div>
            
            <div id="dsl" class="tabcontent">
                <h2>Definicje DSL</h2>
                <button class="btn" onclick="refreshDSL()">Odśwież</button>
                <div id="dsl-list">
                    <p>Ładowanie definicji DSL...</p>
                </div>
            </div>
            
            <div id="logs" class="tabcontent">
                <h2>Logi</h2>
                <div class="form-group">
                    <label for="log-source">Źródło logów:</label>
                    <select id="log-source" onchange="refreshLogs()">
                        <option value="flow">Przepływy</option>
                        <option value="python">Python</option>
                    </select>
                </div>
                <button class="btn" onclick="refreshLogs()">Odśwież</button>
                <div id="logs-content">
                    <pre>Ładowanie logów...</pre>
                </div>
            </div>
            
            <div id="run" class="tabcontent">
                <h2>Uruchom przepływ</h2>
                <div class="form-group">
                    <label for="dsl-select">Wybierz definicję DSL:</label>
                    <select id="dsl-select">
                        <option value="">-- Wybierz definicję --</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="dsl-content">Lub wpisz definicję DSL:</label>
                    <textarea id="dsl-content" placeholder="flow MyFlow:&#10;    description: &quot;Opis przepływu&quot;&#10;    task1 -> task2"></textarea>
                </div>
                <div class="form-group">
                    <label for="input-data">Dane wejściowe (JSON):</label>
                    <textarea id="input-data" placeholder='{&#10;    "param1": "value1",&#10;    "param2": 123&#10;}'></textarea>
                </div>
                <button class="btn" onclick="runFlow()">Uruchom przepływ</button>
                <div id="run-result" style="margin-top: 20px;"></div>
            </div>
        </div>
    </div>
    
    <script>
        // Inicjalizacja Mermaid
        mermaid.initialize({ startOnLoad: true });
        
        // Obsługa zakładek
        function openTab(evt, tabName) {
            var i, tabcontent, tablinks;
            tabcontent = document.getElementsByClassName("tabcontent");
            for (i = 0; i < tabcontent.length; i++) {
                tabcontent[i].style.display = "none";
            }
            tablinks = document.getElementsByClassName("tablinks");
            for (i = 0; i < tablinks.length; i++) {
                tablinks[i].className = tablinks[i].className.replace(" active", "");
            }
            document.getElementById(tabName).style.display = "block";
            evt.currentTarget.className += " active";
            
            // Odświeżanie zawartości zakładki
            if (tabName === "flows") {
                refreshFlows();
            } else if (tabName === "dsl") {
                refreshDSL();
            } else if (tabName === "logs") {
                refreshLogs();
            } else if (tabName === "run") {
                loadDSLOptions();
            }
        }
        
        // Pobieranie listy przepływów
        function refreshFlows() {
            fetch('/api/flows')
                .then(response => response.json())
                .then(data => {
                    let html = '<table>';
                    html += '<tr><th>ID</th><th>Nazwa</th><th>Status</th><th>Czas rozpoczęcia</th><th>Czas trwania</th><th>Akcje</th></tr>';
                    
                    if (data.length === 0) {
                        html += '<tr><td colspan="6">Brak przepływów</td></tr>';
                    } else {
                        data.forEach(flow => {
                            let statusClass = '';
                            if (flow.status === 'COMPLETED') {
                                statusClass = 'status-completed';
                            } else if (flow.status === 'FAILED') {
                                statusClass = 'status-failed';
                            } else if (flow.status === 'RUNNING') {
                                statusClass = 'status-running';
                            }
                            
                            html += `<tr>
                                <td>${flow.flow_id}</td>
                                <td>${flow.name}</td>
                                <td class="${statusClass}">${flow.status}</td>
                                <td>${flow.start_time}</td>
                                <td>${flow.duration ? flow.duration.toFixed(2) + 's' : 'N/A'}</td>
                                <td>
                                    <button class="btn" onclick="viewFlowDetails('${flow.flow_id}')">Szczegóły</button>
                                </td>
                            </tr>`;
                        });
                    }
                    
                    html += '</table>';
                    document.getElementById('flows-list').innerHTML = html;
                })
                .catch(error => {
                    console.error('Błąd pobierania przepływów:', error);
                    document.getElementById('flows-list').innerHTML = '<p>Błąd pobierania przepływów</p>';
                });
        }
        
        // Pobieranie listy definicji DSL
        function refreshDSL() {
            fetch('/api/dsl')
                .then(response => response.json())
                .then(data => {
                    let html = '<table>';
                    html += '<tr><th>Nazwa</th><th>Akcje</th></tr>';
                    
                    if (data.length === 0) {
                        html += '<tr><td colspan="2">Brak definicji DSL</td></tr>';
                    } else {
                        data.forEach(dsl => {
                            html += `<tr>
                                <td>${dsl.name}</td>
                                <td>
                                    <button class="btn" onclick="viewDSL('${dsl.name}')">Podgląd</button>
                                </td>
                            </tr>`;
                        });
                    }
                    
                    html += '</table>';
                    document.getElementById('dsl-list').innerHTML = html;
                })
                .catch(error => {
                    console.error('Błąd pobierania definicji DSL:', error);
                    document.getElementById('dsl-list').innerHTML = '<p>Błąd pobierania definicji DSL</p>';
                });
        }
        
        // Pobieranie logów
        function refreshLogs() {
            const source = document.getElementById('log-source').value;
            
            fetch(`/api/logs?source=${source}`)
                .then(response => response.json())
                .then(data => {
                    document.getElementById('logs-content').innerHTML = `<pre>${data.content}</pre>`;
                })
                .catch(error => {
                    console.error('Błąd pobierania logów:', error);
                    document.getElementById('logs-content').innerHTML = '<pre>Błąd pobierania logów</pre>';
                });
        }
        
        // Pobieranie szczegółów przepływu
        function viewFlowDetails(flowId) {
            fetch(`/api/flows/${flowId}`)
                .then(response => response.json())
                .then(data => {
                    let html = `<div class="card">
                        <h3>Przepływ: ${data.name}</h3>
                        <p><strong>ID:</strong> ${data.flow_id}</p>
                        <p><strong>Status:</strong> <span class="${getStatusClass(data.status)}">${data.status}</span></p>
                        <p><strong>Czas rozpoczęcia:</strong> ${data.start_time}</p>
                        <p><strong>Czas zakończenia:</strong> ${data.end_time || 'N/A'}</p>
                        <p><strong>Czas trwania:</strong> ${data.duration ? data.duration.toFixed(2) + 's' : 'N/A'}</p>
                    `;
                    
                    if (data.error) {
                        html += `<p><strong>Błąd:</strong> ${data.error}</p>`;
                    }
                    
                    html += '<h4>Zadania:</h4><table>';
                    html += '<tr><th>ID</th><th>Nazwa</th><th>Status</th><th>Czas trwania</th></tr>';
                    
                    if (data.tasks && data.tasks.length > 0) {
                        data.tasks.forEach(task => {
                            html += `<tr>
                                <td>${task.task_id}</td>
                                <td>${task.name}</td>
                                <td class="${getStatusClass(task.status)}">${task.status}</td>
                                <td>${task.duration ? task.duration.toFixed(2) + 's' : 'N/A'}</td>
                            </tr>`;
                        });
                    } else {
                        html += '<tr><td colspan="4">Brak zadań</td></tr>';
                    }
                    
                    html += '</table></div>';
                    
                    // Dodanie wizualizacji Mermaid dla przepływu
                    if (data.mermaid_diagram) {
                        const diagramId = `mermaid-flow-${Date.now()}`;
                        html += `<div class="card">
                            <h3>Wizualizacja przepływu</h3>
                            <div class="mermaid" id="${diagramId}">${data.mermaid_diagram}</div>
                        </div>`;
                        
                        // Dodanie przycisku do pobrania diagramu jako SVG
                        html += `<button class="btn" onclick="saveSvg('${diagramId}', '${data.name}_flow_diagram.svg')">Pobierz diagram SVG</button>`;
                    }
                    
                    document.getElementById('flows-list').innerHTML = html + '<button class="btn" onclick="refreshFlows()">Powrót</button>';
                    
                    // Renderowanie diagramu Mermaid
                    if (data.mermaid_diagram) {
                        mermaid.init(undefined, document.querySelectorAll('.mermaid'));
                    }
                })
                .catch(error => {
                    console.error('Błąd pobierania szczegółów przepływu:', error);
                    document.getElementById('flows-list').innerHTML = '<p>Błąd pobierania szczegółów przepływu</p>';
                });
        }
        
        // Podgląd definicji DSL
        function viewDSL(name) {
            fetch(`/api/dsl/${name}`)
                .then(response => response.json())
                .then(data => {
                    let html = `<div class="card">
                        <h3>Definicja DSL: ${name}</h3>
                        <pre>${data.content}</pre>
                    </div>`;
                    
                    // Dodanie wizualizacji Mermaid dla DSL
                    if (data.mermaid_diagram) {
                        const diagramId = `mermaid-diagram-${Date.now()}`;
                        html += `<div class="card">
                            <h3>Wizualizacja przepływu</h3>
                            <div class="mermaid" id="${diagramId}">${data.mermaid_diagram}</div>
                        </div>`;
                        
                        // Dodanie przycisku do pobrania diagramu jako SVG
                        html += `<button class="btn" onclick="saveSvg('${diagramId}', '${name}_diagram.svg')">Pobierz diagram SVG</button>`;
                    }
                    
                    document.getElementById('dsl-list').innerHTML = html + '<button class="btn" onclick="refreshDSL()">Powrót</button>';
                    
                    // Renderowanie diagramu Mermaid i automatyczne zapisanie SVG
                    if (data.mermaid_diagram) {
                        mermaid.init(undefined, document.querySelectorAll('.mermaid'));
                        
                        // Automatyczne generowanie SVG po zainicjowaniu diagramu
                        setTimeout(() => {
                            // Upewniamy się, że diagram został wyrenderowany
                            const svgElement = document.getElementById(diagramId).querySelector('svg');
                            if (svgElement) {
                                // Tworzymy link do pobrania SVG
                                const svgData = new XMLSerializer().serializeToString(svgElement);
                                const svgBlob = new Blob([svgData], {type: 'image/svg+xml;charset=utf-8'});
                                const svgUrl = URL.createObjectURL(svgBlob);
                                
                                // Wyświetlamy SVG w nowym elemencie
                                const svgContainer = document.createElement('div');
                                svgContainer.className = 'card';
                                svgContainer.innerHTML = `
                                    <h3>Diagram SVG</h3>
                                    <object data="${svgUrl}" type="image/svg+xml" style="width:100%;height:auto;"></object>
                                `;
                                
                                // Wstawiamy element przed przyciskiem powrót
                                const dslList = document.getElementById('dsl-list');
                                const backButton = dslList.querySelector('button');
                                dslList.insertBefore(svgContainer, backButton);
                            }
                        }, 500); // Dajemy czas na wyrenderowanie diagramu
                    }
                })
                .catch(error => {
                    console.error('Błąd pobierania definicji DSL:', error);
                    document.getElementById('dsl-list').innerHTML = '<p>Błąd pobierania definicji DSL</p>';
                });
        }
        
        // Ładowanie opcji DSL do selecta
        function loadDSLOptions() {
            fetch('/api/dsl')
                .then(response => response.json())
                .then(data => {
                    const select = document.getElementById('dsl-select');
                    select.innerHTML = '<option value="">-- Wybierz definicję --</option>';
                    
                    data.forEach(dsl => {
                        const option = document.createElement('option');
                        option.value = dsl.name;
                        option.textContent = dsl.name;
                        select.appendChild(option);
                    });
                })
                .catch(error => {
                    console.error('Błąd pobierania definicji DSL:', error);
                });
        }
        
        // Uruchamianie przepływu
        function runFlow() {
            const dslSelect = document.getElementById('dsl-select').value;
            const dslContent = document.getElementById('dsl-content').value;
            const inputData = document.getElementById('input-data').value;
            
            let dsl = '';
            let useFile = false;
            
            if (dslSelect) {
                dsl = dslSelect;
                useFile = true;
            } else if (dslContent) {
                dsl = dslContent;
                useFile = false;
            } else {
                document.getElementById('run-result').innerHTML = '<p class="status-failed">Wybierz definicję DSL lub wpisz własną</p>';
                return;
            }
            
            let data = {};
            try {
                if (inputData) {
                    data = JSON.parse(inputData);
                }
            } catch (e) {
                document.getElementById('run-result').innerHTML = '<p class="status-failed">Nieprawidłowy format danych wejściowych (JSON)</p>';
                return;
            }
            
            document.getElementById('run-result').innerHTML = '<p>Uruchamianie przepływu...</p>';
            
            fetch('/api/run', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    dsl: dsl,
                    use_file: useFile,
                    input_data: data
                })
            })
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        // Wyświetlenie szczegółowego błędu
                        let errorHtml = `<div class="card">
                            <h3 class="status-failed">Błąd uruchamiania przepływu</h3>
                            <p>${data.error}</p>
                        </div>`;
                        
                        // Dodanie informacji o możliwych przyczynach błędu
                        errorHtml += `<div class="card">
                            <h3>Możliwe przyczyny błędu:</h3>
                            <ul>
                                <li>Brakujące zadania - upewnij się, że wszystkie zadania są zaimportowane i zarejestrowane</li>
                                <li>Błędna składnia DSL - sprawdź, czy definicja DSL jest poprawna</li>
                                <li>Nieprawidłowe dane wejściowe - sprawdź, czy dane wejściowe są zgodne z oczekiwanymi przez zadania</li>
                                <li>Błąd podczas wykonania zadania - sprawdź logi, aby uzyskać więcej informacji</li>
                            </ul>
                        </div>`;
                        
                        document.getElementById('run-result').innerHTML = errorHtml;
                    } else {
                        // Wyświetlenie informacji o pomyślnym uruchomieniu
                        let resultHtml = `<div class="card">
                            <h3 class="status-completed">Przepływ uruchomiony pomyślnie!</h3>
                            <p><strong>ID:</strong> ${data.flow_id}</p>
                            <p><strong>Nazwa:</strong> ${data.name}</p>
                        </div>`;
                        
                        // Wyświetlenie wyników przepływu, jeśli są dostępne
                        if (data.result) {
                            resultHtml += `<div class="card">
                                <h3>Wyniki przepływu:</h3>
                                <pre>${JSON.stringify(data.result, null, 2)}</pre>
                            </div>`;
                        }
                        
                        // Dodanie przycisku do podglądu szczegółów
                        resultHtml += `<button class="btn" onclick="viewFlowDetails('${data.flow_id}')">Zobacz szczegóły przepływu</button>`;
                        
                        document.getElementById('run-result').innerHTML = resultHtml;
                        
                        // Odświeżenie listy przepływów w tle
                        setTimeout(refreshFlows, 1000);
                    }
                })
                .catch(error => {
                    console.error('Błąd uruchamiania przepływu:', error);
                    document.getElementById('run-result').innerHTML = `<div class="card">
                        <h3 class="status-failed">Błąd uruchamiania przepływu</h3>
                        <p>Wystąpił nieoczekiwany błąd podczas próby uruchomienia przepływu.</p>
                        <p>Szczegóły błędu: ${error.message || 'Brak szczegółów'}</p>
                    </div>`;
                });
        }
        
        // Funkcja do zapisywania diagramu jako SVG
        function saveSvg(id, filename) {
            const svgEl = document.getElementById(id).querySelector('svg');
            if (!svgEl) {
                console.error('Nie znaleziono elementu SVG');
                return;
            }
            
            // Pobranie kodu SVG
            const svgData = svgEl.outerHTML;
            const svgBlob = new Blob([svgData], {type: 'image/svg+xml;charset=utf-8'});
            const svgUrl = URL.createObjectURL(svgBlob);
            
            // Utworzenie linku do pobrania
            const downloadLink = document.createElement('a');
            downloadLink.href = svgUrl;
            downloadLink.download = filename;
            document.body.appendChild(downloadLink);
            downloadLink.click();
            document.body.removeChild(downloadLink);
            
            // Zwolnienie URL
            setTimeout(() => {
                URL.revokeObjectURL(svgUrl);
            }, 100);
        }
        
        // Pomocnicza funkcja do określania klasy statusu
        function getStatusClass(status) {
            if (status === 'COMPLETED') {
                return 'status-completed';
            } else if (status === 'FAILED') {
                return 'status-failed';
            } else if (status === 'RUNNING') {
                return 'status-running';
            }
            return '';
        }
        
        // Inicjalizacja
        document.addEventListener('DOMContentLoaded', function() {
            refreshFlows();
        });
    </script>
</body>
</html>""")

# Modele danych
class DSLRun(BaseModel):
    dsl: str
    use_file: bool = False
    input_data: Dict[str, Any] = {}

# Endpoint główny - strona HTML
@app.get("/", response_class=HTMLResponse)
async def get_dashboard(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

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

# API - lista definicji DSL
@app.get("/api/dsl")
async def api_dsl_list():
    dsl_files = list_dsl_files()
    return [{"name": dsl_file} for dsl_file in dsl_files]

# API - szczegóły definicji DSL
@app.get("/api/dsl/{name}")
async def api_dsl_details(name: str):
    dsl_file = DSL_DIR / f"{name}"
    
    if not dsl_file.exists():
        raise HTTPException(status_code=404, detail="Definicja DSL nie znaleziona")
    
    dsl_content = load_dsl(str(dsl_file))
    
    # Generowanie diagramu Mermaid dla DSL
    mermaid_code = generate_mermaid_from_dsl(dsl_content)
    
    return {
        "name": name,
        "content": dsl_content,
        "mermaid_diagram": mermaid_code
    }

# API - logi
@app.get("/api/logs")
async def api_logs(source: str = "flow"):
    if source == "flow":
        log_file = LOGS_DIR / "flow.log"
    else:
        log_file = LOGS_DIR / "python.log"
    
    content = ""
    if log_file.exists():
        with open(log_file, "r") as f:
            content = f.read()
    
    return {"source": source, "content": content}

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

# Uruchomienie serwera
def main():
    # Tworzenie katalogów, jeśli nie istnieją
    os.makedirs(FLOWS_DIR, exist_ok=True)
    os.makedirs(LOGS_DIR, exist_ok=True)
    os.makedirs(DSL_DIR, exist_ok=True)
    
    # Próba uruchomienia serwera na różnych portach
    ports = [12345, 23456, 34567, 45678, 56789, 10001, 10002, 10003]
    
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
                print("Możesz również ręcznie zmodyfikować port w pliku simple_dashboard.py.")
                break

if __name__ == "__main__":
    main()
