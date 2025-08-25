#!/bin/bash

# Script to create all GitHub issues for Mids Hero Web project
# Run this after setting up your GitHub repository

set -e  # Exit on error

# Ensure we're in a git repository with a remote
if ! git remote get-url origin > /dev/null 2>&1; then
    echo "Error: No git remote found. Please add a GitHub remote first."
    echo "Example: git remote add origin https://github.com/yourusername/mids-hero-web.git"
    exit 1
fi

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "Error: GitHub CLI (gh) is not installed."
    echo "Please install it from: https://cli.github.com/"
    exit 1
fi

# Check if authenticated
if ! gh auth status > /dev/null 2>&1; then
    echo "Error: Not authenticated with GitHub CLI."
    echo "Please run: gh auth login"
    exit 1
fi

echo "Creating milestones..."
gh api repos/:owner/:repo/milestones -f title="MVP" -f description="Minimum Viable Product (Epics 1-5)"
gh api repos/:owner/:repo/milestones -f title="Post-MVP" -f description="Optimization and Enhancements (Epic 6)"

echo "Creating labels..."
gh label create epic --description "Major development milestone" --color 7057ff || true
gh label create task --description "Feature or requirement" --color 0075ca || true
gh label create subtask --description "Implementation detail" --color d73a4a || true
gh label create frontend --description "Frontend development" --color ffd700 || true
gh label create backend --description "Backend development" --color 2ea44f || true
gh label create database --description "Database related" --color b08800 || true
gh label create devops --description "DevOps and deployment" --color 5319e7 || true

echo "Creating Epic 1..."
EPIC1_ID=$(gh issue create --title "Epic 1: Project Setup and Planning" --body "Establish the project structure, repositories, and development environment for the frontend and backend.\n\n## Tasks\n- [ ] #1.1: Set Up Repositories and Codebase Structure\n- [ ] #1.2: Frontend Scaffold (React)\n- [ ] #1.3: Backend Scaffold (FastAPI + ORM)\n- [ ] #1.4: Docker Environment\n" --label "epic,devops" --milestone "MVP" | grep -o "[0-9]*$")

echo "  Creating Task 1.1..."
TASK1_1_ID=$(gh issue create --title "Task 1.1: Set Up Repositories and Codebase Structure" --body "Part of #{1} Epic 1: Project Setup and Planning\n\n## Subtasks\n- [ ] 1.1.1: Initialize a new Git repository (or mono-repo) for the project. Create folders for frontend/ and backend/ components.\n- [ ] 1.1.2: Choose a naming convention and baseline license/readme. Document the project goal and stack in the README.\n- [ ] 1.1.3: Configure version control and CI pipeline (set up GitHub Actions or similar to lint/test/build on pushes).\n" --label "task,devops" --milestone "MVP" | grep -o "[0-9]*$")
echo "    Creating Subtask 1.1.1..."
gh issue create --title "Subtask 1.1.1: Initialize a new Git repository (or mono-repo) for the proje..." --body "Part of Task #{1_1} Set Up Repositories and Codebase Structure\nPart of #{1} Epic 1: Project Setup and Planning\n\n## Description\nInitialize a new Git repository (or mono-repo) for the project. Create folders for frontend/ and backend/ components." --label "subtask,devops" --milestone "MVP"
echo "    Creating Subtask 1.1.2..."
gh issue create --title "Subtask 1.1.2: Choose a naming convention and baseline license/readme. Docu..." --body "Part of Task #{1_1} Set Up Repositories and Codebase Structure\nPart of #{1} Epic 1: Project Setup and Planning\n\n## Description\nChoose a naming convention and baseline license/readme. Document the project goal and stack in the README." --label "subtask,devops" --milestone "MVP"
echo "    Creating Subtask 1.1.3..."
gh issue create --title "Subtask 1.1.3: Configure version control and CI pipeline (set up GitHub Act..." --body "Part of Task #{1_1} Set Up Repositories and Codebase Structure\nPart of #{1} Epic 1: Project Setup and Planning\n\n## Description\nConfigure version control and CI pipeline (set up GitHub Actions or similar to lint/test/build on pushes)." --label "subtask,devops" --milestone "MVP"

echo "  Creating Task 1.2..."
TASK1_2_ID=$(gh issue create --title "Task 1.2: Frontend Scaffold (React)" --body "Part of #{1} Epic 1: Project Setup and Planning\n\n## Subtasks\n- [ ] 1.2.1: Bootstrap a React app (using Create React App or Vite). Set the project to use TypeScript.\n- [ ] 1.2.2: Install base dependencies (React Router, UI component library, state management).\n- [ ] 1.2.3: Set up a basic file structure for React (components, services, styles). Verify dev server runs.\n" --label "task,devops" --milestone "MVP" | grep -o "[0-9]*$")
echo "    Creating Subtask 1.2.1..."
gh issue create --title "Subtask 1.2.1: Bootstrap a React app (using Create React App or Vite). Set ..." --body "Part of Task #{1_2} Frontend Scaffold (React)\nPart of #{1} Epic 1: Project Setup and Planning\n\n## Description\nBootstrap a React app (using Create React App or Vite). Set the project to use TypeScript." --label "subtask,devops" --milestone "MVP"
echo "    Creating Subtask 1.2.2..."
gh issue create --title "Subtask 1.2.2: Install base dependencies (React Router, UI component librar..." --body "Part of Task #{1_2} Frontend Scaffold (React)\nPart of #{1} Epic 1: Project Setup and Planning\n\n## Description\nInstall base dependencies (React Router, UI component library, state management)." --label "subtask,devops" --milestone "MVP"
echo "    Creating Subtask 1.2.3..."
gh issue create --title "Subtask 1.2.3: Set up a basic file structure for React (components, service..." --body "Part of Task #{1_2} Frontend Scaffold (React)\nPart of #{1} Epic 1: Project Setup and Planning\n\n## Description\nSet up a basic file structure for React (components, services, styles). Verify dev server runs." --label "subtask,devops" --milestone "MVP"

echo "  Creating Task 1.3..."
TASK1_3_ID=$(gh issue create --title "Task 1.3: Backend Scaffold (FastAPI + ORM)" --body "Part of #{1} Epic 1: Project Setup and Planning\n\n## Subtasks\n- [ ] 1.3.1: Create Python virtual environment and initiate FastAPI project. Install FastAPI, Uvicorn, and ORM.\n- [ ] 1.3.2: Set up basic FastAPI application with health-check endpoint (GET /ping).\n- [ ] 1.3.3: Configure CORS in FastAPI to allow React dev server to call APIs.\n- [ ] 1.3.4: Decide on ORM vs Django and configure accordingly.\n- [ ] 1.3.5: Set up database connection config and verify backend can connect to DB.\n" --label "task,devops" --milestone "MVP" | grep -o "[0-9]*$")
echo "    Creating Subtask 1.3.1..."
gh issue create --title "Subtask 1.3.1: Create Python virtual environment and initiate FastAPI proje..." --body "Part of Task #{1_3} Backend Scaffold (FastAPI + ORM)\nPart of #{1} Epic 1: Project Setup and Planning\n\n## Description\nCreate Python virtual environment and initiate FastAPI project. Install FastAPI, Uvicorn, and ORM." --label "subtask,devops" --milestone "MVP"
echo "    Creating Subtask 1.3.2..."
gh issue create --title "Subtask 1.3.2: Set up basic FastAPI application with health-check endpoint ..." --body "Part of Task #{1_3} Backend Scaffold (FastAPI + ORM)\nPart of #{1} Epic 1: Project Setup and Planning\n\n## Description\nSet up basic FastAPI application with health-check endpoint (GET /ping)." --label "subtask,devops" --milestone "MVP"
echo "    Creating Subtask 1.3.3..."
gh issue create --title "Subtask 1.3.3: Configure CORS in FastAPI to allow React dev server to call ..." --body "Part of Task #{1_3} Backend Scaffold (FastAPI + ORM)\nPart of #{1} Epic 1: Project Setup and Planning\n\n## Description\nConfigure CORS in FastAPI to allow React dev server to call APIs." --label "subtask,devops" --milestone "MVP"
echo "    Creating Subtask 1.3.4..."
gh issue create --title "Subtask 1.3.4: Decide on ORM vs Django and configure accordingly...." --body "Part of Task #{1_3} Backend Scaffold (FastAPI + ORM)\nPart of #{1} Epic 1: Project Setup and Planning\n\n## Description\nDecide on ORM vs Django and configure accordingly." --label "subtask,devops" --milestone "MVP"
echo "    Creating Subtask 1.3.5..."
gh issue create --title "Subtask 1.3.5: Set up database connection config and verify backend can con..." --body "Part of Task #{1_3} Backend Scaffold (FastAPI + ORM)\nPart of #{1} Epic 1: Project Setup and Planning\n\n## Description\nSet up database connection config and verify backend can connect to DB." --label "subtask,devops" --milestone "MVP"

