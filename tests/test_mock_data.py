#!/usr/bin/env python

import pytest
import json
from unittest.mock import patch, MagicMock
from adx_mcp_server import server
from adx_mcp_server.server import execute_query

class TestWithMockData:
    @pytest.fixture
    def mock_kusto_real_data(self):
        """Create mock Kusto responses with realistic data."""
        with patch('adx_mcp_server.server.get_kusto_client') as mock_get_client:
            mock_client = MagicMock()
            
            # Create a sample log data that looks like real data
            def create_log_data():
                logs_data = {
                    "primary_results": [
                        {
                            "columns": [
                                {"column_name": "Timestamp", "data_type": "datetime"},
                                {"column_name": "Level", "data_type": "string"},
                                {"column_name": "Message", "data_type": "string"},
                                {"column_name": "Source", "data_type": "string"},
                                {"column_name": "ApplicationId", "data_type": "string"},
                                {"column_name": "Environment", "data_type": "string"},
                                {"column_name": "Duration", "data_type": "timespan"},
                                {"column_name": "Properties", "data_type": "dynamic"}
                            ],
                            "rows": [
                                ["2023-01-01T10:00:00Z", "Info", "User logged in", "AuthService", "app-123", "Production", "00:00:00.125", {"userId": "user1", "ipAddress": "192.168.1.1"}],
                                ["2023-01-01T10:05:32Z", "Warning", "High latency detected", "APIGateway", "app-123", "Production", "00:00:02.341", {"endpoint": "/api/data", "latency": 2341}],
                                ["2023-01-01T10:10:15Z", "Error", "Database connection timeout", "DataService", "app-123", "Production", "00:00:30.000", {"database": "userdb", "operation": "query"}],
                                ["2023-01-01T10:15:45Z", "Info", "Cache refreshed", "CacheService", "app-123", "Production", "00:00:05.132", {"cacheSize": 1024, "itemCount": 532}],
                                ["2023-01-01T10:20:12Z", "Info", "Authentication succeeded", "AuthService", "app-123", "Production", "00:00:00.087", {"userId": "user2", "method": "oauth"}]
                            ]
                        }
                    ]
                }
                
                # Convert the dictionary to a proper MagicMock structure
                mock_result = self._create_mock_from_data(logs_data)
                return mock_result
            
            # Configure the execute method to return our mock data
            mock_client.execute.return_value = create_log_data()
            mock_get_client.return_value = mock_client
            
            yield mock_client
    
    def _create_mock_from_data(self, data_dict):
        """Helper method to create a proper mock structure from a dictionary."""
        mock_result = MagicMock()
        
        # Create primary results
        mock_primary_results = []
        for primary_result_data in data_dict["primary_results"]:
            mock_primary_result = MagicMock()
            
            # Create columns
            mock_columns = []
            for column_data in primary_result_data["columns"]:
                mock_column = MagicMock()
                mock_column.column_name = column_data["column_name"]
                mock_column.data_type = column_data["data_type"]
                mock_columns.append(mock_column)
            
            mock_primary_result.columns = mock_columns
            mock_primary_result.rows = primary_result_data["rows"]
            mock_primary_results.append(mock_primary_result)
        
        mock_result.primary_results = mock_primary_results
        return mock_result
    
    @pytest.mark.asyncio
    async def test_execute_query_with_realistic_data(self, mock_kusto_real_data):
        """Test execute_query tool with a realistic mock dataset."""
        # Save original config values
        original_cluster = server.config.cluster_url
        original_database = server.config.database
        
        try:
            # Set test configuration
            server.config.cluster_url = "https://testcluster.region.kusto.windows.net"
            server.config.database = "testdb"
            
            # Execute a query
            query = "logs | where Level == 'Error' | project Timestamp, Message, Source"
            result = await execute_query(query)
            
            # Verify we got properly formatted results
            assert len(result) == 5  # All 5 rows should be returned
            
            # Check specific fields
            assert "Timestamp" in result[0]
            assert "Level" in result[0]
            assert "Message" in result[0]
            assert "Source" in result[0]
            assert "Properties" in result[0]
            
            # Check dynamic property handling
            assert isinstance(result[0]["Properties"], dict)
            assert "userId" in result[0]["Properties"]
            
            # Check data types
            assert isinstance(result[0]["Timestamp"], str)
            assert isinstance(result[0]["Duration"], str)
            
            # Check specific error record
            error_records = [r for r in result if r["Level"] == "Error"]
            assert len(error_records) == 1
            assert "Database connection timeout" in error_records[0]["Message"]
        finally:
            # Restore original config
            server.config.cluster_url = original_cluster
            server.config.database = original_database
