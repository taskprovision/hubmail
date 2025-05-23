#!/usr/bin/env python3
"""
Skrypt do wysyłania testowych e-maili do środowiska testowego.
Używa zmiennych z pliku .env do konfiguracji.
"""
import os
import sys
import smtplib
import argparse
import random
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Ładowanie zmiennych środowiskowych
load_dotenv()

# Konfiguracja SMTP
SMTP_HOST = os.getenv('EMAIL_SMTP_HOST', 'mailhog')
SMTP_PORT = int(os.getenv('EMAIL_SMTP_PORT', 1025))
SMTP_USERNAME = os.getenv('EMAIL_SMTP_USERNAME', 'test@example.com')
SMTP_PASSWORD = os.getenv('EMAIL_SMTP_PASSWORD', 'password')

# Konfiguracja testów
SENDER = os.getenv('TEST_EMAIL_SENDER', 'sender@example.com')
RECIPIENT = os.getenv('TEST_EMAIL_RECIPIENT', 'test@example.com')
ATTACHMENT_PATH = os.getenv('TEST_ATTACHMENT_PATH', './test_data/attachments')

def send_email(subject, body, attachments=None, html=False):
    """
    Wysyła e-mail z opcjonalnymi załącznikami.
    
    Args:
        subject (str): Temat e-maila
        body (str): Treść e-maila
        attachments (list, optional): Lista ścieżek do załączników
        html (bool, optional): Czy treść jest w formacie HTML
    """
    # Tworzenie wiadomości
    msg = MIMEMultipart()
    msg['From'] = SENDER
    msg['To'] = RECIPIENT
    msg['Subject'] = subject
    
    # Dodawanie treści
    if html:
        msg.attach(MIMEText(body, 'html'))
    else:
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
                    print(f"Dodano załącznik: {attachment_name}")
            except Exception as e:
                print(f"Błąd podczas dodawania załącznika {attachment_path}: {str(e)}")
    
    # Wysyłanie e-maila
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.ehlo()
            # Próba logowania tylko jeśli podano dane
            if SMTP_USERNAME and SMTP_PASSWORD:
                try:
                    server.login(SMTP_USERNAME, SMTP_PASSWORD)
                except Exception as e:
                    print(f"Uwaga: Nie udało się zalogować, kontynuowanie bez logowania: {str(e)}")
            
            server.sendmail(SENDER, RECIPIENT, msg.as_string())
            print(f"E-mail wysłany pomyślnie do {RECIPIENT}")
            print(f"Temat: {subject}")
            return True
    except Exception as e:
        print(f"Błąd podczas wysyłania e-maila: {str(e)}")
        return False

def get_random_attachments(count=1):
    """
    Pobiera losowe załączniki z katalogu załączników.
    
    Args:
        count (int): Liczba załączników do pobrania
        
    Returns:
        list: Lista ścieżek do załączników
    """
    attachments_dir = Path(ATTACHMENT_PATH)
    if not attachments_dir.exists():
        print(f"Katalog załączników {ATTACHMENT_PATH} nie istnieje!")
        return []
    
    attachment_files = list(attachments_dir.glob('*'))
    if not attachment_files:
        print(f"Brak plików w katalogu załączników {ATTACHMENT_PATH}!")
        return []
    
    # Losowe wybieranie załączników
    selected = random.sample(attachment_files, min(count, len(attachment_files)))
    return [str(file) for file in selected]

def main():
    """Główna funkcja skryptu"""
    parser = argparse.ArgumentParser(description='Wysyłanie testowych e-maili')
    parser.add_argument('--urgent', action='store_true', help='Wyślij pilny e-mail')
    parser.add_argument('--report', action='store_true', help='Wyślij raport')
    parser.add_argument('--attachments', type=int, default=1, help='Liczba załączników (domyślnie: 1)')
    parser.add_argument('--html', action='store_true', help='Wyślij treść w formacie HTML')
    args = parser.parse_args()
    
    # Przygotowanie załączników
    attachments = get_random_attachments(args.attachments)
    
    # Przygotowanie treści w zależności od typu
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    if args.urgent:
        subject = f"URGENT: Ważna wiadomość testowa - {timestamp}"
        body = """
        To jest pilna wiadomość testowa wysłana automatycznie.
        
        Proszę o natychmiastową reakcję.
        
        Pozdrawiam,
        System Testowy
        """
    elif args.report:
        subject = f"REPORT: Raport miesięczny - {timestamp}"
        body = """
        Raport miesięczny - wygenerowany automatycznie.
        
        Statystyki:
        - Liczba przetworzonych e-maili: 1250
        - Liczba załączników: 320
        - Liczba błędów: 5
        
        Szczegóły w załączniku.
        
        Pozdrawiam,
        System Raportowania
        """
    else:
        subject = f"Testowa wiadomość - {timestamp}"
        body = """
        To jest standardowa wiadomość testowa wysłana automatycznie.
        
        Służy do testowania systemu przetwarzania e-maili.
        
        Pozdrawiam,
        System Testowy
        """
    
    # Wysyłanie e-maila
    if args.html:
        body = f"<html><body><h2>{subject}</h2><p>{body}</p></body></html>"
    
    success = send_email(subject, body, attachments, args.html)
    
    # Kod wyjścia
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
