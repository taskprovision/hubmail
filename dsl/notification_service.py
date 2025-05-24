#!/usr/bin/env python3
"""
Moduł do obsługi powiadomień dla taskinity.
Obsługuje powiadomienia email i Slack o statusie przepływów.
"""
import os
import json
import time
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

# Import zaawansowanego logowania
try:
    from advanced_logging import setup_logger, log_exception, log_dependency_check, log_config_check, log_performance
    logger = setup_logger("notification_service")
except ImportError:
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger("notification_service")
    logger.warning("Moduł advanced_logging nie jest dostępny. Używam standardowego logowania.")

# Ścieżka do pliku konfiguracyjnego
CONFIG_DIR = Path(__file__).parent / "config"
CONFIG_FILE = CONFIG_DIR / "notification_config.json"

# Domyślna konfiguracja
DEFAULT_CONFIG = {
    "enabled": False,
    "email": {
        "enabled": False,
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "username": "",
        "password": "",
        "from_email": "",
        "recipients": []
    },
    "slack": {
        "enabled": False,
        "webhook_url": "",
        "channel": "#flow-notifications",
        "username": "taskinity Bot"
    },
    "notification_rules": {
        "on_start": True,
        "on_complete": True,
        "on_error": True,
        "include_details": True
    }
}

def ensure_config():
    """Upewnia się, że plik konfiguracyjny istnieje."""
    start_time = time.time()
    logger.debug("Sprawdzanie konfiguracji powiadomień...")
    
    try:
        # Sprawdź, czy katalog konfiguracyjny istnieje
        if not os.path.exists(CONFIG_DIR):
            logger.info(f"Tworzenie katalogu konfiguracyjnego: {CONFIG_DIR}")
            os.makedirs(CONFIG_DIR, exist_ok=True)
        
        # Sprawdź, czy plik konfiguracyjny istnieje
        if not CONFIG_FILE.exists():
            logger.info(f"Tworzenie domyślnego pliku konfiguracyjnego: {CONFIG_FILE}")
            with open(CONFIG_FILE, 'w') as f:
                json.dump(DEFAULT_CONFIG, f, indent=4)
        
        config = load_config()
        
        # Sprawdź, czy konfiguracja zawiera wszystkie wymagane klucze
        required_keys = ["enabled", "email", "slack", "notification_rules"]
        if hasattr(log_config_check, "__call__"):
            log_config_check(logger, config, required_keys)
        else:
            missing_keys = [key for key in required_keys if key not in config]
            if missing_keys:
                logger.warning(f"Brakujące klucze w konfiguracji: {missing_keys}")
        
        end_time = time.time()
        if hasattr(log_performance, "__call__"):
            log_performance(logger, start_time, end_time, "ensure_config")
        else:
            logger.debug(f"ensure_config zakończone w {end_time - start_time:.4f}s")
        
        return config
    
    except Exception as e:
        if hasattr(log_exception, "__call__"):
            log_exception(logger, e, {"function": "ensure_config"})
        else:
            logger.error(f"Błąd podczas sprawdzania konfiguracji: {str(e)}")
        
        # W przypadku błędu zwróć domyślną konfigurację
        return DEFAULT_CONFIG

def load_config() -> Dict[str, Any]:
    """Ładuje konfigurację powiadomień."""
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
        return config
    except Exception as e:
        logger.error(f"Błąd ładowania konfiguracji: {str(e)}")
        return DEFAULT_CONFIG

def save_config(config: Dict[str, Any]):
    """Zapisuje konfigurację powiadomień."""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
        logger.info("Konfiguracja powiadomień zapisana.")
    except Exception as e:
        logger.error(f"Błąd zapisywania konfiguracji: {str(e)}")

