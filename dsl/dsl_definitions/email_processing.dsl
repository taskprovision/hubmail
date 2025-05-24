
flow EmailProcessing:
    description: "Przetwarzanie e-maili z różnymi kategoriami"
    fetch_emails -> classify_emails
    classify_emails -> process_urgent_emails
    classify_emails -> process_emails_with_attachments
    classify_emails -> process_regular_emails
    process_urgent_emails -> send_responses
    process_emails_with_attachments -> send_responses
    process_regular_emails -> send_responses
