# API Integration Usage Guide

This example demonstrates how to integrate Taskinity with external APIs, including how to set up a mock API for testing.

## Setup

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

2. Set up environment variables by copying the example file:

```bash
cp .env.example .env
```

3. Edit the `.env` file to configure your API endpoints and credentials.

## Running the Mock API Server

For testing purposes, this example includes a mock API server:

```bash
# Start the mock API server
cd mock-api
npm install
npm start
```

The mock API server will be available at `http://localhost:3000`.

## Basic API Integration

### Understanding the Example

The example demonstrates:
- How to make API requests within Taskinity tasks
- How to handle API authentication
- How to process API responses
- How to handle errors and retries

### Running the Example

To run the basic API integration example:

```bash
python api_client.py
```

This will execute a flow that fetches data from the API, processes it, and displays the results.

## Docker Integration

This example also includes Docker configuration for easy deployment:

```bash
# Start the services using Docker Compose
docker-compose up -d
```

This will start:
- The mock API server
- A Redis instance for caching API responses
- A PostgreSQL database for storing processed data

## Advanced API Features

### Authentication

The example demonstrates different authentication methods:

```python
# API Key Authentication
headers = {"X-API-Key": os.getenv("API_KEY")}
response = requests.get(url, headers=headers)

# OAuth Authentication
auth_response = requests.post(
    os.getenv("AUTH_URL"),
    json={"client_id": os.getenv("CLIENT_ID"), "client_secret": os.getenv("CLIENT_SECRET")}
)
token = auth_response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(url, headers=headers)
```

### Rate Limiting and Retries

The example includes rate limiting and retry logic:

```python
@task(name="Fetch API Data with Retries")
def fetch_api_data_with_retries(url, max_retries=3, backoff_factor=1.5):
    """Fetch data from API with exponential backoff retry logic."""
    retry_count = 0
    while retry_count < max_retries:
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            retry_count += 1
            if retry_count >= max_retries:
                raise
            sleep_time = backoff_factor ** retry_count
            time.sleep(sleep_time)
```

### Caching

The example demonstrates how to cache API responses:

```python
@task(name="Fetch API Data with Cache")
def fetch_api_data_with_cache(url, cache_key, cache_ttl=3600):
    """Fetch data from API with caching."""
    # Check if data is in cache
    cached_data = redis_client.get(cache_key)
    if cached_data:
        return json.loads(cached_data)
    
    # Fetch from API if not in cache
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()
    
    # Store in cache
    redis_client.setex(cache_key, cache_ttl, json.dumps(data))
    return data
```

## Creating Your Own API Integration

1. Define your API client tasks:

```python
from taskinity import task

@task(name="Fetch User Data")
def fetch_user_data(user_id):
    url = f"{BASE_API_URL}/users/{user_id}"
    response = requests.get(url, headers=get_auth_headers())
    response.raise_for_status()
    return response.json()
```

2. Create a flow DSL that uses your API tasks:

```python
API_FLOW_DSL = """
flow UserDataProcessing:
    description: "Process user data from API"
    fetch_user_list -> process_users
    process_users -> generate_report
"""
```

3. Run the flow with appropriate input data:

```python
from taskinity import run_flow_from_dsl

input_data = {"api_key": "your_api_key", "user_count": 10}
result = run_flow_from_dsl(API_FLOW_DSL, input_data)
```

## Best Practices

1. **Environment Variables**: Store API credentials in environment variables, never hardcode them.

2. **Error Handling**: Implement proper error handling for API requests.

3. **Rate Limiting**: Respect API rate limits to avoid being blocked.

4. **Caching**: Cache API responses to reduce the number of requests.

5. **Pagination**: Handle API pagination for large datasets.

6. **Logging**: Log API requests and responses for debugging.

7. **Timeouts**: Set appropriate timeouts for API requests.

8. **Retries**: Implement retry logic with exponential backoff.

9. **Testing**: Use mock APIs for testing to avoid hitting production APIs.

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
