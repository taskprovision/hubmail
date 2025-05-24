#!/usr/bin/env python3
"""
taskinity - prosty framework do definiowania przepływów za pomocą dekoratorów i DSL.
Pozwala na łatwe łączenie funkcji w przepływy i monitorowanie ich wykonania.
"""
import functools
import inspect
import json
import logging
import os
import re
import time
import traceback
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Type, Union

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("flow_dsl")

# Katalog na logi i dane przepływów
FLOW_DIR = os.getenv("FLOW_DIR", os.path.join(os.path.dirname(__file__), "flows"))
LOG_DIR = os.getenv("LOG_DIR", os.path.join(os.path.dirname(__file__), "logs"))
os.makedirs(FLOW_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

# Typy statusów przepływu
class FlowStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"

# Rejestr wszystkich zarejestrowanych funkcji
REGISTRY = {}

# Historia wykonania przepływów
FLOW_HISTORY = []

def task(name: Optional[str] = None, 
         description: Optional[str] = None, 
         validate_input: Optional[Callable] = None,
         validate_output: Optional[Callable] = None):
    """
    Dekorator do rejestrowania funkcji jako zadania w przepływie.
    
    Args:
        name: Opcjonalna nazwa zadania (domyślnie: nazwa funkcji)
        description: Opcjonalny opis zadania
        validate_input: Opcjonalna funkcja do walidacji danych wejściowych
        validate_output: Opcjonalna funkcja do walidacji danych wyjściowych
    """
    def decorator(func):
        task_name = name or func.__name__
        task_desc = description or func.__doc__ or ""
        
        # Rejestracja funkcji w globalnym rejestrze
        REGISTRY[func.__name__] = {
            "name": task_name,
            "description": task_desc,
            "function": func,
            "signature": inspect.signature(func),
            "validate_input": validate_input,
            "validate_output": validate_output,
        }
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            task_id = f"{func.__name__}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
            logger.info(f"Rozpoczęcie zadania: {task_name}")
            
            # Zapisanie informacji o rozpoczęciu zadania
            task_info = {
                "task_id": task_id,
                "name": task_name,
                "start_time": datetime.now().isoformat(),
                "status": FlowStatus.RUNNING,
                "args": str(args),
                "kwargs": str(kwargs),
            }
            
            # Walidacja danych wejściowych
            if validate_input:
                try:
                    validate_input(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Błąd walidacji danych wejściowych: {str(e)}")
                    task_info["status"] = FlowStatus.FAILED
                    task_info["error"] = str(e)
                    task_info["end_time"] = datetime.now().isoformat()
                    task_info["duration"] = time.time() - start_time
                    FLOW_HISTORY.append(task_info)
                    raise ValueError(f"Błąd walidacji danych wejściowych: {str(e)}")
            
            # Wykonanie funkcji
            try:
                result = func(*args, **kwargs)
                
                # Walidacja danych wyjściowych
                if validate_output:
                    try:
                        validate_output(result)
                    except Exception as e:
                        logger.error(f"Błąd walidacji danych wyjściowych: {str(e)}")
                        task_info["status"] = FlowStatus.FAILED
                        task_info["error"] = str(e)
                        task_info["end_time"] = datetime.now().isoformat()
                        task_info["duration"] = time.time() - start_time
                        FLOW_HISTORY.append(task_info)
                        raise ValueError(f"Błąd walidacji danych wyjściowych: {str(e)}")
                
                # Zapisanie informacji o zakończeniu zadania
                task_info["status"] = FlowStatus.COMPLETED
                task_info["end_time"] = datetime.now().isoformat()
                task_info["duration"] = time.time() - start_time
                logger.info(f"Zakończenie zadania: {task_name} (czas: {task_info['duration']:.2f}s)")
                FLOW_HISTORY.append(task_info)
                return result
            except Exception as e:
                # Zapisanie informacji o błędzie
                error_msg = str(e)
                error_trace = traceback.format_exc()
                logger.error(f"Błąd w zadaniu {task_name}: {error_msg}\n{error_trace}")
                task_info["status"] = FlowStatus.FAILED
                task_info["error"] = error_msg
                task_info["traceback"] = error_trace
                task_info["end_time"] = datetime.now().isoformat()
                task_info["duration"] = time.time() - start_time
                FLOW_HISTORY.append(task_info)
                raise
        
        return wrapper
    
    return decorator

def flow(name: Optional[str] = None, description: Optional[str] = None):
    """
    Dekorator do definiowania przepływu.
    
    Args:
        name: Opcjonalna nazwa przepływu (domyślnie: nazwa funkcji)
        description: Opcjonalny opis przepływu
    """
    def decorator(func):
        flow_name = name or func.__name__
        flow_desc = description or func.__doc__ or ""
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            flow_id = f"{flow_name}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
            start_time = time.time()
            logger.info(f"Rozpoczęcie przepływu: {flow_name}")
            
            # Zapisanie informacji o rozpoczęciu przepływu
            flow_info = {
                "flow_id": flow_id,
                "name": flow_name,
                "description": flow_desc,
                "start_time": datetime.now().isoformat(),
                "status": FlowStatus.RUNNING,
                "tasks": [],
            }
            
            # Wykonanie przepływu
            try:
                # Zapisanie stanu przed wykonaniem
                initial_history_len = len(FLOW_HISTORY)
                
                # Wykonanie funkcji przepływu
                result = func(*args, **kwargs)
                
                # Zebranie informacji o zadaniach wykonanych w przepływie
                tasks = FLOW_HISTORY[initial_history_len:]
                flow_info["tasks"] = [task["task_id"] for task in tasks]
                
                # Zapisanie informacji o zakończeniu przepływu
                flow_info["status"] = FlowStatus.COMPLETED
                flow_info["end_time"] = datetime.now().isoformat()
                flow_info["duration"] = time.time() - start_time
                logger.info(f"Zakończenie przepływu: {flow_name} (czas: {flow_info['duration']:.2f}s)")
                
                # Zapisanie przepływu do pliku
                save_flow(flow_info)
                
                return result
            except Exception as e:
                # Zapisanie informacji o błędzie
                error_msg = str(e)
                error_trace = traceback.format_exc()
                logger.error(f"Błąd w przepływie {flow_name}: {error_msg}\n{error_trace}")
                flow_info["status"] = FlowStatus.FAILED
                flow_info["error"] = error_msg
                flow_info["traceback"] = error_trace
                flow_info["end_time"] = datetime.now().isoformat()
                flow_info["duration"] = time.time() - start_time
                
                # Zapisanie przepływu do pliku
                save_flow(flow_info)
                
                raise
        
        return wrapper
    
    return decorator

def save_flow(flow_info: Dict[str, Any]):
    """
    Zapisuje informacje o przepływie do pliku JSON.
    
    Args:
        flow_info: Informacje o przepływie
    """
    flow_id = flow_info["flow_id"]
    flow_file = os.path.join(FLOW_DIR, f"{flow_id}.json")
    
    with open(flow_file, "w") as f:
        json.dump(flow_info, f, indent=2)

def load_flow(flow_id: str) -> Dict[str, Any]:
    """
    Wczytuje informacje o przepływie z pliku JSON.
    
    Args:
        flow_id: Identyfikator przepływu
    
    Returns:
        Informacje o przepływie
    """
    flow_file = os.path.join(FLOW_DIR, f"{flow_id}.json")
    
    with open(flow_file, "r") as f:
        return json.load(f)

def list_flows() -> List[Dict[str, Any]]:
    """
    Zwraca listę wszystkich przepływów.
    
    Returns:
        Lista przepływów
    """
    flows = []
    
    for flow_file in os.listdir(FLOW_DIR):
        if flow_file.endswith(".json"):
            flow_path = os.path.join(FLOW_DIR, flow_file)
            with open(flow_path, "r") as f:
                flow_info = json.load(f)
                flows.append(flow_info)
    
    # Sortowanie według czasu rozpoczęcia (od najnowszego)
    flows.sort(key=lambda x: x.get("start_time", ""), reverse=True)
    
    return flows

def parse_dsl(dsl_text: str) -> Dict[str, Any]:
    """
    Parsuje tekst DSL do struktury przepływu.
    
    Przykład DSL:
    ```
    flow EmailProcessing:
        description: "Przetwarzanie e-maili"
        fetch_emails -> classify_emails
        classify_emails -> [urgent_emails, regular_emails]
        urgent_emails -> send_urgent_response
        regular_emails -> send_regular_response
    ```
    
    Args:
        dsl_text: Tekst DSL
    
    Returns:
        Struktura przepływu
    """
    lines = dsl_text.strip().split("\n")
    flow_info = {}
    connections = []
    
    # Parsowanie nagłówka przepływu
    flow_match = re.match(r"flow\s+(\w+):", lines[0])
    if flow_match:
        flow_info["name"] = flow_match.group(1)
    else:
        raise ValueError("Nieprawidłowy format DSL: brak definicji przepływu")
    
    # Parsowanie pozostałych linii
    for line in lines[1:]:
        line = line.strip()
        
        # Pominięcie pustych linii
        if not line:
            continue
        
        # Parsowanie opisu
        desc_match = re.match(r'\s*description:\s*"([^"]*)"', line)
        if desc_match:
            flow_info["description"] = desc_match.group(1)
            continue
        
        # Parsowanie połączeń
        conn_match = re.match(r'\s*(\w+)\s*->\s*(\[?[\w\s,]+\]?)', line)
        if conn_match:
            source = conn_match.group(1)
            targets_str = conn_match.group(2)
            
            # Parsowanie wielu celów
            if targets_str.startswith("[") and targets_str.endswith("]"):
                targets = [t.strip() for t in targets_str[1:-1].split(",")]
            else:
                targets = [targets_str.strip()]
            
            for target in targets:
                connections.append({"source": source, "target": target})
        else:
            raise ValueError(f"Nieprawidłowy format linii DSL: {line}")
    
    flow_info["connections"] = connections
    return flow_info

def run_flow_from_dsl(dsl_text: str, input_data: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Uruchamia przepływ zdefiniowany w DSL.
    
    Args:
        dsl_text: Tekst DSL
        input_data: Dane wejściowe dla przepływu
    
    Returns:
        Wyniki przepływu
    """
    flow_def = parse_dsl(dsl_text)
    flow_name = flow_def["name"]
    connections = flow_def["connections"]
    
    # Tworzenie grafu przepływu
    graph = {}
    for conn in connections:
        source = conn["source"]
        target = conn["target"]
        
        if source not in graph:
            graph[source] = []
        
        graph[source].append(target)
    
    # Znajdowanie zadań początkowych (bez poprzedników)
    all_nodes = set()
    for conn in connections:
        all_nodes.add(conn["source"])
        all_nodes.add(conn["target"])
    
    targets = set()
    for conn in connections:
        targets.add(conn["target"])
    
    start_nodes = all_nodes - targets
    
    # Sprawdzenie, czy wszystkie zadania są zarejestrowane
    for node in all_nodes:
        if node not in REGISTRY:
            raise ValueError(f"Zadanie '{node}' nie jest zarejestrowane")
    
    # Uruchomienie przepływu
    @flow(name=flow_name, description=flow_def.get("description", ""))
    def execute_flow():
        results = {}
        node_outputs = {}
        
        # Inicjalizacja danych wejściowych
        if input_data:
            results.update(input_data)
        
        logger.info(f"Uruchamianie przepływu {flow_name} z danymi wejściowymi: {input_data}")
        logger.info(f"Zadania początkowe: {start_nodes}")
        
        # Uruchomienie zadań początkowych
        for node in start_nodes:
            func = REGISTRY[node]["function"]
            # Dopasowanie argumentów funkcji do dostępnych danych
            sig = inspect.signature(func)
            kwargs = {}
            
            for param_name in sig.parameters:
                if param_name in results:
                    kwargs[param_name] = results[param_name]
            
            logger.info(f"Uruchamianie zadania {node} z argumentami: {kwargs}")
            
            # Wykonanie funkcji
            result = func(**kwargs)
            node_outputs[node] = result
            results[node] = result
            logger.info(f"Zadanie {node} zakończone, wynik: {result}")
        
        # Uruchomienie pozostałych zadań w odpowiedniej kolejności
        visited = set(start_nodes)
        while len(visited) < len(all_nodes):
            for node in all_nodes - visited:
                # Sprawdzenie, czy wszystkie poprzedniki zostały odwiedzone
                predecessors = set()
                for conn in connections:
                    if conn["target"] == node:
                        predecessors.add(conn["source"])
                
                if predecessors.issubset(visited):
                    func = REGISTRY[node]["function"]
                    # Dopasowanie argumentów funkcji do dostępnych danych
                    sig = inspect.signature(func)
                    kwargs = {}
                    
                    # Znajdowanie danych wejściowych na podstawie połączeń
                    logger.info(f"Przygotowanie argumentów dla zadania {node}")
                    logger.info(f"Parametry funkcji {node}: {list(sig.parameters.keys())}")
                    
                    # Sprawdzenie bezpośrednich połączeń
                    direct_inputs = []
                    for conn in connections:
                        if conn["target"] == node:
                            source = conn["source"]
                            direct_inputs.append(source)
                            logger.info(f"Bezpośrednie połączenie: {source} -> {node}")
                    
                    # Dla każdego parametru funkcji, spróbuj znaleźć odpowiednie dane
                    for param_name in sig.parameters:
                        # Sprawdź, czy parametr jest bezpośrednio połączony z wynikiem innego zadania
                        for source in direct_inputs:
                            if source in node_outputs:
                                # Jeśli nazwa parametru odpowiada nazwie zadania
                                if param_name == source:
                                    kwargs[param_name] = node_outputs[source]
                                    logger.info(f"Przypisano {source} -> {param_name}")
                                    break
                                # Jeśli nazwa parametru to liczba mnoga nazwy zadania
                                elif param_name == source + "s" and isinstance(node_outputs[source], list):
                                    kwargs[param_name] = node_outputs[source]
                                    logger.info(f"Przypisano {source} -> {param_name} (liczba mnoga)")
                                    break
                                # Specjalne przypadki dla typowych nazw parametrów
                                elif param_name == "emails" and source == "fetch_emails":
                                    kwargs[param_name] = node_outputs[source]
                                    logger.info(f"Przypisano {source} -> {param_name} (specjalny przypadek)")
                                    break
                                # Specjalne przypadki dla funkcji send_responses
                                elif node == "send_responses":
                                    if param_name == "urgent_responses" and source == "process_urgent_emails":
                                        kwargs[param_name] = node_outputs[source]
                                        logger.info(f"Przypisano {source} -> {param_name} (specjalny przypadek)")
                                        break
                                    elif param_name == "attachment_responses" and source == "process_emails_with_attachments":
                                        kwargs[param_name] = node_outputs[source]
                                        logger.info(f"Przypisano {source} -> {param_name} (specjalny przypadek)")
                                        break
                                    elif param_name == "regular_responses" and source == "process_regular_emails":
                                        kwargs[param_name] = node_outputs[source]
                                        logger.info(f"Przypisano {source} -> {param_name} (specjalny przypadek)")
                                        break
                        
                        # Jeśli parametr nie został jeszcze przypisany, spróbuj znaleźć go w wynikach
                        if param_name not in kwargs:
                            # Sprawdź, czy parametr jest kluczem w słowniku zwracanych przez inne zadanie
                            for source in direct_inputs:
                                if source in node_outputs and isinstance(node_outputs[source], dict):
                                    if param_name in node_outputs[source]:
                                        kwargs[param_name] = node_outputs[source][param_name]
                                        logger.info(f"Przypisano {source}.{param_name} -> {param_name}")
                                        break
                        
                        # Jeśli parametr nadal nie został przypisany, spróbuj znaleźć go w danych wejściowych
                        if param_name not in kwargs and param_name in results:
                            kwargs[param_name] = results[param_name]
                            logger.info(f"Przypisano z danych wejściowych: {param_name}")
                    
                    logger.info(f"Uruchamianie zadania {node} z argumentami: {kwargs}")
                    
                    # Wykonanie funkcji
                    result = func(**kwargs)
                    node_outputs[node] = result
                    results[node] = result
                    logger.info(f"Zadanie {node} zakończone, wynik: {result}")
                    visited.add(node)
        
        return results
    
    # Wykonanie przepływu
    return execute_flow()

def save_dsl(dsl_text: str, filename: str):
    """
    Zapisuje tekst DSL do pliku.
    
    Args:
        dsl_text: Tekst DSL
        filename: Nazwa pliku
    """
    dsl_dir = os.path.join(os.path.dirname(__file__), "dsl_definitions")
    os.makedirs(dsl_dir, exist_ok=True)
    
    with open(os.path.join(dsl_dir, filename), "w") as f:
        f.write(dsl_text)

def load_dsl(filename: str) -> str:
    """
    Wczytuje tekst DSL z pliku.
    
    Args:
        filename: Nazwa pliku
    
    Returns:
        Tekst DSL
    """
    dsl_dir = os.path.join(os.path.dirname(__file__), "dsl_definitions")
    
    # Check if the filename already contains the dsl_definitions path
    if os.path.dirname(filename) == "dsl_definitions" or filename.startswith("dsl_definitions/"):
        file_path = os.path.join(os.path.dirname(__file__), filename)
    else:
        file_path = os.path.join(dsl_dir, filename)
    
    with open(file_path, "r") as f:
        return f.read()

def list_dsl_files() -> List[str]:
    """
    Zwraca listę wszystkich plików DSL.
    
    Returns:
        Lista plików DSL
    """
    dsl_dir = os.path.join(os.path.dirname(__file__), "dsl_definitions")
    os.makedirs(dsl_dir, exist_ok=True)
    
    return [f for f in os.listdir(dsl_dir) if not f.startswith(".")]

# Przykład użycia:
if __name__ == "__main__":
    # Przykładowe zadania
    @task(name="Pobieranie e-maili", description="Pobiera e-maile z serwera IMAP")
    def fetch_emails(server: str, username: str, password: str) -> List[Dict[str, Any]]:
        """Pobiera e-maile z serwera IMAP."""
        logger.info(f"Pobieranie e-maili z {server} dla użytkownika {username}")
        # Symulacja pobierania e-maili
        time.sleep(1)
        return [
            {"id": "1", "subject": "Ważna wiadomość", "body": "Treść ważnej wiadomości", "urgent": True},
            {"id": "2", "subject": "Zwykła wiadomość", "body": "Treść zwykłej wiadomości", "urgent": False},
        ]
    
    @task(name="Klasyfikacja e-maili", description="Klasyfikuje e-maile na pilne i zwykłe")
    def classify_emails(emails: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Klasyfikuje e-maile na pilne i zwykłe."""
        logger.info(f"Klasyfikacja {len(emails)} e-maili")
        # Symulacja klasyfikacji
        time.sleep(0.5)
        urgent = [email for email in emails if email.get("urgent", False)]
        regular = [email for email in emails if not email.get("urgent", False)]
        return {"urgent_emails": urgent, "regular_emails": regular}
    
    @task(name="Przetwarzanie pilnych e-maili", description="Przetwarza pilne e-maile")
    def process_urgent_emails(urgent_emails: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Przetwarza pilne e-maile."""
        logger.info(f"Przetwarzanie {len(urgent_emails)} pilnych e-maili")
        # Symulacja przetwarzania
        time.sleep(0.5)
        return [{"id": email["id"], "response": f"Pilna odpowiedź na: {email['subject']}"} for email in urgent_emails]
    
    @task(name="Przetwarzanie zwykłych e-maili", description="Przetwarza zwykłe e-maile")
    def process_regular_emails(regular_emails: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Przetwarza zwykłe e-maile."""
        logger.info(f"Przetwarzanie {len(regular_emails)} zwykłych e-maili")
        # Symulacja przetwarzania
        time.sleep(0.5)
        return [{"id": email["id"], "response": f"Zwykła odpowiedź na: {email['subject']}"} for email in regular_emails]
    
    # Przykładowy przepływ DSL
    dsl_text = """
    flow EmailProcessing:
        description: "Przetwarzanie e-maili"
        fetch_emails -> classify_emails
        classify_emails -> [process_urgent_emails, process_regular_emails]
    """
    
    # Zapisanie DSL do pliku
    save_dsl(dsl_text, "email_processing.dsl")
    
    # Uruchomienie przepływu
    input_data = {
        "server": "imap.example.com",
        "username": "test@example.com",
        "password": "password123",
    }
    
    results = run_flow_from_dsl(dsl_text, input_data)
    print("Wyniki przepływu:", results)
    
    # Wyświetlenie historii przepływów
    flows = list_flows()
    print(f"Liczba wykonanych przepływów: {len(flows)}")
    for flow_info in flows:
        print(f"Przepływ: {flow_info['name']} (status: {flow_info['status']})")
