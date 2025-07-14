#!/bin/bash
# Short alias for update-commit-push
# Usage: claude run ucp.sh [commit message]

set -euo pipefail

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

cd "$(git rev-parse --show-toplevel)"

# Quick function to update, commit, and push
echo -e "${YELLOW}🚀 Quick update-commit-push...${NC}"

# 1. Add all changes
git add -A

# 2. Update refactor progress if possible
if [[ -f "./scripts/context/safe_refactor_update.sh" ]]; then
    # Quick update for any new files
    for file in $(git diff --cached --name-only --diff-filter=A); do
        ./scripts/context/safe_refactor_update.sh --file-created "$file" 2>/dev/null || true
    done
    git add .abundance-ai/refactor-progress.json 2>/dev/null || true
fi

# 3. Commit with provided message or auto-generate
if [[ $# -gt 0 ]]; then
    # Use provided commit message
    git commit -m "$*" || echo "No changes to commit"
else
    # Auto-generate commit message
    if git diff --cached --quiet; then
        echo "No changes to commit"
    else
        files_changed=$(git diff --cached --name-only | wc -l)
        git commit -m "chore: Update $files_changed file(s) and refactor progress"
    fi
fi

# 4. Push
git push 2>/dev/null || git push -u origin "$(git rev-parse --abbrev-ref HEAD)"

echo -e "${GREEN}✅ Done!${NC}"