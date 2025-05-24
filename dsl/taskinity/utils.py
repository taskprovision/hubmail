#!/usr/bin/env python3
"""
Moduł narzędziowy dla Taskinity zawierający funkcje pomocnicze.
"""
import os
import json
import time
import logging
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Callable
from datetime import datetime

# Konfiguracja loggera
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("taskinity.utils")

# Ścieżki do katalogów
BASE_DIR = Path(__file__).parent.parent
CACHE_DIR = BASE_DIR / "cache"
LOGS_DIR = BASE_DIR / "logs"

# Upewniamy się, że katalogi istnieją
os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)


def generate_id(prefix: str = "task") -> str:
    """
    Generuje unikalny identyfikator.
    
    Args:
        prefix: Prefiks identyfikatora
        
    Returns:
        Unikalny identyfikator
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
    random_part = hashlib.md5(f"{timestamp}-{os.getpid()}".encode()).hexdigest()[:8]
    return f"{prefix}_{timestamp}_{random_part}"


def timed_execution(func: Callable) -> Callable:
    """
    Dekorator mierzący czas wykonania funkcji.
    
    Args:
        func: Funkcja do zmierzenia
        
    Returns:
        Funkcja z pomiarem czasu
    """
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        duration = end_time - start_time
        logger.info(f"Funkcja {func.__name__} wykonana w {duration:.4f} s")
        return result
    
    return wrapper


def retry(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0, 
          exceptions: tuple = (Exception,)) -> Callable:
    """
    Dekorator do ponawiania wykonania funkcji w przypadku błędu.
    
    Args:
        max_attempts: Maksymalna liczba prób
        delay: Opóźnienie początkowe (w sekundach)
        backoff: Współczynnik zwiększania opóźnienia
        exceptions: Krotka wyjątków, które mają być obsługiwane
        
    Returns:
        Funkcja z mechanizmem ponawiania
    """
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    logger.warning(f"Próba {attempt}/{max_attempts} funkcji {func.__name__} nie powiodła się: {str(e)}")
                    
                    if attempt < max_attempts:
                        logger.info(f"Ponowienie za {current_delay:.2f} s")
                        time.sleep(current_delay)
                        current_delay *= backoff
            
            logger.error(f"Wszystkie próby funkcji {func.__name__} nie powiodły się")
            raise last_exception
        
        return wrapper
    
    return decorator


def cache_result(ttl: int = 3600, cache_dir: Optional[str] = None) -> Callable:
    """
    Dekorator do buforowania wyników funkcji.
    
    Args:
        ttl: Czas życia bufora (w sekundach)
        cache_dir: Katalog bufora (opcjonalnie)
        
    Returns:
        Funkcja z buforowaniem wyników
    """
    cache_path = Path(cache_dir) if cache_dir else CACHE_DIR
    os.makedirs(cache_path, exist_ok=True)
    
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            # Tworzenie klucza bufora
            key_parts = [func.__name__]
            key_parts.extend([str(arg) for arg in args])
            key_parts.extend([f"{k}:{v}" for k, v in sorted(kwargs.items())])
            key = hashlib.md5("_".join(key_parts).encode()).hexdigest()
            
            cache_file = cache_path / f"{key}.json"
            
            # Sprawdzenie bufora
            if cache_file.exists():
                try:
                    with open(cache_file, "r") as f:
                        cached_data = json.load(f)
                    
                    # Sprawdzenie czasu życia
                    timestamp = cached_data.get("timestamp", 0)
                    if time.time() - timestamp <= ttl:
                        logger.debug(f"Użyto bufora dla funkcji {func.__name__}")
                        return cached_data.get("result")
                except Exception as e:
                    logger.warning(f"Błąd odczytu bufora: {str(e)}")
            
            # Wykonanie funkcji
            result = func(*args, **kwargs)
            
            # Zapisanie wyniku do bufora
            try:
                with open(cache_file, "w") as f:
                    json.dump({
                        "timestamp": time.time(),
                        "result": result
                    }, f)
            except Exception as e:
                logger.warning(f"Błąd zapisu bufora: {str(e)}")
            
            return result
        
        return wrapper
    
    return decorator


def setup_logger(name: str, log_file: Optional[str] = None, level: int = logging.INFO) -> logging.Logger:
    """
    Konfiguruje logger.
    
    Args:
        name: Nazwa loggera
        log_file: Ścieżka do pliku logów (opcjonalnie)
        level: Poziom logowania
        
    Returns:
        Skonfigurowany logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Upewniamy się, że logger nie ma już handlerów
    if logger.handlers:
        return logger
    
    # Dodanie handlera konsolowego
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # Dodanie handlera plikowego, jeśli podano plik
    if log_file:
        log_path = Path(log_file)
        os.makedirs(log_path.parent, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger


def load_json(file_path: str) -> Dict[str, Any]:
    """
    Ładuje dane JSON z pliku.
    
    Args:
        file_path: Ścieżka do pliku JSON
        
    Returns:
        Dane JSON
    """
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Błąd ładowania pliku JSON {file_path}: {str(e)}")
        return {}


def save_json(data: Dict[str, Any], file_path: str, indent: int = 4):
    """
    Zapisuje dane JSON do pliku.
    
    Args:
        data: Dane do zapisania
        file_path: Ścieżka do pliku JSON
        indent: Wcięcie JSON
    """
    try:
        with open(file_path, "w") as f:
            json.dump(data, f, indent=indent)
    except Exception as e:
        logger.error(f"Błąd zapisywania pliku JSON {file_path}: {str(e)}")


def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
    """
    Spłaszcza zagnieżdżony słownik.
    
    Args:
        d: Słownik do spłaszczenia
        parent_key: Klucz nadrzędny
        sep: Separator kluczy
        
    Returns:
        Spłaszczony słownik
    """
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def get_nested_value(d: Dict[str, Any], key_path: str, sep: str = '.', default: Any = None) -> Any:
    """
    Pobiera wartość z zagnieżdżonego słownika.
    
    Args:
        d: Słownik
        key_path: Ścieżka klucza (np. "a.b.c")
        sep: Separator kluczy
        default: Wartość domyślna
        
    Returns:
        Wartość lub wartość domyślna
    """
    keys = key_path.split(sep)
    current = d
    
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    
    return current


def set_nested_value(d: Dict[str, Any], key_path: str, value: Any, sep: str = '.') -> Dict[str, Any]:
    """
    Ustawia wartość w zagnieżdżonym słowniku.
    
    Args:
        d: Słownik
        key_path: Ścieżka klucza (np. "a.b.c")
        value: Wartość do ustawienia
        sep: Separator kluczy
        
    Returns:
        Zaktualizowany słownik
    """
    keys = key_path.split(sep)
    current = d
    
    for i, key in enumerate(keys[:-1]):
        if key not in current or not isinstance(current[key], dict):
            current[key] = {}
        current = current[key]
    
    current[keys[-1]] = value
    return d


def merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """
    Łączy dwa słowniki, zachowując zagnieżdżone struktury.
    
    Args:
        dict1: Pierwszy słownik
        dict2: Drugi słownik
        
    Returns:
        Połączony słownik
    """
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value
    
    return result


def format_time_delta(seconds: float) -> str:
    """
    Formatuje czas w sekundach do czytelnej postaci.
    
    Args:
        seconds: Czas w sekundach
        
    Returns:
        Sformatowany czas
    """
    if seconds < 0.001:
        return f"{seconds * 1000000:.2f} µs"
    elif seconds < 1:
        return f"{seconds * 1000:.2f} ms"
    elif seconds < 60:
        return f"{seconds:.2f} s"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        remaining_seconds = seconds % 60
        return f"{minutes} min {remaining_seconds:.2f} s"
    else:
        hours = int(seconds / 3600)
        remaining = seconds % 3600
        minutes = int(remaining / 60)
        remaining_seconds = remaining % 60
        return f"{hours} godz {minutes} min {remaining_seconds:.2f} s"


def sanitize_filename(filename: str) -> str:
    """
    Sanityzuje nazwę pliku, usuwając niedozwolone znaki.
    
    Args:
        filename: Nazwa pliku
        
    Returns:
        Sanityzowana nazwa pliku
    """
    # Znaki niedozwolone w nazwach plików
    invalid_chars = '<>:"/\\|?*'
    
    # Zastąpienie niedozwolonych znaków
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    return filename


def human_readable_size(size_bytes: int) -> str:
    """
    Konwertuje rozmiar w bajtach na czytelną dla człowieka postać.
    
    Args:
        size_bytes: Rozmiar w bajtach
        
    Returns:
        Czytelny rozmiar
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = 0
    
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024
        i += 1
    
    return f"{size_bytes:.2f} {size_names[i]}"


def is_valid_json(json_str: str) -> bool:
    """
    Sprawdza, czy ciąg znaków jest poprawnym JSON.
    
    Args:
        json_str: Ciąg znaków JSON
        
    Returns:
        True, jeśli ciąg jest poprawnym JSON
    """
    try:
        json.loads(json_str)
        return True
    except ValueError:
        return False


def truncate_string(s: str, max_length: int = 100, suffix: str = '...') -> str:
    """
    Skraca ciąg znaków do określonej długości.
    
    Args:
        s: Ciąg znaków
        max_length: Maksymalna długość
        suffix: Sufiks dodawany do skróconego ciągu
        
    Returns:
        Skrócony ciąg znaków
    """
    if len(s) <= max_length:
        return s
    
    return s[:max_length - len(suffix)] + suffix


if __name__ == "__main__":
    # Przykłady użycia
    logger = setup_logger("taskinity.utils.example", log_file=str(LOGS_DIR / "utils_example.log"))
    
    @timed_execution
    def example_function(n: int) -> int:
        """Przykładowa funkcja."""
        time.sleep(0.1)
        return n * 2
    
    @retry(max_attempts=3, delay=0.5)
    def example_retry_function(should_fail: bool = False) -> str:
        """Przykładowa funkcja z ponawianiem."""
        if should_fail:
            raise ValueError("Przykładowy błąd")
        return "Sukces"
    
    @cache_result(ttl=10)
    def example_cache_function(n: int) -> int:
        """Przykładowa funkcja z buforowaniem."""
        logger.info(f"Obliczanie dla n={n}")
        time.sleep(0.5)
        return n * n
    
    # Przykłady
    logger.info(f"Unikalny ID: {generate_id()}")
    
    logger.info("Testowanie funkcji z pomiarem czasu:")
    result = example_function(5)
    logger.info(f"Wynik: {result}")
    
    logger.info("Testowanie funkcji z ponawianiem:")
    try:
        result = example_retry_function(should_fail=False)
        logger.info(f"Wynik: {result}")
        
        result = example_retry_function(should_fail=True)
    except ValueError:
        logger.info("Funkcja nie powiodła się po wszystkich próbach")
    
    logger.info("Testowanie funkcji z buforowaniem:")
    for i in range(3):
        logger.info(f"Wywołanie {i+1}:")
        result = example_cache_function(10)
        logger.info(f"Wynik: {result}")
    
    logger.info("Testowanie operacji na słownikach:")
    d1 = {"a": 1, "b": {"c": 2, "d": 3}}
    d2 = {"b": {"e": 4}, "f": 5}
    
    logger.info(f"Spłaszczony słownik: {flatten_dict(d1)}")
    logger.info(f"Pobieranie zagnieżdżonej wartości: {get_nested_value(d1, 'b.c')}")
    
    d1 = set_nested_value(d1, "b.g", 6)
    logger.info(f"Ustawienie zagnieżdżonej wartości: {d1}")
    
    merged = merge_dicts(d1, d2)
    logger.info(f"Połączone słowniki: {merged}")
    
    logger.info(f"Formatowanie czasu: {format_time_delta(3661.5)}")
    logger.info(f"Czytelny rozmiar: {human_readable_size(1048576)}")
