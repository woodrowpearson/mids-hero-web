#!/usr/bin/env python3
"""Measure context complexity and provide optimization suggestions."""

import json
import os
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

import tiktoken


class ContextComplexityAnalyzer:
    """Analyze context complexity for Claude Code optimization."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.encoding = tiktoken.get_encoding("cl100k_base")
        self.file_stats = defaultdict(dict)
        
    def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        return len(self.encoding.encode(text))
    
    def analyze_directory(self, directory: Path) -> Dict:
        """Analyze all files in a directory."""
        stats = {
            "total_files": 0,
            "total_tokens": 0,
            "by_extension": defaultdict(lambda: {"count": 0, "tokens": 0}),
            "large_files": []
        }
        
        for file_path in directory.rglob("*"):
            if file_path.is_file() and not any(part.startswith('.') for part in file_path.parts):
                try:
                    content = file_path.read_text(encoding="utf-8")
                    tokens = self.count_tokens(content)
                    
                    stats["total_files"] += 1
                    stats["total_tokens"] += tokens
                    
                    ext = file_path.suffix or "no_extension"
                    stats["by_extension"][ext]["count"] += 1
                    stats["by_extension"][ext]["tokens"] += tokens
                    
                    if tokens > 5000:  # Flag large files
                        stats["large_files"].append({
                            "path": str(file_path.relative_to(self.project_root)),
                            "tokens": tokens
                        })
                except:
                    continue
                    
        return stats
    
    def analyze_project(self) -> Dict:
        """Analyze the entire project."""
        analysis = {
            "project_root": str(self.project_root),
            "claude_context": {},
            "source_code": {},
            "recommendations": []
        }
        
        # Analyze .claude directory
        claude_dir = self.project_root / ".claude"
        if claude_dir.exists():
            analysis["claude_context"] = self.analyze_directory(claude_dir)
            
        # Analyze source code
        src_dirs = ["src", "app", "lib"]
        for dir_name in src_dirs:
            src_dir = self.project_root / dir_name
            if src_dir.exists():
                analysis["source_code"] = self.analyze_directory(src_dir)
                break
        
        # Generate recommendations
        analysis["recommendations"] = self.generate_recommendations(analysis)
        
        return analysis
    
    def generate_recommendations(self, analysis: Dict) -> List[str]:
        """Generate optimization recommendations."""
        recommendations = []
        
        # Check Claude context size
        claude_tokens = analysis["claude_context"].get("total_tokens", 0)
        if claude_tokens > 50000:
            recommendations.append(
                f"Claude context is large ({claude_tokens:,} tokens). "
                "Consider splitting CLAUDE.md into modular files."
            )
        
        # Check for large files
        all_large_files = []
        if "large_files" in analysis["claude_context"]:
            all_large_files.extend(analysis["claude_context"]["large_files"])
        if "large_files" in analysis["source_code"]:
            all_large_files.extend(analysis["source_code"]["large_files"])
            
        if all_large_files:
            recommendations.append(
                f"Found {len(all_large_files)} files over 5,000 tokens. "
                "Consider refactoring or excluding from context."
            )
        
        # Check file type distribution
        if analysis["source_code"]:
            by_ext = analysis["source_code"]["by_extension"]
            high_token_types = [
                (ext, data) for ext, data in by_ext.items() 
                if data["tokens"] > 20000
            ]
            if high_token_types:
                recommendations.append(
                    "Some file types consume significant tokens. "
                    "Consider using .claudeignore for generated files."
                )
        
        return recommendations
    
    def print_summary(self, analysis: Dict, detailed: bool = False):
        """Print analysis summary."""
        print("\n📊 Context Complexity Analysis")
        print("=" * 50)
        
        # Claude context summary
        if analysis["claude_context"]:
            claude = analysis["claude_context"]
            print(f"\n📁 Claude Context (.claude/)")
            print(f"  Files: {claude['total_files']}")
            print(f"  Tokens: {claude['total_tokens']:,}")
            
            if detailed and claude["large_files"]:
                print("\n  Large files:")
                for file in claude["large_files"][:5]:
                    print(f"    - {file['path']}: {file['tokens']:,} tokens")
        
        # Source code summary
        if analysis["source_code"]:
            src = analysis["source_code"]
            print(f"\n📁 Source Code")
            print(f"  Files: {src['total_files']}")
            print(f"  Tokens: {src['total_tokens']:,}")
        
        # Recommendations
        if analysis["recommendations"]:
            print("\n💡 Recommendations:")
            for i, rec in enumerate(analysis["recommendations"], 1):
                print(f"  {i}. {rec}")
    
    def save_report(self, analysis: Dict):
        """Save detailed report."""
        reports_dir = self.project_root / "reports" / "context"
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        report_file = reports_dir / "complexity_analysis.json"
        report_file.write_text(json.dumps(analysis, indent=2, default=str))


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Analyze context complexity")
    parser.add_argument("--detailed", "-d", action="store_true", help="Show detailed output")
    parser.add_argument("--summary", "-s", action="store_true", help="Summary only")
    args = parser.parse_args()
    
    project_root = Path.cwd()
    analyzer = ContextComplexityAnalyzer(project_root)
    
    analysis = analyzer.analyze_project()
    
    if not args.summary:
        analyzer.save_report(analysis)
    
    analyzer.print_summary(analysis, detailed=args.detailed)


if __name__ == "__main__":
    main()