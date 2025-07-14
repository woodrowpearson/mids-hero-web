#!/usr/bin/env python3
"""
Create GitHub issues from ROADMAP.md for the Mids Hero Web project.
This script generates gh CLI commands to create issues with proper labels and milestones.
"""

import json
import subprocess
import sys
from typing import List, Dict, Tuple

# Define the epic structure based on ROADMAP.md
EPICS = {
    1: {
        "title": "Epic 1: Project Setup and Planning",
        "description": "Establish the project structure, repositories, and development environment for the frontend and backend.",
        "label": "epic",
        "milestone": "MVP",
        "tasks": {
            "1.1": {
                "title": "Set Up Repositories and Codebase Structure",
                "subtasks": [
                    "Initialize a new Git repository (or mono-repo) for the project. Create folders for frontend/ and backend/ components.",
                    "Choose a naming convention and baseline license/readme. Document the project goal and stack in the README.",
                    "Configure version control and CI pipeline (set up GitHub Actions or similar to lint/test/build on pushes)."
                ]
            },
            "1.2": {
                "title": "Frontend Scaffold (React)",
                "subtasks": [
                    "Bootstrap a React app (using Create React App or Vite). Set the project to use TypeScript.",
                    "Install base dependencies (React Router, UI component library, state management).",
                    "Set up a basic file structure for React (components, services, styles). Verify dev server runs."
                ]
            },
            "1.3": {
                "title": "Backend Scaffold (FastAPI + ORM)",
                "subtasks": [
                    "Create Python virtual environment and initiate FastAPI project. Install FastAPI, Uvicorn, and ORM.",
                    "Set up basic FastAPI application with health-check endpoint (GET /ping).",
                    "Configure CORS in FastAPI to allow React dev server to call APIs.",
                    "Decide on ORM vs Django and configure accordingly.",
                    "Set up database connection config and verify backend can connect to DB."
                ]
            },
            "1.4": {
                "title": "Docker Environment",
                "subtasks": [
                    "Write Dockerfile for backend service (python:3.11-slim base).",
                    "Write Dockerfile for frontend (node alpine base or serve via backend).",
                    "Create docker-compose.yml for local development (Postgres, backend, frontend).",
                    "Test Docker setup: verify containers can communicate properly."
                ]
            }
        }
    },
    2: {
        "title": "Epic 2: Data Model & Database Integration",
        "description": "Define the database schema and import the City of Heroes data (Homecoming 2025.7.1111) into the new system.",
        "label": "epic",
        "milestone": "MVP",
        "tasks": {
            "2.1": {
                "title": "Design Database Schema",
                "subtasks": [
                    "Identify all data entities: Archetype, Powerset, Power, Enhancement, SetBonus, etc. Design ER diagram.",
                    "Translate design into SQLAlchemy/Django models with appropriate types and relationships.",
                    "Run migrations to apply schema to Postgres database."
                ]
            },
            "2.2": {
                "title": "Data Import Utilities",
                "subtasks": [
                    "Write scripts to convert existing data into new database. Investigate data sources.",
                    "Implement parser for binary .mhd files or create C# export tool.",
                    "Write Python script to insert data into Postgres via ORM.",
                    "Verify imported data: cross-check against known values."
                ]
            },
            "2.3": {
                "title": "Validation against Original",
                "subtasks": [
                    "Cross-check counts: archetypes, powers, enhancements match original.",
                    "Run scenario: verify specific known build elements exist in new DB."
                ]
            },
            "2.4": {
                "title": "Automating Future Imports",
                "subtasks": [
                    "Write general script for updating database with new game versions. Document import process."
                ]
            }
        }
    },
    3: {
        "title": "Epic 3: Backend API Development",
        "description": "Implement the backend functionality to serve data and perform calculations.",
        "label": "epic",
        "milestone": "MVP",
        "tasks": {
            "3.1": {
                "title": "Core Data Endpoints (Read Operations)",
                "subtasks": [
                    "Implement GET /api/archetypes: list all archetypes with key details.",
                    "Implement GET /api/archetypes/{id}: detailed info for specific archetype.",
                    "Implement GET /api/powersets/{id}: powerset details with power list.",
                    "Implement GET /api/powers/{id}: detailed power info.",
                    "Implement GET /api/enhancements and related endpoints.",
                    "Implement miscellaneous data endpoints for incarnates, salvage, recipes."
                ]
            },
            "3.2": {
                "title": "Build Simulation & Calculation Endpoints",
                "subtasks": [
                    "Identify key calculations: defense/resist totals, damage, endurance, validation.",
                    "Implement POST /api/calculate: compute aggregate stats including set bonuses.",
                    "Write unit tests for calculation logic with known scenarios.",
                    "Port complex calculation logic from C# to Python."
                ]
            },
            "3.3": {
                "title": "Write/Modify Operations",
                "subtasks": [
                    "Define JSON schema for build (powers and enhancements).",
                    "Implement POST /api/build/encode and /api/build/decode.",
                    "(Future) Implement authentication and user build storage."
                ]
            },
            "3.4": {
                "title": "Testing the API",
                "subtasks": [
                    "Create automated tests for each endpoint using PyTest.",
                    "Test edge cases: invalid IDs, empty inputs, error handling.",
                    "Test calculation endpoints with known builds.",
                    "Set up continuous integration to run tests."
                ]
            }
        }
    },
    4: {
        "title": "Epic 4: Frontend Application Implementation",
        "description": "Build the React UI for character planning: archetype selection, powers, enhancements, and stats.",
        "label": "epic",
        "milestone": "MVP",
        "tasks": {
            "4.1": {
                "title": "UI Layout and Navigation",
                "subtasks": [
                    "Design layout with sections for character info, powers, enhancements, stats.",
                    "Implement basic layout with placeholder components using responsive design.",
                    "Set up React Router if needed or keep as single-page app.",
                    "Integrate UI theme with light/dark mode support."
                ]
            },
            "4.2": {
                "title": "Archetype and Powerset Selection",
                "subtasks": [
                    "Create ArchetypeSelector component that fetches from API.",
                    "Create PowersetSelection components for Primary/Secondary/Pool powers.",
                    "Display Powers with level availability and prerequisites.",
                    "Implement Incarnate powers selection if included.",
                    "Update UI state with proper validation."
                ]
            },
            "4.3": {
                "title": "Enhancement Slotting Interface",
                "subtasks": [
                    "Display enhancement slots with add/remove functionality per power.",
                    "Create EnhancementPicker dialog showing valid enhancements.",
                    "Implement Set Bonus Display for active bonuses.",
                    "Show power enhancement effects on stats."
                ]
            },
            "4.4": {
                "title": "Stats Summary and Feedback",
                "subtasks": [
                    "Create SummaryPanel showing overall character stats.",
                    "Update summary on build changes via backend or frontend calculations.",
                    "Include validation warnings for invalid builds."
                ]
            },
            "4.5": {
                "title": "Polish UI & User Experience",
                "subtasks": [
                    "Add tooltips and info popups for powers and enhancements.",
                    "Implement reset/clear functionality and New Build button.",
                    "Implement import/export of builds via file or clipboard.",
                    "Ensure mobile/responsive design for smaller screens."
                ]
            },
            "4.6": {
                "title": "Frontend Testing",
                "subtasks": [
                    "Write unit tests for React components using Jest/RTL.",
                    "Perform manual end-to-end testing with backend.",
                    "Conduct usability testing with user feedback."
                ]
            }
        }
    },
    5: {
        "title": "Epic 5: Deployment and DevOps",
        "description": "Deploy the MVP application to GCP and ensure it can be run locally via Docker.",
        "label": "epic",
        "milestone": "MVP",
        "tasks": {
            "5.1": {
                "title": "Prepare for Production Build",
                "subtasks": [
                    "Update backend configuration for production with environment variables.",
                    "Build frontend for production and configure backend to serve static files.",
                    "Configure CORS and security settings for production."
                ]
            },
            "5.2": {
                "title": "Docker Image Finalization",
                "subtasks": [
                    "Ensure Dockerfile optimized with multi-stage builds.",
                    "Test container locally with production-like settings.",
                    "Publish Docker image to registry with versioning."
                ]
            },
            "5.3": {
                "title": "Cloud Deployment (GCP)",
                "subtasks": [
                    "Set up Postgres instance on GCP (Cloud SQL) and load data.",
                    "Deploy to Cloud Run, GKE, or App Engine.",
                    "Configure custom domain with SSL and DNS.",
                    "Test deployed version with full user flow."
                ]
            },
            "5.4": {
                "title": "Docker Distribution for Local Use",
                "subtasks": [
                    "Create documentation for local Docker usage.",
                    "Test offline container functionality with embedded database.",
                    "Publish self-contained image for non-technical users."
                ]
            },
            "5.5": {
                "title": "Monitoring and Logging",
                "subtasks": [
                    "Set up application logging with structured logs.",
                    "Set up error tracking with Sentry or similar.",
                    "Monitor performance with GCP Cloud Monitoring."
                ]
            }
        }
    },
    6: {
        "title": "Epic 6: Optimization and Feature Enhancements",
        "description": "Post-MVP: Optimize the application and add features beyond original desktop app.",
        "label": "epic",
        "milestone": "Post-MVP",
        "tasks": {
            "6.1": {
                "title": "Performance Optimizations",
                "subtasks": [
                    "Profile application performance and identify bottlenecks.",
                    "Implement API caching for static data endpoints.",
                    "Utilize browser localStorage/IndexedDB for client caching."
                ]
            },
            "6.2": {
                "title": "Better Build Validation",
                "subtasks": [
                    "Introduce full ruleset for build validity with level-based limits.",
                    "Add warnings for missing travel powers and optimization suggestions."
                ]
            },
            "6.3": {
                "title": "User Accounts and Cloud Saving",
                "subtasks": [
                    "Implement login system with OAuth integration.",
                    "Provide cloud build saving and sharing capabilities.",
                    "Add privacy settings for builds."
                ]
            },
            "6.4": {
                "title": "In-Game Integration",
                "subtasks": [
                    "Explore integration with City of Heroes servers for data import.",
                    "Implement export formats compatible with game servers."
                ]
            },
            "6.5": {
                "title": "Continual Data Updates",
                "subtasks": [
                    "Automate data update pipeline with scheduled jobs.",
                    "Support multiple databases (Homecoming, Rebirth) with selection."
                ]
            },
            "6.6": {
                "title": "Clean-up and Deprecation",
                "subtasks": [
                    "Re-architect simplified components to match full mechanics.",
                    "Remove legacy/test code and refactor duplicated logic.",
                    "Optimize data storage schema with performance improvements."
                ]
            }
        }
    }
}

