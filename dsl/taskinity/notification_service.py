#!/usr/bin/env python3
"""
Moduł do obsługi powiadomień w Taskinity.
Umożliwia wysyłanie powiadomień o statusie przepływów poprzez różne kanały.
"""
import os
import json
import logging
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Opcjonalne importy dla integracji
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    from slack_sdk import WebClient
    from slack_sdk.errors import SlackApiError
    SLACK_AVAILABLE = True
except ImportError:
    SLACK_AVAILABLE = False

# Konfiguracja loggera
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("taskinity.notification_service")

# Ścieżki do katalogów
BASE_DIR = Path(__file__).parent.parent
CONFIG_DIR = BASE_DIR / "config"
NOTIFICATION_CONFIG_FILE = CONFIG_DIR / "notification_config.json"

# Upewniamy się, że katalogi istnieją
os.makedirs(CONFIG_DIR, exist_ok=True)

# Domyślna konfiguracja
DEFAULT_CONFIG = {
    "enabled": False,
    "channels": {
        "email": {
            "enabled": False,
            "smtp_server": "smtp.example.com",
            "smtp_port": 587,
            "username": "",
            "password": "",
            "from_email": "taskinity@example.com",
            "to_emails": []
        },
        "slack": {
            "enabled": False,
            "token": "",
            "channel": "#taskinity-notifications"
        },
        "webhook": {
            "enabled": False,
            "url": "",
            "headers": {}
        },
        "file": {
            "enabled": True,
            "path": str(BASE_DIR / "logs" / "notifications.log")
        }
    },
    "notification_levels": {
        "SUCCESS": ["file"],
        "ERROR": ["file", "email"],
        "WARNING": ["file"]
    }
}


def load_config() -> Dict[str, Any]:
    """
    Ładuje konfigurację powiadomień.
    
    Returns:
        Konfiguracja powiadomień
    """
    if not os.path.exists(NOTIFICATION_CONFIG_FILE):
        # Tworzenie domyślnej konfiguracji
        with open(NOTIFICATION_CONFIG_FILE, "w") as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)
        return DEFAULT_CONFIG
    
    try:
        with open(NOTIFICATION_CONFIG_FILE, "r") as f:
            config = json.load(f)
        return config
    except Exception as e:
        logger.error(f"Błąd ładowania konfiguracji powiadomień: {str(e)}")
        return DEFAULT_CONFIG


def save_config(config: Dict[str, Any]):
    """
    Zapisuje konfigurację powiadomień.
    
    Args:
        config: Konfiguracja powiadomień
    """
    try:
        with open(NOTIFICATION_CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        logger.error(f"Błąd zapisywania konfiguracji powiadomień: {str(e)}")


def send_email_notification(subject: str, message: str, details: Dict[str, Any] = None, config: Dict[str, Any] = None):
    """
    Wysyła powiadomienie e-mail.
    
    Args:
        subject: Temat wiadomości
        message: Treść wiadomości
        details: Szczegóły powiadomienia
        config: Konfiguracja powiadomień
    """
    if config is None:
        config = load_config()
    
    email_config = config.get("channels", {}).get("email", {})
    
    if not email_config.get("enabled", False):
        logger.info("Powiadomienia e-mail są wyłączone")
        return
    
    smtp_server = email_config.get("smtp_server")
    smtp_port = email_config.get("smtp_port", 587)
    username = email_config.get("username")
    password = email_config.get("password")
    from_email = email_config.get("from_email")
    to_emails = email_config.get("to_emails", [])
    
    if not smtp_server or not from_email or not to_emails:
        logger.error("Niepełna konfiguracja powiadomień e-mail")
        return
    
    try:
        # Tworzenie wiadomości
        msg = MIMEMultipart()
        msg["From"] = from_email
        msg["To"] = ", ".join(to_emails)
        msg["Subject"] = subject
        
        # Dodanie treści
        body = message
        if details:
            body += "\n\nSzczegóły:\n" + json.dumps(details, indent=2)
        
        msg.attach(MIMEText(body, "plain"))
        
        # Wysłanie wiadomości
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            if username and password:
                server.login(username, password)
            server.send_message(msg)
        
        logger.info(f"Wysłano powiadomienie e-mail do: {', '.join(to_emails)}")
    
    except Exception as e:
        logger.error(f"Błąd wysyłania powiadomienia e-mail: {str(e)}")


def send_slack_notification(subject: str, message: str, details: Dict[str, Any] = None, config: Dict[str, Any] = None):
    """
    Wysyła powiadomienie na Slack.
    
    Args:
        subject: Temat wiadomości
        message: Treść wiadomości
        details: Szczegóły powiadomienia
        config: Konfiguracja powiadomień
    """
    if not SLACK_AVAILABLE:
        logger.warning("Biblioteka slack_sdk nie jest zainstalowana")
        return
    
    if config is None:
        config = load_config()
    
    slack_config = config.get("channels", {}).get("slack", {})
    
    if not slack_config.get("enabled", False):
        logger.info("Powiadomienia Slack są wyłączone")
        return
    
    token = slack_config.get("token")
    channel = slack_config.get("channel")
    
    if not token or not channel:
        logger.error("Niepełna konfiguracja powiadomień Slack")
        return
    
    try:
        # Tworzenie klienta Slack
        client = WebClient(token=token)
        
        # Tworzenie treści wiadomości
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": subject
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": message
                }
            }
        ]
        
        if details:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Szczegóły:*\n```{json.dumps(details, indent=2)}```"
                }
            })
        
        # Wysłanie wiadomości
        response = client.chat_postMessage(
            channel=channel,
            blocks=blocks,
            text=subject  # Fallback dla powiadomień
        )
        
        logger.info(f"Wysłano powiadomienie Slack do kanału: {channel}")
    
    except SlackApiError as e:
        logger.error(f"Błąd wysyłania powiadomienia Slack: {str(e)}")
    except Exception as e:
        logger.error(f"Nieoczekiwany błąd Slack: {str(e)}")


