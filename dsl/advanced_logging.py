#!/usr/bin/env python3
"""
Moduł zaawansowanego logowania dla taskinity.
Zapewnia szczegółowe logowanie z formatowaniem, rotacją plików i konfigurowalnymi poziomami logowania.
"""
import os
import sys
import json
import traceback
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List, Union

# Importujemy loguru dla zaawansowanego logowania
from loguru import logger

# Katalog logów
BASE_DIR = Path(__file__).parent
LOGS_DIR = BASE_DIR / "logs"
CONFIG_DIR = BASE_DIR / "config"

# Tworzenie katalogów, jeśli nie istnieją
os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(CONFIG_DIR, exist_ok=True)

# Plik konfiguracyjny logowania
LOGGING_CONFIG_FILE = CONFIG_DIR / "logging_config.json"

# Domyślna konfiguracja logowania
DEFAULT_LOGGING_CONFIG = {
    "console": {
        "enabled": True,
        "level": "INFO",
        "format": "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    },
    "file": {
        "enabled": True,
        "level": "DEBUG",
        "format": "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        "rotation": "1 day",
        "retention": "30 days",
        "compression": "zip"
    },
    "modules": {
        "flow_dsl": "DEBUG",
        "mini_dashboard": "INFO",
        "flow_visualizer": "INFO",
        "notification_service": "DEBUG",
        "parallel_executor": "DEBUG",
        "flow_scheduler": "DEBUG",
        "email_pipeline": "DEBUG"
    }
}

def ensure_logging_config():
    """Upewnia się, że plik konfiguracyjny logowania istnieje."""
    if not LOGGING_CONFIG_FILE.exists():
        with open(LOGGING_CONFIG_FILE, 'w') as f:
            json.dump(DEFAULT_LOGGING_CONFIG, f, indent=4)
        print(f"Utworzono domyślny plik konfiguracyjny logowania: {LOGGING_CONFIG_FILE}")
    
    return load_logging_config()

def load_logging_config() -> Dict[str, Any]:
    """Ładuje konfigurację logowania."""
    try:
        with open(LOGGING_CONFIG_FILE, 'r') as f:
            config = json.load(f)
        return config
    except Exception as e:
        print(f"Błąd ładowania konfiguracji logowania: {str(e)}")
        return DEFAULT_LOGGING_CONFIG

def save_logging_config(config: Dict[str, Any]):
    """Zapisuje konfigurację logowania."""
    try:
        with open(LOGGING_CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
        print("Konfiguracja logowania zapisana.")
    except Exception as e:
        print(f"Błąd zapisywania konfiguracji logowania: {str(e)}")

def setup_logger(module_name: str) -> "logger":
    """
    Konfiguruje i zwraca logger dla określonego modułu.
    
    Args:
        module_name: Nazwa modułu, dla którego konfigurowany jest logger
        
    Returns:
        Skonfigurowany obiekt logger
    """
    # Ładowanie konfiguracji
    config = ensure_logging_config()
    
    # Usunięcie wszystkich handlerów
    logger.remove()
    
    # Dodanie handlera konsolowego
    if config["console"]["enabled"]:
        logger.add(
            sys.stderr,
            level=config["console"]["level"],
            format=config["console"]["format"],
            colorize=True
        )
    
    # Dodanie handlera plikowego
    if config["file"]["enabled"]:
        log_file = LOGS_DIR / f"{module_name}.log"
        logger.add(
            log_file,
            level=config["file"]["level"],
            format=config["file"]["format"],
            rotation=config["file"]["rotation"],
            retention=config["file"]["retention"],
            compression=config["file"]["compression"]
        )
    
    # Ustawienie poziomu logowania dla modułu
    module_level = config["modules"].get(module_name, "INFO")
    
    # Utworzenie loggera dla modułu
    module_logger = logger.bind(module=module_name)
    
    return module_logger

def log_exception(logger, e: Exception, context: Optional[Dict[str, Any]] = None):
    """
    Loguje wyjątek ze szczegółami.
    
    Args:
        logger: Obiekt loggera
        e: Wyjątek do zalogowania
        context: Dodatkowy kontekst do zalogowania
    """
    exc_type, exc_value, exc_traceback = sys.exc_info()
    tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
    tb_text = ''.join(tb_lines)
    
    log_data = {
        "exception_type": exc_type.__name__ if exc_type else "Unknown",
        "exception_message": str(e),
        "traceback": tb_text
    }
    
    if context:
        log_data["context"] = context
    
    logger.error(f"Exception: {exc_type.__name__ if exc_type else 'Unknown'} - {str(e)}")
    logger.debug(f"Exception details: {json.dumps(log_data, indent=2)}")

def log_function_call(logger, func_name: str, args: List[Any], kwargs: Dict[str, Any]):
    """
    Loguje wywołanie funkcji z argumentami.
    
    Args:
        logger: Obiekt loggera
        func_name: Nazwa funkcji
        args: Argumenty pozycyjne
        kwargs: Argumenty nazwane
    """
    logger.debug(f"Function call: {func_name}")
    logger.debug(f"Args: {args}")
    logger.debug(f"Kwargs: {kwargs}")

def log_dependency_check(logger, dependency: str, version: Optional[str] = None, required: bool = True):
    """
    Loguje sprawdzenie zależności.
    
    Args:
        logger: Obiekt loggera
        dependency: Nazwa zależności
        version: Wersja zależności
        required: Czy zależność jest wymagana
    """
    if version:
        logger.debug(f"Dependency check: {dependency} (version: {version})")
    else:
        logger.debug(f"Dependency check: {dependency}")
    
    try:
        module = __import__(dependency)
        module_version = getattr(module, "__version__", "unknown")
        logger.debug(f"Dependency {dependency} found (version: {module_version})")
        return True
    except ImportError:
        if required:
            logger.error(f"Required dependency {dependency} not found")
        else:
            logger.warning(f"Optional dependency {dependency} not found")
        return False

def log_config_check(logger, config: Dict[str, Any], required_keys: List[str]):
    """
    Sprawdza i loguje brakujące klucze w konfiguracji.
    
    Args:
        logger: Obiekt loggera
        config: Słownik konfiguracyjny
        required_keys: Lista wymaganych kluczy
    
    Returns:
        True, jeśli wszystkie wymagane klucze są obecne, False w przeciwnym razie
    """
    missing_keys = []
    
    for key in required_keys:
        if key not in config:
            missing_keys.append(key)
    
    if missing_keys:
        logger.warning(f"Missing required configuration keys: {missing_keys}")
        return False
    
    logger.debug(f"All required configuration keys present: {required_keys}")
    return True

def log_performance(logger, start_time: float, end_time: float, operation: str, details: Optional[Dict[str, Any]] = None):
    """
    Loguje wydajność operacji.
    
    Args:
        logger: Obiekt loggera
        start_time: Czas rozpoczęcia operacji
        end_time: Czas zakończenia operacji
        operation: Nazwa operacji
        details: Dodatkowe szczegóły operacji
    """
    duration = end_time - start_time
    
    log_data = {
        "operation": operation,
        "duration_seconds": duration,
        "start_time": datetime.fromtimestamp(start_time).isoformat(),
        "end_time": datetime.fromtimestamp(end_time).isoformat()
    }
    
    if details:
        log_data["details"] = details
    
    logger.debug(f"Performance: {operation} took {duration:.4f} seconds")
    logger.trace(f"Performance details: {json.dumps(log_data, indent=2)}")

# Inicjalizacja przy importowaniu
ensure_logging_config()

if __name__ == "__main__":
    # Test loggera
    test_logger = setup_logger("test")
    test_logger.info("Test info message")
    test_logger.debug("Test debug message")
    test_logger.warning("Test warning message")
    test_logger.error("Test error message")
    
    try:
        1/0
    except Exception as e:
        log_exception(test_logger, e, {"context": "Test exception logging"})
    
    print(f"Logi zostały zapisane w: {LOGS_DIR}/test.log")
