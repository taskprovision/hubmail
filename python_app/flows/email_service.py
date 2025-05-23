from prefect import task
from imap_tools import MailBox, AND
from typing import List, Dict, Any, Optional
import os
import hashlib
import datetime
from dotenv import load_dotenv

from ..models.email import Email
from ..utils.logger import get_logger

# Load environment variables
load_dotenv()

# Initialize logger
logger = get_logger(__name__)

# Configuration
EMAIL_SERVER = os.getenv("EMAIL_SERVER", "imap.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "993"))
EMAIL_USER = os.getenv("EMAIL_USER", "")
EMAIL_PASS = os.getenv("EMAIL_PASS", "")
EMAIL_USE_SSL = os.getenv("EMAIL_USE_SSL", "true").lower() == "true"
EMAIL_BATCH_SIZE = int(os.getenv("EMAIL_BATCH_SIZE", "50"))

# Keep track of last fetch time
last_fetch_time = datetime.datetime.now()

@task(name="Fetch New Emails", retries=2, retry_delay_seconds=10)
async def fetch_new_emails() -> List[Email]:
    """
    Fetch new emails from the email server
    
    Returns:
        List of Email objects
    """
    global last_fetch_time
    
    logger.info(f"Fetching new emails since {last_fetch_time}")
    
    if not EMAIL_USER or not EMAIL_PASS:
        logger.warning("Email credentials not configured")
        return []
    
    try:
        # Connect to mailbox
        with MailBox(EMAIL_SERVER, EMAIL_PORT).login(EMAIL_USER, EMAIL_PASS, initial_folder='INBOX') as mailbox:
            # Search for unseen emails since last fetch
            emails = []
            criteria = AND(seen=False, date_gte=last_fetch_time.date())
            
            for msg in mailbox.fetch(criteria, limit=EMAIL_BATCH_SIZE):
                try:
                    # Create unique ID
                    unique_id = hashlib.md5(
                        f"{msg.uid}_{msg.date.isoformat()}_{msg.from_}".encode()
                    ).hexdigest()
                    
                    # Create Email object
                    email = Email(
                        id=unique_id,
                        from_address=msg.from_,
                        to_address=msg.to,
                        subject=msg.subject,
                        body=msg.text or msg.html,
                        html=msg.html,
                        date=msg.date,
                        has_attachments=bool(msg.attachments),
                        attachments=[
                            {
                                "filename": att.filename,
                                "content_type": att.content_type,
                                "size": len(att.payload)
                            }
                            for att in msg.attachments
                        ]
                    )
                    
                    emails.append(email)
                except Exception as e:
                    logger.error(f"Error processing email message: {str(e)}")
            
            # Update last fetch time
            last_fetch_time = datetime.datetime.now()
            
            logger.info(f"Fetched {len(emails)} new emails")
            return emails
    except Exception as e:
        logger.error(f"Error fetching emails: {str(e)}")
        return []

@task(name="Mark Email as Seen")
async def mark_as_seen(email_id: str) -> bool:
    """
    Mark an email as seen
    
    Args:
        email_id: Unique ID of the email
        
    Returns:
        Success status
    """
    # In a real implementation, this would mark the email as seen in the mailbox
    # For now, just log it
    logger.info(f"Marked email {email_id} as seen")
    return True

@task(name="Move Email to Folder")
async def move_to_folder(email_id: str, folder: str) -> bool:
    """
    Move an email to a specific folder
    
    Args:
        email_id: Unique ID of the email
        folder: Target folder
        
    Returns:
        Success status
    """
    # In a real implementation, this would move the email to the specified folder
    # For now, just log it
    logger.info(f"Moved email {email_id} to folder {folder}")
    return True
