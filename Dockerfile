# Multi-stage build for Azure Data Explorer MCP Server
# Build stage - uses uv for dependency management
FROM python:3.12-slim-bookworm AS builder

# Copy uv from official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copy project files
COPY pyproject.toml uv.lock ./
COPY src/ ./src/

# Create virtual environment and install dependencies
RUN uv venv && \
    . .venv/bin/activate && \
    uv sync --frozen --no-dev && \
    uv pip install --upgrade pip setuptools

# Runtime stage
FROM python:3.12-slim-bookworm

WORKDIR /app

# Install runtime dependencies and Azure CLI
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    apt-transport-https \
    lsb-release \
    gnupg \
    procps \
    ca-certificates \
    && curl -sL https://aka.ms/InstallAzureCLIDeb | bash \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Create non-root user for security
RUN groupadd -r app -g 1000 && \
    useradd -r -u 1000 -g app -d /app -s /bin/false app && \
    chown -R app:app /app && \
    chmod -R 755 /app && \
    chmod -R go-w /app

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    ADX_MCP_BIND_HOST="0.0.0.0" \
    ADX_MCP_BIND_PORT="8080"

# Expose port for HTTP/SSE transports
EXPOSE 8080

# Switch to non-root user
USER app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD if [ "$ADX_MCP_SERVER_TRANSPORT" = "http" ] || [ "$ADX_MCP_SERVER_TRANSPORT" = "sse" ]; then \
            curl -f http://localhost:${ADX_MCP_BIND_PORT}/health || exit 1; \
        else \
            pgrep -f adx-mcp-server || exit 1; \
        fi

# Entrypoint
ENTRYPOINT ["adx-mcp-server"]

# OCI labels for metadata
LABEL org.opencontainers.image.title="Azure Data Explorer MCP Server" \
      org.opencontainers.image.description="Model Context Protocol server for Azure Data Explorer (ADX/Kusto) providing KQL query execution and database exploration for AI assistants" \
      org.opencontainers.image.version="1.1.0" \
      org.opencontainers.image.authors="pab1it0" \
      org.opencontainers.image.url="https://github.com/pab1it0/adx-mcp-server" \
      org.opencontainers.image.source="https://github.com/pab1it0/adx-mcp-server" \
      org.opencontainers.image.documentation="https://github.com/pab1it0/adx-mcp-server/blob/main/README.md" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.vendor="pab1it0" \
      io.mcp.server.name="adx-mcp-server" \
      io.mcp.server.version="1.1.0" \
      io.mcp.server.transport="stdio,http,sse"
