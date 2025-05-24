#!/usr/bin/env python3
"""
Moduł do równoległego wykonania zadań w Taskinity.
Umożliwia równoległe wykonanie niezależnych zadań w przepływie.
"""
import os
import json
import time
import logging
import threading
import multiprocessing
from queue import Queue
from typing import Dict, List, Any, Optional, Callable, Set, Tuple
from pathlib import Path
from datetime import datetime

# Konfiguracja loggera
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("taskinity.parallel_executor")

class TaskNode:
    """Reprezentacja zadania w grafie przepływu."""
    def __init__(self, name: str, func: Callable, **kwargs):
        self.name = name
        self.func = func
        self.kwargs = kwargs
        self.dependencies = set()  # Zadania, od których zależy to zadanie
        self.dependents = set()    # Zadania, które zależą od tego zadania
        self.result = None
        self.status = "PENDING"    # PENDING, RUNNING, COMPLETED, FAILED
        self.start_time = None
        self.end_time = None
        self.duration = None
        self.error = None

    def add_dependency(self, task: 'TaskNode'):
        """Dodaje zależność od innego zadania."""
        self.dependencies.add(task)
        task.dependents.add(self)

    def can_execute(self) -> bool:
        """Sprawdza, czy zadanie może być wykonane (wszystkie zależności zakończone)."""
        return all(dep.status == "COMPLETED" for dep in self.dependencies)

    def execute(self, flow_context: Dict[str, Any]) -> Any:
        """Wykonuje zadanie."""
        self.status = "RUNNING"
        self.start_time = datetime.now()
        
        try:
            # Przygotowanie argumentów
            kwargs = self.kwargs.copy()
            
            # Dodanie wyników z zależności
            for dep in self.dependencies:
                if dep.name in flow_context:
                    kwargs[dep.name] = flow_context[dep.name]
            
            # Wykonanie funkcji
            self.result = self.func(**kwargs)
            self.status = "COMPLETED"
            return self.result
        except Exception as e:
            self.status = "FAILED"
            self.error = str(e)
            logger.error(f"Błąd w zadaniu {self.name}: {str(e)}")
            raise
        finally:
            self.end_time = datetime.now()
            self.duration = (self.end_time - self.start_time).total_seconds()


