#!/usr/bin/env python3
"""
Tool for adding or updating timestamps in documentation files.
Ensures all documentation includes "Last Updated: YYYY-MM-DD HH:MM:SS UTC" after the title.
"""

import argparse
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List
import sys


def get_current_timestamp() -> str:
    """Generate current timestamp in required format."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def add_or_update_timestamp(content: str, timestamp: Optional[str] = None) -> str:
    """
    Add or update timestamp in documentation content.
    
    Args:
        content: The file content
        timestamp: Custom timestamp or None for current time
        
    Returns:
        Updated content with timestamp
    """
    if timestamp is None:
        timestamp = get_current_timestamp()
    
    timestamp_line = f"Last Updated: {timestamp}"
    
    # Check if content already has a timestamp
    timestamp_pattern = r'^Last Updated: \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} UTC$'
    
    lines = content.split('\n')
    
    # Find the title line (first line starting with #)
    title_index = -1
    for i, line in enumerate(lines):
        if line.strip().startswith('#'):
            title_index = i
            break
    
    if title_index == -1:
        # No title found, add timestamp at the beginning
        return f"{timestamp_line}\n\n{content}"
    
    # Check if next line after title is already a timestamp
    if title_index + 1 < len(lines):
        next_line = lines[title_index + 1]
        if re.match(timestamp_pattern, next_line.strip()):
            # Update existing timestamp
            lines[title_index + 1] = timestamp_line
        elif next_line.strip() == '':
            # There's a blank line after title, insert timestamp
            lines.insert(title_index + 1, timestamp_line)
        else:
            # Insert timestamp after title with blank line
            lines.insert(title_index + 1, '')
            lines.insert(title_index + 1, timestamp_line)
    else:
        # Title is at the end, add timestamp
        lines.append(timestamp_line)
    
    return '\n'.join(lines)


def process_file(filepath: Path, timestamp: Optional[str] = None, dry_run: bool = False) -> bool:
    """
    Process a single documentation file.
    
    Args:
        filepath: Path to the file
        timestamp: Custom timestamp or None for current time
        dry_run: If True, don't write changes
        
    Returns:
        True if file was modified, False otherwise
    """
    if not filepath.exists():
        print(f"Error: File not found: {filepath}")
        return False
    
    try:
        content = filepath.read_text(encoding='utf-8')
        updated_content = add_or_update_timestamp(content, timestamp)
        
        if content != updated_content:
            if not dry_run:
                filepath.write_text(updated_content, encoding='utf-8')
                print(f"✓ Updated: {filepath}")
            else:
                print(f"Would update: {filepath}")
            return True
        else:
            print(f"✓ Already has timestamp: {filepath}")
            return False
            
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False


def find_documentation_files(directory: Path, pattern: str = "*.md") -> List[Path]:
    """Find all documentation files in directory."""
    return list(directory.rglob(pattern))


def main():
    parser = argparse.ArgumentParser(
        description="Add or update timestamps in documentation files"
    )
    parser.add_argument(
        'paths',
        nargs='+',
        type=Path,
        help='Files or directories to process'
    )
    parser.add_argument(
        '--timestamp',
        help='Custom timestamp (default: current time)',
        default=None
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be changed without modifying files'
    )
    parser.add_argument(
        '--recursive',
        action='store_true',
        help='Process directories recursively'
    )
    parser.add_argument(
        '--pattern',
        default='*.md',
        help='File pattern for recursive search (default: *.md)'
    )
    
    args = parser.parse_args()
    
    files_to_process = []
    
    for path in args.paths:
        if path.is_file():
            files_to_process.append(path)
        elif path.is_dir():
            if args.recursive:
                files_to_process.extend(find_documentation_files(path, args.pattern))
            else:
                # Only process direct children
                files_to_process.extend(path.glob(args.pattern))
        else:
            print(f"Warning: Path not found: {path}")
    
    if not files_to_process:
        print("No files to process")
        return 1
    
    modified_count = 0
    for filepath in sorted(set(files_to_process)):
        if process_file(filepath, args.timestamp, args.dry_run):
            modified_count += 1
    
    print(f"\nSummary: {modified_count}/{len(files_to_process)} files modified")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())