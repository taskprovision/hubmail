# Basic Email Processing Docker Environment

This Docker environment provides a simple setup for running the Taskinity email processing example with mock data.

## Features

- Runs the email processing flow in a containerized environment
- Uses mock email data (no actual email server connections)
- Minimal configuration required

## Usage

### Starting the Environment

From the main email_processing directory, run:

```bash
make docker-up-basic
```

Or directly with Docker Compose:

```bash
docker-compose -f docker/basic/docker-compose.yml up -d
```

### Viewing Logs

To view the logs from the container:

```bash
docker logs taskinity-email-basic
```

### Stopping the Environment

```bash
docker-compose -f docker/basic/docker-compose.yml down
```

## Configuration

The basic environment uses the following configuration:

- Mock email data is used instead of connecting to real email servers
- Python 3.9 runtime environment
- Mounts the entire Taskinity project directory

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
4. Send responses
