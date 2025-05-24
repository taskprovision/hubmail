#!/usr/bin/env python3
"""
Main flow for Taskinity email processing example.
This file ties together all the email processing tasks.
"""
import os
import json
from dotenv import load_dotenv
from pathlib import Path

# Import Taskinity core functionality
from taskinity.core.taskinity_core import run_flow_from_dsl, save_dsl, load_dsl

# Import tasks
from tasks import (
    fetch_emails,
    classify_emails,
    process_urgent_emails,
    process_emails_with_attachments,
    process_support_emails,
    process_order_emails,
    process_regular_emails,
    send_responses
)

# Load environment variables
load_dotenv()

# Define the email processing flow DSL
EMAIL_PROCESSING_DSL = """
flow EmailProcessing:
    description: "Email processing flow with categorization"
    fetch_emails -> classify_emails
    classify_emails -> process_urgent_emails
    classify_emails -> process_emails_with_attachments
    classify_emails -> process_support_emails
    classify_emails -> process_order_emails
    classify_emails -> process_regular_emails
    process_urgent_emails -> send_responses
    process_emails_with_attachments -> send_responses
    process_support_emails -> send_responses
    process_order_emails -> send_responses
    process_regular_emails -> send_responses
"""

def save_flow_definition(dsl_text, filename="email_processing.dsl"):
    """Save the flow definition to a file."""
    # Create dsl_definitions directory if it doesn't exist
    dsl_dir = Path("dsl_definitions")
    dsl_dir.mkdir(exist_ok=True)
    
    # Save the DSL to a file
    save_dsl(dsl_text, filename)
    print(f"Flow definition saved to {dsl_dir / filename}")

def run_email_flow(server=None, username=None, password=None, folder="INBOX", limit=10):
    """Run the email processing flow."""
    # Get email server credentials from environment variables if not provided
    if not server:
        server = os.getenv("IMAP_SERVER", "imap.example.com")
    if not username:
        username = os.getenv("IMAP_USERNAME", "user@example.com")
    if not password:
        password = os.getenv("IMAP_PASSWORD", "password123")
    
    # Prepare input data
    input_data = {
        "server": server,
        "username": username,
        "password": password,
        "folder": folder,
        "limit": limit
    }
    
    # Save the flow definition
    save_flow_definition(EMAIL_PROCESSING_DSL)
    
    # Run the flow
    print(f"Running email processing flow for {username} on {server}...")
    results = run_flow_from_dsl(EMAIL_PROCESSING_DSL, input_data)
    
    # Print results
    print("\nEmail Processing Results:")
    if "send_responses" in results:
        response_results = results["send_responses"]
        print(f"Total emails processed: {response_results.get('total_attempted', 0)}")
        print(f"Total emails sent: {response_results.get('total_sent', 0)}")
        print(f"  - Urgent: {response_results.get('sent_urgent', 0)}")
        print(f"  - With attachments: {response_results.get('sent_attachments', 0)}")
        print(f"  - Support: {response_results.get('sent_support', 0)}")
        print(f"  - Orders: {response_results.get('sent_orders', 0)}")
        print(f"  - Regular: {response_results.get('sent_regular', 0)}")
    else:
        print("No email responses were sent.")
    
    return results

def main():
    """Main function to run the email processing flow."""
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Run email processing flow")
    parser.add_argument("--server", help="IMAP server address")
    parser.add_argument("--username", help="Email username")
    parser.add_argument("--password", help="Email password")
    parser.add_argument("--folder", default="INBOX", help="Email folder to process")
    parser.add_argument("--limit", type=int, default=10, help="Maximum number of emails to process")
    parser.add_argument("--save-only", action="store_true", help="Only save the flow definition, don't run it")
    parser.add_argument("--mock", action="store_true", help="Use mock data instead of connecting to a real server")
    
    args = parser.parse_args()
    
    # Set mock mode if requested
    if args.mock:
        os.environ["MOCK_EMAILS"] = "true"
    
    # Save flow definition only if requested
    if args.save_only:
        save_flow_definition(EMAIL_PROCESSING_DSL)
        return
    
    # Run the flow
    run_email_flow(
        server=args.server,
        username=args.username,
        password=args.password,
        folder=args.folder,
        limit=args.limit
    )

if __name__ == "__main__":
    main()
