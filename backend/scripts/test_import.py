#!/usr/bin/env python3
"""Test script for data import functionality."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.data_import.cli import main

if __name__ == "__main__":
    # Test the CLI
    main()
