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

<!-- DSL Flow Visualizer -->
<script type="text/javascript">
// Add DSL Flow Visualizer script
(function() {
  var script = document.createElement('script');
  script.src = '/static/js/dsl-flow-visualizer.js';
  script.async = true;
  script.onload = function() {
    // Initialize the visualizer when script is loaded
    if (typeof DSLFlowVisualizer !== 'undefined') {
      new DSLFlowVisualizer();
    }
  };
  document.head.appendChild(script);
  
  // Add CSS styles
  var style = document.createElement('style');
  style.textContent = `
    .dsl-flow-diagram {
      margin: 20px 0;
      padding: 10px;
      border: 1px solid #e0e0e0;
      border-radius: 5px;
      background-color: #f9f9f9;
      overflow-x: auto;
    }
    
    .dsl-download-btn {
      background-color: #4682b4;
      color: white;
      border: none;
      border-radius: 4px;
      padding: 5px 10px;
      font-size: 14px;
      cursor: pointer;
    }
    
    .dsl-download-btn:hover {
      background-color: #36648b;
    }
  `;
  document.head.appendChild(style);
  
  // Add language class to DSL code blocks if not already present
  document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('pre code').forEach(function(codeBlock) {
      var content = codeBlock.textContent.trim();
      if (content.startsWith('flow ') && !codeBlock.classList.contains('language-dsl')) {
        codeBlock.classList.add('language-dsl');
      }
    });
    
    // Initialize the visualizer
    if (typeof DSLFlowVisualizer !== 'undefined') {
      new DSLFlowVisualizer();
    }
  });
})();
</script>
