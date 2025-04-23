# Azure Data Explorer MCP Server

<a href="https://glama.ai/mcp/servers/1yysyd147h">
  <img width="380" height="200" src="https://glama.ai/mcp/servers/1yysyd147h/badge" />
</a>

A [Model Context Protocol][mcp] (MCP) server for Azure Data Explorer/Eventhouse in Microsoft Fabric.

This provides access to your Azure Data Explorer/Eventhouse clusters and databases through standardized MCP interfaces, allowing AI assistants to execute KQL queries and explore your data.

Supports both STDIO (standard) and SSE (Server-Sent Events) transport modes for flexible integration options.

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
- [x] Docker containerization support

- [x] Multiple transport mode support
  - [x] STDIO (standard input/output) for command-line integration
  - [x] SSE (Server-Sent Events) for web-based integration

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

# Optional: SSE mode configuration (if using SSE transport)
ADX_MCP_HOST=0.0.0.0  # Host to bind for SSE mode
ADX_MCP_PORT=8000     # Port to listen on for SSE mode
ADX_MCP_LOG_LEVEL=INFO  # Logging level
```

### STDIO Mode (Default)

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

### SSE Mode (Server-Sent Events)

3. To use the server in SSE mode, you can run it directly with the `--transport sse` option:

```bash
# Run directly with Python
python -m adx_mcp_server.main --transport sse

# Or using the installed package
adx-mcp-server --transport sse
```

This will start an HTTP server that uses Server-Sent Events (SSE) for MCP communication.

4. Configure your client to connect to the SSE endpoint. For clients that support SSE-based MCP servers:

```json
{
  "mcpServers": {
    "adx": {
      "url": "http://localhost:8000/",
      "transport": "sse"
    }
  }
}
```

The server also provides a `/health` endpoint to verify the server status.

## Docker Usage

This project includes Docker support for easy deployment and isolation.

### Building the Docker Image

Build the Docker image using:

```bash
docker build -t adx-mcp-server .
```

### Running with Docker

You can run the server using Docker in several ways:

#### Using docker run directly (STDIO mode):

```bash
docker run -it --rm \
  -e ADX_CLUSTER_URL=https://yourcluster.region.kusto.windows.net \
  -e ADX_DATABASE=your_database \
  adx-mcp-server
```

#### Using docker run for SSE mode:

```bash
docker run -it --rm \
  -p 8000:8000 \
  -e ADX_CLUSTER_URL=https://yourcluster.region.kusto.windows.net \
  -e ADX_DATABASE=your_database \
  adx-mcp-server --transport sse
```

#### Using docker-compose:

Create a `.env` file with your Azure Data Explorer credentials and then run:

```bash
# For standard STDIO mode
docker-compose up adx-mcp-server

# For SSE mode
docker-compose up adx-mcp-server-sse
```

### Running with Docker in Claude Desktop

To use the containerized server with Claude Desktop, update the configuration to use Docker with the environment variables:

#### STDIO Mode

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
        "adx-mcp-server"
      ],
      "env": {
        "ADX_CLUSTER_URL": "https://yourcluster.region.kusto.windows.net",
        "ADX_DATABASE": "your_database"
      }
    }
  }
}
```

This configuration passes the environment variables from Claude Desktop to the Docker container by using the `-e` flag with just the variable name, and providing the actual values in the `env` object.

#### SSE Mode

For SSE mode, you would typically run the Docker container separately and configure Claude Desktop to connect to it:

1. Start the Docker container with SSE mode and port forwarding:

```bash
docker run -d --name adx-mcp-sse -p 8000:8000 \
  -e ADX_CLUSTER_URL=https://yourcluster.region.kusto.windows.net \
  -e ADX_DATABASE=your_database \
  adx-mcp-server --transport sse
```

2. Configure Claude Desktop to use the SSE endpoint:

```json
{
  "mcpServers": {
    "adx": {
      "url": "http://localhost:8000/",
      "transport": "sse"
    }
  }
}
```

This setup allows multiple clients to connect to the same ADX MCP server instance.

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