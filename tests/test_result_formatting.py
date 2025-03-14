#!/usr/bin/env python

import pytest
from unittest.mock import MagicMock
from adx_mcp_server.server import format_query_results

class TestResultFormatting:
    def test_format_complex_results(self):
        """Test formatting of complex result sets with various data types."""
        # Create a mock result set with different data types
        mock_result_set = MagicMock()
        primary_result = MagicMock()
        
        # Create columns with different types
        column1 = MagicMock()
        column1.column_name = "StringColumn"
        column2 = MagicMock()
        column2.column_name = "IntColumn"
        column3 = MagicMock()
        column3.column_name = "FloatColumn"
        column4 = MagicMock()
        column4.column_name = "BoolColumn"
        column5 = MagicMock()
        column5.column_name = "NullColumn"
        
        primary_result.columns = [column1, column2, column3, column4, column5]
        
        # Create rows with various data types
        primary_result.rows = [
            ["String1", 1, 1.1, True, None],
            ["String2", 2, 2.2, False, None],
            ["", 0, 0.0, None, None],  # Row with empty string and null values
        ]
        
        mock_result_set.primary_results = [primary_result]
        
        # Format the results
        result = format_query_results(mock_result_set)
        
        # Verify the results
        assert len(result) == 3
        
        # Check first row
        assert result[0]["StringColumn"] == "String1"
        assert result[0]["IntColumn"] == 1
        assert result[0]["FloatColumn"] == 1.1
        assert result[0]["BoolColumn"] is True
        assert result[0]["NullColumn"] is None
        
        # Check second row
        assert result[1]["StringColumn"] == "String2"
        assert result[1]["IntColumn"] == 2
        assert result[1]["FloatColumn"] == 2.2
        assert result[1]["BoolColumn"] is False
        assert result[1]["NullColumn"] is None
        
        # Check third row with edge cases
        assert result[2]["StringColumn"] == ""
        assert result[2]["IntColumn"] == 0
        assert result[2]["FloatColumn"] == 0.0
        assert result[2]["BoolColumn"] is None
        assert result[2]["NullColumn"] is None
    
    def test_format_results_with_duplicate_column_names(self):
        """Test formatting when there are duplicate column names."""
        mock_result_set = MagicMock()
        primary_result = MagicMock()
        
        # Create columns with duplicate names
        column1 = MagicMock()
        column1.column_name = "Column"
        column2 = MagicMock()
        column2.column_name = "Column"  # Duplicate name
        
        primary_result.columns = [column1, column2]
        primary_result.rows = [
            ["Value1", "Value2"],
        ]
        
        mock_result_set.primary_results = [primary_result]
        
        # Format the results
        result = format_query_results(mock_result_set)
        
        # The second duplicate column should overwrite the first one
        assert len(result) == 1
        assert result[0]["Column"] == "Value2"
    
    def test_format_results_with_multiple_primary_results(self):
        """Test formatting when there are multiple primary results."""
        mock_result_set = MagicMock()
        
        # First primary result
        primary_result1 = MagicMock()
        column1 = MagicMock()
        column1.column_name = "Column1"
        primary_result1.columns = [column1]
        primary_result1.rows = [["Value1"]]
        
        # Second primary result (should be ignored by format_query_results)
        primary_result2 = MagicMock()
        column2 = MagicMock()
        column2.column_name = "Column2"
        primary_result2.columns = [column2]
        primary_result2.rows = [["Value2"]]
        
        mock_result_set.primary_results = [primary_result1, primary_result2]
        
        # Format the results
        result = format_query_results(mock_result_set)
        
        # Only the first primary result should be processed
        assert len(result) == 1
        assert "Column1" in result[0]
        assert "Column2" not in result[0]
        assert result[0]["Column1"] == "Value1"
