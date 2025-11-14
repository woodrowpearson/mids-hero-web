# Changelog

All notable changes to Mids Hero Web will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project will follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html) once launched.

## [Unreleased]

### Added
- Superpowers plugin integration for structured development
- Frontend development skill for systematic UI building
- Documentation standards to prevent drift
- Bash command validator hook
- Official Anthropic plugin integration (frontend-design, code-review)

### Changed
- Modernized `.claude/` infrastructure to use native Claude Code features
- Deprecated custom modules system in favor of native context loading
- Updated all READMEs to reflect current project state

### Fixed
- Documentation drift from workflow evolution

## [0.1.0] - 2025-11-13 - Backend Complete

### Added
- FastAPI backend with 100% API coverage
- I12 streaming parser for City of Heroes data
- Database schema with PostgreSQL
- Comprehensive calculation engine with 100% test coverage
- Multi-tier caching (LRU + Redis)
- GitHub Actions CI/CD pipeline
- High-performance data import (360K+ records, <1GB memory)

### Technical Details
- Import speed: 1500 records/second
- API response time: <100ms average
- Cache hit rate: >90%
- Backend test coverage: ~85%
- Calculation test coverage: 100%

---

**Project Status**: Backend 100% complete, Frontend in development

**Tech Stack**: FastAPI, PostgreSQL, React 19, Next.js, TypeScript
