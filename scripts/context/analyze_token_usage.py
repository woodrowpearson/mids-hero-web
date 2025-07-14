#!/usr/bin/env python3
"""
Analyze token usage in project documentation.
"""

import os
from pathlib import Path
import tiktoken

# Initialize tokenizer (using GPT-4 tokenizer as approximation)
encoding = tiktoken.get_encoding("cl100k_base")

def count_tokens(text: str) -> int:
    """Count tokens in text."""
    return len(encoding.encode(text))

def analyze_file(file_path: Path) -> dict:
    """Analyze token usage in a single file."""
    try:
        content = file_path.read_text()
        tokens = count_tokens(content)
        return {
            "path": str(file_path),
            "tokens": tokens,
            "size_kb": file_path.stat().st_size / 1024
        }
    except Exception as e:
        return {
            "path": str(file_path),
            "error": str(e)
        }

def analyze_directory(directory: Path, extensions: list) -> list:
    """Analyze all files in directory with given extensions."""
    results = []
    for ext in extensions:
        for file_path in directory.rglob(f"*{ext}"):
            if not any(skip in str(file_path) for skip in ["node_modules", ".git", "__pycache__"]):
                results.append(analyze_file(file_path))
    return results

def main():
    """Main analysis function."""
    project_root = Path.cwd()
    
    # Analyze different file types
    doc_files = analyze_directory(project_root, [".md", ".txt"])
    claude_files = analyze_directory(project_root / ".claude", [".md", ".txt", ".json"])
    
    # Sort by token count
    all_files = [f for f in doc_files + claude_files if "error" not in f]
    all_files.sort(key=lambda x: x["tokens"], reverse=True)
    
    # Calculate totals
    total_tokens = sum(f["tokens"] for f in all_files)
    
    # Print results
    print("🔍 Token Usage Analysis")
    print("=" * 60)
    print(f"Total tokens in documentation: {total_tokens:,}")
    print(f"Context limit warning at: 90,000 tokens")
    print(f"Context limit maximum at: 128,000 tokens")
    print(f"Current usage: {(total_tokens / 128000) * 100:.1f}% of maximum")
    print()
    
    # Warnings
    if total_tokens > 90000:
        print("⚠️  WARNING: Approaching token limit!")
        print("   Consider pruning large files or using modular contexts")
        print()
    
    # Top 10 largest files
    print("📊 Top 10 Largest Files by Token Count:")
    print("-" * 60)
    for i, file in enumerate(all_files[:10], 1):
        percentage = (file["tokens"] / total_tokens) * 100
        print(f"{i:2d}. {file['path']:<40} {file['tokens']:>8,} tokens ({percentage:>4.1f}%)")
    
    # Claude-specific files
    print()
    print("📁 .claude/ Directory Analysis:")
    print("-" * 60)
    claude_tokens = sum(f["tokens"] for f in claude_files if "error" not in f)
    print(f"Total tokens in .claude/: {claude_tokens:,}")
    print(f"Percentage of total: {(claude_tokens / total_tokens) * 100:.1f}%")
    
    # Recommendations
    print()
    print("💡 Recommendations:")
    if total_tokens > 50000:
        print("- Consider splitting large documentation files")
        print("- Use agent-specific contexts for specialized tasks")
        print("- Implement regular context pruning")
    else:
        print("- Token usage is within healthy limits")
        print("- Continue monitoring as project grows")

if __name__ == "__main__":
    main()