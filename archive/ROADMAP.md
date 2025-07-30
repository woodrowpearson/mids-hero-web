# Development Roadmap

This roadmap outlines the development plan for implementing the new web-based Mids Reborn. The plan is organized into **Epics** (major goals or milestones), each broken down into specific **Tasks**, which are further subdivided into **Sub-tasks** as needed.

## Epic 1: Project Setup and Planning

**Goal:** Establish the project structure, repositories, and development environment for the frontend and backend.

### Task 1.1: Set Up Repositories and Codebase Structure

- **Sub-task 1.1.1:** Initialize a new Git repository (or mono-repo) for the project. Create folders for `frontend/` and `backend/` components.
- **Sub-task 1.1.2:** Choose a naming convention and baseline license/readme. Document the project goal and stack in the README (mentioning React, FastAPI, Postgres, etc.).
- **Sub-task 1.1.3:** Configure version control and CI pipeline (set up GitHub Actions or similar to lint/test/build on pushes).

### Task 1.2: Frontend Scaffold (React)

- **Sub-task 1.2.1:** Bootstrap a React app (using Create React App or Vite for a lightweight setup). Set the project to use TypeScript (recommended for easier maintenance and catching errors early) or JavaScript as per team preference.
- **Sub-task 1.2.2:** Install base dependencies (e.g. React Router for navigation if needed, a UI component library like Material-UI, state management like Redux or Context API if complexity grows).
- **Sub-task 1.2.3:** Set up a basic file structure for React (components, services for API calls, styles). Verify that the dev server runs and you can open a default page.

### Task 1.3: Backend Scaffold (FastAPI + ORM)

- **Sub-task 1.3.1:** Create a Python virtual environment and initiate a FastAPI project. Install FastAPI and Uvicorn, plus an ORM library (SQLAlchemy with Alembic for migrations, or Tortoise ORM, etc.).
- **Sub-task 1.3.2:** Set up the basic FastAPI application file (e.g. `main.py`) with a simple health-check endpoint (e.g. `GET /ping` returning "pong") to verify the server runs.
- **Sub-task 1.3.3:** Configure CORS in FastAPI to allow the React dev server to call the APIs (during development).
- **Sub-task 1.3.4:** Decide on ORM vs Django: If using Django, run `django-admin startproject` and integrate Django REST framework; otherwise, configure SQLAlchemy models manually. (This task includes making that architectural decision early.)
- **Sub-task 1.3.5:** Set up database connection config (for now, can use SQLite or a local Postgres instance for dev). Verify the backend can connect to DB.

### Task 1.4: Docker Environment

- **Sub-task 1.4.1:** Write a `Dockerfile` for the backend service (base image python:3.11-slim, copy code, uv install, expose port, command to run Uvicorn).
- **Sub-task 1.4.2:** Write a `Dockerfile` for the frontend (could use node:16-alpine to build, then nginx:alpine to serve static files, or simply use multi-stage and serve via a lightweight server). Alternatively, plan to serve frontend via the backend (in which case, just ensure frontend build outputs can be integrated).
- **Sub-task 1.4.3:** Create a `docker-compose.yml` for local development that brings up: the Postgres database, the backend (mount code for hot-reload in dev), and the frontend (if needed). Ensure `docker-compose up` can start the whole stack in development mode.
- **Sub-task 1.4.4:** Test the Docker setup: verify the backend container can talk to the Postgres container (adjust environment variables accordingly), and that the frontend container can reach the backend's API (network configuration).

## Epic 2: Data Model & Database Integration

**Goal:** Define the database schema and import the City of Heroes data (Homecoming 2025.7.1111) into the new system.

### Task 2.1: Design Database Schema

- **Sub-task 2.1.1:** Identify all data entities from the original app: Archetype, Powerset, Power, Enhancement, SetBonus, Salvage, Recipe, etc., and their relationships. Design an ER diagram or outline.
- **Sub-task 2.1.2:** Translate the design into SQLAlchemy models or Django models. Define fields with appropriate types (e.g., integers for IDs, floats for percentages, text for descriptions). Include foreign keys for relationships and indexes on important fields.
- **Sub-task 2.1.3:** Run migrations (or create the database via sync) to apply the schema to the Postgres database. This yields empty tables ready to be filled.

### Task 2.2: Data Import Utilities

- **Sub-task 2.2.1:** Write scripts to convert existing data into the new database. Investigate available data sources from Mids Reborn data files directly or from update manifests.
- **Sub-task 2.2.2:** Implement a parser for binary .mhd files (if needed). For example, for `I12.mhd`, replicate the reading logic or create a C# export tool using existing Mids Reborn code.
- **Sub-task 2.2.3:** Once data is available in an intermediary form (JSON or CSV), write a Python script to insert it into the Postgres database via the ORM. Ensure to maintain referential integrity.
- **Sub-task 2.2.4:** Verify the imported data: pick a few examples and cross-check against known values to ensure no data loss or corruption in the import.

### Task 2.3: Validation against Original