def create_issue_commands() -> List[str]:
    """Generate gh CLI commands to create all issues."""
    commands = []
    
    # First, create milestones
    commands.append('echo "Creating milestones..."')
    commands.append('gh api repos/:owner/:repo/milestones -f title="MVP" -f description="Minimum Viable Product (Epics 1-5)"')
    commands.append('gh api repos/:owner/:repo/milestones -f title="Post-MVP" -f description="Optimization and Enhancements (Epic 6)"')
    
    # Create labels
    commands.append('\necho "Creating labels..."')
    commands.append('gh label create epic --description "Major development milestone" --color 7057ff || true')
    commands.append('gh label create task --description "Feature or requirement" --color 0075ca || true')
    commands.append('gh label create subtask --description "Implementation detail" --color d73a4a || true')
    commands.append('gh label create frontend --description "Frontend development" --color ffd700 || true')
    commands.append('gh label create backend --description "Backend development" --color 2ea44f || true')
    commands.append('gh label create database --description "Database related" --color b08800 || true')
    commands.append('gh label create devops --description "DevOps and deployment" --color 5319e7 || true')
    
    # Create issues for each epic
    for epic_num, epic_data in EPICS.items():
        commands.append(f'\necho "Creating Epic {epic_num}..."')
        
        # Create the epic issue
        epic_body = f"{epic_data['description']}\\n\\n"
        epic_body += "## Tasks\\n"
        for task_id, task_data in epic_data['tasks'].items():
            epic_body += f"- [ ] #{task_id}: {task_data['title']}\\n"
        
        epic_labels = f"{epic_data['label']}"
        if epic_num in [1, 5]:
            epic_labels += ",devops"
        elif epic_num == 2:
            epic_labels += ",database,backend"
        elif epic_num == 3:
            epic_labels += ",backend"
        elif epic_num == 4:
            epic_labels += ",frontend"
        
        commands.append(
            f'EPIC{epic_num}_ID=$(gh issue create '
            f'--title "{epic_data["title"]}" '
            f'--body "{epic_body}" '
            f'--label "{epic_labels}" '
            f'--milestone "{epic_data["milestone"]}" | grep -o "[0-9]*$")'
        )
        
        # Create task issues
        for task_id, task_data in epic_data['tasks'].items():
            commands.append(f'\necho "  Creating Task {task_id}..."')
            
            task_body = f"Part of #{{{epic_num}}} {epic_data['title']}\\n\\n"
            task_body += "## Subtasks\\n"
            for i, subtask in enumerate(task_data['subtasks'], 1):
                task_body += f"- [ ] {task_id}.{i}: {subtask}\\n"
            
            task_labels = "task"
            if epic_num in [1, 5]:
                task_labels += ",devops"
            elif epic_num == 2:
                task_labels += ",database,backend"
            elif epic_num == 3:
                task_labels += ",backend"
            elif epic_num == 4:
                task_labels += ",frontend"
            
            task_title = f"Task {task_id}: {task_data['title']}"
            
            commands.append(
                f'TASK{task_id.replace(".", "_")}_ID=$(gh issue create '
                f'--title "{task_title}" '
                f'--body "{task_body}" '
                f'--label "{task_labels}" '
                f'--milestone "{epic_data["milestone"]}" | grep -o "[0-9]*$")'
            )
            
            # Create subtask issues
            for i, subtask in enumerate(task_data['subtasks'], 1):
                subtask_id = f"{task_id}.{i}"
                commands.append(f'echo "    Creating Subtask {subtask_id}..."')
                
                subtask_body = (
                    f"Part of Task #{{{task_id.replace('.', '_')}}} {task_data['title']}\\n"
                    f"Part of #{{{epic_num}}} {epic_data['title']}\\n\\n"
                    f"## Description\\n{subtask}"
                )
                
                subtask_labels = "subtask"
                if epic_num in [1, 5]:
                    subtask_labels += ",devops"
                elif epic_num == 2:
                    subtask_labels += ",database,backend"
                elif epic_num == 3:
                    subtask_labels += ",backend"
                elif epic_num == 4:
                    subtask_labels += ",frontend"
                
                subtask_title = f"Subtask {subtask_id}: {subtask[:60]}..."
                
                commands.append(
                    f'gh issue create '
                    f'--title "{subtask_title}" '
                    f'--body "{subtask_body}" '
                    f'--label "{subtask_labels}" '
                    f'--milestone "{epic_data["milestone"]}"'
                )
    
    return commands

