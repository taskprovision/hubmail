#!/usr/bin/env python3
"""
Taskinity - prosty framework do definiowania przepływów za pomocą dekoratorów i DSL.
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
logger = logging.getLogger("taskinity")

# Katalog na logi i dane przepływów
FLOW_DIR = os.getenv("FLOW_DIR", os.path.join(os.path.dirname(__file__), "..", "flows"))
LOG_DIR = os.getenv("LOG_DIR", os.path.join(os.path.dirname(__file__), "..", "logs"))
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
                
                task_info["status"] = FlowStatus.COMPLETED
                task_info["end_time"] = datetime.now().isoformat()
                task_info["duration"] = time.time() - start_time
                FLOW_HISTORY.append(task_info)
                
                logger.info(f"Zakończenie zadania: {task_name} (czas: {task_info['duration']:.2f}s)")
                return result
            except Exception as e:
                logger.error(f"Błąd wykonania zadania: {task_name} - {str(e)}")
                logger.error(traceback.format_exc())
                
                task_info["status"] = FlowStatus.FAILED
                task_info["error"] = str(e)
                task_info["traceback"] = traceback.format_exc()
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
            
            try:
                result = func(*args, **kwargs)
                flow_info["status"] = FlowStatus.COMPLETED
                flow_info["end_time"] = datetime.now().isoformat()
                flow_info["result"] = result
                save_flow(flow_info)
                
                logger.info(f"Zakończenie przepływu: {flow_name}")
                return result
            except Exception as e:
                logger.error(f"Błąd wykonania przepływu: {flow_name} - {str(e)}")
                logger.error(traceback.format_exc())
                
                flow_info["status"] = FlowStatus.FAILED
                flow_info["error"] = str(e)
                flow_info["traceback"] = traceback.format_exc()
                flow_info["end_time"] = datetime.now().isoformat()
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
    with open(os.path.join(FLOW_DIR, f"{flow_id}.json"), "w") as f:
        json.dump(flow_info, f, indent=2)

def load_flow(flow_id: str) -> Dict[str, Any]:
    """
    Wczytuje informacje o przepływie z pliku JSON.
    
    Args:
        flow_id: Identyfikator przepływu
    
    Returns:
        Informacje o przepływie
    """
    with open(os.path.join(FLOW_DIR, f"{flow_id}.json"), "r") as f:
        return json.load(f)

def list_flows() -> List[Dict[str, Any]]:
    """
    Zwraca listę wszystkich przepływów.
    
    Returns:
        Lista przepływów
    """
    flows = []
    for filename in os.listdir(FLOW_DIR):
        if filename.endswith(".json"):
            try:
                with open(os.path.join(FLOW_DIR, filename), "r") as f:
                    flow_info = json.load(f)
                    flows.append(flow_info)
            except Exception as e:
                logger.error(f"Błąd wczytywania przepływu {filename}: {str(e)}")
    
    # Sortowanie po czasie rozpoczęcia (od najnowszych)
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
    flow_match = re.search(r"flow\s+(\w+):", dsl_text)
    if not flow_match:
        raise ValueError("Nieprawidłowy format DSL: brak definicji przepływu")
    
    flow_name = flow_match.group(1)
    
    # Wyszukanie opisu
    desc_match = re.search(r"description:\s*\"([^\"]+)\"", dsl_text)
    flow_description = desc_match.group(1) if desc_match else ""
    
    # Wyszukanie połączeń
    connections = []
    for line in dsl_text.split("\n"):
        line = line.strip()
        if "->" in line:
            parts = line.split("->")
            if len(parts) != 2:
                continue
            
            source = parts[0].strip()
            targets_str = parts[1].strip()
            
            # Sprawdzenie, czy mamy listę celów
            if targets_str.startswith("[") and targets_str.endswith("]"):
                targets = [t.strip() for t in targets_str[1:-1].split(",")]
            else:
                targets = [targets_str]
            
            for target in targets:
                connections.append((source, target))
    
    return {
        "name": flow_name,
        "description": flow_description,
        "connections": connections,
    }

def run_flow_from_dsl(dsl_text: str, input_data: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Uruchamia przepływ zdefiniowany w DSL.
    
    Args:
        dsl_text: Tekst DSL
        input_data: Dane wejściowe dla przepływu
    
    Returns:
        Wyniki przepływu
    """
    if input_data is None:
        input_data = {}
    
    flow_structure = parse_dsl(dsl_text)
    flow_name = flow_structure["name"]
    flow_description = flow_structure["description"]
    connections = flow_structure["connections"]
    
    # Budowa grafu zależności
    graph = {}
    for source, target in connections:
        if source not in graph:
            graph[source] = []
        graph[source].append(target)
    
    # Sprawdzenie, czy wszystkie zadania są zarejestrowane
    all_tasks = set()
    for source, target in connections:
        all_tasks.add(source)
        all_tasks.add(target)
    
    for task_name in all_tasks:
        if task_name not in REGISTRY:
            raise ValueError(f"Zadanie '{task_name}' nie jest zarejestrowane")
    
    # Znalezienie zadań początkowych (nie mają poprzedników)
    has_predecessor = {task: False for task in all_tasks}
    for source, target in connections:
        has_predecessor[target] = True
    
    start_tasks = [task for task, has_pred in has_predecessor.items() if not has_pred]
    
    # Utworzenie identyfikatora przepływu
    flow_id = f"{flow_name}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    
    # Zapisanie informacji o rozpoczęciu przepływu
    flow_info = {
        "flow_id": flow_id,
        "name": flow_name,
        "description": flow_description,
        "start_time": datetime.now().isoformat(),
        "status": FlowStatus.RUNNING,
        "tasks": [],
        "connections": connections,
    }
    
    logger.info(f"Rozpoczęcie przepływu: {flow_name}")
    
    # Funkcja do wykonania przepływu
    def execute_flow():
        # Słownik wyników zadań
        results = {}
        
        # Kolejka zadań do wykonania
        task_queue = list(start_tasks)
        
        # Zbiór wykonanych zadań
        completed_tasks = set()
        
        # Wykonanie zadań
        while task_queue:
            current_task = task_queue.pop(0)
            
            # Sprawdzenie, czy wszystkie poprzedniki zostały wykonane
            predecessors = []
            for source, target in connections:
                if target == current_task:
                    predecessors.append(source)
            
            if not all(pred in completed_tasks for pred in predecessors):
                task_queue.append(current_task)
                continue
            
            # Przygotowanie danych wejściowych dla zadania
            task_input = {}
            
            # Jeśli zadanie ma poprzedników, użyj ich wyników
            if predecessors:
                for pred in predecessors:
                    # Jeśli poprzednik zwrócił słownik, użyj go jako danych wejściowych
                    if isinstance(results[pred], dict):
                        task_input.update(results[pred])
                    else:
                        # W przeciwnym razie użyj wyniku jako pojedynczej wartości
                        task_input = results[pred]
            else:
                # Jeśli zadanie nie ma poprzedników, użyj danych wejściowych przepływu
                task_input = input_data
            
            # Wykonanie zadania
            task_func = REGISTRY[current_task]["function"]
            
            try:
                # Sprawdzenie, czy zadanie przyjmuje dane wejściowe jako słownik czy jako argumenty
                sig = inspect.signature(task_func)
                
                if len(sig.parameters) == 1 and isinstance(task_input, dict):
                    # Zadanie przyjmuje jeden argument (słownik)
                    task_result = task_func(task_input)
                elif isinstance(task_input, dict):
                    # Zadanie przyjmuje wiele argumentów
                    task_result = task_func(**task_input)
                else:
                    # Zadanie przyjmuje jeden argument (nie słownik)
                    task_result = task_func(task_input)
                
                # Zapisanie wyniku zadania
                results[current_task] = task_result
                completed_tasks.add(current_task)
                
                # Dodanie następników do kolejki
                if current_task in graph:
                    for next_task in graph[current_task]:
                        if next_task not in completed_tasks and next_task not in task_queue:
                            task_queue.append(next_task)
            
            except Exception as e:
                logger.error(f"Błąd wykonania zadania {current_task}: {str(e)}")
                logger.error(traceback.format_exc())
                
                # Aktualizacja informacji o przepływie
                flow_info["status"] = FlowStatus.FAILED
                flow_info["error"] = str(e)
                flow_info["traceback"] = traceback.format_exc()
                flow_info["end_time"] = datetime.now().isoformat()
                save_flow(flow_info)
                
                raise
        
        # Aktualizacja informacji o przepływie
        flow_info["status"] = FlowStatus.COMPLETED
        flow_info["end_time"] = datetime.now().isoformat()
        flow_info["results"] = results
        save_flow(flow_info)
        
        logger.info(f"Zakończenie przepływu: {flow_name}")
        
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
    dsl_dir = os.path.join(os.path.dirname(__file__), "..", "dsl_definitions")
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
    # Sprawdzenie, czy podana ścieżka jest bezwzględna
    if os.path.isabs(filename):
        if os.path.exists(filename):
            with open(filename, "r") as f:
                return f.read()
    else:
        # Sprawdzenie w katalogu dsl_definitions
        dsl_dir = os.path.join(os.path.dirname(__file__), "..", "dsl_definitions")
        dsl_path = os.path.join(dsl_dir, filename)
        
        if os.path.exists(dsl_path):
            with open(dsl_path, "r") as f:
                return f.read()
    
    raise FileNotFoundError(f"Nie znaleziono pliku DSL: {filename}")

def list_dsl_files() -> List[str]:
    """
    Zwraca listę wszystkich plików DSL.
    
    Returns:
        Lista plików DSL
    """
    dsl_dir = os.path.join(os.path.dirname(__file__), "..", "dsl_definitions")
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
