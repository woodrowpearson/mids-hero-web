#!/usr/bin/env python3
"""Analyze and monitor token usage for Claude Code sessions."""

import json
import os
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import tiktoken


class TokenUsageAnalyzer:
    """Analyze token usage patterns for optimization."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.claude_dir = project_root / ".claude"
        self.memory_dir = self.claude_dir / "shared" / "memory"
        self.encoding = tiktoken.get_encoding("cl100k_base")
        self.usage_file = self.memory_dir / "token_usage.json"
        self.session_data = self.load_session_data()
        
    def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        return len(self.encoding.encode(text))
    
    def load_session_data(self) -> Dict:
        """Load existing session data."""
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        
        if self.usage_file.exists():
            try:
                return json.loads(self.usage_file.read_text())
            except:
                pass
                
        return {
            "sessions": [],
            "total_tokens": 0,
            "session_count": 0
        }
    
    def save_session_data(self):
        """Save session data."""
        self.usage_file.write_text(json.dumps(self.session_data, indent=2))
    
    def start_session(self) -> str:
        """Start a new session."""
        session_id = datetime.now().strftime("session_%Y%m%d_%H%M%S")
        session = {
            "id": session_id,
            "start_time": datetime.now().isoformat(),
            "files_accessed": [],
            "token_snapshots": [],
            "total_tokens": 0
        }
        self.session_data["sessions"].append(session)
        self.session_data["session_count"] += 1
        return session_id
    
    def record_file_access(self, session_id: str, file_path: Path, tokens: int):
        """Record file access in session."""
        for session in self.session_data["sessions"]:
            if session["id"] == session_id:
                session["files_accessed"].append({
                    "file": str(file_path.relative_to(self.project_root)),
                    "tokens": tokens,
                    "timestamp": datetime.now().isoformat()
                })
                session["total_tokens"] += tokens
                self.session_data["total_tokens"] += tokens
                break
    
    def take_snapshot(self, session_id: str) -> Dict:
        """Take a snapshot of current token usage."""
        snapshot = {
            "timestamp": datetime.now().isoformat(),
            "context_files": {},
            "total_tokens": 0
        }
        
        # Analyze all context files
        for pattern in ["*.md", "*.py", "*.txt"]:
            for file_path in self.claude_dir.rglob(pattern):
                if file_path.is_file() and "backup" not in file_path.parts:
                    try:
                        content = file_path.read_text(encoding="utf-8")
                        tokens = self.count_tokens(content)
                        rel_path = str(file_path.relative_to(self.project_root))
                        snapshot["context_files"][rel_path] = tokens
                        snapshot["total_tokens"] += tokens
                    except:
                        continue
        
        # Add to session
        for session in self.session_data["sessions"]:
            if session["id"] == session_id:
                session["token_snapshots"].append(snapshot)
                break
                
        return snapshot
    
    def analyze_growth(self) -> Dict:
        """Analyze token growth patterns."""
        if not self.session_data["sessions"]:
            return {"status": "no_data"}
            
        analysis = {
            "total_sessions": self.session_data["session_count"],
            "total_tokens_used": self.session_data["total_tokens"],
            "average_tokens_per_session": 0,
            "growth_pattern": [],
            "hotspot_files": defaultdict(int)
        }
        
        # Calculate averages
        if analysis["total_sessions"] > 0:
            analysis["average_tokens_per_session"] = (
                analysis["total_tokens_used"] // analysis["total_sessions"]
            )
        
        # Find hotspot files
        for session in self.session_data["sessions"]:
            for file_access in session.get("files_accessed", []):
                analysis["hotspot_files"][file_access["file"]] += file_access["tokens"]
        
        # Sort hotspots
        analysis["hotspot_files"] = dict(
            sorted(analysis["hotspot_files"].items(), 
                   key=lambda x: x[1], 
                   reverse=True)[:10]
        )
        
        return analysis
    
    def monitor_live(self, session_id: str, interval: int = 30):
        """Monitor token usage live."""
        print(f"📊 Monitoring token usage (interval: {interval}s)")
        print("Press Ctrl+C to stop\n")
        
        try:
            while True:
                snapshot = self.take_snapshot(session_id)
                self.save_session_data()
                
                # Display current status
                os.system('clear' if os.name == 'posix' else 'cls')
                print(f"🔤 Token Usage Monitor - {datetime.now().strftime('%H:%M:%S')}")
                print("=" * 50)
                print(f"Total Context Tokens: {snapshot['total_tokens']:,}")
                
                # Alert levels
                if snapshot['total_tokens'] > 90000:
                    print("⚠️  CRITICAL: Approaching token limit!")
                elif snapshot['total_tokens'] > 50000:
                    print("⚠️  WARNING: High token usage")
                else:
                    print("✅ Token usage is healthy")
                
                # Top files
                print("\nTop 5 Files by Token Count:")
                top_files = sorted(
                    snapshot['context_files'].items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:5]
                
                for file, tokens in top_files:
                    print(f"  {file}: {tokens:,} tokens")
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n\n✅ Monitoring stopped")
            self.save_session_data()
    
    def print_analysis(self, analysis: Dict):
        """Print usage analysis."""
        print("\n📊 Token Usage Analysis")
        print("=" * 40)
        
        if analysis.get("status") == "no_data":
            print("No usage data available yet.")
            return
            
        print(f"Total Sessions: {analysis['total_sessions']}")
        print(f"Total Tokens Used: {analysis['total_tokens_used']:,}")
        print(f"Average per Session: {analysis['average_tokens_per_session']:,}")
        
        if analysis["hotspot_files"]:
            print("\n🔥 Hotspot Files (most accessed):")
            for file, tokens in list(analysis["hotspot_files"].items())[:5]:
                print(f"  {file}: {tokens:,} total tokens")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Analyze token usage")
    parser.add_argument("--watch", "-w", action="store_true", help="Monitor live")
    parser.add_argument("--interval", "-i", type=int, default=30, help="Monitor interval (seconds)")
    parser.add_argument("--analyze", "-a", action="store_true", help="Analyze usage patterns")
    args = parser.parse_args()
    
    project_root = Path.cwd()
    analyzer = TokenUsageAnalyzer(project_root)
    
    if args.analyze:
        analysis = analyzer.analyze_growth()
        analyzer.print_analysis(analysis)
    elif args.watch:
        session_id = analyzer.start_session()
        analyzer.monitor_live(session_id, args.interval)
    else:
        # Take single snapshot
        session_id = analyzer.start_session()
        snapshot = analyzer.take_snapshot(session_id)
        analyzer.save_session_data()
        
        print(f"Current token usage: {snapshot['total_tokens']:,}")
        if snapshot['total_tokens'] > 50000:
            print("⚠️  Consider running 'just context-prune' to optimize")


if __name__ == "__main__":
    main()