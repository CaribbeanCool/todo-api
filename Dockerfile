# Use an official image that already has uv installed
FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim

# Set working directory inside the container
WORKDIR /app

# Copy only dependency-related files first (for layer caching)
COPY pyproject.toml uv.lock README.md ./

# Install dependencies (not the project itself yet — no source code present)
RUN uv sync --frozen --no-install-project

# Now copy the actual source code
COPY src ./src

# Install the project itself now that source is present
RUN uv sync --frozen

# Tell Docker which port the app listens on (documentation, not enforcement)
EXPOSE 8000

# Run the app — note: no --reload, that's a dev-only flag
CMD ["uv", "run", "uvicorn", "todo_api.app:app", "--host", "0.0.0.0", "--port", "8000"]