echo "  Creating Task 1.4..."
TASK1_4_ID=$(gh issue create --title "Task 1.4: Docker Environment" --body "Part of #{1} Epic 1: Project Setup and Planning\n\n## Subtasks\n- [ ] 1.4.1: Write Dockerfile for backend service (python:3.11-slim base).\n- [ ] 1.4.2: Write Dockerfile for frontend (node alpine base or serve via backend).\n- [ ] 1.4.3: Create docker-compose.yml for local development (Postgres, backend, frontend).\n- [ ] 1.4.4: Test Docker setup: verify containers can communicate properly.\n" --label "task,devops" --milestone "MVP" | grep -o "[0-9]*$")
echo "    Creating Subtask 1.4.1..."
gh issue create --title "Subtask 1.4.1: Write Dockerfile for backend service (python:3.11-slim base)..." --body "Part of Task #{1_4} Docker Environment\nPart of #{1} Epic 1: Project Setup and Planning\n\n## Description\nWrite Dockerfile for backend service (python:3.11-slim base)." --label "subtask,devops" --milestone "MVP"
echo "    Creating Subtask 1.4.2..."
gh issue create --title "Subtask 1.4.2: Write Dockerfile for frontend (node alpine base or serve via..." --body "Part of Task #{1_4} Docker Environment\nPart of #{1} Epic 1: Project Setup and Planning\n\n## Description\nWrite Dockerfile for frontend (node alpine base or serve via backend)." --label "subtask,devops" --milestone "MVP"
echo "    Creating Subtask 1.4.3..."
gh issue create --title "Subtask 1.4.3: Create docker-compose.yml for local development (Postgres, b..." --body "Part of Task #{1_4} Docker Environment\nPart of #{1} Epic 1: Project Setup and Planning\n\n## Description\nCreate docker-compose.yml for local development (Postgres, backend, frontend)." --label "subtask,devops" --milestone "MVP"
echo "    Creating Subtask 1.4.4..."
gh issue create --title "Subtask 1.4.4: Test Docker setup: verify containers can communicate properl..." --body "Part of Task #{1_4} Docker Environment\nPart of #{1} Epic 1: Project Setup and Planning\n\n## Description\nTest Docker setup: verify containers can communicate properly." --label "subtask,devops" --milestone "MVP"

echo "Creating Epic 2..."
EPIC2_ID=$(gh issue create --title "Epic 2: Data Model & Database Integration" --body "Define the database schema and import the City of Heroes data (Homecoming 2025.7.1111) into the new system.\n\n## Tasks\n- [ ] #2.1: Design Database Schema\n- [ ] #2.2: Data Import Utilities\n- [ ] #2.3: Validation against Original\n- [ ] #2.4: Automating Future Imports\n" --label "epic,database,backend" --milestone "MVP" | grep -o "[0-9]*$")

echo "  Creating Task 2.1..."
TASK2_1_ID=$(gh issue create --title "Task 2.1: Design Database Schema" --body "Part of #{2} Epic 2: Data Model & Database Integration\n\n## Subtasks\n- [ ] 2.1.1: Identify all data entities: Archetype, Powerset, Power, Enhancement, SetBonus, etc. Design ER diagram.\n- [ ] 2.1.2: Translate design into SQLAlchemy/Django models with appropriate types and relationships.\n- [ ] 2.1.3: Run migrations to apply schema to Postgres database.\n" --label "task,database,backend" --milestone "MVP" | grep -o "[0-9]*$")
echo "    Creating Subtask 2.1.1..."
gh issue create --title "Subtask 2.1.1: Identify all data entities: Archetype, Powerset, Power, Enha..." --body "Part of Task #{2_1} Design Database Schema\nPart of #{2} Epic 2: Data Model & Database Integration\n\n## Description\nIdentify all data entities: Archetype, Powerset, Power, Enhancement, SetBonus, etc. Design ER diagram." --label "subtask,database,backend" --milestone "MVP"
echo "    Creating Subtask 2.1.2..."
gh issue create --title "Subtask 2.1.2: Translate design into SQLAlchemy/Django models with appropri..." --body "Part of Task #{2_1} Design Database Schema\nPart of #{2} Epic 2: Data Model & Database Integration\n\n## Description\nTranslate design into SQLAlchemy/Django models with appropriate types and relationships." --label "subtask,database,backend" --milestone "MVP"
echo "    Creating Subtask 2.1.3..."
gh issue create --title "Subtask 2.1.3: Run migrations to apply schema to Postgres database...." --body "Part of Task #{2_1} Design Database Schema\nPart of #{2} Epic 2: Data Model & Database Integration\n\n## Description\nRun migrations to apply schema to Postgres database." --label "subtask,database,backend" --milestone "MVP"

echo "  Creating Task 2.2..."
TASK2_2_ID=$(gh issue create --title "Task 2.2: Data Import Utilities" --body "Part of #{2} Epic 2: Data Model & Database Integration\n\n## Subtasks\n- [ ] 2.2.1: Write scripts to convert existing data into new database. Investigate data sources.\n- [ ] 2.2.2: Implement parser for binary .mhd files or create C# export tool.\n- [ ] 2.2.3: Write Python script to insert data into Postgres via ORM.\n- [ ] 2.2.4: Verify imported data: cross-check against known values.\n" --label "task,database,backend" --milestone "MVP" | grep -o "[0-9]*$")
echo "    Creating Subtask 2.2.1..."
gh issue create --title "Subtask 2.2.1: Write scripts to convert existing data into new database. In..." --body "Part of Task #{2_2} Data Import Utilities\nPart of #{2} Epic 2: Data Model & Database Integration\n\n## Description\nWrite scripts to convert existing data into new database. Investigate data sources." --label "subtask,database,backend" --milestone "MVP"
echo "    Creating Subtask 2.2.2..."
gh issue create --title "Subtask 2.2.2: Implement parser for binary .mhd files or create C# export t..." --body "Part of Task #{2_2} Data Import Utilities\nPart of #{2} Epic 2: Data Model & Database Integration\n\n## Description\nImplement parser for binary .mhd files or create C# export tool." --label "subtask,database,backend" --milestone "MVP"
echo "    Creating Subtask 2.2.3..."
gh issue create --title "Subtask 2.2.3: Write Python script to insert data into Postgres via ORM...." --body "Part of Task #{2_2} Data Import Utilities\nPart of #{2} Epic 2: Data Model & Database Integration\n\n## Description\nWrite Python script to insert data into Postgres via ORM." --label "subtask,database,backend" --milestone "MVP"
echo "    Creating Subtask 2.2.4..."
gh issue create --title "Subtask 2.2.4: Verify imported data: cross-check against known values...." --body "Part of Task #{2_2} Data Import Utilities\nPart of #{2} Epic 2: Data Model & Database Integration\n\n## Description\nVerify imported data: cross-check against known values." --label "subtask,database,backend" --milestone "MVP"

