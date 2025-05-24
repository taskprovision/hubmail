from prefect import task
import aiohttp
import os
from typing import Dict, Any
from dotenv import load_dotenv

import sys
import os

# Add the parent directory to sys.path to enable absolute imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.email import Email, EmailAnalysis, EmailClassification
from utils.logger import get_logger

# Load environment variables
load_dotenv()

# Initialize logger
logger = get_logger(__name__)

# Configuration
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "")
SLACK_CHANNEL = os.getenv("SLACK_CHANNEL", "#email-alerts")
COMPANY_NAME = os.getenv("COMPANY_NAME", "Softreck")

@task(name="Send Notification")
async def send_notification(email: Email, analysis: EmailAnalysis) -> bool:
    """
    Send notification based on email classification
    
    Args:
        email: The email that was analyzed
        analysis: Analysis results
        
    Returns:
        Success status
    """
    try:
        if analysis.classification == EmailClassification.URGENT:
            return await send_urgent_alert(email, analysis)
        elif analysis.classification == EmailClassification.BUSINESS:
            return await send_business_notification(email, analysis)
        elif analysis.classification == EmailClassification.SPAM:
            return await log_spam(email, analysis)
        elif analysis.classification == EmailClassification.PERSONAL:
            return await log_personal(email, analysis)
        else:
            logger.info(f"No notification sent for {email.id} with classification {analysis.classification}")
            return True
    except Exception as e:
        logger.error(f"Error sending notification for {email.id}: {str(e)}")
        return False

async def send_urgent_alert(email: Email, analysis: EmailAnalysis) -> bool:
    """
    Send an urgent alert for critical emails
    
    Args:
        email: The email that was analyzed
        analysis: Analysis results
        
    Returns:
        Success status
    """
    try:
        message = {
            "text": "🚨 URGENT EMAIL ALERT 🚨",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "🚨 URGENT EMAIL ALERT 🚨",
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*From:* {email.from_address}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Date:* {email.date.strftime('%Y-%m-%d %H:%M:%S')}"
                        }
                    ]
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Subject:* {email.subject}"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Content:*\n{email.body[:500]}{'...' if len(email.body) > 500 else ''}"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Confidence:* {(analysis.confidence * 100):.1f}%"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Suggested Action:* {analysis.suggested_action}"
                        }
                    ]
                }
            ]
        }
        
        await send_slack_notification(message)
        logger.info(f"Sent urgent alert for email: {email.id}")
        return True
    except Exception as e:
        logger.error(f"Error sending urgent alert for {email.id}: {str(e)}")
        return False

async def send_business_notification(email: Email, analysis: EmailAnalysis) -> bool:
    """
    Send a business notification for standard emails
    
    Args:
        email: The email that was analyzed
        analysis: Analysis results
        
    Returns:
        Success status
    """
    try:
        message = {
            "text": f"📧 Business Email: {email.subject}",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "📧 Business Email",
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*From:* {email.from_address}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Subject:* {email.subject}"
                        }
                    ]
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Classification:* Business ({(analysis.confidence * 100):.1f}% confidence)"
                    }
                }
            ]
        }
        
        await send_slack_notification(message)
        logger.info(f"Sent business notification for email: {email.id}")
        return True
    except Exception as e:
        logger.error(f"Error sending business notification for {email.id}: {str(e)}")
        return False

async def log_spam(email: Email, analysis: EmailAnalysis) -> bool:
    """
    Log spam emails
    
    Args:
        email: The email that was analyzed
        analysis: Analysis results
        
    Returns:
        Success status
    """
    try:
        logger.info({
            "email_id": email.id,
            "from": email.from_address,
            "subject": email.subject,
            "classification": "SPAM",
            "confidence": analysis.confidence,
            "reasoning": analysis.reasoning
        }, "Spam email detected")
        return True
    except Exception as e:
        logger.error(f"Error logging spam for {email.id}: {str(e)}")
        return False

async def log_personal(email: Email, analysis: EmailAnalysis) -> bool:
    """
    Log personal emails
    
    Args:
        email: The email that was analyzed
        analysis: Analysis results
        
    Returns:
        Success status
    """
    try:
        logger.info({
            "email_id": email.id,
            "from": email.from_address,
            "subject": email.subject,
            "classification": "PERSONAL",
            "confidence": analysis.confidence
        }, "Personal email detected")
        return True
    except Exception as e:
        logger.error(f"Error logging personal email for {email.id}: {str(e)}")
        return False

async def send_slack_notification(message: Dict[str, Any]) -> None:
    """
    Send a notification to Slack
    
    Args:
        message: Slack message object
        
    Raises:
        Exception: If sending fails
    """
    if not SLACK_WEBHOOK_URL:
        logger.warning("Slack webhook URL not configured, skipping notification")
        return
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                SLACK_WEBHOOK_URL,
                json=message,
                headers={"Content-Type": "application/json"},
                timeout=5
            ) as response:
                if response.status != 200:
                    text = await response.text()
                    raise Exception(f"Error sending Slack notification: {response.status} - {text}")
    except Exception as e:
        logger.error(f"Error sending Slack notification: {str(e)}")
        raise
