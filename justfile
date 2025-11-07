#!/usr/bin/env just --justfile

# Configure uv for Python script execution
set unstable
set script-interpreter := ['uv', 'run', '--script']

# Default recipe - show available commands
default:
    @just --list --unsorted

# Project root directory
project_root := `git rev-parse --show-toplevel 2>/dev/null || pwd`

# Python and uv configuration
python := "python3"
uv := "uv"
database_url := "postgresql://postgres:postgres@localhost:5432/mids_web"

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

# JSON processing with jq
jq *args:
    @command -v jq >/dev/null 2>&1 || (echo "❌ jq not installed. Install with: brew install jq" && exit 1)
    @jq {{args}}

# Start development servers
dev:
    @echo "🚀 Starting development environment..."
    docker-compose up --build

# Run health checks
health:
    @echo "🏥 Running health checks..."
    @bash .claude/commands/validate-git-workflow.sh || true
    {{python}} scripts/dev.py setup
    @just json-import-health
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
    just check-commands
    just lint
    just type-check

# Check for forbidden commands
check-commands:
    @echo "🔍 Checking command compliance..."
    @./scripts/check-forbidden-commands.sh

# Verify MHD cleanup completeness
verify-cleanup:
    @echo "🔍 Running cleanup verification..."
    @./scripts/verify_mhd_cleanup.sh

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

# Database setup - comprehensive setup including Docker
db-setup:
    @echo "🗃️ Setting up database..."
    ./scripts/setup-database.sh

# Database migrations
db-migrate:
    @echo "🗄️ Running database migrations..."
    cd backend && DATABASE_URL=postgresql://postgres:postgres@localhost:5432/mids_web {{uv}} run alembic upgrade head

# Create a new migration
db-migration-create description:
    @echo "🗄️ Creating new migration: {{description}}..."
    cd backend && DATABASE_URL=postgresql://postgres:postgres@localhost:5432/mids_web {{uv}} run alembic revision --autogenerate -m "{{description}}"

# Reset database
db-reset:
    @echo "⚠️  Resetting database..."
    docker-compose down db -v || true
    just db-setup

# Database status
db-status:
    @echo "📊 Database status..."
    cd backend && DATABASE_URL=postgresql://postgres:postgres@localhost:5432/mids_web {{uv}} run alembic current

# Connect to database
db-connect:
    @echo "🔗 Connecting to database..."
    docker exec -it mids-hero-web-db-1 psql -U postgres -d mids_web

# Database shell alias
db-shell: db-connect

# Load sample data
db-seed:
    @echo "🌱 Loading sample data..."
    cd backend && {{uv}} run python -m scripts.seed_data

# Generic Data Import Operations (All Parsers)
import-all data_dir batch_size="1000":
    @echo "🚀 Importing all data from {{data_dir}}..."
    cd backend && {{uv}} run python -m app.data_import.cli --batch-size {{batch_size}} all "{{data_dir}}"

import-type type file batch_size="1000":
    @echo "📥 Importing {{type}} data from {{file}}..."
    cd backend && {{uv}} run python -m app.data_import.cli --batch-size {{batch_size}} {{type}} "{{file}}"

import-clear type file batch_size="1000":
    @echo "🧹 Clearing and importing {{type}} data from {{file}}..."
    cd backend && {{uv}} run python -m app.data_import.cli --clear --batch-size {{batch_size}} {{type}} "{{file}}"

import-resume type file resume_from batch_size="1000":
    @echo "🔄 Resuming {{type}} import from record {{resume_from}}..."
    cd backend && {{uv}} run python -m app.data_import.cli --resume-from {{resume_from}} --batch-size {{batch_size}} {{type}} "{{file}}"

# JSON Data Import Commands
json-import-archetypes:
    @echo "Importing archetypes from JSON..."
    {{uv}} run python -m backend.app.data_import.json_importer archetypes

json-import-powersets:
    @echo "Importing powersets from JSON..."
    {{uv}} run python -m backend.app.data_import.json_importer powersets

json-import-powers:
    @echo "Importing powers from JSON..."
    {{uv}} run python -m backend.app.data_import.json_importer powers

json-import-enhancements:
    @echo "Importing enhancement sets from JSON..."
    {{uv}} run python -m backend.app.data_import.json_importer enhancements

json-import-all:
    @echo "Importing all JSON data..."
    @just json-import-archetypes
    @just json-import-powersets
    @just json-import-powers
    @just json-import-enhancements
    @echo "✅ All JSON data imported"

json-import-health:
    @echo "🏥 Validating JSON import system..."
    @test -f filtered_data/manifest.json || (echo "❌ Manifest not found"; exit 1)
    @{{uv}} run python scripts/validate_filtered_data.py
    @echo "✅ JSON import system healthy"

# Common Import Examples
import-archetypes file:
    @just import-type archetypes "{{file}}"

import-powersets file:
    @just import-type powersets "{{file}}"

import-powers file:
    @just import-type powers "{{file}}"

import-enhancements file:
    @just import-type enhancements "{{file}}"