echo "  Creating Task 2.3..."
TASK2_3_ID=$(gh issue create --title "Task 2.3: Validation against Original" --body "Part of #{2} Epic 2: Data Model & Database Integration\n\n## Subtasks\n- [ ] 2.3.1: Cross-check counts: archetypes, powers, enhancements match original.\n- [ ] 2.3.2: Run scenario: verify specific known build elements exist in new DB.\n" --label "task,database,backend" --milestone "MVP" | grep -o "[0-9]*$")
echo "    Creating Subtask 2.3.1..."
gh issue create --title "Subtask 2.3.1: Cross-check counts: archetypes, powers, enhancements match o..." --body "Part of Task #{2_3} Validation against Original\nPart of #{2} Epic 2: Data Model & Database Integration\n\n## Description\nCross-check counts: archetypes, powers, enhancements match original." --label "subtask,database,backend" --milestone "MVP"
echo "    Creating Subtask 2.3.2..."
gh issue create --title "Subtask 2.3.2: Run scenario: verify specific known build elements exist in ..." --body "Part of Task #{2_3} Validation against Original\nPart of #{2} Epic 2: Data Model & Database Integration\n\n## Description\nRun scenario: verify specific known build elements exist in new DB." --label "subtask,database,backend" --milestone "MVP"

echo "  Creating Task 2.4..."
TASK2_4_ID=$(gh issue create --title "Task 2.4: Automating Future Imports" --body "Part of #{2} Epic 2: Data Model & Database Integration\n\n## Subtasks\n- [ ] 2.4.1: Write general script for updating database with new game versions. Document import process.\n" --label "task,database,backend" --milestone "MVP" | grep -o "[0-9]*$")
echo "    Creating Subtask 2.4.1..."
gh issue create --title "Subtask 2.4.1: Write general script for updating database with new game ver..." --body "Part of Task #{2_4} Automating Future Imports\nPart of #{2} Epic 2: Data Model & Database Integration\n\n## Description\nWrite general script for updating database with new game versions. Document import process." --label "subtask,database,backend" --milestone "MVP"

echo "Creating Epic 3..."
EPIC3_ID=$(gh issue create --title "Epic 3: Backend API Development" --body "Implement the backend functionality to serve data and perform calculations.\n\n## Tasks\n- [ ] #3.1: Core Data Endpoints (Read Operations)\n- [ ] #3.2: Build Simulation & Calculation Endpoints\n- [ ] #3.3: Write/Modify Operations\n- [ ] #3.4: Testing the API\n" --label "epic,backend" --milestone "MVP" | grep -o "[0-9]*$")

echo "  Creating Task 3.1..."
TASK3_1_ID=$(gh issue create --title "Task 3.1: Core Data Endpoints (Read Operations)" --body "Part of #{3} Epic 3: Backend API Development\n\n## Subtasks\n- [ ] 3.1.1: Implement GET /api/archetypes: list all archetypes with key details.\n- [ ] 3.1.2: Implement GET /api/archetypes/{id}: detailed info for specific archetype.\n- [ ] 3.1.3: Implement GET /api/powersets/{id}: powerset details with power list.\n- [ ] 3.1.4: Implement GET /api/powers/{id}: detailed power info.\n- [ ] 3.1.5: Implement GET /api/enhancements and related endpoints.\n- [ ] 3.1.6: Implement miscellaneous data endpoints for incarnates, salvage, recipes.\n" --label "task,backend" --milestone "MVP" | grep -o "[0-9]*$")
echo "    Creating Subtask 3.1.1..."
gh issue create --title "Subtask 3.1.1: Implement GET /api/archetypes: list all archetypes with key ..." --body "Part of Task #{3_1} Core Data Endpoints (Read Operations)\nPart of #{3} Epic 3: Backend API Development\n\n## Description\nImplement GET /api/archetypes: list all archetypes with key details." --label "subtask,backend" --milestone "MVP"
echo "    Creating Subtask 3.1.2..."
gh issue create --title "Subtask 3.1.2: Implement GET /api/archetypes/{id}: detailed info for specif..." --body "Part of Task #{3_1} Core Data Endpoints (Read Operations)\nPart of #{3} Epic 3: Backend API Development\n\n## Description\nImplement GET /api/archetypes/{id}: detailed info for specific archetype." --label "subtask,backend" --milestone "MVP"
echo "    Creating Subtask 3.1.3..."
gh issue create --title "Subtask 3.1.3: Implement GET /api/powersets/{id}: powerset details with pow..." --body "Part of Task #{3_1} Core Data Endpoints (Read Operations)\nPart of #{3} Epic 3: Backend API Development\n\n## Description\nImplement GET /api/powersets/{id}: powerset details with power list." --label "subtask,backend" --milestone "MVP"
echo "    Creating Subtask 3.1.4..."
gh issue create --title "Subtask 3.1.4: Implement GET /api/powers/{id}: detailed power info...." --body "Part of Task #{3_1} Core Data Endpoints (Read Operations)\nPart of #{3} Epic 3: Backend API Development\n\n## Description\nImplement GET /api/powers/{id}: detailed power info." --label "subtask,backend" --milestone "MVP"
echo "    Creating Subtask 3.1.5..."
gh issue create --title "Subtask 3.1.5: Implement GET /api/enhancements and related endpoints...." --body "Part of Task #{3_1} Core Data Endpoints (Read Operations)\nPart of #{3} Epic 3: Backend API Development\n\n## Description\nImplement GET /api/enhancements and related endpoints." --label "subtask,backend" --milestone "MVP"
echo "    Creating Subtask 3.1.6..."
gh issue create --title "Subtask 3.1.6: Implement miscellaneous data endpoints for incarnates, salva..." --body "Part of Task #{3_1} Core Data Endpoints (Read Operations)\nPart of #{3} Epic 3: Backend API Development\n\n## Description\nImplement miscellaneous data endpoints for incarnates, salvage, recipes." --label "subtask,backend" --milestone "MVP"

