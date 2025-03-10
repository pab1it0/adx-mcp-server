# Azure Data Explorer MCP Server

A [Model Context Protocol][mcp] (MCP) server for Azure Data Explorer.

This provides access to your Azure Data Explorer clusters and databases through standardized MCP interfaces, allowing AI assistants to execute KQL queries and explore your data.

[mcp]: https://modelcontextprotocol.io

## Features

- [x] Execute KQL queries against Azure Data Explorer
- [x] Discover and explore database resources
  - [x] List tables in the configured database
  - [x] View table schemas
  - [x] Sample data from tables
- [x] Authentication support
  - [x] Client credentials from environment variables

- [x] Provide interactive tools for AI assistants

The list of tools is configurable, so you can choose which tools you want to make available to the MCP client.
This is useful if you don't use certain functionality or if you don't want to take up too much of the context window.

## Usage

1. Create a service account in Azure Data Explorer with appropriate permissions, or ensure you have access through your Azure account.

2. Configure the environment variables for your ADX cluster, either through a `.env` file or system environment variables:

```env
# Required: Azure Data Explorer configuration
ADX_CLUSTER_URL=https://yourcluster.region.kusto.windows.net
ADX_DATABASE=your_database

# Optional: Azure authentication (if not using default credentials)
AZURE_TENANT_ID=your_tenant_id
AZURE_CLIENT_ID=your_client_id
AZURE_CLIENT_SECRET=your_client_secret
```

3. Add the server configuration to your client configuration file. For example, for Claude Desktop:

```json
{
  "mcpServers": {
    "adx": {
      "command": "uv",
      "args": [
        "--directory",
        "<full path to adx-mcp-server directory>",
        "run",
        "main.py"
      ],
      "env": {
        "ADX_CLUSTER_URL": "https://yourcluster.region.kusto.windows.net",
        "ADX_DATABASE": "your_database"
      }
    }
  }
}
```

> Note: if you see `Error: spawn uv ENOENT` in Claude Desktop, you may need to specify the full path to `uv` or set the environment variable `NO_UV=1` in the configuration.

## Development

Contributions are welcome! Please open an issue or submit a pull request if you have any suggestions or improvements.

This project uses [`uv`](https://github.com/astral-sh/uv) to manage dependencies. Install `uv` following the instructions for your platform:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

You can then create a virtual environment and install the dependencies with:

```bash
uv venv
source .venv/bin/activate  # On Unix/macOS
.venv\Scripts\activate     # On Windows
uv pip install -e .
```

To run the server in development mode with the MCP Inspector, use:

```bash
uv run -m mcp.cli dev server.py
```

Or to run the server directly:

```bash
uv run main.py
```

### Testing

Run the tests with pytest:

```bash
uv run -m pytest
```

### Tools

| Tool | Category | Description |
| --- | --- | --- |
| `execute_query` | Query | Execute a KQL query against Azure Data Explorer |
| `list_tables` | Discovery | List all tables in the configured database |
| `get_table_schema` | Discovery | Get the schema for a specific table |
| `sample_table_data` | Discovery | Get sample data from a table with optional sample size |

## Example Usage

Here's how an AI assistant might use this MCP server to interact with your Azure Data Explorer instance:

```
User: I need to analyze some data in Azure Data Explorer. Can you help me?

AI: I can help you analyze data in Azure Data Explorer. Let me first check what tables are available in your database.
[AI uses the list_tables tool]

AI: I found several tables in your database. Here are the available tables:
- logs
- metrics
- users
- events

What kind of analysis would you like to perform?

User: I want to see if there were any errors in the logs in the last 24 hours.

AI: I'll query the logs table for errors in the last 24 hours.
[AI uses the execute_query tool with:
  "logs | where Timestamp > ago(24h) and Level == 'Error' | summarize count() by Source"]

AI: Here are the error counts by source from the last 24 hours:
| Source      | count |
|-------------|-------|
| WebService  | 42    |
| DataProcessor| 17   |
| API         | 5     |

Would you like me to investigate any of these error sources in more detail?
```

## License

MIT

---

[mcp]: https://modelcontextprotocol.io
