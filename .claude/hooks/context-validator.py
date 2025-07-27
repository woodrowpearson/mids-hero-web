#!/usr/bin/env python3
"""
Claude Code hook for context validation
Runs token analysis and validates context structure
"""

import json
import sys
import os
from pathlib import Path
import tiktoken

def validate_context():
    """Validate context structure and token usage."""
    try:
        # Initialize tokenizer
        encoding = tiktoken.get_encoding("cl100k_base")
        
        # Load context configuration
        context_map_path = Path(".claude/context-map.json")
        if not context_map_path.exists():
            return {"continue": True, "status": "no_config"}
        
        context_config = json.loads(context_map_path.read_text())
        limits = context_config.get('file_health_checks', {}).get('max_file_sizes', {})
        
        issues = []
        
        # Check CLAUDE.md
        claude_path = Path("CLAUDE.md")
        if claude_path.exists():
            tokens = len(encoding.encode(claude_path.read_text()))
            limit = limits.get('CLAUDE.md', 5000)
            if tokens > limit:
                issues.append(f"CLAUDE.md: {tokens} > {limit} tokens")
        
        # Check module files
        modules_dir = Path(".claude/modules")
        if modules_dir.exists():
            for module_dir in modules_dir.iterdir():
                if module_dir.is_dir():
                    guide_path = module_dir / "guide.md"
                    if guide_path.exists():
                        tokens = len(encoding.encode(guide_path.read_text()))
                        limit = limits.get('module_guide', 10000)
                        if tokens > limit:
                            issues.append(f"{guide_path}: {tokens} > {limit} tokens")
        
        # Log validation
        log_dir = Path(".claude/state/logs")
        log_dir.mkdir(parents=True, exist_ok=True)
        
        with open(log_dir / "validation.log", "a") as f:
            import datetime
            timestamp = datetime.datetime.now().isoformat()
            if issues:
                f.write(f"{timestamp} WARN: {len(issues)} context issues\\n")
                for issue in issues:
                    f.write(f"  - {issue}\\n")
            else:
                f.write(f"{timestamp} OK: Context validation passed\\n")
        
        return {
            "continue": True,
            "status": "validation_complete",
            "issues_found": len(issues)
        }
        
    except Exception as e:
        return {
            "continue": True,
            "status": "validation_error",
            "error": str(e)
        }

def main():
    """Main hook entry point."""
    try:
        # Read input from Claude Code
        input_data = json.load(sys.stdin)
        
        # Run validation
        result = validate_context()
        
        # Output result
        print(json.dumps(result))
        
        # Exit with appropriate code
        sys.exit(0 if result.get("issues_found", 0) == 0 else 1)
        
    except Exception as e:
        # Graceful fallback
        print(json.dumps({"continue": True, "error": str(e)}))
        sys.exit(0)

if __name__ == "__main__":
    main()
