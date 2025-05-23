#!/usr/bin/env python3
"""
Skrypt do ładowania zmiennych środowiskowych z pliku .env i zastępowania ich w pliku config.yaml.
"""
import os
import re
import yaml
from pathlib import Path
from dotenv import load_dotenv

def load_config_with_env_vars(config_path='config.yaml'):
    """
    Ładuje plik konfiguracyjny i zastępuje zmienne środowiskowe.
    
    Args:
        config_path (str): Ścieżka do pliku konfiguracyjnego
        
    Returns:
        dict: Załadowana konfiguracja z zastąpionymi zmiennymi środowiskowymi
    """
    # Ładowanie zmiennych środowiskowych
    load_dotenv()
    
    # Ładowanie pliku konfiguracyjnego
    with open(config_path, 'r') as f:
        config_str = f.read()
    
    # Zastępowanie zmiennych środowiskowych
    pattern = r'\${([A-Za-z0-9_]+)}'
    
    def replace_env_var(match):
        env_var = match.group(1)
        value = os.getenv(env_var)
        if value is None:
            print(f"OSTRZEŻENIE: Zmienna środowiskowa {env_var} nie jest ustawiona!")
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
            return match.group(0)  # Pozostawienie oryginalnego tekstu
        return value
    
    config_str = re.sub(pattern, replace_env_var, config_str)
    
    # Parsowanie YAML
    config = yaml.safe_load(config_str)
    
    return config

def save_processed_config(config, output_path='config_processed.yaml'):
    """
    Zapisuje przetworzoną konfigurację do pliku.
    
    Args:
        config (dict): Konfiguracja do zapisania
        output_path (str): Ścieżka do pliku wyjściowego
    """
    with open(output_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)
    
    print(f"Zapisano przetworzoną konfigurację do {output_path}")

if __name__ == "__main__":
    # Ładowanie konfiguracji
    config = load_config_with_env_vars()
    
    # Zapisywanie przetworzonej konfiguracji
    save_processed_config(config)
    
    print("Zmienne środowiskowe zostały załadowane i zastąpione w konfiguracji.")
