#!/usr/bin/env python3
"""
Development helper script for Mids-Web project using uv.
"""

import subprocess
import sys
from pathlib import Path


def run_command(command, cwd=None):
    """Run a command and return the result."""
    try:
        result = subprocess.run(
            command, shell=True, cwd=cwd, check=True, capture_output=True, text=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}")
        print(f"Error: {e.stderr}")
        return None


def main():
    """Main function to handle command line arguments."""
    if len(sys.argv) < 2:
        print("Usage: python scripts/dev.py <command>")
        print("\nAvailable commands:")
        print("  setup     - Set up the development environment")
        print("  install   - Install dependencies")
        print("  run       - Run the backend server")
        print("  test      - Run tests")
        print("  lint      - Run linting")
        print("  format    - Format code")
        print("  migrate   - Run database migrations")
        print("  clean     - Clean up build artifacts")
        return

    command = sys.argv[1]
    backend_dir = Path(__file__).parent.parent / "backend"

    if command == "setup":
        print("Setting up development environment...")
        print("Installing uv if not already installed...")
        run_command("curl -LsSf https://astral.sh/uv/install.sh | sh", cwd=backend_dir)
        print("Installing dependencies...")
        run_command("uv sync", cwd=backend_dir)
        print("Setup complete!")

    elif command == "install":
        print("Installing dependencies...")
        run_command("uv sync", cwd=backend_dir)
        print("Dependencies installed!")

    elif command == "run":
        print("Starting backend server...")
        run_command(
            "uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000",
            cwd=backend_dir,
        )

    elif command == "test":
        print("Running tests...")
        run_command("uv run pytest", cwd=backend_dir)

    elif command == "lint":
        print("Running linting...")
        run_command("uv run ruff check .", cwd=backend_dir)
        run_command("uv run mypy .", cwd=backend_dir)

    elif command == "format":
        print("Formatting code...")
        run_command("uv run black .", cwd=backend_dir)
        run_command("uv run isort .", cwd=backend_dir)
        run_command("uv run ruff format .", cwd=backend_dir)

    elif command == "migrate":
        print("Running database migrations...")
        run_command("uv run alembic upgrade head", cwd=backend_dir)

    elif command == "clean":
        print("Cleaning up build artifacts...")
        # Use proper commands instead of rm -rf
        run_command("fd __pycache__ -t d -x trash", cwd=backend_dir)
        run_command("fd -e pyc -x trash", cwd=backend_dir)
        run_command("trash .pytest_cache", cwd=backend_dir)
        run_command("trash .mypy_cache", cwd=backend_dir)
        run_command("trash .ruff_cache", cwd=backend_dir)
        print("Clean complete!")

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
