#!/usr/bin/env python
"""
Comprehensive tests for all ADX MCP server tools to reach 90%+ coverage.
"""

import pytest
from unittest.mock import patch, MagicMock

from adx_mcp_server.server import config


class TestListTablesTool:
    """Tests for list_tables tool."""

    @pytest.mark.asyncio
    async def test_list_tables_success(self):
        """Test list_tables with successful execution."""
        original_url = config.cluster_url
        original_db = config.database
        config.cluster_url = "https://testcluster.region.kusto.windows.net"
        config.database = "testdb"

        try:
            with patch('adx_mcp_server.server.get_kusto_client') as mock_get_client:
                with patch('adx_mcp_server.server.format_query_results') as mock_format:
                    with patch('adx_mcp_server.server.logger'):
                        mock_client = MagicMock()
                        mock_result_set = MagicMock()
                        mock_client.execute.return_value = mock_result_set
                        mock_get_client.return_value = mock_client
                        mock_format.return_value = [{"TableName": "table1"}]

                        from adx_mcp_server import server
                        list_tables_fn = server.list_tables

                        if hasattr(list_tables_fn, 'fn'):
                            result = await list_tables_fn.fn()
                        else:
                            result = await list_tables_fn()

                        assert result == [{"TableName": "table1"}]
        finally:
            config.cluster_url = original_url
            config.database = original_db

    @pytest.mark.asyncio
    async def test_list_tables_missing_config(self):
        """Test list_tables with missing configuration."""
        original_url = config.cluster_url
        original_db = config.database
        config.cluster_url = ""
        config.database = ""

        try:
            with patch('adx_mcp_server.server.logger'):
                from adx_mcp_server import server
                list_tables_fn = server.list_tables

                with pytest.raises(ValueError):
                    if hasattr(list_tables_fn, 'fn'):
                        await list_tables_fn.fn()
                    else:
                        await list_tables_fn()
        finally:
            config.cluster_url = original_url
            config.database = original_db

    @pytest.mark.asyncio
    async def test_list_tables_error(self):
        """Test list_tables with execution error."""
        original_url = config.cluster_url
        original_db = config.database
        config.cluster_url = "https://testcluster.region.kusto.windows.net"
        config.database = "testdb"

        try:
            with patch('adx_mcp_server.server.get_kusto_client') as mock_get_client:
                with patch('adx_mcp_server.server.logger'):
                    mock_client = MagicMock()
                    mock_client.execute.side_effect = Exception("List error")
                    mock_get_client.return_value = mock_client

                    from adx_mcp_server import server
                    list_tables_fn = server.list_tables

                    with pytest.raises(Exception, match="List error"):
                        if hasattr(list_tables_fn, 'fn'):
                            await list_tables_fn.fn()
                        else:
                            await list_tables_fn()
        finally:
            config.cluster_url = original_url
            config.database = original_db


class TestGetTableSchemaTool:
    """Tests for get_table_schema tool."""

    @pytest.mark.asyncio
    async def test_get_table_schema_success(self):
        """Test get_table_schema with successful execution."""
        original_url = config.cluster_url
        original_db = config.database
        config.cluster_url = "https://testcluster.region.kusto.windows.net"
        config.database = "testdb"

        try:
            with patch('adx_mcp_server.server.get_kusto_client') as mock_get_client:
                with patch('adx_mcp_server.server.format_query_results') as mock_format:
                    with patch('adx_mcp_server.server.logger'):
                        mock_client = MagicMock()
                        mock_result_set = MagicMock()
                        mock_client.execute.return_value = mock_result_set
                        mock_get_client.return_value = mock_client
                        mock_format.return_value = [{"ColumnName": "col1"}]

                        from adx_mcp_server import server
                        get_schema_fn = server.get_table_schema

                        if hasattr(get_schema_fn, 'fn'):
                            result = await get_schema_fn.fn("test_table")
                        else:
                            result = await get_schema_fn("test_table")

                        assert result == [{"ColumnName": "col1"}]
        finally:
            config.cluster_url = original_url
            config.database = original_db

    @pytest.mark.asyncio
    async def test_get_table_schema_missing_config(self):
        """Test get_table_schema with missing configuration."""
        original_url = config.cluster_url
        original_db = config.database
        config.cluster_url = ""
        config.database = ""

        try:
            with patch('adx_mcp_server.server.logger'):
                from adx_mcp_server import server
                get_schema_fn = server.get_table_schema

                with pytest.raises(ValueError):
                    if hasattr(get_schema_fn, 'fn'):
                        await get_schema_fn.fn("test_table")
                    else:
                        await get_schema_fn("test_table")
        finally:
            config.cluster_url = original_url
            config.database = original_db

    @pytest.mark.asyncio
    async def test_get_table_schema_error(self):
        """Test get_table_schema with execution error."""
        original_url = config.cluster_url
        original_db = config.database
        config.cluster_url = "https://testcluster.region.kusto.windows.net"
        config.database = "testdb"

        try:
            with patch('adx_mcp_server.server.get_kusto_client') as mock_get_client:
                with patch('adx_mcp_server.server.logger'):
                    mock_client = MagicMock()
                    mock_client.execute.side_effect = Exception("Schema error")
                    mock_get_client.return_value = mock_client

                    from adx_mcp_server import server
                    get_schema_fn = server.get_table_schema

                    with pytest.raises(Exception, match="Schema error"):
                        if hasattr(get_schema_fn, 'fn'):
                            await get_schema_fn.fn("test_table")
                        else:
                            await get_schema_fn("test_table")
        finally:
            config.cluster_url = original_url
            config.database = original_db


