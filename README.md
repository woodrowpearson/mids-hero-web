# Mids Hero Web

> **A modern, web-based character build planner for City of Heroes**
>
> Replacing the legacy Mids Reborn Windows application with a React/FastAPI stack, powered by AI-assisted development.

[![CI Status](https://github.com/woodrowpearson/mids-hero-web/workflows/CI/badge.svg)](https://github.com/woodrowpearson/mids-hero-web/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![React 19](https://img.shields.io/badge/react-19-61dafb.svg)](https://reactjs.org/)

---

## 📖 Table of Contents

- [What is Mids Hero Web?](#what-is-mids-hero-web)
- [Problem We're Solving](#problem-were-solving)
- [Architecture](#architecture)
  - [Tech Stack](#tech-stack)
  - [System Architecture](#system-architecture)
  - [Data Model](#data-model)
- [Quick Start](#quick-start)
- [Development](#development)
- [Project Status](#project-status)
- [Contributing](#contributing)
- [License](#license)

---

## What is Mids Hero Web?

Mids Hero Web is a **modern web application** that brings the powerful character build planning capabilities of **Mids Reborn** to the browser.

### Features

- ✅ **Character Archetypes**: Select from all City of Heroes archetypes (Blaster, Controller, Defender, etc.)
- ✅ **Power Selection**: Browse and select powers from primary/secondary/pool powersets
- ✅ **Enhancement Slotting**: Plan enhancement slots with accurate set bonuses
- ✅ **Build Statistics**: Calculate damage, resistance, defense, recharge, and more
- 🚧 **Build Import/Export**: Import existing Mids builds (coming soon)
- 🚧 **Cloud Saving**: Save and share builds online (coming soon)
- 📋 **Real-time Validation**: Ensure builds follow game rules (planned)

### For Players

- **Browser-based**: No installation required
- **Cross-platform**: Works on Windows, Mac, Linux, mobile
- **Always up-to-date**: Game data synced from servers
- **Shareable**: Send build links to teammates

### For Developers

- **Modern stack**: React 19, FastAPI, PostgreSQL
- **AI-assisted**: Specialized Claude agents for each domain
- **Well-tested**: TDD approach with comprehensive test coverage
- **Well-documented**: Extensive documentation in `.claude/` and `docs/`

---

## Problem We're Solving

### The Legacy Tool: Mids Reborn

[Mids Reborn](https://github.com/LoadedCamel/MidsReborn) is a **Windows Forms desktop application** (fork of the original Mids' Hero Designer) that has been the gold standard for City of Heroes build planning since 2006.

**Limitations**:
- ❌ Windows-only (requires Wine/compatibility layers on Mac/Linux)
- ❌ Desktop installation required
- ❌ Binary `.mhd` file format (not web-compatible)
- ❌ Manual updates needed for game data changes
- ❌ No cloud saving or sharing
- ❌ Aging C# Windows Forms codebase

### Our Solution: Mids Hero Web

**Goals**:
- ✅ **Web-native**: Run in any modern browser
- ✅ **Cross-platform**: Windows, Mac, Linux, mobile
- ✅ **Modern UX**: React 19 with responsive design
- ✅ **Live data**: Automatic updates from game servers
- ✅ **Cloud builds**: Save and share builds online
- ✅ **Maintainable**: Modern TypeScript/Python stack

---

## Architecture

### Tech Stack

```mermaid
graph TB
    subgraph "Frontend"
        React[React 19 + TypeScript]
        MUI[Material-UI]
        Vite[Vite Build Tool]
    end

    subgraph "Backend"
        FastAPI[FastAPI]
        SQLAlchemy[SQLAlchemy ORM]
        Pydantic[Pydantic Schemas]
    end

    subgraph "Data Layer"
        PostgreSQL[(PostgreSQL)]
        Alembic[Alembic Migrations]
        Redis[(Redis Cache)]
    end

    subgraph "Data Source"
        CityOfData[city_of_data JSON]
        Homecoming[Homecoming Server]
    end

    subgraph "Infrastructure"
        Docker[Docker]
        GHA[GitHub Actions]
        Claude[Claude AI Agents]
    end

    React -->|REST API| FastAPI
    FastAPI --> SQLAlchemy
    SQLAlchemy --> PostgreSQL
    FastAPI -.->|Caching| Redis
    PostgreSQL --> Alembic

    CityOfData -->|Import| FastAPI
    Homecoming -->|Updates| CityOfData

    Docker --> React
    Docker --> FastAPI
    Docker --> PostgreSQL

    GHA -->|CI/CD| Docker
    Claude -.->|Assists| GHA
    Claude -.->|Assists| React
    Claude -.->|Assists| FastAPI

    style React fill:#61dafb
    style FastAPI fill:#009688
    style PostgreSQL fill:#336791
    style Claude fill:#ff9900
    style CityOfData fill:#90ee90
```

### System Architecture

```mermaid
graph LR
    subgraph "Client Tier"
        Browser[Web Browser]
    end

    subgraph "Application Tier"
        API[FastAPI Backend]
        Cache[(Redis)]
    end

    subgraph "Data Tier"
        DB[(PostgreSQL)]
        DataSource[city_of_data JSON]
    end

    subgraph "AI Development"
        Agents[Claude Sub-Agents]
        GH[GitHub Actions]
    end

    Browser -->|HTTPS| API
    API -->|Query| Cache
    Cache -.->|Cache Miss| DB
    API -->|ORM| DB

    DataSource -->|Import Script| DB

    Agents -.->|Assists| API
    Agents -.->|Assists| Browser
    GH -->|CI/CD| API
    GH -->|CI/CD| Browser

    style Browser fill:#61dafb
    style API fill:#009688
    style DB fill:#336791
    style Agents fill:#ff9900
```

### Data Model

#### Source: city_of_data Repository

We use the [city_of_data GitLab repository](https://gitlab.com/bearcano/coh-content-db-homecoming), which provides **JSON exports** of City of Heroes game data directly from the Homecoming server.

**Data Location**: `/Users/w/code/mids-hero-web/external/city_of_data/raw_data_homecoming-20250617_6916`

```mermaid
graph TB
    subgraph "city_of_data JSON Structure"
        Archetypes[archetypes/]
        Powers[powers/]
        BoostSets[boost_sets/]
        Entities[entities/]
        EntityTags[entity_tags/]
        Tables[tables/]
    end

    subgraph "Database Schema"
        AT[Archetype]
        PS[Powerset]
        P[Power]
        E[Enhancement]
        ES[EnhancementSet]
        B[Boost]
    end

    Archetypes -->|Import| AT
    Powers -->|Import| P
    Powers -->|Import| PS
    BoostSets -->|Import| ES
    BoostSets -->|Import| E
    Entities -->|Import| B

    AT -->|1:N| PS
    PS -->|1:N| P
    P -->|N:M| E
    E -->|N:1| ES
    P -->|N:M| B

    style Archetypes fill:#90ee90
    style Powers fill:#90ee90
    style BoostSets fill:#90ee90
    style AT fill:#336791
    style PS fill:#336791
    style P fill:#336791
```

#### Import Flow

```mermaid
sequenceDiagram
    participant Script as Import Script
    participant JSON as city_of_data JSON
    participant Parser as Streaming Parser
    participant Cache as Redis Cache
    participant DB as PostgreSQL

    Script->>JSON: Read JSON file
    JSON->>Parser: Stream chunks
    Parser->>Cache: Check cache
    Cache-->>Parser: Cache miss
    Parser->>DB: Batch insert (1000 records)
    DB-->>Parser: Success
    Parser->>Cache: Update cache
    Parser->>Script: Progress update

    Note over Script,DB: Processes 360K+ records<br/>in <1GB memory
```

#### Database Schema (Simplified)

```mermaid
erDiagram
    ARCHETYPE ||--o{ POWERSET : "has"
    POWERSET ||--o{ POWER : "contains"
    POWER ||--o{ POWER_EFFECT : "applies"
    POWER }o--o{ ENHANCEMENT : "accepts"
    ENHANCEMENT }o--|| ENHANCEMENT_SET : "belongs_to"
    ENHANCEMENT_SET ||--o{ SET_BONUS : "grants"

    ARCHETYPE {
        int id PK
        string name
        string display_name
        int hit_points
        float damage_scale
    }

    POWERSET {
        int id PK
        int archetype_id FK
        string name
        string full_name
        string type
    }

    POWER {
        int id PK
        int powerset_id FK
        string name
        string description
        int level_available
        int num_allowed_enhancements
        float accuracy
        float endurance_cost
        float recharge_time
    }

    ENHANCEMENT {
        int id PK
        int enhancement_set_id FK
        string name
        string type
        jsonb modifiers
    }

    ENHANCEMENT_SET {
        int id PK
        string name
        int min_level
        int max_level
    }
```

---

## Quick Start

### Prerequisites

- **Docker** and **Docker Compose**
- **just** command runner - [Install](https://github.com/casey/just)
- **Node.js 18+**
- **Python 3.11+**
- **uv** (Python package manager) - [Install](https://docs.astral.sh/uv/)

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/woodrowpearson/mids-hero-web.git
   cd mids-hero-web
   ```

2. **Run quick start**:
   ```bash
   just quickstart
   ```

   This will:
   - Start PostgreSQL in Docker
   - Run database migrations
   - Install Python dependencies with uv
   - Install Node.js dependencies
   - Verify setup

3. **Start development servers**:
   ```bash
   just dev
   ```

4. **Access the application**:
   - **Frontend**: http://localhost:3000
   - **Backend API**: http://localhost:8000
   - **API Docs**: http://localhost:8000/docs

---

## Development

### Essential Commands

```bash
# Development
just dev            # Start all services
just health         # Run health checks
just test           # Run all tests
just quality        # Code quality checks
just lint-fix       # Auto-fix linting issues

# Database
just db-setup       # Complete database setup
just db-migrate     # Run migrations
just db-reset       # Reset database
just db-connect     # PostgreSQL shell

# Data Import
just import-all data-directory         # Import all data types
just i12-import data.json              # High-performance I12 import
just import-health                     # System health check
just cache-stats                       # Cache performance

# Git Workflow
git checkout -b feature/issue-XXX      # Create feature branch
just ucp "message"                     # Quick commit
just update-progress                   # Update progress tracking
git push -u origin feature/issue-XXX   # Push branch
gh pr create                           # Create pull request
```

### Project Structure

```
mids-hero-web/
├── frontend/              # React 19 + TypeScript
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── services/     # API service layer
│   │   └── types/        # TypeScript definitions
│   └── package.json
│
├── backend/              # FastAPI application
│   ├── app/
│   │   ├── models.py     # SQLAlchemy models
│   │   ├── schemas.py    # Pydantic schemas
│   │   ├── crud.py       # Database operations
│   │   └── commands/     # CLI commands
│   ├── main.py           # FastAPI entry point
│   └── pyproject.toml    # Python dependencies
│
├── alembic/              # Database migrations
├── scripts/              # Development scripts
├── .claude/              # AI agent configuration
├── .github/              # CI/CD workflows
└── docs/                 # Documentation
```

### Development Workflow

1. **Create feature branch**:
   ```bash
   git checkout -b feature/description
   ```

2. **Run health check before starting**:
   ```bash
   just health
   ```

3. **Make changes and test**:
   ```bash
   just test
   just lint-fix
   ```

4. **Commit and push**:
   ```bash
   just ucp "feat: add power selection UI"
   git push -u origin feature/description
   ```

5. **Create pull request**:
   ```bash
   gh pr create
   ```

6. **AI Review**: Claude will automatically review your PR

### AI-Assisted Development

This project uses **Claude Code native sub-agents** for specialized assistance:

- **Database Specialist**: Schema design, migrations, query optimization
- **Backend Specialist**: FastAPI endpoints, Pydantic schemas
- **Frontend Specialist**: React components, TypeScript, UI/UX
- **Import Specialist**: Data import, city_of_data integration
- **Testing Specialist**: pytest, Vitest, E2E tests
- **DevOps Specialist**: Docker, CI/CD, deployment
- **Calculation Specialist**: Game mechanics, damage calculations
- **Documentation Specialist**: Maintaining docs

**Usage**:
- Tell Claude your task: "I need to work on database migrations"
- Claude automatically loads the appropriate specialist context
- Get domain-specific guidance and code suggestions

---

## Project Status

### Current Progress

| Epic | Status | Progress | Description |
|------|--------|----------|-------------|
| **Epic 1** | ✅ Complete | 100% | Project setup, CI/CD, Docker |
| **Epic 2** | ✅ Complete | 100% | Data model, database, JSON import |
| **Epic 2.5** | ✅ Complete | 100% | AI agents, workflows, optimization |
| **Epic 3** | 🚧 In Progress | 25% | Backend API endpoints |
| **Epic 4** | 📋 Planned | 0% | Frontend React UI |
| **Epic 5** | 📋 Planned | 0% | Deployment to GCP |
| **Epic 6** | 📋 Planned | 0% | Performance optimization |

### Completed Milestones

#### ✅ Epic 1: Project Setup (July 2025)
- Git repository and structure
- React 19 frontend scaffold
- FastAPI backend with SQLAlchemy
- Docker development environment
- GitHub Actions CI/CD
- Database migrations with Alembic

#### ✅ Epic 2: Data Import (July-August 2025)
- ~~Binary MHD parser (abandoned)~~
- ~~MidsReborn DataExporter (abandoned)~~
- JSON-native import from city_of_data
- High-performance streaming parser (360K+ records)
- Multi-tier caching (LRU + Redis)
- Database optimizations (composite indexes, GIN indexes)

#### ✅ Epic 2.5: AI-Assisted Development (August-October 2025)
- Native Claude sub-agents (8 specialists)
- GitHub Actions optimization (40% performance gain)
- Automated documentation sync
- Context health monitoring
- RAG implementation (completed, later archived)

#### 🚧 Epic 3: Backend API (October 2025 - Current)
- ✅ Core data endpoints (GET /api/archetypes, powers, etc.)
- 🚧 Build simulation endpoints
- 🚧 Calculation logic
- 📋 Write/modify operations

### Next Steps

1. **Complete Epic 3**: Finish backend API endpoints
2. **Start Epic 4**: Build React UI for power selection
3. **Epic 5 Planning**: Design GCP deployment architecture
4. **Community Feedback**: Gather feedback from CoH players

---

## Contributing

We welcome contributions! Please see our [development roadmap](docs/PROJECT_EVOLUTION.md) for current priorities.

### How to Contribute

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Use just commands**: `just health`, `just test`, `just lint-fix`
4. **Commit changes**: `just ucp "Add amazing feature"`
5. **Push branch**: `git push origin feature/amazing-feature`
6. **Open Pull Request**: Claude will automatically review

### Development Guidelines

- **Use feature branches**: Never commit directly to `main`
- **Write tests**: TDD approach preferred
- **Follow conventions**: ESLint, Black, Prettier
- **Document changes**: Update relevant docs
- **Run quality checks**: `just quality` before pushing

### AI Assistance

- Use **@claude** in PR comments for help
- Claude will review for City of Heroes domain accuracy
- Automated documentation updates

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- **Mids Reborn** team for the original desktop application
- **LoadedCamel** for maintaining Mids Reborn
- **City of Heroes** community for continued support
- **Homecoming** and **Rebirth** server teams for game data
- **bearcano** for the city_of_data repository

---

## Support

For support, please:

- Check the [documentation](docs/)
- Open an issue on GitHub
- Join our Discord server (coming soon)

---

_Mids Hero Web is not affiliated with or endorsed by NCSoft or the original City of Heroes development team._

**Project Links**:
- GitHub: https://github.com/woodrowpearson/mids-hero-web
- Mids Reborn: https://github.com/LoadedCamel/MidsReborn
- city_of_data: https://gitlab.com/bearcano/coh-content-db-homecoming
- City of Heroes Homecoming: https://homecoming.wiki/
