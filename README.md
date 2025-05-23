# HubMail - Email Intelligence Hub 

Automatyczne przetwarzanie i klasyfikacja emaili z wykorzystaniem LLM i monitoringu w czasie rzeczywistym.

## ✨ Funkcje

- 🤖 **AI Classification**: Automatyczna klasyfikacja emaili (URGENT/BUSINESS/SPAM/PERSONAL)
- 📊 **Real-time Monitoring**: Dashboard z metrykami w Grafana
- 🔄 **Process Automation**: Automatyczne odpowiedzi i routing emaili
- 📈 **Analytics**: Szczegółowe analizy wzorców emailowych

## 🚀 Szybki Start

1. Sklonuj repozytorium i przejdź do katalogu:
   ```bash
   git clone https://github.com/taskprovision/hubmail.git
   cd hubmail
   ```

2. Skonfiguruj zmienne środowiskowe:
   ```bash
   cp .env.example .env
   # Edytuj plik .env i ustaw odpowiednie wartości
   ```

3. Uruchom instalację:
   ```bash
   ./install.sh
   ```

4. Przetestuj system:
   ```bash
   ./scripts/test-flow.sh
   ```

## 🌐 Dostęp do Serwisów

| Usługa | URL | Domyślne dane logowania |
|--------|-----|-------------------------|
| **Node-RED** | http://localhost:1880 | - |
| **Grafana** | http://localhost:3000 | admin/admin |
| **Prometheus** | http://localhost:9090 | - |

## ⚙️ Konfiguracja

### Konfiguracja Email

Edytuj plik `.env` i zaktualizuj poniższe zmienne:

```bash
# Konfiguracja serwera pocztowego
EMAIL_SERVER=imap.gmail.com
EMAIL_USER=your-email@gmail.com
EMAIL_PASS=your-app-password
EMAIL_PORT=993
EMAIL_SSL=true

# Inne ustawienia
LOG_LEVEL=info
```

## 📁 Architektura Systemu

Każdy email przechodzi przez następujący proces:

1. **Pobranie** - Pobieranie wiadomości z serwera IMAP
2. **Analiza** - Przetwarzanie przez model LLM (klasyfikacja + wyciągnięcie intencji)
3. **Routing** - Kierowanie wiadomości na podstawie klasyfikacji
4. **Akcja** - Wykonanie odpowiedniej akcji (alert, auto-odpowiedź, archiwizacja)
5. **Monitoring** - Zbieranie metryk i wyświetlanie ich w panelu

## 🔄 Zarządzanie

### Tworzenie kopii zapasowej

```bash
./scripts/backup.sh
```

### Najczęstsze problemy

- **Sprawdzanie logów**:
  ```bash
  docker-compose logs -f
  ```

- **Restart usług**:
  ```bash
  docker-compose restart
  ```

- **Pełna reinstalacja** (ostrożnie - usuwa dane):
  ```bash
  docker-compose down -v
  ./install.sh
  ```

## 📝 Licencja

Ten projekt jest dostępny na licencji Apache. Więcej informacji w pliku [LICENSE](LICENSE).


