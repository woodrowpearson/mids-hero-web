#!/bin/bash
# validate-git-workflow.sh - Ensures proper Git workflow is followed

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🔍 Validating Git workflow..."

# Get current branch
current_branch=$(git branch --show-current)

# Check if on protected branch
if [[ "$current_branch" == "main" ]] || [[ "$current_branch" == "master" ]]; then
    echo -e "${RED}❌ ERROR: You are on a protected branch: $current_branch${NC}"
    echo ""
    echo "You must create a feature branch before making changes:"
    echo "  git checkout -b feature/issue-XXX-description"
    echo ""
    echo "Standard branch prefixes:"
    echo "  - feature/ : New features"
    echo "  - fix/     : Bug fixes"
    echo "  - docs/    : Documentation"
    echo "  - test/    : Test additions"
    echo "  - chore/   : Maintenance"
    echo "  - refactor/: Code refactoring"
    echo "  - perf/    : Performance improvements"
    exit 1
fi

# Validate branch naming convention
if [[ ! "$current_branch" =~ ^(feature|fix|docs|test|chore|refactor|perf)/.+ ]]; then
    echo -e "${YELLOW}⚠️  WARNING: Branch name doesn't follow convention${NC}"
    echo "  Current: $current_branch"
    echo "  Expected: {prefix}/issue-XXX-description"
    echo ""
    echo "Examples:"
    echo "  - feature/issue-123-user-auth"
    echo "  - fix/issue-456-login-bug"
    echo "  - docs/epic-3-api-documentation"
fi

# Check for uncommitted changes
if [[ -n $(git status -s) ]]; then
    echo -e "${YELLOW}📝 You have uncommitted changes${NC}"
    echo ""
    echo "To commit:"
    echo "  just ucp \"feat: your message\""
    echo "  # or"
    echo "  git add ."
    echo "  git commit -m \"feat: your message\""
fi

# Check if branch exists on remote
if ! git ls-remote --heads origin "$current_branch" | grep -q "$current_branch"; then
    echo -e "${YELLOW}🔄 Branch not yet pushed to remote${NC}"
    echo ""
    echo "To push:"
    echo "  git push -u origin $current_branch"
fi

# Check for existing PR
if command -v gh &> /dev/null; then
    pr_info=$(gh pr list --head "$current_branch" --json number,state,title 2>/dev/null || echo "[]")
    if [[ "$pr_info" == "[]" ]]; then
        echo -e "${YELLOW}🔀 No PR exists for this branch${NC}"
        echo ""
        echo "To create PR:"
        echo "  gh pr create"
    else
        echo -e "${GREEN}✅ PR exists for this branch${NC}"
        echo "$pr_info" | jq -r '.[] | "  #\(.number): \(.title) (\(.state))"'
    fi
fi

echo ""
echo -e "${GREEN}✅ Git workflow validation complete${NC}"

# If we're on a feature branch with changes, remind about the workflow
if [[ "$current_branch" != "main" ]] && [[ "$current_branch" != "master" ]] && [[ -n $(git status -s) ]]; then
    echo ""
    echo "📋 Next steps:"
    echo "  1. just ucp \"your commit message\""
    echo "  2. git push -u origin $current_branch"
    echo "  3. gh pr create"
fi