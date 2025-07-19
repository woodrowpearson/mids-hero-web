# Mids Web Backend

FastAPI backend for the Mids Hero Web character planner.

## Overview

This backend provides the REST API for the Mids Hero Web application, handling:
- Game data serving (archetypes, powersets, powers, enhancements)
- High-performance data import (360K+ records with I12 streaming parser)
- Multi-tier caching for <100ms query performance
- Build calculations and validation
- Character build storage and retrieval
- Authentication and user management (planned)

## Tech Stack

- **FastAPI** - Modern async web framework
- **SQLAlchemy 2.0** - ORM with async support  
- **PostgreSQL** - Primary database
- **Alembic** - Database migrations
- **Pydantic** - Data validation

## Development

```bash
# Install dependencies
uv sync

# Run development server
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Run tests
uv run pytest

# Run linting
uv run ruff check .
uv run mypy .
```

## API Documentation

When running, visit:
- API docs: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc

## Project Structure

```
backend/
├── app/
│   ├── routers/      # API endpoints
│   ├── models.py     # Database models
│   ├── schemas.py    # Pydantic schemas
│   ├── crud.py       # Database operations
│   └── database.py   # Database configuration
├── alembic/          # Database migrations
├── tests/            # Test suite
└── main.py           # Application entry point
```

## Environment Variables

Create a `.env` file with:

```
DATABASE_URL=postgresql://user:password@localhost/dbname
SECRET_KEY=your-secret-key
API_HOST=0.0.0.0
API_PORT=8000
```

## Database Setup

```bash
# Run migrations
uv run alembic upgrade head

# Create new migration
uv run alembic revision --autogenerate -m "description"
```

## Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=app

# Run specific test file
uv run pytest tests/test_api.py
```

## Data Import

The backend includes a comprehensive data import system for City of Heroes game data.

### Import Types

- **Archetypes** - Character classes (Blaster, Controller, etc.)
- **Powersets** - Power collections for each archetype
- **Powers** - Individual powers with effects and requirements
- **Enhancements** - Enhancement sets and IOs
- **Salvage** - Crafting components
- **Recipes** - Enhancement crafting recipes
- **Attribute Modifiers** - Character attribute modifications
- **Type Grades** - Archetype-specific scaling factors

### Import Methods

**Using justfile commands (recommended):**
```bash
# Import all data from directory
just import-all /path/to/exported-json-latest

# Import specific types
just import-archetypes /path/to/I9_structured.json
just import-powers /path/to/I9_structured.json

# High-performance I12 import (360K+ records)
just i12-import /path/to/I12_powers.json

# Check system status
just import-health
just import-stats
```

**Using CLI directly:**
```bash
# Import all data files
uv run python -m app.data_import.cli all /path/to/data

# Import specific type
uv run python -m app.data_import.cli powers /path/to/powers.json

# High-performance I12 import
uv run python scripts/import_i12_data.py /path/to/I12_data.json
```

### Performance Features

- **I12 Streaming Parser**: Handles 360K+ records within 1GB memory
- **Multi-tier Caching**: LRU + Redis for <100ms queries
- **Database Optimization**: Composite indexes, GIN indexes, materialized views
- **Resume Capability**: Restart failed imports from any point
- **Batch Processing**: Configurable batch sizes for optimal performance

### Import Order

Due to foreign key dependencies, import data in this order:
1. Archetypes → 2. Powersets → 3. Powers → 4. Enhancements → 5. Salvage → 6. Recipes

The `import-all` command handles this automatically.

## Contributing

1. Create feature branch from `main`
2. Write tests for new functionality
3. Ensure all tests pass
4. Run linting and fix issues
5. Submit PR with clear description

See the main project README for more details.