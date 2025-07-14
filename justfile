#!/usr/bin/env just --justfile

# Default recipe - show available commands
default:
    @just --list --unsorted

# Project root directory
project_root := `git rev-parse --show-toplevel 2>/dev/null || pwd`

# Python executable
python := "python3"
uv := "uv"

# Quick start - setup everything
quickstart: install-tools install dev-setup
    @echo "✅ Quickstart complete! Run 'just dev' to start development."

# Install required tools
install-tools:
    @echo "📦 Installing required tools..."
    @command -v uv >/dev/null 2>&1 || curl -LsSf https://astral.sh/uv/install.sh | sh
    @echo "✅ Tools installed"

# Install all dependencies
install:
    @echo "📦 Installing backend dependencies..."
    cd backend && {{uv}} sync
    @echo "📦 Installing frontend dependencies..."
    cd frontend && npm install
    @echo "✅ Dependencies installed"

# Development setup
dev-setup:
    @echo "🔧 Setting up development environment..."
    @if [ ! -f .env ]; then cp .env.example .env 2>/dev/null || echo "⚠️  No .env.example found"; fi
    @echo "✅ Development environment ready"

# Start development servers
dev:
    @echo "🚀 Starting development environment..."
    docker-compose up --build

# Run health checks
health:
    @echo "🏥 Running health checks..."
    {{python}} scripts/dev.py setup
    @echo "✅ Health checks passed"

# Run all tests
test:
    @echo "🧪 Running all tests..."
    cd backend && {{uv}} run pytest -v
    cd frontend && npm test -- --watchAll=false

# Run tests in watch mode
test-watch:
    @echo "🧪 Running tests in watch mode..."
    cd backend && {{uv}} run pytest-watch

# Run linting and type checking
quality:
    @echo "🔍 Running code quality checks..."
    just lint
    just type-check

# Run linters
lint:
    @echo "🔍 Running linters..."
    cd backend && {{uv}} run ruff check .
    cd frontend && npm run lint

# Fix linting issues
lint-fix:
    @echo "🔧 Fixing linting issues..."
    cd backend && {{uv}} run ruff check --fix .
    cd backend && {{uv}} run black .
    cd frontend && npm run lint -- --fix

# Run type checking
type-check:
    @echo "🔍 Running type checking..."
    cd backend && {{uv}} run mypy .
    cd frontend && npm run type-check

# Format code
format:
    @echo "✨ Formatting code..."
    cd backend && {{uv}} run black .
    cd backend && {{uv}} run isort .
    cd backend && {{uv}} run ruff format .
    cd frontend && npm run format

# Database migrations
db-migrate:
    @echo "🗄️ Running database migrations..."
    cd backend && {{uv}} run alembic upgrade head

# Create a new migration
db-migration-create description:
    @echo "🗄️ Creating new migration: {{description}}..."
    cd backend && {{uv}} run alembic revision --autogenerate -m "{{description}}"

# Reset database
db-reset:
    @echo "⚠️  Resetting database..."
    cd backend && {{uv}} run alembic downgrade base
    cd backend && {{uv}} run alembic upgrade head

# Load sample data
db-seed:
    @echo "🌱 Loading sample data..."
    cd backend && {{uv}} run python -m scripts.seed_data

# Clean build artifacts
clean:
    @echo "🧹 Cleaning build artifacts..."
    {{python}} scripts/dev.py clean
    find . -type d -name "__pycache__" -exec trash {} + 2>/dev/null || true
    find . -type d -name ".pytest_cache" -exec trash {} + 2>/dev/null || true
    find . -type d -name "node_modules" -prune -o -type d -name ".next" -exec trash {} + 2>/dev/null || true

# Update progress in roadmap
progress-update:
    @echo "📊 Updating progress..."
    {{python}} scripts/context/update_progress.py

# Analyze token usage
token-usage:
    @echo "📊 Analyzing token usage..."
    {{python}} scripts/context/analyze_token_usage.py

# Monitor context health
context-health:
    @echo "🏥 Checking context health..."
    {{python}} scripts/context/context_health_monitor.py

# Prune context
context-prune:
    @echo "✂️ Pruning context..."
    {{python}} scripts/context/context_pruning.py

# Git add, commit and push
ucp message:
    git add -A
    git commit -m "{{message}}"
    git push

# Build for production
build:
    @echo "🏗️ Building for production..."
    cd frontend && npm run build
    cd backend && {{uv}} build

# Docker commands
docker-up:
    docker-compose up -d

docker-down:
    docker-compose down

docker-logs:
    docker-compose logs -f

docker-clean:
    docker-compose down -v
    docker system prune -f

# Show current epic status
epic-status:
    @echo "📊 Current Epic Status:"
    @echo "✅ Epic 1: Project Setup - Complete"
    @echo "🚧 Epic 2: Data Import - In Progress (BLOCKED)"
    @echo "📋 Epic 3: Backend API - Planned"
    @echo "📋 Epic 4: Frontend - Planned"
    @echo "📋 Epic 5: Deployment - Planned"
    @echo "📋 Epic 6: Optimization - Future"

# Setup GitHub workflows and secrets
setup-github-workflows:
    @echo "🤖 Setting up GitHub workflows..."
    bash scripts/setup-github-secret.sh

# Open API documentation
api-docs:
    @echo "📚 Opening API documentation..."
    open http://localhost:8000/docs || xdg-open http://localhost:8000/docs

# Frontend development server
frontend-dev:
    cd frontend && npm start

# Backend development server
backend-dev:
    cd backend && {{uv}} run uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Help - show this message
help:
    @echo "Mids Hero Web Development Commands"
    @echo "================================="
    @just --list