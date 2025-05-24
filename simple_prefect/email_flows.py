#!/usr/bin/env python3
"""
Automatyzacja przetwarzania e-maili z wykorzystaniem Prefect.
Zapewnia prostą wizualizację procesów, monitorowanie i debugowanie.
"""
import os
import yaml
import time
import email
import imaplib
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

# Prefect
from prefect import flow, task, get_run_logger
from prefect.logging import get_run_logger
from prefect.task_runners import SequentialTaskRunner

# Dodatkowe biblioteki
from dotenv import load_dotenv
from loguru import logger

# Ładowanie zmiennych środowiskowych
load_dotenv()

# Konfiguracja loggera
logger.remove()
logger.add(
    "logs/email_flow_{time}.log", 
    rotation="500 MB", 
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
)
logger.add(lambda msg: print(msg), level=os.getenv("LOG_LEVEL", "INFO"))

# ===== Funkcje pomocnicze =====

def load_config():
    """Ładowanie konfiguracji z pliku YAML i zmiennych środowiskowych"""
    config = {
        "email": {
            "imap": {
                "host": os.getenv("EMAIL_IMAP_HOST", "localhost"),
                "port": int(os.getenv("EMAIL_IMAP_PORT", 1143)),
                "username": os.getenv("EMAIL_IMAP_USERNAME", "test@example.com"),
                "password": os.getenv("EMAIL_IMAP_PASSWORD", "password"),
                "folder": os.getenv("EMAIL_IMAP_FOLDER", "INBOX"),
                "check_interval": int(os.getenv("EMAIL_IMAP_CHECK_INTERVAL", 30))
            },
            "smtp": {
                "host": os.getenv("EMAIL_SMTP_HOST", "localhost"),
                "port": int(os.getenv("EMAIL_SMTP_PORT", 1025)),
                "username": os.getenv("EMAIL_SMTP_USERNAME", "test@example.com"),
                "password": os.getenv("EMAIL_SMTP_PASSWORD", "password")
            }
        },
        "attachments": {
            "save_path": os.getenv("ATTACHMENTS_PATH", "./attachments")
        }
    }
    
    return config

# ===== Taski Prefect =====

@task(name="Pobieranie nieprzeczytanych e-maili", 
      description="Pobiera nieprzeczytane e-maile z serwera IMAP",
      retries=3, 
      retry_delay_seconds=5)
def fetch_emails() -> List[Dict[str, Any]]:
    """
    Pobiera nieprzeczytane e-maile z serwera IMAP
    
    Returns:
        List[Dict[str, Any]]: Lista słowników reprezentujących e-maile
    """
    logger = get_run_logger()
    config = load_config()
    
    # Konfiguracja IMAP
    imap_config = config["email"]["imap"]
    
    logger.info(f"Łączenie z serwerem IMAP: {imap_config['host']}:{imap_config['port']}")
    
    try:
        # Połączenie z serwerem IMAP
        mail = imaplib.IMAP4(imap_config["host"], imap_config["port"])
        
        # Logowanie
        mail.login(imap_config["username"], imap_config["password"])
        logger.info(f"Zalogowano do serwera IMAP jako {imap_config['username']}")
        
        # Wybór folderu
        mail.select(imap_config["folder"])
        
        # Wyszukiwanie nieprzeczytanych e-maili
        status, data = mail.search(None, "UNSEEN")
        
        if status != "OK":
            logger.error(f"Błąd podczas wyszukiwania e-maili: {status}")
            return []
        
        email_ids = data[0].split()
        logger.info(f"Znaleziono {len(email_ids)} nieprzeczytanych e-maili")
        
        emails = []
        
        # Pobieranie e-maili
        for email_id in email_ids:
            status, data = mail.fetch(email_id, "(RFC822)")
            
            if status != "OK":
                logger.error(f"Błąd podczas pobierania e-maila {email_id}: {status}")
                continue
            
            raw_email = data[0][1]
            email_message = email.message_from_bytes(raw_email)
            
            # Tworzenie słownika reprezentującego e-mail
            email_dict = {
                "id": email_id.decode(),
                "subject": email_message["Subject"],
                "from": email_message["From"],
                "to": email_message["To"],
                "date": email_message["Date"],
                "body": "",
                "attachments": []
            }
            
            # Pobieranie treści e-maila
            if email_message.is_multipart():
                for part in email_message.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))
                    
                    # Pobieranie treści tekstowej
                    if content_type == "text/plain" and "attachment" not in content_disposition:
                        email_dict["body"] = part.get_payload(decode=True).decode()
                    
                    # Pobieranie informacji o załącznikach
                    if "attachment" in content_disposition:
                        filename = part.get_filename()
                        if filename:
                            email_dict["attachments"].append({
                                "filename": filename,
                                "content_type": content_type,
                                "data": part.get_payload(decode=True)
                            })
            else:
                # E-mail nie jest wieloczęściowy
                email_dict["body"] = email_message.get_payload(decode=True).decode()
            
            emails.append(email_dict)
        
        # Zamykanie połączenia
        mail.close()
        mail.logout()
        
        return emails
    
    except Exception as e:
        logger.error(f"Błąd podczas pobierania e-maili: {str(e)}")
        return []

