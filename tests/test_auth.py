"""Tests for QBench authentication module."""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from qbench.auth import QBenchAuth
from qbench.exceptions import QBenchAuthError, QBenchConnectionError


class TestQBenchAuth:
    """Test cases for QBenchAuth class."""
    
    def test_init_success(self):
        """Test successful QBenchAuth initialization."""
        with patch.object(QBenchAuth, '_fetch_access_token'):
            auth = QBenchAuth("https://test.qbench.com", "test_key", "test_secret")
            
            assert auth._base_url == "https://test.qbench.com"
            assert auth._api_key == "test_key"
            assert auth._api_secret == "test_secret"
    
    def test_init_missing_params(self):
        """Test QBenchAuth initialization with missing parameters."""
        with pytest.raises(QBenchAuthError):
            QBenchAuth("", "test_key", "test_secret")
        
        with pytest.raises(QBenchAuthError):
            QBenchAuth("https://test.qbench.com", "", "test_secret")
        
        with pytest.raises(QBenchAuthError):
            QBenchAuth("https://test.qbench.com", "test_key", "")
    
    def test_base64_url_encode(self):
        """Test base64 URL encoding."""
        with patch.object(QBenchAuth, '_fetch_access_token'):
            auth = QBenchAuth("https://test.qbench.com", "test_key", "test_secret")
            
            test_data = b"test_data"
            result = auth._base64_url_encode(test_data)
            
            # Should be base64 encoded without padding
            assert isinstance(result, str)
            assert result == "dGVzdF9kYXRh"  # base64 of "test_data" without padding
    
    def test_generate_jwt(self):
        """Test JWT generation."""
        with patch.object(QBenchAuth, '_fetch_access_token'):
            auth = QBenchAuth("https://test.qbench.com", "test_key", "test_secret")
            
            # Mock time to make test deterministic
            with patch('time.time', return_value=1640995200):  # Fixed timestamp
                jwt_token = auth._generate_jwt()
                
                assert isinstance(jwt_token, str)
                assert jwt_token.count('.') == 2  # JWT has 3 parts separated by dots
                
                # Split and verify structure
                header, payload, signature = jwt_token.split('.')
                assert len(header) > 0
                assert len(payload) > 0
                assert len(signature) > 0
    
    @patch('requests.post')
    def test_fetch_access_token_success(self, mock_post):
        """Test successful token fetching."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"access_token": "test_token_123"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        with patch.object(QBenchAuth, '_fetch_access_token'):
            auth = QBenchAuth("https://test.qbench.com", "test_key", "test_secret")
        
        # Now test the actual token fetching
        auth._fetch_access_token()
        
        assert auth._access_token == "test_token_123"
        assert auth._token_expiry > time.time()
        mock_post.assert_called_once()
    
    @patch('requests.post')
    def test_fetch_access_token_401(self, mock_post):
        """Test token fetching with 401 error."""
        from requests.exceptions import HTTPError
        
        mock_response = Mock()
        mock_response.status_code = 401
        http_error = HTTPError(response=mock_response)
        mock_post.side_effect = http_error
        
        with patch.object(QBenchAuth, '_fetch_access_token'):
            auth = QBenchAuth("https://test.qbench.com", "test_key", "test_secret")
        
        with pytest.raises(QBenchAuthError) as exc_info:
            auth._fetch_access_token()
        
        assert "Invalid API credentials" in str(exc_info.value)
    
    @patch('requests.post')
    def test_fetch_access_token_403_forbidden(self, mock_post):
        """Test token fetching with 403 Forbidden error."""
        from requests.exceptions import HTTPError
        
        mock_response = Mock()
        mock_response.status_code = 403
        http_error = HTTPError(response=mock_response)
        mock_post.side_effect = http_error
        
        with patch.object(QBenchAuth, '_fetch_access_token'):
            auth = QBenchAuth("https://test.qbench.com", "test_key", "test_secret")
        
        with pytest.raises(QBenchAuthError) as exc_info:
            auth._fetch_access_token()
        
        assert "API access forbidden" in str(exc_info.value)
    
    @patch('requests.post')
    def test_fetch_access_token_other_http_error(self, mock_post):
        """Test token fetching with other HTTP error."""
        from requests.exceptions import HTTPError
        
        mock_response = Mock()
        mock_response.status_code = 500
        http_error = HTTPError(response=mock_response)
        mock_post.side_effect = http_error
        
        with patch.object(QBenchAuth, '_fetch_access_token'):
            auth = QBenchAuth("https://test.qbench.com", "test_key", "test_secret")
        
        with pytest.raises(QBenchAuthError) as exc_info:
            auth._fetch_access_token()
        
        assert "HTTP error during authentication" in str(exc_info.value)
    
    @patch('requests.post')
    def test_fetch_access_token_no_token_in_response(self, mock_post):
        """Test token fetching when response doesn't contain access_token."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"error": "No token"}  # Missing access_token
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        with patch.object(QBenchAuth, '_fetch_access_token'):
            auth = QBenchAuth("https://test.qbench.com", "test_key", "test_secret")
        
        with pytest.raises(QBenchAuthError) as exc_info:
            auth._fetch_access_token()
        
        assert "Failed to obtain access token from response" in str(exc_info.value)
    
    @patch('requests.post')
    def test_fetch_access_token_unexpected_error(self, mock_post):
        """Test token fetching with unexpected error."""
        mock_post.side_effect = ValueError("Unexpected error")
        
        with patch.object(QBenchAuth, '_fetch_access_token'):
            auth = QBenchAuth("https://test.qbench.com", "test_key", "test_secret")
        
        with pytest.raises(QBenchAuthError) as exc_info:
            auth._fetch_access_token()
        
        assert "Unexpected error during authentication" in str(exc_info.value)
    
    def test_get_access_token_valid(self):
        """Test getting access token when valid."""
        with patch.object(QBenchAuth, '_fetch_access_token'):
            auth = QBenchAuth("https://test.qbench.com", "test_key", "test_secret")
            
            # Set up a valid token
            auth._access_token = "valid_token"
            auth._token_expiry = int(time.time()) + 3600  # Expires in 1 hour
            
            token = auth.get_access_token()
            assert token == "valid_token"
    
    def test_get_access_token_expired(self):
        """Test getting access token when expired."""
        with patch.object(QBenchAuth, '_fetch_access_token') as mock_fetch:
            auth = QBenchAuth("https://test.qbench.com", "test_key", "test_secret")
            
            # Reset the call count after initialization
            mock_fetch.reset_mock()
            
            # Set up an expired token
            auth._access_token = "expired_token"
            auth._token_expiry = int(time.time()) - 3600  # Expired 1 hour ago
            
            # Mock the refresh to set a new token
            def refresh_token():
                auth._access_token = "new_token"
                auth._token_expiry = int(time.time()) + 3600
            
            mock_fetch.side_effect = refresh_token
            
            token = auth.get_access_token()
            assert token == "new_token"
            mock_fetch.assert_called_once()
    
    def test_get_headers(self):
        """Test getting headers with authorization."""
        with patch.object(QBenchAuth, '_fetch_access_token'):
            auth = QBenchAuth("https://test.qbench.com", "test_key", "test_secret")
            
            # Set up a valid token
            auth._access_token = "test_token"
            auth._token_expiry = int(time.time()) + 3600
            
            headers = auth.get_headers()
            
            assert headers["Authorization"] == "Bearer test_token"
            assert headers["Content-Type"] == "application/json"
    
    def test_is_authenticated_true(self):
        """Test is_authenticated when token is valid."""
        with patch.object(QBenchAuth, '_fetch_access_token'):
            auth = QBenchAuth("https://test.qbench.com", "test_key", "test_secret")
            
            # Set up a valid token
            auth._access_token = "valid_token"
            auth._token_expiry = int(time.time()) + 3600
            
            assert auth.is_authenticated() is True
    
    def test_is_authenticated_false(self):
        """Test is_authenticated when token is expired or missing."""
        with patch.object(QBenchAuth, '_fetch_access_token'):
            auth = QBenchAuth("https://test.qbench.com", "test_key", "test_secret")
            
            # No token
            auth._access_token = None
            assert auth.is_authenticated() is False
            
            # Expired token
            auth._access_token = "expired_token"
            auth._token_expiry = int(time.time()) - 3600
            assert auth.is_authenticated() is False
    
    def test_init_authentication_failure(self):
        """Test QBenchAuth initialization when initial authentication fails."""
        with patch.object(QBenchAuth, '_fetch_access_token') as mock_fetch:
            # Simulate an authentication failure during initialization
            mock_fetch.side_effect = Exception("Network error")
            
            with pytest.raises(QBenchAuthError) as exc_info:
                QBenchAuth("https://test.qbench.com", "test_key", "test_secret")
            
            assert "Initial authentication failed" in str(exc_info.value)
    
    @patch('requests.post')
    def test_fetch_access_token_request_exception(self, mock_post):
        """Test token fetching with RequestException."""
        from requests.exceptions import RequestException
        
        mock_post.side_effect = RequestException("Network connection failed")
        
        with patch.object(QBenchAuth, '_fetch_access_token'):
            auth = QBenchAuth("https://test.qbench.com", "test_key", "test_secret")
        
        with pytest.raises(QBenchConnectionError) as exc_info:
            auth._fetch_access_token()
        
        assert "Connection error during authentication" in str(exc_info.value)


if __name__ == '__main__':
    pytest.main([__file__])
