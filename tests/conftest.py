"""Test configuration and fixtures for QBench SDK tests."""

import os
import pytest
from unittest.mock import Mock, patch
from qbench import QBenchAPI
from qbench.auth import QBenchAuth


# Test configuration
TEST_BASE_URL = "https://test.qbench.net"
TEST_API_KEY = "test_key"
TEST_API_SECRET = "test_secret"


@pytest.fixture
def mock_auth():
    """Mock QBench authentication."""
    with patch.object(QBenchAuth, '__init__', return_value=None) as mock_init:
        with patch.object(QBenchAuth, 'get_headers') as mock_headers:
            with patch.object(QBenchAuth, 'get_access_token') as mock_token:
                with patch.object(QBenchAuth, 'is_authenticated', return_value=True) as mock_is_auth:
                    with patch.object(QBenchAuth, '_fetch_access_token', return_value=None) as mock_fetch:
                        mock_headers.return_value = {
                            "Authorization": "Bearer test_token",
                            "Content-Type": "application/json"
                        }
                        mock_token.return_value = "test_token"
                        yield {
                            'headers': mock_headers,
                            'token': mock_token,
                            'is_auth': mock_is_auth,
                            'fetch': mock_fetch,
                            'init': mock_init
                        }


@pytest.fixture
def qb_client(mock_auth):
    """Create a test QBench client."""
    with patch('requests.Session') as mock_session_class:
        # Mock the session instance
        mock_session_instance = Mock()
        mock_session_class.return_value = mock_session_instance
        
        # Create client - this will now use our mocked session
        client = QBenchAPI(TEST_BASE_URL, TEST_API_KEY, TEST_API_SECRET)
        
        # Store the mock session for testing
        client._mock_session = mock_session_instance
        
        yield client


@pytest.fixture
def sample_response():
    """Sample API response data."""
    return {
        "data": [
            {
                "id": 1,
                "name": "Test Sample 1",
                "status": "active",
                "customer_id": 123
            },
            {
                "id": 2,
                "name": "Test Sample 2", 
                "status": "pending",
                "customer_id": 124
            }
        ],
        "total_pages": 1,
        "current_page": 1,
        "total_count": 2
    }


@pytest.fixture
def customer_response():
    """Sample customer response data."""
    return {
        "data": [
            {
                "id": 123,
                "name": "ACME Corp",
                "email": "contact@acme.com",
                "phone": "555-0123"
            }
        ],
        "total_pages": 1,
        "current_page": 1,
        "total_count": 1
    }
