# Mids-Web: Modern Character Planner

Modern web-based rewrite of the Mids Reborn character planner for _City of Heroes_.

## 🚀 Quick Start

```bash
# 1. Clone and setup
git clone https://github.com/mids-web/mids-web.git
cd mids-web
export PROJECT_ROOT_DIR=$(git rev-parse --show-toplevel)

# 2. Run health checks
python scripts/dev.py setup

# 3. Start development
docker-compose up --build
```

See [ROADMAP.md](ROADMAP.md) for detailed development milestones and [README.md](README.md) for project overview.

## 📋 Overview

Mids-Web is a complete rewrite of the popular Mids Reborn character build planner, transforming the Windows Forms desktop application into a modern, responsive web application. The goal is to provide the same powerful build planning capabilities with improved accessibility, easier updates, and potential for new collaborative features.

### Technology Stack

- **Frontend**: React with TypeScript for responsive user interface
- **Backend**: Python with FastAPI (using `uv` for modern package management)
- **Database**: PostgreSQL with SQLAlchemy ORM and Alembic migrations
- **Authentication**: JWT-based (planned for user accounts)
- **Storage**: PostgreSQL for game data, file export/import for builds
- **API**: RESTful FastAPI with automatic OpenAPI documentation
- **Cloud Platform**: Google Cloud Platform (GCP)
- **Deployment**: Docker containers with Cloud Run (serverless)

## 🛠️ Development Setup

### Prerequisites

- Python 3.11+
- `uv` (modern Python package manager)
- Node.js 18+ (for React frontend)
- Git
- Docker and Docker Compose
- PostgreSQL (for local development outside Docker)

### Environment Setup

```bash
# 1. Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Set up backend dependencies
cd backend
uv sync  # Creates virtual environment and installs dependencies

# 3. Set up frontend dependencies
cd ../frontend
npm install

# 4. Set up environment variables
cp .env.example .env
# Edit .env with your database URL and other configuration

# 5. Start development environment
cd ..
docker-compose up --build
```

### Daily Development Workflow

```bash
# Always start with setup/health checks
python scripts/dev.py setup

# Start all services via Docker
docker-compose up --build

# Or run backend directly
python scripts/dev.py run

# Run tests
python scripts/dev.py test

# Run database migrations
python scripts/dev.py migrate

# Format and lint code
python scripts/dev.py format
python scripts/dev.py lint

# Clean up build artifacts
python scripts/dev.py clean
```

## 🏗️ Project Structure

```
mids-web/
├── backend/                   # FastAPI Python application
│   ├── app/                  # Application code
│   │   ├── routers/         # API route handlers
│   │   ├── models.py        # Database models
│   │   ├── schemas.py       # Pydantic schemas
│   │   ├── crud.py          # Database operations
│   │   └── database.py      # Database configuration
│   ├── main.py              # FastAPI entry point
│   └── pyproject.toml       # Python dependencies & config
├── frontend/                  # React TypeScript application
│   ├── src/                 # Source code
│   │   ├── components/      # React components
│   │   ├── services/        # API service layer
│   │   └── App.tsx          # Main application component
│   ├── public/              # Static assets
│   └── package.json         # Node.js dependencies
├── alembic/                   # Database migrations
│   ├── versions/            # Migration files
│   ├── env.py              # Alembic configuration
│   └── alembic.ini         # Alembic settings
├── scripts/                   # Development and utility scripts
│   └── dev.py              # Main development helper
├── docs/                      # Documentation (future)
├── ROADMAP.md                # Development roadmap
├── CLAUDE.md                 # This file - Core development instructions
└── README.md                 # Project overview
```

## 🧪 Testing

```bash
# Run all backend tests with coverage
python scripts/dev.py test

# Backend tests directly
cd backend
uv run pytest -v --cov=app

# Frontend tests
cd frontend
npm test

# Specific test files
cd backend
uv run pytest tests/test_api.py -v

# Integration tests with Docker
docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit
```

## 🚦 Development Standards

1. **Branch Strategy**: Create feature branches from `main`

   ```bash
   git checkout main && git pull
   git checkout -b feature/epic-{number}-{description}
   ```

