#!/usr/bin/env python3
"""
Skrypt startowy dla systemu automatyzacji przetwarzania e-maili.
Uruchamia zarówno proces przetwarzania e-maili, jak i dashboard monitorujący.
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
    """Ładowanie konfiguracji z pliku YAML"""
    config_path = BASE_DIR / "config.yaml"
    try:
        # Ładowanie zmiennych środowiskowych
        load_dotenv()
        
        # Ładowanie pliku konfiguracyjnego
        with open(config_path, 'r') as f:
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
                    print(f"Używam domyślnej wartości dla {env_var}: {defaults[env_var]}")
                    return defaults[env_var]
                print(f"OSTRZEŻENIE: Zmienna środowiskowa {env_var} nie jest ustawiona!")
                return match.group(0)  # Pozostawienie oryginalnego tekstu
            return value
        
        config_str = re.sub(pattern, replace_env_var, config_str)
        
        # Parsowanie YAML
        config = yaml.safe_load(config_str)
        return config
    except Exception as e:
        print(f"Błąd podczas ładowania konfiguracji: {str(e)}")
        return {}

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
    attachments_dir = Path(config.get('attachments', {}).get('save_path', './attachments'))
    attachments_dir.mkdir(exist_ok=True)
    
    # Katalogi dla dashboardu
    templates_dir = BASE_DIR / "templates"
    templates_dir.mkdir(exist_ok=True)
    
    static_dir = BASE_DIR / "static"
    static_dir.mkdir(exist_ok=True)
    
    print("Katalogi utworzone pomyślnie.")

def start_email_flow(detach=False):
    """Uruchamianie procesu przetwarzania e-maili"""
    print("Uruchamianie procesu przetwarzania e-maili...")
    
    email_flow_path = BASE_DIR / "email_flow.py"
    
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
            print("Zatrzymano proces przetwarzania e-maili.")
        except subprocess.CalledProcessError as e:
            print(f"Błąd podczas uruchamiania procesu przetwarzania e-maili: {e}")
            sys.exit(1)

def start_dashboard(detach=False):
    """Uruchamianie dashboardu monitorującego"""
    print("Uruchamianie dashboardu monitorującego...")
    
    dashboard_path = BASE_DIR / "dashboard.py"
    
    if detach:
        # Uruchamianie w tle
        process = subprocess.Popen(
            [sys.executable, str(dashboard_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return process
    else:
        # Uruchamianie w bieżącym procesie
        try:
            subprocess.run([sys.executable, str(dashboard_path)], check=True)
        except KeyboardInterrupt:
            print("Zatrzymano dashboard monitorujący.")
        except subprocess.CalledProcessError as e:
            print(f"Błąd podczas uruchamiania dashboardu: {e}")
            sys.exit(1)

def main():
    """Główna funkcja skryptu startowego"""
    parser = argparse.ArgumentParser(description="Uruchamianie systemu automatyzacji przetwarzania e-maili")
    parser.add_argument("--email-only", action="store_true", help="Uruchom tylko proces przetwarzania e-maili")
    parser.add_argument("--dashboard-only", action="store_true", help="Uruchom tylko dashboard monitorujący")
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
            # Tylko proces przetwarzania e-maili
            start_email_flow(detach=False)
        elif args.dashboard_only:
            # Tylko dashboard
            start_dashboard(detach=False)
        else:
            # Oba komponenty
            email_process = start_email_flow(detach=True)
            processes.append(email_process)
            
            # Krótkie opóźnienie
            time.sleep(1)
            
            dashboard_process = start_dashboard(detach=True)
            processes.append(dashboard_process)
            
            # Wyświetlanie informacji
            dashboard_port = config.get('monitoring', {}).get('dashboard_port', 8000)
            print(f"\nSystem uruchomiony pomyślnie!")
            print(f"Dashboard dostępny pod adresem: http://localhost:{dashboard_port}")
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
