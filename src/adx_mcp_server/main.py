#!/usr/bin/env python
import sys
import dotenv
import argparse
import os
import uvicorn
from fastapi import FastAPI
from adx_mcp_server.server import mcp, config, SSE_HOST, SSE_PORT, create_sse_server

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

    print(f"Azure Data Explorer configuration:")
    print(f"  Cluster: {config.cluster_url}")
    print(f"  Database: {config.database}")
    print(f"  Authentication: Using DefaultAzureCredential")
    
    return True

def create_app():
    """Create a FastAPI application for SSE mode"""
    app = FastAPI(title="Azure Data Explorer MCP Server")
    
    # Mount the SSE handler at the root path
    app.mount("/", create_sse_server(mcp))
    
    # Health check endpoint
    @app.get("/health")
    def health_check():
        return {"status": "healthy", "service": "ADX MCP Server"}
    
    return app

def run_server(transport_mode="stdio", host=None, port=None):
    """Main entry point for the Azure Data Explorer MCP Server
    
    Args:
        transport_mode (str): The transport mode to use ("stdio" or "sse")
        host (str, optional): The host to bind to in SSE mode. Defaults to SSE_HOST env var or "0.0.0.0".
        port (int, optional): The port to bind to in SSE mode. Defaults to SSE_PORT env var or 8000.
    """
    # Setup environment
    if not setup_environment():
        sys.exit(1)
    
    print("\nStarting Azure Data Explorer MCP Server...")
    
    if transport_mode == "sse":
        # Use the provided host/port or fall back to environment/defaults
        sse_host = host or SSE_HOST
        sse_port = port or SSE_PORT
        
        print(f"Running server in SSE mode on {sse_host}:{sse_port}...")
        
        # Create the FastAPI app
        app = create_app()
        
        # Start Uvicorn server
        uvicorn.run(app, host=sse_host, port=sse_port, log_level="info")
    else:
        # Default to STDIO mode
        print("Running server in STDIO mode...")
        
        # Run the server with the stdio transport
        mcp.run(transport="stdio")

if __name__ == "__main__":
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(description="Azure Data Explorer MCP Server")
    parser.add_argument(
        "--transport", 
        choices=["stdio", "sse"], 
        default="stdio",
        help="Transport mode to use (default: stdio)"
    )
    parser.add_argument(
        "--host", 
        default=None,
        help="Host to bind to in SSE mode (default: from env or 0.0.0.0)"
    )
    parser.add_argument(
        "--port", 
        type=int,
        default=None,
        help="Port to bind to in SSE mode (default: from env or 8000)"
    )
    
    args = parser.parse_args()
    
    # Run the server with the specified transport mode and options
    run_server(
        transport_mode=args.transport,
        host=args.host, 
        port=args.port
    )