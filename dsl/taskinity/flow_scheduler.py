#!/usr/bin/env python3
"""
Moduł do planowania wykonania przepływów w Taskinity.
Umożliwia zaplanowanie wykonania przepływów w określonych terminach.
"""
import os
import json
import time
import logging
import threading
import schedule
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta

# Import funkcji z Taskinity
from taskinity.flow_dsl import run_flow_from_dsl, load_dsl, parse_dsl

# Opcjonalny import równoległego wykonawcy
try:
    from taskinity.parallel_executor import run_parallel_flow_from_dsl
    PARALLEL_AVAILABLE = True
except ImportError:
    PARALLEL_AVAILABLE = False

# Opcjonalny import powiadomień
try:
    from taskinity.notification_service import notify_flow_status
    NOTIFICATIONS_AVAILABLE = True
except ImportError:
    NOTIFICATIONS_AVAILABLE = False

# Konfiguracja loggera
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("taskinity.flow_scheduler")

# Ścieżki do katalogów
BASE_DIR = Path(__file__).parent.parent
SCHEDULE_DIR = BASE_DIR / "schedules"
DSL_DIR = BASE_DIR / "dsl_definitions"

# Upewniamy się, że katalogi istnieją
os.makedirs(SCHEDULE_DIR, exist_ok=True)
os.makedirs(DSL_DIR, exist_ok=True)

# Globalna flaga do kontroli wątku planowania
scheduler_running = False
scheduler_thread = None

