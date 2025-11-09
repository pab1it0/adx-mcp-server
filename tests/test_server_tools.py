#!/usr/bin/env python
"""
Comprehensive tests for ADX MCP server tools and functions.
"""

import os
import pytest
from unittest.mock import patch, MagicMock, call

from adx_mcp_server.server import (
    get_kusto_client,
    format_query_results,
    config,
    TransportType,
    MCPServerConfig,
    ADXConfig
)


class TestGetKustoClient:
    """Tests for get_kusto_client function."""

    def test_workload_identity_credential(self, monkeypatch):
        """Test using WorkloadIdentityCredential when env vars are set."""
        monkeypatch.setenv('AZURE_TENANT_ID', 'test-tenant')
        monkeypatch.setenv('AZURE_CLIENT_ID', 'test-client')
        monkeypatch.setenv('ADX_TOKEN_FILE_PATH', '/test/path')

        original_url = config.cluster_url
        config.cluster_url = "https://testcluster.region.kusto.windows.net"

        try:
            with patch('adx_mcp_server.server.WorkloadIdentityCredential') as mock_wic:
                with patch('adx_mcp_server.server.KustoConnectionStringBuilder') as mock_kcsb:
                    with patch('adx_mcp_server.server.KustoClient') as mock_client:
                        with patch('adx_mcp_server.server.logger') as mock_logger:
                            mock_wic_instance = MagicMock()
                            mock_wic.return_value = mock_wic_instance

                            result = get_kusto_client()

                            # Verify WorkloadIdentityCredential was created
                            mock_wic.assert_called_once_with(
                                tenant_id='test-tenant',
                                client_id='test-client',
                                token_file_path='/test/path'
                            )

                            # Verify logger was called
                            mock_logger.info.assert_called_with(
                                "Using WorkloadIdentityCredential",
                                client_id='test-client',
                                tenant_id='test-tenant',
                                token_file_path='/test/path'
                            )
        finally:
            config.cluster_url = original_url

    def test_default_azure_credential_fallback(self, monkeypatch):
        """Test falling back to DefaultAzureCredential."""
        monkeypatch.delenv('AZURE_TENANT_ID', raising=False)
        monkeypatch.delenv('AZURE_CLIENT_ID', raising=False)

        original_url = config.cluster_url
        config.cluster_url = "https://testcluster.region.kusto.windows.net"

        try:
            with patch('adx_mcp_server.server.DefaultAzureCredential') as mock_dac:
                with patch('adx_mcp_server.server.KustoConnectionStringBuilder') as mock_kcsb:
                    with patch('adx_mcp_server.server.KustoClient') as mock_client:
                        with patch('adx_mcp_server.server.logger') as mock_logger:
                            mock_dac_instance = MagicMock()
                            mock_dac.return_value = mock_dac_instance

                            result = get_kusto_client()

                            # Verify DefaultAzureCredential was created
                            mock_dac.assert_called_once()

                            # Verify logger was called
                            mock_logger.info.assert_called_with(
                                "Using DefaultAzureCredential (missing WorkloadIdentity credentials)"
                            )
        finally:
            config.cluster_url = original_url

    def test_workload_identity_exception_fallback(self, monkeypatch):
        """Test fallback when WorkloadIdentityCredential fails."""
        monkeypatch.setenv('AZURE_TENANT_ID', 'test-tenant')
        monkeypatch.setenv('AZURE_CLIENT_ID', 'test-client')

        original_url = config.cluster_url
        config.cluster_url = "https://testcluster.region.kusto.windows.net"

        try:
            with patch('adx_mcp_server.server.WorkloadIdentityCredential') as mock_wic:
                with patch('adx_mcp_server.server.DefaultAzureCredential') as mock_dac:
                    with patch('adx_mcp_server.server.KustoConnectionStringBuilder') as mock_kcsb:
                        with patch('adx_mcp_server.server.KustoClient') as mock_client:
                            with patch('adx_mcp_server.server.logger') as mock_logger:
                                # Make WorkloadIdentityCredential raise an exception
                                mock_wic.side_effect = Exception("Test error")
                                mock_dac_instance = MagicMock()
                                mock_dac.return_value = mock_dac_instance

                                result = get_kusto_client()

                                # Verify fallback to DefaultAzureCredential
                                mock_dac.assert_called_once()

                                # Verify warning was logged
                                mock_logger.warning.assert_called_once()
        finally:
            config.cluster_url = original_url

    def test_kusto_client_creation_error(self, monkeypatch):
        """Test error handling when KustoClient creation fails."""
        monkeypatch.delenv('AZURE_TENANT_ID', raising=False)
        monkeypatch.delenv('AZURE_CLIENT_ID', raising=False)

        original_url = config.cluster_url
        config.cluster_url = "https://testcluster.region.kusto.windows.net"

        try:
            with patch('adx_mcp_server.server.DefaultAzureCredential') as mock_dac:
                with patch('adx_mcp_server.server.KustoConnectionStringBuilder') as mock_kcsb:
                    with patch('adx_mcp_server.server.KustoClient') as mock_client:
                        with patch('adx_mcp_server.server.logger') as mock_logger:
                            # Make KustoClient raise an exception
                            mock_client.side_effect = Exception("Connection error")

                            with pytest.raises(Exception) as exc_info:
                                get_kusto_client()

                            assert str(exc_info.value) == "Connection error"

                            # Verify error was logged
                            mock_logger.error.assert_called_once()
        finally:
            config.cluster_url = original_url


