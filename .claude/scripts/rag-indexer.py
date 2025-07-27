#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# ///
"""Placeholder RAG index builder."""
import sys
from pathlib import Path


def main(directory: str = 'docs') -> None:
    path = Path(directory)
    print(f"Indexing documents in {path} (placeholder)")


if __name__ == '__main__':
    arg = sys.argv[1] if len(sys.argv) > 1 else 'docs'
    main(arg)
