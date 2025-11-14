#!/usr/bin/env python3
"""
Claude Code hook to enforce token limits on file edits
Prevents files from exceeding defined token limits
"""

import json
import sys
import tiktoken
from pathlib import Path

def check_token_limits():
    """Check if file content exceeds token limits."""
    try:
        # Read input from Claude Code
        input_data = json.load(sys.stdin)
        
        # Get tool input
        tool_input = input_data.get('tool_input', {})
        file_path = tool_input.get('file_path', '')
        
        # Get content to check
        content = (
            tool_input.get('content', '') or 
            tool_input.get('new_string', '') or
            ''
        )
        
        if not content or not file_path:
            # No content to check
            return {"continue": True}
        
        # Initialize tokenizer
        encoding = tiktoken.get_encoding("cl100k_base")
        tokens = len(encoding.encode(content))
        
        # Load limits from context-map.json
        context_map_path = Path(".claude/context-map.json")
        if context_map_path.exists():
            context_config = json.loads(context_map_path.read_text())
            limits = context_config.get('file_health_checks', {}).get('max_file_sizes', {})
        else:
            # Default limits
            limits = {
                'CLAUDE.md': 5000,
                'module_guide': 10000,
                'workflow': 5000,
                'reference': 8000
            }
        
        # Determine limit based on file path
        limit = 5000  # Default
        
        if file_path == 'CLAUDE.md':
            limit = limits.get('CLAUDE.md', 5000)
        elif 'modules' in file_path and file_path.endswith('guide.md'):
            limit = limits.get('module_guide', 10000)
        elif 'workflows' in file_path:
            limit = limits.get('workflow', 5000)
        elif any(keyword in file_path for keyword in ['reference', 'spec', 'schema']):
            limit = limits.get('reference', 8000)
        
        # Check limit
        if tokens > limit:
            return {
                "continue": False,
                "decision": "block",
                "reason": f"File {file_path} would exceed token limit: {tokens} > {limit} tokens"
            }
        
        # Log the check
        log_dir = Path(".claude/state/logs")
        log_dir.mkdir(parents=True, exist_ok=True)
        
        with open(log_dir / "token-checks.log", "a") as f:
            import datetime
            timestamp = datetime.datetime.now().isoformat()
            f.write(f"{timestamp} {file_path}: {tokens}/{limit} tokens\\n")
        
        return {"continue": True}
        
    except Exception as e:
        # Don't block on errors
        return {"continue": True, "error": str(e)}

def main():
    """Main hook entry point."""
    result = check_token_limits()
    print(json.dumps(result))
    
    # Exit with appropriate code
    if result.get("decision") == "block":
        sys.exit(2)  # Block the operation
    else:
        sys.exit(0)  # Allow the operation

if __name__ == "__main__":
    main()
