# HubMail - Email Automation System

Automated email processing and classification using LLM technology with real-time monitoring.

## 📑 Dokumentacja

- [📖 Instrukcja instalacji](docs/INSTALL.md)
- [⚙️ Konfiguracja systemu](docs/CONFIG.md)
- [🚀 Szybki start](docs/START.md)
- [📝 Dokumentacja API](docs/API.md)
- [👤 Przewodnik użytkownika](docs/user-guide.md)
- [👨‍💻 Przewodnik administratora](docs/admin-guide.md)

## ✨ Funkcje

- 🤖 **AI Classification**: Automatyczna klasyfikacja emaili (URGENT/BUSINESS/SPAM/PERSONAL)
- 📊 **Real-time Monitoring**: Dashboard z metrykami w Grafana
- 🔄 **Process Automation**: Automatyczne odpowiedzi i routing emaili
- 📈 **Analytics**: Szczegółowe analizy wzorów emailowych
- ⚙️ **Configuration Dashboard**: Wizualizacja konfiguracji systemu i zmiennych środowiskowych
- 📱 **Responsive UI**: Nowoczesny interfejs użytkownika oparty na Streamlit

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
| **Python API** | http://localhost:3001 | - |
| **Dashboard** | http://localhost:8501 | - |
| **Config Dashboard** | http://localhost:8502 | - |
| **Node-RED** | http://localhost:1880 | - |
| **Grafana** | http://localhost:3000 | admin/admin |
| **Prometheus** | http://localhost:9090 | - |
| **Ollama** | http://localhost:11436 | - |

## ⚙️ Konfiguracja

### Panel Konfiguracyjny

System zawiera dedykowany panel konfiguracyjny, który pozwala na wizualizację i zarządzanie konfiguracją systemu. Panel ten dostępny jest pod adresem http://localhost:8502 lub można go otworzyć za pomocą komendy:

```bash
make config-ui
```

Panel konfiguracyjny oferuje:

- **Wizualizację usług** - graf zależności między usługami
- **Szczegóły konfiguracji** - pełne informacje o portach, wolumenach i zmiennych środowiskowych
- **Wyszukiwanie zmiennych** - łatwe wyszukiwanie zmiennych środowiskowych
- **Renderowanie wartości** - podgląd rzeczywistych wartości zmiennych używanych w `docker-compose.yml`

Aby otworzyć wszystkie panele na raz, użyj:

```bash
make all-ui
```

Aby uruchomić wszystkie usługi i otworzyć wszystkie panele jednocześnie:

```bash
make dashboard
```

### Konfiguracja Email

Edytuj plik `.env` i zaktualizuj poniższe zmienne:

```bash
# Konfiguracja serwera pocztowego
EMAIL_SERVER=imap.gmail.com
EMAIL_USER=your-email@gmail.com
EMAIL_PASS=your-app-password
EMAIL_PORT=993
EMAIL_USE_SSL=true

# Inne ustawienia
LLM_MODEL=llama2:7b
LLM_TEMPERATURE=0.3
```

Aby zaktualizować plik `.env` o nowe zmienne z `.env.example` bez nadpisywania istniejących wartości, użyj:

```bash
make update-env
```

Więcej szczegółów znajdziesz w [dokumentacji konfiguracji](docs/CONFIG.md).

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

## 🔗 Struktura projektu

```
hubmail/
├── config/                # Pliki konfiguracyjne dla usług
│   ├── grafana/           # Konfiguracja Grafana
│   ├── node-red/          # Konfiguracja Node-RED
│   ├── ollama/            # Konfiguracja Ollama
│   └── prometheus/        # Konfiguracja Prometheus
├── config-dashboard/      # Panel konfiguracyjny
│   ├── app.py             # Aplikacja Streamlit do wizualizacji konfiguracji
│   ├── Dockerfile         # Konfiguracja kontenera
│   └── requirements.txt   # Zależności Pythona
├── docs/                  # Dokumentacja
├── python_app/            # Główna aplikacja Pythona
│   ├── api/               # API FastAPI
│   ├── flows/             # Przepływy Prefect
│   ├── models/            # Modele danych
│   ├── ui/                # Dashboard Streamlit
│   ├── utils/             # Narzędzia pomocnicze
│   ├── Dockerfile         # Konfiguracja kontenera
│   └── requirements.txt   # Zależności Pythona
├── scripts/               # Skrypty pomocnicze
│   ├── backup.sh          # Skrypt do tworzenia kopii zapasowej
│   ├── setup.sh           # Skrypt konfiguracyjny
│   └── test-flow.sh       # Skrypt testowy
├── .env.example           # Przykładowy plik zmiennych środowiskowych
├── docker-compose.yml     # Konfiguracja Docker Compose
├── Makefile               # Polecenia make do zarządzania systemem
└── install.sh             # Skrypt instalacyjny
