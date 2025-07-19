#!/bin/bash
# Claude session start hook - runs when a new session begins

set -euo pipefail

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}🚀 Claude Session Starting...${NC}"

# 1. Run context validation
echo -e "\n${YELLOW}🔍 Validating context structure...${NC}"
if command -v python3 &> /dev/null; then
    python3 scripts/context/validate_context.py 2>/dev/null || echo "Context validation not available"
fi

# 2. Check token usage
echo -e "\n${YELLOW}📊 Checking token usage...${NC}"
if [[ -f "CLAUDE.md" ]]; then
    claude_tokens=$(python3 -c "
import tiktoken
encoding = tiktoken.get_encoding('cl100k_base')
with open('CLAUDE.md', 'r') as f:
    print(len(encoding.encode(f.read())))
" 2>/dev/null || echo "unknown")
    echo "CLAUDE.md: ${claude_tokens} tokens"
fi

# 3. Clear scratchpad
if [[ -f ".claude/state/scratchpad.md" ]]; then
    echo -e "\n${YELLOW}🧹 Clearing scratchpad...${NC}"
    cat > .claude/state/scratchpad.md << 'EOF'
# Claude Scratchpad

> **Purpose**: Temporary working memory for current session. Cleared between sessions.

## Current Task Notes
<!-- Add working notes here -->

## Decisions Made
<!-- Track key decisions -->

## Questions/Blockers
<!-- Note any issues -->

## Next Steps
<!-- What to do next -->

---
*This file is for temporary notes. Important information should be moved to appropriate documentation.*
EOF
fi

# 4. Log session start
echo -e "\n${YELLOW}📝 Logging session start...${NC}"
mkdir -p .claude/state/logs
echo "$(date '+%Y-%m-%d %H:%M:%S') - Session started" >> .claude/state/logs/sessions.log

echo -e "\n${GREEN}✅ Session initialized!${NC}"
echo -e "${YELLOW}💡 Remember to run 'just health' before starting work${NC}"