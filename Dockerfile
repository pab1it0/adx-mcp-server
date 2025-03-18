FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy the project files
COPY . /app/

# Install uv
RUN pip install --upgrade pip && \
    pip install uv

# Create a virtual environment, install dependencies
RUN uv venv /app/.venv && \
    . /app/.venv/bin/activate && \
    uv pip install -e .

# Set the entrypoint
ENTRYPOINT ["/app/.venv/bin/python", "-m", "adx_mcp_server.main"]

# Label the image
LABEL maintainer="pab1it0" \
      description="Azure Data Explorer MCP Server" \
      version="1.0.0"

# Expose port if needed (but this is optional as the MCP server typically runs on stdio)
# EXPOSE 8000
