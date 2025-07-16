import requests
import aiohttp
import asyncio
import logging
from typing import Optional, Dict
from tenacity import retry, wait_exponential, stop_after_attempt
from .auth import QBenchAuth
from .exceptions import QBenchAPIError
from .endpoints import QBENCH_ENDPOINTS


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
        self._session = requests.Session() # Reuse HTTP session
        self._session.headers.update(self._auth.get_headers())


    @retry(wait=wait_exponential(multiplier=2, min=1, max=10), stop=stop_after_attempt(5))
    def _make_request(self, method: str, endpoint_key: str, use_v1: bool = False,
                      params: Optional[dict] = None, data: Optional[dict] = None,
                      path_params: Optional[dict] = None) -> dict:
        """
        Makes a synchronous request to the QBench API.

        Args:
            method (str): HTTP method ('GET', 'POST', etc.).
            endpoint (str): API endpoint path.
            use_v1 (bool): If True, use the v1 API. Else use v2.
            params (dict, optional): URL parameters for the request.
            data (dict, optional): JSON payload for the request.
            path_params (dict, optional): Parameters to replace in the endpoint

        Returns:
            dict: JSON response from the API.
        """
        if endpoint_key not in QBENCH_ENDPOINTS:
            raise ValueError(f"Invalid API endpoint: {endpoint_key}")
        
        # Default to v2 unless explicitly set
        version = "v1" if use_v1 else "v2"
        base_url = f"{self._base_url_v1 if use_v1 else self._base_url}"

        # Get the correct endpoint format
        endpoint = QBENCH_ENDPOINTS[endpoint_key].get(version)
        if not endpoint:
            raise ValueError(f"Endpoint '{endpoint_key}' does not exist in version {version}")

        # If path_params are provided, safely format the url
        if path_params:
            endpoint = endpoint.format(**path_params)

        url = f"{base_url}/{endpoint}"

        try:
            response = self._session.request(method, url, params=params, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"API request failed: {method.upper()} {url} - {e}")
            raise QBenchAPIError(f"Error in {method.upper()} request to {url}: {e}")

    async def _fetch_page(self, session: aiohttp.ClientSession, url: str, page: int, params: Dict) -> Dict:
        final_url = f"{url}?page_num={page}&page_size=50"
        async with session.get(final_url, params=params) as response:
            response.raise_for_status()
            return (await response.json()) or {'data': []}

    async def _get_entity_list(self, endpoint_key: str, use_v1: bool = False, page_limit: Optional[int] = None, path_params: Optional[Dict] = {}, **kwargs):
        version = "v1" if use_v1 else "v2"
        base_url = f"{self._base_url_v1 if use_v1 else self._base_url}"

        endpoint = QBENCH_ENDPOINTS[endpoint_key][version]
        if path_params:
            endpoint = endpoint.format(**path_params)

        url = f"{base_url}/{endpoint}"

        entity_array = []
        async with aiohttp.ClientSession(headers=self._auth.get_headers()) as session:
            page_1_res = await self._fetch_page(session, url, 1, kwargs)
            page_1_data = page_1_res.get('data') or []

            page_limit = page_limit or page_1_res.get('total_pages') or 1
            entity_array.extend(page_1_data)

            if page_limit > 1:
                tasks = [self._fetch_page(session, url, page, kwargs) for page in range(2, page_limit + 1)]
                results = await asyncio.gather(*tasks)

                for page_data in results:
                    entity_array.extend(page_data.get('data') or [])

        return {'data': entity_array}

    def __getattr__(self, name):
        # Overrides behavior of the get attr function to route different endpoints to their correct logic
        if name not in QBENCH_ENDPOINTS:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
        
        async def async_dynamic_method(entity_id: Optional[int] = None, use_v1: bool = False, page_limit: Optional[int] = None, data: Optional[Dict] = None, **kwargs):
            path_params = {"id": entity_id} if entity_id else {}
            method = QBENCH_ENDPOINTS[name].get('method', 'GET')

            if QBENCH_ENDPOINTS[name].get('paginated'):
                return await self._get_entity_list(name, use_v1=use_v1, page_limit=page_limit, path_params=path_params, **kwargs)
            else:
                loop = asyncio.get_running_loop()
                return await loop.run_in_executor(None, self._make_request, method, name, use_v1, kwargs, data, path_params)

        def dynamic_method(entity_id: Optional[int] = None, use_v1: bool = False, data: Optional[Dict] = None, page_limit: Optional[int] = None, **kwargs):
            try:
                loop = asyncio.get_running_loop()
                # If there's an active event loop, return coroutine
                return async_dynamic_method(entity_id=entity_id, use_v1=use_v1, page_limit=page_limit, data=data, **kwargs)
            except RuntimeError:
                # No active event loop; safe to call asyncio.run()
                return asyncio.run(async_dynamic_method(entity_id=entity_id, use_v1=use_v1, page_limit=page_limit, data=data, **kwargs))
            
        return dynamic_method
