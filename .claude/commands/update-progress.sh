#!/bin/bash
# Claude command to update project progress, commit, and push
# Usage: claude run update-progress.sh

set -euo pipefail

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project root
PROJECT_ROOT=$(git rev-parse --show-toplevel)
cd "$PROJECT_ROOT"

echo -e "${BLUE}🔄 Updating project progress, committing, and pushing...${NC}"

# Function to check if there are uncommitted changes
has_changes() {
    [[ -n $(git status --porcelain) ]]
}

# Function to get current branch
get_current_branch() {
    git rev-parse --abbrev-ref HEAD
}

# Function to check if branch has upstream
has_upstream() {
    git rev-parse --abbrev-ref --symbolic-full-name @{u} >/dev/null 2>&1
}

# Function to update progress.json
update_progress() {
    if [[ -f ".claude/state/progress.json" ]] && command -v python3 &> /dev/null; then
        python3 -c "
import json
from datetime import datetime

with open('.claude/state/progress.json', 'r') as f:
    data = json.load(f)

# Update timestamp
data['last_updated'] = datetime.now().strftime('%Y-%m-%d')

# Update commit count
import subprocess
try:
    commit_count = subprocess.check_output(['git', 'rev-list', '--count', 'HEAD'], text=True).strip()
    data['commit_count'] = int(commit_count)
except:
    pass

# Update files modified count
try:
    files_modified = len(subprocess.check_output(['git', 'diff', '--cached', '--name-only'], text=True).strip().split('\n'))
    if files_modified > 0:
        data['files_modified'] = files_modified
except:
    pass

# Add recent activity
activity = {
    'timestamp': datetime.now().isoformat(),
    'branch': subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], text=True).strip(),
    'action': 'progress_update'
}

if 'recent_activities' not in data:
    data['recent_activities'] = []

data['recent_activities'].insert(0, activity)
# Keep only last 10 activities
data['recent_activities'] = data['recent_activities'][:10]

with open('.claude/state/progress.json', 'w') as f:
    json.dump(data, f, indent=2)

print('Progress updated successfully')
" || echo "Failed to update progress.json"
    fi
}

# Main workflow
main() {
    local current_branch=$(get_current_branch)
    
    # 1. Stage all changes if any exist
    if has_changes; then
        echo -e "${YELLOW}📝 Staging changes...${NC}"
        git add -A
        
        # Show what will be committed
        echo -e "${YELLOW}Changes to be committed:${NC}"
        git status --short
    else
        echo -e "${YELLOW}ℹ️  No changes to stage${NC}"
    fi
    
    # 2. Update progress
    echo -e "${YELLOW}📊 Updating project progress...${NC}"
    update_progress
    
    # Stage the updated progress file
    git add .claude/state/progress.json 2>/dev/null || true
    
    # 3. Commit if there are staged changes
    if git diff --cached --quiet; then
        echo -e "${YELLOW}ℹ️  No staged changes to commit${NC}"
    else
        echo -e "${YELLOW}💾 Committing changes...${NC}"
        
        # Generate commit message based on changes
        num_files=$(git diff --cached --name-only | wc -l)
        
        # Check if only progress file changed
        if [[ $(git diff --cached --name-only) == ".claude/progress.json" ]]; then
            commit_msg="chore: Update project progress"
        else
            commit_msg="chore: Update $num_files file(s) and project progress

$(git diff --cached --stat)"
        fi
        
        git commit -m "$commit_msg"
        echo -e "${GREEN}✅ Changes committed${NC}"
    fi
    
    # 4. Push to remote
    echo -e "${YELLOW}🚀 Pushing to remote...${NC}"
    
    # Check if branch has upstream
    if has_upstream; then
        git push
    else
        # First time pushing this branch
        git push -u origin "$current_branch"
    fi
    
    echo -e "${GREEN}✅ Successfully pushed to origin/$current_branch${NC}"
    
    # 5. Show summary
    echo -e "\n${BLUE}📋 Summary:${NC}"
    echo -e "Branch: ${GREEN}$current_branch${NC}"
    echo -e "Latest commit: $(git log -1 --oneline)"
    
    # Check if PR exists
    if command -v gh &> /dev/null; then
        pr_number=$(gh pr list --head "$current_branch" --json number --jq '.[0].number' 2>/dev/null || echo "")
        if [[ -n "$pr_number" ]]; then
            echo -e "Pull Request: ${GREEN}#$pr_number${NC}"
            echo -e "View at: ${BLUE}$(gh pr view "$pr_number" --json url --jq '.url')${NC}"
        else
            echo -e "\n💡 ${YELLOW}Tip:${NC} Create a PR with:"
            echo -e "   ${BLUE}gh pr create${NC}"
        fi
    fi
}

# Run main function
main "$@"