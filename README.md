# Mids Hero Web: Modern City of Heroes Character Build Planner

A modern web-based character build planner for City of Heroes, replacing the legacy Windows Forms application with a React/FastAPI stack. This project provides the same powerful build planning capabilities in a modern web environment with AI-assisted development workflows.

## Overview

Mids Hero Web is a complete rewrite of the popular Mids Reborn character build planner, designed to provide the same powerful build planning capabilities in a modern web environment. The application allows players to:

- Select archetypes, powersets, and individual powers
- Plan enhancement slotting with accurate set bonuses
- Calculate build statistics and totals
- Export and import character builds
- Access up-to-date game data from City of Heroes servers

## Tech Stack

### Frontend

- **React 19** with TypeScript for the user interface
- **Material-UI** (planned) for component library
- Component structure with services layer for API integration
- Modern development tooling (ESLint, Prettier)

### Backend

- **FastAPI** for high-performance REST API
- **SQLAlchemy** with **Alembic** for database ORM and migrations
- **PostgreSQL** for data storage
- **Uvicorn** ASGI server for production deployment
- **uv** for modern Python package management (faster than pip)

### DevOps & Deployment

- **Docker** with multi-stage builds
- **Docker Compose** for local development
- **Google Cloud Platform (GCP)** (planned) for production deployment
- **GitHub Actions** CI/CD with AI-powered workflows
- **AI-assisted development** with Claude integration

## Project Structure

```
mids-hero-web/
├── frontend/                 # React TypeScript application
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── services/        # API service layer
│   │   └── ...
├── backend/                 # FastAPI application
│   ├── app/
│   │   ├── models.py        # Database models
│   │   ├── schemas.py       # Pydantic schemas
│   │   ├── crud.py          # Database operations
│   │   └── database.py      # Database configuration
│   ├── main.py              # FastAPI entry point
│   └── pyproject.toml       # Python dependencies & project config
├── alembic/                 # Database migration files
├── scripts/                 # Development helper scripts
│   └── dev.py              # uv development commands
├── docker-compose.yml       # Local development environment
├── Dockerfile              # Multi-stage container build
└── README.md               # This file
```

## Quick Start 

> **Note**: This project requires Node.js 18+ and Python 3.11+


### Prerequisites