@task(name="Klasyfikacja e-maila", 
      description="Klasyfikuje e-mail na podstawie tematu i treści",
      retries=2)
def classify_email(email: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
    """
    Klasyfikuje e-mail na podstawie tematu i treści
    
    Args:
        email (Dict[str, Any]): Słownik reprezentujący e-mail
        
    Returns:
        Tuple[Dict[str, Any], str]: Krotka (e-mail, typ)
    """
    logger = get_run_logger()
    
    subject = email["subject"].lower()
    body = email["body"].lower()
    
    # Klasyfikacja na podstawie tematu
    if "urgent" in subject or "pilne" in subject:
        email_type = "urgent"
        logger.info(f"E-mail '{email['subject']}' sklasyfikowany jako PILNY")
    elif "report" in subject or "raport" in subject:
        email_type = "report"
        logger.info(f"E-mail '{email['subject']}' sklasyfikowany jako RAPORT")
    else:
        email_type = "regular"
        logger.info(f"E-mail '{email['subject']}' sklasyfikowany jako ZWYKŁY")
    
    # Dodanie typu do e-maila
    email["type"] = email_type
    
    return email, email_type

@task(name="Zapisywanie załączników", 
      description="Zapisuje załączniki e-maila na dysku",
      retries=3)
def save_attachments(email: Dict[str, Any]) -> Dict[str, Any]:
    """
    Zapisuje załączniki e-maila na dysku
    
    Args:
        email (Dict[str, Any]): Słownik reprezentujący e-mail
        
    Returns:
        Dict[str, Any]: Zaktualizowany słownik e-maila
    """
    logger = get_run_logger()
    config = load_config()
    
    # Ścieżka do katalogu z załącznikami
    attachments_dir = Path(config["attachments"]["save_path"])
    attachments_dir.mkdir(exist_ok=True)
    
    # Zapisywanie załączników
    saved_attachments = []
    
    for attachment in email["attachments"]:
        filename = attachment["filename"]
        data = attachment["data"]
        
        # Tworzenie ścieżki do pliku
        file_path = attachments_dir / filename
        
        try:
            # Zapisywanie pliku
            with open(file_path, "wb") as f:
                f.write(data)
            
            logger.info(f"Zapisano załącznik: {filename}")
            
            # Dodawanie informacji o zapisanym załączniku
            saved_attachments.append({
                "filename": filename,
                "path": str(file_path),
                "content_type": attachment["content_type"],
                "size": len(data)
            })
        
        except Exception as e:
            logger.error(f"Błąd podczas zapisywania załącznika {filename}: {str(e)}")
    
    # Aktualizacja e-maila
    email["saved_attachments"] = saved_attachments
    
    return email

@task(name="Wysyłanie odpowiedzi", 
      description="Wysyła odpowiedź na e-mail",
      retries=3, 
      retry_delay_seconds=5)
def send_response(email: Dict[str, Any], email_type: str) -> Dict[str, Any]:
    """
    Wysyła odpowiedź na e-mail
    
    Args:
        email (Dict[str, Any]): Słownik reprezentujący e-mail
        email_type (str): Typ e-maila
        
    Returns:
        Dict[str, Any]: Zaktualizowany słownik e-maila
    """
    logger = get_run_logger()
    config = load_config()
    
    # Konfiguracja SMTP
    smtp_config = config["email"]["smtp"]
    
    # Przygotowanie odpowiedzi w zależności od typu e-maila
    if email_type == "urgent":
        subject = f"RE: {email['subject']} - POTWIERDZENIE ODBIORU PILNEJ WIADOMOŚCI"
        body = f"""
        Szanowny Nadawco,
        
        Potwierdzamy otrzymanie Twojej pilnej wiadomości.
        Zajmiemy się nią w pierwszej kolejności.
        
        Treść Twojej wiadomości:
        ------------------------
        {email['body']}
        ------------------------
        
        Z poważaniem,
        System Automatyzacji E-mail
        """
    elif email_type == "report":
        subject = f"RE: {email['subject']} - POTWIERDZENIE ODBIORU RAPORTU"
        body = f"""
        Szanowny Nadawco,
        
        Potwierdzamy otrzymanie Twojego raportu.
        Raport został zapisany w systemie.
        
        Z poważaniem,
        System Automatyzacji E-mail
        """
    else:
        subject = f"RE: {email['subject']} - POTWIERDZENIE ODBIORU"
        body = f"""
        Szanowny Nadawco,
        
        Potwierdzamy otrzymanie Twojej wiadomości.
        
        Z poważaniem,
        System Automatyzacji E-mail
        """
    
    try:
        # Tworzenie wiadomości
        msg = MIMEMultipart()
        msg["From"] = smtp_config["username"]
        msg["To"] = email["from"]
        msg["Subject"] = subject
        
        # Dodawanie treści
        msg.attach(MIMEText(body, "plain"))
        
        # Połączenie z serwerem SMTP
        with smtplib.SMTP(smtp_config["host"], smtp_config["port"]) as server:
            # Logowanie
            if smtp_config["username"] and smtp_config["password"]:
                try:
                    server.login(smtp_config["username"], smtp_config["password"])
                except Exception as e:
                    logger.warning(f"Nie udało się zalogować do serwera SMTP: {str(e)}")
            
            # Wysyłanie wiadomości
            server.sendmail(smtp_config["username"], email["from"], msg.as_string())
        
        logger.info(f"Wysłano odpowiedź na e-mail '{email['subject']}'")
        
        # Aktualizacja e-maila
        email["response"] = {
            "subject": subject,
            "body": body,
            "sent_at": datetime.now().isoformat()
        }
        
        return email
    
    except Exception as e:
        logger.error(f"Błąd podczas wysyłania odpowiedzi: {str(e)}")
        
        # Aktualizacja e-maila
        email["response_error"] = str(e)
        
        return email

# ===== Przepływy Prefect =====

@flow(name="Przetwarzanie pilnego e-maila",
      description="Przepływ przetwarzania pilnego e-maila",
      task_runner=SequentialTaskRunner())
def process_urgent_email(email: Dict[str, Any]) -> Dict[str, Any]:
    """
    Przepływ przetwarzania pilnego e-maila
    
    Args:
        email (Dict[str, Any]): Słownik reprezentujący e-mail
        
    Returns:
        Dict[str, Any]: Zaktualizowany słownik e-maila
    """
    logger = get_run_logger()
    logger.info(f"Rozpoczęto przetwarzanie pilnego e-maila: {email['subject']}")
    
    # Zapisywanie załączników
    email = save_attachments(email)
    
    # Wysyłanie odpowiedzi
    email = send_response(email, "urgent")
    
    logger.info(f"Zakończono przetwarzanie pilnego e-maila: {email['subject']}")
    
    return email

@flow(name="Przetwarzanie raportu",
      description="Przepływ przetwarzania e-maila z raportem",
      task_runner=SequentialTaskRunner())
def process_report_email(email: Dict[str, Any]) -> Dict[str, Any]:
    """
    Przepływ przetwarzania e-maila z raportem
    
    Args:
        email (Dict[str, Any]): Słownik reprezentujący e-mail
        
    Returns:
        Dict[str, Any]: Zaktualizowany słownik e-maila
    """
    logger = get_run_logger()
    logger.info(f"Rozpoczęto przetwarzanie raportu: {email['subject']}")
    
    # Zapisywanie załączników
    email = save_attachments(email)
    
    # Wysyłanie odpowiedzi
    email = send_response(email, "report")
    
    logger.info(f"Zakończono przetwarzanie raportu: {email['subject']}")
    
    return email

@flow(name="Przetwarzanie zwykłego e-maila",
      description="Przepływ przetwarzania zwykłego e-maila",
      task_runner=SequentialTaskRunner())
def process_regular_email(email: Dict[str, Any]) -> Dict[str, Any]:
    """
    Przepływ przetwarzania zwykłego e-maila
    
    Args:
        email (Dict[str, Any]): Słownik reprezentujący e-mail
        
    Returns:
        Dict[str, Any]: Zaktualizowany słownik e-maila
    """
    logger = get_run_logger()
    logger.info(f"Rozpoczęto przetwarzanie zwykłego e-maila: {email['subject']}")
    
    # Zapisywanie załączników
    email = save_attachments(email)
    
    # Wysyłanie odpowiedzi
    email = send_response(email, "regular")
    
    logger.info(f"Zakończono przetwarzanie zwykłego e-maila: {email['subject']}")
    
    return email

@flow(name="Główny przepływ przetwarzania e-maili",
      description="Główny przepływ przetwarzania e-maili",
      task_runner=SequentialTaskRunner())
def main_email_flow():
    """
    Główny przepływ przetwarzania e-maili
    """
    logger = get_run_logger()
    logger.info("Rozpoczęto główny przepływ przetwarzania e-maili")
    
    # Pobieranie e-maili
    emails = fetch_emails()
    
    processed_emails = []
    
    # Przetwarzanie e-maili
    for email in emails:
        # Klasyfikacja e-maila
        email, email_type = classify_email(email)
        
        # Przetwarzanie w zależności od typu
        if email_type == "urgent":
            processed_email = process_urgent_email(email)
        elif email_type == "report":
            processed_email = process_report_email(email)
        else:
            processed_email = process_regular_email(email)
        
        processed_emails.append(processed_email)
    
    logger.info(f"Zakończono główny przepływ przetwarzania e-maili. Przetworzono {len(processed_emails)} e-maili.")
    
    return processed_emails

# ===== Funkcja cyklicznego uruchamiania =====

def run_email_flow_periodically():
    """
    Cyklicznie uruchamia przepływ przetwarzania e-maili
    """
    config = load_config()
    check_interval = config["email"]["imap"]["check_interval"]
    
    logger.info(f"Uruchamianie cyklicznego przetwarzania e-maili co {check_interval} sekund")
    
    while True:
        try:
            # Uruchamianie przepływu
            main_email_flow()
            
            # Oczekiwanie na następne uruchomienie
            logger.info(f"Następne sprawdzenie e-maili za {check_interval} sekund")
            time.sleep(check_interval)
        
        except KeyboardInterrupt:
            logger.info("Przerwano cykliczne przetwarzanie e-maili")
            break
        
        except Exception as e:
            logger.error(f"Błąd podczas cyklicznego przetwarzania e-maili: {str(e)}")
            # Krótkie oczekiwanie przed ponowną próbą
            time.sleep(5)

# ===== Główna funkcja =====

if __name__ == "__main__":
    # Tworzenie katalogów
    os.makedirs("logs", exist_ok=True)
    os.makedirs("attachments", exist_ok=True)
    
    # Uruchamianie cyklicznego przetwarzania e-maili
    run_email_flow_periodically()
