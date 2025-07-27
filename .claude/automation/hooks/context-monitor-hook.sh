#!/bin/bash
# Context monitoring hook - runs periodically during session

set -euo pipefail

# Check if we should run (every 10 minutes or on demand)
LAST_CHECK_FILE=".claude/state/.last-context-check"
if [[ -f "$LAST_CHECK_FILE" ]]; then
    LAST_CHECK=$(cat "$LAST_CHECK_FILE")
    CURRENT_TIME=$(date +%s)
    ELAPSED=$((CURRENT_TIME - LAST_CHECK))
    
    # Skip if less than 10 minutes
    if [[ $ELAPSED -lt 600 ]]; then
        exit 0
    fi
fi

# Record check time
date +%s > "$LAST_CHECK_FILE"

# Calculate current context usage
CONTEXT_USAGE=$(python3 -c "
import os
import tiktoken
from pathlib import Path

encoding = tiktoken.get_encoding('cl100k_base')
total_tokens = 0

# Count tokens in loaded files
loaded_files = [
    'CLAUDE.md',
    '.claude/settings.json',
    '.claude/context-map.json'
]

for file_path in loaded_files:
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            total_tokens += len(encoding.encode(f.read()))

print(f'{total_tokens:,}')
" 2>/dev/null || echo "0")

# Check against thresholds
if [[ "$CONTEXT_USAGE" =~ ^[0-9,]+$ ]]; then
    USAGE_NUM=$(echo "$CONTEXT_USAGE" | tr -d ',')
    
    if [[ $USAGE_NUM -gt 90000 ]]; then
        echo "⚠️  WARNING: Context usage high: ${CONTEXT_USAGE} tokens (>90K)"
        echo "💡 Consider using /clear to reset context"
    elif [[ $USAGE_NUM -gt 110000 ]]; then
        echo "🚨 CRITICAL: Context usage critical: ${CONTEXT_USAGE} tokens (>110K)"
        echo "🔄 Auto-pruning recommended"
    fi
fi

# Log current usage
mkdir -p .claude/state/logs
echo "$(date '+%Y-%m-%d %H:%M:%S') - Context usage: ${CONTEXT_USAGE} tokens" >> .claude/state/logs/context-usage.log

echo "Context usage: ${CONTEXT_USAGE} tokens"
exit 0
