# Testing Workflow

Follow this routine before submitting any pull request.

## 🧪 Run Test Suite

```bash
# Execute backend and frontend tests
just test
```

## 🔁 Watch Mode

```bash
# Continuous backend testing during development
just test-watch
```

## 📊 Coverage

```bash
cd backend
uv run pytest --cov=app --cov-report=term-missing
```

Review coverage output and ensure critical paths remain tested.

## ✅ Pre-Push Checklist

1. `just quality` – linting and type checks
2. `just test` – all tests pass
3. Review coverage for regressions

---
*Reference `.claude/modules/testing/guide.md` for more details.*
