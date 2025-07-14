#!/usr/bin/env python3
"""Update progress for multi-agent coordination and long-running tasks."""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional


class ProgressTracker:
    """Track progress across Claude Code sessions."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.memory_dir = project_root / ".claude" / "shared" / "memory"
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.progress_file = self.memory_dir / "progress.json"
        self.progress = self.load_progress()
        
    def load_progress(self) -> Dict:
        """Load existing progress or create new."""
        if self.progress_file.exists():
            try:
                return json.loads(self.progress_file.read_text())
            except:
                pass
        
        return {
            "tasks": {},
            "session_started": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }
    
    def save_progress(self):
        """Save progress to file."""
        self.progress["last_updated"] = datetime.now().isoformat()
        self.progress_file.write_text(json.dumps(self.progress, indent=2))
    
    def update_task(self, task_id: str, status: str, notes: Optional[str] = None):
        """Update a specific task."""
        if task_id not in self.progress["tasks"]:
            self.progress["tasks"][task_id] = {
                "created": datetime.now().isoformat(),
                "status": "pending",
                "updates": []
            }
        
        task = self.progress["tasks"][task_id]
        task["status"] = status
        task["last_updated"] = datetime.now().isoformat()
        
        update_entry = {
            "timestamp": datetime.now().isoformat(),
            "status": status
        }
        
        if notes:
            update_entry["notes"] = notes
            
        task["updates"].append(update_entry)
        
        self.save_progress()
    
    def list_tasks(self, status_filter: Optional[str] = None) -> Dict:
        """List all tasks with optional status filter."""
        tasks = self.progress["tasks"]
        
        if status_filter:
            return {
                task_id: task for task_id, task in tasks.items()
                if task["status"] == status_filter
            }
        
        return tasks
    
    def get_summary(self) -> Dict:
        """Get progress summary."""
        tasks = self.progress["tasks"]
        
        summary = {
            "total_tasks": len(tasks),
            "by_status": {},
            "session_duration": self.calculate_duration(),
            "last_updated": self.progress["last_updated"]
        }
        
        # Count by status
        for task in tasks.values():
            status = task["status"]
            summary["by_status"][status] = summary["by_status"].get(status, 0) + 1
            
        return summary
    
    def calculate_duration(self) -> str:
        """Calculate session duration."""
        start = datetime.fromisoformat(self.progress["session_started"])
        duration = datetime.now() - start
        
        hours = int(duration.total_seconds() // 3600)
        minutes = int((duration.total_seconds() % 3600) // 60)
        
        return f"{hours}h {minutes}m"
    
    def print_status(self):
        """Print current status."""
        summary = self.get_summary()
        
        print("\n📊 Progress Status")
        print("=" * 40)
        print(f"Session Duration: {summary['session_duration']}")
        print(f"Total Tasks: {summary['total_tasks']}")
        
        if summary["by_status"]:
            print("\nBy Status:")
            for status, count in summary["by_status"].items():
                emoji = {
                    "completed": "✅",
                    "in_progress": "🔄",
                    "pending": "⏳",
                    "blocked": "🚫"
                }.get(status, "❓")
                print(f"  {emoji} {status}: {count}")
        
        # Show active tasks
        active_tasks = self.list_tasks("in_progress")
        if active_tasks:
            print("\nActive Tasks:")
            for task_id, task in active_tasks.items():
                print(f"  - {task_id}")
                if task["updates"]:
                    last_note = next(
                        (u["notes"] for u in reversed(task["updates"]) if "notes" in u),
                        None
                    )
                    if last_note:
                        print(f"    {last_note}")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Update task progress")
    parser.add_argument("--task", "-t", help="Task ID to update")
    parser.add_argument("--status", "-s", help="New status (completed, in_progress, pending, blocked)")
    parser.add_argument("--notes", "-n", help="Optional notes")
    parser.add_argument("--list", "-l", action="store_true", help="List all tasks")
    parser.add_argument("--filter", "-f", help="Filter tasks by status")
    parser.add_argument("--resume", "-r", action="store_true", help="Show current status")
    
    args = parser.parse_args()
    
    project_root = Path.cwd()
    tracker = ProgressTracker(project_root)
    
    if args.list:
        tasks = tracker.list_tasks(args.filter)
        print(f"\n📋 Tasks ({len(tasks)} total):")
        for task_id, task in tasks.items():
            print(f"  [{task['status']}] {task_id}")
    elif args.task and args.status:
        tracker.update_task(args.task, args.status, args.notes)
        print(f"✅ Updated task '{args.task}' to status '{args.status}'")
        tracker.print_status()
    else:
        tracker.print_status()


if __name__ == "__main__":
    main()