def send_webhook_notification(subject: str, message: str, details: Dict[str, Any] = None, config: Dict[str, Any] = None):
    """
    Wysyła powiadomienie przez webhook.
    
    Args:
        subject: Temat wiadomości
        message: Treść wiadomości
        details: Szczegóły powiadomienia
        config: Konfiguracja powiadomień
    """
    if not REQUESTS_AVAILABLE:
        logger.warning("Biblioteka requests nie jest zainstalowana")
        return
    
    if config is None:
        config = load_config()
    
    webhook_config = config.get("channels", {}).get("webhook", {})
    
    if not webhook_config.get("enabled", False):
        logger.info("Powiadomienia webhook są wyłączone")
        return
    
    url = webhook_config.get("url")
    headers = webhook_config.get("headers", {})
    
    if not url:
        logger.error("Niepełna konfiguracja powiadomień webhook")
        return
    
    try:
        # Przygotowanie danych
        payload = {
            "subject": subject,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "details": details
        }
        
        # Wysłanie żądania
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        
        logger.info(f"Wysłano powiadomienie webhook do: {url}")
    
    except Exception as e:
        logger.error(f"Błąd wysyłania powiadomienia webhook: {str(e)}")


def send_file_notification(subject: str, message: str, details: Dict[str, Any] = None, config: Dict[str, Any] = None):
    """
    Zapisuje powiadomienie do pliku.
    
    Args:
        subject: Temat wiadomości
        message: Treść wiadomości
        details: Szczegóły powiadomienia
        config: Konfiguracja powiadomień
    """
    if config is None:
        config = load_config()
    
    file_config = config.get("channels", {}).get("file", {})
    
    if not file_config.get("enabled", False):
        logger.info("Powiadomienia plikowe są wyłączone")
        return
    
    file_path = file_config.get("path")
    
    if not file_path:
        logger.error("Niepełna konfiguracja powiadomień plikowych")
        return
    
    try:
        # Upewnienie się, że katalog istnieje
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Przygotowanie treści
        timestamp = datetime.now().isoformat()
        content = f"[{timestamp}] {subject}: {message}\n"
        
        if details:
            content += f"Szczegóły: {json.dumps(details)}\n"
        
        content += "-" * 80 + "\n"
        
        # Zapisanie do pliku
        with open(file_path, "a") as f:
            f.write(content)
        
        logger.info(f"Zapisano powiadomienie do pliku: {file_path}")
    
    except Exception as e:
        logger.error(f"Błąd zapisywania powiadomienia do pliku: {str(e)}")


def notify_flow_status(flow_id: str, status: str, message: str, details: Dict[str, Any] = None):
    """
    Wysyła powiadomienie o statusie przepływu.
    
    Args:
        flow_id: Identyfikator przepływu
        status: Status przepływu (SUCCESS, ERROR, WARNING)
        message: Treść powiadomienia
        details: Szczegóły powiadomienia
    """
    config = load_config()
    
    if not config.get("enabled", False):
        logger.info("Powiadomienia są wyłączone")
        return
    
    # Określenie kanałów dla danego poziomu powiadomienia
    notification_levels = config.get("notification_levels", {})
    channels = notification_levels.get(status, ["file"])
    
    # Przygotowanie tematu
    subject = f"Taskinity Flow {flow_id} - {status}"
    
    # Wysłanie powiadomień przez odpowiednie kanały
    for channel in channels:
        if channel == "email":
            send_email_notification(subject, message, details, config)
        elif channel == "slack":
            send_slack_notification(subject, message, details, config)
        elif channel == "webhook":
            send_webhook_notification(subject, message, details, config)
        elif channel == "file":
            send_file_notification(subject, message, details, config)


