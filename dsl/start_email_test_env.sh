#!/bin/bash
# Skrypt do uruchamiania środowiska testowego dla powiadomień email i pipeline'u do analizy emaili

# Kolory do logowania
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== taskinity - Uruchamianie środowiska testowego dla powiadomień email ===${NC}"

# Sprawdzenie, czy Docker jest zainstalowany
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker nie jest zainstalowany. Zainstaluj Docker i spróbuj ponownie.${NC}"
    exit 1
fi

# Sprawdzenie, czy Docker Compose jest zainstalowany
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Docker Compose nie jest zainstalowany. Zainstaluj Docker Compose i spróbuj ponownie.${NC}"
    exit 1
fi

# Tworzenie katalogów, jeśli nie istnieją
echo -e "${BLUE}Tworzenie katalogów...${NC}"
mkdir -p logs flows dsl_definitions config emails

# Sprawdzenie, czy plik konfiguracyjny powiadomień istnieje
if [ ! -f "config/notification_config.json" ]; then
    echo -e "${YELLOW}Tworzenie domyślnego pliku konfiguracyjnego powiadomień...${NC}"
    cat > config/notification_config.json << EOL
{
    "enabled": true,
    "email": {
        "enabled": true,
        "smtp_server": "mailhog",
        "smtp_port": 1025,
        "username": "test",
        "password": "test",
        "from_email": "taskinity@example.com",
        "recipients": ["info@softreck.dev"]
    },
    "slack": {
        "enabled": false,
        "webhook_url": "",
        "channel": "#flow-notifications",
        "username": "taskinity Bot"
    },
    "notification_rules": {
        "on_start": true,
        "on_complete": true,
        "on_error": true,
        "include_details": true
    }
}
EOL
    echo -e "${GREEN}Utworzono domyślny plik konfiguracyjny powiadomień.${NC}"
fi

# Sprawdzenie, czy plik konfiguracyjny email pipeline istnieje
if [ ! -f "config/email_config.json" ]; then
    echo -e "${YELLOW}Tworzenie domyślnego pliku konfiguracyjnego email pipeline...${NC}"
    cat > config/email_config.json << EOL
{
    "imap": {
        "server": "mailhog",
        "port": 1143,
        "username": "test",
        "password": "test",
        "folder": "INBOX",
        "ssl": false
    },
    "smtp": {
        "server": "mailhog",
        "port": 1025,
        "username": "test",
        "password": "test",
        "from_email": "taskinity@example.com",
        "use_tls": false
    },
    "auto_reply": {
        "enabled": true,
        "criteria": {
            "subject_contains": ["pytanie", "zapytanie", "pomoc", "wsparcie"],
            "from_domains": ["example.com", "gmail.com"],
            "priority_keywords": ["pilne", "ważne", "urgent", "asap"]
        },
        "templates": {
            "default": "Dziękujemy za wiadomość. Odpowiemy najszybciej jak to możliwe.",
            "priority": "Dziękujemy za pilną wiadomość. Zajmiemy się nią priorytetowo.",
            "support": "Dziękujemy za zgłoszenie. Nasz zespół wsparcia skontaktuje się z Tobą wkrótce."
        },
        "signature": "\n\nPozdrawiamy,\nZespół taskinity",
        "reply_to_all": false,
        "add_original_message": true,
        "cooldown_hours": 24
    },
    "processing": {
        "check_interval_seconds": 10,
        "max_emails_per_batch": 10,
        "save_attachments": true,
        "attachments_folder": "emails/attachments",
        "archive_processed": true,
        "archive_folder": "Processed"
    },
    "flows": {
        "trigger_flow_on_email": true,
        "flow_mapping": {
            "support": "support_flow.dsl",
            "order": "order_processing.dsl",
            "complaint": "complaint_handling.dsl"
        }
    }
}
EOL
    echo -e "${GREEN}Utworzono domyślny plik konfiguracyjny email pipeline.${NC}"
