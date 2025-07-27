#!/usr/bin/env python3
"""Configuration for session management system.

This module provides configuration options for where session data is stored.
"""

import os
from pathlib import Path
from typing import Optional


class SessionConfig:
    """Configuration for session management storage locations."""
    
    @staticmethod
    def get_session_dir(use_project_dir: bool = False) -> Path:
        """Get the directory for session data.
        
        Args:
            use_project_dir: If True, use project .claude/sessions directory
                           If False, use ~/.claude/sessions (default)
        
        Returns:
            Path to session directory
        """
        if use_project_dir:
            # Try to find project root
            project_root = SessionConfig._find_project_root()
            if project_root:
                return project_root / ".claude" / "sessions"
        
        # Default to home directory
        return Path.home() / ".claude" / "sessions"
    
    @staticmethod
    def get_auto_summary_dir(use_project_dir: bool = False) -> Path:
        """Get the directory for auto-summary data."""
        if use_project_dir:
            project_root = SessionConfig._find_project_root()
            if project_root:
                return project_root / ".claude" / "auto_summary"
        
        return Path.home() / ".claude" / "auto_summary"
    
    @staticmethod
    def get_threshold_config_path(use_project_dir: bool = False) -> Path:
        """Get the path for threshold configuration."""
        if use_project_dir:
            project_root = SessionConfig._find_project_root()
            if project_root:
                return project_root / ".claude" / "context-map.json"
        
        return Path.home() / ".claude" / "context-map.json"
    
    @staticmethod
    def _find_project_root() -> Optional[Path]:
        """Find the project root by looking for .git directory."""
        current = Path.cwd()
        
        while current != current.parent:
            if (current / ".git").exists():
                return current
            current = current.parent
        
        return None
    
    @staticmethod
    def get_storage_info() -> dict:
        """Get information about current storage configuration."""
        info = {
            "home_dir": {
                "sessions": str(Path.home() / ".claude" / "sessions"),
                "auto_summary": str(Path.home() / ".claude" / "auto_summary"),
                "context_map": str(Path.home() / ".claude" / "context-map.json"),
            },
            "project_dir": None
        }
        
        project_root = SessionConfig._find_project_root()
        if project_root:
            info["project_dir"] = {
                "root": str(project_root),
                "sessions": str(project_root / ".claude" / "sessions"),
                "auto_summary": str(project_root / ".claude" / "auto_summary"),
                "context_map": str(project_root / ".claude" / "context-map.json"),
            }
        
        # Check environment variable
        info["use_project_dir"] = os.getenv("CLAUDE_USE_PROJECT_DIR", "false").lower() == "true"
        
        return info


def main():
    """Show current configuration."""
    print("Session Management Storage Configuration")
    print("=" * 40)
    
    info = SessionConfig.get_storage_info()
    
    print("\nHome Directory Storage:")
    for key, path in info["home_dir"].items():
        exists = Path(path).exists() if not path.endswith(".json") else Path(path).exists()
        status = "✓" if exists else "✗"
        print(f"  {status} {key:12}: {path}")
    
    if info["project_dir"]:
        print("\nProject Directory Storage:")
        for key, path in info["project_dir"].items():
            if key == "root":
                continue
            exists = Path(path).exists() if not path.endswith(".json") else Path(path).exists()
            status = "✓" if exists else "✗"
            print(f"  {status} {key:12}: {path}")
    
    print(f"\nCurrent Mode: {'Project' if info['use_project_dir'] else 'Home'} Directory")
    print("\nTo use project directory, set: export CLAUDE_USE_PROJECT_DIR=true")


if __name__ == "__main__":
    main()