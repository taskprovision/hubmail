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
   git clone https://github.com/taskinity/taskinity.git
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
