# API Module Guide
Last Updated: 2025-11-19 20:27:56 UTC

## Quick Reference

```bash
# Start development server
just dev

# Run backend tests only
cd backend && uv run pytest -v

# API docs
http://localhost:8000/docs
```

## Service Layout

```
backend/
├── main.py           # Application entry
└── app/
    ├── routers/      # Endpoint definitions
    ├── schemas.py    # Pydantic models
    ├── crud.py       # Database operations
    └── database.py   # DB configuration
```

## Endpoint Pattern

- Prefix all routes with `/api`.
- Use APIRouter per resource in `app/routers`.
- Response models defined in `schemas.py`.

### Example Endpoint

```python
@router.get("/powers/{power_id}", response_model=schemas.Power)
async def get_power(power_id: int, db: Session = Depends(get_db)):
    power = crud.get_power(db, power_id=power_id)
    if power is None:
        raise HTTPException(status_code=404, detail="Power not found")
    return power
```

## Authentication

- JWT-based auth planned via `fastapi.security`.
- Protect routes using dependency injection once implemented.

---
*See `.claude/modules/api/specification.md` for endpoint details.*