class FlowSchedule:
    """Klasa reprezentująca zaplanowane wykonanie przepływu."""
    def __init__(self, 
                 schedule_id: str,
                 dsl_path: str,
                 input_data: Optional[Dict[str, Any]] = None,
                 schedule_type: str = "interval",
                 interval_minutes: int = 60,
                 cron_expression: Optional[str] = None,
                 next_run: Optional[datetime] = None,
                 enabled: bool = True,
                 use_parallel: bool = False,
                 description: Optional[str] = None):
        """
        Inicjalizuje zaplanowane wykonanie przepływu.
        
        Args:
            schedule_id: Unikalny identyfikator harmonogramu
            dsl_path: Ścieżka do pliku DSL lub nazwa pliku w katalogu DSL_DIR
            input_data: Dane wejściowe dla przepływu
            schedule_type: Typ harmonogramu ('interval', 'daily', 'weekly', 'monthly', 'cron')
            interval_minutes: Interwał w minutach (dla typu 'interval')
            cron_expression: Wyrażenie cron (dla typu 'cron')
            next_run: Następne zaplanowane wykonanie
            enabled: Czy harmonogram jest aktywny
            use_parallel: Czy używać równoległego wykonania
            description: Opis harmonogramu
        """
        self.schedule_id = schedule_id
        self.dsl_path = dsl_path
        self.input_data = input_data or {}
        self.schedule_type = schedule_type
        self.interval_minutes = interval_minutes
        self.cron_expression = cron_expression
        self.next_run = next_run
        self.enabled = enabled
        self.use_parallel = use_parallel and PARALLEL_AVAILABLE
        self.description = description
        self.last_run = None
        self.last_status = None
        self.job = None  # Referencja do zadania w bibliotece schedule
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwertuje obiekt do słownika."""
        return {
            "schedule_id": self.schedule_id,
            "dsl_path": self.dsl_path,
            "input_data": self.input_data,
            "schedule_type": self.schedule_type,
            "interval_minutes": self.interval_minutes,
            "cron_expression": self.cron_expression,
            "next_run": self.next_run.isoformat() if self.next_run else None,
            "enabled": self.enabled,
            "use_parallel": self.use_parallel,
            "description": self.description,
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "last_status": self.last_status
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FlowSchedule':
        """Tworzy obiekt z słownika."""
        # Konwersja dat z formatu ISO
        next_run = None
        if data.get("next_run"):
            try:
                next_run = datetime.fromisoformat(data["next_run"])
            except ValueError:
                pass
        
        last_run = None
        if data.get("last_run"):
            try:
                last_run = datetime.fromisoformat(data["last_run"])
            except ValueError:
                pass
        
        # Tworzenie obiektu
        schedule = cls(
            schedule_id=data["schedule_id"],
            dsl_path=data["dsl_path"],
            input_data=data.get("input_data", {}),
            schedule_type=data.get("schedule_type", "interval"),
            interval_minutes=data.get("interval_minutes", 60),
            cron_expression=data.get("cron_expression"),
            next_run=next_run,
            enabled=data.get("enabled", True),
            use_parallel=data.get("use_parallel", False),
            description=data.get("description")
        )
        
        schedule.last_run = last_run
        schedule.last_status = data.get("last_status")
        
        return schedule
    
    def calculate_next_run(self) -> datetime:
        """Oblicza następny czas wykonania."""
        now = datetime.now()
        
        if self.schedule_type == "interval":
            self.next_run = now + timedelta(minutes=self.interval_minutes)
        
        elif self.schedule_type == "daily":
            # Format: "HH:MM"
            if isinstance(self.cron_expression, str) and ":" in self.cron_expression:
                hour, minute = map(int, self.cron_expression.split(":", 1))
                next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                if next_run <= now:
                    next_run += timedelta(days=1)
                self.next_run = next_run
        
        elif self.schedule_type == "weekly":
            # TODO: Implementacja harmonogramu tygodniowego
            self.next_run = now + timedelta(days=7)
        
        elif self.schedule_type == "monthly":
            # TODO: Implementacja harmonogramu miesięcznego
            self.next_run = now + timedelta(days=30)
        
        else:
            # Domyślnie: interwał 60 minut
            self.next_run = now + timedelta(minutes=60)
        
        return self.next_run
    
    def run(self) -> Dict[str, Any]:
        """Wykonuje zaplanowany przepływ."""
        self.last_run = datetime.now()
        
        try:
            logger.info(f"Uruchamianie przepływu: {self.schedule_id}")
            
            # Ładowanie DSL
            if os.path.isabs(self.dsl_path) and os.path.exists(self.dsl_path):
                dsl_file = self.dsl_path
            else:
                dsl_file = DSL_DIR / self.dsl_path
                if not os.path.exists(dsl_file):
                    raise FileNotFoundError(f"Nie znaleziono pliku DSL: {self.dsl_path}")
            
            dsl_content = load_dsl(str(dsl_file))
            
            # Przygotowanie danych wejściowych
            input_data = self.input_data.copy()
            
            # Dodanie informacji o harmonogramie
            input_data["_schedule"] = {
                "id": self.schedule_id,
                "type": self.schedule_type,
                "run_time": self.last_run.isoformat()
            }
            
            # Wykonanie przepływu
            if self.use_parallel and PARALLEL_AVAILABLE:
                logger.info(f"Uruchamianie przepływu {self.schedule_id} w trybie równoległym")
                result = run_parallel_flow_from_dsl(dsl_content, input_data)
            else:
                logger.info(f"Uruchamianie przepływu {self.schedule_id} w trybie sekwencyjnym")
                result = run_flow_from_dsl(dsl_content, input_data)
            
            # Aktualizacja statusu
            self.last_status = "SUCCESS"
            
            # Wysłanie powiadomienia
            if NOTIFICATIONS_AVAILABLE:
                notify_flow_status(
                    flow_id=self.schedule_id,
                    status="SUCCESS",
                    message=f"Przepływ {self.schedule_id} zakończony pomyślnie",
                    details={
                        "schedule_id": self.schedule_id,
                        "dsl_path": self.dsl_path,
                        "run_time": self.last_run.isoformat(),
                        "result": result
                    }
                )
            
            # Obliczenie następnego wykonania
            self.calculate_next_run()
            
            # Zapisanie zaktualizowanego harmonogramu
            save_schedule(self)
            
            return {
                "status": "SUCCESS",
                "schedule_id": self.schedule_id,
                "run_time": self.last_run.isoformat(),
                "next_run": self.next_run.isoformat() if self.next_run else None,
                "result": result
            }
        
        except Exception as e:
            logger.error(f"Błąd wykonania przepływu {self.schedule_id}: {str(e)}")
            
            # Aktualizacja statusu
            self.last_status = "ERROR"
            
            # Wysłanie powiadomienia
            if NOTIFICATIONS_AVAILABLE:
                notify_flow_status(
                    flow_id=self.schedule_id,
                    status="ERROR",
                    message=f"Błąd wykonania przepływu {self.schedule_id}: {str(e)}",
                    details={
                        "schedule_id": self.schedule_id,
                        "dsl_path": self.dsl_path,
                        "run_time": self.last_run.isoformat(),
                        "error": str(e)
                    }
                )
            
            # Obliczenie następnego wykonania
            self.calculate_next_run()
            
            # Zapisanie zaktualizowanego harmonogramu
            save_schedule(self)
            
            return {
                "status": "ERROR",
                "schedule_id": self.schedule_id,
                "run_time": self.last_run.isoformat(),
                "next_run": self.next_run.isoformat() if self.next_run else None,
                "error": str(e)
            }


def save_schedule(schedule: FlowSchedule):
    """Zapisuje harmonogram do pliku."""
    schedule_file = SCHEDULE_DIR / f"{schedule.schedule_id}.json"
    with open(schedule_file, "w") as f:
        json.dump(schedule.to_dict(), f, indent=4)


def load_schedule(schedule_id: str) -> Optional[FlowSchedule]:
    """Ładuje harmonogram z pliku."""
    schedule_file = SCHEDULE_DIR / f"{schedule_id}.json"
    
    if not os.path.exists(schedule_file):
        return None
    
    try:
        with open(schedule_file, "r") as f:
            data = json.load(f)
        return FlowSchedule.from_dict(data)
    except Exception as e:
        logger.error(f"Błąd ładowania harmonogramu {schedule_id}: {str(e)}")
        return None


def list_schedules() -> List[Dict[str, Any]]:
    """Zwraca listę wszystkich harmonogramów."""
    schedules = []
    
    for file in os.listdir(SCHEDULE_DIR):
        if file.endswith(".json"):
            try:
                with open(os.path.join(SCHEDULE_DIR, file), "r") as f:
                    schedules.append(json.load(f))
            except Exception as e:
                logger.error(f"Błąd ładowania harmonogramu {file}: {str(e)}")
    
    return schedules


def create_schedule(dsl_path: str,
                   schedule_type: str = "interval",
                   interval_minutes: int = 60,
                   cron_expression: Optional[str] = None,
                   input_data: Optional[Dict[str, Any]] = None,
                   enabled: bool = True,
                   use_parallel: bool = False,
                   description: Optional[str] = None) -> FlowSchedule:
    """
    Tworzy nowy harmonogram.
    
    Args:
        dsl_path: Ścieżka do pliku DSL lub nazwa pliku w katalogu DSL_DIR
        schedule_type: Typ harmonogramu ('interval', 'daily', 'weekly', 'monthly', 'cron')
        interval_minutes: Interwał w minutach (dla typu 'interval')
        cron_expression: Wyrażenie cron (dla typu 'cron')
        input_data: Dane wejściowe dla przepływu
        enabled: Czy harmonogram jest aktywny
        use_parallel: Czy używać równoległego wykonania
        description: Opis harmonogramu
        
    Returns:
        Utworzony obiekt FlowSchedule
    """
    # Generowanie unikalnego ID
    schedule_id = f"schedule_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # Sprawdzenie, czy plik DSL istnieje
    if os.path.isabs(dsl_path):
        if not os.path.exists(dsl_path):
            raise FileNotFoundError(f"Nie znaleziono pliku DSL: {dsl_path}")
    else:
        dsl_file = DSL_DIR / dsl_path
        if not os.path.exists(dsl_file):
            raise FileNotFoundError(f"Nie znaleziono pliku DSL: {dsl_path}")
    
    # Tworzenie obiektu harmonogramu
    schedule = FlowSchedule(
        schedule_id=schedule_id,
        dsl_path=dsl_path,
        input_data=input_data,
        schedule_type=schedule_type,
        interval_minutes=interval_minutes,
        cron_expression=cron_expression,
        enabled=enabled,
        use_parallel=use_parallel,
        description=description
    )
    
    # Obliczenie następnego czasu wykonania
    schedule.calculate_next_run()
    
    # Zapisanie harmonogramu
    save_schedule(schedule)
    
    # Rejestracja w bibliotece schedule, jeśli planer jest uruchomiony
    if scheduler_running and enabled:
        register_schedule_job(schedule)
    
    return schedule


def update_schedule(schedule_id: str, **kwargs) -> Optional[FlowSchedule]:
    """
    Aktualizuje istniejący harmonogram.
    
    Args:
        schedule_id: Identyfikator harmonogramu
        **kwargs: Parametry do aktualizacji
        
    Returns:
        Zaktualizowany obiekt FlowSchedule lub None, jeśli nie znaleziono
    """
    schedule = load_schedule(schedule_id)
    
    if not schedule:
        return None
    
    # Aktualizacja parametrów
    for key, value in kwargs.items():
        if hasattr(schedule, key):
            setattr(schedule, key, value)
    
    # Obliczenie następnego czasu wykonania
    schedule.calculate_next_run()
    
    # Zapisanie harmonogramu
    save_schedule(schedule)
    
    # Aktualizacja w bibliotece schedule, jeśli planer jest uruchomiony
    if scheduler_running and schedule.enabled:
        unregister_schedule_job(schedule_id)
        register_schedule_job(schedule)
    
    return schedule


def delete_schedule(schedule_id: str) -> bool:
    """
    Usuwa harmonogram.
    
    Args:
        schedule_id: Identyfikator harmonogramu
        
    Returns:
        True, jeśli usunięto pomyślnie, False w przeciwnym razie
    """
    schedule_file = SCHEDULE_DIR / f"{schedule_id}.json"
    
    if not os.path.exists(schedule_file):
        return False
    
    # Usunięcie z biblioteki schedule, jeśli planer jest uruchomiony
    if scheduler_running:
        unregister_schedule_job(schedule_id)
    
    # Usunięcie pliku
    try:
        os.remove(schedule_file)
        return True
    except Exception as e:
        logger.error(f"Błąd usuwania harmonogramu {schedule_id}: {str(e)}")
        return False


def register_schedule_job(schedule: FlowSchedule):
    """Rejestruje zadanie w bibliotece schedule."""
    if schedule.schedule_type == "interval":
        schedule.job = schedule.run
        schedule.job = schedule.every(schedule.interval_minutes).minutes.do(schedule.run)
    
    elif schedule.schedule_type == "daily":
        if isinstance(schedule.cron_expression, str) and ":" in schedule.cron_expression:
            hour, minute = map(int, schedule.cron_expression.split(":", 1))
            schedule.job = schedule.every().day.at(f"{hour:02d}:{minute:02d}").do(schedule.run)
    
    elif schedule.schedule_type == "weekly":
        # TODO: Implementacja harmonogramu tygodniowego
        pass
    
    elif schedule.schedule_type == "monthly":
        # Funkcja pomocnicza do wykonania zadania w określonym dniu miesiąca
        def monthly_job():
            now = datetime.now()
            if now.day == int(schedule.cron_expression):
                return schedule.run()
        
        schedule.job = schedule.every().day.at("00:00").do(monthly_job)
    
    else:
        logger.warning("Wyrażenia cron nie są obecnie obsługiwane")


def unregister_schedule_job(schedule_id: str):
    """Usuwa zadanie z biblioteki schedule."""
    schedule_obj = load_schedule(schedule_id)
    if schedule_obj and schedule_obj.job:
        schedule.cancel_job(schedule_obj.job)


def run_scheduler():
    """Uruchamia wątek planowania."""
    global scheduler_running
    
    while scheduler_running:
        schedule.run_pending()
        time.sleep(1)


def start_scheduler():
    """Uruchamia planowanie zadań."""
    global scheduler_running, scheduler_thread
    
    if scheduler_running:
        logger.warning("Planer jest już uruchomiony")
        return
    
    logger.info("Uruchamianie planera zadań...")
    scheduler_running = True
    
    # Załaduj wszystkie harmonogramy
    for schedule_data in list_schedules():
        try:
            schedule_obj = FlowSchedule.from_dict(schedule_data)
            if schedule_obj.enabled:
                register_schedule_job(schedule_obj)
        except Exception as e:
            logger.error(f"Błąd rejestracji harmonogramu: {str(e)}")
    
    # Uruchom wątek planowania
    scheduler_thread = threading.Thread(target=run_scheduler)
    scheduler_thread.daemon = True
    scheduler_thread.start()
    
    logger.info("Planer zadań uruchomiony")


def stop_scheduler():
    """Zatrzymuje planowanie zadań."""
    global scheduler_running, scheduler_thread
    
    if not scheduler_running:
        logger.warning("Planer nie jest uruchomiony")
        return
    
    logger.info("Zatrzymywanie planera zadań...")
    scheduler_running = False
    
    if scheduler_thread:
        scheduler_thread.join(timeout=5)
    
    # Wyczyść wszystkie zaplanowane zadania
    schedule.clear()
    
    logger.info("Planer zadań zatrzymany")


class FlowScheduler:
    """Klasa zarządzająca harmonogramami przepływów."""
    
    def __init__(self):
        """Inicjalizuje zarządcę harmonogramów."""
        pass
    
    def start(self, daemon: bool = False):
        """
        Uruchamia planowanie zadań.
        
        Args:
            daemon: Czy uruchomić jako daemon
        """
        start_scheduler()
        
        if not daemon:
            try:
                while scheduler_running:
                    time.sleep(1)
            except KeyboardInterrupt:
                self.stop()
    
    def stop(self):
        """Zatrzymuje planowanie zadań."""
        stop_scheduler()
    
    def list_schedules(self) -> List[Dict[str, Any]]:
        """
        Zwraca listę wszystkich harmonogramów.
        
        Returns:
            Lista harmonogramów
        """
        return list_schedules()
    
    def add_schedule(self, dsl_path: str, interval: Optional[int] = None, 
                    daily: Optional[str] = None, input_data: Optional[Dict[str, Any]] = None) -> str:
        """
        Dodaje nowy harmonogram.
        
        Args:
            dsl_path: Ścieżka do pliku DSL
            interval: Interwał w minutach
            daily: Czas codzienny (format HH:MM)
            input_data: Dane wejściowe
            
        Returns:
            ID harmonogramu
        """
        if interval:
            schedule = create_schedule(
                dsl_path=dsl_path,
                schedule_type="interval",
                interval_minutes=interval,
                input_data=input_data,
                description=f"Harmonogram co {interval} minut"
            )
        elif daily:
            schedule = create_schedule(
                dsl_path=dsl_path,
                schedule_type="daily",
                cron_expression=daily,
                input_data=input_data,
                description=f"Harmonogram codzienny o {daily}"
            )
        else:
            schedule = create_schedule(
                dsl_path=dsl_path,
                input_data=input_data,
                description=f"Harmonogram dla {dsl_path}"
            )
        
        return schedule.schedule_id
    
    def remove_schedule(self, schedule_id: str) -> bool:
        """
        Usuwa harmonogram.
        
        Args:
            schedule_id: ID harmonogramu
            
        Returns:
            True, jeśli usunięto pomyślnie
        """
        return delete_schedule(schedule_id)
    
    def run_schedule(self, schedule_id: str) -> Dict[str, Any]:
        """
        Uruchamia harmonogram ręcznie.
        
        Args:
            schedule_id: ID harmonogramu
            
        Returns:
            Wynik wykonania
        """
        schedule = load_schedule(schedule_id)
        if not schedule:
            return {"status": "ERROR", "error": f"Nie znaleziono harmonogramu {schedule_id}"}
        
        return schedule.run()


if __name__ == "__main__":
    # Przykład użycia
    import sys
    
    if len(sys.argv) < 2:
        print("Użycie: python flow_scheduler.py [start|stop|list|create|delete|run]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "start":
        start_scheduler()
        print("Planer uruchomiony. Naciśnij Ctrl+C, aby zakończyć.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            stop_scheduler()
    
    elif command == "stop":
        stop_scheduler()
    
    elif command == "list":
        schedules = list_schedules()
        print(f"Znaleziono {len(schedules)} harmonogramów:")
        for s in schedules:
            enabled = "aktywny" if s.get("enabled", True) else "nieaktywny"
            next_run = s.get("next_run", "brak")
            print(f"- {s.get('schedule_id')}: {s.get('description', 'brak opisu')} ({enabled}, następne wykonanie: {next_run})")
    
    elif command == "create" and len(sys.argv) >= 3:
        dsl_path = sys.argv[2]
        interval = int(sys.argv[3]) if len(sys.argv) > 3 else 60
        
        schedule = create_schedule(
            dsl_path=dsl_path,
            interval_minutes=interval,
            description=f"Harmonogram dla {dsl_path} co {interval} minut"
        )
        
        print(f"Utworzono harmonogram: {schedule.schedule_id}")
    
    elif command == "delete" and len(sys.argv) >= 3:
        schedule_id = sys.argv[2]
        if delete_schedule(schedule_id):
            print(f"Usunięto harmonogram: {schedule_id}")
        else:
            print(f"Nie znaleziono harmonogramu: {schedule_id}")
    
    elif command == "run" and len(sys.argv) >= 3:
        schedule_id = sys.argv[2]
        schedule = load_schedule(schedule_id)
        
        if schedule:
            print(f"Uruchamianie harmonogramu: {schedule_id}")
            result = schedule.run()
            print(f"Wynik: {result}")
        else:
            print(f"Nie znaleziono harmonogramu: {schedule_id}")
    
    else:
        print("Nieznane polecenie lub brak wymaganych parametrów")
        print("Użycie: python flow_scheduler.py [start|stop|list|create|delete|run]")