def send_email_notification(subject: str, message: str, config: Optional[Dict[str, Any]] = None) -> bool:
    """Wysyła powiadomienie email."""
    start_time = time.time()
    logger.debug(f"Próba wysłania powiadomienia email: {subject}")
    
    # Sprawdzenie konfiguracji
    if config is None:
        logger.debug("Brak przekazanej konfiguracji, ładowanie domyślnej")
        config = load_config()
    
    email_config = config.get("email", {})
    
    # Sprawdzenie, czy powiadomienia email są włączone
    if not email_config.get("enabled", False):
        logger.info("Powiadomienia email są wyłączone.")
        return False
    
    # Sprawdzenie wymaganych parametrów konfiguracji
    required_params = ["smtp_server", "smtp_port", "username", "password", "from_email", "recipients"]
    missing_params = [param for param in required_params if not email_config.get(param)]
    
    if missing_params:
        logger.error(f"Brakujące parametry konfiguracji email: {missing_params}")
        return False
    
    # Sprawdzenie, czy lista odbiorców nie jest pusta
    recipients = email_config.get("recipients", [])
    if not recipients:
        logger.warning("Lista odbiorców jest pusta, nie można wysłać powiadomienia")
        return False
    
    try:
        # Tworzenie wiadomości
        logger.debug("Tworzenie wiadomości email")
        msg = MIMEMultipart()
        msg['From'] = email_config.get("from_email")
        msg['To'] = ", ".join(recipients)
        msg['Subject'] = subject
        
        # Dodanie treści
        msg.attach(MIMEText(message, 'plain'))
        
        # Połączenie z serwerem SMTP
        logger.debug(f"Próba połączenia z serwerem SMTP: {email_config.get('smtp_server')}:{email_config.get('smtp_port')}")
        server = smtplib.SMTP(email_config.get("smtp_server"), email_config.get("smtp_port"))
        
        # Logowanie połączenia
        server_info = server.ehlo()
        logger.debug(f"Informacje o serwerze: {server_info}")
        
        # Rozpoczęcie TLS
        logger.debug("Rozpoczynanie TLS")
        server.starttls()
        
        # Logowanie do serwera
        logger.debug(f"Logowanie jako: {email_config.get('username')}")
        server.login(email_config.get("username"), email_config.get("password"))
        
        # Wysłanie wiadomości
        logger.debug(f"Wysyłanie wiadomości do: {recipients}")
        server.send_message(msg)
        
        # Zamknięcie połączenia
        server.quit()
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Logowanie wydajności
        if hasattr(log_performance, "__call__"):
            log_performance(logger, start_time, end_time, "send_email_notification", {
                "subject": subject,
                "recipients_count": len(recipients)
            })
        else:
            logger.debug(f"Wysłanie powiadomienia email zajęło {duration:.4f}s")
        
        logger.info(f"Wysłano powiadomienie email: {subject} do {len(recipients)} odbiorców")
        return True
    
    except ConnectionRefusedError as e:
        if hasattr(log_exception, "__call__"):
            log_exception(logger, e, {
                "function": "send_email_notification",
                "smtp_server": email_config.get("smtp_server"),
                "smtp_port": email_config.get("smtp_port")
            })
        else:
            logger.error(f"Nie można połączyć się z serwerem SMTP: {str(e)}")
        return False
    
    except smtplib.SMTPAuthenticationError as e:
        if hasattr(log_exception, "__call__"):
            log_exception(logger, e, {
                "function": "send_email_notification",
                "username": email_config.get("username")
            })
        else:
            logger.error(f"Błąd uwierzytelniania SMTP: {str(e)}")
        return False
    
    except Exception as e:
        if hasattr(log_exception, "__call__"):
            log_exception(logger, e, {"function": "send_email_notification"})
        else:
            logger.error(f"Błąd wysyłania powiadomienia email: {str(e)}")
        return False

