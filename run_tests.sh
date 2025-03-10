#!/bin/bash
# Script to run tests for the Azure Data Explorer MCP Server

# Make sure we're in the project root
cd "$(dirname "$0")"

# Activate the virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
elif [ -d "venv" ]; then
    source venv/bin/activate
fi

# Install development dependencies
echo "Installing development dependencies..."
uv pip install -e ".[dev]"

# Run the tests
echo "Running tests..."
if [ "$1" == "--coverage" ]; then
    # Run with coverage report
    pytest --cov=src --cov-report=term-missing
else
    # Run without coverage report
    pytest
fi

echo "Tests completed."