import-salvage file:
    @just import-type salvage "{{file}}"

import-recipes file:
    @just import-type recipes "{{file}}"

# Cache Management
cache-clear:
    @echo "🧹 Clearing power cache..."
    @{{uv}} run scripts/cache_clear.py

cache-stats:
    @echo "📊 Power cache statistics..."
    @{{uv}} run scripts/cache_stats.py

# Import System Status & Health Checks
import-status:
    @echo "📊 Import System Status"
    @echo "======================="
    @echo "Database status:"
    @just db-status
    @echo "\nTable record counts:"
    @just import-stats
    @echo "\nCache status:"
    @just cache-stats 2>/dev/null || echo "Cache not available"
    @echo "\nRedis status:"
    @docker-compose exec redis redis-cli ping 2>/dev/null || echo "Redis not available"

import-stats:
    @echo "📈 Database record counts..."
    @DATABASE_URL={{database_url}} {{uv}} run scripts/db_stats.py

# Database Optimization
db-optimize:
    @echo "🎯 Optimizing database for import operations..."
    @DATABASE_URL={{database_url}} {{uv}} run scripts/db_optimize.py

[script]
db-vacuum:
    # /// script
    # requires-python = ">=3.11"
    # dependencies = ["sqlalchemy", "psycopg2-binary"]
    # ///
    import os
    from sqlalchemy import create_engine, text
    
    print("🧹 Vacuuming database for optimal performance...")
    database_url = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/mids_web')
    engine = create_engine(database_url)
    
    with engine.connect() as conn:
        conn.execution_options(isolation_level='AUTOCOMMIT').execute(text('VACUUM ANALYZE'))
        print('✅ Database vacuum completed')

# Clean build artifacts
clean:
    @echo "🧹 Cleaning build artifacts..."
    {{python}} scripts/dev.py clean
    fd __pycache__ -t d -x trash 2>/dev/null || true
    fd .pytest_cache -t d -x trash 2>/dev/null || true
    fd node_modules -t d -x trash 2>/dev/null || true
    fd .next -t d -x trash 2>/dev/null || true

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

# Full update-progress workflow (update progress.json, commit, push)
update-progress:
    @echo "🔄 Running full update-progress workflow..."
    @bash .claude/commands/update-progress.sh


# Build for production
build:
    @echo "🏗️ Building for production..."
    cd frontend && npm run build
    cd backend && {{uv}} build

# Context Management Commands
context-validate:
    @echo "🔍 Validating Claude context structure..."
    {{python}} scripts/context/validate_context.py

token-analyze path=".claude/":
    @echo "📊 Analyzing token usage in {{path}}..."
    {{python}} scripts/context/analyze_token_usage.py {{path}}

context-check:
    @echo "🏥 Claude Context Full Check"
    @just context-validate
    @echo "\n📊 Token Usage Analysis:"
    @just token-analyze .claude/core/
    @just token-analyze .claude/modules/

# Docker commands
docker-up:
    docker-compose up -d

docker-down:
    docker-compose down

docker-logs:
    docker-compose logs -f

# View Docker service logs (accepts optional service name)
logs service="":
    @if [ -z "{{service}}" ]; then \
        echo "🔍 Viewing all service logs..."; \
        docker-compose logs -f; \
    else \
        echo "🔍 Viewing logs for {{service}}..."; \
        docker-compose logs -f {{service}}; \
    fi

docker-clean:
    docker-compose down -v
    docker system prune -f

# Show current epic status
epic-status:
    @echo "📊 Current Epic Status:"
    @echo "✅ Epic 1: Project Setup - Complete"
    @echo "🚧 Epic 2: Data Import - 90% Complete (I12 parser ready, MHD pending)"
    @echo "  ✅ I12 streaming parser (360K+ records)"
    @echo "  ✅ Multi-tier caching system"
    @echo "  ✅ Database optimizations"
    @echo "  🚧 MidsReborn MHD integration pending"
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

# Open Python REPL with backend environment
backend-shell:
    @echo "🐍 Opening Python REPL with backend environment..."
    cd backend && {{uv}} run python -i -c "import sys; sys.path.insert(0, '.'); from app.database import get_db; from app.models import *; print('Backend environment loaded. Database session available via get_db()')"

# Git workflow commands
git-validate:
    @bash .claude/commands/validate-git-workflow.sh

git-feature name:
    @echo "🌿 Creating feature branch..."
    @git checkout -b feature/{{name}}
    @echo "✅ Created branch: feature/{{name}}"

git-fix name:
    @echo "🔧 Creating fix branch..."
    @git checkout -b fix/{{name}}
    @echo "✅ Created branch: fix/{{name}}"

git-pr:
    @echo "🔀 Creating pull request..."
    @bash .claude/commands/validate-git-workflow.sh || exit 1
    @gh pr create

# Session Management Commands
session-summarize:
    @echo "📝 Generating session summary..."
    {{python}} scripts/context/session_summarizer.py test

session-status:
    @echo "📊 Session status..."
    {{python}} scripts/context/auto_summarizer.py status

