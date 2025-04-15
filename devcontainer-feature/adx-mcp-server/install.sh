#!/usr/bin/env bash
set -e

# The 'install.sh' entrypoint script is always executed as the root user

# Variable declarations from feature options
VERSION="${VERSION:-"latest"}"
ADX_CLUSTER_URL="${ADXCLUSTERURL}"
ADX_DATABASE="${ADXDATABASE}"
ADX_MCP_REPO="${ADXMCPREPO}"

echo "Setting up Azure Data Explorer MCP Server..."

# Setup the server directory
mkdir -p /opt/adx-mcp-server
cd /opt/adx-mcp-server

if [ "${VERSION}" = "latest" ]; then
    # Clone the repository if not in the workspace
    echo "Cloning the latest version of ADX MCP Server from ${ADX_MCP_REPO}..."
    git clone ${ADX_MCP_REPO} .
else
    # Clone a specific version
    echo "Cloning version ${VERSION} of ADX MCP Server from ${ADX_MCP_REPO}..."
    git clone --depth 1 --branch ${VERSION} ${ADX_MCP_REPO} .
fi

INSTALL_WITH_SUDO="false"
if command -v sudo >/dev/null 2>&1; then
    if [ "root" != "$_REMOTE_USER" ]; then
        INSTALL_WITH_SUDO="true"
    fi
fi

ENV_PATH=/home/$_REMOTE_USER/.adx-mcp-env

if [ "${INSTALL_WITH_SUDO}" = "true" ]; then
    sudo -u ${_REMOTE_USER} bash -c "echo 'ADX_CLUSTER_URL=$ADX_CLUSTER_URL' >> $ENV_PATH"
    sudo -u ${_REMOTE_USER} bash -c "echo 'ADX_DATABASE=$ADX_DATABASE' >> $ENV_PATH"
else
    echo ADX_CLUSTER_URL=$ADX_CLUSTER_URL >> $ENV_PATH || true
    echo ADX_DATABASE=$ADX_DATABASE >> $ENV_PATH || true
fi