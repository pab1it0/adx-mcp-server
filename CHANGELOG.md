# Changelog

## 1.0.5 (2025-04-15)

* Fixed `get_table_schema` function to return the correct schema (PR #31)
* Added support for table statistics and Eventhouse in Microsoft Fabric (PR #32)
* Improved error handling and logging
* Performance optimizations for query execution
* Updated dependencies

## 1.0.4 (2025-03-27)

* Updated Dockerfile to use uv for dependency management
* Added Smithery configuration for deployment
* Updated README with additional documentation
* Fixed various minor bugs and improved stability

## 1.0.3 (2025-03-25)

* Version bump for new release
* Switched to DefaultAzureCredential for authentication
* Removed client credential requirements from code and environment variables
* Updated tests to support token-based authentication
* Based on improvements from v1.0.2

## 1.0.2 (2025-03-24)

* Added token credential authentication support
* Fixed get_table_schema implementation
* Updated tests to reflect token credential changes

## 1.0.0 (2025-03-14)

* Initial stable release
* Full functionality for Azure Data Explorer integration
* MCP tools for query execution and schema exploration
