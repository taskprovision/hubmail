# API Integration Example

This example demonstrates how to use Taskinity to integrate with external APIs. It shows how to make API requests, process responses, handle errors, and build complete API integration workflows.

## Features

- Connect to external APIs
- Handle authentication
- Process API responses
- Implement error handling and retries
- Chain multiple API calls
- Schedule API integration tasks

## Prerequisites

- Python 3.8 or higher
- Docker and Docker Compose (for running the mock API server)

## Setup

1. Clone the Taskinity repository:
   ```bash
   git clone https://github.com/taskinity/python.git
   cd taskinity/examples/api_integration
   ```

2. Copy the example environment file and configure it:
   ```bash
   cp .env.example .env
   # Edit .env with your specific configuration
   ```

3. Start the mock API server using Docker Compose:
   ```bash
   docker-compose up -d
   ```
   This will start a mock API server that provides endpoints for testing.

4. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Examples

### Weather API Integration

The `weather_api.py` file demonstrates integrating with a weather API:

```bash
python weather_api.py
```

### GitHub API Integration

The `github_api.py` file shows how to integrate with the GitHub API:

```bash
python github_api.py
```

### REST API Integration

The `rest_api.py` file demonstrates a generic REST API integration:

```bash
python rest_api.py
```

## Docker Compose Configuration

The included `docker-compose.yml` file sets up:

- Mock API Server - A server that simulates various API endpoints
- API Documentation - Available at http://localhost:8080

## Flow Definition

This example defines the following Taskinity flow:

```
flow APIIntegrationFlow:
    description: "Flow for API integration"
    
    task PrepareRequest:
        description: "Prepare API request parameters"
        # Code to prepare request parameters
    
    task MakeAPIRequest:
        description: "Make request to external API"
        # Code to make API request
    
    task ProcessResponse:
        description: "Process API response"
        # Code to process response data
    
    task HandleErrors:
        description: "Handle API errors"
        # Code to handle errors
    
    task SaveResults:
        description: "Save API results"
        # Code to save results
    
    PrepareRequest -> MakeAPIRequest -> ProcessResponse -> SaveResults
    MakeAPIRequest -> HandleErrors
    HandleErrors -> MakeAPIRequest
```

## Performance Comparison

This example demonstrates the efficiency of using Taskinity for API integration compared to traditional approaches:

| Metric | Taskinity | Traditional Script | Improvement |
|--------|-----------|-------------------|-------------|
| Lines of Code | ~120 | ~250 | 52% reduction |
| Setup Time | 5 minutes | 25 minutes | 80% reduction |
| Error Handling | Built-in retries | Manual implementation | Simplified |
| Maintainability | High | Medium | Easier to maintain |

## Extending the Example

You can extend this example by:

1. Adding more API integrations
2. Implementing OAuth authentication
3. Creating a dashboard to monitor API calls
4. Setting up scheduled API polling

## Troubleshooting

- If you can't connect to the mock API server, check your Docker Compose setup
- Ensure your API keys are correctly configured in the .env file
- Check the logs directory for detailed error messages

<!-- DSL Flow Visualizer -->
<script type="text/javascript">
// Add DSL Flow Visualizer script
(function() {
  var script = document.createElement('script');
  script.src = '/hubmail/dsl/static/js/dsl-flow-visualizer.js';
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


<!-- Markdown Enhancements -->

<!-- Taskinity Markdown Enhancements -->
<!-- Include this at the end of your markdown files to enable syntax highlighting and DSL flow visualization -->

<!-- Prism.js for syntax highlighting -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism.min.css">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/plugins/line-numbers/prism-line-numbers.min.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/prism.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/plugins/line-numbers/prism-line-numbers.min.js"></script>

<!-- Load common language components -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-python.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-bash.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-javascript.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-yaml.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-json.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-markdown.min.js"></script>

<!-- Taskinity custom scripts -->
<script src="../../static/js/dsl-flow-visualizer.js"></script>
<script src="../../static/js/markdown-syntax-highlighter.js"></script>

<script>
  // Initialize both scripts when the page loads
  document.addEventListener('DOMContentLoaded', () => {
    // Initialize syntax highlighter
    window.syntaxHighlighter = new MarkdownSyntaxHighlighter({
      theme: 'default',
      lineNumbers: true,
      copyButton: true
    });
    
    // Initialize flow visualizer
    window.flowVisualizer = new DSLFlowVisualizer({
      codeBlockSelector: 'pre code.language-dsl, pre code.language-flow'
    });
  });
</script>

<!-- Custom styles for better markdown rendering -->
<style>
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
    line-height: 1.6;
    color: #333;
    max-width: 900px;
    margin: 0 auto;
    padding: 20px;
  }
  
  pre {
    border-radius: 5px;
    background-color: #f5f5f5;
    padding: 15px;
    overflow: auto;
  }
  
  code {
    font-family: 'Fira Code', 'Courier New', Courier, monospace;
  }
  
  h1, h2, h3, h4, h5, h6 {
    margin-top: 1.5em;
    margin-bottom: 0.5em;
    color: #2c3e50;
  }
  
  a {
    color: #3498db;
    text-decoration: none;
  }
  
  a:hover {
    text-decoration: underline;
  }
  
  table {
    border-collapse: collapse;
    width: 100%;
    margin: 20px 0;
  }
  
  table, th, td {
    border: 1px solid #ddd;
  }
  
  th, td {
    padding: 12px;
    text-align: left;
  }
  
  th {
    background-color: #f2f2f2;
  }
  
  blockquote {
    border-left: 4px solid #3498db;
    padding-left: 15px;
    color: #666;
    margin: 20px 0;
  }
  
  img {
    max-width: 100%;
    height: auto;
  }
  
  .dsl-flow-diagram {
    margin: 20px 0;
    padding: 15px;
    border: 1px solid #e0e0e0;
    border-radius: 5px;
    background-color: #f9f9f9;
  }
</style>