echo "  Creating Task 3.2..."
TASK3_2_ID=$(gh issue create --title "Task 3.2: Build Simulation & Calculation Endpoints" --body "Part of #{3} Epic 3: Backend API Development\n\n## Subtasks\n- [ ] 3.2.1: Identify key calculations: defense/resist totals, damage, endurance, validation.\n- [ ] 3.2.2: Implement POST /api/calculate: compute aggregate stats including set bonuses.\n- [ ] 3.2.3: Write unit tests for calculation logic with known scenarios.\n- [ ] 3.2.4: Port complex calculation logic from C# to Python.\n" --label "task,backend" --milestone "MVP" | grep -o "[0-9]*$")
echo "    Creating Subtask 3.2.1..."
gh issue create --title "Subtask 3.2.1: Identify key calculations: defense/resist totals, damage, en..." --body "Part of Task #{3_2} Build Simulation & Calculation Endpoints\nPart of #{3} Epic 3: Backend API Development\n\n## Description\nIdentify key calculations: defense/resist totals, damage, endurance, validation." --label "subtask,backend" --milestone "MVP"
echo "    Creating Subtask 3.2.2..."
gh issue create --title "Subtask 3.2.2: Implement POST /api/calculate: compute aggregate stats inclu..." --body "Part of Task #{3_2} Build Simulation & Calculation Endpoints\nPart of #{3} Epic 3: Backend API Development\n\n## Description\nImplement POST /api/calculate: compute aggregate stats including set bonuses." --label "subtask,backend" --milestone "MVP"
echo "    Creating Subtask 3.2.3..."
gh issue create --title "Subtask 3.2.3: Write unit tests for calculation logic with known scenarios...." --body "Part of Task #{3_2} Build Simulation & Calculation Endpoints\nPart of #{3} Epic 3: Backend API Development\n\n## Description\nWrite unit tests for calculation logic with known scenarios." --label "subtask,backend" --milestone "MVP"
echo "    Creating Subtask 3.2.4..."
gh issue create --title "Subtask 3.2.4: Port complex calculation logic from C# to Python...." --body "Part of Task #{3_2} Build Simulation & Calculation Endpoints\nPart of #{3} Epic 3: Backend API Development\n\n## Description\nPort complex calculation logic from C# to Python." --label "subtask,backend" --milestone "MVP"

echo "  Creating Task 3.3..."
TASK3_3_ID=$(gh issue create --title "Task 3.3: Write/Modify Operations" --body "Part of #{3} Epic 3: Backend API Development\n\n## Subtasks\n- [ ] 3.3.1: Define JSON schema for build (powers and enhancements).\n- [ ] 3.3.2: Implement POST /api/build/encode and /api/build/decode.\n- [ ] 3.3.3: (Future) Implement authentication and user build storage.\n" --label "task,backend" --milestone "MVP" | grep -o "[0-9]*$")
echo "    Creating Subtask 3.3.1..."
gh issue create --title "Subtask 3.3.1: Define JSON schema for build (powers and enhancements)...." --body "Part of Task #{3_3} Write/Modify Operations\nPart of #{3} Epic 3: Backend API Development\n\n## Description\nDefine JSON schema for build (powers and enhancements)." --label "subtask,backend" --milestone "MVP"
echo "    Creating Subtask 3.3.2..."
gh issue create --title "Subtask 3.3.2: Implement POST /api/build/encode and /api/build/decode...." --body "Part of Task #{3_3} Write/Modify Operations\nPart of #{3} Epic 3: Backend API Development\n\n## Description\nImplement POST /api/build/encode and /api/build/decode." --label "subtask,backend" --milestone "MVP"
echo "    Creating Subtask 3.3.3..."
gh issue create --title "Subtask 3.3.3: (Future) Implement authentication and user build storage...." --body "Part of Task #{3_3} Write/Modify Operations\nPart of #{3} Epic 3: Backend API Development\n\n## Description\n(Future) Implement authentication and user build storage." --label "subtask,backend" --milestone "MVP"

echo "  Creating Task 3.4..."
TASK3_4_ID=$(gh issue create --title "Task 3.4: Testing the API" --body "Part of #{3} Epic 3: Backend API Development\n\n## Subtasks\n- [ ] 3.4.1: Create automated tests for each endpoint using PyTest.\n- [ ] 3.4.2: Test edge cases: invalid IDs, empty inputs, error handling.\n- [ ] 3.4.3: Test calculation endpoints with known builds.\n- [ ] 3.4.4: Set up continuous integration to run tests.\n" --label "task,backend" --milestone "MVP" | grep -o "[0-9]*$")
echo "    Creating Subtask 3.4.1..."
gh issue create --title "Subtask 3.4.1: Create automated tests for each endpoint using PyTest...." --body "Part of Task #{3_4} Testing the API\nPart of #{3} Epic 3: Backend API Development\n\n## Description\nCreate automated tests for each endpoint using PyTest." --label "subtask,backend" --milestone "MVP"
echo "    Creating Subtask 3.4.2..."
gh issue create --title "Subtask 3.4.2: Test edge cases: invalid IDs, empty inputs, error handling...." --body "Part of Task #{3_4} Testing the API\nPart of #{3} Epic 3: Backend API Development\n\n## Description\nTest edge cases: invalid IDs, empty inputs, error handling." --label "subtask,backend" --milestone "MVP"
echo "    Creating Subtask 3.4.3..."
gh issue create --title "Subtask 3.4.3: Test calculation endpoints with known builds...." --body "Part of Task #{3_4} Testing the API\nPart of #{3} Epic 3: Backend API Development\n\n## Description\nTest calculation endpoints with known builds." --label "subtask,backend" --milestone "MVP"
echo "    Creating Subtask 3.4.4..."
gh issue create --title "Subtask 3.4.4: Set up continuous integration to run tests...." --body "Part of Task #{3_4} Testing the API\nPart of #{3} Epic 3: Backend API Development\n\n## Description\nSet up continuous integration to run tests." --label "subtask,backend" --milestone "MVP"

echo "Creating Epic 4..."
EPIC4_ID=$(gh issue create --title "Epic 4: Frontend Application Implementation" --body "Build the React UI for character planning: archetype selection, powers, enhancements, and stats.\n\n## Tasks\n- [ ] #4.1: UI Layout and Navigation\n- [ ] #4.2: Archetype and Powerset Selection\n- [ ] #4.3: Enhancement Slotting Interface\n- [ ] #4.4: Stats Summary and Feedback\n- [ ] #4.5: Polish UI & User Experience\n- [ ] #4.6: Frontend Testing\n" --label "epic,frontend" --milestone "MVP" | grep -o "[0-9]*$")

echo "  Creating Task 4.1..."
TASK4_1_ID=$(gh issue create --title "Task 4.1: UI Layout and Navigation" --body "Part of #{4} Epic 4: Frontend Application Implementation\n\n## Subtasks\n- [ ] 4.1.1: Design layout with sections for character info, powers, enhancements, stats.\n- [ ] 4.1.2: Implement basic layout with placeholder components using responsive design.\n- [ ] 4.1.3: Set up React Router if needed or keep as single-page app.\n- [ ] 4.1.4: Integrate UI theme with light/dark mode support.\n" --label "task,frontend" --milestone "MVP" | grep -o "[0-9]*$")
echo "    Creating Subtask 4.1.1..."
gh issue create --title "Subtask 4.1.1: Design layout with sections for character info, powers, enha..." --body "Part of Task #{4_1} UI Layout and Navigation\nPart of #{4} Epic 4: Frontend Application Implementation\n\n## Description\nDesign layout with sections for character info, powers, enhancements, stats." --label "subtask,frontend" --milestone "MVP"
echo "    Creating Subtask 4.1.2..."
gh issue create --title "Subtask 4.1.2: Implement basic layout with placeholder components using res..." --body "Part of Task #{4_1} UI Layout and Navigation\nPart of #{4} Epic 4: Frontend Application Implementation\n\n## Description\nImplement basic layout with placeholder components using responsive design." --label "subtask,frontend" --milestone "MVP"
echo "    Creating Subtask 4.1.3..."
gh issue create --title "Subtask 4.1.3: Set up React Router if needed or keep as single-page app...." --body "Part of Task #{4_1} UI Layout and Navigation\nPart of #{4} Epic 4: Frontend Application Implementation\n\n## Description\nSet up React Router if needed or keep as single-page app." --label "subtask,frontend" --milestone "MVP"
echo "    Creating Subtask 4.1.4..."
gh issue create --title "Subtask 4.1.4: Integrate UI theme with light/dark mode support...." --body "Part of Task #{4_1} UI Layout and Navigation\nPart of #{4} Epic 4: Frontend Application Implementation\n\n## Description\nIntegrate UI theme with light/dark mode support." --label "subtask,frontend" --milestone "MVP"

