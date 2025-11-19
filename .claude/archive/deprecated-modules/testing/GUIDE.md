# Testing Module Guide
Last Updated: 2025-11-19 20:27:56 UTC

## Quick Reference

```bash
# Run all backend and frontend tests
just test

# Watch backend tests
just test-watch

# Coverage report
cd backend && uv run pytest --cov=app
```

## Tools

- **pytest** for Python unit tests located in `backend/tests`.
- **Jest** for React tests in `frontend/src`.
- Continuous integration runs `just quality` before merging.

## Writing Tests

- Place backend tests under `backend/tests/` and mirror the module structure.
- Use `async` test functions with `httpx.AsyncClient` for API endpoints.
- Frontend tests use React Testing Library located beside components.

---
*Testing workflow steps are in `.claude/workflows/testing.md`*
