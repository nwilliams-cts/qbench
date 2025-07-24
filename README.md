# QBench Python SDK

A modern, production-ready Python SDK for the QBench LIMS API that provides a simple and intuitive interface for interacting with your QBench laboratory information management system.

## Features

- **Async-first design** with seamless sync compatibility 
- **Comprehensive API coverage** with 200+ endpoints (v1 and v2)
- **Automatic pagination** with configurable limits and concurrent page fetching
- **Robust authentication** with JWT token management and automatic refresh
- **Advanced error handling** with custom exceptions and retry logic
- **Type hints throughout** for excellent IDE support and development experience
- **Concurrent request handling** with rate limiting and connection pooling
- **Dynamic method generation** based on available endpoints
- **Comprehensive test suite** with 91% code coverage
- **Production-ready packaging** with modern Python tooling

## Installation

### For Development

```bash
git clone https://github.com/nwilliams-cts/qbench.git
cd qbench
pip install -e .[dev]
```

### As a Package

```bash
pip install qbench
```

## Quick Start

```python
import qbench

# Connect to your QBench instance
qb = qbench.connect(
    base_url="https://your-qbench-instance.qbench.net",
    api_key="your_api_key",
    api_secret="your_api_secret"
)

# Check connection health
health = qb.health_check()
print(f"API Status: {health['status']}")

# Get a specific sample
sample = qb.get_sample(entity_id=1234)
print(f"Sample: {sample}")

# Get all customers (automatically paginated)
customers = qb.get_customers()
print(f"Total customers: {len(customers['data'])}")

# Search with filters
filtered_samples = qb.get_samples(status="active", page_limit=2)

# Use v1 API when needed  
legacy_data = qb.get_samples(use_v1=True)

# Create new records
new_customer = qb.create_customers(data={
    "name": "ACME Corp",
    "email": "contact@acme.com"
})

# Clean up connection when done
qb.close()
```

## API Coverage

The SDK provides comprehensive coverage of the QBench API with 200+ endpoints across both v1 and v2 APIs:

### Core Entities
- **Samples**: Full CRUD operations with filtering and batch processing
- **Customers**: Customer management and relationship tracking  
- **Orders**: Order lifecycle management
- **Assays**: Laboratory test and assay management
- **Tests**: Individual test result handling
- **Invoicing**: Complete billing and payment processing
- **Reports**: Access to QBench reporting system

### Laboratory Management
- **Batches**: Sample batch processing and tracking
- **Worksheets**: Laboratory worksheet management
- **Turnarounds**: SLA and timing management
- **Locations**: Sample location and storage tracking
- **Projects**: Project-based sample organization

### Advanced Features
- **File Management**: Attachment upload and management
- **User Management**: User accounts and permissions
- **API Client Management**: API access control
- **Label Printing**: Barcode and label generation
- **Payment Processing**: Invoice and payment handling

### Available Methods

The SDK dynamically generates methods based on the QBench API. Common patterns:

```python
# GET single entity
sample = qb.get_sample(entity_id=123)
customer = qb.get_customer(entity_id=456)

# GET collections (with automatic pagination)
all_samples = qb.get_samples()
active_orders = qb.get_orders(status="active")

# CREATE entities
new_sample = qb.create_samples(data={...})
new_customer = qb.create_customers(data={...})

# UPDATE entities  
updated = qb.update_samples(entity_id=123, data={...})
modified = qb.update_customers(entity_id=456, data={...})

# DELETE entities
qb.delete_sample(entity_id=123)
qb.delete_customer(entity_id=456)
```

See the [full endpoint documentation](qbench/endpoints.py) for all 200+ available methods.

## Configuration

### Authentication

QBench uses JWT-based authentication with automatic token management. You'll need:

1. **API Key**: Your unique API identifier
2. **API Secret**: Your secret key for signing JWTs  
3. **Base URL**: Your QBench instance URL

```python
# Basic connection
qb = qbench.connect(
    base_url="https://your-instance.qbench.com", 
    api_key="your_api_key_here",
    api_secret="your_secret_here"
)

# Advanced configuration
qb = qbench.connect(
    base_url="https://your-instance.qbench.com",
    api_key="your_api_key_here", 
    api_secret="your_secret_here",
    timeout=30,              # Request timeout in seconds
    retry_attempts=3,        # Number of retry attempts
    concurrency_limit=10     # Max concurrent requests for pagination
)
```

### Environment Variables

For security, you can use environment variables:

```bash
export QBENCH_BASE_URL="https://your-instance.qbench.com"
export QBENCH_API_KEY="your_api_key"
export QBENCH_API_SECRET="your_secret"
```

```python
import os
import qbench

qb = qbench.connect(
    base_url=os.getenv("QBENCH_BASE_URL"),
    api_key=os.getenv("QBENCH_API_KEY"), 
    api_secret=os.getenv("QBENCH_API_SECRET")
)
```

### Advanced Usage