echo "  Creating Task 4.2..."
TASK4_2_ID=$(gh issue create --title "Task 4.2: Archetype and Powerset Selection" --body "Part of #{4} Epic 4: Frontend Application Implementation\n\n## Subtasks\n- [ ] 4.2.1: Create ArchetypeSelector component that fetches from API.\n- [ ] 4.2.2: Create PowersetSelection components for Primary/Secondary/Pool powers.\n- [ ] 4.2.3: Display Powers with level availability and prerequisites.\n- [ ] 4.2.4: Implement Incarnate powers selection if included.\n- [ ] 4.2.5: Update UI state with proper validation.\n" --label "task,frontend" --milestone "MVP" | grep -o "[0-9]*$")
echo "    Creating Subtask 4.2.1..."
gh issue create --title "Subtask 4.2.1: Create ArchetypeSelector component that fetches from API...." --body "Part of Task #{4_2} Archetype and Powerset Selection\nPart of #{4} Epic 4: Frontend Application Implementation\n\n## Description\nCreate ArchetypeSelector component that fetches from API." --label "subtask,frontend" --milestone "MVP"
echo "    Creating Subtask 4.2.2..."
gh issue create --title "Subtask 4.2.2: Create PowersetSelection components for Primary/Secondary/Po..." --body "Part of Task #{4_2} Archetype and Powerset Selection\nPart of #{4} Epic 4: Frontend Application Implementation\n\n## Description\nCreate PowersetSelection components for Primary/Secondary/Pool powers." --label "subtask,frontend" --milestone "MVP"
echo "    Creating Subtask 4.2.3..."
gh issue create --title "Subtask 4.2.3: Display Powers with level availability and prerequisites...." --body "Part of Task #{4_2} Archetype and Powerset Selection\nPart of #{4} Epic 4: Frontend Application Implementation\n\n## Description\nDisplay Powers with level availability and prerequisites." --label "subtask,frontend" --milestone "MVP"
echo "    Creating Subtask 4.2.4..."
gh issue create --title "Subtask 4.2.4: Implement Incarnate powers selection if included...." --body "Part of Task #{4_2} Archetype and Powerset Selection\nPart of #{4} Epic 4: Frontend Application Implementation\n\n## Description\nImplement Incarnate powers selection if included." --label "subtask,frontend" --milestone "MVP"
echo "    Creating Subtask 4.2.5..."
gh issue create --title "Subtask 4.2.5: Update UI state with proper validation...." --body "Part of Task #{4_2} Archetype and Powerset Selection\nPart of #{4} Epic 4: Frontend Application Implementation\n\n## Description\nUpdate UI state with proper validation." --label "subtask,frontend" --milestone "MVP"

echo "  Creating Task 4.3..."
TASK4_3_ID=$(gh issue create --title "Task 4.3: Enhancement Slotting Interface" --body "Part of #{4} Epic 4: Frontend Application Implementation\n\n## Subtasks\n- [ ] 4.3.1: Display enhancement slots with add/remove functionality per power.\n- [ ] 4.3.2: Create EnhancementPicker dialog showing valid enhancements.\n- [ ] 4.3.3: Implement Set Bonus Display for active bonuses.\n- [ ] 4.3.4: Show power enhancement effects on stats.\n" --label "task,frontend" --milestone "MVP" | grep -o "[0-9]*$")
echo "    Creating Subtask 4.3.1..."
gh issue create --title "Subtask 4.3.1: Display enhancement slots with add/remove functionality per ..." --body "Part of Task #{4_3} Enhancement Slotting Interface\nPart of #{4} Epic 4: Frontend Application Implementation\n\n## Description\nDisplay enhancement slots with add/remove functionality per power." --label "subtask,frontend" --milestone "MVP"
echo "    Creating Subtask 4.3.2..."
gh issue create --title "Subtask 4.3.2: Create EnhancementPicker dialog showing valid enhancements...." --body "Part of Task #{4_3} Enhancement Slotting Interface\nPart of #{4} Epic 4: Frontend Application Implementation\n\n## Description\nCreate EnhancementPicker dialog showing valid enhancements." --label "subtask,frontend" --milestone "MVP"
echo "    Creating Subtask 4.3.3..."
gh issue create --title "Subtask 4.3.3: Implement Set Bonus Display for active bonuses...." --body "Part of Task #{4_3} Enhancement Slotting Interface\nPart of #{4} Epic 4: Frontend Application Implementation\n\n## Description\nImplement Set Bonus Display for active bonuses." --label "subtask,frontend" --milestone "MVP"
echo "    Creating Subtask 4.3.4..."
gh issue create --title "Subtask 4.3.4: Show power enhancement effects on stats...." --body "Part of Task #{4_3} Enhancement Slotting Interface\nPart of #{4} Epic 4: Frontend Application Implementation\n\n## Description\nShow power enhancement effects on stats." --label "subtask,frontend" --milestone "MVP"

echo "  Creating Task 4.4..."
TASK4_4_ID=$(gh issue create --title "Task 4.4: Stats Summary and Feedback" --body "Part of #{4} Epic 4: Frontend Application Implementation\n\n## Subtasks\n- [ ] 4.4.1: Create SummaryPanel showing overall character stats.\n- [ ] 4.4.2: Update summary on build changes via backend or frontend calculations.\n- [ ] 4.4.3: Include validation warnings for invalid builds.\n" --label "task,frontend" --milestone "MVP" | grep -o "[0-9]*$")
echo "    Creating Subtask 4.4.1..."
gh issue create --title "Subtask 4.4.1: Create SummaryPanel showing overall character stats...." --body "Part of Task #{4_4} Stats Summary and Feedback\nPart of #{4} Epic 4: Frontend Application Implementation\n\n## Description\nCreate SummaryPanel showing overall character stats." --label "subtask,frontend" --milestone "MVP"
echo "    Creating Subtask 4.4.2..."
gh issue create --title "Subtask 4.4.2: Update summary on build changes via backend or frontend calc..." --body "Part of Task #{4_4} Stats Summary and Feedback\nPart of #{4} Epic 4: Frontend Application Implementation\n\n## Description\nUpdate summary on build changes via backend or frontend calculations." --label "subtask,frontend" --milestone "MVP"
echo "    Creating Subtask 4.4.3..."
gh issue create --title "Subtask 4.4.3: Include validation warnings for invalid builds...." --body "Part of Task #{4_4} Stats Summary and Feedback\nPart of #{4} Epic 4: Frontend Application Implementation\n\n## Description\nInclude validation warnings for invalid builds." --label "subtask,frontend" --milestone "MVP"

