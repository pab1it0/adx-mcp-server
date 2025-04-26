#!/usr/bin/env python

import os
import json
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass

import dotenv
from mcp.server.fastmcp import FastMCP
from azure.identity import DefaultAzureCredential, WorkloadIdentityCredential
from azure.kusto.data import KustoClient, KustoConnectionStringBuilder

dotenv.load_dotenv()
mcp = FastMCP("Azure Data Explorer MCP")

@dataclass
class ADXConfig:
    cluster_url: str
    database: str

config = ADXConfig(
    cluster_url=os.environ.get("ADX_CLUSTER_URL", ""),
    database=os.environ.get("ADX_DATABASE", ""),
)

def get_kusto_client() -> KustoClient:
    # Get tenant and client IDs from environment variables
    tenant_id = os.environ.get('AZURE_TENANT_ID')
    client_id = os.environ.get('AZURE_CLIENT_ID')
    token_file_path = os.environ.get('ADX_TOKEN_FILE_PATH', '/var/run/secrets/azure/tokens/azure-identity-token')
    
    # Check if we have the necessary credentials for WorkloadIdentityCredential
    if tenant_id and client_id:
        print(f"Using WorkloadIdentityCredential with client_id: {client_id}")
        try:
            # Use WorkloadIdentityCredential as the default option
            credential = WorkloadIdentityCredential(
                tenant_id=tenant_id,
                client_id=client_id,
                token_file_path=token_file_path
            )
        except Exception as e:
            print(f"Error initializing WorkloadIdentityCredential: {str(e)}")
            print("Falling back to DefaultAzureCredential")
            credential = DefaultAzureCredential()
    else:
        # Fall back to DefaultAzureCredential if tenant_id or client_id is missing
        print("Missing tenant_id or client_id, using DefaultAzureCredential")
        credential = DefaultAzureCredential()
    
    kcsb = KustoConnectionStringBuilder.with_azure_token_credential(
        connection_string=config.cluster_url,
        credential=credential
    )
    return KustoClient(kcsb)

def format_query_results(result_set) -> List[Dict[str, Any]]:
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

@mcp.tool(description="Executes a Kusto Query Language (KQL) query against the configured Azure Data Explorer database and returns the results as a list of dictionaries.")
async def execute_query(query: str) -> List[Dict[str, Any]]:
    if not config.cluster_url or not config.database:
        raise ValueError("Azure Data Explorer configuration is missing. Please set ADX_CLUSTER_URL and ADX_DATABASE environment variables.")
    
    client = get_kusto_client()
    result_set = client.execute(config.database, query)
    return format_query_results(result_set)

@mcp.tool(description="Retrieves a list of all tables available in the configured Azure Data Explorer database, including their names, folders, and database associations.")
async def list_tables() -> List[Dict[str, Any]]:
    if not config.cluster_url or not config.database:
        raise ValueError("Azure Data Explorer configuration is missing. Please set ADX_CLUSTER_URL and ADX_DATABASE environment variables.")
    
    client = get_kusto_client()
    query = ".show tables | project TableName, Folder, DatabaseName"
    result_set = client.execute(config.database, query)
    return format_query_results(result_set)

@mcp.tool(description="Retrieves the schema information for a specified table in the Azure Data Explorer database, including column names, data types, and other schema-related metadata.")
async def get_table_schema(table_name: str) -> List[Dict[str, Any]]:
    if not config.cluster_url or not config.database:
        raise ValueError("Azure Data Explorer configuration is missing. Please set ADX_CLUSTER_URL and ADX_DATABASE environment variables.")
    
    client = get_kusto_client()
    query = f"{table_name} | getschema"
    result_set = client.execute(config.database, query)
    return format_query_results(result_set)

@mcp.tool(description="Retrieves a random sample of rows from the specified table in the Azure Data Explorer database. The sample_size parameter controls how many rows to return (default: 10).")
async def sample_table_data(table_name: str, sample_size: int = 10) -> List[Dict[str, Any]]:
    if not config.cluster_url or not config.database:
        raise ValueError("Azure Data Explorer configuration is missing. Please set ADX_CLUSTER_URL and ADX_DATABASE environment variables.")
    
    client = get_kusto_client()
    query = f"{table_name} | sample {sample_size}"
    result_set = client.execute(config.database, query)
    return format_query_results(result_set)

@mcp.tool(description="Retrieves table details including TotalRowCount, HotExtentSize")
async def get_table_details(table_name: str) -> List[Dict[str, Any]]:
    if not config.cluster_url or not config.database:
        raise ValueError("Azure Data Explorer configuration is missing. Please set ADX_CLUSTER_URL and ADX_DATABASE environment variables.")
    
    client = get_kusto_client()
    query = f".show table {table_name} details"
    result_set = client.execute(config.database, query)
    return format_query_results(result_set)


if __name__ == "__main__":
    print(f"Starting Azure Data Explorer MCP Server...")
    mcp.run()
