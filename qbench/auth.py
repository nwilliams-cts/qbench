import jwt
import json
import time
import requests
from hashlib import sha256
from hmac import HMAC
from base64 import urlsafe_b64encode
from requests.exceptions import HTTPError

class QBenchAuth:
    def __init__(self, base_url, api_key, api_secret):
        if not all([base_url, api_key, api_secret]):
            raise ValueError("Missing required information to connect to QBench. Please review parameters")
        
        self._base_url = base_url
        self._api_key = api_key
        self._api_secret = api_secret
        self._access_token = None
        self._token_expiry = 0

<<<<<<< HEAD
=======
        ## TODO: Get jwt and conduct a health check after initialization
        

>>>>>>> f78ae61 (init commit)
    def _base64_url_encode(self, data):
        """Helper to Base64 URL encode data without padding."""
        return urlsafe_b64encode(data).decode('utf-8').rstrip("=")

    def _generate_jwt(self):
        """Generate a JWT with HMAC SHA-256 encoding."""

        iat = int(time.time())
        exp = iat + 3600 # Valid for 1 hour

        # Header and payload as per QBench spec
        header = {"typ": "JWT", "alg": "HS256"}
        payload = {"sub": self._api_key, "iat": iat, "exp": exp}

        # JSON encode and Base64 URL encode header and payload
        header_encoded = self._base64_url_encode(json.dumps(header).encode())
        payload_encoded = self._base64_url_encode(json.dumps(payload).encode())

        # Create token string
        token = f"{header_encoded}.{payload_encoded}"

        # Sign the token with the secret
        signature = HMAC(self._api_secret.encode(), token.encode(), sha256).digest()
        signature_encoded = urlsafe_b64encode(signature).decode().rstrip("=")

        # Full signed token output
        signed_token = f"{token}.{signature_encoded}"
        return signed_token

    def _fetch_access_token(self):
        """Obtain an access token from QBench."""
        signed_token = self._generate_jwt()

        # Prepare the request params
        parameters = {
            "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
            "assertion": signed_token
        }

        # Endpoint to fetch the token
        token_url = f"{self._base_url}/qbench/oauth2/v1/token"

        try:
            response = requests.post(token_url, data=parameters)
            response.raise_for_status()
            token_data = response.json()
            self._access_token = token_data.get('access_token')
            self._token_expiry = int(time.time()) + 3600

            if not self._access_token:
                raise ValueError("Failed to obtain access token.")

        except HTTPError as e:
            print(f"Error fetching access token: {e}")
            raise

    def get_access_token(self):
        """Retrieve a valid access token, refreshing if necessary."""
        if not self._access_token or int(time.time()) >= self._token_expiry:
            self._fetch_access_token()
        return self._access_token

    def get_headers(self):
        """Return headers with Bearer authorization for authenticated requests."""
        access_token = self.get_access_token()
        return {
            "Authorization": f"Bearer {access_token}",
<<<<<<< HEAD
            "Content-Type": "applicaiton/json"
        }
=======
            "Content-Type": "application/json"
        }
>>>>>>> f78ae61 (init commit)
