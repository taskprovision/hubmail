#!/usr/bin/env python3
"""
Tests for the email processor module.
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
from flows.email_processor import process_email, check_emails


class TestEmailProcessor(unittest.TestCase):
    """Test cases for the email processor module."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_email = Email(
            id="test-123",
            from_address="test@example.com",
            subject="Test Subject",
            body="This is a test email body.",
            date=datetime.datetime.now()
        )
        
        self.test_analysis = EmailAnalysis(
            id="analysis-123",
            email_id="test-123",
            classification="test",
            priority="medium",
            summary="This is a test email.",
            action_items=["Reply to sender"],
            sentiment="neutral",
            created_at=datetime.datetime.now()
        )

    @patch('flows.llm_service.analyze_email_content')
    @patch('flows.notification_service.send_notification')
    @patch('flows.email_service.mark_as_seen')
    async def test_process_email(self, mock_mark_seen, mock_send_notification, mock_analyze):
        """Test processing a single email."""
        # Configure mocks
        mock_analyze.return_value = self.test_analysis
        mock_send_notification.return_value = None
        mock_mark_seen.return_value = None
        
        # Call the function
        result = await process_email(self.test_email)
        
        # Verify the result
        self.assertEqual(result['email']['id'], self.test_email.id)
        self.assertEqual(result['analysis']['id'], self.test_analysis.id)
        self.assertIn('processed_at', result)
        
        # Verify the mocks were called correctly
        mock_analyze.assert_called_once_with(self.test_email)
        mock_send_notification.assert_called_once_with(self.test_email, self.test_analysis)
        mock_mark_seen.assert_called_once_with(self.test_email.id)

    @patch('flows.email_service.fetch_new_emails')
    @patch('flows.email_processor.process_email')
    async def test_check_emails_with_emails(self, mock_process_email, mock_fetch_emails):
        """Test checking emails when there are new emails."""
        # Configure mocks
        mock_fetch_emails.return_value = [self.test_email]
        mock_process_email.return_value = {
            'email': self.test_email.dict(),
            'analysis': self.test_analysis.dict(),
            'processed_at': datetime.datetime.now().isoformat()
        }
        
        # Call the function
        results = await check_emails()
        
        # Verify the result
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['email']['id'], self.test_email.id)
        
        # Verify the mocks were called correctly
        mock_fetch_emails.assert_called_once()
        mock_process_email.assert_called_once_with(self.test_email)

    @patch('flows.email_service.fetch_new_emails')
    @patch('flows.email_processor.process_email')
    async def test_check_emails_no_emails(self, mock_process_email, mock_fetch_emails):
        """Test checking emails when there are no new emails."""
        # Configure mocks
        mock_fetch_emails.return_value = []
        
        # Call the function
        results = await check_emails()
        
        # Verify the result
        self.assertEqual(results, [])
        
        # Verify the mocks were called correctly
        mock_fetch_emails.assert_called_once()
        mock_process_email.assert_not_called()

    @patch('flows.email_service.fetch_new_emails')
    @patch('flows.email_processor.process_email')
    async def test_check_emails_with_error(self, mock_process_email, mock_fetch_emails):
        """Test checking emails when there's an error processing an email."""
        # Configure mocks
        mock_fetch_emails.return_value = [self.test_email]
        mock_process_email.side_effect = Exception("Test error")
        
        # Call the function
        results = await check_emails()
        
        # Verify the result
        self.assertEqual(results, [])
        
        # Verify the mocks were called correctly
        mock_fetch_emails.assert_called_once()
        mock_process_email.assert_called_once_with(self.test_email)


def run_async_test(coroutine):
    """Helper function to run async tests."""
    return asyncio.run(coroutine)


if __name__ == '__main__':
    unittest.main()