2. **Code Quality**: Use `uv` with automated tools

   ```bash
   # Format code
   python scripts/dev.py format

   # Lint and type check
   python scripts/dev.py lint

   # Pre-commit checks
   uv run ruff check --fix .
   uv run black .
   uv run mypy .
   ```

3. **Commit Standards**: Use conventional commits aligned with roadmap epics

   - `feat:` New feature implementation
   - `fix:` Bug fix
   - `docs:` Documentation changes
   - `test:` Test additions/changes
   - `refactor:` Code refactoring
   - `data:` Game data updates

4. **Test-Driven Development**: Write tests first, especially for API endpoints and calculations

## 🎮 Game Data Architecture

Modern approach to City of Heroes data management:

- **Data Import**: Python scripts to convert original .mhd files to PostgreSQL
- **API Endpoints**: RESTful access to archetypes, powersets, powers, enhancements
- **Calculations**: Server-side build validation and statistics computation
- **Caching**: Efficient data serving with potential Redis integration
- **Updates**: Automated data pipeline for new game versions

## 📚 Documentation

- **[CLAUDE.md](CLAUDE.md)** - 🚨 **START HERE** - Core development workflow
- **[README.md](README.md)** - Project overview and quick start
- **[ROADMAP.md](ROADMAP.md)** - Detailed development plan with 6 epics
- **[backend/pyproject.toml](backend/pyproject.toml)** - Python dependencies and tool configuration

## 🔧 Common Commands

```bash
# Development helper (shows all available commands)
python scripts/dev.py

# Database operations
cd backend
uv run alembic upgrade head              # Run migrations
uv run alembic revision --autogenerate -m "description"  # Create migration

# Docker operations
docker-compose up --build               # Start all services
docker-compose logs -f backend          # View backend logs
docker-compose down -v                  # Stop and remove volumes

# Frontend operations
cd frontend
npm start                               # Start development server
npm run build                           # Build for production
npm test                                # Run tests

# API testing
curl http://localhost:8000/ping         # Health check
curl http://localhost:8000/docs         # API documentation
```

## 🚢 Deployment

The project uses Docker for containerized deployment:

- **Development**: Docker Compose with hot-reload
- **Production**: Multi-stage Dockerfile with optimized builds
- **Cloud**: Google Cloud Platform with Cloud Run
- **CI/CD**: GitHub Actions (to be implemented)

Current deployment targets:

- **Local**: `docker-compose up --build`
- **Cloud**: GCP Cloud Run with Cloud SQL PostgreSQL

## 🛡️ Security

- Environment variables for all configuration
- No hardcoded API keys or database credentials
- Non-root Docker containers
- CORS configuration for API access
- Input validation with Pydantic schemas

## 🤝 Contributing

1. Read [ROADMAP.md](ROADMAP.md) for current development priorities
2. Create feature branch aligned with roadmap epics
3. Write tests first (TDD approach)
4. Ensure all checks pass: `python scripts/dev.py test`
5. Submit PR with clear description referencing roadmap tasks

## 📊 Current Status

Following the [6-epic roadmap](ROADMAP.md):

- **Epic 1**: ✅ Project Setup and Planning (Complete)
- **Epic 2**: 🚧 Data Model & Database Integration (In Progress)
- **Epic 3**: 📋 Backend API Development (Next)
- **Epic 4**: 📋 Frontend Application Implementation (Planned)
- **Epic 5**: 📋 Deployment and DevOps (Planned)
- **Epic 6**: 📋 Optimization and Feature Enhancements (Future)

**MVP Target**: Functional character build planner with Homecoming 2025.7.1111 database

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

_Mids-Web is not affiliated with or endorsed by NCSoft or the original City of Heroes development team._

---

<!-- Auto-generated development notes -->

## Development Setup

This project uses modern Python tooling with two main approaches:

### Daily Development

Use `scripts/dev.py` for common development tasks:

- Setting up Python environment with `uv`
- Installing dependencies
- Running the development server
- Database migrations
- Code formatting and linting

### Container Development

Use `docker-compose up --build` for:

- Full-stack development environment
- Database with sample data
- Hot-reload for both frontend and backend
- Consistent environment across team members

New developers should start with the Quick Start section and use `python scripts/dev.py setup` for initial environment configuration.
