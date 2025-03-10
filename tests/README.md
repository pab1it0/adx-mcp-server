# Tests for Azure Data Explorer MCP Server

This directory contains unit tests for the Azure Data Explorer MCP Server.

## Test Structure

- `conftest.py` - Contains common fixtures used across tests
- `test_config.py` - Tests for the configuration handling
- `test_server.py` - Tests for the MCP server tools and functionality
- `test_main.py` - Tests for the main application entry point
- `test_error_handling.py` - Tests for error handling behaviors

## Running Tests

You can run the tests using pytest:

```bash
# Install the development dependencies if not already installed
uv pip install -e ".[dev]"

# Run all tests
pytest

# Run with coverage report
pytest --cov=src --cov-report=term-missing

# Run specific test file
pytest tests/test_server.py

# Run specific test
pytest tests/test_server.py::TestServerTools::test_execute_query
```

## Coverage

The test suite aims to cover:

1. Configuration validation and error handling
2. MCP tools functionality
3. Error handling for Azure Data Explorer operations
4. Environment setup and validation

## Adding New Tests

When adding new features to the server, follow these guidelines for adding tests:

1. Put related tests in the appropriate test file or create a new one if needed
2. Use fixtures from `conftest.py` where possible
3. Mock external dependencies (especially Azure services)
4. Test both success and failure paths
5. Add appropriate assertions to verify functionality