def send_slack_notification(title: str, message: str, config: Optional[Dict[str, Any]] = None) -> bool:
    """Wysyła powiadomienie Slack."""
    if config is None:
        config = load_config()
    
    slack_config = config.get("slack", {})
    if not slack_config.get("enabled", False):
        logger.info("Powiadomienia Slack są wyłączone.")
        return False
    
    try:
        webhook_url = slack_config.get("webhook_url")
        if not webhook_url:
            logger.error("Brak URL webhooka Slack.")
            return False
        
        # Przygotowanie danych
        payload = {
            "channel": slack_config.get("channel", "#flow-notifications"),
            "username": slack_config.get("username", "taskinity Bot"),
            "text": f"*{title}*\n{message}",
            "icon_emoji": ":gear:"
        }
        
        # Wysłanie powiadomienia
        response = requests.post(webhook_url, json=payload)
        
        if response.status_code == 200:
            logger.info(f"Wysłano powiadomienie Slack: {title}")
            return True
        else:
            logger.error(f"Błąd wysyłania powiadomienia Slack: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        logger.error(f"Błąd wysyłania powiadomienia Slack: {str(e)}")
        return False

def notify_flow_status(flow_data: Dict[str, Any], status: str, error: Optional[str] = None):
    """
    Wysyła powiadomienie o statusie przepływu.
    
    Args:
        flow_data: Dane przepływu
        status: Status przepływu (STARTED, COMPLETED, FAILED)
        error: Opcjonalny komunikat błędu
    """
    config = load_config()
    if not config.get("enabled", False):
        return
    
    rules = config.get("notification_rules", {})
    
    # Sprawdzenie, czy powiadomienie powinno być wysłane
    should_notify = False
    if status == "STARTED" and rules.get("on_start", True):
        should_notify = True
    elif status == "COMPLETED" and rules.get("on_complete", True):
        should_notify = True
    elif status == "FAILED" and rules.get("on_error", True):
        should_notify = True
    
    if not should_notify:
        return
    
    # Przygotowanie treści powiadomienia
    flow_name = flow_data.get("name", "Nieznany przepływ")
    flow_id = flow_data.get("flow_id", "")
    
    if status == "STARTED":
        subject = f"Przepływ {flow_name} został uruchomiony"
        message = f"Przepływ {flow_name} (ID: {flow_id}) został uruchomiony o {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}."
    elif status == "COMPLETED":
        duration = flow_data.get("duration", 0)
        subject = f"Przepływ {flow_name} zakończony pomyślnie"
        message = f"Przepływ {flow_name} (ID: {flow_id}) zakończył się pomyślnie po {duration:.2f}s."
    elif status == "FAILED":
        subject = f"Przepływ {flow_name} zakończony błędem"
        message = f"Przepływ {flow_name} (ID: {flow_id}) zakończył się błędem: {error or 'Nieznany błąd'}"
    else:
        subject = f"Status przepływu {flow_name}: {status}"
        message = f"Przepływ {flow_name} (ID: {flow_id}) zmienił status na {status}."
    
    # Dodanie szczegółów przepływu
    if rules.get("include_details", True):
        tasks = flow_data.get("tasks", [])
        if tasks:
            message += "\n\nZadania:\n"
            for task in tasks:
                task_status = task.get("status", "")
                task_duration = task.get("duration", 0)
                message += f"- {task.get('name', '')}: {task_status} ({task_duration:.2f}s)\n"
    
    # Wysłanie powiadomień
    if config.get("email", {}).get("enabled", False):
        send_email_notification(subject, message, config)
    
    if config.get("slack", {}).get("enabled", False):
        send_slack_notification(subject, message, config)

# Inicjalizacja przy importowaniu
ensure_config()

if __name__ == "__main__":
    # Test powiadomień
    test_flow = {
        "flow_id": "test-flow-123",
        "name": "Test Flow",
        "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "tasks": [
            {"name": "Task 1", "status": "COMPLETED", "duration": 1.5},
            {"name": "Task 2", "status": "COMPLETED", "duration": 2.3}
        ]
    }
    
    print("Testowanie powiadomień...")
    notify_flow_status(test_flow, "STARTED")
    notify_flow_status(test_flow, "COMPLETED")
    notify_flow_status(test_flow, "FAILED", "Test błędu")
