# Use Python 3.13 slim image for smaller size
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        git \
    && rm -rf /var/lib/apt/lists/*

# Install uv for dependency management
RUN pip install --no-cache-dir uv

# Copy pyproject.toml and uv.lock from root
COPY pyproject.toml uv.lock ./

# Install Python dependencies using uv
RUN uv sync --frozen --no-dev

# Copy backend directory
COPY backend/ ./backend/

# Create database directory and copy database file
RUN mkdir -p /app/backend/database
COPY backend/database/portfolio_data.sqlite /app/backend/database/portfolio_data.sqlite

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# Expose port (will be overridden by Azure App Service)
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:$PORT/health || exit 1

# Run the FastAPI application
CMD ["uv", "run", "python", "backend/run_api.py"]