class TestSampleTableDataTool:
    """Tests for sample_table_data tool."""

    @pytest.mark.asyncio
    async def test_sample_table_data_success(self):
        """Test sample_table_data with successful execution."""
        original_url = config.cluster_url
        original_db = config.database
        config.cluster_url = "https://testcluster.region.kusto.windows.net"
        config.database = "testdb"

        try:
            with patch('adx_mcp_server.server.get_kusto_client') as mock_get_client:
                with patch('adx_mcp_server.server.format_query_results') as mock_format:
                    with patch('adx_mcp_server.server.logger'):
                        mock_client = MagicMock()
                        mock_result_set = MagicMock()
                        mock_client.execute.return_value = mock_result_set
                        mock_get_client.return_value = mock_client
                        mock_format.return_value = [{"data": "sample"}]

                        from adx_mcp_server import server
                        sample_fn = server.sample_table_data

                        if hasattr(sample_fn, 'fn'):
                            result = await sample_fn.fn("test_table", 10)
                        else:
                            result = await sample_fn("test_table", 10)

                        assert result == [{"data": "sample"}]
        finally:
            config.cluster_url = original_url
            config.database = original_db

    @pytest.mark.asyncio
    async def test_sample_table_data_custom_size(self):
        """Test sample_table_data with custom sample size."""
        original_url = config.cluster_url
        original_db = config.database
        config.cluster_url = "https://testcluster.region.kusto.windows.net"
        config.database = "testdb"

        try:
            with patch('adx_mcp_server.server.get_kusto_client') as mock_get_client:
                with patch('adx_mcp_server.server.format_query_results') as mock_format:
                    with patch('adx_mcp_server.server.logger'):
                        mock_client = MagicMock()
                        mock_result_set = MagicMock()
                        mock_client.execute.return_value = mock_result_set
                        mock_get_client.return_value = mock_client
                        mock_format.return_value = [{"data": f"sample{i}"} for i in range(20)]

                        from adx_mcp_server import server
                        sample_fn = server.sample_table_data

                        if hasattr(sample_fn, 'fn'):
                            result = await sample_fn.fn("test_table", 20)
                        else:
                            result = await sample_fn("test_table", 20)

                        assert len(result) == 20
        finally:
            config.cluster_url = original_url
            config.database = original_db

    @pytest.mark.asyncio
    async def test_sample_table_data_error(self):
        """Test sample_table_data with execution error."""
        original_url = config.cluster_url
        original_db = config.database
        config.cluster_url = "https://testcluster.region.kusto.windows.net"
        config.database = "testdb"

        try:
            with patch('adx_mcp_server.server.get_kusto_client') as mock_get_client:
                with patch('adx_mcp_server.server.logger'):
                    mock_client = MagicMock()
                    mock_client.execute.side_effect = Exception("Sample error")
                    mock_get_client.return_value = mock_client

                    from adx_mcp_server import server
                    sample_fn = server.sample_table_data

                    with pytest.raises(Exception, match="Sample error"):
                        if hasattr(sample_fn, 'fn'):
                            await sample_fn.fn("test_table", 10)
                        else:
                            await sample_fn("test_table", 10)
        finally:
            config.cluster_url = original_url
            config.database = original_db


class TestGetTableDetailsTool:
    """Tests for get_table_details tool."""

    @pytest.mark.asyncio
    async def test_get_table_details_success(self):
        """Test get_table_details with successful execution."""
        original_url = config.cluster_url
        original_db = config.database
        config.cluster_url = "https://testcluster.region.kusto.windows.net"
        config.database = "testdb"

        try:
            with patch('adx_mcp_server.server.get_kusto_client') as mock_get_client:
                with patch('adx_mcp_server.server.format_query_results') as mock_format:
                    with patch('adx_mcp_server.server.logger'):
                        mock_client = MagicMock()
                        mock_result_set = MagicMock()
                        mock_client.execute.return_value = mock_result_set
                        mock_get_client.return_value = mock_client
                        mock_format.return_value = [{"TotalRowCount": 1000}]

                        from adx_mcp_server import server
                        details_fn = server.get_table_details

                        if hasattr(details_fn, 'fn'):
                            result = await details_fn.fn("test_table")
                        else:
                            result = await details_fn("test_table")

                        assert result == [{"TotalRowCount": 1000}]
        finally:
            config.cluster_url = original_url
            config.database = original_db

    @pytest.mark.asyncio
    async def test_get_table_details_missing_config(self):
        """Test get_table_details with missing configuration."""
        original_url = config.cluster_url
        original_db = config.database
        config.cluster_url = ""
        config.database = ""

        try:
            with patch('adx_mcp_server.server.logger'):
                from adx_mcp_server import server
                details_fn = server.get_table_details

                with pytest.raises(ValueError):
                    if hasattr(details_fn, 'fn'):
                        await details_fn.fn("test_table")
                    else:
                        await details_fn("test_table")
        finally:
            config.cluster_url = original_url
            config.database = original_db

    @pytest.mark.asyncio
    async def test_get_table_details_error(self):
        """Test get_table_details with execution error."""
        original_url = config.cluster_url
        original_db = config.database
        config.cluster_url = "https://testcluster.region.kusto.windows.net"
        config.database = "testdb"

        try:
            with patch('adx_mcp_server.server.get_kusto_client') as mock_get_client:
                with patch('adx_mcp_server.server.logger'):
                    mock_client = MagicMock()
                    mock_client.execute.side_effect = Exception("Details error")
                    mock_get_client.return_value = mock_client

                    from adx_mcp_server import server
                    details_fn = server.get_table_details

                    with pytest.raises(Exception, match="Details error"):
                        if hasattr(details_fn, 'fn'):
                            await details_fn.fn("test_table")
                        else:
                            await details_fn("test_table")
        finally:
            config.cluster_url = original_url
            config.database = original_db
