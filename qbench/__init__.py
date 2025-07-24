"""QBench SDK - A Python SDK for QBench LIMS API."""

__version__ = "0.1.1"
__author__ = "Smithers"
__email__ = "nwilliams@smithers.com"
__description__ = "Python SDK for QBench LIMS API"

from .api import QBenchAPI
from .exceptions import (
    QBenchAPIError, 
    QBenchAuthError, 
    QBenchConnectionError,
    QBenchTimeoutError,
    QBenchValidationError
)

# Main connection function for ease of use
def connect(base_url: str, api_key: str, api_secret: str, **kwargs) -> QBenchAPI:
    """
    Create a connection to QBench LIMS.
    
    Args:
        base_url (str): The base URL of your QBench instance
        api_key (str): Your QBench API key
        api_secret (str): Your QBench API secret
        **kwargs: Additional arguments passed to QBenchAPI constructors
        
    Returns:
        QBenchAPI: Configured QBench API client
        
    Example:
        >>> import qbench
        >>> qb = qbench.connect(
        ...     base_url="https://your-instance.qbench.com",
        ...     api_key="your_key",
        ...     api_secret="your_secret"
        ... )
        >>> sample = qb.get_sample(1234)
    """
    return QBenchAPI(base_url=base_url, api_key=api_key, api_secret=api_secret, **kwargs)

# Export the main classes and functions
__all__ = [
    "QBenchAPI",
    "QBenchAPIError", 
    "QBenchAuthError",
    "QBenchConnectionError",
    "QBenchTimeoutError",
    "QBenchValidationError",
    "connect",
    "__version__",
]