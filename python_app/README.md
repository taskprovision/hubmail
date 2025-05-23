# HubMail - Simplified Email Automation System

A streamlined email automation system with visual workflows and easy configuration.

## Architecture

This solution uses a modern Python stack designed for simplicity and ease of use:

1. **FastAPI** - Modern, fast web framework for building APIs
2. **Streamlit** - Simple visualization and UI with minimal code
3. **Prefect** - Flow-based task orchestration with visual graphs
4. **Pydantic** - Data validation and settings management

## Key Features

- **Visual Workflows**: See your email processing flows as visual graphs
- **Simple Configuration**: Easy to understand Python code with decorators
- **Interactive Dashboard**: Monitor and test your email processing in real-time
- **Type Annotations**: Clear interfaces with Python type hints
- **Modular Design**: Easy to extend and modify components

## Getting Started

1. Make sure Docker and Docker Compose are installed
2. Configure your email settings in the `.env` file
3. Run `docker-compose up -d` to start the system
4. Access the dashboard at http://localhost:8501

## Components

- **API** (`/api`): FastAPI-based REST API for email processing
- **Flows** (`/flows`): Prefect workflows for email processing
- **UI** (`/ui`): Streamlit dashboard for visualization
- **Models** (`/models`): Pydantic data models
- **Utils** (`/utils`): Utility functions and helpers

## Extending the System

### Adding a New Email Processor

```python
from prefect import task
from models.email import Email, EmailAnalysis

@task(name="My Custom Processor")
async def process_special_emails(email: Email) -> EmailAnalysis:
    # Your custom logic here
    return EmailAnalysis(...)
```

### Adding a New UI Component

```python
import streamlit as st

def show_custom_metrics():
    st.header("My Custom Metrics")
    st.metric("Important Value", 42, 5)
```

## Troubleshooting

- **API not responding**: Check logs with `docker-compose logs hubmail-app`
- **Email processing not working**: Verify your email credentials in `.env`
- **Dashboard not showing data**: Ensure the API is running properly

## Benefits Over the Previous Solution

- **Simpler Code**: Python with decorators reduces boilerplate
- **Visual Workflows**: See your processing flows as visual graphs
- **Interactive Dashboard**: Test and monitor in real-time
- **Type Safety**: Catch errors before they happen with type annotations
- **Faster Development**: Make changes quickly and see results immediately
