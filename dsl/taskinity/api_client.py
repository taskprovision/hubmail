"""
API Client for Taskinity.

This module provides classes for interacting with external APIs,
including REST, GraphQL, and WebSocket APIs.
"""
import json
import logging
import time
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union, Callable

# Check if optional dependencies are installed
try:
    import requests
    from requests.adapters import HTTPAdapter
    from requests.packages.urllib3.util.retry import Retry
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    import websocket
    WEBSOCKET_AVAILABLE = True
except ImportError:
    WEBSOCKET_AVAILABLE = False

try:
    import gql
    from gql import Client
    from gql.transport.requests import RequestsHTTPTransport
    GQL_AVAILABLE = True
except ImportError:
    GQL_AVAILABLE = False


class APIClient(ABC):
    """Base class for API clients."""
    
    def __init__(self, base_url: str, logger: Optional[logging.Logger] = None):
        """
        Initialize the API client.
        
        Args:
            base_url: Base URL for the API
            logger: Logger instance (optional)
        """
        self.base_url = base_url
        self.logger = logger or logging.getLogger(__name__)
    
    @abstractmethod
    def request(self, endpoint: str, method: str = "GET", **kwargs) -> Any:
        """
        Make a request to the API.
        
        Args:
            endpoint: API endpoint
            method: HTTP method
            **kwargs: Additional arguments
            
        Returns:
            API response
        """
        pass


