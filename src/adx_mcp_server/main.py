#!/usr/bin/env python
import sys
import dotenv
import logging
from adx_mcp_server.server import mcp, config
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [adx] [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(stream=sys.stderr)]  # Log to stderr instead of stdout
)
logger = logging.getLogger("adx")

def setup_environment():
    # Check if required env vars are already set before trying to load .env
    if not os.environ.get("ADX_CLUSTER_URL") or not os.environ.get("ADX_DATABASE"):
        # Only try to load .env if needed
        dotenv.load_dotenv(verbose=False)
    
    if not config.cluster_url:
        logger.error("ADX_CLUSTER_URL environment variable is not set")
        logger.error("Please set it to your Azure Data Explorer cluster URL")
        logger.error("Example: https://youradxcluster.region.kusto.windows.net")
        return False
    
    if not config.database:
        logger.error("ADX_DATABASE environment variable is not set")
        logger.error("Please set it to your Azure Data Explorer database name")
        return False

    logger.info(f"Azure Data Explorer configuration: Cluster: {config.cluster_url}, Database: {config.database}, Auth: DefaultAzureCredential")
    
    return True

def run_server():
    """Main entry point for the Azure Data Explorer MCP Server"""
    if not setup_environment():
        sys.exit(1)
    
    logger.info("Starting Azure Data Explorer MCP Server...")
    
    mcp.run(transport="stdio")

if __name__ == "__main__":
    run_server()