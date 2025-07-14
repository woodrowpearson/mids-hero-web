#!/bin/bash
# Claude command to update refactor progress, commit, and push
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

echo -e "${BLUE}🔄 Updating refactor progress, committing, and pushing...${NC}"

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

# Main workflow
main() {
    local current_branch=$(get_current_branch)
    
    # 1. Check if we're on a feature branch
    if [[ "$current_branch" == "main" ]] || [[ "$current_branch" == "develop" ]]; then
        echo -e "${RED}❌ Cannot run on $current_branch branch${NC}"
        echo "Please switch to a feature branch first"
        exit 1
    fi
    
    # 2. Stage all changes if any exist
    if has_changes; then
        echo -e "${YELLOW}📝 Staging changes...${NC}"
        git add -A
        
        # Show what will be committed
        echo -e "${YELLOW}Changes to be committed:${NC}"
        git status --short
    else
        echo -e "${YELLOW}ℹ️  No changes to stage${NC}"
    fi
    
    # 3. Update refactor progress if the script exists
    if [[ -f "./scripts/context/safe_refactor_update.sh" ]]; then
        echo -e "${YELLOW}📊 Updating refactor progress...${NC}"
        
        # Check for any new files to track
        new_files=$(git diff --cached --name-only --diff-filter=A)
        if [[ -n "$new_files" ]]; then
            for file in $new_files; do
                ./scripts/context/safe_refactor_update.sh --file-created "$file" || true
            done
        fi
        
        # Check for modified files
        modified_files=$(git diff --cached --name-only --diff-filter=M)
        if [[ -n "$modified_files" ]]; then
            for file in $modified_files; do
                # Only track if not already the refactor-progress.json itself
                if [[ "$file" != ".abundance-ai/refactor-progress.json" ]]; then
                    ./scripts/context/safe_refactor_update.sh --file-modified "$file" || true
                fi
            done
        fi
        
        # Show current status
        ./scripts/context/safe_refactor_update.sh --status-check || true
        
        # Stage the updated progress file
        git add .abundance-ai/refactor-progress.json 2>/dev/null || true
    fi
    
    # 4. Commit if there are staged changes
    if git diff --cached --quiet; then
        echo -e "${YELLOW}ℹ️  No staged changes to commit${NC}"
    else
        echo -e "${YELLOW}💾 Committing changes...${NC}"
        
        # Generate commit message based on changes
        if git diff --cached --name-only | grep -q "refactor-progress.json"; then
            # If only progress file changed
            if [[ $(git diff --cached --name-only | wc -l) -eq 1 ]]; then
                commit_msg="chore: Update refactor progress"
            else
                # Other files changed too
                commit_msg="chore: Update implementation and refactor progress

$(git diff --cached --stat)"
            fi
        else
            # No progress file, generate based on changes
            num_files=$(git diff --cached --name-only | wc -l)
            commit_msg="chore: Update $num_files file(s)

$(git diff --cached --stat)"
        fi
        
        git commit -m "$commit_msg"
        echo -e "${GREEN}✅ Changes committed${NC}"
    fi
    
    # 5. Push to remote
    echo -e "${YELLOW}🚀 Pushing to remote...${NC}"
    
    # Check if branch has upstream
    if has_upstream; then
        git push
    else
        # First time pushing this branch
        git push -u origin "$current_branch"
    fi
    
    echo -e "${GREEN}✅ Successfully pushed to origin/$current_branch${NC}"
    
    # 6. Show summary
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