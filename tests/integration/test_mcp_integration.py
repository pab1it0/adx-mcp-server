#!/usr/bin/env python

import pytest
import asyncio
import json
from unittest.mock import patch, MagicMock
from io import StringIO
import sys

from server import mcp, config
import server
from main import setup_environment

class TestMCPIntegration:
    @pytest.fixture
    def mock_kusto_integration(self):
        """Create a more comprehensive mock for integration testing."""
        with patch('server.get_kusto_client') as mock_get_client:
            # Create a mock client
            mock_client = MagicMock()
            
            # Helper function to create table lists
            def create_table_result():
                mock_result = MagicMock()
                primary_result = MagicMock()
                
                # Columns for table list
                col1 = MagicMock()
                col1.column_name = "TableName"
                col2 = MagicMock()
                col2.column_name = "Folder"
                col3 = MagicMock()
                col3.column_name = "DatabaseName"
                
                primary_result.columns = [col1, col2, col3]
                primary_result.rows = [
                    ["logs", "", "testdb"],
                    ["users", "User Data", "testdb"],
                    ["metrics", "System", "testdb"]
                ]
                
                mock_result.primary_results = [primary_result]
                return mock_result
            
            # Helper function to create schema results
            def create_schema_result(table_name):
                mock_result = MagicMock()
                primary_result = MagicMock()
                
                # Columns for schema
                col1 = MagicMock()
                col1.column_name = "ColumnName"
                col2 = MagicMock()
                col2.column_name = "ColumnType"
                
                primary_result.columns = [col1, col2]
                
                if table_name == "logs":
                    primary_result.rows = [
                        ["Timestamp", "datetime"],
                        ["Level", "string"],
                        ["Message", "string"],
                        ["Source", "string"]
                    ]
                elif table_name == "users":
                    primary_result.rows = [
                        ["UserId", "string"],
                        ["Name", "string"],
                        ["Email", "string"],
                        ["CreatedAt", "datetime"]
                    ]
                elif table_name == "metrics":
                    primary_result.rows = [
                        ["Timestamp", "datetime"],
                        ["MetricName", "string"],
                        ["Value", "real"],
                        ["Tags", "dynamic"]
                    ]
                else:
                    primary_result.rows = []
                
                mock_result.primary_results = [primary_result]
                return mock_result
            
            # Helper function to create sample data results
            def create_sample_data(table_name, sample_size=10):
                mock_result = MagicMock()
                primary_result = MagicMock()
                
                if table_name == "logs":
                    col1 = MagicMock()
                    col1.column_name = "Timestamp"
                    col2 = MagicMock()
                    col2.column_name = "Level"
                    col3 = MagicMock()
                    col3.column_name = "Message"
                    col4 = MagicMock()
                    col4.column_name = "Source"
                    
                    primary_result.columns = [col1, col2, col3, col4]
                    primary_result.rows = [
                        ["2023-01-01T00:00:00Z", "Info", "Server started", "WebService"],
                        ["2023-01-01T00:05:00Z", "Error", "Database connection failed", "DataProcessor"]
                    ]
                else:
                    # Default empty result
                    primary_result.columns = []
                    primary_result.rows = []
                
                mock_result.primary_results = [primary_result]
                return mock_result
            
            # Configure the mock execute function to return different results based on the query
            def mock_execute(database, query):
                if ".show tables" in query:
                    return create_table_result()
                elif "getschema" in query:
                    table_name = query.split("table ")[1].split(" ")[0]
                    return create_schema_result(table_name)
                elif "sample" in query:
                    table_name = query.split(" ")[0]
                    return create_sample_data(table_name)
                else:
                    # Default custom query result
                    mock_result = MagicMock()
                    primary_result = MagicMock()
                    
                    # Default columns and rows for custom query
                    col1 = MagicMock()
                    col1.column_name = "Result"
                    
                    primary_result.columns = [col1]
                    primary_result.rows = [["Custom query result"]]
                    
                    mock_result.primary_results = [primary_result]
                    return mock_result
            
            mock_client.execute.side_effect = mock_execute
            mock_get_client.return_value = mock_client
            
            yield mock_client
    
    @pytest.mark.asyncio
    async def test_tool_execution_flow(self, monkeypatch, mock_kusto_integration):
        """Test direct execution of the list_tables tool."""
        # Save original config values
        original_cluster = config.cluster_url
        original_database = config.database
        
        try:
            # Set test configuration
            config.cluster_url = "https://testcluster.region.kusto.windows.net"
            config.database = "testdb"
            
            # Import the tool function
            from server import list_tables
            
            # Execute the tool directly
            result = await list_tables()
            
            # Verify the response
            assert len(result) == 3
            table_names = [table["TableName"] for table in result]
            assert "logs" in table_names
            assert "users" in table_names
            assert "metrics" in table_names
        finally:
            # Restore original config
            config.cluster_url = original_cluster
            config.database = original_database
    
    @pytest.mark.asyncio
    async def test_table_schema_flow(self, monkeypatch, mock_kusto_integration):
        """Test direct execution of the get_table_schema tool."""
        # Save original config values
        original_cluster = config.cluster_url
        original_database = config.database
        
        try:
            # Set test configuration
            config.cluster_url = "https://testcluster.region.kusto.windows.net"
            config.database = "testdb"
            
            # Import the tool function
            from server import get_table_schema
            
            # Execute the tool directly
            result = await get_table_schema("logs")
            
            # Verify the response structure
            assert len(result) == 4  # 4 columns in the logs table
            column_names = [col["ColumnName"] for col in result]
            assert "Timestamp" in column_names
            assert "Level" in column_names
            assert "Message" in column_names
            assert "Source" in column_names
        finally:
            # Restore original config
            config.cluster_url = original_cluster
            config.database = original_database
    
    @pytest.mark.asyncio
    async def test_sample_data_flow(self, monkeypatch, mock_kusto_integration):
        """Test direct execution of the sample_table_data tool."""
        # Save original config values
        original_cluster = config.cluster_url
        original_database = config.database
        
        try:
            # Set test configuration
            config.cluster_url = "https://testcluster.region.kusto.windows.net"
            config.database = "testdb"
            
            # Import the tool function
            from server import sample_table_data
            
            # Execute the tool directly
            result = await sample_table_data("logs", 2)
            
            # Verify the response structure
            assert len(result) == 2  # 2 sample rows
            assert result[0]["Level"] == "Info"
            assert result[1]["Level"] == "Error"
            assert "Server started" in result[0]["Message"]
        finally:
            # Restore original config
            config.cluster_url = original_cluster
            config.database = original_database
