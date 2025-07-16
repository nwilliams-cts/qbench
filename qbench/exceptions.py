"""Custom exceptions for QBench SDK."""

from typing import Optional, Dict, Any


class QBenchError(Exception):
    """Base exception for all QBench SDK errors."""
    pass


class QBenchAPIError(QBenchError):
    """Exception raised for errors in the QBench API.

    Attributes:
        message -- explanation of the error
        status_code -- HTTP status code if available
        response_data -- API response data if available
    """
    
    def __init__(
        self, 
        message: str, 
        status_code: Optional[int] = None, 
        response_data: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.response_data = response_data
        super().__init__(self.message)

    def __str__(self) -> str:
        if self.status_code:
            return f"HTTP {self.status_code}: {self.message}"
        return self.message


class QBenchAuthError(QBenchError):
    """Exception raised for authentication-related errors."""
    pass


class QBenchConnectionError(QBenchError):
    """Exception raised for connection-related errors."""
    pass


class QBenchValidationError(QBenchError):
    """Exception raised for validation errors."""
    pass


class QBenchTimeoutError(QBenchError):
    """Exception raised for timeout errors."""
    pass
