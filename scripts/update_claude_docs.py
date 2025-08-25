#!/usr/bin/env python3
"""Auto-update Claude documentation based on codebase changes."""

import json
import os
import subprocess
from pathlib import Path
import tiktoken
import yaml
from datetime import datetime

def count_tokens(text):
    """Count tokens in text using tiktoken."""
    encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))

def update_readme():
    """Update .claude/README.md with current directory structure."""
    claude_dir = Path(".claude")
    readme_path = claude_dir / "README.md"
    
    # Read existing README
    content = readme_path.read_text()
    
    # Update last modified date
    today = datetime.now().strftime("%Y-%m-%d")
    content = content.replace(
        "Last updated:",
        f"Last updated: {today}"
    )
    
    # Write back
    readme_path.write_text(content)
    print(f"Updated {readme_path}")

def check_file_sizes():
    """Check and report files exceeding token limits."""
    context_map = json.loads(Path(".claude/context-map.json").read_text())
    limits = context_map["file_health_checks"]["max_file_sizes"]
    
    issues = []
    
    # Check CLAUDE.md
    claude_md = Path("CLAUDE.md")
    if claude_md.exists():
        tokens = count_tokens(claude_md.read_text())
        limit = limits["CLAUDE.md"]
        if tokens > limit * 0.9:  # 90% threshold
            issues.append(f"CLAUDE.md: {tokens}/{limit} tokens (>90%)")
    
    # Check module guides
    modules_dir = Path(".claude/modules")
    for module_path in modules_dir.glob("*/guide.md"):
        tokens = count_tokens(module_path.read_text())
        limit = limits["module_guide"]
        if tokens > limit * 0.9:
            issues.append(f"{module_path}: {tokens}/{limit} tokens (>90%)")
    
    if issues:
        print("⚠️  Files approaching token limits:")
        for issue in issues:
            print(f"  - {issue}")
        
        # Create issue if needed
        with open("token_limit_warnings.txt", "w") as f:
            f.write("\n".join(issues))

def update_progress_timestamp():
    """Update progress.json with current timestamp."""
    progress_file = Path(".claude/state/progress.json")
    if progress_file.exists():
        progress = json.loads(progress_file.read_text())
        progress["last_auto_update"] = datetime.now().isoformat()
        progress_file.write_text(json.dumps(progress, indent=2))
        print(f"Updated {progress_file}")

def update_documentation_timestamps():
    """Update timestamps on all Claude documentation files."""
    timestamp_script = Path(".claude/scripts/add_timestamp.py")
    
    if timestamp_script.exists():
        # Run timestamp update for all .claude documentation
        result = subprocess.run(
            ["python3", str(timestamp_script), ".claude", "--recursive"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Documentation timestamps updated")
            if result.stdout:
                print(result.stdout)
        else:
            print("⚠️  Error updating timestamps:")
            if result.stderr:
                print(result.stderr)
    else:
        print("⚠️  Timestamp script not found at", timestamp_script)

def main():
    """Run all documentation updates."""
    print("🔄 Updating Claude documentation...")
    
    update_readme()
    check_file_sizes()
    update_progress_timestamp()
    update_documentation_timestamps()
    
    print("✅ Documentation update complete")

if __name__ == "__main__":
    main()
