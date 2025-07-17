# Multi-stage build for Mids-Web
FROM node:18-alpine AS frontend-builder

# Set working directory for frontend
WORKDIR /app/frontend

# Copy package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy frontend source
COPY frontend/ .

# Build frontend
RUN npm run build

# Backend stage with uv
FROM python:3.11-slim AS backend-builder

# Install curl and uv - the modern Python package manager
RUN apt-get update && apt-get install -y curl && \
    curl -LsSf https://astral.sh/uv/install.sh | sh && \
    rm -rf /var/lib/apt/lists/*

# Add uv to PATH (uv installs to ~/.local/bin by default)
ENV PATH="/root/.local/bin:$PATH"

# Set working directory for backend
WORKDIR /app/backend

# Copy Python project files
COPY backend/pyproject.toml backend/README.md backend/uv.lock ./

# Create virtual environment and install dependencies
RUN uv venv .venv && uv sync --group dev --group test

# Production stage
FROM python:3.11-slim AS production

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy virtual environment from builder
COPY --from=backend-builder /app/backend/.venv /app/.venv

# Copy backend source
COPY backend/ ./backend/

# Copy built frontend static files
COPY --from=frontend-builder /app/frontend/build ./backend/static/

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/backend:$PYTHONPATH"

# Create non-root user
RUN adduser --disabled-password --gecos '' --shell /bin/bash user && \
    chown -R user:user /app
USER user

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/ping || exit 1

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]