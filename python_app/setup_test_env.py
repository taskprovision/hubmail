#!/usr/bin/env python3
"""
Setup script to create the necessary directories and files for testing.
This ensures that all required modules and mock implementations are available.
"""
import os
import sys
from pathlib import Path

def ensure_dir(directory):
    """Ensure a directory exists"""
    Path(directory).mkdir(parents=True, exist_ok=True)
    print(f"✓ Ensured directory exists: {directory}")

def create_file(file_path, content):
    """Create a file with the given content if it doesn't exist"""
    if not os.path.exists(file_path):
        with open(file_path, 'w') as f:
            f.write(content)
        print(f"✓ Created file: {file_path}")
    else:
        print(f"✓ File already exists: {file_path}")

def setup_test_environment():
    """Set up the test environment with all necessary files and directories"""
    # Get the base directory (python_app)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Ensure all required directories exist
    directories = [
        os.path.join(base_dir, "tests"),
        os.path.join(base_dir, "models"),
        os.path.join(base_dir, "flows"),
        os.path.join(base_dir, "api"),
        os.path.join(base_dir, "utils"),
    ]
    
    for directory in directories:
        ensure_dir(directory)
    
    # Create __init__.py files in each directory to make them proper packages
    for directory in directories:
        init_file = os.path.join(directory, "__init__.py")
        create_file(init_file, "# Package initialization\n")
    
    # Create a mock utils/logger.py if it doesn't exist
    logger_file = os.path.join(base_dir, "utils", "logger.py")
    logger_content = """
import logging

def get_logger(name):
    """Get a logger instance with the given name"""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s | %(levelname)-8s | %(name)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger
"""
    create_file(logger_file, logger_content)
    
    # Create a mock flows/llm_service.py if it doesn't exist
    llm_service_file = os.path.join(base_dir, "flows", "llm_service.py")
    llm_service_content = """
from models.email import Email, EmailAnalysis, EmailClassification
import asyncio

async def analyze_email_content(email):
    """Mock implementation of email analysis"""
    # This is a mock implementation for testing
    return EmailAnalysis(
        classification=EmailClassification.BUSINESS,
        confidence=0.85,
        reasoning="This is a test email",
        suggested_action="Reply to sender"
    )

def get_llm_client():
    """Mock implementation of LLM client"""
    return MockLLMClient()

class MockLLMClient:
    async def analyze_text(self, text):
        return {
            "classification": "BUSINESS",
            "confidence": 0.85,
            "reasoning": "This is a test email",
            "suggested_action": "Reply to sender"
        }
"""
    create_file(llm_service_file, llm_service_content)
    
    # Create a mock flows/notification_service.py if it doesn't exist
    notification_file = os.path.join(base_dir, "flows", "notification_service.py")
    notification_content = """
async def send_notification(email, analysis):
    """Mock implementation of notification sending"""
    # This is a mock implementation for testing
    print(f"Sending notification for email: {email.id}")
    return True
"""
    create_file(notification_file, notification_content)
    
    # Create a mock flows/email_service.py if it doesn't exist
    email_service_file = os.path.join(base_dir, "flows", "email_service.py")
    email_service_content = """
from models.email import Email
import datetime

async def fetch_new_emails():
    """Mock implementation of email fetching"""
    # This is a mock implementation for testing
    return [
        Email(
            id="test-123",
            from_address="test@example.com",
            subject="Test Subject",
            body="This is a test email body.",
            date=datetime.datetime.now()
        )
    ]

async def mark_as_seen(email_id):
    """Mock implementation of marking an email as seen"""
    # This is a mock implementation for testing
    print(f"Marking email as seen: {email_id}")
    return True
"""
    create_file(email_service_file, email_service_content)
    
    print("\n✅ Test environment setup complete!")
    print("You can now run the tests with: ./tests/run_tests.sh")

if __name__ == "__main__":
    setup_test_environment()
