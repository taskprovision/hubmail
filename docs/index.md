# HubMail - Dokumentacja

## Spis treści

### Podstawy
- [📖 Instrukcja instalacji](INSTALL.md)
- [⚙️ Konfiguracja systemu](CONFIG.md)
- [🚀 Szybki start](START.md)

### Użytkowanie
- [👤 Przewodnik użytkownika](user-guide.md)
- [👨‍💻 Przewodnik administratora](admin-guide.md)

### Programowanie
- [📝 Dokumentacja API](API.md)

## Architektura systemu

HubMail to kompleksowe rozwiązanie do automatycznego przetwarzania i klasyfikacji emaili z wykorzystaniem modeli AI oraz monitoringu w czasie rzeczywistym.

### Komponenty systemu

- **Node-RED** (Port: 1880) - Silnik automatyzacji przepływów emaili
- **Ollama** (Port: 11436) - Lokalne modele AI do klasyfikacji
- **Prometheus** (Port: 9090) - Zbieranie metryk
- **Grafana** (Port: 3000) - Wizualizacja i dashboardy
- **Redis** (Port: 6379) - Przechowywanie danych tymczasowych

### Przepływ przetwarzania emaili

1. **Pobranie** - Pobieranie wiadomości z serwera IMAP
2. **Analiza** - Przetwarzanie przez model LLM (klasyfikacja + wyciągnięcie intencji)
3. **Routing** - Kierowanie wiadomości na podstawie klasyfikacji
4. **Akcja** - Wykonanie odpowiedniej akcji (alert, auto-odpowiedź, archiwizacja)
5. **Monitoring** - Zbieranie metryk i wyświetlanie ich w panelu

## Klasyfikacja emaili

System automatycznie klasyfikuje emaile do jednej z kategorii:

- **URGENT** - Wiadomości wymagające natychmiastowej uwagi
- **BUSINESS** - Wiadomości związane z działalnością biznesową
- **PERSONAL** - Wiadomości prywatne
- **SPAM** - Wiadomości niechciane

## Wsparcie i zgłaszanie problemów

W przypadku problemów z systemem, sprawdź [przewodnik administratora](admin-guide.md) lub skontaktuj się z zespołem wsparcia.
