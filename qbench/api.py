import requests
import aiohttp
import asyncio
from typing import List, Dict, Optional
from .auth import QBenchAuth
from .exceptions import QBenchAPIError


class QBenchAPI:
    def __init__(self, base_url: str, api_key: str, api_secret: str, concurrency_limit: int = 10):
        """
        Initializes the QBenchAPI instance with authentication and base URLs.

        Args:
            base_url (str): The base URL of the QBench API.
            api_key (str): API key for authentication.
            api_secret (str): API secret for authentication.
            concurrency_limit (int): Maximum number of concurrent requests.
        """
        self._auth = QBenchAuth(base_url, api_key, api_secret)
        self._base_url = f"{base_url}/qbench/api/v2"
        self._base_url_v1 = f"{base_url}/qbench/api/v1"
        self._concurrency_limit = concurrency_limit  # Control API concurrency level

    def _make_request(self, method: str, endpoint: str, params: Optional[dict] = None, data: Optional[dict] = None) -> dict:
        """
        Makes a synchronous request to the QBench API.

        Args:
            method (str): HTTP method ('GET', 'POST', etc.).
            endpoint (str): API endpoint path.
            params (dict, optional): URL parameters for the request.
            data (dict, optional): JSON payload for the request.

        Returns:
            dict: JSON response from the API.
        """
        url = f"{self._base_url}/{endpoint}"
        headers = self._auth.get_headers()
        try:
            response = requests.request(method, url, headers=headers, params=params, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            raise QBenchAPIError(f"Error in {method.upper()} request to {url}: {str(e)}")

    def _get_entity(self, entity_type: str, object_id: Optional[int] = None, page_num: Optional[int] = None) -> dict:
        """
        Retrieves a specific entity or a paginated list of entities synchronously.

        Args:
            entity_type (str): The type of entity to retrieve.
            object_id (int, optional): ID of the specific entity.
            page_num (int, optional): Page number for pagination.

        Returns:
            dict: JSON response containing the entity data.
        """
        url = f"{entity_type}/{object_id}" if object_id else f"{entity_type}?page_num={page_num or 1}"
        return self._make_request("GET", url)

    async def _fetch_page_with_retry(self, session: aiohttp.ClientSession, entity_type: str, page_num: int, total_pages: int, addl_params: str) -> List[dict]:
        """
        Asynchronously fetches a page of entities with retry logic for handling rate limits.

        Args:
            session (aiohttp.ClientSession): The client session for making HTTP requests.
            entity_type (str): The type of entity to retrieve.
            page_num (int): Page number to fetch.
            total_pages (int): Total number of pages available.
            addl_params (str): Additional query parameters for the request.

        Returns:
            List[dict]: Data from the requested page.
        """
        retries = 5
        page_url = f"{self._base_url}/{entity_type}?page_num={page_num}&page_size=50{addl_params}"
        
        for attempt in range(retries):
            try:
                async with session.get(page_url) as response:
                    response.raise_for_status()
                    data = await response.json()
                    print(f"Page Processed: {page_num}/{total_pages}")
                    return data.get('data', [])
            except aiohttp.ClientResponseError as e:
                if e.status >= 400:
                    retry_after = int(response.headers.get('Retry-After', 4))
                    await asyncio.sleep(retry_after)
                    print(f"Retry {attempt+1} for page {page_num} due to {e.status}")
        return []

    async def _get_entity_list(self, entity_type: str, use_v1_endpoint: bool = False, page_limit: Optional[int] = None, **kwargs) -> dict:
        """
        Asynchronously retrieves a list of entities with pagination and optional concurrency control.

        Args:
            entity_type (str): The type of entity to retrieve.
            use_v1_endpoint (bool): Flag to use v1 or v2 of the API.
            page_limit (int, optional): Maximum number of pages to retrieve.
            **kwargs: Additional parameters for the API request.

        Returns:
            dict: Aggregated data from all retrieved pages.
        """
        entity_array = []
        addl_params = ''.join(f"&{k}={v}" for k, v in kwargs.items())
        base_url = self._base_url_v1 if use_v1_endpoint else self._base_url

        connector = aiohttp.TCPConnector(limit=self._concurrency_limit)
        timeout = aiohttp.ClientTimeout(total=1200)
        async with aiohttp.ClientSession(connector=connector, timeout=timeout, headers=self._auth.get_headers()) as session:
            page_1_url = f"{base_url}/{entity_type}?page_size=50{addl_params}"
            async with session.get(page_1_url) as response:
                response.raise_for_status()
                result = await response.json()
                total_pages = min(page_limit, result.get('total_pages')) if page_limit else result.get('total_pages')
                entity_array.extend(result.get('data', []))

                tasks = [
                    self._fetch_page_with_retry(session, entity_type, page, total_pages, addl_params)
                    for page in range(2, total_pages + 1)
                ]

                for batch_start in range(0, len(tasks), self._concurrency_limit):
                    batch_tasks = tasks[batch_start: batch_start + self._concurrency_limit]
                    pages_data = await asyncio.gather(*batch_tasks)
                    for page_data in pages_data:
                        entity_array.extend(page_data)

        return {'data': entity_array}

    def get_customer(self, customer_id: int) -> dict:
        """
        Retrieves a specific customer by ID.

        Args:
            customer_id (int): ID of the customer.

        Returns:
            dict: Customer data.
        """
        return self._get_entity('customers', object_id=customer_id)

    def get_customer_list(self, page_limit: Optional[int] = None, **kwargs) -> dict:
        """
        Synchronously retrieves a list of customers with optional pagination.

        Args:
            page_limit (int, optional): Maximum number of pages to retrieve.
            **kwargs: Additional parameters for the API request.

        Returns:
            dict: List of customer data.
        """
        return asyncio.run(self._get_entity_list('customers', use_v1_endpoint=True, page_limit=page_limit, **kwargs))

    async def get_customer_list_async(self, page_limit: Optional[int] = None, **kwargs) -> dict:
        """
        Asynchronously retrieves a list of customers with optional pagination.

        Args:
            page_limit (int, optional): Maximum number of pages to retrieve.
            **kwargs: Additional parameters for the API request.

        Returns:
            dict: List of customer data.
        """
        return await self._get_entity_list('customers', use_v1_endpoint=True, page_limit=page_limit, **kwargs)

    def get_order(self, order_id: int) -> dict:
        """
        Retrieves a specific order by ID.

        Args:
            order_id (int): ID of the order.

        Returns:
            dict: Order data.
        """
        return self._get_entity('orders', object_id=order_id)

    def get_order_list(self, page_limit: Optional[int] = None, **kwargs) -> dict:
        """
        Synchronously retrieves a list of orders with optional pagination.

        Args:
            page_limit (int, optional): Maximum number of pages to retrieve.
            **kwargs: Additional parameters for the API request.

        Returns:
            dict: List of order data.
        """
        return asyncio.run(self._get_entity_list('orders', page_limit=page_limit, **kwargs))

    async def get_order_list_async(self, page_limit: Optional[int] = None, **kwargs) -> dict:
        """
        Asynchronously retrieves a list of orders with optional pagination.

        Args:
            page_limit (int, optional): Maximum number of pages to retrieve.
            **kwargs: Additional parameters for the API request.

        Returns:
            dict: List of order data.
        """
        return await self._get_entity_list('orders', page_limit=page_limit, **kwargs)

    def get_sample(self, sample_id: int) -> dict:
        """
        Retrieves a specific sample by ID.

        Args:
            sample_id (int): ID of the sample.

        Returns:
            dict: Sample data.
        """
        return self._get_entity('samples', object_id=sample_id)

    def get_sample_list(self, page_limit: Optional[int] = None, **kwargs) -> dict:
        """
        Synchronously retrieves a list of samples with optional pagination.

        Args:
            page_limit (int, optional): Maximum number of pages to retrieve.
            **kwargs: Additional parameters for the API request.

        Returns:
            dict: List of sample data.
        """
        return asyncio.run(self._get_entity_list('samples', page_limit=page_limit, **kwargs))

    async def get_sample_list_async(self, page_limit: Optional[int] = None, **kwargs) -> dict:
        """
        Asynchronously retrieves a list of samples with optional pagination.

        Args:
            page_limit (int, optional): Maximum number of pages to retrieve.
            **kwargs: Additional parameters for the API request.

        Returns:
            dict: List of sample data.
        """
        return await self._get_entity_list('samples', page_limit=page_limit, **kwargs)