class ParallelFlowExecutor:
    """Wykonawca przepływów z równoległym wykonaniem niezależnych zadań."""
    def __init__(self, max_workers: int = None):
        """
        Inicjalizuje wykonawcę przepływów.
        
        Args:
            max_workers: Maksymalna liczba równoległych zadań. Domyślnie liczba rdzeni CPU.
        """
        self.max_workers = max_workers or multiprocessing.cpu_count()
        self.tasks = {}  # name -> TaskNode
        self.flow_context = {}
        self.execution_log = []
        self.flow_id = None
        self.flow_name = None
        self.flow_start_time = None
        self.flow_end_time = None
        self.logs_dir = Path(__file__).parent.parent / "logs"
        self.flows_dir = Path(__file__).parent.parent / "flows"
        
        # Upewniamy się, że katalogi istnieją
        os.makedirs(self.logs_dir, exist_ok=True)
        os.makedirs(self.flows_dir, exist_ok=True)

    def add_task(self, name: str, func: Callable, **kwargs) -> TaskNode:
        """
        Dodaje zadanie do przepływu.
        
        Args:
            name: Nazwa zadania
            func: Funkcja do wykonania
            **kwargs: Argumenty dla funkcji
            
        Returns:
            Utworzony obiekt TaskNode
        """
        task = TaskNode(name, func, **kwargs)
        self.tasks[name] = task
        return task

    def add_dependency(self, source_name: str, target_name: str):
        """
        Dodaje zależność między zadaniami.
        
        Args:
            source_name: Nazwa zadania źródłowego
            target_name: Nazwa zadania docelowego
        """
        if source_name not in self.tasks:
            raise ValueError(f"Zadanie źródłowe '{source_name}' nie istnieje")
        if target_name not in self.tasks:
            raise ValueError(f"Zadanie docelowe '{target_name}' nie istnieje")
        
        self.tasks[target_name].add_dependency(self.tasks[source_name])

    def _worker(self, task_queue: Queue, result_queue: Queue, flow_context: Dict[str, Any]):
        """
        Funkcja wykonująca zadania z kolejki.
        
        Args:
            task_queue: Kolejka zadań do wykonania
            result_queue: Kolejka wyników
            flow_context: Kontekst przepływu z wynikami zadań
        """
        while True:
            task = task_queue.get()
            if task is None:  # Sygnał zakończenia
                task_queue.task_done()
                break
            
            try:
                result = task.execute(flow_context)
                result_queue.put((task.name, result, None))  # (nazwa, wynik, błąd)
            except Exception as e:
                result_queue.put((task.name, None, str(e)))  # (nazwa, wynik, błąd)
            finally:
                task_queue.task_done()

    def _find_ready_tasks(self) -> List[TaskNode]:
        """Znajduje zadania gotowe do wykonania."""
        return [task for task in self.tasks.values() 
                if task.status == "PENDING" and task.can_execute()]

    def execute_flow(self, flow_name: str, input_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Wykonuje przepływ z równoległym wykonaniem niezależnych zadań.
        
        Args:
            flow_name: Nazwa przepływu
            input_data: Dane wejściowe dla przepływu
            
        Returns:
            Wyniki przepływu
        """
        if input_data is None:
            input_data = {}
        
        self.flow_name = flow_name
        self.flow_id = f"{flow_name}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        self.flow_start_time = datetime.now()
        self.flow_context = input_data.copy()
        
        # Konfiguracja logowania do pliku
        log_file = self.logs_dir / f"{self.flow_id}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        logger.addHandler(file_handler)
        
        logger.info(f"Rozpoczęcie przepływu: {flow_name}")
        logger.info(f"Dane wejściowe: {input_data}")
        
        try:
            # Kolejki dla zadań i wyników
            task_queue = Queue()
            result_queue = Queue()
            
            # Uruchomienie wątków roboczych
            workers = []
            for _ in range(min(self.max_workers, len(self.tasks))):
                worker = threading.Thread(
                    target=self._worker,
                    args=(task_queue, result_queue, self.flow_context)
                )
                worker.daemon = True
                worker.start()
                workers.append(worker)
            
            # Licznik zadań do wykonania
            tasks_to_complete = len(self.tasks)
            
            # Dodanie początkowych zadań do kolejki
            ready_tasks = self._find_ready_tasks()
            for task in ready_tasks:
                task_queue.put(task)
            
            # Przetwarzanie wyników i dodawanie nowych zadań
            while tasks_to_complete > 0:
                task_name, result, error = result_queue.get()
                tasks_to_complete -= 1
                
                if error:
                    # Obsługa błędu
                    task = self.tasks[task_name]
                    task.status = "FAILED"
                    task.error = error
                    logger.error(f"Zadanie {task_name} zakończone błędem: {error}")
                    
                    # Oznaczenie zależnych zadań jako pominiętych
                    for dependent in task.dependents:
                        dependent.status = "SKIPPED"
                        tasks_to_complete -= 1
                        logger.info(f"Zadanie {dependent.name} pominięte z powodu błędu w zależności")
                else:
                    # Zapisanie wyniku
                    self.flow_context[task_name] = result
                    logger.info(f"Zadanie {task_name} zakończone pomyślnie")
                    
                    # Sprawdzenie, czy są nowe zadania gotowe do wykonania
                    ready_tasks = self._find_ready_tasks()
                    for task in ready_tasks:
                        task_queue.put(task)
                        tasks_to_complete += 1
            
            # Zakończenie wątków roboczych
            for _ in range(len(workers)):
                task_queue.put(None)
            
            # Oczekiwanie na zakończenie wątków
            for worker in workers:
                worker.join()
            
            self.flow_end_time = datetime.now()
            flow_duration = (self.flow_end_time - self.flow_start_time).total_seconds()
            logger.info(f"Przepływ {flow_name} zakończony pomyślnie (czas: {flow_duration:.2f}s)")
            
            # Sprawdzenie, czy wszystkie zadania zostały wykonane
            all_completed = all(task.status == "COMPLETED" for task in self.tasks.values())
            flow_status = "COMPLETED" if all_completed else "PARTIALLY_COMPLETED"
            
            # Zapisanie historii przepływu
            flow_history = {
                "flow_id": self.flow_id,
                "name": flow_name,
                "status": flow_status,
                "start_time": self.flow_start_time.isoformat(),
                "end_time": self.flow_end_time.isoformat(),
                "duration": flow_duration,
                "tasks": [
                    {
                        "name": task.name,
                        "status": task.status,
                        "start_time": task.start_time.isoformat() if task.start_time else None,
                        "end_time": task.end_time.isoformat() if task.end_time else None,
                        "duration": task.duration
                    }
                    for task in self.tasks.values()
                ]
            }
            
            # Zapisanie historii przepływu do pliku
            flow_file = self.flows_dir / f"{self.flow_id}.json"
            with open(flow_file, "w") as f:
                json.dump(flow_history, f, indent=4)
            
            return self.flow_context
        
        except Exception as e:
            self.flow_end_time = datetime.now()
            flow_duration = (self.flow_end_time - self.flow_start_time).total_seconds()
            logger.error(f"Błąd w przepływie {flow_name}: {str(e)}")
            
            # Zapisz historię przepływu z błędem
            flow_history = {
                "flow_id": self.flow_id,
                "name": self.flow_name,
                "status": "FAILED",
                "start_time": self.flow_start_time.isoformat(),
                "end_time": self.flow_end_time.isoformat(),
                "duration": flow_duration,
                "error": str(e),
                "tasks": [
                    {
                        "name": task.name,
                        "status": task.status,
                        "start_time": task.start_time.isoformat() if task.start_time else None,
                        "end_time": task.end_time.isoformat() if task.end_time else None,
                        "duration": task.duration,
                        "error": task.error
                    }
                    for task in self.tasks.values()
                ]
            }
            
            # Zapisz historię przepływu do pliku
            flow_file = self.flows_dir / f"{self.flow_id}.json"
            with open(flow_file, "w") as f:
                json.dump(flow_history, f, indent=4)
            
            return {
                "flow_id": self.flow_id,
                "status": "FAILED",
                "error": str(e),
                "duration": flow_duration,
                "results": self.flow_context
            }
        finally:
            logger.removeHandler(file_handler)

def build_flow_from_dsl(dsl_definition: Dict[str, Any], task_registry: Dict[str, Callable]) -> ParallelFlowExecutor:
    """
    Buduje przepływ na podstawie definicji DSL.
    
    Args:
        dsl_definition: Definicja przepływu w formacie DSL
        task_registry: Rejestr zadań (nazwa -> funkcja)
        
    Returns:
        Obiekt ParallelFlowExecutor z zdefiniowanym przepływem
    """
    flow_name = dsl_definition.get("name", "UnknownFlow")
    executor = ParallelFlowExecutor()
    
    # Dodaj zadania
    tasks = set()
    connections = dsl_definition.get("connections", [])
    
    # Zbierz wszystkie unikalne nazwy zadań z połączeń
    for source, target in connections:
        tasks.add(source)
        tasks.add(target)
    
    # Dodaj zadania do wykonawcy
    for task_name in tasks:
        if task_name not in task_registry:
            raise ValueError(f"Zadanie '{task_name}' nie jest zarejestrowane")
        
        task_func = task_registry[task_name]["function"]
        executor.add_task(task_name, task_func)
    
    # Dodaj połączenia
    for source, target in connections:
        executor.add_dependency(source, target)
    
    return executor

def run_parallel_flow_from_dsl(dsl_text: str, input_data: Dict[str, Any] = None, max_workers: int = None) -> Dict[str, Any]:
    """
    Uruchamia przepływ z równoległym wykonaniem na podstawie definicji DSL.
    
    Args:
        dsl_text: Definicja przepływu w formacie DSL (tekst)
        input_data: Dane wejściowe dla przepływu
        max_workers: Maksymalna liczba równoległych zadań
        
    Returns:
        Wyniki przepływu
    """
    from taskinity.flow_dsl import parse_dsl, REGISTRY
    
    # Parsuj definicję DSL
    dsl_definition = parse_dsl(dsl_text)
    
    # Zbuduj i uruchom przepływ
    executor = build_flow_from_dsl(dsl_definition, REGISTRY)
    
    # Ustaw maksymalną liczbę wątków, jeśli podano
    if max_workers is not None:
        executor.max_workers = max_workers
    
    return executor.execute_flow(dsl_definition.get("name", "UnknownFlow"), input_data)

if __name__ == "__main__":
    # Przykład użycia
    from taskinity.flow_dsl import task
    
    @task()
    def task1(x: int, y: int):
        time.sleep(1)
        return x + y
    
    @task()
    def task2(x: int):
        time.sleep(2)
        return x * 2
    
    @task()
    def task3(task1, task2):
        time.sleep(1)
        return task1 + task2
    
    # Ręczne tworzenie przepływu
    executor = ParallelFlowExecutor()
    t1 = executor.add_task("task1", task1, x=5, y=3)
    t2 = executor.add_task("task2", task2, x=10)
    t3 = executor.add_task("task3", task3)
    
    t3.add_dependency(t1)
    t3.add_dependency(t2)
    
    result = executor.execute_flow("TestFlow")
    print(f"Wynik przepływu: {result}")
