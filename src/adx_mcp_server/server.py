#!/usr/bin/env python
"""
Azure Data Explorer MCP Server
Main server implementation with KQL query execution and database exploration tools.
"""

import os
import sys
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

import dotenv
import structlog
from fastmcp import FastMCP
from azure.identity import DefaultAzureCredential, WorkloadIdentityCredential
from azure.kusto.data import KustoClient, KustoConnectionStringBuilder

# Configure structured logging
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer() if os.getenv("LOG_FORMAT", "json") != "json" else structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.make_filtering_bound_logger(int(os.getenv("LOG_LEVEL", "20"))),  # 20 = INFO
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

dotenv.load_dotenv()
mcp = FastMCP("Azure Data Explorer MCP")

class TransportType(str, Enum):
    """Supported MCP server transport types."""

    STDIO = "stdio"
    HTTP = "http"
    SSE = "sse"

    @classmethod
    def values(cls) -> list[str]:
        """Get all valid transport values."""
        return [transport.value for transport in cls]

@dataclass
class MCPServerConfig:
    """Global Configuration for MCP."""
    mcp_server_transport: TransportType = None
    mcp_bind_host: str = None
    mcp_bind_port: int = None

    def __post_init__(self):
        """Validate mcp configuration."""
        if not self.mcp_server_transport:
            raise ValueError("MCP SERVER TRANSPORT is required")
        if not self.mcp_bind_host:
            raise ValueError(f"MCP BIND HOST is required")
        if not self.mcp_bind_port:
            raise ValueError(f"MCP BIND PORT is required")

@dataclass
class ADXConfig:
    cluster_url: str
    database: str
    # Optional Custom MCP Server Configuration
    mcp_server_config: Optional[MCPServerConfig] = None

config = ADXConfig(
    cluster_url=os.environ.get("ADX_CLUSTER_URL", ""),
    database=os.environ.get("ADX_DATABASE", ""),
    mcp_server_config=MCPServerConfig(
        mcp_server_transport=os.environ.get("ADX_MCP_SERVER_TRANSPORT", "stdio").lower(),
        mcp_bind_host=os.environ.get("ADX_MCP_BIND_HOST", "127.0.0.1"),
        mcp_bind_port=int(os.environ.get("ADX_MCP_BIND_PORT", "8080"))
    )
)

def get_kusto_client() -> KustoClient:
    """
    Create and configure a Kusto client with appropriate Azure credentials.

    Prioritizes WorkloadIdentityCredential when running in AKS with workload identity,
    falls back to DefaultAzureCredential for other authentication methods.

    Returns:
        KustoClient: Configured Kusto client instance
    """
    tenant_id = os.environ.get('AZURE_TENANT_ID')
    client_id = os.environ.get('AZURE_CLIENT_ID')
    token_file_path = os.environ.get('ADX_TOKEN_FILE_PATH', '/var/run/secrets/azure/tokens/azure-identity-token')

    if tenant_id and client_id:
        logger.info(
            "Using WorkloadIdentityCredential",
            client_id=client_id,
            tenant_id=tenant_id,
            token_file_path=token_file_path
        )
        try:
            credential = WorkloadIdentityCredential(
                tenant_id=tenant_id,
                client_id=client_id,
                token_file_path=token_file_path
            )
        except Exception as e:
            logger.warning(
                "Failed to initialize WorkloadIdentityCredential, falling back",
                error=str(e),
                exception_type=type(e).__name__
            )
            credential = DefaultAzureCredential()
    else:
        logger.info("Using DefaultAzureCredential (missing WorkloadIdentity credentials)")
        credential = DefaultAzureCredential()

    try:
        kcsb = KustoConnectionStringBuilder.with_azure_token_credential(
            connection_string=config.cluster_url,
            credential=credential
        )
        client = KustoClient(kcsb)
        logger.debug("Kusto client initialized successfully", cluster_url=config.cluster_url)
        return client
    except Exception as e:
        logger.error(
            "Failed to create Kusto client",
            error=str(e),
            exception_type=type(e).__name__,
            cluster_url=config.cluster_url
        )
        raise

def format_query_results(result_set) -> List[Dict[str, Any]]:
    """
    Format Kusto query results into a list of dictionaries.

    Args:
        result_set: Raw result set from KustoClient

    Returns:
        List of dictionaries with column names as keys
    """
    if not result_set or not result_set.primary_results:
        logger.debug("Empty or null result set received")
        return []

    try:
        primary_result = result_set.primary_results[0]
        columns = [col.column_name for col in primary_result.columns]

        formatted_results = []
        for row in primary_result.rows:
            record = {}
            for i, value in enumerate(row):
                record[columns[i]] = value
            formatted_results.append(record)

        logger.debug("Query results formatted", row_count=len(formatted_results), columns=columns)
        return formatted_results
    except Exception as e:
        logger.error(
            "Error formatting query results",
            error=str(e),
            exception_type=type(e).__name__
        )
        raise