echo "  Creating Task 4.5..."
TASK4_5_ID=$(gh issue create --title "Task 4.5: Polish UI & User Experience" --body "Part of #{4} Epic 4: Frontend Application Implementation\n\n## Subtasks\n- [ ] 4.5.1: Add tooltips and info popups for powers and enhancements.\n- [ ] 4.5.2: Implement reset/clear functionality and New Build button.\n- [ ] 4.5.3: Implement import/export of builds via file or clipboard.\n- [ ] 4.5.4: Ensure mobile/responsive design for smaller screens.\n" --label "task,frontend" --milestone "MVP" | grep -o "[0-9]*$")
echo "    Creating Subtask 4.5.1..."
gh issue create --title "Subtask 4.5.1: Add tooltips and info popups for powers and enhancements...." --body "Part of Task #{4_5} Polish UI & User Experience\nPart of #{4} Epic 4: Frontend Application Implementation\n\n## Description\nAdd tooltips and info popups for powers and enhancements." --label "subtask,frontend" --milestone "MVP"
echo "    Creating Subtask 4.5.2..."
gh issue create --title "Subtask 4.5.2: Implement reset/clear functionality and New Build button...." --body "Part of Task #{4_5} Polish UI & User Experience\nPart of #{4} Epic 4: Frontend Application Implementation\n\n## Description\nImplement reset/clear functionality and New Build button." --label "subtask,frontend" --milestone "MVP"
echo "    Creating Subtask 4.5.3..."
gh issue create --title "Subtask 4.5.3: Implement import/export of builds via file or clipboard...." --body "Part of Task #{4_5} Polish UI & User Experience\nPart of #{4} Epic 4: Frontend Application Implementation\n\n## Description\nImplement import/export of builds via file or clipboard." --label "subtask,frontend" --milestone "MVP"
echo "    Creating Subtask 4.5.4..."
gh issue create --title "Subtask 4.5.4: Ensure mobile/responsive design for smaller screens...." --body "Part of Task #{4_5} Polish UI & User Experience\nPart of #{4} Epic 4: Frontend Application Implementation\n\n## Description\nEnsure mobile/responsive design for smaller screens." --label "subtask,frontend" --milestone "MVP"

echo "  Creating Task 4.6..."
TASK4_6_ID=$(gh issue create --title "Task 4.6: Frontend Testing" --body "Part of #{4} Epic 4: Frontend Application Implementation\n\n## Subtasks\n- [ ] 4.6.1: Write unit tests for React components using Jest/RTL.\n- [ ] 4.6.2: Perform manual end-to-end testing with backend.\n- [ ] 4.6.3: Conduct usability testing with user feedback.\n" --label "task,frontend" --milestone "MVP" | grep -o "[0-9]*$")
echo "    Creating Subtask 4.6.1..."
gh issue create --title "Subtask 4.6.1: Write unit tests for React components using Jest/RTL...." --body "Part of Task #{4_6} Frontend Testing\nPart of #{4} Epic 4: Frontend Application Implementation\n\n## Description\nWrite unit tests for React components using Jest/RTL." --label "subtask,frontend" --milestone "MVP"
echo "    Creating Subtask 4.6.2..."
gh issue create --title "Subtask 4.6.2: Perform manual end-to-end testing with backend...." --body "Part of Task #{4_6} Frontend Testing\nPart of #{4} Epic 4: Frontend Application Implementation\n\n## Description\nPerform manual end-to-end testing with backend." --label "subtask,frontend" --milestone "MVP"
echo "    Creating Subtask 4.6.3..."
gh issue create --title "Subtask 4.6.3: Conduct usability testing with user feedback...." --body "Part of Task #{4_6} Frontend Testing\nPart of #{4} Epic 4: Frontend Application Implementation\n\n## Description\nConduct usability testing with user feedback." --label "subtask,frontend" --milestone "MVP"

echo "Creating Epic 5..."
EPIC5_ID=$(gh issue create --title "Epic 5: Deployment and DevOps" --body "Deploy the MVP application to GCP and ensure it can be run locally via Docker.\n\n## Tasks\n- [ ] #5.1: Prepare for Production Build\n- [ ] #5.2: Docker Image Finalization\n- [ ] #5.3: Cloud Deployment (GCP)\n- [ ] #5.4: Docker Distribution for Local Use\n- [ ] #5.5: Monitoring and Logging\n" --label "epic,devops" --milestone "MVP" | grep -o "[0-9]*$")

echo "  Creating Task 5.1..."
TASK5_1_ID=$(gh issue create --title "Task 5.1: Prepare for Production Build" --body "Part of #{5} Epic 5: Deployment and DevOps\n\n## Subtasks\n- [ ] 5.1.1: Update backend configuration for production with environment variables.\n- [ ] 5.1.2: Build frontend for production and configure backend to serve static files.\n- [ ] 5.1.3: Configure CORS and security settings for production.\n" --label "task,devops" --milestone "MVP" | grep -o "[0-9]*$")
echo "    Creating Subtask 5.1.1..."
gh issue create --title "Subtask 5.1.1: Update backend configuration for production with environment..." --body "Part of Task #{5_1} Prepare for Production Build\nPart of #{5} Epic 5: Deployment and DevOps\n\n## Description\nUpdate backend configuration for production with environment variables." --label "subtask,devops" --milestone "MVP"
echo "    Creating Subtask 5.1.2..."
gh issue create --title "Subtask 5.1.2: Build frontend for production and configure backend to serve..." --body "Part of Task #{5_1} Prepare for Production Build\nPart of #{5} Epic 5: Deployment and DevOps\n\n## Description\nBuild frontend for production and configure backend to serve static files." --label "subtask,devops" --milestone "MVP"
echo "    Creating Subtask 5.1.3..."
gh issue create --title "Subtask 5.1.3: Configure CORS and security settings for production...." --body "Part of Task #{5_1} Prepare for Production Build\nPart of #{5} Epic 5: Deployment and DevOps\n\n## Description\nConfigure CORS and security settings for production." --label "subtask,devops" --milestone "MVP"

echo "  Creating Task 5.2..."
TASK5_2_ID=$(gh issue create --title "Task 5.2: Docker Image Finalization" --body "Part of #{5} Epic 5: Deployment and DevOps\n\n## Subtasks\n- [ ] 5.2.1: Ensure Dockerfile optimized with multi-stage builds.\n- [ ] 5.2.2: Test container locally with production-like settings.\n- [ ] 5.2.3: Publish Docker image to registry with versioning.\n" --label "task,devops" --milestone "MVP" | grep -o "[0-9]*$")
echo "    Creating Subtask 5.2.1..."
gh issue create --title "Subtask 5.2.1: Ensure Dockerfile optimized with multi-stage builds...." --body "Part of Task #{5_2} Docker Image Finalization\nPart of #{5} Epic 5: Deployment and DevOps\n\n## Description\nEnsure Dockerfile optimized with multi-stage builds." --label "subtask,devops" --milestone "MVP"
echo "    Creating Subtask 5.2.2..."
gh issue create --title "Subtask 5.2.2: Test container locally with production-like settings...." --body "Part of Task #{5_2} Docker Image Finalization\nPart of #{5} Epic 5: Deployment and DevOps\n\n## Description\nTest container locally with production-like settings." --label "subtask,devops" --milestone "MVP"
echo "    Creating Subtask 5.2.3..."
gh issue create --title "Subtask 5.2.3: Publish Docker image to registry with versioning...." --body "Part of Task #{5_2} Docker Image Finalization\nPart of #{5} Epic 5: Deployment and DevOps\n\n## Description\nPublish Docker image to registry with versioning." --label "subtask,devops" --milestone "MVP"