def configure_notifications(enabled: bool = None, 
                           email_config: Dict[str, Any] = None,
                           slack_config: Dict[str, Any] = None,
                           webhook_config: Dict[str, Any] = None,
                           file_config: Dict[str, Any] = None,
                           notification_levels: Dict[str, List[str]] = None) -> Dict[str, Any]:
    """
    Konfiguruje system powiadomień.
    
    Args:
        enabled: Czy powiadomienia są włączone
        email_config: Konfiguracja powiadomień e-mail
        slack_config: Konfiguracja powiadomień Slack
        webhook_config: Konfiguracja powiadomień webhook
        file_config: Konfiguracja powiadomień plikowych
        notification_levels: Poziomy powiadomień
        
    Returns:
        Zaktualizowana konfiguracja
    """
    config = load_config()
    
    # Aktualizacja głównego przełącznika
    if enabled is not None:
        config["enabled"] = enabled
    
    # Aktualizacja konfiguracji e-mail
    if email_config:
        current_email_config = config.get("channels", {}).get("email", {})
        current_email_config.update(email_config)
        config.setdefault("channels", {})["email"] = current_email_config
    
    # Aktualizacja konfiguracji Slack
    if slack_config:
        current_slack_config = config.get("channels", {}).get("slack", {})
        current_slack_config.update(slack_config)
        config.setdefault("channels", {})["slack"] = current_slack_config
    
    # Aktualizacja konfiguracji webhook
    if webhook_config:
        current_webhook_config = config.get("channels", {}).get("webhook", {})
        current_webhook_config.update(webhook_config)
        config.setdefault("channels", {})["webhook"] = current_webhook_config
    
    # Aktualizacja konfiguracji plikowej
    if file_config:
        current_file_config = config.get("channels", {}).get("file", {})
        current_file_config.update(file_config)
        config.setdefault("channels", {})["file"] = current_file_config
    
    # Aktualizacja poziomów powiadomień
    if notification_levels:
        config["notification_levels"] = notification_levels
    
    # Zapisanie konfiguracji
    save_config(config)
    
    return config


def test_notification(channel: str) -> bool:
    """
    Testuje kanał powiadomień.
    
    Args:
        channel: Kanał do przetestowania ('email', 'slack', 'webhook', 'file')
        
    Returns:
        True, jeśli test się powiódł
    """
    try:
        subject = f"Taskinity - Test powiadomień {channel}"
        message = f"To jest testowe powiadomienie dla kanału {channel}."
        details = {
            "test": True,
            "timestamp": datetime.now().isoformat(),
            "channel": channel
        }
        
        if channel == "email":
            send_email_notification(subject, message, details)
        elif channel == "slack":
            send_slack_notification(subject, message, details)
        elif channel == "webhook":
            send_webhook_notification(subject, message, details)
        elif channel == "file":
            send_file_notification(subject, message, details)
        else:
            logger.error(f"Nieznany kanał powiadomień: {channel}")
            return False
        
        return True
    
    except Exception as e:
        logger.error(f"Błąd testowania powiadomień {channel}: {str(e)}")
        return False


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Użycie: python notification_service.py [test|configure]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "test" and len(sys.argv) >= 3:
        channel = sys.argv[2]
        print(f"Testowanie kanału powiadomień: {channel}")
        result = test_notification(channel)
        print(f"Wynik: {'Sukces' if result else 'Błąd'}")
    
    elif command == "configure":
        print("Konfiguracja powiadomień")
        
        # Przykładowa konfiguracja
        enabled = input("Włączyć powiadomienia? (t/n): ").lower() == 't'
        
        email_enabled = input("Włączyć powiadomienia e-mail? (t/n): ").lower() == 't'
        email_config = None
        if email_enabled:
            email_config = {
                "enabled": True,
                "smtp_server": input("Serwer SMTP: "),
                "smtp_port": int(input("Port SMTP: ")),
                "username": input("Nazwa użytkownika: "),
                "password": input("Hasło: "),
                "from_email": input("Adres nadawcy: "),
                "to_emails": [e.strip() for e in input("Adresy odbiorców (oddzielone przecinkami): ").split(",")]
            }
        
        slack_enabled = input("Włączyć powiadomienia Slack? (t/n): ").lower() == 't'
        slack_config = None
        if slack_enabled:
            slack_config = {
                "enabled": True,
                "token": input("Token Slack: "),
                "channel": input("Kanał Slack: ")
            }
        
        webhook_enabled = input("Włączyć powiadomienia webhook? (t/n): ").lower() == 't'
        webhook_config = None
        if webhook_enabled:
            webhook_config = {
                "enabled": True,
                "url": input("URL webhook: ")
            }
        
        file_enabled = input("Włączyć powiadomienia plikowe? (t/n): ").lower() == 't'
        file_config = None
        if file_enabled:
            file_config = {
                "enabled": True,
                "path": input("Ścieżka do pliku: ")
            }
        
        # Aktualizacja konfiguracji
        config = configure_notifications(
            enabled=enabled,
            email_config=email_config,
            slack_config=slack_config,
            webhook_config=webhook_config,
            file_config=file_config
        )
        
        print("Konfiguracja zaktualizowana")
    
    else:
        print("Nieznane polecenie")
        print("Użycie: python notification_service.py [test|configure]")
