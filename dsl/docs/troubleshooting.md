# Rozwiązywanie problemów

## Spis treści

- [Problemy z instalacją](#problemy-z-instalacją)
- [Problemy z konfiguracją](#problemy-z-konfiguracją)
- [Problemy z uruchamianiem przepływów](#problemy-z-uruchamianiem-przepływów)
- [Problemy z dashboardem](#problemy-z-dashboardem)
- [Problemy z powiadomieniami](#problemy-z-powiadomieniami)
- [Problemy z równoległym wykonaniem](#problemy-z-równoległym-wykonaniem)
- [Problemy z planowaniem przepływów](#problemy-z-planowaniem-przepływów)
- [Problemy z przetwarzaniem email](#problemy-z-przetwarzaniem-email)
- [Problemy z logowaniem](#problemy-z-logowaniem)
- [Najczęściej występujące błędy](#najczęściej-występujące-błędy)

## Problemy z instalacją

### Problem: Brak wymaganych zależności

**Objawy:**
- Błędy importu modułów
- Komunikaty o braku pakietów

**Rozwiązanie:**
1. Upewnij się, że zainstalowałeś wszystkie zależności:
   ```bash
   pip install -r requirements.txt
   ```
2. Sprawdź wersje zainstalowanych pakietów:
   ```bash
   pip list
   ```
3. Jeśli występują konflikty wersji, rozważ utworzenie wirtualnego środowiska:
   ```bash
   python -m venv taskinity_env
   source taskinity_env/bin/activate  # Linux/macOS
   taskinity_env\Scripts\activate     # Windows
   pip install -r requirements.txt
   ```

### Problem: Błędy podczas instalacji zależności

**Objawy:**
- Błędy kompilacji podczas instalacji pakietów
- Komunikaty o braku nagłówków lub bibliotek systemowych

**Rozwiązanie:**
1. Zainstaluj wymagane biblioteki systemowe:
   - **Linux (Debian/Ubuntu):**
     ```bash
     sudo apt-get update
     sudo apt-get install python3-dev build-essential
     ```
   - **Linux (RHEL/CentOS):**
     ```bash
     sudo yum install python3-devel gcc
     ```
   - **macOS:**
     ```bash
     xcode-select --install
     ```
   - **Windows:**
     Zainstaluj Visual C++ Build Tools

2. Spróbuj zainstalować pakiety pojedynczo, aby zidentyfikować problematyczny pakiet:
   ```bash
   pip install package_name
   ```

## Problemy z konfiguracją

### Problem: Brak plików konfiguracyjnych

**Objawy:**
- Komunikaty o braku plików konfiguracyjnych
- Błędy podczas ładowania konfiguracji

**Rozwiązanie:**
1. Upewnij się, że katalogi konfiguracyjne istnieją:
   ```bash
   mkdir -p config logs flows dsl_definitions emails
   ```
2. Uruchom skrypt, który automatycznie utworzy domyślne pliki konfiguracyjne:
   ```bash
   python -c "from notification_service import ensure_config; ensure_config()"
   python -c "from email_pipeline import ensure_config; ensure_config()"
   python -c "from advanced_logging import ensure_logging_config; ensure_logging_config()"
   ```

### Problem: Niepoprawna konfiguracja

**Objawy:**
- Błędy walidacji konfiguracji
- Nieoczekiwane zachowanie aplikacji

**Rozwiązanie:**
1. Sprawdź pliki konfiguracyjne pod kątem poprawności JSON:
   ```bash
   python -c "import json; json.load(open('config/notification_config.json'))"
   python -c "import json; json.load(open('config/email_config.json'))"
   python -c "import json; json.load(open('config/logging_config.json'))"
   ```
2. Porównaj swoją konfigurację z domyślną:
   ```bash
   diff config/notification_config.json config/notification_config.json.bak
   ```
3. W razie potrzeby przywróć domyślną konfigurację:
   ```bash
   cp config/notification_config.json.bak config/notification_config.json
   ```

## Problemy z uruchamianiem przepływów

### Problem: Błędy parsowania DSL

**Objawy:**
- Komunikaty o błędach składni DSL
- Niepoprawne parsowanie definicji przepływu

**Rozwiązanie:**
1. Sprawdź składnię DSL, zwracając uwagę na:
   - Wcięcia i spacje
   - Poprawność nazw zadań
   - Poprawność połączeń między zadaniami
2. Użyj funkcji `parse_dsl` do debugowania:
   ```python
   from flow_dsl import parse_dsl
   
   try:
       parsed = parse_dsl(flow_dsl)
       print("Poprawnie sparsowano DSL:")
       print(parsed)
   except Exception as e:
       print(f"Błąd parsowania DSL: {str(e)}")
   ```
3. Porównaj swoją definicję DSL z przykładami z dokumentacji

### Problem: Zadania nie są wykonywane

**Objawy:**
- Brak wyników z niektórych zadań
- Przepływ kończy się przedwcześnie

**Rozwiązanie:**
1. Sprawdź, czy wszystkie zadania są poprawnie zdefiniowane:
   ```python
   from flow_dsl import task_registry
   
   print("Zarejestrowane zadania:")
   for task_name, task_func in task_registry.items():
       print(f"- {task_name}: {task_func}")
   ```
2. Dodaj więcej logowania do zadań:
   ```python
   @task(name="Moje zadanie")
   def my_task(input_data):
       print(f"Rozpoczynam zadanie my_task z danymi: {input_data}")
       # Implementacja
       result = {"result": "wartość"}
       print(f"Kończę zadanie my_task z wynikiem: {result}")
       return result
   ```
3. Sprawdź, czy dane wejściowe są poprawne:
   ```python
   results = run_flow_from_dsl(flow_dsl, input_data, debug=True)
   ```

### Problem: Błędy podczas wykonania zadań

**Objawy:**
- Wyjątki podczas wykonania zadań
- Przepływ kończy się błędem

**Rozwiązanie:**
1. Dodaj obsługę wyjątków do zadań:
   ```python
   @task(name="Moje zadanie")
   def my_task(input_data):
       try:
           # Implementacja
           return result
       except Exception as e:
           print(f"Błąd w zadaniu my_task: {str(e)}")
           # Możesz zwrócić wartość domyślną lub ponownie zgłosić wyjątek
           raise
   ```
2. Sprawdź logi wykonania:
   ```bash
   cat logs/flow_dsl.log
   ```
3. Uruchom przepływ w trybie debugowania:
   ```python
   results = run_flow_from_dsl(flow_dsl, input_data, debug=True)
   ```

## Problemy z dashboardem

### Problem: Dashboard nie uruchamia się

**Objawy:**
- Błędy podczas uruchamiania dashboardu
- Dashboard nie jest dostępny w przeglądarce

**Rozwiązanie:**
1. Sprawdź, czy port nie jest zajęty:
   ```bash
   # Linux/macOS
   lsof -i :8765
   
   # Windows
   netstat -ano | findstr :8765
   ```
2. Zmień port w pliku `mini_dashboard.py`:
   ```python
   app.run(host="0.0.0.0", port=8766)  # Zmień port na inny
   ```
3. Sprawdź, czy masz zainstalowane wszystkie zależności:
   ```bash
   pip install fastapi uvicorn jinja2
   ```

### Problem: Błędy podczas ładowania stron dashboardu

**Objawy:**
- Błędy 404, 500 w przeglądarce
- Puste strony lub brakujące elementy

**Rozwiązanie:**
1. Sprawdź logi dashboardu:
   ```bash
   cat logs/mini_dashboard.log
   ```
2. Upewnij się, że wszystkie wymagane katalogi istnieją:
   ```bash
   mkdir -p flows logs dsl_definitions
   ```
3. Sprawdź, czy pliki statyczne są dostępne:
   ```bash
   ls -la static/
   ```
4. Wyczyść pamięć podręczną przeglądarki i spróbuj ponownie

### Problem: Nie można uruchomić przepływu z dashboardu

**Objawy:**
- Błędy podczas uruchamiania przepływu z dashboardu
- Brak odpowiedzi po kliknięciu przycisku "Uruchom"

**Rozwiązanie:**
1. Sprawdź logi dashboardu:
   ```bash
   cat logs/mini_dashboard.log
   ```
2. Sprawdź, czy definicja DSL jest poprawna:
   ```python
   from flow_dsl import parse_dsl
   
   try:
       parsed = parse_dsl(dsl_content)
       print("Poprawnie sparsowano DSL")
   except Exception as e:
       print(f"Błąd parsowania DSL: {str(e)}")
   ```
3. Sprawdź, czy dane wejściowe są poprawne:
   ```python
   import json
   
   try:
       input_data = json.loads(input_json)
       print("Poprawnie sparsowano dane wejściowe")
   except Exception as e:
       print(f"Błąd parsowania danych wejściowych: {str(e)}")
   ```

## Problemy z powiadomieniami

### Problem: Powiadomienia email nie są wysyłane

**Objawy:**
- Brak powiadomień email
- Błędy podczas wysyłania powiadomień

**Rozwiązanie:**
1. Sprawdź konfigurację SMTP:
   ```python
   from notification_service import load_config
   
   config = load_config()
   print("Konfiguracja SMTP:")
   print(config["email"])
   ```
2. Sprawdź, czy powiadomienia są włączone:
   ```python
   from notification_service import load_config
   
   config = load_config()
   print(f"Powiadomienia włączone: {config['enabled']}")
   print(f"Powiadomienia email włączone: {config['email']['enabled']}")
   ```
3. Sprawdź logi serwisu powiadomień:
   ```bash
   cat logs/notification_service.log
   ```
4. Przetestuj połączenie SMTP:
   ```python
   import smtplib
   
   server = smtplib.SMTP("smtp.example.com", 587)
   server.starttls()
   server.login("user@example.com", "password123")
   server.quit()
   ```

### Problem: Powiadomienia Slack nie są wysyłane

**Objawy:**
- Brak powiadomień Slack
- Błędy podczas wysyłania powiadomień

**Rozwiązanie:**
1. Sprawdź konfigurację Slack:
   ```python
   from notification_service import load_config
   
   config = load_config()
   print("Konfiguracja Slack:")
   print(config["slack"])
   ```
2. Sprawdź, czy powiadomienia są włączone:
   ```python
   from notification_service import load_config
   
   config = load_config()
   print(f"Powiadomienia włączone: {config['enabled']}")
   print(f"Powiadomienia Slack włączone: {config['slack']['enabled']}")
   ```
3. Sprawdź logi serwisu powiadomień:
   ```bash
   cat logs/notification_service.log
   ```
4. Przetestuj webhook Slack:
   ```python
   import requests
   import json
   
   webhook_url = "https://hooks.slack.com/services/XXX/YYY/ZZZ"
   data = {"text": "Test powiadomienia Slack"}
   response = requests.post(webhook_url, data=json.dumps(data), headers={"Content-Type": "application/json"})
   print(f"Status: {response.status_code}")
   print(f"Odpowiedź: {response.text}")
   ```

## Problemy z równoległym wykonaniem

### Problem: Zadania nie są wykonywane równolegle

**Objawy:**
- Zadania są wykonywane sekwencyjnie
- Brak poprawy wydajności

**Rozwiązanie:**
1. Upewnij się, że używasz funkcji `run_parallel_flow_from_dsl`:
   ```python
   from parallel_executor import run_parallel_flow_from_dsl
   
   results = run_parallel_flow_from_dsl(flow_dsl, input_data)
   ```
2. Sprawdź, czy zadania są niezależne od siebie:
   ```python
   from flow_dsl import parse_dsl
   
   parsed = parse_dsl(flow_dsl)
   print("Zależności między zadaniami:")
   for task, deps in parsed["dependencies"].items():
       print(f"- {task} zależy od: {deps}")
   ```
3. Zwiększ liczbę równoległych zadań:
   ```python
   results = run_parallel_flow_from_dsl(flow_dsl, input_data, max_workers=8)
   ```

### Problem: Błędy podczas równoległego wykonania

**Objawy:**
- Wyjątki podczas równoległego wykonania
- Deadlocki lub race conditions

**Rozwiązanie:**
1. Sprawdź, czy zadania są bezpieczne wątkowo:
   - Unikaj modyfikacji współdzielonych danych
   - Używaj lokalnych zmiennych zamiast globalnych
   - Używaj mechanizmów synchronizacji, jeśli to konieczne
2. Sprawdź logi równoległego wykonawcy:
   ```bash
   cat logs/parallel_executor.log
   ```
3. Uruchom przepływ w trybie sekwencyjnym, aby zidentyfikować problematyczne zadania:
   ```python
   from flow_dsl import run_flow_from_dsl
   
   results = run_flow_from_dsl(flow_dsl, input_data)
   ```

## Problemy z planowaniem przepływów

### Problem: Zaplanowane przepływy nie są uruchamiane

**Objawy:**
- Brak uruchomień zaplanowanych przepływów
- Planer nie działa

**Rozwiązanie:**
1. Sprawdź, czy planer jest uruchomiony:
   ```bash
   ps aux | grep flow_scheduler
   ```
2. Sprawdź konfigurację harmonogramów:
   ```python
   from flow_scheduler import Scheduler
   
   scheduler = Scheduler()
   print("Harmonogramy:")
   for schedule in scheduler.list_schedules():
       print(f"- {schedule}")
   ```
3. Sprawdź logi planera:
   ```bash
   cat logs/flow_scheduler.log
   ```
4. Uruchom planer w trybie debugowania:
   ```bash
   python flow_scheduler.py start --debug
   ```

### Problem: Błędy podczas uruchamiania zaplanowanych przepływów

**Objawy:**
- Wyjątki podczas uruchamiania zaplanowanych przepływów
- Przepływy są zaplanowane, ale nie są uruchamiane

**Rozwiązanie:**
1. Sprawdź, czy plik DSL istnieje:
   ```bash
   ls -la dsl_definitions/
   ```
2. Sprawdź, czy definicja DSL jest poprawna:
   ```python
   from flow_dsl import load_dsl, parse_dsl
   
   dsl_content = load_dsl("dsl_definitions/my_flow.dsl")
   try:
       parsed = parse_dsl(dsl_content)
       print("Poprawnie sparsowano DSL")
   except Exception as e:
       print(f"Błąd parsowania DSL: {str(e)}")
   ```
3. Sprawdź logi planera:
   ```bash
   cat logs/flow_scheduler.log
   ```
4. Uruchom przepływ ręcznie, aby sprawdzić, czy działa poprawnie:
   ```python
   from flow_dsl import load_dsl, run_flow_from_dsl
   
   dsl_content = load_dsl("dsl_definitions/my_flow.dsl")
   results = run_flow_from_dsl(dsl_content, {})
   ```

## Problemy z przetwarzaniem email

### Problem: Nie można połączyć się z serwerem IMAP/SMTP

**Objawy:**
- Błędy połączenia z serwerem IMAP/SMTP
- Nie można pobierać lub wysyłać emaili

**Rozwiązanie:**
1. Sprawdź konfigurację IMAP/SMTP:
   ```python
   from email_pipeline import load_config
   
   config = load_config()
   print("Konfiguracja IMAP:")
   print(config["imap"])
   print("Konfiguracja SMTP:")
   print(config["smtp"])
   ```
2. Sprawdź, czy serwery są dostępne:
   ```python
   import socket
   
   imap_server = "imap.example.com"
   imap_port = 993
   smtp_server = "smtp.example.com"
   smtp_port = 587
   
   try:
       socket.create_connection((imap_server, imap_port), timeout=5)
       print(f"Serwer IMAP {imap_server}:{imap_port} jest dostępny")
   except Exception as e:
       print(f"Serwer IMAP {imap_server}:{imap_port} nie jest dostępny: {str(e)}")
   
   try:
       socket.create_connection((smtp_server, smtp_port), timeout=5)
       print(f"Serwer SMTP {smtp_server}:{smtp_port} jest dostępny")
   except Exception as e:
       print(f"Serwer SMTP {smtp_server}:{smtp_port} nie jest dostępny: {str(e)}")
   ```
3. Sprawdź logi procesora email:
   ```bash
   cat logs/email_pipeline.log
   ```
4. Przetestuj połączenie IMAP/SMTP:
   ```python
   import imaplib
   import smtplib
   
   # Test IMAP
   imap = imaplib.IMAP4_SSL("imap.example.com", 993)
   imap.login("user@example.com", "password123")
   imap.select("INBOX")
   imap.logout()
   
   # Test SMTP
   smtp = smtplib.SMTP("smtp.example.com", 587)
   smtp.starttls()
   smtp.login("user@example.com", "password123")
   smtp.quit()
   ```

### Problem: Automatyczne odpowiedzi nie są wysyłane

**Objawy:**
- Brak automatycznych odpowiedzi na emaile
- Błędy podczas wysyłania odpowiedzi

**Rozwiązanie:**
1. Sprawdź konfigurację automatycznych odpowiedzi:
   ```python
   from email_pipeline import load_config
   
   config = load_config()
   print("Konfiguracja automatycznych odpowiedzi:")
   print(config["auto_reply"])
   ```
2. Sprawdź, czy automatyczne odpowiedzi są włączone:
   ```python
   from email_pipeline import load_config
   
   config = load_config()
   print(f"Automatyczne odpowiedzi włączone: {config['auto_reply']['enabled']}")
   ```
3. Sprawdź logi procesora email:
   ```bash
   cat logs/email_pipeline.log
   ```
4. Przetestuj funkcję wysyłania automatycznych odpowiedzi:
   ```python
   from email_pipeline import EmailProcessor
   
   processor = EmailProcessor()
   email_data = {
       "id": "test_id",
       "from": "sender@example.com",
       "to": "recipient@example.com",
       "subject": "Test",
       "body": "Test message"
   }
   processor.send_auto_reply(email_data, "default")
   ```

## Problemy z logowaniem

### Problem: Logi nie są generowane

**Objawy:**
- Brak plików logów
- Puste pliki logów

**Rozwiązanie:**
1. Upewnij się, że katalog logów istnieje:
   ```bash
   mkdir -p logs
   ```
2. Sprawdź konfigurację logowania:
   ```python
   from advanced_logging import load_logging_config
   
   config = load_logging_config()
   print("Konfiguracja logowania:")
   print(config)
   ```
3. Sprawdź, czy logowanie jest włączone:
   ```python
   from advanced_logging import load_logging_config
   
   config = load_logging_config()
   print(f"Logowanie do pliku włączone: {config['file']['enabled']}")
   ```
4. Przetestuj logowanie:
   ```python
   from advanced_logging import setup_logger
   
   logger = setup_logger("test")
   logger.info("Test info message")
   logger.debug("Test debug message")
   logger.warning("Test warning message")
   logger.error("Test error message")
   
   print("Sprawdź plik logs/test.log")
   ```

### Problem: Niepoprawny poziom logowania

**Objawy:**
- Za mało lub za dużo logów
- Brak ważnych informacji w logach

**Rozwiązanie:**
1. Sprawdź konfigurację poziomów logowania:
   ```python
   from advanced_logging import load_logging_config
   
   config = load_logging_config()
   print("Poziomy logowania:")
   print(f"Konsola: {config['console']['level']}")
   print(f"Plik: {config['file']['level']}")
   for module, level in config["modules"].items():
       print(f"{module}: {level}")
   ```
2. Zmień poziom logowania:
   ```python
   from advanced_logging import load_logging_config, save_logging_config
   
   config = load_logging_config()
   config["console"]["level"] = "DEBUG"
   config["file"]["level"] = "DEBUG"
   config["modules"]["flow_dsl"] = "DEBUG"
   save_logging_config(config)
   ```
3. Przetestuj logowanie z nową konfiguracją:
   ```python
   from advanced_logging import setup_logger
   
   logger = setup_logger("flow_dsl")
   logger.debug("Test debug message")
   
   print("Sprawdź plik logs/flow_dsl.log")
   ```

## Najczęściej występujące błędy

### `ImportError: No module named 'flow_dsl'`

**Przyczyna:** Moduł `flow_dsl` nie jest dostępny w ścieżce Pythona.

**Rozwiązanie:**
1. Upewnij się, że jesteś w katalogu projektu:
   ```bash
   cd /path/to/hubmail/dsl
   ```
2. Dodaj katalog projektu do ścieżki Pythona:
   ```python
   import sys
   sys.path.append("/path/to/hubmail/dsl")
   ```
3. Zainstaluj projekt jako pakiet:
   ```bash
   pip install -e .
   ```

### `KeyError: 'task_name'`

**Przyczyna:** Zadanie o podanej nazwie nie istnieje w rejestrze zadań.

**Rozwiązanie:**
1. Sprawdź, czy zadanie jest poprawnie zdefiniowane:
   ```python
   @task(name="task_name")
   def task_name():
       pass
   ```
2. Sprawdź, czy zadanie jest zaimportowane przed uruchomieniem przepływu:
   ```python
   from my_module import task_name
   ```
3. Sprawdź rejestr zadań:
   ```python
   from flow_dsl import task_registry
   
   print("Zarejestrowane zadania:")
   for task_name, task_func in task_registry.items():
       print(f"- {task_name}: {task_func}")
   ```

### `SyntaxError: invalid syntax` w DSL

**Przyczyna:** Niepoprawna składnia DSL.

**Rozwiązanie:**
1. Sprawdź składnię DSL, zwracając uwagę na:
   - Wcięcia i spacje
   - Poprawność nazw zadań
   - Poprawność połączeń między zadaniami
2. Porównaj swoją definicję DSL z przykładami z dokumentacji
3. Użyj funkcji `parse_dsl` do debugowania:
   ```python
   from flow_dsl import parse_dsl
   
   try:
       parsed = parse_dsl(flow_dsl)
       print("Poprawnie sparsowano DSL:")
       print(parsed)
   except Exception as e:
       print(f"Błąd parsowania DSL: {str(e)}")
   ```

### `SMTPAuthenticationError: (535, b'5.7.8 Authentication failed')`

**Przyczyna:** Niepoprawne dane uwierzytelniające SMTP.

**Rozwiązanie:**
1. Sprawdź konfigurację SMTP:
   ```python
   from notification_service import load_config
   
   config = load_config()
   print("Konfiguracja SMTP:")
   print(config["email"])
   ```
2. Upewnij się, że nazwa użytkownika i hasło są poprawne
3. Sprawdź, czy serwer SMTP wymaga TLS/SSL
4. Jeśli używasz konta Google, może być konieczne włączenie dostępu dla mniej bezpiecznych aplikacji lub użycie hasła aplikacji

### `ConnectionRefusedError: [Errno 111] Connection refused`

**Przyczyna:** Nie można połączyć się z serwerem.

**Rozwiązanie:**
1. Sprawdź, czy serwer jest uruchomiony
2. Sprawdź, czy adres i port są poprawne
3. Sprawdź, czy firewall nie blokuje połączenia
4. Sprawdź, czy serwer jest dostępny z Twojej sieci:
   ```bash
   telnet server_address port
   ```

### `FileNotFoundError: [Errno 2] No such file or directory`

**Przyczyna:** Plik nie istnieje.

**Rozwiązanie:**
1. Sprawdź, czy plik istnieje:
   ```bash
   ls -la /path/to/file
   ```
2. Sprawdź, czy ścieżka do pliku jest poprawna
3. Upewnij się, że masz uprawnienia do odczytu pliku:
   ```bash
   chmod +r /path/to/file
   ```
4. Jeśli plik powinien być utworzony automatycznie, sprawdź, czy katalog nadrzędny istnieje i masz uprawnienia do zapisu:
   ```bash
   mkdir -p /path/to/directory
   chmod +w /path/to/directory
   ```

### `PermissionError: [Errno 13] Permission denied`

**Przyczyna:** Brak uprawnień do pliku lub katalogu.

**Rozwiązanie:**
1. Sprawdź uprawnienia:
   ```bash
   ls -la /path/to/file
   ```
2. Zmień uprawnienia:
   ```bash
   chmod +rw /path/to/file
   ```
3. Zmień właściciela:
   ```bash
   chown user:group /path/to/file
   ```
4. Uruchom aplikację z odpowiednimi uprawnieniami:
   ```bash
   sudo python my_script.py
   ```

### `JSONDecodeError: Expecting value`

**Przyczyna:** Niepoprawny format JSON.

**Rozwiązanie:**
1. Sprawdź plik JSON pod kątem poprawności:
   ```bash
   python -c "import json; json.load(open('/path/to/file.json'))"
   ```
2. Użyj narzędzia do walidacji JSON, np. [JSONLint](https://jsonlint.com/)
3. Przywróć domyślną konfigurację:
   ```bash
   cp config/notification_config.json.bak config/notification_config.json
   ```
4. Ręcznie popraw plik JSON, zwracając uwagę na:
   - Brakujące lub nadmiarowe przecinki
   - Brakujące cudzysłowy
   - Niepoprawne wartości

<!-- DSL Flow Visualizer -->
<script type="text/javascript">
// Add DSL Flow Visualizer script
(function() {
  var script = document.createElement('script');
  script.src = '/hubmail/dsl/static/js/dsl-flow-visualizer.js';
  script.async = true;
  script.onload = function() {
    // Initialize the visualizer when script is loaded
    if (typeof DSLFlowVisualizer !== 'undefined') {
      new DSLFlowVisualizer();
    }
  };
  document.head.appendChild(script);
  
  // Add CSS styles
  var style = document.createElement('style');
  style.textContent = `
    .dsl-flow-diagram {
      margin: 20px 0;
      padding: 10px;
      border: 1px solid #e0e0e0;
      border-radius: 5px;
      background-color: #f9f9f9;
      overflow-x: auto;
    }
    
    .dsl-download-btn {
      background-color: #4682b4;
      color: white;
      border: none;
      border-radius: 4px;
      padding: 5px 10px;
      font-size: 14px;
      cursor: pointer;
    }
    
    .dsl-download-btn:hover {
      background-color: #36648b;
    }
  `;
  document.head.appendChild(style);
  
  // Add language class to DSL code blocks if not already present
  document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('pre code').forEach(function(codeBlock) {
      var content = codeBlock.textContent.trim();
      if (content.startsWith('flow ') && !codeBlock.classList.contains('language-dsl')) {
        codeBlock.classList.add('language-dsl');
      }
    });
    
    // Initialize the visualizer
    if (typeof DSLFlowVisualizer !== 'undefined') {
      new DSLFlowVisualizer();
    }
  });
})();
</script>


<!-- Markdown Enhancements -->

<!-- Taskinity Markdown Enhancements -->
<!-- Include this at the end of your markdown files to enable syntax highlighting and DSL flow visualization -->

<!-- Prism.js for syntax highlighting -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism.min.css">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/plugins/line-numbers/prism-line-numbers.min.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/prism.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/plugins/line-numbers/prism-line-numbers.min.js"></script>

<!-- Load common language components -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-python.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-bash.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-javascript.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-yaml.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-json.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-markdown.min.js"></script>

<!-- Taskinity custom scripts -->
<script src="../static/js/dsl-flow-visualizer.js"></script>
<script src="../static/js/markdown-syntax-highlighter.js"></script>

<script>
  // Initialize both scripts when the page loads
  document.addEventListener('DOMContentLoaded', () => {
    // Initialize syntax highlighter
    window.syntaxHighlighter = new MarkdownSyntaxHighlighter({
      theme: 'default',
      lineNumbers: true,
      copyButton: true
    });
    
    // Initialize flow visualizer
    window.flowVisualizer = new DSLFlowVisualizer({
      codeBlockSelector: 'pre code.language-dsl, pre code.language-flow'
    });
  });
</script>

<!-- Custom styles for better markdown rendering -->
<style>
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
    line-height: 1.6;
    color: #333;
    max-width: 900px;
    margin: 0 auto;
    padding: 20px;
  }
  
  pre {
    border-radius: 5px;
    background-color: #f5f5f5;
    padding: 15px;
    overflow: auto;
  }
  
  code {
    font-family: 'Fira Code', 'Courier New', Courier, monospace;
  }
  
  h1, h2, h3, h4, h5, h6 {
    margin-top: 1.5em;
    margin-bottom: 0.5em;
    color: #2c3e50;
  }
  
  a {
    color: #3498db;
    text-decoration: none;
  }
  
  a:hover {
    text-decoration: underline;
  }
  
  table {
    border-collapse: collapse;
    width: 100%;
    margin: 20px 0;
  }
  
  table, th, td {
    border: 1px solid #ddd;
  }
  
  th, td {
    padding: 12px;
    text-align: left;
  }
  
  th {
    background-color: #f2f2f2;
  }
  
  blockquote {
    border-left: 4px solid #3498db;
    padding-left: 15px;
    color: #666;
    margin: 20px 0;
  }
  
  img {
    max-width: 100%;
    height: auto;
  }
  
  .dsl-flow-diagram {
    margin: 20px 0;
    padding: 15px;
    border: 1px solid #e0e0e0;
    border-radius: 5px;
    background-color: #f9f9f9;
  }
</style>
