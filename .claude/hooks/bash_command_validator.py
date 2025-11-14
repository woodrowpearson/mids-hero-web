#!/usr/bin/env python3
"""
Bash Command Validator Hook
Enforces project command standards
"""

import json
import re
import sys

# Validation rules: (pattern, suggestion)
_VALIDATION_RULES = [
    (r'\bgrep\b', "Use 'rg' (ripgrep) instead of 'grep'"),
    (r'\bfind\b', "Use 'fd' instead of 'find'"),
    (r'\brm\s+-rf\b', "Use 'trash' instead of 'rm -rf'"),
    (r'\bpip\b', "Use 'uv' instead of 'pip'"),
]


def _validate_command(command: str) -> list[str]:
    """Check command against validation rules."""
    issues = []
    for pattern, message in _VALIDATION_RULES:
        if re.search(pattern, command):
            issues.append(message)
    return issues


def main():
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)

    tool_name = input_data.get("tool_name", "")
    if tool_name != "Bash":
        sys.exit(0)

    tool_input = input_data.get("tool_input", {})
    command = tool_input.get("command", "")

    if not command:
        sys.exit(0)

    issues = _validate_command(command)
    if issues:
        print("Command validation failed:", file=sys.stderr)
        for message in issues:
            print(f"  • {message}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
