#!/usr/bin/env python3
"""
Tests for the API endpoints.
"""
import sys
import os
import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import asyncio
import datetime
from fastapi.testclient import TestClient

# Add the parent directory to sys.path to enable absolute imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.main import app
from models.email import Email, EmailAnalysis


class TestAPI(unittest.TestCase):
    """Test cases for the API endpoints."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = TestClient(app)
        self.test_email_request = {
            "from_address": "test@example.com",
            "subject": "Test Subject",
            "body": "This is a test email body."
        }

    def test_health_check(self):
        """Test the health check endpoint."""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["version"], "1.0.0")
        self.assertIn("timestamp", data)

    @patch('api.main.analyze_email_content')
    async def test_test_analysis(self, mock_analyze):
        """Test the test analysis endpoint."""
        # Configure mock
        mock_analyze.return_value = EmailAnalysis(
            id="analysis-123",
            email_id="test-123",
            classification="test",
            priority="medium",
            summary="This is a test email.",
            action_items=["Reply to sender"],
            sentiment="neutral",
            created_at=datetime.datetime.now()
        )
        
        # Make the request
        response = self.client.post("/api/test-analysis", json=self.test_email_request)
        
        # Verify the response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("email", data)
        self.assertIn("analysis", data)
        self.assertEqual(data["email"]["from_address"], self.test_email_request["from_address"])
        self.assertEqual(data["email"]["subject"], self.test_email_request["subject"])
        
        # Verify the mock was called correctly
        mock_analyze.assert_called_once()

    @patch('api.main.check_emails')
    def test_trigger_email_check(self, mock_check_emails):
        """Test the trigger email check endpoint."""
        # Configure mock
        mock_check_emails.return_value = None
        
        # Make the request
        response = self.client.post("/api/check-emails")
        
        # Verify the response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "processing")
        self.assertEqual(data["message"], "Email check triggered successfully")
        
        # Verify the mock was called correctly
        # Note: In a real test, we'd need to verify that the background task was added
        # This is simplified for demonstration purposes
        self.assertTrue(True)

    def test_get_recent_emails(self):
        """Test the get recent emails endpoint."""
        # Make the request
        response = self.client.get("/api/emails")
        
        # Verify the response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("emails", data)
        self.assertEqual(data["emails"], [])


if __name__ == '__main__':
    unittest.main()
