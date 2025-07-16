"""Tests for QBench exceptions module."""

import pytest
from qbench.exceptions import (
    QBenchError,
    QBenchAPIError,
    QBenchAuthError,
    QBenchConnectionError,
    QBenchTimeoutError,
    QBenchValidationError
)


class TestQBenchExceptions:
    """Test cases for QBench exception classes."""
    
    def test_qbench_error_base(self):
        """Test base QBenchError exception."""
        error = QBenchError("Test error")
        assert str(error) == "Test error"
        assert isinstance(error, Exception)
    
    def test_qbench_api_error(self):
        """Test QBenchAPIError with status code and data."""
        error = QBenchAPIError("API failed", 404, {"error": "Not found"})
        assert str(error) == "HTTP 404: API failed"  # Includes status code in string
        assert error.status_code == 404
        assert error.response_data == {"error": "Not found"}
        
        # Test without status code and data
        error2 = QBenchAPIError("Simple API error")
        assert str(error2) == "Simple API error"  # No status code prefix
        assert error2.status_code is None
        assert error2.response_data is None
    
    def test_qbench_auth_error(self):
        """Test QBenchAuthError."""
        error = QBenchAuthError("Authentication failed")
        assert str(error) == "Authentication failed"
        assert isinstance(error, QBenchError)
    
    def test_qbench_connection_error(self):
        """Test QBenchConnectionError."""
        error = QBenchConnectionError("Connection timeout")
        assert str(error) == "Connection timeout"
        assert isinstance(error, QBenchError)
    
    def test_qbench_timeout_error(self):
        """Test QBenchTimeoutError."""
        error = QBenchTimeoutError("Request timed out")
        assert str(error) == "Request timed out"
        assert isinstance(error, QBenchError)
    
    def test_qbench_validation_error(self):
        """Test QBenchValidationError."""
        error = QBenchValidationError("Invalid input")
        assert str(error) == "Invalid input"
        assert isinstance(error, QBenchError)
    
    def test_exception_inheritance(self):
        """Test that all exceptions inherit from QBenchError."""
        exceptions = [
            QBenchAPIError("test"),
            QBenchAuthError("test"),
            QBenchConnectionError("test"),
            QBenchTimeoutError("test"),
            QBenchValidationError("test")
        ]
        
        for exc in exceptions:
            assert isinstance(exc, QBenchError)
            assert isinstance(exc, Exception)
