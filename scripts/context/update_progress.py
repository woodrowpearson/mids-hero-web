#!/usr/bin/env python3
"""
Update progress tracking for roadmap epics.
"""

import json
from pathlib import Path
from datetime import datetime

def load_progress():
    """Load current progress from file."""
    progress_file = Path(".claude/progress.json")
    if progress_file.exists():
        return json.loads(progress_file.read_text())
    return {
        "epics": {
            "1": {"status": "complete", "percentage": 100},
            "2": {"status": "blocked", "percentage": 20},
            "3": {"status": "planned", "percentage": 0},
            "4": {"status": "planned", "percentage": 0},
            "5": {"status": "planned", "percentage": 0},
            "6": {"status": "future", "percentage": 0}
        },
        "last_updated": None
    }

def save_progress(progress):
    """Save progress to file."""
    progress_file = Path(".claude/progress.json")
    progress_file.parent.mkdir(exist_ok=True)
    progress["last_updated"] = datetime.now().isoformat()
    progress_file.write_text(json.dumps(progress, indent=2))

def update_epic_status():
    """Interactive update of epic status."""
    progress = load_progress()
    
    print("📊 Epic Progress Update")
    print("=" * 60)
    
    epic_names = {
        "1": "Project Setup and Planning",
        "2": "Data Model & Database Integration", 
        "3": "Backend API Development",
        "4": "Frontend Application Implementation",
        "5": "Deployment and DevOps",
        "6": "Optimization and Feature Enhancements"
    }
    
    # Show current status
    print("\nCurrent Status:")
    for epic_id, epic_name in epic_names.items():
        epic = progress["epics"][epic_id]
        status_emoji = {
            "complete": "✅",
            "in_progress": "🚧",
            "blocked": "🚫",
            "planned": "📋",
            "future": "🔮"
        }.get(epic["status"], "❓")
        print(f"{status_emoji} Epic {epic_id}: {epic_name}")
        print(f"   Status: {epic['status']} | Progress: {epic['percentage']}%")
    
    # Update prompt
    print("\nEnter epic number to update (1-6) or 'q' to quit:")
    
    while True:
        choice = input("> ").strip()
        
        if choice.lower() == 'q':
            break
            
        if choice in epic_names:
            print(f"\nUpdating Epic {choice}: {epic_names[choice]}")
            
            # Status update
            print("Select new status:")
            print("1. complete")
            print("2. in_progress") 
            print("3. blocked")
            print("4. planned")
            print("5. future")
            
            status_choice = input("Status (1-5): ").strip()
            status_map = {
                "1": "complete",
                "2": "in_progress",
                "3": "blocked",
                "4": "planned",
                "5": "future"
            }
            
            if status_choice in status_map:
                progress["epics"][choice]["status"] = status_map[status_choice]
                
                # Percentage update
                percentage = input("Progress percentage (0-100): ").strip()
                try:
                    percentage = int(percentage)
                    if 0 <= percentage <= 100:
                        progress["epics"][choice]["percentage"] = percentage
                except ValueError:
                    print("Invalid percentage, keeping current value")
                
                print(f"✅ Epic {choice} updated!")
        
        print("\nEnter epic number to update (1-6) or 'q' to quit:")
    
    # Save progress
    save_progress(progress)
    print("\n✅ Progress saved!")
    
    # Generate summary
    generate_summary(progress)

def generate_summary(progress):
    """Generate a summary for CLAUDE.md."""
    print("\n📋 Summary for CLAUDE.md:")
    print("-" * 60)
    
    for epic_id in ["1", "2", "3", "4", "5", "6"]:
        epic = progress["epics"][epic_id]
        status_emoji = {
            "complete": "✅",
            "in_progress": "🚧", 
            "blocked": "🚫",
            "planned": "📋",
            "future": "🔮"
        }.get(epic["status"], "❓")
        
        epic_names = {
            "1": "Project Setup",
            "2": "Data Import",
            "3": "Backend API",
            "4": "Frontend",
            "5": "Deployment",
            "6": "Optimization"
        }
        
        status_text = epic["status"].replace("_", " ").title()
        if epic["status"] == "blocked":
            status_text += " (CRITICAL BLOCKER)"
        elif epic["status"] == "in_progress":
            status_text += f" ({epic['percentage']}%)"
            
        print(f"**{status_emoji} Epic {epic_id}: {epic_names[epic_id]}** - {status_text}")

if __name__ == "__main__":
    update_epic_status()