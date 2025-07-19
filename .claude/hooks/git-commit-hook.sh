#!/bin/bash
# Git commit validation hook
# Prevents direct commits to main branch

current_branch=$(git branch --show-current)

# Check if on main branch
if [[ "$current_branch" == "main" ]]; then
    echo "❌ ERROR: Cannot commit directly to main branch!"
    echo ""
    echo "Please create a feature branch first:"
    echo "  git checkout -b feature/issue-XXX-description"
    echo ""
    echo "Then commit your changes and create a PR:"
    echo "  git add ."
    echo "  git commit -m 'feat: your message'"
    echo "  git push -u origin feature/issue-XXX-description"
    echo "  gh pr create"
    exit 1
fi

# Check if branch follows naming convention
if [[ ! "$current_branch" =~ ^(feature|fix|docs|test|chore|refactor|perf)/.+ ]]; then
    echo "⚠️  WARNING: Branch name doesn't follow convention"
    echo "  Expected: feature/issue-XXX-description"
    echo "  Got: $current_branch"
    echo ""
    echo "Continue anyway? (y/n)"
    read -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "✅ Git commit validation passed"