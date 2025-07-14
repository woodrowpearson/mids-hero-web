#!/bin/bash
# Start a monitored debug session with context protection

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Create session ID
SESSION_ID="debug-$(date +%Y%m%d-%H%M%S)"
SESSION_DIR=".agent-scratch/$SESSION_ID"

echo -e "${BLUE}🔧 Starting Debug Session: $SESSION_ID${NC}"

# Create session directory
mkdir -p "$SESSION_DIR"

# Initialize session log
cat > "$SESSION_DIR/session.log" << EOF
Debug Session Started: $(date)
Session ID: $SESSION_ID
Working Directory: $(pwd)
Git Branch: $(git branch --show-current 2>/dev/null || echo "not in git repo")
EOF

# Save initial state
echo -e "${GREEN}📸 Saving initial state...${NC}"
git status --short > "$SESSION_DIR/initial-git-status.txt" 2>/dev/null || true

# Start context monitor in background
echo -e "${YELLOW}📊 Starting context monitor...${NC}"
python scripts/context/debug_context_monitor.py --session-id "$SESSION_ID" &
MONITOR_PID=$!
echo $MONITOR_PID > "$SESSION_DIR/monitor.pid"

# Set up cleanup
cleanup() {
    echo -e "\n${YELLOW}🧹 Cleaning up debug session...${NC}"
    
    # Stop monitor if running
    if [ -f "$SESSION_DIR/monitor.pid" ]; then
        PID=$(cat "$SESSION_DIR/monitor.pid")
        if kill -0 $PID 2>/dev/null; then
            kill $PID
        fi
    fi
    
    # Generate summary
    echo -e "${BLUE}📝 Generating session summary...${NC}"
    python scripts/context/debug_context_monitor.py --session-id "$SESSION_ID" --once > "$SESSION_DIR/final-summary.json"
    
    # Show token usage
    if [ -f "$SESSION_DIR/monitor_state.json" ]; then
        USAGE=$(jq -r '.token_checkpoints[-1].token_usage // 0' "$SESSION_DIR/monitor_state.json")
        PCT=$(jq -r '.token_checkpoints[-1].percentage // 0' "$SESSION_DIR/monitor_state.json")
        echo -e "${GREEN}Final token usage: $USAGE (${PCT}%)${NC}"
    fi
    
    echo -e "${GREEN}✅ Debug session ended. Artifacts in: $SESSION_DIR${NC}"
}

trap cleanup EXIT

# Print instructions
echo -e "${GREEN}✅ Debug session initialized!${NC}"
echo -e "${YELLOW}📍 Session directory: $SESSION_DIR${NC}"
echo -e "${YELLOW}🔍 Monitor PID: $MONITOR_PID${NC}"
echo ""
echo -e "Commands:"
echo -e "  ${BLUE}Check status:${NC} cat $SESSION_DIR/monitor_state.json | jq '.token_checkpoints[-1]'"
echo -e "  ${BLUE}View alerts:${NC}  cat $SESSION_DIR/monitor_state.json | jq '.alerts'"
echo -e "  ${BLUE}Stop session:${NC} exit or Ctrl+C"
echo ""
echo -e "${YELLOW}⚠️  Context monitor will alert at 70%, 85%, and 90% usage${NC}"
echo -e "${YELLOW}💡 Run '/compact <summary>' if alerted about high usage${NC}"
echo ""

# Export session variables
export DEBUG_SESSION_ID="$SESSION_ID"
export DEBUG_SESSION_DIR="$SESSION_DIR"

# Keep session active
echo -e "${GREEN}Debug session is active. Press Ctrl+C to end.${NC}"
wait $MONITOR_PID