fi

# Sprawdzenie, czy plik konfiguracyjny logowania istnieje
if [ ! -f "config/logging_config.json" ]; then
    echo -e "${YELLOW}Tworzenie domyślnego pliku konfiguracyjnego logowania...${NC}"
    cat > config/logging_config.json << EOL
{
    "console": {
        "enabled": true,
        "level": "INFO",
        "format": "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    },
    "file": {
        "enabled": true,
        "level": "DEBUG",
        "format": "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        "rotation": "1 day",
        "retention": "30 days",
        "compression": "zip"
    },
    "modules": {
        "flow_dsl": "DEBUG",
        "mini_dashboard": "INFO",
        "flow_visualizer": "INFO",
        "notification_service": "DEBUG",
        "parallel_executor": "DEBUG",
        "flow_scheduler": "DEBUG",
        "email_pipeline": "DEBUG"
    }
}
EOL
    echo -e "${GREEN}Utworzono domyślny plik konfiguracyjny logowania.${NC}"
fi

# Sprawdzenie, czy plik przykładowego przepływu dla obsługi emaili istnieje
if [ ! -f "dsl_definitions/support_flow.dsl" ]; then
    echo -e "${YELLOW}Tworzenie przykładowego przepływu dla obsługi emaili...${NC}"
    mkdir -p dsl_definitions
    cat > dsl_definitions/support_flow.dsl << EOL
{
    "name": "SupportFlow",
    "description": "Przepływ do obsługi zgłoszeń wsparcia z emaili",
    "tasks": [
        {
            "name": "parse_email",
            "description": "Parsowanie treści emaila"
        },
        {
            "name": "classify_issue",
            "description": "Klasyfikacja problemu"
        },
        {
            "name": "assign_to_agent",
            "description": "Przypisanie do agenta wsparcia"
        },
        {
            "name": "create_ticket",
            "description": "Utworzenie zgłoszenia w systemie"
        },
        {
            "name": "send_confirmation",
            "description": "Wysłanie potwierdzenia"
        }
    ],
    "connections": [
        {
            "source": "parse_email",
            "target": "classify_issue"
        },
        {
            "source": "classify_issue",
            "target": "assign_to_agent"
        },
        {
            "source": "assign_to_agent",
            "target": "create_ticket"
        },
        {
            "source": "create_ticket",
            "target": "send_confirmation"
        }
    ]
}
EOL
    echo -e "${GREEN}Utworzono przykładowy przepływ dla obsługi emaili.${NC}"
fi

# Uruchamianie środowiska Docker Compose
echo -e "${BLUE}Uruchamianie środowiska Docker Compose...${NC}"
docker-compose -f docker-compose-email.yml up -d

# Sprawdzenie, czy kontenery zostały uruchomione
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Środowisko testowe zostało uruchomione pomyślnie!${NC}"
    echo -e "${BLUE}Dostępne usługi:${NC}"
    echo -e "- ${YELLOW}MailHog (SMTP/Web UI):${NC} http://localhost:8025"
    echo -e "- ${YELLOW}Mini Dashboard:${NC} http://localhost:8765"
    echo -e "\n${BLUE}Aby zatrzymać środowisko, użyj:${NC} docker-compose -f docker-compose-email.yml down"
    echo -e "\n${BLUE}Aby wysłać testowy email:${NC}"
    echo -e "curl -X POST http://localhost:8025/api/v2/send \
    -H \"Content-Type: application/json\" \
    -d '{\"From\":\"test@example.com\",\"To\":[\"taskinity@example.com\"],\"Subject\":\"Pilne pytanie o wsparcie\",\"Text\":\"Potrzebuję pilnej pomocy z moim zamówieniem.\"}'"
else
    echo -e "${RED}Wystąpił błąd podczas uruchamiania środowiska.${NC}"
    exit 1
fi

exit 0
