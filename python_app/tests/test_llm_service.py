#!/usr/bin/env python3
"""
Tests for the LLM service module.
"""
import sys
import os
import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import asyncio
import datetime

# Add the parent directory to sys.path to enable absolute imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.email import Email, EmailAnalysis
from flows.llm_service import analyze_email_content


class TestLLMService(unittest.TestCase):
    """Test cases for the LLM service module."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_email = Email(
            id="test-123",
            from_address="test@example.com",
            subject="Test Subject",
            body="This is a test email body.",
            date=datetime.datetime.now()
        )

    @patch('flows.llm_service.get_llm_client')
    async def test_analyze_email_content(self, mock_get_llm_client):
        """Test analyzing email content with LLM."""
        # Configure mock
        mock_llm = MagicMock()
        mock_llm.analyze_text = AsyncMock(return_value={
            "classification": "test",
            "priority": "medium",
            "summary": "This is a test email.",
            "action_items": ["Reply to sender"],
            "sentiment": "neutral"
        })
        mock_get_llm_client.return_value = mock_llm
        
        # Call the function
        result = await analyze_email_content(self.test_email)
        
        # Verify the result
        self.assertEqual(result.email_id, self.test_email.id)
        self.assertEqual(result.classification, "test")
        self.assertEqual(result.priority, "medium")
        self.assertEqual(result.summary, "This is a test email.")
        self.assertEqual(result.action_items, ["Reply to sender"])
        self.assertEqual(result.sentiment, "neutral")
        
        # Verify the mock was called correctly
        mock_get_llm_client.assert_called_once()
        mock_llm.analyze_text.assert_called_once()
        

def run_async_test(coroutine):
    """Helper function to run async tests."""
    return asyncio.run(coroutine)


if __name__ == '__main__':
    unittest.main()
