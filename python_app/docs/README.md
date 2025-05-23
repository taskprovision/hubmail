# HubMail Python Application Documentation

## Overview

HubMail is an intelligent email processing system that uses Large Language Models (LLMs) to analyze and categorize emails, automate responses, and provide notifications based on email content. The system is built with a modular architecture using Python, FastAPI, and Prefect for workflow orchestration.

## Architecture

The application is structured into several key components:

1. **API Layer**: FastAPI-based REST API for external communication
2. **Flow Layer**: Prefect workflows that orchestrate the email processing pipeline
3. **Service Layer**: Specialized services for email, LLM, and notifications
4. **Model Layer**: Data models for emails and analysis results
5. **Utility Layer**: Logging and other utility functions

## System Components

### API (api/main.py)

The API layer provides HTTP endpoints for:
- Health checks
- Testing email analysis
- Triggering email checks
- Retrieving recent email analyses

### Flows

#### Email Processor (flows/email_processor.py)

The main workflow orchestrator that:
- Fetches new emails
- Processes each email with LLM analysis
- Sends notifications based on analysis results
- Marks emails as processed

#### Email Service (flows/email_service.py)

Handles email-specific operations:
- Fetching new emails from IMAP/POP3 servers
- Marking emails as read/processed
- Email storage and retrieval

#### LLM Service (flows/llm_service.py)

Manages interactions with Large Language Models:
- Analyzing email content
- Classifying emails by type and priority
- Generating summaries and action items
- Sentiment analysis

#### Notification Service (flows/notification_service.py)

Handles sending notifications based on email analysis:
- Email notifications for high-priority items
- Integration with messaging platforms
- Customizable notification rules

### Models

#### Email Models (models/email.py)

Data structures for:
- Email messages
- Email analysis results
- Classification schemas

### Utilities

#### Logger (utils/logger.py)

Centralized logging configuration for consistent log formatting across the application.

## Workflow Diagrams

### Main Email Processing Flow

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│  Fetch Emails   │────▶│ Process Emails  │────▶│  Send Notifs    │
│                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                              │
                              ▼
                        ┌─────────────────┐
                        │                 │
                        │  Mark as Seen   │
                        │                 │
                        └─────────────────┘
```

### Email Processing Detail

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│   Email Input   │────▶│  LLM Analysis   │────▶│ Classification  │
│                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                       │
                                                       ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│  Store Results  │◀────│ Action Items    │◀────│ Summarization   │
│                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check endpoint |
| `/api/test-analysis` | POST | Test email analysis with provided content |
| `/api/check-emails` | POST | Trigger a check for new emails |
| `/api/emails` | GET | Retrieve recent email analyses |

## Running the Application

### Prerequisites

- Python 3.10+
- Docker and Docker Compose (for containerized deployment)
- SMTP/IMAP access for email processing

### Environment Variables

Create a `.env` file with the following variables:

```
# API Configuration
API_PORT=3001
API_HOST=0.0.0.0

# Email Configuration
EMAIL_SERVER=imap.example.com
EMAIL_PORT=993
EMAIL_USERNAME=user@example.com
EMAIL_PASSWORD=your_password
EMAIL_USE_SSL=true

# LLM Configuration
LLM_PROVIDER=ollama
LLM_MODEL=llama2
LLM_API_KEY=your_api_key
LLM_API_URL=http://localhost:11434

# Notification Configuration
NOTIFICATION_EMAIL=alerts@example.com
SMTP_SERVER=smtp.example.com
SMTP_PORT=587
SMTP_USERNAME=user@example.com
SMTP_PASSWORD=your_password
SMTP_USE_TLS=true
```

### Starting the Application

```bash
# Install dependencies
pip install -r requirements.txt

# Run the API server
python -m api.main

# Run the email processing flow (can be scheduled with cron or Prefect)
python -m flows.email_processor
```

### Using Docker

```bash
# Build and start the containers
docker-compose up -d
```

## Testing

The application includes comprehensive unit tests for all components:

```bash
# Run all tests
python -m tests.run_tests

# Run specific test modules
python -m unittest tests.test_api
python -m unittest tests.test_email_processor
python -m unittest tests.test_llm_service
```

## Extending the Application

### Adding New Email Providers

Extend the `email_service.py` module with new connector classes for different email providers.

### Integrating Different LLM Providers

Add new provider classes in the `llm_service.py` module to support additional LLM services.

### Custom Notification Channels

Extend the `notification_service.py` module with new notification methods (Slack, Teams, etc.).
