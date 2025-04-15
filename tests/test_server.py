#!/usr/bin/env python

import os
import pytest
import json
from unittest.mock import patch, MagicMock, AsyncMock
import asyncio

# Import the modules to test
from adx_mcp_server import server
from adx_mcp_server.server import execute_query, list_tables, get_table_schema, sample_table_data

class TestServerTools:
    @pytest.mark.asyncio
    async def test_execute_query(self, monkeypatch):
        """Test the execute_query tool."""
        # Configure a known database value
        original_database = server.config.database
        server.config.database = "testdb"
        
        try:
            with patch('adx_mcp_server.server.get_kusto_client') as mock_get_client:
                # Create mock client and result
                mock_client = MagicMock()
                
                # Set up mock response
                mock_result_set = MagicMock()
                primary_result = MagicMock()
                
                # Create a column structure similar to what KustoClient would return
                column1 = MagicMock()
                column1.column_name = "Column1"
                column2 = MagicMock()
                column2.column_name = "Column2"
                
                primary_result.columns = [column1, column2]
                primary_result.rows = [
                    ["Value1", 1],
                    ["Value2", 2]
                ]
                
                mock_result_set.primary_results = [primary_result]
                mock_client.execute.return_value = mock_result_set
                
                mock_get_client.return_value = mock_client
                
                # Execute the query
                test_query = "test query"
                result = await execute_query(test_query)
                
                # Manually verify the call arguments
                assert mock_client.execute.call_count == 1
                args, kwargs = mock_client.execute.call_args
                assert args[0] == "testdb"  # First arg should be database
                assert args[1] == test_query  # Second arg should be query
                
                # Check result structure
                assert len(result) == 2
                assert result[0]["Column1"] == "Value1"
                assert result[0]["Column2"] == 1
                assert result[1]["Column1"] == "Value2"
                assert result[1]["Column2"] == 2
        finally:
            # Restore the original database value
            server.config.database = original_database
    
    @pytest.mark.asyncio
    async def test_list_tables(self, monkeypatch):
        """Test the list_tables tool."""
        # Configure a known database value
        original_database = server.config.database
        server.config.database = "testdb"
        
        try:
            with patch('adx_mcp_server.server.get_kusto_client') as mock_get_client:
                # Create mock client and result
                mock_client = MagicMock()
                
                # Set up mock response
                mock_result_set = MagicMock()
                primary_result = MagicMock()
                
                # Create columns for table list
                col1 = MagicMock()
                col1.column_name = "TableName"
                col2 = MagicMock()
                col2.column_name = "Folder"
                col3 = MagicMock()
                col3.column_name = "DatabaseName"
                
                primary_result.columns = [col1, col2, col3]
                primary_result.rows = [
                    ["table1", "folder1", "testdb"],
                    ["table2", "folder2", "testdb"]
                ]
                
                mock_result_set.primary_results = [primary_result]
                mock_client.execute.return_value = mock_result_set
                
                mock_get_client.return_value = mock_client
                
                # Execute the query
                result = await list_tables()
                
                # Manually verify the execute call
                assert mock_client.execute.call_count == 1
                args, kwargs = mock_client.execute.call_args
                assert args[0] == "testdb"  # First arg should be database
                assert ".show tables" in args[1]  # Second arg should contain the query
                
                # Check result structure
                assert len(result) == 2
                assert result[0]["TableName"] == "table1"
                assert result[1]["TableName"] == "table2"
        finally:
            # Restore the original database value
            server.config.database = original_database
    
    @pytest.mark.asyncio
    async def test_get_table_schema(self, monkeypatch):
        """Test the get_table_schema tool."""
        # Configure a known database value
        original_database = server.config.database
        server.config.database = "testdb"
        
        try:
            with patch('adx_mcp_server.server.get_kusto_client') as mock_get_client:
                # Create mock client and result
                mock_client = MagicMock()
                
                # Set up mock response
                mock_result_set = MagicMock()
                primary_result = MagicMock()
                
                # Create columns for schema
                col1 = MagicMock()
                col1.column_name = "ColumnName"
                col2 = MagicMock()
                col2.column_name = "ColumnType"
                
                primary_result.columns = [col1, col2]
                primary_result.rows = [
                    ["id", "string"],
                    ["value", "double"]
                ]
                
                mock_result_set.primary_results = [primary_result]
                mock_client.execute.return_value = mock_result_set
                
                mock_get_client.return_value = mock_client
                
                # Execute the query
                table_name = "test_table"
                result = await get_table_schema(table_name)
                
                # Manually verify the execute call
                assert mock_client.execute.call_count == 1
                args, kwargs = mock_client.execute.call_args
                assert args[0] == "testdb"  # First arg should be database
                assert f"{table_name}" in args[1]  # Second arg should contain the table name
                assert "getschema" in args[1]  # Second arg should contain the getschema command
                
                # Check result structure
                assert len(result) == 2
                assert result[0]["ColumnName"] == "id"
                assert result[0]["ColumnType"] == "string"
                assert result[1]["ColumnName"] == "value"
                assert result[1]["ColumnType"] == "double"
        finally:
            # Restore the original database value
            server.config.database = original_database
    
    @pytest.mark.asyncio
    async def test_sample_table_data(self, monkeypatch):
        """Test the sample_table_data tool."""
        # Configure a known database value
        original_database = server.config.database
        server.config.database = "testdb"
        
        try:
            with patch('adx_mcp_server.server.get_kusto_client') as mock_get_client:
                # Create mock client and result
                mock_client = MagicMock()
                
                # Set up mock response
                mock_result_set = MagicMock()
                primary_result = MagicMock()
                
                # Create columns for sample data
                col1 = MagicMock()
                col1.column_name = "id"
                col2 = MagicMock()
                col2.column_name = "value"
                
                primary_result.columns = [col1, col2]
                primary_result.rows = [
                    ["row1", 100],
                    ["row2", 200]
                ]
                
                mock_result_set.primary_results = [primary_result]
                mock_client.execute.return_value = mock_result_set
                
                mock_get_client.return_value = mock_client
                
                # Execute the query
                table_name = "test_table"
                sample_size = 5
                result = await sample_table_data(table_name, sample_size)
                
                # Manually verify the execute call
                assert mock_client.execute.call_count == 1
                args, kwargs = mock_client.execute.call_args
                assert args[0] == "testdb"  # First arg should be database
                assert table_name in args[1]  # Second arg should contain the table name
                assert f"sample {sample_size}" in args[1]  # Second arg should contain the sample command
                
                # Check result structure
                assert len(result) == 2
                assert result[0]["id"] == "row1"
                assert result[0]["value"] == 100
                assert result[1]["id"] == "row2"
                assert result[1]["value"] == 200
        finally:
            # Restore the original database value
            server.config.database = original_database
    
    @pytest.mark.asyncio
    async def test_missing_config_cluster_url(self, monkeypatch):
        """Test that tools handle missing configuration."""
        # Directly modify the server.config object
        original_cluster_url = server.config.cluster_url
        original_database = server.config.database
        
        try:
            # Set empty values for testing
            server.config.cluster_url = ""
            server.config.database = ""
            
            with pytest.raises(ValueError) as excinfo:
                await execute_query("test query")
            
            assert "Azure Data Explorer configuration is missing" in str(excinfo.value)
        finally:
            # Restore original values
            server.config.cluster_url = original_cluster_url
            server.config.database = original_database
    
    @pytest.mark.asyncio
    @patch('adx_mcp_server.server.DefaultAzureCredential')
    @patch('adx_mcp_server.server.KustoConnectionStringBuilder.with_azure_token_credential')
    async def test_token_credential_error(self, mock_kcsb, mock_credential, monkeypatch):
        """Test that get_kusto_client handles token credential errors."""
        # Make sure we have valid cluster and database 
        original_cluster_url = server.config.cluster_url
        original_database = server.config.database
        
        try:
            server.config.cluster_url = "https://testcluster.region.kusto.windows.net"
            server.config.database = "testdb"
            
            # Set up the mocks to simulate a token credential error
            mock_credential.side_effect = Exception("Token credential error")
            
            with pytest.raises(Exception) as excinfo:
                await execute_query("test query")
            
            # Verify the error was from the credential
            assert "Token credential error" in str(excinfo.value)
            
            # Verify DefaultAzureCredential was attempted
            mock_credential.assert_called_once()
            
            # Verify KustoConnectionStringBuilder.with_azure_token_credential was NOT called
            # since the credential creation failed
            mock_kcsb.assert_not_called()
        finally:
            # Restore original values
            server.config.cluster_url = original_cluster_url
            server.config.database = original_database
    
    def test_format_query_results_empty(self):
        """Test that format_query_results handles empty results."""
        mock_result_set = MagicMock()
        mock_result_set.primary_results = []
        
        result = server.format_query_results(mock_result_set)
        assert result == []
        
        # Test with None
        result = server.format_query_results(None)
        assert result == []
