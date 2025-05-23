#!/usr/bin/env python3
"""
Prosty system automatyzacji przetwarzania e-maili z wykorzystaniem koncepcji Apache Camel.
Zaprojektowany z myślą o łatwości użycia i monitorowaniu.
"""
import os
import yaml
import time
import email
import imaplib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from loguru import logger
from dotenv import load_dotenv
from functools import wraps
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Ładowanie zmiennych środowiskowych
load_dotenv()

# Konfiguracja loggera
logger.remove()
logger.add(
    "logs/email_flow_{time}.log", 
    rotation="500 MB", 
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
)
logger.add(lambda msg: print(msg), level="INFO")

# Ładowanie konfiguracji
def load_config():
    try:
        # Ładowanie zmiennych środowiskowych
        load_dotenv()
        
        # Ładowanie pliku konfiguracyjnego
        with open('config.yaml', 'r') as f:
            config_str = f.read()
        
        # Zastępowanie zmiennych środowiskowych
        import re
        import os
        
        pattern = r'\${([A-Za-z0-9_]+)}'
        
        def replace_env_var(match):
            env_var = match.group(1)
            value = os.getenv(env_var)
            if value is None:
                # Domyślne wartości dla często używanych zmiennych
                defaults = {
                    'EMAIL_IMAP_HOST': 'localhost',
                    'EMAIL_IMAP_PORT': '1143',
                    'EMAIL_IMAP_USERNAME': 'test@example.com',
                    'EMAIL_IMAP_PASSWORD': 'password',
                    'EMAIL_IMAP_FOLDER': 'INBOX',
                    'EMAIL_IMAP_CHECK_INTERVAL': '30',
                    'EMAIL_SMTP_HOST': 'localhost',
                    'EMAIL_SMTP_PORT': '1025',
                    'EMAIL_SMTP_USERNAME': 'test@example.com',
                    'EMAIL_SMTP_PASSWORD': 'password',
                    'ATTACHMENTS_PATH': './attachments',
                    'LOG_LEVEL': 'INFO',
                    'DASHBOARD_PORT': '8000',
                    'METRICS_ENABLED': 'true'
                }
                if env_var in defaults:
                    logger.info(f"Używam domyślnej wartości dla {env_var}: {defaults[env_var]}")
                    return defaults[env_var]
                logger.warning(f"Zmienna środowiskowa {env_var} nie jest ustawiona!")
                return match.group(0)  # Pozostawienie oryginalnego tekstu
            return value
        
        config_str = re.sub(pattern, replace_env_var, config_str)
        
        # Parsowanie YAML
        config = yaml.safe_load(config_str)
        return config
    except Exception as e:
        logger.error(f"Błąd podczas ładowania konfiguracji: {str(e)}")
        return {}

config = load_config()

# ===== Dekoratory do monitorowania i śledzenia przepływów =====

def flow_step(name=None):
    """Dekorator do oznaczania kroków przepływu"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            step_name = name or func.__name__
            logger.info(f"Krok przepływu: {step_name} - rozpoczęty")
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                logger.info(f"Krok przepływu: {step_name} - zakończony (czas: {execution_time:.2f}s)")
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(f"Krok przepływu: {step_name} - błąd: {str(e)} (czas: {execution_time:.2f}s)")
                raise
        return wrapper
    return decorator

def route(name=None):
    """Dekorator do oznaczania tras"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            route_name = name or func.__name__
            logger.info(f"Trasa: {route_name} - rozpoczęta")
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                logger.info(f"Trasa: {route_name} - zakończona (czas: {execution_time:.2f}s)")
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(f"Trasa: {route_name} - błąd: {str(e)} (czas: {execution_time:.2f}s)")
                raise
        return wrapper
    return decorator

