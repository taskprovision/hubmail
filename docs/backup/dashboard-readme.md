# HubMail - Email Intelligence Hub

## Real-time Email Processing & Monitoring Dashboard

Dashboard z żywym monitoringiem wszystkich serwisów HubMail, automatycznym odczytem konfiguracji z .env i docker-compose.yml.

## 🚀 Funkcje

- **Real-time Status**: Żywy monitoring wszystkich serwisów
- **Auto-Configuration**: Automatyczny odczyt portów z .env
- **One-Click Access**: Klik w kartę serwisu = otwarcie w nowej karcie
- **Health Checks**: Sprawdzanie zdrowia każdego serwisu
- **Auto-Refresh**: Odświeżanie co 30 sekund
- **REST API**: Programowy dostęp do statusów
- **Responsive Design**: Działa na desktop i mobile
- **Email Classification**: Automatyczna klasyfikacja emaili (URGENT/BUSINESS/SPAM/PERSONAL)
- **Process Automation**: Automatyczne odpowiedzi i routing emaili

## 📦 Instalacja

### Opcja 1: Zintegrowany z Docker Compose (Zalecane)
```bash
# 1. Uruchom skrypt setup
chmod +x setup-dashboard.sh
./setup-dashboard.sh integrated

# 2. Dashboard automatycznie startuje z resztą serwisów
docker-compose up -d

# 3. Otwórz dashboard
open http://localhost:8000
```

### Opcja 2: Standalone Python App
```bash
# 1. Zainstaluj wymagania
pip3 install -r requirements.txt

# 2. Uruchom dashboard
./setup-dashboard.sh standalone

# 3. Otwórz dashboard
open http://localhost:8000
```

### Opcja 3: Osobny kontener Docker
```bash
# 1. Uruchom jako osobny serwis
./setup-dashboard.sh docker

# 2. Dashboard działa niezależnie
docker-compose -f docker-compose.dashboard.yml ps
```

## 🎯 Dostęp

| Endpoint | Opis |
|----------|------|
| **http://localhost:8000** | Główny dashboard |
| **http://localhost:8000/api/services** | Status wszystkich serwisów (JSON) |
| **http://localhost:8000/api/service/{name}/health** | Status konkretnego serwisu |
| **http://localhost:8000/api/config** | Aktualna konfiguracja |
| **http://localhost:8000/api/stats** | Statystyki systemu |

## 🎮 Klawisze skrótu

- **Ctrl+R**: Odśwież dashboard
- **Ctrl+I**: Pokaż informacje systemowe
- **Ctrl+Click**: Test zdrowia serwisu

## 🔧 Konfiguracja

Dashboard automatycznie czyta konfigurację z:

### .env file
```bash
# Porty serwisów (automatycznie wykrywane)
NODERED_PORT=1880
OLLAMA_PORT=11435
PROMETHEUS_PORT=9090
GRAFANA_PORT=3000
REDIS_PORT=6379

# Konfiguracja dashboard
DASHBOARD_PORT=8000
DASHBOARD_HOST=0.0.0.0
```

### docker-compose.yml
Dashboard automatycznie skanuje docker-compose.yml dla:
- Mapowania portów
- Nazwy serwisów
- Obrazy Docker
- Nazwy kontenerów

## 📊 Monitored Services

Dashboard monitoruje następujące serwisy:

### Core Services
- **Node-RED** (Port: 1880) - Workflow designer
- **Grafana** (Port: 3000) - Analytics dashboard
- **Prometheus** (Port: 9090) - Metrics collection

### AI & Cache
- **Ollama** (Port: 11435) - Local AI models
- **Redis** (Port: 6379) - Cache storage

## 🔍 Status Indicators

- 🟢 **Online**: Serwis działa poprawnie
- 🔴 **Offline**: Serwis nie odpowiada
- 🟡 **Degraded**: Serwis działa z problemami
- ⚪ **Not Configured**: Serwis nie skonfigurowany

## 🌐 API Usage

### Get All Services Status
```bash
curl http://localhost:8000/api/services
```

