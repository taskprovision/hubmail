# HubMail - Prosty System Automatyzacji E-mail

Ten projekt to uproszczona implementacja systemu automatyzacji przetwarzania e-maili, inspirowana koncepcjami Apache Camel, ale zaimplementowana w sposób przyjazny dla początkujących programistów.

## Spis treści

1. [Funkcjonalności](#funkcjonalności)
2. [Instalacja](#instalacja)
3. [Uruchamianie](#uruchamianie)
4. [Struktura projektu](#struktura-projektu)
5. [Jak to działa](#jak-to-działa)
6. [Rozszerzanie systemu](#rozszerzanie-systemu)
7. [Monitorowanie](#monitorowanie)
8. [Dekoratory](#dekoratory)
9. [FAQ](#faq)

## Funkcjonalności

- Automatyczne pobieranie e-maili z serwera IMAP
- Klasyfikacja e-maili na podstawie tematu (pilne, raporty, zwykłe)
- Zapisywanie załączników
- Automatyczne odpowiedzi
- Dashboard do monitorowania w czasie rzeczywistym
- Logowanie z możliwością śledzenia przepływów
- Prosta struktura, łatwa do zrozumienia i modyfikacji

## Instalacja

1. Sklonuj repozytorium:
   ```bash
   git clone https://github.com/twojafirma/hubmail.git
   cd hubmail/simple_camel
   ```

2. Zainstaluj zależności:
   ```bash
   pip install -r requirements.txt
   ```

3. Skonfiguruj plik `config.yaml` zgodnie z Twoimi potrzebami:
   ```yaml
   email:
     imap:
       host: imap.example.com
       port: 993
       username: twoj@email.com
       password: twoje_haslo
       folder: INBOX
       check_interval: 300  # sekundy
     smtp:
       host: smtp.example.com
       port: 587
       username: twoj@email.com
       password: twoje_haslo

   attachments:
     save_path: ./attachments

   monitoring:
     enabled: true
     log_level: INFO
     dashboard_port: 8000
     metrics_enabled: true
   ```

## Uruchamianie

Uruchom system za pomocą skryptu startowego:

```bash
python start.py
```

Możesz też uruchomić tylko wybrane komponenty:

```bash
# Tylko proces przetwarzania e-maili
python start.py --email-only

# Tylko dashboard monitorujący
python start.py --dashboard-only

# Pomiń sprawdzanie zależności
python start.py --no-deps
```

Po uruchomieniu, dashboard będzie dostępny pod adresem: http://localhost:8000

## Struktura projektu

```
simple_camel/
├── config.yaml           # Konfiguracja systemu
├── email_flow.py         # Główny skrypt przetwarzania e-maili
├── dashboard.py          # Dashboard monitorujący
├── start.py              # Skrypt startowy
├── requirements.txt      # Zależności
├── logs/                 # Katalog na logi
├── attachments/          # Katalog na załączniki
├── templates/            # Szablony HTML dla dashboardu
└── static/               # Pliki statyczne dla dashboardu
```

## Jak to działa

System działa w oparciu o koncepcję tras (routes) i wymiany wiadomości (exchanges), podobnie jak w Apache Camel:

1. **Trasy** - definiują przepływ przetwarzania e-maili
2. **Wymiana** - reprezentuje wiadomość e-mail i jej metadane podczas przetwarzania
3. **Procesory** - funkcje przetwarzające wiadomości

Główny przepływ:

1. Pobieranie nieprzeczytanych e-maili z serwera IMAP
2. Klasyfikacja e-maili na podstawie tematu
3. Kierowanie do odpowiedniej trasy (pilne, raporty, zwykłe)
4. Przetwarzanie zgodnie z typem (zapisywanie załączników, wysyłanie odpowiedzi)
5. Logowanie wszystkich operacji

## Rozszerzanie systemu

### Dodawanie nowego typu e-maili

1. Dodaj nową klasyfikację w funkcji `process_email`:

```python
if "urgent" in subject.lower():
    email_type = "urgent"
elif "report" in subject.lower():
    email_type = "report"
elif "feedback" in subject.lower():  # Nowy typ
    email_type = "feedback"
else:
    email_type = "regular"
```

2. Dodaj nową trasę:

```python
@route("Feedback")
def feedback_email_route(exchange):
    """Trasa dla e-maili z feedbackiem"""
    logger.info(f"Przetwarzanie feedbacku: {exchange.get_header('subject')}")
    
    try:
        # Zapisywanie załączników
        exchange = save_attachments(exchange)
        
        # Dodatkowa logika dla feedbacku
        # ...
        
        logger.info("Zakończono przetwarzanie feedbacku")
    except Exception as e:
        logger.error(f"Błąd podczas przetwarzania feedbacku: {str(e)}")
```

3. Dodaj wywołanie nowej trasy w `fetch_emails_route`:

```python
if email_type == 'urgent':
    urgent_email_route(exchange)
elif email_type == 'report':
    report_email_route(exchange)
elif email_type == 'feedback':  # Nowy typ
    feedback_email_route(exchange)
else:
    regular_email_route(exchange)
```

### Dodawanie nowego procesora

1. Utwórz nową funkcję procesora z dekoratorem `@flow_step`:

```python
@flow_step("Analiza sentymentu")
def analyze_sentiment(exchange):
    """Analiza sentymentu wiadomości e-mail"""
    body = exchange.get_body().get_payload()
    
    # Prosta analiza sentymentu
    positive_words = ['dobry', 'świetny', 'doskonały', 'zadowolony']
    negative_words = ['zły', 'problem', 'błąd', 'niezadowolony']
    
    positive_count = sum(1 for word in positive_words if word in body.lower())
    negative_count = sum(1 for word in negative_words if word in body.lower())
    
    if positive_count > negative_count:
        sentiment = 'positive'
    elif negative_count > positive_count:
        sentiment = 'negative'
    else:
        sentiment = 'neutral'
    
    exchange.set_header('sentiment', sentiment)
    logger.info(f"Wykryto sentyment: {sentiment}")
    
    return exchange
```

2. Dodaj procesor do odpowiedniej trasy:

```python
@route("Pilne e-maile")
def urgent_email_route(exchange):
    """Trasa dla pilnych e-maili"""
    logger.info(f"Przetwarzanie pilnego e-maila: {exchange.get_header('subject')}")
    
    try:
        # Zapisywanie załączników
        exchange = save_attachments(exchange)
        
        # Analiza sentymentu
        exchange = analyze_sentiment(exchange)
        
        # Wysyłanie odpowiedzi
        exchange = send_response(exchange)
        
        logger.info("Zakończono przetwarzanie pilnego e-maila")
    except Exception as e:
        logger.error(f"Błąd podczas przetwarzania pilnego e-maila: {str(e)}")
```

## Monitorowanie

System zawiera wbudowany dashboard do monitorowania przepływów w czasie rzeczywistym:

- **Status systemu** - aktualny stan, czasy ostatniego i następnego sprawdzenia
- **Statystyki** - liczba przetworzonych e-maili, załączników, błędów
- **Logi** - podgląd logów w czasie rzeczywistym

Dashboard automatycznie odświeża dane co kilka sekund i używa WebSocket do aktualizacji statusu.

## Dekoratory

System wykorzystuje kilka dekoratorów, które ułatwiają pracę i monitorowanie:

### @flow_step

Oznacza krok w przepływie przetwarzania:

```python
@flow_step("Zapisywanie załączników")
def save_attachments(exchange):
    # ...
```

Dekorator automatycznie:
- Loguje rozpoczęcie i zakończenie kroku
- Mierzy czas wykonania
- Obsługuje błędy

### @route

Oznacza trasę przepływu:

```python
@route("Pilne e-maile")
def urgent_email_route(exchange):
    # ...
```

Dekorator automatycznie:
- Loguje rozpoczęcie i zakończenie trasy
- Mierzy czas wykonania
- Obsługuje błędy

### @retry

Automatycznie ponawia operację w przypadku błędu:

```python
@retry(max_attempts=3, delay=2)
def send_response(exchange):
    # ...
```

Parametry:
- `max_attempts` - maksymalna liczba prób
- `delay` - opóźnienie między próbami (w sekundach)

## FAQ

### Jak zmienić częstotliwość sprawdzania e-maili?

Edytuj parametr `check_interval` w pliku `config.yaml`:

```yaml
email:
  imap:
    check_interval: 300  # sekundy
```

### Jak dodać obsługę nowego typu załączników?

Funkcja `save_attachments` już obsługuje wszystkie typy załączników. Jeśli chcesz dodać specjalne przetwarzanie dla określonych typów, możesz zmodyfikować tę funkcję:

```python
@flow_step("Zapisywanie załączników")
def save_attachments(exchange):
    # ...
    
    # Dodaj specjalne przetwarzanie dla określonych typów plików
    filename = part.get_filename()
    if filename:
        # Sprawdź rozszerzenie pliku
        _, ext = os.path.splitext(filename)
        
        if ext.lower() == '.pdf':
            # Specjalne przetwarzanie dla PDF
            # ...
        elif ext.lower() in ['.jpg', '.jpeg', '.png']:
            # Specjalne przetwarzanie dla obrazów
            # ...
        
        # Standardowe zapisywanie
        filepath = os.path.join(attachment_dir, filename)
        with open(filepath, 'wb') as f:
            f.write(part.get_payload(decode=True))
```

### Jak zmienić port dashboardu?

Edytuj parametr `dashboard_port` w pliku `config.yaml`:

```yaml
monitoring:
  dashboard_port: 8000
```

### Jak dodać nowe statystyki do dashboardu?

1. Dodaj nowe pole w funkcji `get_flow_stats` w pliku `dashboard.py`
2. Zaktualizuj szablon HTML w funkcji `generate_templates`
3. Dodaj obsługę nowego pola w skrypcie JavaScript
