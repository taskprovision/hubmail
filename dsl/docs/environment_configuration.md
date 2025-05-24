# Environment Configuration for Taskinity

This document provides guidelines for configuring environment variables across Taskinity examples and projects.

## Overview

Taskinity uses environment variables for configuration to:
- Keep sensitive information out of source code
- Allow for different configurations in development, testing, and production
- Make examples easily configurable without code changes

## Standard Environment Variables

The following environment variables are standardized across all Taskinity examples:

### Logging Configuration
| Variable | Description | Default Value |
|----------|-------------|---------------|
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) | INFO |
| `LOG_DIR` | Directory for log files | ./logs |
| `LOG_FORMAT` | Format for log messages | %(asctime)s - %(name)s - %(levelname)s - %(message)s |

### Output Configuration
| Variable | Description | Default Value |
|----------|-------------|---------------|
| `OUTPUT_DIR` | Directory for output files | ./output |
| `REPORT_FORMAT` | Format for reports (csv, json, txt) | json |

### Database Configuration
| Variable | Description | Default Value |
|----------|-------------|---------------|
| `DB_TYPE` | Database type (sqlite, postgresql, mysql) | sqlite |
| `DB_HOST` | Database host | localhost |
| `DB_PORT` | Database port | Depends on DB_TYPE |
| `DB_NAME` | Database name | taskinity |
| `DB_USER` | Database username | taskinity |
| `DB_PASSWORD` | Database password | taskinity |
| `DB_POOL_SIZE` | Connection pool size | 5 |

### API Configuration
| Variable | Description | Default Value |
|----------|-------------|---------------|
| `API_TIMEOUT` | Timeout for API requests in seconds | 30 |
| `API_RETRIES` | Number of retries for failed API requests | 3 |
| `API_BACKOFF_FACTOR` | Backoff factor for retries | 0.5 |

## Example-Specific Environment Variables

Each example may define additional environment variables specific to its functionality. These should be clearly documented in the example's README.md and .env.example files.

## Using Environment Variables

### In Python Code

Taskinity provides a utility function for loading environment variables:

```python
from taskinity.utils import load_env

# Load environment variables from .env file
env = load_env()

# Access environment variables with defaults
log_level = env.get("LOG_LEVEL", "INFO")
db_host = env.get("DB_HOST", "localhost")

# Access required environment variables (raises exception if not set)
api_key = env.get_required("API_KEY")
```

### Manual Configuration

1. Copy the `.env.example` file to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file with your specific configuration.

3. The `.env` file should never be committed to version control.

## Docker Environment Variables

When using Docker, environment variables can be passed in multiple ways:

1. Using environment variables in the docker-compose.yml file:
   ```yaml
   services:
     app:
       image: taskinity/example
       environment:
         - LOG_LEVEL=INFO
         - DB_HOST=postgres
   ```

2. Using an env_file in docker-compose.yml:
   ```yaml
   services:
     app:
       image: taskinity/example
       env_file:
         - ./.env
   ```

3. Using the `-e` flag with docker run:
   ```bash
   docker run -e LOG_LEVEL=DEBUG -e DB_HOST=postgres taskinity/example
   ```

## Best Practices

1. Always provide sensible defaults for non-sensitive configuration.
2. Never hardcode sensitive information (passwords, API keys) in code.
3. Include clear documentation for all environment variables.
4. Use descriptive names for environment variables.
5. Group related environment variables together in .env.example files.
6. Validate environment variables at application startup.
7. Use different .env files for different environments (.env.development, .env.test, .env.production).

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
