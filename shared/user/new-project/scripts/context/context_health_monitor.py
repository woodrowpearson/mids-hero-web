#!/usr/bin/env python3
"""Context Health Monitor - Check Claude context health and token usage."""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

import tiktoken


class ContextHealthMonitor:
    """Monitor context health and token usage for Claude Code."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.claude_dir = project_root / ".claude"
        self.max_tokens = int(os.getenv("AI_MAX_CONTEXT_TOKENS", "50000"))
        self.alert_threshold = int(os.getenv("AI_ALERT_THRESHOLD", "90000"))
        self.encoding = tiktoken.get_encoding("cl100k_base")
        
    def count_tokens(self, text: str) -> int:
        """Count tokens in text using tiktoken."""
        return len(self.encoding.encode(text))
    
    def analyze_file(self, file_path: Path) -> Tuple[str, int]:
        """Analyze a single file for token count."""
        try:
            content = file_path.read_text(encoding="utf-8")
            tokens = self.count_tokens(content)
            return str(file_path.relative_to(self.project_root)), tokens
        except Exception as e:
            return str(file_path), 0
    
    def scan_context_files(self) -> Dict[str, int]:
        """Scan all context files and count tokens."""
        context_files = {}
        
        # Key files to check
        key_files = [
            self.project_root / "CLAUDE.md",
            self.claude_dir / "CLAUDE.md",
        ]
        
        # Add all markdown files in .claude
        if self.claude_dir.exists():
            for md_file in self.claude_dir.rglob("*.md"):
                key_files.append(md_file)
        
        # Analyze each file
        for file_path in key_files:
            if file_path.exists():
                rel_path, tokens = self.analyze_file(file_path)
                context_files[rel_path] = tokens
                
        return context_files
    
    def generate_report(self) -> Dict:
        """Generate health report."""
        context_files = self.scan_context_files()
        total_tokens = sum(context_files.values())
        
        # Determine health status
        if total_tokens > self.alert_threshold:
            status = "CRITICAL"
        elif total_tokens > self.max_tokens:
            status = "WARNING"
        else:
            status = "HEALTHY"
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "status": status,
            "total_tokens": total_tokens,
            "max_tokens": self.max_tokens,
            "alert_threshold": self.alert_threshold,
            "utilization": f"{(total_tokens / self.max_tokens * 100):.1f}%",
            "files": context_files,
            "largest_files": sorted(
                context_files.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:5]
        }
        
        return report
    
    def print_report(self, report: Dict):
        """Print formatted health report."""
        status_colors = {
            "HEALTHY": "\033[32m",  # Green
            "WARNING": "\033[33m",  # Yellow
            "CRITICAL": "\033[31m"  # Red
        }
        
        color = status_colors.get(report["status"], "")
        reset = "\033[0m"
        
        print(f"\n{color}Context Health: {report['status']}{reset}")
        print(f"Total Tokens: {report['total_tokens']:,} / {report['max_tokens']:,}")
        print(f"Utilization: {report['utilization']}")
        
        if report["total_tokens"] > self.max_tokens:
            print(f"\n⚠️  Context exceeds recommended limit!")
            print("Largest files:")
            for file, tokens in report["largest_files"]:
                print(f"  - {file}: {tokens:,} tokens")
            print("\nRecommendation: Run 'just context-prune' to optimize")
    
    def save_report(self, report: Dict):
        """Save report to file."""
        reports_dir = self.project_root / "reports" / "context"
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        report_file = reports_dir / "health.json"
        report_file.write_text(json.dumps(report, indent=2))


def main():
    """Main entry point."""
    project_root = Path.cwd()
    monitor = ContextHealthMonitor(project_root)
    
    report = monitor.generate_report()
    monitor.print_report(report)
    monitor.save_report(report)
    
    # Exit with error if critical
    if report["status"] == "CRITICAL":
        sys.exit(1)


if __name__ == "__main__":
    main()