# HubMail - Automatyzacja E-mail z Prefect

Ten projekt to uproszczona implementacja systemu automatyzacji przetwarzania e-maili z wykorzystaniem Prefect - nowoczesnego narzędzia do orkiestracji zadań, które oferuje gotowe rozwiązania dla monitorowania, debugowania i wizualizacji przepływów pracy.

## Spis treści

1. [Zalety rozwiązania](#zalety-rozwiązania)
2. [Instalacja](#instalacja)
3. [Uruchamianie](#uruchamianie)
   - [Uruchamianie z Makefile](#uruchamianie-z-makefile)
   - [Uruchamianie w Dockerze](#uruchamianie-w-dockerze)
   - [Otwieranie UI](#otwieranie-ui)
4. [Struktura projektu](#struktura-projektu)
5. [Jak to działa](#jak-to-działa)
6. [Rozszerzanie systemu](#rozszerzanie-systemu)
7. [Monitorowanie i debugowanie](#monitorowanie-i-debugowanie)
   - [Prefect UI](#prefect-ui)
   - [Logi](#logi)
   - [Debugowanie w Dockerze](#debugowanie-w-dockerze)
8. [Testowanie](#testowanie)
9. [FAQ](#faq)

## Zalety rozwiązania

W porównaniu do poprzedniej implementacji opartej na własnych dekoratorach, rozwiązanie z Prefect oferuje:

1. **Gotową infrastrukturę monitorowania** - Prefect UI pokazuje wszystkie przepływy, zadania, logi i błędy
2. **Wizualizację przepływów** - automatycznie generowane diagramy przepływów
3. **Łatwiejsze debugowanie** - szczegółowe logi, śledzenie czasu wykonania, obsługa błędów
4. **Prostsze rozszerzanie** - dodawanie nowych przepływów i zadań jest bardzo proste
5. **Mniej kodu** - mniej boilerplate'u, więcej funkcjonalności
6. **Niezawodność** - automatyczne ponawianie zadań, obsługa błędów, monitorowanie stanu
7. **Skalowanie** - możliwość uruchamiania zadań równolegle, na wielu maszynach

## Instalacja

1. Sklonuj repozytorium:
   ```bash
   git clone https://github.com/twojafirma/hubmail.git
   cd hubmail/simple_prefect
   ```

2. Utwórz plik .env na podstawie .env.example:
   ```bash
   cp .env.example .env
   ```

3. Zainstaluj zależności:
   ```bash
   pip install -r requirements.txt
   ```

## Uruchamianie

### Uruchamianie z Makefile

Projekt zawiera Makefile, który upraszcza uruchamianie i zarządzanie systemem:

```bash
# Przygotowanie środowiska (utworzenie .env, katalogów, itp.)
make setup

# Instalacja zależności
make install

# Uruchomienie całego systemu
make run

# Uruchomienie tylko przepływu przetwarzania e-maili
make run-email

# Uruchomienie tylko serwera Prefect
make run-server

# Otwarcie Prefect UI w przeglądarce
make open-ui

# Wyświetlenie logów
make logs

# Wysłanie testowego e-maila
make test-email
```

Aby zobaczyć pełną listę dostępnych komend, użyj:

```bash
make help
```

### Uruchamianie w Dockerze

Możesz również uruchomić system w środowisku Docker:

```bash
# Zbudowanie obrazów Docker
make docker-build

# Uruchomienie kontenerów
make docker-up

# Zatrzymanie kontenerów
make docker-down

# Wyświetlenie logów kontenerów
make docker-logs
```

Po uruchomieniu w Dockerze, Prefect UI będzie dostępny pod adresem: http://localhost:4200, a MailHog (serwer SMTP/IMAP do testów) pod adresem: http://localhost:8025.

### Otwieranie UI

Możesz otworzyć Prefect UI bezpośrednio z linii poleceń:

```bash
make open-ui
```

Lub ręcznie w przeglądarce pod adresem: http://localhost:4200

Prefect UI oferuje kompleksowy widok wszystkich przepływów pracy, zadań, logów i błędów. Pozwala na monitorowanie statusu przepływów, debugowanie problemów i wizualizację zależności między zadaniami.

## Struktura projektu

```
simple_prefect/
├── .env.example        # Przykładowy plik zmiennych środowiskowych
├── requirements.txt    # Zależności
├── email_flows.py      # Główny skrypt z przepływami e-mail
├── start.py            # Skrypt startowy
├── logs/               # Katalog na logi
└── attachments/        # Katalog na załączniki
```

## Jak to działa

System działa w oparciu o koncepcję przepływów (flows) i zadań (tasks) Prefect:

1. **Zadania (Tasks)** - atomowe jednostki pracy, np. pobieranie e-maili, klasyfikacja, zapisywanie załączników
2. **Przepływy (Flows)** - sekwencje zadań, np. przetwarzanie pilnego e-maila, przetwarzanie raportu
3. **Główny przepływ** - orkiestruje wszystkie pozostałe przepływy

Główny przepływ:

1. Pobiera nieprzeczytane e-maile z serwera IMAP
2. Klasyfikuje e-maile na podstawie tematu
3. Kieruje do odpowiedniego przepływu (pilne, raporty, zwykłe)
4. Każdy przepływ wykonuje odpowiednie zadania (zapisywanie załączników, wysyłanie odpowiedzi)
5. Wszystko jest monitorowane i wizualizowane w Prefect UI

## Rozszerzanie systemu

### Dodawanie nowego typu e-maili

1. Dodaj nową klasyfikację w funkcji `classify_email`:

```python
@task(name="Klasyfikacja e-maila")
def classify_email(email: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
    subject = email["subject"].lower()
    
    if "urgent" in subject:
        email_type = "urgent"
    elif "report" in subject:
        email_type = "report"
    elif "feedback" in subject:  # Nowy typ
        email_type = "feedback"
    else:
        email_type = "regular"
    
    email["type"] = email_type
    return email, email_type
```

2. Dodaj nowy przepływ dla tego typu:

```python
@flow(name="Przetwarzanie feedbacku")
def process_feedback_email(email: Dict[str, Any]) -> Dict[str, Any]:
    logger = get_run_logger()
    logger.info(f"Rozpoczęto przetwarzanie feedbacku: {email['subject']}")
    
    # Zapisywanie załączników
    email = save_attachments(email)
    
    # Wysyłanie odpowiedzi
    email = send_response(email, "feedback")
    
    logger.info(f"Zakończono przetwarzanie feedbacku: {email['subject']}")
    
    return email
```

3. Dodaj wywołanie nowego przepływu w głównym przepływie:

```python
@flow(name="Główny przepływ przetwarzania e-maili")
def main_email_flow():
    # ...
    
    # Przetwarzanie w zależności od typu
    if email_type == "urgent":
        processed_email = process_urgent_email(email)
    elif email_type == "report":
        processed_email = process_report_email(email)
    elif email_type == "feedback":  # Nowy typ
        processed_email = process_feedback_email(email)
    else:
        processed_email = process_regular_email(email)
    
    # ...
```

### Dodawanie nowego zadania

1. Utwórz nową funkcję z dekoratorem `@task`:

```python
@task(name="Analiza sentymentu", 
      description="Analizuje sentyment treści e-maila",
      retries=2)
def analyze_sentiment(email: Dict[str, Any]) -> Dict[str, Any]:
    logger = get_run_logger()
    
    body = email["body"].lower()
    
    # Prosta analiza sentymentu
    positive_words = ['dobry', 'świetny', 'doskonały', 'zadowolony']
    negative_words = ['zły', 'problem', 'błąd', 'niezadowolony']
    
    positive_count = sum(1 for word in positive_words if word in body)
    negative_count = sum(1 for word in negative_words if word in body)
    
    if positive_count > negative_count:
        sentiment = 'positive'
    elif negative_count > positive_count:
        sentiment = 'negative'
    else:
        sentiment = 'neutral'
    
    logger.info(f"Wykryto sentyment: {sentiment}")
    
    # Aktualizacja e-maila
    email["sentiment"] = sentiment
    
    return email
```

2. Dodaj wywołanie zadania w odpowiednim przepływie:

```python
@flow(name="Przetwarzanie pilnego e-maila")
def process_urgent_email(email: Dict[str, Any]) -> Dict[str, Any]:
    # ...
    
    # Analiza sentymentu
    email = analyze_sentiment(email)
    
    # ...
    
    return email
```

## Monitorowanie i debugowanie

Prefect oferuje zaawansowane narzędzia do monitorowania i debugowania:

### Prefect UI

Prefect UI (http://localhost:4200) pozwala na:

1. **Przeglądanie przepływów** - wszystkie przepływy, ich stan, czas wykonania
2. **Przeglądanie zadań** - wszystkie zadania w przepływie, ich stan, czas wykonania
3. **Przeglądanie logów** - szczegółowe logi dla każdego przepływu i zadania
4. **Wizualizację przepływów** - automatycznie generowane diagramy przepływów
5. **Śledzenie błędów** - szczegółowe informacje o błędach, stacktrace

Aby otworzyć Prefect UI:

```bash
make open-ui
```

### Logi

Logi są zapisywane w katalogu `logs/` i zawierają szczegółowe informacje o wykonaniu przepływów i zadań. Możesz je przeglądać za pomocą:

```bash
# Wyświetlenie wszystkich logów
make logs

# Wyświetlenie logów z filtrami
make logs FILTER="error"

# Wyświetlenie logów w czasie rzeczywistym
make logs-follow
```

W środowisku Docker, możesz przeglądać logi za pomocą:

```bash
make docker-logs
```

### Debugowanie w Dockerze

Prefect w środowisku Docker oferuje dodatkowe możliwości debugowania:

1. **Izolowane środowisko** - eliminuje problemy z zależnościami i konfiguracją
2. **Spójne środowisko** - gwarantuje, że wszyscy członkowie zespołu pracują w identycznym środowisku
3. **Łatwe resetowanie** - możliwość szybkiego resetowania środowiska do czystego stanu

Aby debugować w kontenerze:

```bash
# Uruchomienie powłoki w kontenerze
make docker-shell

# Uruchomienie konkretnego przepływu w trybie debug
make docker-debug FLOW=main_email_flow
```

W przypadku błędu, Prefect automatycznie zapisuje szczegółowe informacje o błędzie, co ułatwia debugowanie:

1. Stacktrace błędu
2. Wartości wejściowe i wyjściowe zadań
3. Czas wykonania zadań
4. Logi z wykonania zadań

## Testowanie

System zawiera zestaw testów, które można uruchomić za pomocą Makefile:

```bash
# Uruchomienie wszystkich testów
make test

# Uruchomienie konkretnego testu
make test TEST=test_email_flow

# Uruchomienie testów z pokryciem kodu
make test-coverage

# Uruchomienie testów w środowisku Docker
make docker-test
```

Testy wykorzystują MailHog jako serwer SMTP/IMAP do testowania wysyłania i odbierania e-maili. Możesz również ręcznie testować system, wysyłając testowe e-maile:

```bash
# Wysłanie zwykłego e-maila testowego
make test-email

# Wysłanie pilnego e-maila testowego
make test-urgent-email

# Wysłanie e-maila testowego z raportem
make test-report-email

# Wysłanie e-maila testowego z załącznikiem
make test-email-with-attachment
```

Po wysłaniu testowego e-maila, możesz zobaczyć go w interfejsie MailHog (http://localhost:8025) oraz śledzić jego przetwarzanie w Prefect UI (http://localhost:4200).

## FAQ

### Jak zmienić częstotliwość sprawdzania e-maili?

Edytuj zmienną `EMAIL_IMAP_CHECK_INTERVAL` w pliku `.env`:

```
EMAIL_IMAP_CHECK_INTERVAL=60
```

### Jak zmienić port Prefect UI?

Edytuj zmienną `PREFECT_UI_PORT` w pliku `.env`:

```
PREFECT_UI_PORT=4200
```

### Jak uruchomić system w tle?

Użyj nohup lub systemd:

```bash
nohup python start.py > output.log 2>&1 &
```

### Jak dodać obsługę nowego typu załączników?

Funkcja `save_attachments` już obsługuje wszystkie typy załączników. Jeśli chcesz dodać specjalne przetwarzanie dla określonych typów, możesz zmodyfikować tę funkcję:

```python
@task(name="Zapisywanie załączników")
def save_attachments(email: Dict[str, Any]) -> Dict[str, Any]:
    # ...
    
    for attachment in email["attachments"]:
        filename = attachment["filename"]
        data = attachment["data"]
        content_type = attachment["content_type"]
        
        # Specjalne przetwarzanie dla określonych typów plików
        if content_type == "application/pdf":
            # Specjalne przetwarzanie dla PDF
            # ...
        elif content_type.startswith("image/"):
            # Specjalne przetwarzanie dla obrazów
            # ...
        
        # Standardowe zapisywanie
        # ...
    
    return email
```
