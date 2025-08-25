# API Specification
Last Updated: 2025-08-25 00:00:00 UTC

Base URL: `http://localhost:8000/api`

## Endpoints

| Method | Path | Description |
|-------|------|-------------|
| GET | `/archetypes` | List all archetypes |
| GET | `/archetypes/{id}` | Get archetype details |
| GET | `/archetypes/{id}/powersets` | Powersets for an archetype |
| GET | `/powersets` | List powersets |
| GET | `/powersets/{id}` | Get powerset details |
| GET | `/powers` | Search powers with filters |
| GET | `/powers/{id}` | Power details |
| GET | `/enhancements` | List enhancements |
| GET | `/ping` | Health check |

## Response Codes

- `200` Successful response
- `404` Resource not found
- `422` Validation error

All responses are JSON and follow Pydantic models defined in `schemas.py`.
