#!/usr/bin/env python
"""
Azure Data Explorer MCP Server - Application Entry Point
Handles environment setup, configuration validation, and server startup.
"""

import sys
import os
import dotenv
import structlog

from adx_mcp_server.server import mcp, config, TransportType

logger = structlog.get_logger()

def setup_environment() -> bool:
    """
    Setup and validate the environment configuration.

    Returns:
        bool: True if configuration is valid, False otherwise
    """
    if dotenv.load_dotenv():
        logger.info("Loaded environment variables from .env file")
    else:
        logger.info("No .env file found, using system environment variables")

    # Validate required configuration
    if not config.cluster_url:
        logger.error(
            "Missing required configuration",
            variable="ADX_CLUSTER_URL",
            example="https://youradxcluster.region.kusto.windows.net"
        )
        return False

    if not config.database:
        logger.error(
            "Missing required configuration",
            variable="ADX_DATABASE"
        )
        return False

    # Validate MCP server configuration
    mcp_config = config.mcp_server_config
    if mcp_config:
        if str(mcp_config.mcp_server_transport).lower() not in TransportType.values():
            logger.error(
                "Invalid MCP transport",
                transport=mcp_config.mcp_server_transport,
                valid_transports=TransportType.values()
            )
            return False

        try:
            if mcp_config.mcp_bind_port:
                int(mcp_config.mcp_bind_port)
        except (TypeError, ValueError):
            logger.error(
                "Invalid MCP port",
                port=mcp_config.mcp_bind_port,
                expected_type="integer"
            )
            return False

    # Log configuration summary
    logger.info(
        "Azure Data Explorer configuration loaded",
        cluster_url=config.cluster_url,
        database=config.database
    )

    # Check for Azure workload identity credentials
    tenant_id = os.environ.get('AZURE_TENANT_ID')
    client_id = os.environ.get('AZURE_CLIENT_ID')
    if tenant_id and client_id:
        token_file_path = os.environ.get('ADX_TOKEN_FILE_PATH', '/var/run/secrets/azure/tokens/azure-identity-token')
        logger.info(
            "Workload Identity credentials detected",
            tenant_id=tenant_id,
            client_id=client_id,
            token_file_path=token_file_path
        )
    else:
        logger.info("Using DefaultAzureCredential for authentication")

    return True

def run_server():
    """Main entry point for the Azure Data Explorer MCP Server."""
    logger.info("Starting Azure Data Explorer MCP Server")

    # Setup and validate environment
    if not setup_environment():
        logger.error("Environment setup failed, exiting")
        sys.exit(1)

    mcp_config = config.mcp_server_config
    transport = mcp_config.mcp_server_transport

    http_transports = [TransportType.HTTP.value, TransportType.SSE.value]
    if transport in http_transports:
        logger.info(
            "Starting server with network transport",
            transport=transport,
            host=mcp_config.mcp_bind_host,
            port=mcp_config.mcp_bind_port
        )
        mcp.run(transport=transport, host=mcp_config.mcp_bind_host, port=mcp_config.mcp_bind_port)
    else:
        logger.info("Starting server with stdio transport", transport=transport)
        mcp.run(transport=transport)

if __name__ == "__main__":
    run_server()
