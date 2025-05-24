#!/usr/bin/env python3
"""
Moduł do planowania wykonania przepływów w taskinity.
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

# Import funkcji z taskinity
from flow_dsl import run_flow_from_dsl, load_dsl, parse_dsl

# Opcjonalny import równoległego wykonawcy
try:
    from parallel_executor import run_parallel_flow_from_dsl
    PARALLEL_AVAILABLE = True
except ImportError:
    PARALLEL_AVAILABLE = False

# Opcjonalny import powiadomień
try:
    from notification_service import notify_flow_status
    NOTIFICATIONS_AVAILABLE = True
except ImportError:
    NOTIFICATIONS_AVAILABLE = False

# Konfiguracja loggera
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("flow_scheduler")

# Ścieżki do katalogów
BASE_DIR = Path(__file__).parent
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
        next_run = None
        if data.get("next_run"):
            try:
                next_run = datetime.fromisoformat(data["next_run"])
            except (ValueError, TypeError):
                next_run = None
        
        last_run = None
        if data.get("last_run"):
            try:
                last_run = datetime.fromisoformat(data["last_run"])
            except (ValueError, TypeError):
                last_run = None
        
        schedule = cls(
            schedule_id=data.get("schedule_id", ""),
            dsl_path=data.get("dsl_path", ""),
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
            return now + timedelta(minutes=self.interval_minutes)
        elif self.schedule_type == "daily":
            # Wykonaj o tej samej porze następnego dnia
            return now + timedelta(days=1)
        elif self.schedule_type == "weekly":
            # Wykonaj w ten sam dzień tygodnia następnego tygodnia
            return now + timedelta(days=7)
        elif self.schedule_type == "monthly":
            # Wykonaj tego samego dnia następnego miesiąca
            if now.month == 12:
                next_month = 1
                next_year = now.year + 1
            else:
                next_month = now.month + 1
                next_year = now.year
            
            # Obsługa różnych długości miesięcy
            day = min(now.day, [31, 29 if (next_year % 4 == 0 and next_year % 100 != 0) or next_year % 400 == 0 else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][next_month - 1])
            
            return datetime(next_year, next_month, day, now.hour, now.minute, now.second)
        else:
            # Domyślnie interwał
            return now + timedelta(minutes=self.interval_minutes)
    
    def run(self):
        """Wykonuje zaplanowany przepływ."""
        if not self.enabled:
            logger.info(f"Harmonogram {self.schedule_id} jest wyłączony, pomijam wykonanie")
            return
        
        logger.info(f"Wykonuję zaplanowany przepływ: {self.schedule_id}")
        self.last_run = datetime.now()
        
        try:
            # Załaduj definicję DSL
            dsl_path = self.dsl_path
            if not os.path.isabs(dsl_path):
                dsl_path = str(DSL_DIR / dsl_path)
            
            dsl_content = load_dsl(dsl_path)
            
            # Parsuj DSL, aby uzyskać nazwę przepływu
            flow_def = parse_dsl(dsl_content)
            flow_name = flow_def.get("name", "UnknownFlow")
            
            # Przygotuj dane do powiadomienia
            flow_data = {
                "flow_id": f"{flow_name}-{int(time.time())}",
                "name": flow_name,
                "start_time": datetime.now().isoformat()
            }
            
            # Powiadomienie o rozpoczęciu
            if NOTIFICATIONS_AVAILABLE:
                notify_flow_status(flow_data, "STARTED")
            
            # Wykonaj przepływ
            if self.use_parallel and PARALLEL_AVAILABLE:
                result = run_parallel_flow_from_dsl(dsl_content, self.input_data)
            else:
                result = run_flow_from_dsl(dsl_content, self.input_data)
            
            # Aktualizuj status
            self.last_status = "SUCCESS"
            
            # Aktualizuj dane do powiadomienia
            flow_data.update({
                "flow_id": result.get("flow_id", flow_data["flow_id"]),
                "end_time": datetime.now().isoformat(),
                "duration": result.get("duration", 0),
                "tasks": result.get("tasks", [])
            })
            
            # Powiadomienie o zakończeniu
            if NOTIFICATIONS_AVAILABLE:
                notify_flow_status(flow_data, "COMPLETED")
            
            logger.info(f"Zaplanowany przepływ {self.schedule_id} zakończony pomyślnie")
            return result
        
        except Exception as e:
            logger.error(f"Błąd podczas wykonywania zaplanowanego przepływu {self.schedule_id}: {str(e)}")
            self.last_status = "ERROR"
            
            # Powiadomienie o błędzie
            if NOTIFICATIONS_AVAILABLE:
                flow_data = {
                    "flow_id": f"{self.schedule_id}-{int(time.time())}",
                    "name": self.schedule_id,
                    "start_time": self.last_run.isoformat(),
                    "end_time": datetime.now().isoformat()
                }
                notify_flow_status(flow_data, "FAILED", str(e))
            
            return {"error": str(e)}
        finally:
            # Aktualizuj następne wykonanie dla harmonogramów typu 'interval'
            if self.schedule_type == "interval":
                self.next_run = self.calculate_next_run()
                save_schedule(self)


def save_schedule(schedule: FlowSchedule):
    """Zapisuje harmonogram do pliku."""
    schedule_file = SCHEDULE_DIR / f"{schedule.schedule_id}.json"
    with open(schedule_file, "w") as f:
        json.dump(schedule.to_dict(), f, indent=4)
    logger.info(f"Zapisano harmonogram: {schedule.schedule_id}")


def load_schedule(schedule_id: str) -> Optional[FlowSchedule]:
    """Ładuje harmonogram z pliku."""
    schedule_file = SCHEDULE_DIR / f"{schedule_id}.json"
    if not schedule_file.exists():
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
    for file in SCHEDULE_DIR.glob("*.json"):
        try:
            with open(file, "r") as f:
                data = json.load(f)
            schedules.append(data)
        except Exception as e:
            logger.error(f"Błąd ładowania harmonogramu z pliku {file}: {str(e)}")
    
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
    # Generuj unikalny identyfikator
    schedule_id = f"schedule-{int(time.time())}"
    
    # Sprawdź, czy plik DSL istnieje
    if not os.path.isabs(dsl_path):
        full_path = DSL_DIR / dsl_path
        if not full_path.exists():
            raise FileNotFoundError(f"Plik DSL nie istnieje: {full_path}")
    elif not Path(dsl_path).exists():
        raise FileNotFoundError(f"Plik DSL nie istnieje: {dsl_path}")
    
    # Oblicz następny czas wykonania
    next_run = datetime.now()
    if schedule_type == "interval":
        next_run += timedelta(minutes=interval_minutes)
    
    # Utwórz harmonogram
    schedule = FlowSchedule(
        schedule_id=schedule_id,
        dsl_path=dsl_path,
        input_data=input_data,
        schedule_type=schedule_type,
        interval_minutes=interval_minutes,
        cron_expression=cron_expression,
        next_run=next_run,
        enabled=enabled,
        use_parallel=use_parallel,
        description=description
    )
    
    # Zapisz harmonogram
    save_schedule(schedule)
    
    # Dodaj do aktywnego planera, jeśli jest uruchomiony
    if scheduler_running:
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
    
    # Aktualizuj parametry
    for key, value in kwargs.items():
        if hasattr(schedule, key):
            setattr(schedule, key, value)
    
    # Jeśli zmieniono typ harmonogramu lub interwał, oblicz nowy czas wykonania
    if "schedule_type" in kwargs or "interval_minutes" in kwargs:
        schedule.next_run = schedule.calculate_next_run()
    
    # Zapisz zaktualizowany harmonogram
    save_schedule(schedule)
    
    # Aktualizuj w aktywnym planerze, jeśli jest uruchomiony
    if scheduler_running:
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
    if not schedule_file.exists():
        return False
    
    # Usuń z aktywnego planera, jeśli jest uruchomiony
    if scheduler_running:
        unregister_schedule_job(schedule_id)
    
    # Usuń plik
    try:
        os.remove(schedule_file)
        logger.info(f"Usunięto harmonogram: {schedule_id}")
        return True
    except Exception as e:
        logger.error(f"Błąd usuwania harmonogramu {schedule_id}: {str(e)}")
        return False


def register_schedule_job(schedule: FlowSchedule):
    """Rejestruje zadanie w bibliotece schedule."""
    if schedule.schedule_type == "interval":
        schedule.job = schedule.run
        schedule.job = schedule.interval_minutes
    elif schedule.schedule_type == "daily":
        # Wykonaj codziennie o określonej godzinie
        if schedule.next_run:
            time_str = schedule.next_run.strftime("%H:%M")
            schedule.job = schedule.daily.at(time_str).do(schedule.run)
    elif schedule.schedule_type == "weekly":
        # Wykonaj co tydzień w określonym dniu
        if schedule.next_run:
            day = schedule.next_run.strftime("%A").lower()
            time_str = schedule.next_run.strftime("%H:%M")
            getattr(schedule.every(), day).at(time_str).do(schedule.run)
    elif schedule.schedule_type == "monthly":
        # Dla miesięcznych używamy interwału i sprawdzamy datę w funkcji run
        def monthly_job():
            now = datetime.now()
            if now.day == schedule.next_run.day:
                schedule.run()
        
        # Wykonuj codziennie, ale sprawdzaj dzień miesiąca
        schedule.job = schedule.every().day.at("00:01").do(monthly_job)
    elif schedule.schedule_type == "cron" and schedule.cron_expression:
        # Obsługa wyrażeń cron jest bardziej złożona i wymaga dodatkowej biblioteki
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
