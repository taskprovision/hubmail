# Mock Email Processing Docker Environment

This Docker environment provides a development-friendly setup for running the Taskinity email processing example with a mock email server (MailHog) that provides both SMTP and a web interface for viewing emails.

## Features

- Runs the email processing flow in a containerized environment
- Includes MailHog for simulating SMTP and viewing sent emails
- Web UI for inspecting sent emails
- Perfect for development and testing without real email accounts

## Usage

### Starting the Environment

From the main email_processing directory, run:

```bash
make docker-up-mock
```

Or directly with Docker Compose:

```bash
docker-compose -f docker/mock/docker-compose.yml up -d
```

### Accessing the Web UI

The MailHog web interface is available at:

```
http://localhost:8025
```

This interface allows you to:
- View all sent emails
- Inspect email content, headers, and attachments
- Release emails to real SMTP servers (if configured)
- Search and filter emails

### Sending Test Emails

You can send test emails to the mock server using any SMTP client configured to use:
- Server: localhost
- Port: 1025
- No authentication required

For example, using Python:

```python
import smtplib
from email.mime.text import MIMEText

msg = MIMEText("This is a test email")
msg["Subject"] = "Test Email"
msg["From"] = "sender@taskinity.org"
msg["To"] = "recipient@taskinity.org"

with smtplib.SMTP("localhost", 1025) as server:
    server.send_message(msg)
```

### Viewing Logs

To view the logs from the email processor:

```bash
docker logs taskinity-email-mock
```

To view the MailHog logs:

```bash
docker logs taskinity-mockserver
```

### Stopping the Environment

```bash
docker-compose -f docker/mock/docker-compose.yml down
```

## Configuration

The mock environment uses the following configuration:

- MailHog for SMTP and email viewing
- Python 3.9 runtime environment
- Web UI for email inspection
- No authentication required for SMTP

## Flow DSL

The email processing flow is defined in the main `flow.py` file and uses the following DSL:

```
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
```

This flow demonstrates how to:
1. Fetch emails (mock data in this environment)
2. Classify them into different categories
3. Process each category appropriately
4. Send responses via SMTP (which can be viewed in the MailHog UI)