Response:
```json
{
  "services": [
    {
      "name": "node-red",
      "display_name": "Node-RED",
      "status": "online",
      "url": "http://localhost:1880",
      "port": "1880",
      "response_time": 45,
      "status_code": 200
    }
  ],
  "timestamp": "2024-01-20T10:30:00",
  "total_services": 5,
  "online_services": 5
}
```

### Check Specific Service
```bash
curl http://localhost:8000/api/service/node-red/health
```

### Get System Stats
```bash
curl http://localhost:8000/api/stats
```

Response:
```json
{
  "total_services": 5,
  "online_services": 5,
  "offline_services": 0,
  "health_percentage": 100,
  "categories": ["Core", "AI", "Cache"],
  "last_check": "2024-01-20T10:30:00"
}
```

## 🎨 Customization

### Custom Service Icons
Edytuj `app.py` w sekcji `service_definitions`:

```python
'my_service': {
    'name': 'My Custom Service',
    'description': 'Custom service description',
    'icon': 'fas fa-custom-icon',
    'color': 'success',
    'health_endpoint': '/health',
    'category': 'Custom'
}
```

### Custom CSS
Dodaj własne style w `templates/dashboard.html`:

```css
.custom-service-card {
    background: linear-gradient(45deg, #your-color1, #your-color2);
}
```

### Custom Health Checks
```python
async def custom_health_check(self, service_name: str, url: str) -> Dict:
    # Implementuj własną logikę health check
    return {
        'status': 'online',
        'custom_metric': 'value'
    }
```

## 🔌 Adding New Services
1. Dodaj definicję serwisu w `service_definitions`
2. Dodaj mapowanie portu w `get_service_url()`
3. Opcjonalnie: dodaj custom health check endpoint

### Environment Variables
```bash
# Development
export DASHBOARD_PORT=8000
export DASHBOARD_HOST=localhost
export ENV_FILE=.env.development

# Production
export DASHBOARD_PORT=80
export DASHBOARD_HOST=0.0.0.0
export ENV_FILE=.env.production
```

## 🐳 Docker Configuration

### Dockerfile.dashboard
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "app.py"]
```

### docker-compose integration
```yaml
services:
  dashboard:
    build:
      context: .
      dockerfile: Dockerfile.dashboard
    ports:
      - "${DASHBOARD_PORT:-8000}:8000"
    volumes:
      - ./.env:/app/.env:ro
      - ./docker-compose.yml:/app/docker-compose.yml:ro
    depends_on:
      - node-red
      - grafana
      - prometheus
```

## 📈 Monitoring Features

### Auto-Refresh
- Automatyczne odświeżanie co 30 sekund
- Możliwość ręcznego odświeżenia (Ctrl+R)
- Visual loading indicators

### Health Metrics
- Response time tracking
- HTTP status codes
- Error logging
- Availability percentages

### System Information
- Configuration display
- Service URLs
- Port mappings
- Environment variables

## 🚨 Troubleshooting

### Dashboard nie startuje
```bash
# Sprawdź porty
netstat -tulpn | grep 8000

# Sprawdź logi
docker-compose logs dashboard

# Reset dashboard
docker-compose restart dashboard
```

### Serwisy pokazują offline
```bash
# Sprawdź połączenie sieciowe
docker network ls
docker network inspect hub-net

# Test bezpośredni
curl http://localhost:1880
curl http://localhost:3000
```

### Błędy konfiguracji
```bash
# Waliduj .env
cat .env | grep -v "^#" | grep "="

# Sprawdź docker-compose
docker-compose config

# Test konfiguracji dashboard
curl http://localhost:8000/api/config
```

## 📚 Related Documentation

- [USER-GUIDE.md](USER-GUIDE.md) - How to use HubMail services
- [ADMIN-GUIDE.md](ADMIN-GUIDE.md) - System administration
- [API-REFERENCE.md](API-REFERENCE.md) - Complete API documentation
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Problem solving guide

---

**🎉 Dashboard jest gotowy do użycia!**

1. Uruchom: `./setup-dashboard.sh`
2. Otwórz: http://localhost:8000
3. Klikaj karty serwisów aby je otworzyć
4. Monitoruj status w czasie rzeczywistym