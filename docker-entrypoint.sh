#!/bin/bash
set -e

# Output environment variables for debugging (excluding secrets)
echo "Starting Azure Data Explorer MCP Server in Docker..."
echo "  Cluster URL: $ADX_CLUSTER_URL"
echo "  Database: $ADX_DATABASE"

# Run the MCP server
exec /app/.venv/bin/python -m adx_mcp_server.main "$@"
