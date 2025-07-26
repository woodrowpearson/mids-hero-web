#!/usr/bin/env python3
"""Migrate session data from home directory to project directory."""

import json
import shutil
from pathlib import Path


def find_project_root() -> Path:
    """Find project root by looking for .git."""
    current = Path.cwd()
    while current != current.parent:
        if (current / ".git").exists():
            return current
        current = current.parent
    return Path.cwd()


def migrate_session_data():
    """Migrate session data from ~/.claude to project .claude/sessions."""
    # Find directories
    home_claude = Path.home() / ".claude"
    project_root = find_project_root()
    project_sessions = project_root / ".claude" / "sessions"
    
    print(f"🔄 Migrating session data")
    print(f"   From: {home_claude}")
    print(f"   To:   {project_sessions}")
    
    # Create project directory
    project_sessions.mkdir(parents=True, exist_ok=True)
    
    # Files to migrate
    migrations = []
    
    # Check for session metadata
    home_sessions = home_claude / "sessions"
    if home_sessions.exists():
        metadata_file = home_sessions / "session_metadata.json"
        if metadata_file.exists():
            # Only migrate sessions for this project
            with open(metadata_file) as f:
                metadata = json.load(f)
            
            project_sessions_data = {"sessions": {}, "active_session": None}
            
            for session_id, session_info in metadata.get("sessions", {}).items():
                # Check if session belongs to this project
                if session_info.get("working_directory") == str(project_root):
                    project_sessions_data["sessions"][session_id] = session_info
                    
                    # Migrate session state files
                    for pattern in [f"{session_id}_state.json", f"{session_id}_checkpoint_*.json"]:
                        for state_file in home_sessions.glob(pattern):
                            dest = project_sessions / state_file.name
                            if not dest.exists():
                                shutil.copy2(state_file, dest)
                                migrations.append(f"   ✓ {state_file.name}")
            
            # Save project-specific metadata
            if project_sessions_data["sessions"]:
                with open(project_sessions / "session_metadata.json", "w") as f:
                    json.dump(project_sessions_data, f, indent=2)
                migrations.append("   ✓ session_metadata.json (filtered)")
    
    # Migrate auto-summary states
    home_auto_summary = home_claude / "auto_summary"
    if home_auto_summary.exists():
        for auto_state in home_auto_summary.glob("*_auto_state.json"):
            # Check if it belongs to this project
            try:
                with open(auto_state) as f:
                    state = json.load(f)
                # Simple check - you might want to enhance this
                dest = project_sessions / auto_state.name
                if not dest.exists():
                    shutil.copy2(auto_state, dest)
                    migrations.append(f"   ✓ {auto_state.name}")
            except:
                pass
    
    # Migrate thresholds
    home_thresholds = home_claude / "thresholds.json"
    if home_thresholds.exists():
        project_thresholds = project_root / ".claude" / "thresholds.json"
        if not project_thresholds.exists():
            shutil.copy2(home_thresholds, project_thresholds)
            migrations.append("   ✓ thresholds.json")
    
    # Report results
    if migrations:
        print(f"\n✅ Migrated {len(migrations)} files:")
        for item in migrations:
            print(item)
    else:
        print("\n📭 No data to migrate")
    
    # Cleanup prompt
    if home_sessions.exists() and migrations:
        print(f"\n💡 You can now remove old data from {home_claude}")
        print("   Run: trash ~/.claude/sessions ~/.claude/auto_summary")


def main():
    """Run migration."""
    migrate_session_data()


if __name__ == "__main__":
    main()