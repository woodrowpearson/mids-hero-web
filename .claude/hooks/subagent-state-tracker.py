#!/usr/bin/env python3
"""
Claude Code hook for tracking sub-agent work and state
Automatically saves agent state, logs, and summaries when sub-agents perform work
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime
import hashlib

def get_agent_type(input_data):
    """Extract agent type from Task tool input."""
    tool_input = input_data.get('tool_input', {})
    subagent_type = tool_input.get('subagent_type', 'unknown')
    return subagent_type

def save_agent_state(agent_type, input_data):
    """Save current agent state to agents directory."""
    state_dir = Path(".claude/state/agents")
    state_dir.mkdir(parents=True, exist_ok=True)
    
    # Create state entry
    state_entry = {
        'timestamp': datetime.now().isoformat(),
        'agent_type': agent_type,
        'task_description': input_data.get('tool_input', {}).get('description', ''),
        'prompt_preview': input_data.get('tool_input', {}).get('prompt', '')[:200] + '...',
        'session_id': input_data.get('session_id', 'unknown'),
        'task_id': hashlib.md5(
            f"{datetime.now().isoformat()}-{agent_type}".encode()
        ).hexdigest()[:8]
    }
    
    # Save to agent-specific state file
    agent_state_file = state_dir / f"{agent_type}-state.json"
    
    # Load existing state or create new
    if agent_state_file.exists():
        states = json.loads(agent_state_file.read_text())
    else:
        states = {
            'agent_type': agent_type,
            'first_use': datetime.now().isoformat(),
            'tasks': []
        }
    
    # Add new task
    states['last_use'] = datetime.now().isoformat()
    states['total_tasks'] = states.get('total_tasks', 0) + 1
    states['tasks'].append(state_entry)
    
    # Keep only last 100 tasks per agent
    if len(states['tasks']) > 100:
        states['tasks'] = states['tasks'][-100:]
    
    # Save updated state
    agent_state_file.write_text(json.dumps(states, indent=2))
    
    return state_entry['task_id']

def save_agent_log(agent_type, task_id, input_data):
    """Save detailed log entry for agent work."""
    log_dir = Path(".claude/state/logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Create detailed log entry
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'task_id': task_id,
        'agent_type': agent_type,
        'tool': 'Task',
        'session_id': input_data.get('session_id', 'unknown'),
        'task_details': {
            'description': input_data.get('tool_input', {}).get('description', ''),
            'prompt_length': len(input_data.get('tool_input', {}).get('prompt', '')),
            'subagent_type': agent_type
        }
    }
    
    # Append to agent activity log
    with open(log_dir / "agent-activity.jsonl", "a") as f:
        f.write(json.dumps(log_entry) + "\\n")
    
    # Also append to general activity log
    with open(log_dir / "activity.jsonl", "a") as f:
        f.write(json.dumps(log_entry) + "\\n")

def save_agent_summary(agent_type, task_id):
    """Create summary entry for agent work."""
    summary_dir = Path(".claude/state/summaries")
    summary_dir.mkdir(parents=True, exist_ok=True)
    
    # Create daily summary file
    today = datetime.now().strftime("%Y-%m-%d")
    summary_file = summary_dir / f"agent-activity-{today}.json"
    
    # Load or create summary
    if summary_file.exists():
        summary = json.loads(summary_file.read_text())
    else:
        summary = {
            'date': today,
            'agents': {},
            'total_tasks': 0,
            'created': datetime.now().isoformat()
        }
    
    # Update summary
    if agent_type not in summary['agents']:
        summary['agents'][agent_type] = {
            'count': 0,
            'first_use': datetime.now().isoformat(),
            'task_ids': []
        }
    
    summary['agents'][agent_type]['count'] += 1
    summary['agents'][agent_type]['last_use'] = datetime.now().isoformat()
    summary['agents'][agent_type]['task_ids'].append(task_id)
    summary['total_tasks'] += 1
    summary['last_updated'] = datetime.now().isoformat()
    
    # Save updated summary
    summary_file.write_text(json.dumps(summary, indent=2))

def update_global_stats(agent_type):
    """Update global agent usage statistics."""
    stats_file = Path(".claude/state/agent-stats.json")
    
    # Load or create stats
    if stats_file.exists():
        stats = json.loads(stats_file.read_text())
    else:
        stats = {
            'created': datetime.now().isoformat(),
            'total_invocations': 0,
            'agents': {}
        }
    
    # Update stats
    stats['total_invocations'] += 1
    stats['last_invocation'] = datetime.now().isoformat()
    
    if agent_type not in stats['agents']:
        stats['agents'][agent_type] = {
            'count': 0,
            'first_use': datetime.now().isoformat()
        }
    
    stats['agents'][agent_type]['count'] += 1
    stats['agents'][agent_type]['last_use'] = datetime.now().isoformat()
    
    # Save updated stats
    stats_file.write_text(json.dumps(stats, indent=2))

def main():
    """Main hook entry point."""
    try:
        # Read input from Claude Code
        input_data = json.load(sys.stdin)
        
        # Only process Task tool calls
        tool_name = input_data.get('tool_name', '')
        if tool_name != 'Task':
            return {"continue": True}
        
        # Get agent type
        agent_type = get_agent_type(input_data)
        
        # Skip if not a recognized agent
        valid_agents = [
            'general-purpose', 'documentation-specialist', 'backend-specialist',
            'calculation-specialist', 'frontend-specialist', 'database-specialist',
            'testing-specialist', 'import-specialist', 'devops-specialist'
        ]
        
        if agent_type not in valid_agents:
            return {"continue": True}
        
        # Save state in all three locations
        task_id = save_agent_state(agent_type, input_data)
        save_agent_log(agent_type, task_id, input_data)
        save_agent_summary(agent_type, task_id)
        update_global_stats(agent_type)
        
        # Log success
        print(json.dumps({
            "continue": True,
            "tracked": True,
            "agent_type": agent_type,
            "task_id": task_id
        }))
        
    except Exception as e:
        # Don't interfere with normal operation
        print(json.dumps({
            "continue": True,
            "error": str(e)
        }))

if __name__ == "__main__":
    main()