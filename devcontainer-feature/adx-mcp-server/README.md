# Azure Data Explorer MCP Server Dev Container Feature

This dev container feature installs and configures an Azure Data Explorer Model Context Protocol (MCP) server for development purposes.

## Description

This feature sets up everything needed to run and develop with an Azure Data Explorer MCP server:

- Installs the MCP server and its dependencies
- Sets up Docker CLI for container management
- Configures the necessary environment for development

## Usage

```json
"features": {
    "ghcr.io/your-username/devcontainer-features/adx-mcp-server:1.0.0": {
        "version": "latest",
        "adxClusterUrl": "https://cluster.region.kusto.windows.net",
        "adxDatabase": "my_database",
        "adxMcpRepo": "https://github.com/pab1it0/adx-mcp-server"
    }
}
```

## Dependencies

This feature automatically installs the following dependencies:
- `ghcr.io/devcontainers/features/docker-in-docker` - For Docker container support
- `ghcr.io/devcontainers/features/azure-cli` - For Azure Data Explorer authentication and operations

You don't need to explicitly include these in your devcontainer.json file.

## Options

| Option       | Default                                      | Description                                                    |
|--------------|----------------------------------------------|----------------------------------------------------------------|
| version      | "latest"                                     | Version of the ADX MCP server to install                       |
| adxClusterUrl| ""                                           | Azure Data Explorer cluster URL (must be specified at runtime) |
| adxDatabase  | ""                                           | Azure Data Explorer database name (must be specified at runtime)|
| adxMcpRepo   | "https://github.com/pab1it0/adx-mcp-server"  | Azure Data Explorer MCP repository URL                         |

## Docker Support

This feature includes the Docker CLI (`docker`) pre-installed and available on the `PATH` for running and managing containers using a dedicated Docker daemon running inside the dev container.

## License

See the [LICENSE](../../LICENSE) file for details.

## Troubleshooting

For more information about the MCP server, see the [documentation](../../docs/testing.md).
