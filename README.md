# hubmail - Email Intelligence Hub 

Automatyczne przetwarzanie i klasyfikacja emaili z wykorzystaniem LLM i monitoringu w czasie rzeczywistym.

## Funkcje

- 🤖 **AI Classification**: Automatyczna klasyfikacja emaili (URGENT/BUSINESS/SPAM/PERSONAL)
- 📊 **Real-time Monitoring**: Dashboard z metrykami w Grafana
- 🔄 **Process Automation**: Automatyczne odpowiedzi i routing emaili
- 📈 **Analytics**: Szczegółowe analizy wzorców emailowych

## Szybki Start

1. Sklonuj repozytorium i przejdź do katalogu
2. Skopiuj i edytuj konfigurację: `cp .env.example .env`
3. Uruchom instalację: `./install.sh`
4. Przetestuj system: `./scripts/test-flow.sh`

## Dostęp do Serwisów

- **Node-RED**: http://localhost:1880 - Zarządzanie workflow
- **Grafana**: http://localhost:3000 (admin/admin) - Monitoring i dashboardy  
- **Prometheus**: http://localhost:9090 - Metryki i alerty

## Konfiguracja Email

Edytuj plik `.env` i dodaj swoje dane:

```bash
EMAIL_SERVER=imap.gmail.com
EMAIL_USER=your-email@gmail.com
EMAIL_PASS=your-app-password

## Struktura Plików

## Struktura Projektów

Każdy email przechodzi przez:
1. **Pobranie** z serwera IMAP
2. **Analiza** przez LLM (klasyfikacja + wyciągnięcie intencji)
3. **Routing** na podstawie klasyfikacji
4. **Akcja** (alert, auto-reply, archiwizacja)
5. **Monitoring** (metryki, logi, dashboard)

## Backup

Utwórz backup: `./scripts/backup.sh`

## Troubleshooting

- Sprawdź logi: `docker-compose logs -f`
- Restart serwisów: `docker-compose restart`
- Pełna reinstalacja: `docker-compose down -v && ./install.sh`
```