class TestFormatQueryResults:
    """Tests for format_query_results function."""

    def test_format_valid_results(self):
        """Test formatting valid query results."""
        # Create mock result set
        mock_result_set = MagicMock()
        primary_result = MagicMock()

        col1 = MagicMock()
        col1.column_name = "Name"
        col2 = MagicMock()
        col2.column_name = "Value"

        primary_result.columns = [col1, col2]
        primary_result.rows = [
            ["Row1", 100],
            ["Row2", 200],
            ["Row3", 300]
        ]

        mock_result_set.primary_results = [primary_result]

        with patch('adx_mcp_server.server.logger'):
            result = format_query_results(mock_result_set)

        assert len(result) == 3
        assert result[0] == {"Name": "Row1", "Value": 100}
        assert result[1] == {"Name": "Row2", "Value": 200}
        assert result[2] == {"Name": "Row3", "Value": 300}

    def test_format_empty_result_set(self):
        """Test formatting empty result set."""
        with patch('adx_mcp_server.server.logger'):
            result = format_query_results(None)
        assert result == []

    def test_format_no_primary_results(self):
        """Test formatting result set with no primary results."""
        mock_result_set = MagicMock()
        mock_result_set.primary_results = []

        with patch('adx_mcp_server.server.logger'):
            result = format_query_results(mock_result_set)
        assert result == []

    def test_format_results_error_handling(self):
        """Test error handling in format_query_results."""
        mock_result_set = MagicMock()
        mock_result_set.primary_results = [MagicMock()]
        # Make accessing columns raise an exception
        mock_result_set.primary_results[0].columns = None

        with patch('adx_mcp_server.server.logger') as mock_logger:
            with pytest.raises(Exception):
                format_query_results(mock_result_set)

            # Verify error was logged
            mock_logger.error.assert_called_once()


