# Database Migration Issues and Solutions

## 🚨 Problems Encountered During Task 2.1.3

### Issue 1: PostgreSQL Connection Failures
**Error**: `FATAL: role "postgres" does not exist`

**Root Cause**: Multiple PostgreSQL instances were running simultaneously:
- System PostgreSQL installed via Homebrew (port 5432)
- Docker PostgreSQL container (also trying to use port 5432)

**Symptoms**:
```bash
psycopg2.OperationalError: connection to server at "localhost" (::1), port 5432 failed: FATAL: role "postgres" does not exist
```

**Solution Applied**:
1. Stopped system PostgreSQL: `brew services stop postgresql@14`
2. Verified Docker container was accessible: `docker exec mids-hero-web-db-1 psql -U postgres -d mids_web -c "SELECT current_user;"`
3. Used explicit DATABASE_URL in Alembic commands: `DATABASE_URL=postgresql://postgres:postgres@localhost:5432/mids_web`

### Issue 2: Docker Build Failures
**Error**: `uv: not found` in Docker build process

**Root Cause**: The `uv` package manager was not properly installed in the Docker image PATH.

**Symptoms**:
```bash
/bin/sh: 1: uv: not found
ERROR: process "/bin/sh -c uv venv .venv && uv sync --no-dev" did not complete successfully: exit code 127
```

**Workaround**: Started only the database container for migration purposes instead of full development environment.

### Issue 3: Alembic Migration Tracking
**Problem**: After manually applying schema, Alembic was not tracking the migration as applied.

**Solution**: Used `alembic stamp head` to mark the migration as applied in the tracking table.

## 🔧 Recommended Fixes

### 1. Docker Configuration Issues

#### Problem: Current docker-compose.yml has build issues
The current Dockerfile has problems with `uv` installation that prevent the full development environment from starting.

#### Fix 1: Update Dockerfile for proper uv installation
```dockerfile
# Current problematic section:
RUN apt-get update && apt-get install -y curl &&     curl -LsSf https://astral.sh/uv/install.sh | sh &&     rm -rf /var/lib/apt/lists/*

# Fixed version:
RUN apt-get update && apt-get install -y curl && \
    curl -LsSf https://astral.sh/uv/install.sh | sh && \
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc && \
    export PATH="$HOME/.local/bin:$PATH" && \
    rm -rf /var/lib/apt/lists/*
```

#### Fix 2: Use multi-stage build approach
```dockerfile
# Development stage with proper uv setup
FROM python:3.11-slim as backend-dev

# Install uv with proper PATH setup
RUN apt-get update && apt-get install -y curl && \
    curl -LsSf https://astral.sh/uv/install.sh | sh && \
    ln -s ~/.local/bin/uv /usr/local/bin/uv && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app/backend
COPY backend/pyproject.toml backend/README.md backend/uv.lock ./
RUN uv venv .venv && uv sync --no-dev
```

### 2. PostgreSQL Configuration Strategy

#### Option A: Docker-Only PostgreSQL (Recommended)
**Pros**: 
- Consistent environment across development and production
- No conflicts with system PostgreSQL
- Easy to reset/recreate database
- Version control of database state

**Cons**:
- Requires Docker to be running for development
- Slight performance overhead

**Implementation**: Keep current docker-compose.yml but fix the backend build issues.

#### Option B: Local PostgreSQL with Docker fallback
**Pros**:
- Better performance for development
- Can use system PostgreSQL tools directly
- No Docker dependency for database

**Cons**:
- Environment inconsistency
- Requires manual PostgreSQL setup
- Version conflicts possible

**Implementation**: 
1. Use local PostgreSQL for development
2. Use Docker PostgreSQL for CI/CD and production
3. Provide clear setup instructions for both

### 3. Recommended Solution: Hybrid Approach

#### Development Environment Setup
```bash
# Option 1: Docker-only (recommended for consistency)
just dev  # Should work after Docker fixes

# Option 2: Local PostgreSQL
brew install postgresql@15
brew services start postgresql@15
createdb mids_web
export DATABASE_URL=postgresql://postgres@localhost:5432/mids_web
```

#### Environment Variables
Create `.env` file in backend directory:
```env
# Docker environment
DATABASE_URL=postgresql://postgres:postgres@db:5432/mids_web

# Local development (alternative)
# DATABASE_URL=postgresql://postgres@localhost:5432/mids_web
```

### 4. Migration Process Improvements

#### Create migration utility script
```python
# backend/scripts/migrate.py
import os
import subprocess
import sys

def run_migration():
    """Run database migrations with proper error handling."""
    try:
        # Try Docker database first
        docker_url = "postgresql://postgres:postgres@localhost:5432/mids_web"
        subprocess.run(["alembic", "upgrade", "head"], 
                      env={**os.environ, "DATABASE_URL": docker_url}, 
                      check=True)
        print("✅ Migration completed successfully")
    except subprocess.CalledProcessError:
        print("❌ Docker migration failed, trying local PostgreSQL...")
        # Fallback to local PostgreSQL
        local_url = "postgresql://postgres@localhost:5432/mids_web"
        subprocess.run(["alembic", "upgrade", "head"], 
                      env={**os.environ, "DATABASE_URL": local_url}, 
                      check=True)
```

## 🏁 Final Recommendations

### 1. Fix Docker Configuration (High Priority)
- Update Dockerfile to properly install and configure `uv`
- Test full development environment startup
- Ensure consistent builds across platforms

### 2. Documentation Updates
- Add clear database setup instructions to README.md
- Document both Docker and local PostgreSQL options
- Include troubleshooting section for common issues

### 3. Development Workflow
- Use Docker for consistency (recommended)
- Provide local PostgreSQL option for performance-sensitive development
- Ensure migrations work in both environments

### 4. CI/CD Considerations
- Always use Docker PostgreSQL in CI/CD
- Test migrations in both environments
- Use consistent database URLs across environments

## 🔍 Immediate Next Steps

1. **Fix Docker build issues** to make `just dev` work reliably
2. **Add database setup documentation** to project README
3. **Test migration process** in both Docker and local environments
4. **Update justfile** with database management commands

This will prevent future developers from encountering the same PostgreSQL connection issues and provide clear paths for different development preferences.