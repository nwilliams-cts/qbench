"""Main API client for QBench SDK."""

import requests
import aiohttp
import asyncio
import logging
import time
from typing import Optional, Dict, Any, Union, List
from tenacity import retry, wait_exponential, stop_after_attempt, RetryError, retry_if_exception_type

from .auth import QBenchAuth
from .exceptions import (
    QBenchAPIError, 
    QBenchConnectionError, 
    QBenchValidationError,
    QBenchTimeoutError
)
from .endpoints import QBENCH_ENDPOINTS

# Set up logging
logger = logging.getLogger(__name__)


class QBenchAPI:
    """
    QBench API client with async support and automatic pagination.
    
    This class provides a unified interface to interact with QBench LIMS API,
    supporting both v1 and v2 endpoints with automatic method generation.
    """
    
    def __init__(
        self, 
        base_url: str, 
        api_key: str, 
        api_secret: str, 
        concurrency_limit: int = 10,
        timeout: int = 30
    ):
        """
        Initialize the QBenchAPI instance with authentication and base URLs.

        Args:
            base_url (str): The base URL of the QBench API.
            api_key (str): API key for authentication.
            api_secret (str): API secret for authentication.
            concurrency_limit (int): Maximum number of concurrent requests.
            timeout (int): Request timeout in seconds.
            
        Raises:
            QBenchAuthError: If authentication fails
        """
        self._auth = QBenchAuth(base_url, api_key, api_secret)
        self._base_url = f"{base_url.rstrip('/')}/qbench/api/v2"
        self._base_url_v1 = f"{base_url.rstrip('/')}/qbench/api/v1"
        self._concurrency_limit = concurrency_limit
        self._timeout = timeout
        
        # Create reusable session with connection pooling
        self._session = requests.Session()
        self._session.headers.update(self._auth.get_headers())
        
        # Configure session for better performance
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=10,
            pool_maxsize=20,
            max_retries=0  # We handle retries with tenacity
        )
        self._session.mount("http://", adapter)
        self._session.mount("https://", adapter)
        
        logger.info(f"QBench API client initialized for {base_url}")

    def __del__(self):
        """Clean up session on deletion."""
        if hasattr(self, '_session'):
            self._session.close()


    @retry(
        wait=wait_exponential(multiplier=2, min=1, max=10), 
        stop=stop_after_attempt(5),
        retry=retry_if_exception_type((requests.exceptions.ConnectionError, requests.exceptions.Timeout)),
        reraise=True
    )
    def _make_request(
        self, 
        method: str, 
        endpoint_key: str, 
        use_v1: bool = False,
        params: Optional[Dict[str, Any]] = None, 
        data: Optional[Dict[str, Any]] = None,
        path_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make a synchronous request to the QBench API with retry logic.

        Args:
            method (str): HTTP method ('GET', 'POST', etc.).
            endpoint_key (str): API endpoint key from QBENCH_ENDPOINTS.
            use_v1 (bool): If True, use the v1 API. Else use v2.
            params (dict, optional): URL parameters for the request.
            data (dict, optional): JSON payload for the request.
            path_params (dict, optional): Parameters to replace in the endpoint

        Returns:
            dict: JSON response from the API.
            
        Raises:
            QBenchValidationError: For invalid endpoint or parameters
            QBenchAPIError: For API-related errors
            QBenchConnectionError: For connection issues
        """
        if endpoint_key not in QBENCH_ENDPOINTS:
            raise QBenchValidationError(f"Invalid API endpoint: {endpoint_key}")
        
        # Default to v2 unless explicitly set
        version = "v1" if use_v1 else "v2"
        base_url = self._base_url_v1 if use_v1 else self._base_url

        # Get the correct endpoint format
        endpoint = QBENCH_ENDPOINTS[endpoint_key].get(version)
        if not endpoint:
            raise QBenchValidationError(
                f"Endpoint '{endpoint_key}' does not exist in version {version}"
            )

        # Format endpoint with path parameters if provided
        if path_params:
            try:
                endpoint = endpoint.format(**path_params)
            except KeyError as e:
                raise QBenchValidationError(
                    f"Missing required path parameter: {e}"
                )

        url = f"{base_url}/{endpoint}"
        
        # Refresh auth headers if needed
        self._session.headers.update(self._auth.get_headers())

        try:
            logger.debug(f"Making {method} request to {url}")
            response = self._session.request(
                method, 
                url, 
                params=params, 
                json=data,
                timeout=self._timeout
            )
            response.raise_for_status()
            
            # Handle empty responses
            if response.status_code == 204:  # No Content
                return {}
                
            try:
                return response.json()
            except ValueError:
                # Response is not JSON
                return {"status": "success", "data": response.text}
                
        except requests.exceptions.Timeout:
            raise QBenchTimeoutError(f"Request timeout after {self._timeout} seconds")
        except requests.exceptions.ConnectionError as e:
            raise QBenchConnectionError(f"Connection error: {e}")
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code if e.response else None
            try:
                error_data = e.response.json() if e.response else None
            except ValueError:
                error_data = None
                
            if status_code == 401:
                # Try to refresh token and retry once
                try:
                    self._auth._fetch_access_token()
                    self._session.headers.update(self._auth.get_headers())
                    raise  # Will be caught by retry decorator
                except Exception:
                    raise QBenchAPIError("Authentication failed", status_code, error_data)
            elif status_code == 404:
                raise QBenchAPIError("Resource not found", status_code, error_data)
            elif status_code == 429:
                raise QBenchAPIError("Rate limit exceeded", status_code, error_data)
            else:
                raise QBenchAPIError(
                    f"API request failed: {method.upper()} {url} - {e}",
                    status_code, 
                    error_data
                )
        except requests.exceptions.RequestException as e:
            raise QBenchAPIError(f"Request failed: {e}")
        except RetryError as e:
            # All retries exhausted
            raise QBenchAPIError(f"Request failed after all retries: {e.last_attempt.exception()}")

    async def _fetch_page(
        self, 
        session: aiohttp.ClientSession, 
        url: str, 
        page: int, 
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Fetch a single page of paginated data.
        
        Args:
            session: aiohttp session
            url: Base URL for the request
            page: Page number to fetch
            params: Additional URL parameters
            
        Returns:
            Dict containing the page data
        """
        page_params = params.copy()
        page_params.update({
            'page_num': page,
            'page_size': 50
        })
        
        try:
            async with session.get(url, params=page_params, timeout=self._timeout) as response:
                response.raise_for_status()
                data = await response.json()
                return data or {'data': []}
        except asyncio.TimeoutError:
            raise QBenchTimeoutError(f"Page {page} request timed out")
        except aiohttp.ClientError as e:
            raise QBenchConnectionError(f"Error fetching page {page}: {e}")

    async def _get_entity_list(
        self, 
        endpoint_key: str, 
        use_v1: bool = False, 
        page_limit: Optional[int] = None, 
        path_params: Optional[Dict[str, Any]] = None, 
        include_metadata: bool = False,
        **kwargs
    ) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Get a paginated list of entities with concurrent page fetching.
        
        Args:
            endpoint_key: The endpoint key from QBENCH_ENDPOINTS
            use_v1: Whether to use v1 API
            page_limit: Maximum number of pages to fetch (None for all)
            path_params: Parameters for URL formatting
            include_metadata: Whether to include full response metadata
            **kwargs: Additional query parameters
            
        Returns:
            List of entities (if include_metadata=False) or Dict with full metadata
        """
        if path_params is None:
            path_params = {}
            
        version = "v1" if use_v1 else "v2"
        base_url = self._base_url_v1 if use_v1 else self._base_url

        endpoint = QBENCH_ENDPOINTS[endpoint_key][version]
        if path_params:
            endpoint = endpoint.format(**path_params)

        url = f"{base_url}/{endpoint}"
        entity_array = []
        
        # Set up aiohttp session with proper headers and concurrency control
        connector = aiohttp.TCPConnector(limit=self._concurrency_limit)
        timeout = aiohttp.ClientTimeout(total=self._timeout)
        
        async with aiohttp.ClientSession(
            headers=self._auth.get_headers(),
            connector=connector,
            timeout=timeout
        ) as session:
            try:
                # Fetch first page to determine total pages
                page_1_res = await self._fetch_page(session, url, 1, kwargs)
                page_1_data = page_1_res.get('data', [])

                # Determine how many pages to fetch
                total_pages = page_1_res.get('total_pages', 1)
                pages_to_fetch = min(page_limit or total_pages, total_pages)
                
                entity_array.extend(page_1_data)
                logger.debug(f"Fetching {pages_to_fetch} pages for {endpoint_key}")

                # Fetch remaining pages concurrently if needed
                if pages_to_fetch > 1:
                    # Create semaphore to limit concurrent requests
                    semaphore = asyncio.Semaphore(self._concurrency_limit)
                    
                    async def fetch_with_semaphore(page_num):
                        async with semaphore:
                            return await self._fetch_page(session, url, page_num, kwargs)
                    
                    tasks = [
                        fetch_with_semaphore(page) 
                        for page in range(2, pages_to_fetch + 1)
                    ]
                    
                    results = await asyncio.gather(*tasks, return_exceptions=True)

                    for i, result in enumerate(results):
                        if isinstance(result, Exception):
                            logger.error(f"Error fetching page {i+2}: {result}")
                            continue
                        entity_array.extend(result.get('data', []))

            except Exception as e:
                logger.error(f"Error in _get_entity_list for {endpoint_key}: {e}")
                raise

        logger.debug(f"Retrieved {len(entity_array)} entities for {endpoint_key}")
        
        # Return response based on include_metadata flag
        full_response = {'data': entity_array}
        if include_metadata:
            # Include metadata from the first page response
            if page_1_res:
                full_response.update({
                    k: v for k, v in page_1_res.items() 
                    if k != 'data'
                })
            return full_response
        else:
            # Return just the entity array
            return entity_array

    def __getattr__(self, name: str):
        """
        Dynamic method generation for QBench API endpoints.
        
        This method intercepts attribute access and creates dynamic methods
        for all endpoints defined in QBENCH_ENDPOINTS. Each method supports
        both synchronous and asynchronous execution depending on context.
        
        Args:
            name: The method name being accessed
            
        Returns:
            A callable method that handles the API request
            
        Raises:
            AttributeError: If the method name is not a valid endpoint
        """
        if name not in QBENCH_ENDPOINTS:
            raise AttributeError(
                f"'{self.__class__.__name__}' object has no attribute '{name}'. "
                f"Available endpoints: {', '.join(sorted(QBENCH_ENDPOINTS.keys()))}"
            )
        
        endpoint_config = QBENCH_ENDPOINTS[name]
        
        async def async_dynamic_method(
            entity_id: Optional[int] = None, 
            use_v1: bool = False, 
            page_limit: Optional[int] = None, 
            data: Optional[Dict[str, Any]] = None, 
            include_metadata: bool = False,
            **kwargs
        ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
            """
            Async implementation of the dynamic method.
            
            Args:
                entity_id: ID for single entity endpoints
                use_v1: Whether to use v1 API
                page_limit: Max pages for paginated endpoints
                data: Request body for POST/PATCH/PUT requests
                include_metadata: Whether to include API metadata (default: False)
                **kwargs: Additional query parameters
                
            Returns:
                API response data (just the data by default, full response if include_metadata=True)
            """
            path_params = {"id": entity_id} if entity_id else {}
            method = endpoint_config.get('method', 'GET')

            if endpoint_config.get('paginated'):
                result = await self._get_entity_list(
                    name, 
                    use_v1=use_v1, 
                    page_limit=page_limit, 
                    path_params=path_params, 
                    include_metadata=include_metadata,
                    **kwargs
                )
            else:
                # Run synchronous method in thread pool for non-paginated endpoints
                loop = asyncio.get_running_loop()
                result = await loop.run_in_executor(
                    None, 
                    self._make_request, 
                    method, 
                    name, 
                    use_v1, 
                    kwargs, 
                    data, 
                    path_params
                )
                
                # Extract data if not including metadata
                if not include_metadata and isinstance(result, dict) and 'data' in result:
                    result = result['data']
                    
            return result

        def dynamic_method(
            entity_id: Optional[int] = None, 
            use_v1: bool = False, 
            data: Optional[Dict[str, Any]] = None, 
            page_limit: Optional[int] = None, 
            include_metadata: bool = False,
            **kwargs
        ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
            """
            Synchronous wrapper that handles async/sync context detection.
            
            Args:
                entity_id: ID for single entity endpoints
                use_v1: Whether to use v1 API  
                data: Request body for POST/PATCH/PUT requests
                page_limit: Max pages for paginated endpoints
                include_metadata: Whether to include API metadata (default: False)
                **kwargs: Additional query parameters
                
            Returns:
                API response data (just the data by default, full response if include_metadata=True)
            """
            try:
                # Check if we're in an async context
                loop = asyncio.get_running_loop()
                # If there's an active event loop, return coroutine for awaiting
                return async_dynamic_method(
                    entity_id=entity_id, 
                    use_v1=use_v1, 
                    page_limit=page_limit, 
                    data=data, 
                    include_metadata=include_metadata,
                    **kwargs
                )
            except RuntimeError:
                # No active event loop; safe to call asyncio.run()
                return asyncio.run(
                    async_dynamic_method(
                        entity_id=entity_id, 
                        use_v1=use_v1, 
                        page_limit=page_limit, 
                        data=data, 
                        include_metadata=include_metadata,
                        **kwargs
                    )
                )
            
        # Add docstring with endpoint information
        method_doc = f"""
        {endpoint_config.get('method', 'GET')} {name}
        
        QBench API endpoint: {name}
        Method: {endpoint_config.get('method', 'GET')}
        Paginated: {endpoint_config.get('paginated', False)}
        
        Args:
            entity_id (int, optional): ID for single entity requests
            use_v1 (bool): Use v1 API instead of v2 (default: False)
            data (dict, optional): Request body for POST/PATCH/PUT requests
            page_limit (int, optional): Max pages for paginated requests (None = all)
            include_metadata (bool): Include full API response metadata (default: False)
            **kwargs: Additional query parameters
            
        Returns:
            By default returns just the data (list or dict).
            If include_metadata=True, returns full API response with metadata.
            
        Example:
            # Get single entity (returns just the entity data)
            entity = qb.{name}(entity_id=123)
            
            # Get list with filters (returns just the list of entities)
            entities = qb.{name}(status='active', limit=50)
            
            # Get full response with metadata
            full_response = qb.{name}(include_metadata=True)
            
            # Create new entity
            new_entity = qb.{name}(data={{"name": "Example"}})
        """
        
        dynamic_method.__doc__ = method_doc
        dynamic_method.__name__ = name
        
        return dynamic_method

    def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check by making a simple API request.
        
        Returns:
            dict: Health check results
        """
        try:
            # Try to fetch a simple endpoint to verify connectivity
            result = self._make_request('GET', 'get_api_clients', params={'page_size': 1})
            return {
                'status': 'healthy',
                'authenticated': self._auth.is_authenticated(),
                'api_accessible': True,
                'timestamp': time.time()
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'authenticated': self._auth.is_authenticated(),
                'api_accessible': False,
                'error': str(e),
                'timestamp': time.time()
            }
    
    def list_available_endpoints(self) -> List[str]:
        """
        Get a list of all available endpoint methods.
        
        Returns:
            List[str]: All available endpoint method names
        """
        return sorted(QBENCH_ENDPOINTS.keys())
    
    def get_endpoint_info(self, endpoint_name: str) -> Dict[str, Any]:
        """
        Get information about a specific endpoint.
        
        Args:
            endpoint_name: Name of the endpoint
            
        Returns:
            dict: Endpoint configuration information
            
        Raises:
            QBenchValidationError: If endpoint doesn't exist
        """
        if endpoint_name not in QBENCH_ENDPOINTS:
            raise QBenchValidationError(f"Endpoint '{endpoint_name}' not found")
        
        config = QBENCH_ENDPOINTS[endpoint_name].copy()
        config['name'] = endpoint_name
        return config
    
    def close(self) -> None:
        """Close the HTTP session and clean up resources."""
        if hasattr(self, '_session'):
            self._session.close()
            logger.debug("QBench API session closed")
