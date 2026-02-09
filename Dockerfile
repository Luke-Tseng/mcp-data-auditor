FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Set the working directory
WORKDIR /app

# Enable bytecode compilation for faster startups
ENV UV_COMPILE_BYTECODE=1

# Copy only the dependency files first
COPY pyproject.toml uv.lock ./

# Install dependencies without the project itself
RUN uv sync --frozen --no-install-project --no-dev

# Copy the rest of your application code
COPY . .

# Final sync to install the project code
RUN uv sync --frozen --no-install-project --no-dev

# Expose the port your server will run on
EXPOSE 8000

# Start MCP server
CMD ["uv", "run", "server.py"]