#!/usr/bin/env bash
set -e

# The 'install.sh' entrypoint script is always executed as the root user

# Variable declarations from feature options
VERSION="${VERSION:-"latest"}"
ADX_CLUSTER_URL="${ADXCLUSTERURL:-""}"
ADX_DATABASE="${ADXDATABASE:-""}"
INSTALL_DEPENDENCIES="${INSTALLDEPENDENCIES:-"true"}"
INSTALL_UV="${INSTALLUV:-"true"}"
SERVER_PORT="${SERVERPORT:-"3000"}"

# Clean up
apt-get clean -y
rm -rf /var/lib/apt/lists/*

# Install prerequisites
apt-get update
apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    gnupg \
    lsb-release \
    git

echo "Setting up Azure Data Explorer MCP Server..."

# Install uv if selected
if [ "${INSTALL_UV}" = "true" ]; then
    echo "Installing uv package manager..."
    curl -fsSL https://astral.sh/uv/install.sh | bash
    export PATH="/root/.cargo/bin:$PATH"
fi

# Setup the server directory
mkdir -p /opt/adx-mcp-server
cd /opt/adx-mcp-server

# If working in the actual repository, copy the code
if [ -d "/workspaces/adx-mcp-server" ]; then
    echo "Repository found, copying files..."
    cp -r /workspaces/adx-mcp-server/* /opt/adx-mcp-server/
elif [ "${VERSION}" = "latest" ]; then
    # Clone the repository if not in the workspace
    echo "Cloning the latest version of ADX MCP Server..."
    git clone https://github.com/yourusername/adx-mcp-server.git .
else
    # Clone a specific version
    echo "Cloning version ${VERSION} of ADX MCP Server..."
    git clone --depth 1 --branch ${VERSION} https://github.com/yourusername/adx-mcp-server.git .
fi

# Create virtual environment and install dependencies
if [ "${INSTALL_DEPENDENCIES}" = "true" ]; then
    echo "Installing Python dependencies..."
    if [ "${INSTALL_UV}" = "true" ]; then
        # Install using uv
        uv venv .venv
        source .venv/bin/activate
        uv pip install -e .
    else
        # Install using standard pip
        python -m venv .venv
        source .venv/bin/activate
        pip install -e .
    fi
fi

# Create a convenience script to start the server
cat > /usr/local/bin/start-adx-mcp-server << 'EOF'
#!/bin/bash
set -e

# Source the virtual environment
source /opt/adx-mcp-server/.venv/bin/activate

# Set environment variables if provided
if [ -n "$1" ]; then
    export ADX_CLUSTER_URL="$1"
fi

if [ -n "$2" ]; then
    export ADX_DATABASE="$2"
fi

if [ -n "$3" ]; then
    export MCP_PORT="$3"
fi

# Run the server
adx-mcp-server
EOF

# Make the script executable
chmod +x /usr/local/bin/start-adx-mcp-server

# Set default environment variables
echo "export ADX_CLUSTER_URL=${ADX_CLUSTER_URL}" >> /etc/bash.bashrc
echo "export ADX_DATABASE=${ADX_DATABASE}" >> /etc/bash.bashrc
echo "export MCP_PORT=${SERVER_PORT}" >> /etc/bash.bashrc

echo "Azure Data Explorer MCP Server Feature installation complete!"