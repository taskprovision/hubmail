#!/usr/bin/env python3
"""
Skrypt startowy dla systemu automatyzacji przetwarzania e-maili z Prefect.
Uruchamia zarówno przepływy e-mail, jak i serwer Prefect do wizualizacji i monitorowania.
"""
import os
import sys
import time
import yaml
import argparse
import subprocess
import signal
from pathlib import Path
from dotenv import load_dotenv

# Ścieżka do katalogu z projektem
BASE_DIR = Path(__file__).resolve().parent

def load_config():
    """Ładowanie zmiennych środowiskowych"""
    # Ładowanie zmiennych środowiskowych
    load_dotenv()
    
    # Tworzenie konfiguracji
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
        },
        "monitoring": {
            "prefect_ui_port": int(os.getenv("PREFECT_UI_PORT", 4200))
        }
    }
    
    return config

def check_dependencies():
    """Sprawdzanie i instalacja zależności"""
    print("Sprawdzanie zależności...")
    requirements_path = BASE_DIR / "requirements.txt"
    
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", str(requirements_path)],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print("Zależności zainstalowane pomyślnie.")
    except subprocess.CalledProcessError as e:
        print(f"Błąd podczas instalacji zależności: {e.stderr.decode()}")
        sys.exit(1)

def create_directories():
    """Tworzenie wymaganych katalogów"""
    print("Tworzenie katalogów...")
    
    # Katalog na logi
    logs_dir = BASE_DIR / "logs"
    logs_dir.mkdir(exist_ok=True)
    
    # Katalog na załączniki
    config = load_config()
    attachments_dir = Path(config["attachments"]["save_path"])
    attachments_dir.mkdir(exist_ok=True)
    
    print("Katalogi utworzone pomyślnie.")

def start_prefect_server(detach=False):
    """Uruchamianie serwera Prefect"""
    print("Uruchamianie serwera Prefect...")
    
    config = load_config()
    port = config["monitoring"]["prefect_ui_port"]
    
    if detach:
        # Uruchamianie w tle
        process = subprocess.Popen(
            [sys.executable, "-m", "prefect", "server", "start", "--host", "0.0.0.0", "--port", str(port)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return process
    else:
        # Uruchamianie w bieżącym procesie
        try:
            subprocess.run([sys.executable, "-m", "prefect", "server", "start", "--host", "0.0.0.0", "--port", str(port)], check=True)
        except KeyboardInterrupt:
            print("Zatrzymano serwer Prefect.")
        except subprocess.CalledProcessError as e:
            print(f"Błąd podczas uruchamiania serwera Prefect: {e}")
            sys.exit(1)

def start_email_flow(detach=False):
    """Uruchamianie przepływu przetwarzania e-maili"""
    print("Uruchamianie przepływu przetwarzania e-maili...")
    
    email_flow_path = BASE_DIR / "email_flows.py"
    
    if detach:
        # Uruchamianie w tle
        process = subprocess.Popen(
            [sys.executable, str(email_flow_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return process
    else:
        # Uruchamianie w bieżącym procesie
        try:
            subprocess.run([sys.executable, str(email_flow_path)], check=True)
        except KeyboardInterrupt:
            print("Zatrzymano przepływ przetwarzania e-maili.")
        except subprocess.CalledProcessError as e:
            print(f"Błąd podczas uruchamiania przepływu przetwarzania e-maili: {e}")
            sys.exit(1)

def main():
    """Główna funkcja skryptu startowego"""
    parser = argparse.ArgumentParser(description="Uruchamianie systemu automatyzacji przetwarzania e-maili z Prefect")
    parser.add_argument("--email-only", action="store_true", help="Uruchom tylko przepływ przetwarzania e-maili")
    parser.add_argument("--server-only", action="store_true", help="Uruchom tylko serwer Prefect")
    parser.add_argument("--no-deps", action="store_true", help="Pomiń sprawdzanie zależności")
    args = parser.parse_args()
    
    # Sprawdzanie zależności
    if not args.no_deps:
        check_dependencies()
    
    # Tworzenie katalogów
    create_directories()
    
    # Ładowanie konfiguracji
    config = load_config()
    
    # Uruchamianie komponentów
    processes = []
    
    try:
        if args.email_only:
            # Tylko przepływ przetwarzania e-maili
            start_email_flow(detach=False)
        elif args.server_only:
            # Tylko serwer Prefect
            start_prefect_server(detach=False)
        else:
            # Oba komponenty
            prefect_process = start_prefect_server(detach=True)
            processes.append(prefect_process)
            
            # Krótkie opóźnienie
            time.sleep(5)
            
            email_process = start_email_flow(detach=True)
            processes.append(email_process)
            
            # Wyświetlanie informacji
            prefect_port = config["monitoring"]["prefect_ui_port"]
            print(f"\nSystem uruchomiony pomyślnie!")
            print(f"Prefect UI dostępny pod adresem: http://localhost:{prefect_port}")
            print("Naciśnij Ctrl+C, aby zatrzymać...")
            
            # Oczekiwanie na przerwanie
            while True:
                time.sleep(1)
    except KeyboardInterrupt:
        print("\nZatrzymywanie systemu...")
        
        # Zatrzymywanie procesów
        for process in processes:
            process.send_signal(signal.SIGINT)
            process.wait()
        
        print("System zatrzymany.")

if __name__ == "__main__":
    main()