@mcp.tool(description="Executes a Kusto Query Language (KQL) query against the configured Azure Data Explorer database and returns the results as a list of dictionaries.")
async def execute_query(query: str) -> List[Dict[str, Any]]:
    """Execute a KQL query against the configured ADX database."""
    logger.info("Executing KQL query", database=config.database, query_preview=query[:100])

    if not config.cluster_url or not config.database:
        logger.error("Missing ADX configuration")
        raise ValueError("Azure Data Explorer configuration is missing. Please set ADX_CLUSTER_URL and ADX_DATABASE environment variables.")

    try:
        client = get_kusto_client()
        result_set = client.execute(config.database, query)
        results = format_query_results(result_set)
        logger.info("Query executed successfully", row_count=len(results))
        return results
    except Exception as e:
        logger.error(
            "Query execution failed",
            error=str(e),
            exception_type=type(e).__name__,
            database=config.database
        )
        raise

@mcp.tool(description="Retrieves a list of all tables available in the configured Azure Data Explorer database, including their names, folders, and database associations.")
async def list_tables() -> List[Dict[str, Any]]:
    """List all tables in the configured ADX database."""
    logger.info("Listing tables", database=config.database)

    if not config.cluster_url or not config.database:
        logger.error("Missing ADX configuration")
        raise ValueError("Azure Data Explorer configuration is missing. Please set ADX_CLUSTER_URL and ADX_DATABASE environment variables.")

    try:
        client = get_kusto_client()
        query = ".show tables | project TableName, Folder, DatabaseName"
        result_set = client.execute(config.database, query)
        results = format_query_results(result_set)
        logger.info("Tables listed successfully", table_count=len(results))
        return results
    except Exception as e:
        logger.error("Failed to list tables", error=str(e), exception_type=type(e).__name__)
        raise

@mcp.tool(description="Retrieves the schema information for a specified table in the Azure Data Explorer database, including column names, data types, and other schema-related metadata.")
async def get_table_schema(table_name: str) -> List[Dict[str, Any]]:
    """Get schema information for a specific table."""
    logger.info("Getting table schema", table_name=table_name, database=config.database)

    if not config.cluster_url or not config.database:
        logger.error("Missing ADX configuration")
        raise ValueError("Azure Data Explorer configuration is missing. Please set ADX_CLUSTER_URL and ADX_DATABASE environment variables.")

    try:
        client = get_kusto_client()
        query = f"{table_name} | getschema"
        result_set = client.execute(config.database, query)
        results = format_query_results(result_set)
        logger.info("Schema retrieved successfully", table_name=table_name, column_count=len(results))
        return results
    except Exception as e:
        logger.error("Failed to get table schema", table_name=table_name, error=str(e), exception_type=type(e).__name__)
        raise

@mcp.tool(description="Retrieves a random sample of rows from the specified table in the Azure Data Explorer database. The sample_size parameter controls how many rows to return (default: 10).")
async def sample_table_data(table_name: str, sample_size: int = 10) -> List[Dict[str, Any]]:
    """Get sample data from a table."""
    logger.info("Sampling table data", table_name=table_name, sample_size=sample_size, database=config.database)

    if not config.cluster_url or not config.database:
        logger.error("Missing ADX configuration")
        raise ValueError("Azure Data Explorer configuration is missing. Please set ADX_CLUSTER_URL and ADX_DATABASE environment variables.")

    try:
        client = get_kusto_client()
        query = f"{table_name} | sample {sample_size}"
        result_set = client.execute(config.database, query)
        results = format_query_results(result_set)
        logger.info("Sample data retrieved successfully", table_name=table_name, row_count=len(results))
        return results
    except Exception as e:
        logger.error("Failed to sample table data", table_name=table_name, error=str(e), exception_type=type(e).__name__)
        raise

@mcp.tool(description="Retrieves table details including TotalRowCount, HotExtentSize")
async def get_table_details(table_name: str) -> List[Dict[str, Any]]:
    """Get detailed statistics and metadata for a table."""
    logger.info("Getting table details", table_name=table_name, database=config.database)

    if not config.cluster_url or not config.database:
        logger.error("Missing ADX configuration")
        raise ValueError("Azure Data Explorer configuration is missing. Please set ADX_CLUSTER_URL and ADX_DATABASE environment variables.")

    try:
        client = get_kusto_client()
        query = f".show table {table_name} details"
        result_set = client.execute(config.database, query)
        results = format_query_results(result_set)
        logger.info("Table details retrieved successfully", table_name=table_name)
        return results
    except Exception as e:
        logger.error("Failed to get table details", table_name=table_name, error=str(e), exception_type=type(e).__name__)
        raise


if __name__ == "__main__":
    print(f"Starting Azure Data Explorer MCP Server...")
    mcp.run()
