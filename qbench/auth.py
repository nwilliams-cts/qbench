"""Authentication module for QBench SDK."""

import json
import time
import requests
from hashlib import sha256
from hmac import HMAC
from base64 import urlsafe_b64encode
from typing import Dict, Optional
from requests.exceptions import HTTPError, RequestException

from .exceptions import QBenchAuthError, QBenchConnectionError


class QBenchAuth:
    """Handles JWT-based authentication for QBench API."""
    
    def __init__(self, base_url: str, api_key: str, api_secret: str):
        """
        Initialize QBench authentication.
        
        Args:
            base_url (str): The base URL of the QBench instance
            api_key (str): API key for authentication
            api_secret (str): API secret for authentication
            
        Raises:
            QBenchAuthError: If required authentication parameters are missing
        """
        if not all([base_url, api_key, api_secret]):
            raise QBenchAuthError(
                "Missing required authentication information. "
                "Please provide base_url, api_key, and api_secret."
            )
        
        self._base_url = base_url.rstrip('/')
        self._api_key = api_key
        self._api_secret = api_secret
        self._access_token: Optional[str] = None
        self._token_expiry: int = 0

        # Perform initial authentication check
        try:
            self._fetch_access_token()
        except Exception as e:
            raise QBenchAuthError(f"Initial authentication failed: {e}")

    def _base64_url_encode(self, data: bytes) -> str:
        """Helper to Base64 URL encode data without padding."""
        return urlsafe_b64encode(data).decode('utf-8').rstrip("=")

    def _generate_jwt(self) -> str:
        """
        Generate a JWT with HMAC SHA-256 encoding.
        
        Returns:
            str: Signed JWT token
        """
        iat = int(time.time())
        exp = iat + 3600  # Valid for 1 hour

        # Header and payload as per QBench spec
        header = {"typ": "JWT", "alg": "HS256"}
        payload = {"sub": self._api_key, "iat": iat, "exp": exp}

        # JSON encode and Base64 URL encode header and payload
        header_encoded = self._base64_url_encode(json.dumps(header, separators=(',', ':')).encode())
        payload_encoded = self._base64_url_encode(json.dumps(payload, separators=(',', ':')).encode())

        # Create token string
        token = f"{header_encoded}.{payload_encoded}"

        # Sign the token with the secret
        signature = HMAC(self._api_secret.encode(), token.encode(), sha256).digest()
        signature_encoded = self._base64_url_encode(signature)

        # Full signed token output
        signed_token = f"{token}.{signature_encoded}"
        return signed_token
    def _fetch_access_token(self) -> None:
        """
        Obtain an access token from QBench.
        
        Raises:
            QBenchAuthError: If token acquisition fails
            QBenchConnectionError: If connection to QBench fails
        """
        try:
            signed_token = self._generate_jwt()

            # Prepare the request params
            parameters = {
                "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
                "assertion": signed_token
            }

            # Endpoint to fetch the token
            token_url = f"{self._base_url}/qbench/oauth2/v1/token"

            response = requests.post(
                token_url, 
                data=parameters,
                timeout=30,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            response.raise_for_status()
            
            token_data = response.json()
            self._access_token = token_data.get('access_token')
            
            # Set expiry to 50 minutes to allow for refresh before actual expiry
            self._token_expiry = int(time.time()) + (50 * 60)

            if not self._access_token:
                raise QBenchAuthError("Failed to obtain access token from response.")

        except HTTPError as e:
            if e.response.status_code == 401:
                raise QBenchAuthError("Invalid API credentials provided.")
            elif e.response.status_code == 403:
                raise QBenchAuthError("API access forbidden. Check your permissions.")
            else:
                raise QBenchAuthError(f"HTTP error during authentication: {e}")
        except RequestException as e:
            raise QBenchConnectionError(f"Connection error during authentication: {e}")
        except Exception as e:
            raise QBenchAuthError(f"Unexpected error during authentication: {e}")

    def get_access_token(self) -> str:
        """
        Retrieve a valid access token, refreshing if necessary.
        
        Returns:
            str: Valid access token
            
        Raises:
            QBenchAuthError: If token refresh fails
        """
        if not self._access_token or int(time.time()) >= self._token_expiry:
            self._fetch_access_token()
        return self._access_token

    def get_headers(self) -> Dict[str, str]:
        """
        Return headers with Bearer authorization for authenticated requests.
        
        Returns:
            Dict[str, str]: HTTP headers with authorization
        """
        access_token = self.get_access_token()
        return {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

    def is_authenticated(self) -> bool:
        """
        Check if the current token is valid and not expired.
        
        Returns:
            bool: True if authenticated, False otherwise
        """
        return (
            self._access_token is not None 
            and int(time.time()) < self._token_expiry
        )