- **Docker** and **Docker Compose** installed
- **Git** for version control
- **just** command runner - [Install just](https://github.com/casey/just)
- **uv** (modern Python package manager) - [Install uv](https://docs.astral.sh/uv/getting-started/installation/)

### Clone and Run

1. **Clone the repository:**

   ```bash
   git clone https://github.com/woodrowpearson/mids-hero-web.git
   cd mids-hero-web
   ```

2. **Quick start:**

   ```bash
   just quickstart  # Sets up everything
   just dev         # Start development environment
   ```

3. **Access the application:**
   - Frontend: <http://localhost:3000>
   - Backend API: <http://localhost:8000>
   - API Documentation: <http://localhost:8000/docs>

### Development Setup

All development operations use the `just` command runner for consistency:

#### Essential Commands

```bash
just quickstart      # Initial setup
just dev            # Start all services
just health         # Run health checks
just test           # Run all tests
just quality        # Code quality checks
just lint-fix       # Auto-fix linting issues
```

#### Database Operations

```bash
just db-setup                      # Complete database setup (recommended)
just db-migrate                    # Run pending migrations
just db-migration-create "description"  # Create new migration
just db-reset                      # Reset database
just db-status                     # Check migration status
just db-connect                    # Connect to database
just db-seed                       # Load sample data
```

> **Database Setup**: The project uses PostgreSQL in Docker for consistency. Run `just db-setup` for automated setup including Docker container management and migration application.

#### Individual Service Development

```bash
# Backend only
just backend-dev

# Frontend only  
just frontend-dev

# API documentation
just api-docs
```

#### Legacy Commands (if needed)

```bash
# Backend development (direct)
cd backend && uv run uvicorn main:app --reload

# Frontend development (direct)
cd frontend && npm start
```

## Features

### Current Status

**✅ Epic 1: Project Setup** - Complete
- Git repository and project structure
- React frontend scaffold with TypeScript
- FastAPI backend with proper Python structure  
- Docker environment configuration
- GitHub Actions CI/CD pipeline
- AI-powered workflows

**🚧 Epic 2: Data Import** - In Progress (BLOCKED)
- Need City of Heroes game data files (.mhd)
- Database migrations pending
- Import scripts to be created

**📋 Epics 3-6**: Backend API, Frontend, Deployment, Optimization - Planned

### AI-Powered Development

This project features AI-assisted development workflows:

- **@claude mentions** in PRs and issues for AI assistance
- **Automated PR reviews** with City of Heroes domain knowledge
- **Context health monitoring** to prevent token limit issues
- **Command compliance checks** (uv over pip, fd over find, etc.)
- **Epic progress tracking** and documentation synthesis

### Planned Features

- [ ] User accounts and cloud build saving
- [ ] Real-time build sharing
- [ ] Advanced build validation
- [ ] Multi-server database support (Homecoming, Rebirth)
- [ ] Mobile-responsive design
- [ ] Community build sharing

## Database Setup and Troubleshooting

### Recommended Setup (Docker)

The project uses PostgreSQL in Docker for consistency across development environments:

```bash
just db-setup  # Automated setup with Docker
```

This script:
1. Checks for conflicts with local PostgreSQL
2. Starts Docker PostgreSQL container
3. Runs database migrations
4. Verifies setup

### Database Connection Information

```bash
# Database URL
postgresql://postgres:postgres@localhost:5432/mids_web

# Container name
mids-hero-web-db-1

# Admin interface (when running)
http://localhost:8080  # Adminer
```

### Common Issues and Solutions

**Issue**: `FATAL: role "postgres" does not exist`

**Solution**: Local PostgreSQL is conflicting with Docker
```bash
# Stop local PostgreSQL
brew services stop postgresql@14

# Or use the automated setup
just db-setup
```

**Issue**: Docker build fails with `uv: not found`

**Solution**: Docker image build issue (fixed in latest version)
```bash
# Use database-only setup
docker-compose up -d db
just db-migrate
```

**Issue**: Migration fails or tables don't exist

**Solution**: Reset and recreate database
```bash
just db-reset  # Complete reset
```

### Alternative: Local PostgreSQL

If you prefer local PostgreSQL:

```bash
# Install PostgreSQL
brew install postgresql@15
brew services start postgresql@15

# Create database
createdb mids_web

# Set environment variable
export DATABASE_URL=postgresql://postgres@localhost:5432/mids_web

# Run migrations
just db-migrate
```

## Data Sources

The application uses game data from:

- **Homecoming** (primary): Latest game data from the Homecoming CoH server
- **Rebirth** (planned): Community-maintained server data
- **Generic**: Fallback database for basic functionality

Data is automatically updated through the server's update mechanism, eliminating the need for individual client updates.

## Modern Python Development

This project uses **uv**, a modern Python package manager that provides:

- **Faster dependency resolution** - Up to 10x faster than pip
- **Better dependency management** - Reliable lockfile and conflict resolution
- **Improved developer experience** - Single command for project setup
- **Built-in virtual environment management** - No need to manually create/activate venvs
- **Modern pyproject.toml support** - Standard Python project configuration

Benefits over traditional package managers:

- Faster installs and updates
- Better reproducibility across environments
- Simplified dependency management
- Integrated tooling (linting, formatting, testing)

## Contributing

We welcome contributions! Please see our [development roadmap](ROADMAP.md) for current priorities and planned features.

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Use `just` commands for development (`just health`, `just test`, etc.)
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request (AI workflows will assist with review)

### AI Assistance

- Use **@claude** in PR comments for AI assistance
- AI workflows automatically review code for City of Heroes domain compliance
- Context health is monitored to prevent token limit issues

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **Mids Reborn** team for the original desktop application
- **City of Heroes** community for continued support
- **Homecoming** and **Rebirth** server teams for maintaining the game data

## Support

For support, please:

- Check the [documentation](docs/)
- Open an issue on GitHub
- Join our Discord server (link coming soon)

---

_Mids-Web is not affiliated with or endorsed by NCSoft or the original City of Heroes development team._
