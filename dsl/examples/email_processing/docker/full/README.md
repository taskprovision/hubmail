# Full Email Processing Docker Environment

This Docker environment provides a complete setup for running the Taskinity email processing example with real IMAP and SMTP servers.

## Features

- Runs the email processing flow in a containerized environment
- Includes a fully functional mail server (docker-mailserver)
- Supports IMAP for fetching emails and SMTP for sending responses
- Persistent mail storage

## Usage

### Starting the Environment

From the main email_processing directory, run:

```bash
make docker-up-full
```

Or directly with Docker Compose:

```bash
docker-compose -f docker/full/docker-compose.yml up -d
```

### Setting Up Email Accounts

Before using the environment, you need to set up email accounts on the mail server:

```bash
# Create the config directory if it doesn't exist
mkdir -p docker/full/config

# Add a new user (replace 'user@taskinity.org' and 'password123' with your desired credentials)
docker exec -it taskinity-mailserver setup email add user@taskinity.org password123

# Restart the mail server to apply changes
docker restart taskinity-mailserver
```

### Sending Test Emails

You can send test emails to the mail server using:

```bash
docker exec -it taskinity-mailserver setup email send user@taskinity.org support@taskinity.org "Test Subject" "This is a test email body"
```

### Viewing Logs

To view the logs from the email processor:

```bash
docker logs taskinity-email-processor
```

To view the mail server logs:

```bash
docker logs taskinity-mailserver
```

### Stopping the Environment

```bash
docker-compose -f docker/full/docker-compose.yml down
```

To completely remove all data (including mail storage):

```bash
docker-compose -f docker/full/docker-compose.yml down -v
```

## Configuration

The full environment uses the following configuration:

- Real IMAP and SMTP servers (docker-mailserver)
- Python 3.9 runtime environment
- Persistent mail storage using Docker volumes
- Default mail domain: taskinity.org

You can customize the environment variables in the docker-compose.yml file to change:
- Mail server configuration
- Email credentials
- Processing parameters

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
1. Fetch emails from a real IMAP server
2. Classify them into different categories
3. Process each category appropriately
4. Send responses via SMTP
