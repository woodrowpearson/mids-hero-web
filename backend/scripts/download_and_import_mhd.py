#!/usr/bin/env python3
"""Download MHD JSON exports from GitHub Actions and import to database."""

import os
import sys
import json
import zipfile
import tempfile
import subprocess
from pathlib import Path

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def download_latest_artifact():
    """Download the latest mhd-exported-json artifact from GitHub Actions."""
    print("Downloading latest MHD export from GitHub Actions...")
    
    # Use GitHub CLI to download artifact
    cmd = [
        "gh", "run", "download", "--name", "mhd-exported-json",
        "--repo", "w/mids-hero-web"  # Update with actual repo
    ]
    
    try:
        subprocess.run(cmd, check=True)
        return Path("mhd-exported-json")
    except subprocess.CalledProcessError:
        print("Failed to download artifact. Make sure:")
        print("1. GitHub CLI (gh) is installed and authenticated")
        print("2. The export workflow has been run at least once")
        print("3. You have access to the repository")
        return None


def import_from_directory(json_dir: Path):
    """Import JSON files from directory to database."""
    print(f"\nImporting JSON files from {json_dir}...")
    
    # Run the import script
    import_script = Path(__file__).parent / "import_mhd_json_to_db.py"
    cmd = [
        sys.executable,
        str(import_script),
        str(json_dir)
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("\nImport completed successfully!")
    except subprocess.CalledProcessError:
        print("\nImport failed!")
        return False
    
    return True


def main():
    """Main function."""
    print("MHD Data Import from GitHub Actions")
    print("===================================\n")
    
    # Option to use local directory or download
    if len(sys.argv) > 1:
        json_dir = Path(sys.argv[1])
        if not json_dir.exists():
            print(f"Error: Directory not found: {json_dir}")
            sys.exit(1)
    else:
        # Download from GitHub Actions
        json_dir = download_latest_artifact()
        if not json_dir:
            sys.exit(1)
    
    # Import the data
    if import_from_directory(json_dir):
        # Clean up downloaded files
        if json_dir.name == "mhd-exported-json" and len(sys.argv) == 1:
            print(f"\nCleaning up {json_dir}...")
            import shutil
            shutil.rmtree(json_dir)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()