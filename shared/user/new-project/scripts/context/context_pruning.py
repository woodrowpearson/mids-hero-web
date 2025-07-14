#!/usr/bin/env python3
"""Context pruning service to keep token usage optimal."""

import json
import os
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

import tiktoken


class ContextPruner:
    """Prune oversized context files for Claude Code."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.claude_dir = project_root / ".claude"
        self.backup_dir = project_root / ".claude" / "backups"
        self.max_file_tokens = 10000  # Max tokens per file
        self.encoding = tiktoken.get_encoding("cl100k_base")
        
    def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        return len(self.encoding.encode(text))
    
    def backup_file(self, file_path: Path) -> Path:
        """Create backup of file before pruning."""
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
        backup_path = self.backup_dir / backup_name
        shutil.copy2(file_path, backup_path)
        return backup_path
    
    def split_markdown_sections(self, content: str) -> List[Tuple[str, str]]:
        """Split markdown content into sections."""
        sections = []
        current_section = []
        current_header = "Introduction"
        
        for line in content.splitlines():
            if line.startswith("# "):
                if current_section:
                    sections.append((current_header, "\n".join(current_section)))
                current_header = line[2:].strip()
                current_section = [line]
            else:
                current_section.append(line)
        
        if current_section:
            sections.append((current_header, "\n".join(current_section)))
            
        return sections
    
    def prune_file(self, file_path: Path, auto: bool = False) -> Dict:
        """Prune a single file if oversized."""
        result = {
            "file": str(file_path.relative_to(self.project_root)),
            "status": "unchanged",
            "original_tokens": 0,
            "final_tokens": 0
        }
        
        try:
            content = file_path.read_text(encoding="utf-8")
            tokens = self.count_tokens(content)
            result["original_tokens"] = tokens
            
            if tokens <= self.max_file_tokens:
                result["final_tokens"] = tokens
                return result
            
            if not auto:
                print(f"\n⚠️  {file_path.name} has {tokens:,} tokens")
                response = input("Prune this file? [y/N]: ").lower()
                if response != 'y':
                    result["status"] = "skipped"
                    result["final_tokens"] = tokens
                    return result
            
            # Backup before pruning
            backup_path = self.backup_file(file_path)
            result["backup"] = str(backup_path.relative_to(self.project_root))
            
            # Split into sections
            sections = self.split_markdown_sections(content)
            
            # Keep essential sections, move others to separate files
            essential_content = []
            moved_sections = []
            
            for header, section_content in sections:
                section_tokens = self.count_tokens(section_content)
                
                # Keep small sections in main file
                if section_tokens < 2000 or header in ["Introduction", "Quick Start", "Critical Rules"]:
                    essential_content.append(section_content)
                else:
                    # Move to separate file
                    section_file = file_path.parent / f"{file_path.stem}-{header.lower().replace(' ', '-')}.md"
                    section_file.write_text(section_content)
                    moved_sections.append(header)
                    
                    # Add reference in main file
                    ref_line = f"\n## {header}\n\nSee [{header}]({section_file.name})\n"
                    essential_content.append(ref_line)
            
            # Write pruned content
            new_content = "\n\n".join(essential_content)
            file_path.write_text(new_content)
            
            result["final_tokens"] = self.count_tokens(new_content)
            result["status"] = "pruned"
            result["moved_sections"] = moved_sections
            
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            
        return result
    
    def scan_and_prune(self, auto: bool = False) -> Dict:
        """Scan all context files and prune if needed."""
        results = {
            "timestamp": datetime.now().isoformat(),
            "files_processed": 0,
            "files_pruned": 0,
            "tokens_saved": 0,
            "details": []
        }
        
        # Files to check
        check_patterns = ["*.md", "*.txt", "*.py"]
        
        for pattern in check_patterns:
            for file_path in self.claude_dir.rglob(pattern):
                if "backup" in file_path.parts:
                    continue
                    
                result = self.prune_file(file_path, auto)
                results["files_processed"] += 1
                results["details"].append(result)
                
                if result["status"] == "pruned":
                    results["files_pruned"] += 1
                    tokens_saved = result["original_tokens"] - result["final_tokens"]
                    results["tokens_saved"] += tokens_saved
        
        return results
    
    def print_summary(self, results: Dict):
        """Print pruning summary."""
        print("\n✂️  Context Pruning Summary")
        print("=" * 40)
        print(f"Files processed: {results['files_processed']}")
        print(f"Files pruned: {results['files_pruned']}")
        print(f"Tokens saved: {results['tokens_saved']:,}")
        
        if results["files_pruned"] > 0:
            print("\nPruned files:")
            for detail in results["details"]:
                if detail["status"] == "pruned":
                    print(f"  - {detail['file']}: {detail['original_tokens']:,} → {detail['final_tokens']:,} tokens")
                    if "moved_sections" in detail:
                        print(f"    Moved sections: {', '.join(detail['moved_sections'])}")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Prune oversized context files")
    parser.add_argument("--auto", "-a", action="store_true", help="Auto-prune without prompting")
    args = parser.parse_args()
    
    project_root = Path.cwd()
    pruner = ContextPruner(project_root)
    
    results = pruner.scan_and_prune(auto=args.auto)
    pruner.print_summary(results)
    
    # Save report
    reports_dir = project_root / "reports" / "context"
    reports_dir.mkdir(parents=True, exist_ok=True)
    report_file = reports_dir / "pruning_report.json"
    report_file.write_text(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()