class RESTClient(APIClient):
    """Client for REST APIs."""
    
    def __init__(
        self,
        base_url: str,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 30,
        max_retries: int = 3,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize the REST client.
        
        Args:
            base_url: Base URL for the API
            headers: Default headers to include in requests
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
            logger: Logger instance (optional)
        """
        super().__init__(base_url, logger)
        
        if not REQUESTS_AVAILABLE:
            raise ImportError("Requests is required for REST API client. "
                             "Install with: pip install requests")
        
        self.headers = headers or {}
        self.timeout = timeout
        self.session = self._create_session(max_retries)
    
    def _create_session(self, max_retries: int) -> requests.Session:
        """
        Create a requests session with retry configuration.
        
        Args:
            max_retries: Maximum number of retries
            
        Returns:
            Configured requests session
        """
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            method_whitelist=["GET", "POST", "PUT", "DELETE", "PATCH"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def request(
        self,
        endpoint: str,
        method: str = "GET",
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Any] = None,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        **kwargs
    ) -> Any:
        """
        Make a request to the REST API.
        
        Args:
            endpoint: API endpoint
            method: HTTP method
            params: Query parameters
            data: Request body as form data
            json_data: Request body as JSON
            headers: Request headers
            timeout: Request timeout in seconds
            **kwargs: Additional arguments for requests.request
            
        Returns:
            API response
        """
        # Build URL
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        # Merge headers
        merged_headers = {**self.headers}
        if headers:
            merged_headers.update(headers)
        
        # Set timeout
        request_timeout = timeout or self.timeout
        
        # Log request
        self.logger.info(f"Making {method} request to {url}")
        
        try:
            # Make request
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                data=data,
                json=json_data,
                headers=merged_headers,
                timeout=request_timeout,
                **kwargs
            )
            
            # Raise exception for error status codes
            response.raise_for_status()
            
            # Parse response
            if response.headers.get("content-type", "").startswith("application/json"):
                return response.json()
            else:
                return response.text
        
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request failed: {str(e)}")
            raise
    
    def get(self, endpoint: str, **kwargs) -> Any:
        """
        Make a GET request.
        
        Args:
            endpoint: API endpoint
            **kwargs: Additional arguments for request
            
        Returns:
            API response
        """
        return self.request(endpoint, method="GET", **kwargs)
    
    def post(self, endpoint: str, **kwargs) -> Any:
        """
        Make a POST request.
        
        Args:
            endpoint: API endpoint
            **kwargs: Additional arguments for request
            
        Returns:
            API response
        """
        return self.request(endpoint, method="POST", **kwargs)
    
    def put(self, endpoint: str, **kwargs) -> Any:
        """
        Make a PUT request.
        
        Args:
            endpoint: API endpoint
            **kwargs: Additional arguments for request
            
        Returns:
            API response
        """
        return self.request(endpoint, method="PUT", **kwargs)
    
    def delete(self, endpoint: str, **kwargs) -> Any:
        """
        Make a DELETE request.
        
        Args:
            endpoint: API endpoint
            **kwargs: Additional arguments for request
            
        Returns:
            API response
        """
        return self.request(endpoint, method="DELETE", **kwargs)
    
    def patch(self, endpoint: str, **kwargs) -> Any:
        """
        Make a PATCH request.
        
        Args:
            endpoint: API endpoint
            **kwargs: Additional arguments for request
            
        Returns:
            API response
        """
        return self.request(endpoint, method="PATCH", **kwargs)


class GraphQLClient(APIClient):
    """Client for GraphQL APIs."""
    
    def __init__(
        self,
        base_url: str,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 30,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize the GraphQL client.
        
        Args:
            base_url: Base URL for the GraphQL API
            headers: Default headers to include in requests
            timeout: Request timeout in seconds
            logger: Logger instance (optional)
        """
        super().__init__(base_url, logger)
        
        if not GQL_AVAILABLE:
            raise ImportError("GQL is required for GraphQL API client. "
                             "Install with: pip install gql[requests]")
        
        self.headers = headers or {}
        self.timeout = timeout
        self.client = self._create_client()
    
    def _create_client(self) -> gql.Client:
        """
        Create a GQL client.
        
        Returns:
            Configured GQL client
        """
        transport = RequestsHTTPTransport(
            url=self.base_url,
            headers=self.headers,
            timeout=self.timeout,
            use_json=True
        )
        
        return Client(transport=transport, fetch_schema_from_transport=True)
    
    def request(
        self,
        query: str,
        variables: Optional[Dict[str, Any]] = None,
        operation_name: Optional[str] = None,
        **kwargs
    ) -> Any:
        """
        Make a request to the GraphQL API.
        
        Args:
            query: GraphQL query or mutation
            variables: Query variables
            operation_name: Operation name
            **kwargs: Additional arguments
            
        Returns:
            API response
        """
        self.logger.info(f"Making GraphQL request to {self.base_url}")
        
        try:
            # Create GQL document
            document = gql.gql(query)
            
            # Execute query
            result = self.client.execute(
                document,
                variable_values=variables,
                operation_name=operation_name
            )
            
            return result
        
        except Exception as e:
            self.logger.error(f"GraphQL request failed: {str(e)}")
            raise
    
    def query(
        self,
        query: str,
        variables: Optional[Dict[str, Any]] = None,
        operation_name: Optional[str] = None
    ) -> Any:
        """
        Execute a GraphQL query.
        
        Args:
            query: GraphQL query
            variables: Query variables
            operation_name: Operation name
            
        Returns:
            Query result
        """
        return self.request(query, variables, operation_name)
    
    def mutate(
        self,
        mutation: str,
        variables: Optional[Dict[str, Any]] = None,
        operation_name: Optional[str] = None
    ) -> Any:
        """
        Execute a GraphQL mutation.
        
        Args:
            mutation: GraphQL mutation
            variables: Mutation variables
            operation_name: Operation name
            
        Returns:
            Mutation result
        """
        return self.request(mutation, variables, operation_name)


class WebSocketClient(APIClient):
    """Client for WebSocket APIs."""
    
    def __init__(
        self,
        base_url: str,
        headers: Optional[Dict[str, str]] = None,
        on_message: Optional[Callable[[str], None]] = None,
        on_error: Optional[Callable[[Exception], None]] = None,
        on_close: Optional[Callable[[], None]] = None,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize the WebSocket client.
        
        Args:
            base_url: WebSocket URL
            headers: Headers for the WebSocket connection
            on_message: Callback for received messages
            on_error: Callback for errors
            on_close: Callback for connection close
            logger: Logger instance (optional)
        """
        super().__init__(base_url, logger)
        
        if not WEBSOCKET_AVAILABLE:
            raise ImportError("websocket-client is required for WebSocket API client. "
                             "Install with: pip install websocket-client")
        
        self.headers = headers or {}
        self.on_message = on_message
        self.on_error = on_error
        self.on_close = on_close
        self.ws = None
    
    def connect(self) -> None:
        """Connect to the WebSocket."""
        self.logger.info(f"Connecting to WebSocket at {self.base_url}")
        
        try:
            # Create WebSocket connection
            self.ws = websocket.WebSocketApp(
                self.base_url,
                header=self._format_headers(),
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close
            )
            
            # Start WebSocket connection in a separate thread
            import threading
            thread = threading.Thread(target=self.ws.run_forever)
            thread.daemon = True
            thread.start()
            
            # Wait for connection to establish
            time.sleep(1)
            
            self.logger.info("WebSocket connection established")
        
        except Exception as e:
            self.logger.error(f"WebSocket connection failed: {str(e)}")
            raise
    
    def disconnect(self) -> None:
        """Disconnect from the WebSocket."""
        if self.ws:
            self.logger.info("Disconnecting from WebSocket")
            self.ws.close()
            self.ws = None
    
    def send(self, data: Union[str, Dict[str, Any]]) -> None:
        """
        Send data through the WebSocket.
        
        Args:
            data: Data to send (string or dictionary to be JSON-encoded)
        """
        if not self.ws:
            raise RuntimeError("WebSocket not connected")
        
        # Convert dictionary to JSON string
        if isinstance(data, dict):
            data = json.dumps(data)
        
        self.logger.info("Sending data through WebSocket")
        self.ws.send(data)
    
    def request(self, endpoint: str, method: str = "GET", **kwargs) -> Any:
        """
        Make a request to the WebSocket API.
        
        Note: This method is not typically used for WebSockets, but is implemented
        to conform to the APIClient interface. It sends a message and does not
        wait for a response.
        
        Args:
            endpoint: Not used for WebSockets
            method: Not used for WebSockets
            **kwargs: Additional arguments
            
        Returns:
            None
        """
        if "data" in kwargs:
            self.send(kwargs["data"])
        elif "json_data" in kwargs:
            self.send(kwargs["json_data"])
        else:
            self.send({"endpoint": endpoint, "method": method, **kwargs})
    
    def _format_headers(self) -> List[str]:
        """
        Format headers for WebSocket connection.
        
        Returns:
            List of header strings in the format "key: value"
        """
        return [f"{key}: {value}" for key, value in self.headers.items()]
    
    def _on_message(self, ws, message: str) -> None:
        """
        Handle received WebSocket messages.
        
        Args:
            ws: WebSocket instance
            message: Received message
        """
        self.logger.debug(f"Received WebSocket message: {message}")
        
        if self.on_message:
            self.on_message(message)
    
    def _on_error(self, ws, error: Exception) -> None:
        """
        Handle WebSocket errors.
        
        Args:
            ws: WebSocket instance
            error: Error
        """
        self.logger.error(f"WebSocket error: {str(error)}")
        
        if self.on_error:
            self.on_error(error)
    
    def _on_close(self, ws, close_status_code, close_msg) -> None:
        """
        Handle WebSocket connection close.
        
        Args:
            ws: WebSocket instance
            close_status_code: Close status code
            close_msg: Close message
        """
        self.logger.info(f"WebSocket connection closed: {close_status_code} {close_msg}")
        
        if self.on_close:
            self.on_close()
