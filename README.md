# Mids-Web: Modern Web Rewrite of Mids Reborn

A modern web-based rewrite of the Mids Reborn character planner for _City of Heroes_. This project transforms the existing Windows Forms desktop application into a responsive web application with a React frontend and FastAPI backend.

## Overview

Mids-Web is a complete rewrite of the popular Mids Reborn character build planner, designed to provide the same powerful build planning capabilities in a modern web environment. The application allows players to:

- Select archetypes, powersets, and individual powers
- Plan enhancement slotting with accurate set bonuses
- Calculate build statistics and totals
- Export and import character builds
- Access up-to-date game data from City of Heroes servers

## Tech Stack

### Frontend

- **React** with TypeScript for the user interface
- **Material-UI** or **Ant Design** for component library
- **React Router** for navigation
- **Redux Toolkit** for state management

### Backend

- **FastAPI** for high-performance REST API
- **SQLAlchemy** with **Alembic** for database ORM and migrations
- **PostgreSQL** for data storage
- **Uvicorn** ASGI server for production deployment
- **uv** for modern Python package management (faster than pip)

### DevOps & Deployment

- **Docker** with multi-stage builds
- **Docker Compose** for local development
- **Google Cloud Platform (GCP)** for production deployment
- **GitHub Actions** for CI/CD pipeline

## Project Structure

```
mids-web/
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

### Prerequisites

- **Docker** and **Docker Compose** installed
- **Git** for version control
- **uv** (modern Python package manager) - [Install uv](https://docs.astral.sh/uv/getting-started/installation/)

### Clone and Run

1. **Clone the repository:**

   ```bash
   git clone https://github.com/your-org/mids-web.git
   cd mids-web
   ```

2. **Start the development environment:**

   ```bash
   docker-compose up --build
   ```

3. **Access the application:**
   - Frontend: <http://localhost:3000>
   - Backend API: <http://localhost:8000>
   - API Documentation: <http://localhost:8000/docs>

### Development Setup

#### Backend Development

```bash
cd backend
uv sync  # Install dependencies and create virtual environment
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Or activate the virtual environment and run directly
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Development Helper Script

We provide a convenient development script that wraps common uv commands:

```bash
# Set up development environment (installs uv if needed)
python scripts/dev.py setup

# Install dependencies
python scripts/dev.py install

# Run the backend server
python scripts/dev.py run

# Run tests
python scripts/dev.py test

# Run linting
python scripts/dev.py lint

# Format code
python scripts/dev.py format

# Run database migrations
python scripts/dev.py migrate

# Clean up build artifacts
python scripts/dev.py clean
```

#### Frontend Development

```bash
cd frontend
npm install
npm start
```

#### Database Setup

```bash
# Run database migrations
cd backend
uv run alembic upgrade head

# Create a new migration (when needed)
uv run alembic revision --autogenerate -m "Description of changes"
```

## Features

### Current Features (MVP)

- [ ] Archetype selection and powerset browsing
- [ ] Power selection with prerequisite validation
- [ ] Enhancement slotting interface
- [ ] Basic build statistics calculation
- [ ] Build export/import functionality

### Planned Features

- [ ] User accounts and cloud build saving
- [ ] Real-time build sharing
- [ ] Advanced build validation
- [ ] Multi-server database support (Homecoming, Rebirth)
- [ ] Mobile-responsive design
- [ ] Community build sharing

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
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

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