session-continue session_id="":
    @echo "🔄 Continuing session {{session_id}}..."
    {{python}} scripts/context/session_continuity.py continue {{session_id}}

session-list:
    @echo "📋 Recent sessions..."
    {{python}} scripts/context/session_continuity.py list

threshold-config:
    @echo "⚙️ Threshold configuration..."
    {{python}} scripts/context/threshold_config.py config

threshold-set key value:
    @echo "⚙️ Setting threshold {{key}} = {{value}}..."
    {{python}} scripts/context/threshold_config.py set {{key}} {{value}}

summary-validate summary_file:
    @echo "✅ Validating summary quality..."
    {{python}} scripts/context/summary_validator.py validate {{summary_file}}

# RAG System Commands
rag-setup:
    @echo "🔧 Setting up RAG system..."
    @if [ ! -f backend/.env ] && [ -f backend/.env.example ]; then cp backend/.env.example backend/.env; fi
    @echo "⚠️  Please edit backend/.env and add your GEMINI_API_KEY"
    @echo "✅ RAG setup complete"

rag-test-auth:
    @echo "🔐 Testing Gemini API authentication..."
    cd backend && {{python}} -m app.rag.cli embed -t "test connection"

rag-init-db:
    @echo "🗄️ Initializing ChromaDB collections..."
    cd backend && {{python}} -m app.rag.cli status

rag-index path collection="mids_hero_codebase":
    @echo "📥 Indexing {{path}} into {{collection}}..."
    cd backend && {{python}} -m app.rag.cli index codebase {{path}} -p "**/*.py" -p "**/*.ts" -p "**/*.tsx" -p "**/*.md"

rag-search query collection="mids_hero_codebase" limit="5":
    @echo "🔍 Searching for: {{query}}..."
    cd backend && {{python}} -m app.rag.cli search -q "{{query}}" -c {{collection}} -n {{limit}}

rag-status:
    @echo "📊 RAG system status..."
    cd backend && {{python}} -m app.rag.cli status

rag-usage days="7":
    @echo "📈 Usage report for {{days}} days..."
    cd backend && {{python}} -m app.rag.cli usage -d {{days}}

rag-embed text:
    @echo "🧮 Generating embedding..."
    cd backend && {{python}} -m app.rag.cli embed -t "{{text}}"

rag-index-codebase:
    @echo "📚 Indexing entire codebase..."
    cd backend && {{python}} -m app.rag.cli index -p {{project_root}} -c mids_hero_codebase -g "**/*.py" -g "**/*.ts" -g "**/*.tsx" -g "**/*.md"

rag-index-midsreborn:
    @echo "📚 Indexing MidsReborn codebase..."
    cd backend && {{python}} -m app.rag.cli index -p {{project_root}}/external/dev/MidsReborn -c midsreborn_docs -g "**/*.cs" -g "**/*.md"

rag-reset-collection collection:
    @echo "🗑️ Resetting collection {{collection}}..."
    cd backend && {{python}} -m app.rag.cli reset -c {{collection}} --yes

# Help - show this message
help:
    @echo "Mids Hero Web Development Commands"
    @echo "================================="
    @echo ""
    @echo "🚀 Quick Start:"
    @echo "  just quickstart           # Initial setup"
    @echo "  just dev                  # Start all services"
    @echo ""
    @echo "🌿 Git Workflow:"
    @echo "  just git-validate         # Check Git workflow"
    @echo "  just git-feature NAME     # Create feature branch"
    @echo "  just git-fix NAME         # Create fix branch"
    @echo "  just git-pr               # Create pull request"
    @echo ""
    @echo "📥 Data Import:"
    @echo "  just import-all DIR       # Import all data from directory"
    @echo "  just import-type TYPE FILE # Import specific type"
    @echo "  just import-archetypes FILE"
    @echo "  just import-powers FILE"
    @echo ""
    @echo "📊 System Status:"
    @echo "  just import-status        # Import system status"
    @echo "  just import-stats         # Database record counts"
    @echo "  just cache-stats          # Cache performance"
    @echo ""
    @echo "⚡ Performance:"
    @echo "  just db-optimize          # Database optimization"
    @echo ""
    @echo "🗄️ Database:"
    @echo "  just db-setup             # Database setup"
    @echo "  just db-migrate           # Run migrations"
    @echo "  just db-status            # Migration status"
    @echo ""
    @echo "🤖 Session Management:"
    @echo "  just session-summarize    # Generate session summary"
    @echo "  just session-status       # Show session status"
    @echo "  just session-continue     # Continue previous session"
    @echo "  just session-list         # List recent sessions"
    @echo ""
    @echo "🧠 RAG System:"
    @echo "  just rag-setup            # Initial RAG setup"
    @echo "  just rag-status           # System status"
    @echo "  just rag-index-codebase   # Index project code"
    @echo "  just rag-search QUERY     # Search indexed docs"
    @echo "  just rag-usage            # Usage report"
    @echo "  just threshold-config     # Show threshold config"
    @echo ""
    @echo "For full command list:"
    @just --list