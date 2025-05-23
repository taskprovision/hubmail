#!/usr/bin/env python3
"""
Testy dla systemu przetwarzania e-maili.
"""
import os
import sys
import time
import pytest
import smtplib
import imaplib
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from pathlib import Path
from dotenv import load_dotenv

# Dodanie katalogu głównego do ścieżki, aby umożliwić import modułów
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Ładowanie zmiennych środowiskowych
load_dotenv()

# Konfiguracja testów
SMTP_HOST = os.getenv('EMAIL_SMTP_HOST', 'mailhog')
SMTP_PORT = int(os.getenv('EMAIL_SMTP_PORT', 1025))
IMAP_HOST = os.getenv('EMAIL_IMAP_HOST', 'mailhog')
IMAP_PORT = int(os.getenv('EMAIL_IMAP_PORT', 1143))
EMAIL_USERNAME = os.getenv('EMAIL_IMAP_USERNAME', 'test@example.com')
EMAIL_PASSWORD = os.getenv('EMAIL_IMAP_PASSWORD', 'password')
TEST_SENDER = os.getenv('TEST_EMAIL_SENDER', 'sender@example.com')
TEST_RECIPIENT = os.getenv('TEST_EMAIL_RECIPIENT', 'test@example.com')
ATTACHMENT_PATH = os.getenv('TEST_ATTACHMENT_PATH', './test_data/attachments')

def send_test_email(subject, body, attachments=None):
    """
    Wysyła testowy e-mail z opcjonalnymi załącznikami.
    
    Args:
        subject (str): Temat e-maila
        body (str): Treść e-maila
        attachments (list, optional): Lista ścieżek do załączników
        
    Returns:
        bool: True jeśli wysłanie się powiodło, False w przeciwnym razie
    """
    msg = MIMEMultipart()
    msg['From'] = TEST_SENDER
    msg['To'] = TEST_RECIPIENT
    msg['Subject'] = subject
    
    # Dodawanie treści
    msg.attach(MIMEText(body, 'plain'))
    
    # Dodawanie załączników
    if attachments:
        for attachment_path in attachments:
            try:
                with open(attachment_path, 'rb') as file:
                    attachment = MIMEApplication(file.read())
                    attachment_name = Path(attachment_path).name
                    attachment.add_header('Content-Disposition', f'attachment; filename="{attachment_name}"')
                    msg.attach(attachment)
            except Exception as e:
                print(f"Błąd podczas dodawania załącznika {attachment_path}: {str(e)}")
    
    # Wysyłanie e-maila
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.sendmail(TEST_SENDER, TEST_RECIPIENT, msg.as_string())
            return True
    except Exception as e:
        print(f"Błąd podczas wysyłania e-maila: {str(e)}")
        return False

def check_email_received(subject, timeout=30):
    """
    Sprawdza, czy e-mail o podanym temacie został odebrany.
    
    Args:
        subject (str): Temat e-maila do sprawdzenia
        timeout (int): Maksymalny czas oczekiwania w sekundach
        
    Returns:
        bool: True jeśli e-mail został odebrany, False w przeciwnym razie
    """
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            # Połączenie z serwerem IMAP
            mail = imaplib.IMAP4(IMAP_HOST, IMAP_PORT)
            
            # Próba logowania (może nie być wymagana w MailHog)
            try:
                mail.login(EMAIL_USERNAME, EMAIL_PASSWORD)
            except:
                pass
            
            # Wybór skrzynki odbiorczej
            mail.select('INBOX')
            
            # Wyszukiwanie e-maili o podanym temacie
            _, data = mail.search(None, f'SUBJECT "{subject}"')
            
            # Sprawdzanie, czy znaleziono e-maile
            if data[0]:
                mail.close()
                mail.logout()
                return True
            
            # Zamykanie połączenia
            mail.close()
            mail.logout()
            
            # Oczekiwanie przed kolejną próbą
            time.sleep(2)
        except Exception as e:
            print(f"Błąd podczas sprawdzania e-maila: {str(e)}")
            time.sleep(2)
    
    return False

@pytest.fixture
def setup_test_environment():
    """Przygotowanie środowiska testowego"""
    # Tworzenie katalogów
    os.makedirs('./attachments', exist_ok=True)
    os.makedirs('./logs', exist_ok=True)
    
    # Czyszczenie katalogów
    for file in Path('./attachments').glob('*'):
        if file.is_file():
            file.unlink()
    
    yield
    
    # Sprzątanie po testach
    # (opcjonalne, można dodać dodatkowe czyszczenie)

def test_send_regular_email(setup_test_environment):
    """Test wysyłania zwykłego e-maila"""
    subject = f"Test zwykły {time.time()}"
    body = "To jest testowa wiadomość"
    
    # Wysyłanie e-maila
    assert send_test_email(subject, body)
    
    # Sprawdzanie, czy e-mail został odebrany
    assert check_email_received(subject)

def test_send_urgent_email(setup_test_environment):
    """Test wysyłania pilnego e-maila"""
    subject = f"URGENT: Test pilny {time.time()}"
    body = "To jest pilna testowa wiadomość"
    
    # Wysyłanie e-maila
    assert send_test_email(subject, body)
    
    # Sprawdzanie, czy e-mail został odebrany
    assert check_email_received(subject)

def test_send_report_email(setup_test_environment):
    """Test wysyłania raportu"""
    subject = f"REPORT: Test raport {time.time()}"
    body = "To jest testowy raport"
    
    # Przygotowanie załącznika
    attachments = [os.path.join(ATTACHMENT_PATH, 'report.csv')]
    
    # Wysyłanie e-maila
    assert send_test_email(subject, body, attachments)
    
    # Sprawdzanie, czy e-mail został odebrany
    assert check_email_received(subject)

def test_send_email_with_attachment(setup_test_environment):
    """Test wysyłania e-maila z załącznikiem"""
    subject = f"Test z załącznikiem {time.time()}"
    body = "To jest testowa wiadomość z załącznikiem"
    
    # Przygotowanie załącznika
    attachments = [os.path.join(ATTACHMENT_PATH, 'example.txt')]
    
    # Wysyłanie e-maila
    assert send_test_email(subject, body, attachments)
    
    # Sprawdzanie, czy e-mail został odebrany
    assert check_email_received(subject)

if __name__ == "__main__":
    # Uruchamianie testów bezpośrednio
    pytest.main(["-v", __file__])
