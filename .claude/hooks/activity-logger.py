#!/usr/bin/env python3
"""
Claude Code hook for logging development activity
Tracks tool usage and provides session insights
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime

def log_activity():
    """Log Claude Code activity for session tracking."""
    try:
        # Read input from Claude Code
        input_data = json.load(sys.stdin)
        
        # Extract key information
        tool_name = input_data.get('tool_name', 'unknown')
        tool_input = input_data.get('tool_input', {})
        
        # Create log entry
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'tool': tool_name,
            'session_id': input_data.get('session_id', 'unknown')
        }
        
        # Add tool-specific details
        if tool_name == 'Bash':
            log_entry['command'] = tool_input.get('command', '')
            log_entry['description'] = tool_input.get('description', '')
        elif tool_name in ['Edit', 'MultiEdit', 'Write']:
            log_entry['file_path'] = tool_input.get('file_path', '')
            log_entry['operation'] = tool_name
        elif tool_name == 'Read':
            log_entry['file_path'] = tool_input.get('file_path', '')
            log_entry['operation'] = 'read'
        
        # Ensure log directory exists
        log_dir = Path(".claude/state/logs")
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Write to activity log
        with open(log_dir / "activity.jsonl", "a") as f:
            f.write(json.dumps(log_entry) + "\\n")
        
        # Update session stats
        update_session_stats(tool_name)
        
        return {"continue": True, "logged": True}
        
    except Exception as e:
        # Don't interfere with normal operation
        return {"continue": True, "error": str(e)}

def update_session_stats(tool_name):
    """Update session statistics."""
    try:
        stats_file = Path(".claude/state/session-stats.json")
        
        # Load existing stats
        if stats_file.exists():
            stats = json.loads(stats_file.read_text())
        else:
            stats = {
                'session_start': datetime.now().isoformat(),
                'tool_usage': {},
                'files_modified': 0,
                'commands_run': 0
            }
        
        # Update stats
        stats['last_activity'] = datetime.now().isoformat()
        stats['tool_usage'][tool_name] = stats['tool_usage'].get(tool_name, 0) + 1
        
        if tool_name == 'Bash':
            stats['commands_run'] += 1
        elif tool_name in ['Edit', 'MultiEdit', 'Write']:
            stats['files_modified'] += 1
        
        # Save updated stats
        stats_file.write_text(json.dumps(stats, indent=2))
        
    except Exception:
        # Ignore stats errors
        pass

def main():
    """Main hook entry point."""
    result = log_activity()
    print(json.dumps(result))
    sys.exit(0)

if __name__ == "__main__":
    main()