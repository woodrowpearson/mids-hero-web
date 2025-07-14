# Mids Web Backend

FastAPI backend for the Mids Hero Web character planner.

## Overview

This backend provides the REST API for the Mids Hero Web application, handling:
- Game data serving (archetypes, powersets, powers, enhancements)
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

## Contributing

1. Create feature branch from `main`
2. Write tests for new functionality
3. Ensure all tests pass
4. Run linting and fix issues
5. Submit PR with clear description

See the main project README for more details.