- **Sub-task 2.3.1:** Cross-check counts: The number of archetypes, total powers, total enhancements, etc., in the new DB should match those from the original data.
- **Sub-task 2.3.2:** Run a small scenario: pick a specific build that was known to the original and ensure all those elements exist in the new DB.

### Task 2.4: Automating Future Imports

- **Sub-task 2.4.1:** Write a general script or document a procedure for updating the database when a new game version is released. Document the import process for future automation.

## Epic 3: Backend API Development

**Goal:** Implement the backend functionality to serve data and perform calculations, aligning with all features needed by the frontend.

### Task 3.1: Core Data Endpoints (Read Operations)

- **Sub-task 3.1.1:** Implement `GET /api/archetypes`: returns list of all archetypes with key details (id, name, origin list, primary/secondary set names).
- **Sub-task 3.1.2:** Implement `GET /api/archetypes/{id}`: returns detailed info for a specific archetype, including its powersets or create separate endpoint for powersets.
- **Sub-task 3.1.3:** Implement `GET /api/powersets/{id}`: returns details of a powerset, including the list of powers in it with each power's name, level availability, etc.
- **Sub-task 3.1.4:** Implement `GET /api/powers/{id}`: returns detailed info for a single power including descriptions, base damage, endurance cost, recharge, effects, etc.
- **Sub-task 3.1.5:** Implement `GET /api/enhancements` and related endpoints for enhancement sets, individual enhancements, and power-specific enhancement queries.
- **Sub-task 3.1.6:** Implement any miscellaneous data endpoints for incarnates, salvage, recipes as needed for MVP.

### Task 3.2: Build Simulation & Calculation Endpoints

- **Sub-task 3.2.1:** Identify the key calculations the original app performs: defense/resist totals, attack damage with enhancements, endurance consumption, validation rules.
- **Sub-task 3.2.2:** Implement `POST /api/calculate`: accepts current build in JSON format and responds with computed aggregate stats including set bonuses.
- **Sub-task 3.2.3:** Write unit tests for the calculation logic using known scenarios and expected outcomes from the original app.
- **Sub-task 3.2.4:** Port complex calculation logic from the original C# code to Python to ensure consistency and accuracy.

### Task 3.3: Write/Modify Operations (if needed for MVP)

- **Sub-task 3.3.1:** Define a JSON schema for a build (list of chosen powers and enhancements) for save/load functionality.
- **Sub-task 3.3.2:** Implement `POST /api/build/encode` and `POST /api/build/decode` for build export/import functionality.
- **Sub-task 3.3.3:** (Future consideration) Implement authentication and user build storage endpoints if user accounts are planned.

### Task 3.4: Testing the API

- **Sub-task 3.4.1:** Create automated tests for each endpoint using PyTest or FastAPI's test client.
- **Sub-task 3.4.2:** Test edge cases: invalid IDs, empty inputs, error handling.
- **Sub-task 3.4.3:** Test calculation endpoints with known simple builds and verify output.
- **Sub-task 3.4.4:** Set up continuous integration to run tests and catch regressions.

## Epic 4: Frontend Application Implementation

**Goal:** Build the React UI to allow users to perform all the tasks the WinForms app could: select an archetype, choose powers, slot enhancements, and view results.

### Task 4.1: UI Layout and Navigation

- **Sub-task 4.1.1:** Design a layout structure with sections for character info, power selection, enhancement slots, and stats summary.
- **Sub-task 4.1.2:** Implement a basic layout with placeholder components for each area using responsive grid or flexbox.
- **Sub-task 4.1.3:** Set up React Router if multiple routes are needed, or keep as single-page app with conditional renders.
- **Sub-task 4.1.4:** Integrate a UI theme and test styling (light vs dark mode) with legible fonts and colors.

### Task 4.2: Archetype and Powerset Selection

- **Sub-task 4.2.1:** Create an **ArchetypeSelector** component that fetches archetypes from API and handles selection.
- **Sub-task 4.2.2:** Create **PowersetSelection** components for Primary, Secondary, and Pool powers with appropriate constraints.
- **Sub-task 4.2.3:** Display Powers within each selected powerset with level availability and prerequisite handling.
- **Sub-task 4.2.4:** Implement Incarnate powers selection if included in the data.
- **Sub-task 4.2.5:** Update UI state as user selects archetype and powersets, with proper validation.

### Task 4.3: Enhancement Slotting Interface

- **Sub-task 4.3.1:** For each chosen power, display enhancement slots with ability to add/remove slots per power.
- **Sub-task 4.3.2:** Create **EnhancementPicker** dialog/popover that shows valid enhancements for a power slot.
- **Sub-task 4.3.3:** Implement Set Bonus Display that shows active set bonuses when multiple pieces of the same set are slotted.
- **Sub-task 4.3.4:** Show power enhancement effects - how enhancements modify each power's stats.

### Task 4.4: Stats Summary and Feedback

- **Sub-task 4.4.1:** Create a **SummaryPanel** that shows overall character stats (defense, damage, endurance, etc.).
- **Sub-task 4.4.2:** Update summary whenever the build changes, either via backend calculate endpoint or frontend calculations.
- **Sub-task 4.4.3:** Include validation warnings for invalid builds (too many powers, slot limits, etc.).

