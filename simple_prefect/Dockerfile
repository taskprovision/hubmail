FROM python:3.9-slim

WORKDIR /app

# Instalacja zależności systemowych
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Kopiowanie plików projektu
COPY requirements.txt .
COPY .env.example .

# Instalacja zależności Pythona
RUN pip install --no-cache-dir -r requirements.txt

# Instalacja debugpy dla zdalnego debugowania
RUN pip install --no-cache-dir debugpy

# Tworzenie katalogów
RUN mkdir -p attachments logs test_data/attachments

# Kopiowanie kodu źródłowego
COPY *.py .
COPY test_data/ test_data/

# Ustawienie zmiennych środowiskowych
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Otworzenie portów
EXPOSE 5678

# Uruchomienie aplikacji
CMD ["python", "email_flows.py"]