```python
# Connection health monitoring
health = qb.health_check()
is_connected = health.get('api_accessible', False)

# Explore available endpoints
endpoints = qb.list_available_endpoints()
print(f"Available endpoints: {len(endpoints)}")

# Get endpoint information
info = qb.get_endpoint_info("get_samples")
print(f"Method: {info['method']}, Paginated: {info.get('paginated', False)}")

# Control pagination behavior
all_samples = qb.get_samples(page_limit=None)    # Get all pages
limited = qb.get_samples(page_limit=5)           # First 5 pages only
single_page = qb.get_samples(page_limit=1)       # Just first page

# Use v1 API when needed for specific endpoints
legacy_data = qb.get_samples(use_v1=True)

# Concurrent processing with rate limiting
qb = qbench.connect(..., concurrency_limit=5)  # Max 5 concurrent requests
```

## Error Handling

The SDK provides comprehensive error handling with custom exceptions:

```python
from qbench.exceptions import (
    QBenchAPIError,
    QBenchAuthError, 
    QBenchConnectionError,
    QBenchTimeoutError,
    QBenchValidationError
)

try:
    sample = qb.get_sample(entity_id=999999)
except QBenchAPIError as e:
    print(f"API Error: {e}")
    print(f"Status Code: {e.status_code}")
    print(f"Response Data: {e.response_data}")
except QBenchAuthError as e:
    print(f"Authentication Error: {e}")
except QBenchConnectionError as e:
    print(f"Connection Error: {e}")
except QBenchTimeoutError as e:
    print(f"Timeout Error: {e}")
except QBenchValidationError as e:
    print(f"Validation Error: {e}")
```

### Automatic Retry Logic

The SDK includes intelligent retry logic for connection issues:

```python
# Retries are automatic for:
# - Connection timeouts
# - Network errors
# - Rate limiting (429 errors)

# HTTP errors (4xx, 5xx) are NOT retried automatically
# Authentication errors trigger token refresh attempts
```

## Async Usage

The SDK is built async-first with seamless sync compatibility:

```python
import asyncio
import qbench

async def main():
    qb = qbench.connect(
        base_url="https://your-instance.qbench.com",
        api_key="your_api_key",
        api_secret="your_secret"
    )
    
    # These calls are naturally async when called from async context
    sample = await qb.get_sample(entity_id=1234)
    customers = await qb.get_customers()
    
    # Concurrent operations
    tasks = [
        qb.get_sample(entity_id=i) 
        for i in range(1000, 1010)
    ]
    results = await asyncio.gather(*tasks)
    
    qb.close()

# Run async function
asyncio.run(main())

# Or use sync mode (automatically detected)
qb = qbench.connect(...)
sample = qb.get_sample(entity_id=1234)  # Sync call
customers = qb.get_customers()          # Sync call
qb.close()
```

## Development

### Setup

```bash
# Clone repository
git clone https://github.com/nwilliams-cts/qbench.git
cd qbench

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode
pip install -e .[dev]
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=qbench --cov-report=html

# Run specific test file
pytest tests/test_api.py

# Run with verbose output
pytest -v

# Run integration tests (requires QBench instance)
pytest tests/test_integration.py
```

**Current Test Coverage: 91%** (265 statements, 86 tests)

### Code Quality

```bash
# Format code with black
black qbench/ tests/

# Sort imports  
isort qbench/ tests/

# Lint with flake8
flake8 qbench/ tests/

# Type checking with mypy
mypy qbench/

# Run pre-commit hooks
pre-commit run --all-files
```

### Project Structure

```
qbench/
├── qbench/                 # Main package
│   ├── __init__.py        # Package entry point
│   ├── api.py             # Main API client
│   ├── auth.py            # Authentication handling
│   ├── endpoints.py       # API endpoint definitions
│   └── exceptions.py      # Custom exceptions
├── tests/                 # Test suite
│   ├── test_api.py        # API client tests
│   ├── test_auth.py       # Authentication tests
│   ├── test_exceptions.py # Exception tests
│   ├── test_init.py       # Package tests
│   ├── test_integration.py # Integration tests
│   └── conftest.py        # Test fixtures
├── examples/              # Usage examples
├── setup.py              # Package setup
├── pyproject.toml        # Modern Python configuration
└── README.md             # This file
```

## Examples

See the [examples/](examples/) directory for complete usage examples:

- [basic_usage.py](examples/basic_usage.py) - Getting started with common operations
- [advanced_usage.py](examples/advanced_usage.py) - Advanced features and async usage

## API Documentation

- [QBench REST API v1 Documentation](https://junctionconcepts.zendesk.com/hc/en-us/articles/360030760992-QBench-REST-API-v1-0-Documentation-Full)
- [API v2 Swagger Definition](example_v2_swagger.json) (included in repository)

## Package Information

- **Version**: 1.0.0
- **Python**: >=3.8
- **Dependencies**: requests, aiohttp, tenacity, python-dateutil
- **License**: MIT
- **Test Coverage**: 91%

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes with tests
4. Ensure code quality (`black`, `flake8`, `mypy`)
5. Run the test suite (`pytest --cov=qbench`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### Development Guidelines

- Write tests for all new functionality
- Maintain code coverage above 90%
- Follow PEP 8 style guidelines
- Add type hints to all public APIs
- Update documentation for new features

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **SDK Issues**: Open an issue on GitHub
- **QBench API Support**: Contact Junction Concepts support
- **Documentation**: See examples and API docs above