def main():
    """Generate the shell script to create all GitHub issues."""
    
    print("Generating GitHub issue creation script...")
    
    commands = create_issue_commands()
    
    # Write to shell script
    script_content = "#!/bin/bash\n\n"
    script_content += "# Script to create all GitHub issues for Mids Hero Web project\n"
    script_content += "# Run this after setting up your GitHub repository\n\n"
    script_content += "set -e  # Exit on error\n\n"
    script_content += "# Ensure we're in a git repository with a remote\n"
    script_content += 'if ! git remote get-url origin > /dev/null 2>&1; then\n'
    script_content += '    echo "Error: No git remote found. Please add a GitHub remote first."\n'
    script_content += '    echo "Example: git remote add origin https://github.com/yourusername/mids-hero-web.git"\n'
    script_content += '    exit 1\n'
    script_content += 'fi\n\n'
    script_content += "# Check if gh CLI is installed\n"
    script_content += 'if ! command -v gh &> /dev/null; then\n'
    script_content += '    echo "Error: GitHub CLI (gh) is not installed."\n'
    script_content += '    echo "Please install it from: https://cli.github.com/"\n'
    script_content += '    exit 1\n'
    script_content += 'fi\n\n'
    script_content += "# Check if authenticated\n"
    script_content += 'if ! gh auth status > /dev/null 2>&1; then\n'
    script_content += '    echo "Error: Not authenticated with GitHub CLI."\n'
    script_content += '    echo "Please run: gh auth login"\n'
    script_content += '    exit 1\n'
    script_content += 'fi\n\n'
    
    script_content += "\n".join(commands)
    script_content += '\n\necho "\\nAll issues created successfully!"'
    
    with open("create_issues.sh", "w") as f:
        f.write(script_content)
    
    print("Script generated: create_issues.sh")
    print("\nTo use this script:")
    print("1. Ensure you have a GitHub repository set up")
    print("2. Make sure you have the GitHub CLI (gh) installed and authenticated")
    print("3. Run: chmod +x create_issues.sh")
    print("4. Run: ./create_issues.sh")

if __name__ == "__main__":
    main()