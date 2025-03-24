#!/usr/bin/env python

import os
import pytest
import json
from unittest.mock import patch, MagicMock, AsyncMock
import asyncio

# Import the modules to test
from adx_mcp_server import server
from adx_mcp_server.server import execute_query, get_kusto_client

class TestTokenAuthentication:
    def test_get_kusto_client_with_token_credential(self):
        """Test that get_kusto_client uses DefaultAzureCredential."""
        with patch('adx_mcp_server.server.DefaultAzureCredential') as mock_credential:
            # Create a mock token credential
            mock_token_cred = MagicMock()
            mock_credential.return_value = mock_token_cred
            
            # Also patch KustoConnectionStringBuilder.with_azure_token_credential
            with patch('adx_mcp_server.server.KustoConnectionStringBuilder.with_azure_token_credential') as mock_kcsb:
                # Create a mock connection string builder
                mock_conn_builder = MagicMock()
                mock_kcsb.return_value = mock_conn_builder
                
                # Patch KustoClient constructor
                with patch('adx_mcp_server.server.KustoClient') as mock_client_constructor:
                    # Create a mock client
                    mock_client = MagicMock()
                    mock_client_constructor.return_value = mock_client
                    
                    # Call the function
                    result = get_kusto_client()
                    
                    # Verify DefaultAzureCredential was created
                    mock_credential.assert_called_once()
                    
                    # Verify the connection string builder was used with the token credential
                    mock_kcsb.assert_called_once()
                    args, kwargs = mock_kcsb.call_args
                    assert kwargs['credential'] == mock_token_cred
                    
                    # Verify the KustoClient was created with the connection string builder
                    mock_client_constructor.assert_called_once_with(mock_conn_builder)
                    
                    # Verify the result is the mocked client
                    assert result == mock_client
    
    @pytest.mark.asyncio
    async def test_execute_query_with_token_credential(self):
        """Test that execute_query ultimately uses the token credential."""
        # Configure a known database value
        original_cluster_url = server.config.cluster_url
        original_database = server.config.database
        
        server.config.cluster_url = "https://testcluster.kusto.windows.net"
        server.config.database = "testdb"
        
        try:
            # Patch get_kusto_client to return a mock client
            with patch('adx_mcp_server.server.get_kusto_client') as mock_get_client:
                # Create a mock client
                mock_client = MagicMock()
                
                # Setup the mock client's execute method to return a mock result_set
                mock_result_set = MagicMock()
                mock_primary_result = MagicMock()
                
                # Set up columns
                column = MagicMock()
                column.column_name = "Column"
                mock_primary_result.columns = [column]
                
                # Set up rows
                mock_primary_result.rows = [["Value"]]
                
                mock_result_set.primary_results = [mock_primary_result]
                mock_client.execute.return_value = mock_result_set
                
                mock_get_client.return_value = mock_client
                
                # Call execute_query
                result = await execute_query("test query")
                
                # Verify get_kusto_client was called
                mock_get_client.assert_called_once()
                
                # Verify execute was called with the right parameters
                mock_client.execute.assert_called_once_with("testdb", "test query")
                
                # Verify the result is properly formatted
                assert len(result) == 1
                assert result[0]["Column"] == "Value"
        finally:
            # Restore original values
            server.config.cluster_url = original_cluster_url
            server.config.database = original_database
