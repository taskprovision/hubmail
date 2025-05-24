#!/usr/bin/env python3
"""
Email processing flow example for Taskinity.
"""
import sys

# Check if running in mock mode
if '--mock' in sys.argv:
    # Create mock task decorator
    def task(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    
    # Create mock run_flow_from_dsl function
    def run_flow_from_dsl(flow_dsl, input_data):
        print(f"Running mock email flow")
        return {
            "process_urgent": [
                {"id": "1", "response": "Urgent response to: Urgent matter"}
            ],
            "process_regular": [
                {"id": "2", "response": "Standard response to: Newsletter"},
                {"id": "3", "response": "Standard response to: General inquiry"}
            ]
        }
else:
    # Import real Taskinity functionality
    try:
        from taskinity.core.taskinity_core import task, run_flow_from_dsl
    except ImportError:
        print("Error: Could not import Taskinity modules. Run with --mock flag for testing.")
        sys.exit(1)

@task(name="Fetch Emails")
def fetch_emails():
    print("Fetching emails...")
    emails = [
        {"id": "1", "subject": "Urgent matter", "urgent": True},
        {"id": "2", "subject": "Newsletter", "urgent": False},
        {"id": "3", "subject": "General inquiry", "urgent": False}
    ]
    return emails

@task(name="Classify Emails")
def classify_emails(emails):
    print(f"Classifying {len(emails)} emails")
    urgent = [email for email in emails if email.get("urgent", False)]
    regular = [email for email in emails if not email.get("urgent", False)]
    return {"urgent": urgent, "regular": regular}

@task(name="Process Urgent Emails")
def process_urgent(urgent_emails):
    print(f"Processing {len(urgent_emails)} urgent emails")
    responses = []
    for email in urgent_emails:
        responses.append({"id": email["id"], "response": f"Urgent response to: {email['subject']}"})  
    return responses

@task(name="Process Regular Emails")
def process_regular(regular_emails):
    print(f"Processing {len(regular_emails)} regular emails")
    responses = []
    for email in regular_emails:
        responses.append({"id": email["id"], "response": f"Standard response to: {email['subject']}"})  
    return responses

# Define the flow DSL
flow_dsl = """
flow EmailProcessing:
    description: "Email processing flow"
    fetch_emails -> classify_emails
    classify_emails.urgent -> process_urgent
    classify_emails.regular -> process_regular
"""

# Run the flow
result = run_flow_from_dsl(flow_dsl, {})
print("\nFlow results:")
print(f"Processed emails: {len(result.get('process_urgent', [])) + len(result.get('process_regular', []))}")
print(f"Urgent: {len(result.get('process_urgent', []))}")
print(f"Regular: {len(result.get('process_regular', []))}")

# Print sample responses
if result.get('process_urgent'):
    print("\nSample urgent response:")
    print(result['process_urgent'][0]['response'])

if result.get('process_regular'):
    print("\nSample regular response:")
    print(result['process_regular'][0]['response'])