def retry(max_attempts=3, delay=1):
    """Dekorator do ponawiania operacji w przypadku błędu"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    if attempts == max_attempts:
                        logger.error(f"Funkcja {func.__name__} nie powiodła się po {max_attempts} próbach: {str(e)}")
                        raise
                    logger.warning(f"Próba {attempts}/{max_attempts} nie powiodła się: {str(e)}. Ponowienie za {delay}s")
                    time.sleep(delay)
        return wrapper
    return decorator

# ===== Klasy do obsługi wiadomości =====

class Exchange:
    """Klasa reprezentująca wymianę wiadomości (podobnie jak w Apache Camel)"""
    def __init__(self, message=None, headers=None):
        self.message = message
        self.headers = headers or {}
        self.properties = {}
        
    def get_body(self):
        return self.message
        
    def set_body(self, body):
        self.message = body
        
    def get_header(self, name, default=None):
        return self.headers.get(name, default)
        
    def set_header(self, name, value):
        self.headers[name] = value
        
    def get_property(self, name, default=None):
        return self.properties.get(name, default)
        
    def set_property(self, name, value):
        self.properties[name] = value

# ===== Funkcje procesujące =====

@flow_step("Przetwarzanie e-maila")
def process_email(exchange):
    """Przetwarzanie e-maila i określenie jego typu"""
    message = exchange.get_body()
    
    if not message:
        logger.warning("Otrzymano pustą wiadomość")
        return
    
    # Parsowanie wiadomości
    if isinstance(message, bytes):
        email_message = email.message_from_bytes(message)
    else:
        email_message = email.message_from_string(message)
    
    # Pobieranie nagłówków
    subject = email_message.get('Subject', '')
    from_addr = email_message.get('From', '')
    date = email_message.get('Date', '')
    
    # Ustawienie nagłówków w exchange
    exchange.set_header('subject', subject)
    exchange.set_header('from', from_addr)
    exchange.set_header('date', date)
    
    # Określenie typu e-maila na podstawie tematu
    email_type = "regular"
    if "urgent" in subject.lower():
        email_type = "urgent"
    elif "report" in subject.lower():
        email_type = "report"
    
    exchange.set_header('emailType', email_type)
    exchange.set_body(email_message)
    
    logger.info(f"Przetworzono e-mail typu: {email_type}, temat: {subject}")
    return exchange

@flow_step("Zapisywanie załączników")
def save_attachments(exchange):
    """Zapisywanie załączników z e-maila"""
    email_message = exchange.get_body()
    
    if not email_message:
        logger.warning("Brak wiadomości do przetworzenia")
        return exchange
    
    # Tworzenie katalogu na załączniki
    today = datetime.now().strftime("%Y%m%d")
    attachment_dir = os.path.join(config['attachments']['save_path'], today)
    os.makedirs(attachment_dir, exist_ok=True)
    
    attachments_saved = []
    
    # Zapisywanie załączników
    if email_message.get_content_maintype() == 'multipart':
        for part in email_message.walk():
            if part.get_content_maintype() == 'multipart':
                continue
            if part.get('Content-Disposition') is None:
                continue
                
            filename = part.get_filename()
            if filename:
                filepath = os.path.join(attachment_dir, filename)
                with open(filepath, 'wb') as f:
                    f.write(part.get_payload(decode=True))
                logger.info(f"Zapisano załącznik: {filename}")
                attachments_saved.append(filename)
    
    exchange.set_header('attachments', attachments_saved)
    return exchange

@flow_step("Wysyłanie odpowiedzi")
@retry(max_attempts=3, delay=2)
def send_response(exchange):
    """Wysyłanie odpowiedzi na e-mail"""
    email_type = exchange.get_header('emailType', 'regular')
    from_addr = exchange.get_header('from', '')
    subject = exchange.get_header('subject', '')
    
    if not from_addr:
        logger.warning("Brak adresu nadawcy - nie można wysłać odpowiedzi")
        return exchange
    
    # Konfiguracja SMTP
    smtp_config = config['email']['smtp']
    
    # Treść odpowiedzi w zależności od typu e-maila
    if email_type == "urgent":
        body = "Dziękujemy za Twoją pilną wiadomość. Zajmiemy się nią priorytetowo."
    elif email_type == "report":
        body = "Dziękujemy za przesłanie raportu. Zostanie on przeanalizowany."
    else:
        body = "Dziękujemy za Twoją wiadomość. Odpowiemy najszybciej jak to możliwe."
    
    # Tworzenie wiadomości
    msg = MIMEMultipart()
    msg['From'] = smtp_config['username']
    msg['To'] = from_addr
    msg['Subject'] = f"Re: {subject}"
    msg.attach(MIMEText(body, 'plain'))
    
    # Wysyłanie odpowiedzi
    try:
        server = smtplib.SMTP(smtp_config['host'], smtp_config['port'])
        server.starttls()
        server.login(smtp_config['username'], smtp_config['password'])
        server.send_message(msg)
        server.quit()
        logger.info(f"Wysłano odpowiedź do: {from_addr}")
    except Exception as e:
        logger.error(f"Błąd podczas wysyłania odpowiedzi: {str(e)}")
        raise
    
    return exchange

# ===== Trasy (Routes) =====

@route("Pobieranie e-maili")
def fetch_emails_route():
    """Trasa pobierająca e-maile z serwera IMAP"""
    imap_config = config['email']['imap']
    
    try:
        # Połączenie z serwerem IMAP
        mail = imaplib.IMAP4_SSL(imap_config['host'], imap_config['port'])
        mail.login(imap_config['username'], imap_config['password'])
        mail.select(imap_config['folder'])
        
        # Wyszukiwanie nieprzeczytanych wiadomości
        status, messages = mail.search(None, 'UNSEEN')
        
        if status != 'OK':
            logger.error("Nie udało się wyszukać wiadomości")
            return
        
        # Pobieranie wiadomości
        for num in messages[0].split():
            status, data = mail.fetch(num, '(RFC822)')
            if status != 'OK':
                logger.error(f"Nie udało się pobrać wiadomości {num}")
                continue
            
            # Tworzenie obiektu Exchange
            exchange = Exchange(data[0][1])
            
            # Przetwarzanie wiadomości
            try:
                exchange = process_email(exchange)
                
                # Kierowanie do odpowiedniej trasy
                email_type = exchange.get_header('emailType')
                if email_type == 'urgent':
                    urgent_email_route(exchange)
                elif email_type == 'report':
                    report_email_route(exchange)
                else:
                    regular_email_route(exchange)
                
                # Oznaczanie jako przeczytane
                mail.store(num, '+FLAGS', '\\Seen')
                
            except Exception as e:
                logger.error(f"Błąd podczas przetwarzania wiadomości: {str(e)}")
        
        # Zamykanie połączenia
        mail.close()
        mail.logout()
        
    except Exception as e:
        logger.error(f"Błąd podczas pobierania e-maili: {str(e)}")

@route("Pilne e-maile")
def urgent_email_route(exchange):
    """Trasa dla pilnych e-maili"""
    logger.info(f"Przetwarzanie pilnego e-maila: {exchange.get_header('subject')}")
    
    try:
        # Zapisywanie załączników
        exchange = save_attachments(exchange)
        
        # Wysyłanie odpowiedzi
        exchange = send_response(exchange)
        
        logger.info("Zakończono przetwarzanie pilnego e-maila")
    except Exception as e:
        logger.error(f"Błąd podczas przetwarzania pilnego e-maila: {str(e)}")

@route("Raporty")
def report_email_route(exchange):
    """Trasa dla raportów"""
    logger.info(f"Przetwarzanie raportu: {exchange.get_header('subject')}")
    
    try:
        # Zapisywanie załączników
        exchange = save_attachments(exchange)
        
        logger.info("Zakończono przetwarzanie raportu")
    except Exception as e:
        logger.error(f"Błąd podczas przetwarzania raportu: {str(e)}")

@route("Zwykłe e-maile")
def regular_email_route(exchange):
    """Trasa dla zwykłych e-maili"""
    logger.info(f"Przetwarzanie zwykłego e-maila: {exchange.get_header('subject')}")
    
    # Tutaj można dodać dodatkową logikę dla zwykłych e-maili
    
    logger.info("Zakończono przetwarzanie zwykłego e-maila")

# ===== Monitorowanie katalogu z załącznikami =====

class AttachmentWatcher(FileSystemEventHandler):
    """Klasa monitorująca zmiany w katalogu z załącznikami"""
    
    def on_created(self, event):
        if not event.is_directory:
            logger.info(f"Nowy załącznik: {event.src_path}")
    
    def on_modified(self, event):
        if not event.is_directory:
            logger.info(f"Zmodyfikowano załącznik: {event.src_path}")

def start_attachment_watcher():
    """Uruchamia monitorowanie katalogu z załącznikami"""
    attachment_dir = config['attachments']['save_path']
    os.makedirs(attachment_dir, exist_ok=True)
    
    event_handler = AttachmentWatcher()
    observer = Observer()
    observer.schedule(event_handler, attachment_dir, recursive=True)
    observer.start()
    logger.info(f"Rozpoczęto monitorowanie katalogu załączników: {attachment_dir}")
    return observer

# ===== Główna pętla =====

def main():
    """Główna funkcja programu"""
    logger.info("Uruchamianie systemu automatyzacji przetwarzania e-maili")
    
    # Tworzenie katalogu na logi
    os.makedirs("logs", exist_ok=True)
    
    # Tworzenie katalogu na załączniki
    os.makedirs(config['attachments']['save_path'], exist_ok=True)
    
    # Uruchamianie monitorowania katalogu z załącznikami
    observer = start_attachment_watcher()
    
    try:
        # Główna pętla programu
        while True:
            # Pobieranie i przetwarzanie e-maili
            fetch_emails_route()
            
            # Przerwa przed kolejnym sprawdzeniem
            logger.info(f"Oczekiwanie {config['email']['imap']['check_interval']} sekund przed kolejnym sprawdzeniem")
            time.sleep(config['email']['imap']['check_interval'])
    except KeyboardInterrupt:
        logger.info("Zatrzymywanie systemu...")
        observer.stop()
    finally:
        observer.join()
        logger.info("System zatrzymany")

if __name__ == "__main__":
    main()
