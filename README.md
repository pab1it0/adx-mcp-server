# Azure Data Explorer MCP Server

<a href="https://glama.ai/mcp/servers/1yysyd147h">
  <img width="380" height="200" src="https://glama.ai/mcp/servers/1yysyd147h/badge" />
</a>

A [Model Context Protocol][mcp] (MCP) server for Azure Data Explorer/Eventhouse in Microsoft Fabric.

This provides access to your Azure Data Explorer/Eventhouse clusters and databases through standardized MCP interfaces, allowing AI assistants to execute KQL queries and explore your data.

[mcp]: https://modelcontextprotocol.io

## Features

- [x] Execute KQL queries against Azure Data Explorer
- [x] Discover and explore database resources
  - [x] List tables in the configured database
  - [x] View table schemas
  - [x] Sample data from tables
  - [x] Get table statistics/details

- [x] Authentication support
  - [x] Token credential support (Azure CLI, MSI, etc.)
  - [x] Workload Identity credential support for AKS
- [x] Docker containerization support

- [x] Provide interactive tools for AI assistants

The list of tools is configurable, so you can choose which tools you want to make available to the MCP client.
This is useful if you don't use certain functionality or if you don't want to take up too much of the context window.

## Usage

1. Login to your Azure account which has the permission to the ADX cluster using Azure CLI.

2. Configure the environment variables for your ADX cluster, either through a `.env` file or system environment variables:

```env
# Required: Azure Data Explorer configuration
ADX_CLUSTER_URL=https://yourcluster.region.kusto.windows.net
ADX_DATABASE=your_database

# Optional: Azure Workload Identity credentials 
# AZURE_TENANT_ID=your-tenant-id
# AZURE_CLIENT_ID=your-client-id 
# ADX_TOKEN_FILE_PATH=/var/run/secrets/azure/tokens/azure-identity-token
```

#### Azure Workload Identity Support

The server now uses WorkloadIdentityCredential by default when running in Azure Kubernetes Service (AKS) environments with workload identity configured. It prioritizes the use of WorkloadIdentityCredential whenever the necessary environment variables are present.

For AKS with Azure Workload Identity, you only need to:
1. Make sure the pod has `AZURE_TENANT_ID` and `AZURE_CLIENT_ID` environment variables set
2. Ensure the token file is mounted at the default path or specify a custom path with `ADX_TOKEN_FILE_PATH`

If these environment variables are not present, the server will automatically fall back to DefaultAzureCredential, which tries multiple authentication methods in sequence.

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
        "src/adx_mcp_server/main.py"
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

## Docker Usage

This project includes Docker support for easy deployment and isolation.

### Building the Docker Image

Build the Docker image using:

```bash
docker build -t adx-mcp-server .
```

### Running with Docker

You can run the server using Docker in several ways:

#### Using docker run directly:

```bash
docker run -it --rm \
  -e ADX_CLUSTER_URL=https://yourcluster.region.kusto.windows.net \
  -e ADX_DATABASE=your_database \
  -e AZURE_TENANT_ID=your_tenant_id \
  -e AZURE_CLIENT_ID=your_client_id \
  adx-mcp-server
```

#### Using docker-compose:

Create a `.env` file with your Azure Data Explorer credentials and then run:

```bash
docker-compose up
```

### Running with Docker in Claude Desktop

To use the containerized server with Claude Desktop, update the configuration to use Docker with the environment variables:

```json
{
  "mcpServers": {
    "adx": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "-e", "ADX_CLUSTER_URL",
        "-e", "ADX_DATABASE",
        "-e", "AZURE_TENANT_ID",
        "-e", "AZURE_CLIENT_ID",
        "-e", "ADX_TOKEN_FILE_PATH",
        "adx-mcp-server"
      ],
      "env": {
        "ADX_CLUSTER_URL": "https://yourcluster.region.kusto.windows.net",
        "ADX_DATABASE": "your_database",
        "AZURE_TENANT_ID": "your_tenant_id",
        "AZURE_CLIENT_ID": "your_client_id",
        "ADX_TOKEN_FILE_PATH": "/var/run/secrets/azure/tokens/azure-identity-token"
      }
    }
  }
}
```

This configuration passes the environment variables from Claude Desktop to the Docker container by using the `-e` flag with just the variable name, and providing the actual values in the `env` object.

## Using as a Dev Container / GitHub Codespace

This repository can also be used as a development container for a seamless development experience. The dev container setup is located in the `devcontainer-feature/adx-mcp-server` folder.

For more details, check the [devcontainer README](devcontainer-feature/adx-mcp-server/README.md).



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

## Project Structure

The project has been organized with a `src` directory structure:

```
adx-mcp-server/
├── src/
│   └── adx_mcp_server/
│       ├── __init__.py      # Package initialization
│       ├── server.py        # MCP server implementation
│       ├── main.py          # Main application logic
├── Dockerfile               # Docker configuration
├── docker-compose.yml       # Docker Compose configuration
├── .dockerignore            # Docker ignore file
├── pyproject.toml           # Project configuration
└── README.md                # This file
```

### Testing

The project includes a comprehensive test suite that ensures functionality and helps prevent regressions.

Run the tests with pytest:

```bash
# Install development dependencies
uv pip install -e ".[dev]"

# Run the tests
pytest

# Run with coverage report
pytest --cov=src --cov-report=term-missing
```
Tests are organized into:

- Configuration validation tests
- Server functionality tests
- Error handling tests
- Main application tests

When adding new features, please also add corresponding tests.

### Tools

| Tool | Category | Description |
| --- | --- | --- |
| `execute_query` | Query | Execute a KQL query against Azure Data Explorer |
| `list_tables` | Discovery | List all tables in the configured database |
| `get_table_schema` | Discovery | Get the schema for a specific table |
| `sample_table_data` | Discovery | Get sample data from a table with optional sample size |


## License

MIT

---

[mcp]: https://modelcontextprotocol.io
