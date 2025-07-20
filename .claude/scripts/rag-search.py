#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# ///
"""Placeholder RAG search utility."""
import sys


def main(query: str) -> None:
    print(f"Searching for '{query}' (placeholder)")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: rag-search.py QUERY")
        sys.exit(1)
    main(sys.argv[1])