### Task 4.5: Polish UI & User Experience

- **Sub-task 4.5.1:** Add tooltips and info popups for powers and enhancements with detailed descriptions.
- **Sub-task 4.5.2:** Implement reset/clear functionality and "New Build" button.
- **Sub-task 4.5.3:** Implement import/export of builds via file download/upload or clipboard codes.
- **Sub-task 4.5.4:** Ensure mobile/responsive design considerations for smaller screens.

### Task 4.6: Frontend Testing

- **Sub-task 4.6.1:** Write unit tests for React components using Jest/React Testing Library.
- **Sub-task 4.6.2:** Perform manual end-to-end testing with backend to verify full build creation workflow.
- **Sub-task 4.6.3:** Conduct usability testing with feedback from users to refine UI/UX.

## Epic 5: Deployment and DevOps

**Goal:** Deploy the MVP application to a cloud environment (GCP) and ensure it can be easily run locally via Docker.

### Task 5.1: Prepare for Production Build

- **Sub-task 5.1.1:** Update backend configuration for production with environment variables and disable debug modes.
- **Sub-task 5.1.2:** Build the frontend for production and configure backend to serve static files.
- **Sub-task 5.1.3:** Configure CORS and security settings appropriately for production.

### Task 5.2: Docker Image Finalization

- **Sub-task 5.2.1:** Ensure Dockerfile is optimized with multi-stage builds and reduced image size.
- **Sub-task 5.2.2:** Test container locally with production-like settings and local Postgres.
- **Sub-task 5.2.3:** Publish Docker image to container registry with proper versioning.

### Task 5.3: Cloud Deployment (GCP)

- **Sub-task 5.3.1:** Set up Postgres instance on GCP (Cloud SQL) and load the imported data.
- **Sub-task 5.3.2:** Deploy to Cloud Run, GKE, or App Engine with proper configuration.
- **Sub-task 5.3.3:** Configure custom domain with SSL and DNS setup.
- **Sub-task 5.3.4:** Test the deployed version thoroughly with full user flow testing.

### Task 5.4: Docker Distribution for Local Use

- **Sub-task 5.4.1:** Create documentation for local Docker usage with docker-compose setup.
- **Sub-task 5.4.2:** Test offline container functionality with embedded database.
- **Sub-task 5.4.3:** Publish self-contained image for non-technical users.

### Task 5.5: Monitoring and Logging

- **Sub-task 5.5.1:** Set up application logging for production with structured logs.
- **Sub-task 5.5.2:** Set up error tracking with Sentry or similar service.
- **Sub-task 5.5.3:** Monitor performance with GCP Cloud Monitoring and set up alerts.

## Epic 6: Optimization and Feature Enhancements (Post-MVP)

**Goal:** Optimize the application and add features that go beyond the original desktop app capabilities.

### Task 6.1: Performance Optimizations

- **Sub-task 6.1.1:** Profile application performance and identify bottlenecks in frontend and backend.
- **Sub-task 6.1.2:** Implement API caching for static data endpoints with CDN or in-memory caching.
- **Sub-task 6.1.3:** Utilize browser localStorage or IndexedDB to cache game data on client.

### Task 6.2: Better Build Validation

- **Sub-task 6.2.1:** Introduce full ruleset for build validity with level-based power picks and pool selection limits.
- **Sub-task 6.2.2:** Add warnings for missing travel powers and other build optimization suggestions.

### Task 6.3: User Accounts and Cloud Saving

- **Sub-task 6.3.1:** Implement login system with OAuth integration for user accounts.
- **Sub-task 6.3.2:** Provide cloud build saving and sharing capabilities.
- **Sub-task 6.3.3:** Add privacy settings for builds (public/private sharing).

### Task 6.4: In-Game Integration (Long-term)

- **Sub-task 6.4.1:** Explore integration with City of Heroes servers for character data import.
- **Sub-task 6.4.2:** Implement export formats compatible with game servers or other tools.

### Task 6.5: Continual Data Updates

- **Sub-task 6.5.1:** Automate data update pipeline with scheduled jobs for new game versions.
- **Sub-task 6.5.2:** Support multiple simultaneous databases (Homecoming, Rebirth) with user selection.

### Task 6.6: Clean-up and Deprecation

- **Sub-task 6.6.1:** Re-architect simplified components to match full game mechanics.
- **Sub-task 6.6.2:** Remove legacy/test code and refactor duplicated logic.
- **Sub-task 6.6.3:** Optimize data storage schema with performance improvements.

---

## Implementation Notes

- **MVP Focus:** Epics 1-5 constitute the Minimum Viable Product
- **Feature Parity:** All core features from the original desktop app must be preserved
- **Community Feedback:** Each epic should include user testing and community input
- **Documentation:** Maintain developer and user documentation throughout development
- **Testing:** Comprehensive testing at each stage to ensure quality and stability

This roadmap provides a structured approach to building a modern, web-based character planner that maintains the power and functionality of the original Mids Reborn while providing enhanced accessibility and maintainability.