echo "  Creating Task 5.3..."
TASK5_3_ID=$(gh issue create --title "Task 5.3: Cloud Deployment (GCP)" --body "Part of #{5} Epic 5: Deployment and DevOps\n\n## Subtasks\n- [ ] 5.3.1: Set up Postgres instance on GCP (Cloud SQL) and load data.\n- [ ] 5.3.2: Deploy to Cloud Run, GKE, or App Engine.\n- [ ] 5.3.3: Configure custom domain with SSL and DNS.\n- [ ] 5.3.4: Test deployed version with full user flow.\n" --label "task,devops" --milestone "MVP" | grep -o "[0-9]*$")
echo "    Creating Subtask 5.3.1..."
gh issue create --title "Subtask 5.3.1: Set up Postgres instance on GCP (Cloud SQL) and load data...." --body "Part of Task #{5_3} Cloud Deployment (GCP)\nPart of #{5} Epic 5: Deployment and DevOps\n\n## Description\nSet up Postgres instance on GCP (Cloud SQL) and load data." --label "subtask,devops" --milestone "MVP"
echo "    Creating Subtask 5.3.2..."
gh issue create --title "Subtask 5.3.2: Deploy to Cloud Run, GKE, or App Engine...." --body "Part of Task #{5_3} Cloud Deployment (GCP)\nPart of #{5} Epic 5: Deployment and DevOps\n\n## Description\nDeploy to Cloud Run, GKE, or App Engine." --label "subtask,devops" --milestone "MVP"
echo "    Creating Subtask 5.3.3..."
gh issue create --title "Subtask 5.3.3: Configure custom domain with SSL and DNS...." --body "Part of Task #{5_3} Cloud Deployment (GCP)\nPart of #{5} Epic 5: Deployment and DevOps\n\n## Description\nConfigure custom domain with SSL and DNS." --label "subtask,devops" --milestone "MVP"
echo "    Creating Subtask 5.3.4..."
gh issue create --title "Subtask 5.3.4: Test deployed version with full user flow...." --body "Part of Task #{5_3} Cloud Deployment (GCP)\nPart of #{5} Epic 5: Deployment and DevOps\n\n## Description\nTest deployed version with full user flow." --label "subtask,devops" --milestone "MVP"

echo "  Creating Task 5.4..."
TASK5_4_ID=$(gh issue create --title "Task 5.4: Docker Distribution for Local Use" --body "Part of #{5} Epic 5: Deployment and DevOps\n\n## Subtasks\n- [ ] 5.4.1: Create documentation for local Docker usage.\n- [ ] 5.4.2: Test offline container functionality with embedded database.\n- [ ] 5.4.3: Publish self-contained image for non-technical users.\n" --label "task,devops" --milestone "MVP" | grep -o "[0-9]*$")
echo "    Creating Subtask 5.4.1..."
gh issue create --title "Subtask 5.4.1: Create documentation for local Docker usage...." --body "Part of Task #{5_4} Docker Distribution for Local Use\nPart of #{5} Epic 5: Deployment and DevOps\n\n## Description\nCreate documentation for local Docker usage." --label "subtask,devops" --milestone "MVP"
echo "    Creating Subtask 5.4.2..."
gh issue create --title "Subtask 5.4.2: Test offline container functionality with embedded database...." --body "Part of Task #{5_4} Docker Distribution for Local Use\nPart of #{5} Epic 5: Deployment and DevOps\n\n## Description\nTest offline container functionality with embedded database." --label "subtask,devops" --milestone "MVP"
echo "    Creating Subtask 5.4.3..."
gh issue create --title "Subtask 5.4.3: Publish self-contained image for non-technical users...." --body "Part of Task #{5_4} Docker Distribution for Local Use\nPart of #{5} Epic 5: Deployment and DevOps\n\n## Description\nPublish self-contained image for non-technical users." --label "subtask,devops" --milestone "MVP"

echo "  Creating Task 5.5..."
TASK5_5_ID=$(gh issue create --title "Task 5.5: Monitoring and Logging" --body "Part of #{5} Epic 5: Deployment and DevOps\n\n## Subtasks\n- [ ] 5.5.1: Set up application logging with structured logs.\n- [ ] 5.5.2: Set up error tracking with Sentry or similar.\n- [ ] 5.5.3: Monitor performance with GCP Cloud Monitoring.\n" --label "task,devops" --milestone "MVP" | grep -o "[0-9]*$")
echo "    Creating Subtask 5.5.1..."
gh issue create --title "Subtask 5.5.1: Set up application logging with structured logs...." --body "Part of Task #{5_5} Monitoring and Logging\nPart of #{5} Epic 5: Deployment and DevOps\n\n## Description\nSet up application logging with structured logs." --label "subtask,devops" --milestone "MVP"
echo "    Creating Subtask 5.5.2..."
gh issue create --title "Subtask 5.5.2: Set up error tracking with Sentry or similar...." --body "Part of Task #{5_5} Monitoring and Logging\nPart of #{5} Epic 5: Deployment and DevOps\n\n## Description\nSet up error tracking with Sentry or similar." --label "subtask,devops" --milestone "MVP"
echo "    Creating Subtask 5.5.3..."
gh issue create --title "Subtask 5.5.3: Monitor performance with GCP Cloud Monitoring...." --body "Part of Task #{5_5} Monitoring and Logging\nPart of #{5} Epic 5: Deployment and DevOps\n\n## Description\nMonitor performance with GCP Cloud Monitoring." --label "subtask,devops" --milestone "MVP"

echo "Creating Epic 6..."
EPIC6_ID=$(gh issue create --title "Epic 6: Optimization and Feature Enhancements" --body "Post-MVP: Optimize the application and add features beyond original desktop app.\n\n## Tasks\n- [ ] #6.1: Performance Optimizations\n- [ ] #6.2: Better Build Validation\n- [ ] #6.3: User Accounts and Cloud Saving\n- [ ] #6.4: In-Game Integration\n- [ ] #6.5: Continual Data Updates\n- [ ] #6.6: Clean-up and Deprecation\n" --label "epic" --milestone "Post-MVP" | grep -o "[0-9]*$")

echo "  Creating Task 6.1..."
TASK6_1_ID=$(gh issue create --title "Task 6.1: Performance Optimizations" --body "Part of #{6} Epic 6: Optimization and Feature Enhancements\n\n## Subtasks\n- [ ] 6.1.1: Profile application performance and identify bottlenecks.\n- [ ] 6.1.2: Implement API caching for static data endpoints.\n- [ ] 6.1.3: Utilize browser localStorage/IndexedDB for client caching.\n" --label "task" --milestone "Post-MVP" | grep -o "[0-9]*$")
echo "    Creating Subtask 6.1.1..."
gh issue create --title "Subtask 6.1.1: Profile application performance and identify bottlenecks...." --body "Part of Task #{6_1} Performance Optimizations\nPart of #{6} Epic 6: Optimization and Feature Enhancements\n\n## Description\nProfile application performance and identify bottlenecks." --label "subtask" --milestone "Post-MVP"
echo "    Creating Subtask 6.1.2..."
gh issue create --title "Subtask 6.1.2: Implement API caching for static data endpoints...." --body "Part of Task #{6_1} Performance Optimizations\nPart of #{6} Epic 6: Optimization and Feature Enhancements\n\n## Description\nImplement API caching for static data endpoints." --label "subtask" --milestone "Post-MVP"
echo "    Creating Subtask 6.1.3..."
gh issue create --title "Subtask 6.1.3: Utilize browser localStorage/IndexedDB for client caching...." --body "Part of Task #{6_1} Performance Optimizations\nPart of #{6} Epic 6: Optimization and Feature Enhancements\n\n## Description\nUtilize browser localStorage/IndexedDB for client caching." --label "subtask" --milestone "Post-MVP"

