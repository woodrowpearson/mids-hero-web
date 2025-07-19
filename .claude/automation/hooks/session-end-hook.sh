#!/bin/bash
# Claude session end hook - runs when session ends

set -euo pipefail

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}🏁 Claude Session Ending...${NC}"

# 1. Save scratchpad if it has content
if [[ -f ".claude/state/scratchpad.md" ]]; then
    SCRATCHPAD_SIZE=$(wc -l < .claude/state/scratchpad.md)
    if [[ $SCRATCHPAD_SIZE -gt 20 ]]; then
        echo -e "\n${YELLOW}💾 Saving scratchpad notes...${NC}"
        TIMESTAMP=$(date +%Y%m%d_%H%M%S)
        mkdir -p .claude/state/summaries
        cp .claude/state/scratchpad.md ".claude/state/summaries/session_${TIMESTAMP}_notes.md"
        echo "Saved to: .claude/state/summaries/session_${TIMESTAMP}_notes.md"
    fi
fi

# 2. Generate session summary if tokens > 50K
echo -e "\n${YELLOW}📊 Checking if summary needed...${NC}"
python3 -c "
import json
from pathlib import Path
from datetime import datetime

# Check context-map for threshold
context_map = json.loads(Path('.claude/context-map.json').read_text())
threshold = context_map.get('context_offloading', {}).get('auto_summarize_at', 50000)

# This would need actual context tracking in practice
print(f'Summary threshold: {threshold:,} tokens')
print('(Automatic summarization will be implemented in future)')
" 2>/dev/null || true

# 3. Log session end
echo -e "\n${YELLOW}📝 Logging session end...${NC}"
mkdir -p .claude/state/logs
echo "$(date '+%Y-%m-%d %H:%M:%S') - Session ended" >> .claude/state/logs/sessions.log

# 4. Run final validation
echo -e "\n${YELLOW}🔍 Final context validation...${NC}"
python3 scripts/context/validate_context.py 2>/dev/null | grep -E "(✅|❌|⚠️)" || true

echo -e "\n${GREEN}✅ Session closed successfully!${NC}"