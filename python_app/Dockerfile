FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV API_PORT=3001
ENV UI_PORT=8501
ENV API_HOST=0.0.0.0
ENV UI_HOST=0.0.0.0

# Expose ports (using ARG to allow overriding at build time)
ARG API_PORT_ARG=3001
ARG UI_PORT_ARG=8501
EXPOSE ${API_PORT_ARG}
EXPOSE ${UI_PORT_ARG}

# Health check (using environment variables)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import requests; import os; requests.get(f'http://localhost:{os.environ.get(\"API_PORT\", 3001)}/health')"

# Entry point script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Start the application
ENTRYPOINT ["/entrypoint.sh"]
