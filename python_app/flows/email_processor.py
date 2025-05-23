from prefect import flow, task
from prefect.task_runners import SequentialTaskRunner
from typing import List, Dict, Any, Optional
import asyncio
import datetime
import os
from dotenv import load_dotenv

# Import our modules
import sys
import os

# Add the parent directory to sys.path to enable absolute imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.email import Email, EmailAnalysis
from utils.logger import get_logger
from flows.llm_service import analyze_email_content
from flows.notification_service import send_notification
from flows.email_service import fetch_new_emails, mark_as_seen

# Load environment variables
load_dotenv()

# Initialize logger
logger = get_logger(__name__)

@task(name="Process Single Email", retries=2, retry_delay_seconds=5)
async def process_email(email: Email) -> Dict[str, Any]:
    """
    Process a single email with LLM analysis and notifications
    
    Args:
        email: The email to process
        
    Returns:
        Dict containing the email and its analysis
    """
    logger.info(f"Processing email: {email.id} - {email.subject}")
    
    try:
        # Analyze email with LLM
        analysis = await analyze_email_content(email)
        
        # Send notifications based on classification
        await send_notification(email, analysis)
        
        # Mark email as processed
        await mark_as_seen(email.id)
        
        # Return results
        return {
            "email": email.dict(),
            "analysis": analysis.dict(),
            "processed_at": datetime.datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error processing email {email.id}: {str(e)}")
        raise
        
@flow(name="Email Processing Flow", task_runner=SequentialTaskRunner())
async def check_emails() -> List[Dict[str, Any]]:
    """
    Main flow to check for new emails and process them
    
    Returns:
        List of processed email results
    """
    logger.info("Starting email check flow")
    
    try:
        # Fetch new emails
        emails = await fetch_new_emails()
        logger.info(f"Fetched {len(emails)} new emails")
        
        if not emails:
            logger.info("No new emails to process")
            return []
            
        # Process each email
        results = []
        for email in emails:
            try:
                result = await process_email(email)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to process email {email.id}: {str(e)}")
                
        logger.info(f"Processed {len(results)} emails successfully")
        return results
    except Exception as e:
        logger.error(f"Error in email check flow: {str(e)}")
        return []

# For manual testing
if __name__ == "__main__":
    asyncio.run(check_emails())
