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

The backend uses JSON-based import for City of Heroes game data (MHD binary parsing deprecated in Epic 2.5.5).

### Import Methods

#### 1. JSON Import (Recommended)
```bash
# Import from City of Data JSON
just i12-import external/city_of_data/raw_data_homecoming-20250617_6916/powers.json

# Or use Python directly
python scripts/import_i12_data.py /path/to/json/file.json
```

#### 2. New JSON Import Module
```bash
# Import all data types
python -m app.json_import.cli import-all /path/to/json/directory/

# Validate before import
python -m app.json_import.cli validate --schema power powers.json
```

### Deprecated Import Types

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

# Parse I12 text format to JSON
python scripts/parse_i12_text.py I12_extracted.txt I12_powers.json

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

### Import System Architecture

**Base Importer (`app.data_import.base_importer`):**
- Abstract base class for all data importers
- Handles session management with automatic recovery from DetachedInstanceError
- Provides batch processing, validation, and error tracking
- Returns simple result objects instead of SQLAlchemy instances
- Key methods:
  - `import_data()`: Main import method with resume capability
  - `transform_data()`: Abstract method for data transformation
  - `validate_data()`: Data validation before import
  - `import_batch()`: Batch import with automatic rollback on errors

**I12 Text Parser (`scripts/parse_i12_text.py`):**
- Converts I12_extracted.txt format to importable JSON
- Handles powerset name mapping (e.g., Arachnos_Soldiers.Arachnos_Soldier → Arachnos_Soldier)
- Parses 68,417+ power records from text format
- Functions:
  - `parse_i12_text_file()`: Main entry point
  - `parse_powers_section()`: Extracts powers from I12 text
  - `parse_single_power()`: Parses individual power data

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