echo "  Creating Task 6.2..."
TASK6_2_ID=$(gh issue create --title "Task 6.2: Better Build Validation" --body "Part of #{6} Epic 6: Optimization and Feature Enhancements\n\n## Subtasks\n- [ ] 6.2.1: Introduce full ruleset for build validity with level-based limits.\n- [ ] 6.2.2: Add warnings for missing travel powers and optimization suggestions.\n" --label "task" --milestone "Post-MVP" | grep -o "[0-9]*$")
echo "    Creating Subtask 6.2.1..."
gh issue create --title "Subtask 6.2.1: Introduce full ruleset for build validity with level-based l..." --body "Part of Task #{6_2} Better Build Validation\nPart of #{6} Epic 6: Optimization and Feature Enhancements\n\n## Description\nIntroduce full ruleset for build validity with level-based limits." --label "subtask" --milestone "Post-MVP"
echo "    Creating Subtask 6.2.2..."
gh issue create --title "Subtask 6.2.2: Add warnings for missing travel powers and optimization sugg..." --body "Part of Task #{6_2} Better Build Validation\nPart of #{6} Epic 6: Optimization and Feature Enhancements\n\n## Description\nAdd warnings for missing travel powers and optimization suggestions." --label "subtask" --milestone "Post-MVP"

echo "  Creating Task 6.3..."
TASK6_3_ID=$(gh issue create --title "Task 6.3: User Accounts and Cloud Saving" --body "Part of #{6} Epic 6: Optimization and Feature Enhancements\n\n## Subtasks\n- [ ] 6.3.1: Implement login system with OAuth integration.\n- [ ] 6.3.2: Provide cloud build saving and sharing capabilities.\n- [ ] 6.3.3: Add privacy settings for builds.\n" --label "task" --milestone "Post-MVP" | grep -o "[0-9]*$")
echo "    Creating Subtask 6.3.1..."
gh issue create --title "Subtask 6.3.1: Implement login system with OAuth integration...." --body "Part of Task #{6_3} User Accounts and Cloud Saving\nPart of #{6} Epic 6: Optimization and Feature Enhancements\n\n## Description\nImplement login system with OAuth integration." --label "subtask" --milestone "Post-MVP"
echo "    Creating Subtask 6.3.2..."
gh issue create --title "Subtask 6.3.2: Provide cloud build saving and sharing capabilities...." --body "Part of Task #{6_3} User Accounts and Cloud Saving\nPart of #{6} Epic 6: Optimization and Feature Enhancements\n\n## Description\nProvide cloud build saving and sharing capabilities." --label "subtask" --milestone "Post-MVP"
echo "    Creating Subtask 6.3.3..."
gh issue create --title "Subtask 6.3.3: Add privacy settings for builds...." --body "Part of Task #{6_3} User Accounts and Cloud Saving\nPart of #{6} Epic 6: Optimization and Feature Enhancements\n\n## Description\nAdd privacy settings for builds." --label "subtask" --milestone "Post-MVP"

echo "  Creating Task 6.4..."
TASK6_4_ID=$(gh issue create --title "Task 6.4: In-Game Integration" --body "Part of #{6} Epic 6: Optimization and Feature Enhancements\n\n## Subtasks\n- [ ] 6.4.1: Explore integration with City of Heroes servers for data import.\n- [ ] 6.4.2: Implement export formats compatible with game servers.\n" --label "task" --milestone "Post-MVP" | grep -o "[0-9]*$")
echo "    Creating Subtask 6.4.1..."
gh issue create --title "Subtask 6.4.1: Explore integration with City of Heroes servers for data imp..." --body "Part of Task #{6_4} In-Game Integration\nPart of #{6} Epic 6: Optimization and Feature Enhancements\n\n## Description\nExplore integration with City of Heroes servers for data import." --label "subtask" --milestone "Post-MVP"
echo "    Creating Subtask 6.4.2..."
gh issue create --title "Subtask 6.4.2: Implement export formats compatible with game servers...." --body "Part of Task #{6_4} In-Game Integration\nPart of #{6} Epic 6: Optimization and Feature Enhancements\n\n## Description\nImplement export formats compatible with game servers." --label "subtask" --milestone "Post-MVP"

echo "  Creating Task 6.5..."
TASK6_5_ID=$(gh issue create --title "Task 6.5: Continual Data Updates" --body "Part of #{6} Epic 6: Optimization and Feature Enhancements\n\n## Subtasks\n- [ ] 6.5.1: Automate data update pipeline with scheduled jobs.\n- [ ] 6.5.2: Support multiple databases (Homecoming, Rebirth) with selection.\n" --label "task" --milestone "Post-MVP" | grep -o "[0-9]*$")
echo "    Creating Subtask 6.5.1..."
gh issue create --title "Subtask 6.5.1: Automate data update pipeline with scheduled jobs...." --body "Part of Task #{6_5} Continual Data Updates\nPart of #{6} Epic 6: Optimization and Feature Enhancements\n\n## Description\nAutomate data update pipeline with scheduled jobs." --label "subtask" --milestone "Post-MVP"
echo "    Creating Subtask 6.5.2..."
gh issue create --title "Subtask 6.5.2: Support multiple databases (Homecoming, Rebirth) with select..." --body "Part of Task #{6_5} Continual Data Updates\nPart of #{6} Epic 6: Optimization and Feature Enhancements\n\n## Description\nSupport multiple databases (Homecoming, Rebirth) with selection." --label "subtask" --milestone "Post-MVP"

echo "  Creating Task 6.6..."
TASK6_6_ID=$(gh issue create --title "Task 6.6: Clean-up and Deprecation" --body "Part of #{6} Epic 6: Optimization and Feature Enhancements\n\n## Subtasks\n- [ ] 6.6.1: Re-architect simplified components to match full mechanics.\n- [ ] 6.6.2: Remove legacy/test code and refactor duplicated logic.\n- [ ] 6.6.3: Optimize data storage schema with performance improvements.\n" --label "task" --milestone "Post-MVP" | grep -o "[0-9]*$")
echo "    Creating Subtask 6.6.1..."
gh issue create --title "Subtask 6.6.1: Re-architect simplified components to match full mechanics...." --body "Part of Task #{6_6} Clean-up and Deprecation\nPart of #{6} Epic 6: Optimization and Feature Enhancements\n\n## Description\nRe-architect simplified components to match full mechanics." --label "subtask" --milestone "Post-MVP"
echo "    Creating Subtask 6.6.2..."
gh issue create --title "Subtask 6.6.2: Remove legacy/test code and refactor duplicated logic...." --body "Part of Task #{6_6} Clean-up and Deprecation\nPart of #{6} Epic 6: Optimization and Feature Enhancements\n\n## Description\nRemove legacy/test code and refactor duplicated logic." --label "subtask" --milestone "Post-MVP"
echo "    Creating Subtask 6.6.3..."
gh issue create --title "Subtask 6.6.3: Optimize data storage schema with performance improvements...." --body "Part of Task #{6_6} Clean-up and Deprecation\nPart of #{6} Epic 6: Optimization and Feature Enhancements\n\n## Description\nOptimize data storage schema with performance improvements." --label "subtask" --milestone "Post-MVP"

echo "\nAll issues created successfully!"