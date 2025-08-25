# Backend Directory Structure Clarification

## Current State (As of Epic 2.5.5)

### Directory Naming Issue
- **`legacy-backend/`** - MISLEADING NAME! This is the **CURRENT, ACTIVE** backend
  - Modern FastAPI/SQLAlchemy/PostgreSQL implementation
  - Uses JSON data from `external/city_of_data/`
  - Contains I12 parser, RAG system, all active development
  - Should be renamed to `backend/` or `api/` for clarity

### What Was Actually "Legacy"
- The old .NET/C# backend code (now removed)
- The MHD binary file format (replaced with JSON in `external/city_of_data/`)
- The Windows Forms application (being replaced with React frontend)

## Recommended Actions

1. **Rename Directory** (Future PR):
   ```bash
   git mv legacy-backend/ backend/
   ```

2. **Update All References**:
   - GitHub Actions workflows
   - Docker configurations
   - Justfile commands
   - Documentation

## Code Reuse vs Replacement

### What's Being Reused
- All code in `legacy-backend/` (the FastAPI backend)
- Database models and schemas
- I12 parser implementation
- RAG system implementation
- API endpoints

### What Was Replaced
- MHD binary parser → JSON files
- .NET backend → FastAPI backend
- Windows Forms → React frontend (in progress)

## Summary
The `legacy-backend/` name is a historical artifact and causes confusion. 
It contains the NEW backend, not legacy code!