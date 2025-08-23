#!/usr/bin/env python
import sys
import os
import dotenv
from adx_mcp_server.server import mcp, config, TransportType

def setup_environment():
    if dotenv.load_dotenv():
        print("Loaded environment variables from .env file")
    else:
        print("No .env file found or could not load it - using environment variables")

    if not config.cluster_url:
        print("ERROR: ADX_CLUSTER_URL environment variable is not set")
        print("Please set it to your Azure Data Explorer cluster URL")
        print("Example: https://youradxcluster.region.kusto.windows.net")
        return False
    
    if not config.database:
        print("ERROR: ADX_DATABASE environment variable is not set")
        print("Please set it to your Azure Data Explorer database name")
        return False

    # MCP Server configuration validation
    mcp_config = config.mcp_server_config
    if mcp_config:
        if str(mcp_config.mcp_server_transport).lower() not in TransportType.values():
            print("ERROR: Invalid MCP transport")
            print("ADX_MCP_SERVER_TRANSPORT environment variable is invalid")
            print("Please define one of these acceptable transports (http/sse/stdio)")
            print("Example: http")
            return False

        try:
            if mcp_config.mcp_bind_port:
                int(mcp_config.mcp_bind_port)
        except (TypeError, ValueError):
            print("ERROR: Invalid MCP port")
            print("ADX_MCP_BIND_PORT environment variable is invalid")
            print("Please define an integer")
            print("Example: 8080")
            return False

    print(f"Azure Data Explorer configuration:")
    print(f"  Cluster: {config.cluster_url}")
    print(f"  Database: {config.database}")
    
    # Check for Azure workload identity credentials
    tenant_id = os.environ.get('AZURE_TENANT_ID')
    client_id = os.environ.get('AZURE_CLIENT_ID')
    if tenant_id and client_id:
        print(f"  Authentication: Using WorkloadIdentityCredential")
        print(f"    Tenant ID: {tenant_id}")
        print(f"    Client ID: {client_id}")
        token_file_path = os.environ.get('ADX_TOKEN_FILE_PATH', '/var/run/secrets/azure/tokens/azure-identity-token')
        print(f"    Token File Path: {token_file_path}")
    else:
        print(f"  Authentication: Using DefaultAzureCredential")
    
    return True

def run_server():
    """Main entry point for the Azure Data Explorer MCP Server"""
    # Setup environment
    if not setup_environment():
        sys.exit(1)
    
    mcp_config = config.mcp_server_config
    transport = mcp_config.mcp_server_transport

    http_transports = [TransportType.HTTP.value, TransportType.SSE.value]
    if transport in http_transports:
        print(f"\nStarting Azure Data Explorer MCP Server...")
        print(f"Running server in {transport} mode on {mcp_config.mcp_bind_host}:{mcp_config.mcp_bind_port}")
        mcp.run(transport=transport, host=mcp_config.mcp_bind_host, port=mcp_config.mcp_bind_port)
    else:
        print(f"\nStarting Azure Data Explorer MCP Server...")
        print(f"Running server in {transport} mode...")
        mcp.run(transport=transport)

if __name__ == "__main__":
    run_server()