class TestAsyncTools:
    """Tests for async tool functions."""

    @pytest.mark.asyncio
    async def test_execute_query_success(self):
        """Test execute_query with successful execution."""
        original_url = config.cluster_url
        original_db = config.database
        config.cluster_url = "https://testcluster.region.kusto.windows.net"
        config.database = "testdb"

        try:
            with patch('adx_mcp_server.server.get_kusto_client') as mock_get_client:
                with patch('adx_mcp_server.server.format_query_results') as mock_format:
                    with patch('adx_mcp_server.server.logger') as mock_logger:
                        mock_client = MagicMock()
                        mock_result_set = MagicMock()
                        mock_client.execute.return_value = mock_result_set
                        mock_get_client.return_value = mock_client
                        mock_format.return_value = [{"test": "data"}]

                        # Import and call the actual function
                        from adx_mcp_server import server
                        # Access the function through the module
                        execute_query_fn = server.execute_query

                        # Call using the tool's underlying function if it exists
                        if hasattr(execute_query_fn, 'fn'):
                            result = await execute_query_fn.fn("SELECT * FROM table")
                        else:
                            # Try calling directly
                            result = await execute_query_fn("SELECT * FROM table")

                        assert result == [{"test": "data"}]
                        mock_logger.info.assert_called()
        finally:
            config.cluster_url = original_url
            config.database = original_db

    @pytest.mark.asyncio
    async def test_execute_query_missing_config(self):
        """Test execute_query with missing configuration."""
        original_url = config.cluster_url
        original_db = config.database
        config.cluster_url = ""
        config.database = ""

        try:
            with patch('adx_mcp_server.server.logger') as mock_logger:
                from adx_mcp_server import server
                execute_query_fn = server.execute_query

                with pytest.raises(ValueError, match="Azure Data Explorer configuration is missing"):
                    if hasattr(execute_query_fn, 'fn'):
                        await execute_query_fn.fn("SELECT * FROM table")
                    else:
                        await execute_query_fn("SELECT * FROM table")

                mock_logger.error.assert_called()
        finally:
            config.cluster_url = original_url
            config.database = original_db

    @pytest.mark.asyncio
    async def test_execute_query_with_error(self):
        """Test execute_query with execution error."""
        original_url = config.cluster_url
        original_db = config.database
        config.cluster_url = "https://testcluster.region.kusto.windows.net"
        config.database = "testdb"

        try:
            with patch('adx_mcp_server.server.get_kusto_client') as mock_get_client:
                with patch('adx_mcp_server.server.logger') as mock_logger:
                    mock_client = MagicMock()
                    mock_client.execute.side_effect = Exception("Query error")
                    mock_get_client.return_value = mock_client

                    from adx_mcp_server import server
                    execute_query_fn = server.execute_query

                    with pytest.raises(Exception, match="Query error"):
                        if hasattr(execute_query_fn, 'fn'):
                            await execute_query_fn.fn("SELECT * FROM table")
                        else:
                            await execute_query_fn("SELECT * FROM table")

                    mock_logger.error.assert_called()
        finally:
            config.cluster_url = original_url
            config.database = original_db


class TestTransportAndConfig:
    """Tests for transport types and configuration classes."""

    def test_transport_type_values(self):
        """Test TransportType enum values."""
        assert TransportType.STDIO.value == "stdio"
        assert TransportType.HTTP.value == "http"
        assert TransportType.SSE.value == "sse"
        assert TransportType.values() == ["stdio", "http", "sse"]

    def test_mcp_server_config_validation(self):
        """Test MCPServerConfig validation."""
        with pytest.raises(ValueError, match="MCP SERVER TRANSPORT is required"):
            MCPServerConfig(mcp_server_transport=None, mcp_bind_host="localhost", mcp_bind_port=8080)

    def test_mcp_server_config_valid(self):
        """Test valid MCPServerConfig creation."""
        config = MCPServerConfig(
            mcp_server_transport="http",
            mcp_bind_host="localhost",
            mcp_bind_port=8080
        )
        assert config.mcp_server_transport == "http"
        assert config.mcp_bind_host == "localhost"
        assert config.mcp_bind_port == 8080

    def test_adx_config_creation(self):
        """Test ADXConfig creation."""
        config = ADXConfig(
            cluster_url="https://test.kusto.windows.net",
            database="testdb"
        )
        assert config.cluster_url == "https://test.kusto.windows.net"
        assert config.database == "testdb"
        assert config.mcp_server_config is None
