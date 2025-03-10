#!/usr/bin/env python
"""
Azure Data Explorer MCP Server
----------------------------
An MCP server for interacting with Azure Data Explorer.
"""

import os
import json
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass

import dotenv
from mcp.server.fastmcp import FastMCP
from azure.identity import ClientSecretCredential
from azure.kusto.data import KustoClient, KustoConnectionStringBuilder

# Load environment variables from .env file if it exists
dotenv.load_dotenv()

# Create an MCP server
mcp = FastMCP("Azure Data Explorer MCP")

# Configuration for Azure Data Explorer
@dataclass
class ADXConfig:
    """Configuration for Azure Data Explorer client"""
    cluster_url: str
    database: str
    # Optional credentials
    tenant_id: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None

# Global configuration
config = ADXConfig(
    cluster_url=os.environ.get("ADX_CLUSTER_URL", ""),
    database=os.environ.get("ADX_DATABASE", ""),
    tenant_id=os.environ.get("AZURE_TENANT_ID", ""),
    client_id=os.environ.get("AZURE_CLIENT_ID", ""),
    client_secret=os.environ.get("AZURE_CLIENT_SECRET", ""),
)

def get_kusto_client() -> KustoClient:
    """Create and return a KustoClient instance using client credentials"""
    
    if not all([config.tenant_id, config.client_id, config.client_secret]):
        raise ValueError("Client credentials are missing. Please set AZURE_TENANT_ID, AZURE_CLIENT_ID, and AZURE_CLIENT_SECRET environment variables.")
        
    # Use client secret credential
    credential = ClientSecretCredential(
        tenant_id=config.tenant_id,
        client_id=config.client_id,
        client_secret=config.client_secret
    )
    # Create connection string builder with AAD
    kcsb = KustoConnectionStringBuilder.with_aad_application_key_authentication(
        connection_string=config.cluster_url,
        aad_app_id=config.client_id,
        app_key=config.client_secret,
        authority_id=config.tenant_id
    )
    return KustoClient(kcsb)

# Helper function to format query results
def format_query_results(result_set) -> List[Dict[str, Any]]:
    """Convert Kusto query results to a list of dictionaries"""
    if not result_set or not result_set.primary_results:
        return []
    
    primary_result = result_set.primary_results[0]
    columns = [col.column_name for col in primary_result.columns]
    
    formatted_results = []
    for row in primary_result.rows:
        record = {}
        for i, value in enumerate(row):
            record[columns[i]] = value
        formatted_results.append(record)
    
    return formatted_results

@mcp.tool()
async def execute_query(query: str) -> List[Dict[str, Any]]:
    """
    Execute a KQL query against Azure Data Explorer
    
    Args:
        query: KQL query to execute
    
    Returns:
        List of result rows as dictionaries
    """
    if not config.cluster_url or not config.database:
        raise ValueError("Azure Data Explorer configuration is missing. Please set ADX_CLUSTER_URL and ADX_DATABASE environment variables.")
    
    client = get_kusto_client()
    result_set = client.execute(config.database, query)
    return format_query_results(result_set)

@mcp.tool()
async def list_tables() -> List[Dict[str, Any]]:
    """
    List all tables in the configured database
    
    Returns:
        List of table information dictionaries
    """
    if not config.cluster_url or not config.database:
        raise ValueError("Azure Data Explorer configuration is missing. Please set ADX_CLUSTER_URL and ADX_DATABASE environment variables.")
    
    client = get_kusto_client()
    query = ".show tables | project TableName, Folder, DatabaseName"
    result_set = client.execute(config.database, query)
    return format_query_results(result_set)

@mcp.tool()
async def get_table_schema(table_name: str) -> List[Dict[str, Any]]:
    """
    Get the schema for a specific table
    
    Args:
        table_name: Name of the table to get schema for
    
    Returns:
        List of column information dictionaries
    """
    if not config.cluster_url or not config.database:
        raise ValueError("Azure Data Explorer configuration is missing. Please set ADX_CLUSTER_URL and ADX_DATABASE environment variables.")
    
    client = get_kusto_client()
    query = f".show table {table_name} schema as json"
    result_set = client.execute(config.database, query)
    
    # This query returns a JSON string in the first cell
    if not result_set.primary_results or not result_set.primary_results[0].rows:
        return []
    
    schema_json = result_set.primary_results[0].rows[0][0]
    schema_data = json.loads(schema_json)
    
    return schema_data.get("Columns", [])

@mcp.tool()
async def sample_table_data(table_name: str, sample_size: int = 10) -> List[Dict[str, Any]]:
    """
    Get sample data from a table
    
    Args:
        table_name: Name of the table to sample
        sample_size: Number of records to sample (default: 10)
    
    Returns:
        List of sample records
    """
    if not config.cluster_url or not config.database:
        raise ValueError("Azure Data Explorer configuration is missing. Please set ADX_CLUSTER_URL and ADX_DATABASE environment variables.")
    
    client = get_kusto_client()
    query = f"{table_name} | sample {sample_size}"
    result_set = client.execute(config.database, query)
    return format_query_results(result_set)

if __name__ == "__main__":
    print(f"Starting Azure Data Explorer MCP Server...")
    mcp.run()
