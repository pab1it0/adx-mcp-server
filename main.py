#!/usr/bin/env python
"""
Azure Data Explorer MCP Server
----------------------------
An MCP server for interacting with Azure Data Explorer.

This script initializes and runs the Azure Data Explorer MCP server.
"""
import sys
import dotenv

# Import the MCP server implementation
from server import mcp, config

def setup_environment():
    """Setup the environment for the ADX MCP server"""
    # Load environment variables from .env file
    if dotenv.load_dotenv():
        print("Loaded environment variables from .env file")
    else:
        print("No .env file found or could not load it - using environment variables")

    # Check if the required environment variables are set
    if not config.cluster_url:
        print("ERROR: ADX_CLUSTER_URL environment variable is not set")
        print("Please set it to your Azure Data Explorer cluster URL")
        print("Example: https://youradxcluster.region.kusto.windows.net")
        return False
    
    if not config.database:
        print("ERROR: ADX_DATABASE environment variable is not set")
        print("Please set it to your Azure Data Explorer database name")
        return False

    print(f"Azure Data Explorer configuration:")
    print(f"  Cluster: {config.cluster_url}")
    print(f"  Database: {config.database}")
    
    # Authentication method
    if all([config.tenant_id, config.client_id, config.client_secret]):
        print("Authentication: Using client credentials")
    else:
        print("Authentication: Using default Azure credentials")
        print("  (Azure CLI, managed identity, or Visual Studio Code)")
    
    return True

def main():
    """Main entry point for the Azure Data Explorer MCP Server"""
    # Setup environment
    if not setup_environment():
        sys.exit(1)
    
    print("\nStarting Azure Data Explorer MCP Server...")
    print("Running server in standard mode...")
    
    # Run the server with the stdio transport
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
