# Azure Data Explorer MCP Server Testing Guide

This document provides comprehensive information about testing the ADX MCP Server.

## Testing Philosophy

The ADX MCP Server follows these testing principles:

1. **Comprehensive Coverage**: Tests should cover both success paths and error paths
2. **Isolation**: Tests should be isolated from external dependencies (like Azure services)
3. **Realistic Data**: Mock data should resemble real Azure Data Explorer responses
4. **Maintainability**: Tests should be easy to understand and maintain

## Test Structure

The test suite is organized into the following categories:

### Unit Tests

- `test_config.py`: Tests for configuration handling and validation
- `test_server.py`: Tests for the core server functionality and tools
- `test_main.py`: Tests for the application entry point and setup process
- `test_error_handling.py`: Tests for various error conditions
- `test_result_formatting.py`: Tests for ADX result formatting functions
- `test_mock_data.py`: Tests with realistic mock data structures

### Integration Tests

- `integration/test_mcp_integration.py`: Tests that verify the complete flow of MCP tool execution

## Setting Up for Testing

### Installing Development Dependencies

```bash
# Install all dependencies including test dependencies
uv pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src --cov-report=term-missing

# Run a specific test file
pytest tests/test_server.py 

# Run a specific test
pytest tests/test_server.py::TestServerTools::test_execute_query
```

## Mock Fixtures

The test suite includes several useful fixtures:

- `mock_env_variables`: Sets up a complete environment with mock Azure credentials
- `mock_missing_env_variables`: Clears environment variables to test error handling
- `mock_kusto_client`: Provides a simple mock of the KustoClient
- `mock_kusto_integration`: Provides a comprehensive mock for integration tests
- `mock_kusto_real_data`: Provides realistic mock data structures

## Adding New Tests

When adding new features to the server, follow these guidelines:

1. **Add Unit Tests First**: Write tests for the new functionality before implementing it
2. **Test Edge Cases**: Include tests for error conditions and edge cases
3. **Use Existing Fixtures**: Leverage the existing fixtures for consistency
4. **Update Integration Tests**: Make sure the integration tests cover the new functionality
5. **Check Coverage**: Ensure that your tests provide adequate coverage

## Continuous Integration

The project includes GitHub Actions workflow configuration to automatically run tests on push and pull requests.

The workflow:
1. Runs on multiple Python versions (3.10, 3.11, 3.12)
2. Installs dependencies
3. Runs the test suite
4. Uploads coverage reports to Codecov

## Best Practices

- Keep tests focused on a single functionality
- Use descriptive test names that indicate what's being tested
- Avoid test dependencies (tests should be able to run in any order)
- Keep mock data realistic but minimal
- Comment complex test logic for clarity
