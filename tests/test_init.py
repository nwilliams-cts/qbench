"""Tests for QBench SDK initialization and connect function."""

import pytest
from unittest.mock import patch, Mock
from qbench import connect, QBenchAPI
from qbench.exceptions import QBenchAuthError, QBenchAPIError, QBenchConnectionError


class TestQBenchInit:
    """Test cases for qbench module initialization."""
    
    def test_connect_function(self):
        """Test the connect convenience function."""
        with patch.object(QBenchAPI, '__init__', return_value=None) as mock_init:
            result = connect(
                base_url="https://test.qbench.com",
                api_key="test_key", 
                api_secret="test_secret",
                timeout=60
            )
            
            # Should return QBenchAPI instance
            assert isinstance(result, QBenchAPI)
            
            # Should have called QBenchAPI.__init__ with correct args
            mock_init.assert_called_once_with(
                base_url="https://test.qbench.com",
                api_key="test_key",
                api_secret="test_secret",
                timeout=60
            )
    
    def test_connect_function_defaults(self):
        """Test connect function with default parameters."""
        with patch.object(QBenchAPI, '__init__', return_value=None) as mock_init:
            result = connect(
                base_url="https://test.qbench.com",
                api_key="test_key",
                api_secret="test_secret"
            )
            
            assert isinstance(result, QBenchAPI)
            mock_init.assert_called_once_with(
                base_url="https://test.qbench.com",
                api_key="test_key",
                api_secret="test_secret"
            )
    
    def test_connect_function_auth_error(self):
        """Test connect function when authentication fails."""
        with patch.object(QBenchAPI, '__init__') as mock_init:
            mock_init.side_effect = QBenchAuthError("Authentication failed")
            
            with pytest.raises(QBenchAuthError):
                connect(
                    base_url="https://test.qbench.com",
                    api_key="invalid_key",
                    api_secret="invalid_secret"
                )
    
    def test_connect_function_with_kwargs(self):
        """Test connect function with additional kwargs."""
        # Test passing additional arguments through kwargs
        with patch('qbench.QBenchAPI') as mock_api:
            mock_api_instance = Mock()
            mock_api.return_value = mock_api_instance
            
            result = connect(
                base_url="https://test.qbench.com",
                api_key="test_key", 
                api_secret="test_secret",
                timeout=60,  # Additional kwarg
                retry_attempts=5  # Additional kwarg
            )
            
            mock_api.assert_called_once_with(
                base_url="https://test.qbench.com",
                api_key="test_key",
                api_secret="test_secret", 
                timeout=60,
                retry_attempts=5
            )
            assert result == mock_api_instance
    
    def test_exception_imports(self):
        """Test that exceptions are properly imported and accessible."""
        # This should exercise the exception import line in __init__.py
        from qbench import QBenchAPIError, QBenchAuthError, QBenchConnectionError
        
        # Test that we can create instances
        api_error = QBenchAPIError("Test API error")
        auth_error = QBenchAuthError("Test auth error") 
        conn_error = QBenchConnectionError("Test connection error")
        
        assert str(api_error) == "Test API error"
        assert str(auth_error) == "Test auth error"
        assert str(conn_error) == "Test connection error"
    

if __name__ == '__main__':
    pytest.main([__file__])
