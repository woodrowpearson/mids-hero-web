# Claude GitHub Integration Guide

> Complete guide to Claude AI integrations in the Mids Hero Web project

## Overview

This project uses **Anthropic's Claude Code Action** (`anthropics/claude-code-action@beta`) to provide AI-powered assistance directly in GitHub workflows. Claude can review PRs, answer questions, implement suggestions, and process approvals automatically.

## Architecture

### Local Development (Claude Code CLI)
When you run `claude` locally in your terminal:
- **Full control**: Interactive session with unlimited turns
- **All tools available**: Read/Write/Edit files, run commands, commit changes
- **Manual workflow**: You explicitly ask Claude to do tasks
- **Context**: Uses `.claude/` directory structure and `CLAUDE.md`

### GitHub Actions (Claude Code Action)
When Claude runs in GitHub Actions:
- **Automated triggers**: Responds to PR events and comments
- **Limited turns**: Configured max_turns (3-5 depending on task)
- **Timeouts**: 5-20 minutes depending on task complexity
- **Prompts**: Pre-built prompts in workflow files
- **Stateless**: Each run is independent

---

## GitHub Workflow: `claude-unified.yml`

**Location**: `.github/workflows/claude-unified.yml`

This is the **main Claude integration workflow** that handles all Claude interactions on GitHub.

### Trigger Events

The workflow activates on:

#### 1. Pull Request Events
```yaml
on:
  pull_request:
    types: [opened, synchronize]
```

**What happens**: Claude automatically reviews the PR
- ✅ Runs on new PRs (opened)
- ✅ Runs when commits are pushed (synchronize)
- ⏭️ Skips if PR has label `skip-claude-review`

#### 2. Issue Comment Events
```yaml
on:
  issue_comment:
    types: [created]
```

**What happens**: Claude responds to comments containing specific triggers

**Supported triggers**:
- `@claude` - Ask Claude a question
- `implement doc suggestions` - Apply documentation suggestions
- `approved` - Process approval and apply changes

**IMPORTANT**: This only works for **regular PR comments**, NOT review comments!

---

## How Claude Triggers Work

### ✅ Automatic PR Review

**When**: PR opened or new commits pushed
**How**: Automatically triggers
**What Claude does**: Reviews code and posts feedback

```bash
# Example: Open a PR
git push -u origin feature/my-feature
gh pr create --title "Add new feature"
# → Claude automatically reviews within 5-15 minutes
```

**Dynamic timeout based on PR size**:
- < 10 files: 5 minutes
- 10-50 files: 10 minutes
- 50+ files: 15 minutes

### ✅ Ask Claude Questions (Regular Comment)

**When**: You leave a **regular comment** with `@claude`
**How**: Comment on the PR conversation
**What Claude does**: Responds to your question

**Example**:
```
# In PR conversation (NOT a review):
@claude What is the current status of Epic 3?
```

**Works**: ✅ Regular PR comment
**Doesn't work**: ❌ PR review comment
**Doesn't work**: ❌ Inline code review comment

### ❌ Review Comments (CURRENT LIMITATION)

**What you tried**: Submit a review with `@claude` mention
**Why it didn't work**: Workflow only listens to `issue_comment`, not `pull_request_review`

GitHub event types:
- `issue_comment` - Regular comments on PR ✅ Supported
- `pull_request_review` - Review submissions ❌ NOT supported
- `pull_request_review_comment` - Inline code comments ❌ NOT supported

**Fix**: See [Solution](#solution-adding-review-comment-support) below

### ✅ Implement Documentation Suggestions

**When**: Comment contains `implement doc suggestions`
**How**: Leave a regular comment
**What Claude does**:
1. Searches for recent doc suggestions from github-actions bot
2. Applies suggested updates
3. Ensures CLAUDE.md stays under 5K tokens
4. Commits with message: `docs: implement automated documentation suggestions`

### ✅ Process Approvals

**When**: Comment contains `approved`
**How**: Leave a regular comment
**What Claude does**:
1. Finds recent documentation suggestions
2. Determines approval type (simple or with modifications)
3. Applies approved changes
4. Commits with message: `docs: apply approved documentation changes`

---

## Claude Action Configuration

### Jobs Overview

The `claude-unified.yml` workflow has 3 jobs:

#### 1. `determine-action`
**Purpose**: Detect what type of action to take
**Outputs**:
- `action_type`: pr-review | question | doc-implement | approval | none
- `should_run`: true/false
- `timeout`: minutes for the action
- `max_turns`: maximum conversation turns

#### 2. `claude-action`
**Purpose**: Execute Claude with the appropriate prompt
**Uses**: `anthropics/claude-code-action@beta`
**Configuration**:
- `cache_prompts: true` - Cache prompts for faster responses
- `cache_control: ephemeral` - Use ephemeral cache
- `timeout_minutes`: Dynamic based on task
- `max_turns`: 3-5 depending on task
- `direct_prompt_file`: Pre-built prompt from determine-action job

#### 3. `create-summary`
**Purpose**: Post summary to GitHub Actions and PR

---

## Action Types Explained

### 1. PR Review (`pr-review`)
- **Trigger**: PR opened/synchronized
- **Timeout**: 5-15 min (dynamic)
- **Max turns**: 5
- **Prompt focus**:
  - City of Heroes domain correctness
  - Code quality and best practices
  - Critical bugs or security issues
  - Performance bottlenecks
  - Missing test coverage

### 2. Question (`question`)
- **Trigger**: `@claude` in comment
- **Timeout**: 10 min
- **Max turns**: 3
- **Prompt focus**: Answer user question about codebase/epics/game mechanics

### 3. Doc Implementation (`doc-implement`)
- **Trigger**: `implement doc suggestions` in comment
- **Timeout**: 15 min
- **Max turns**: 3
- **Prompt focus**: Apply documentation suggestions, verify token limits

### 4. Approval Processing (`approval`)
- **Trigger**: `approved` in comment
- **Timeout**: 20 min
- **Max turns**: 3
- **Prompt focus**: Apply approved changes with any modifications

---

## Solution: Adding Review Comment Support

### Problem Identified

Your comment on PR #295 was a **review comment**, which triggers `pull_request_review` event, but the workflow only listens for `issue_comment` events.

### Fix: Update Workflow Triggers

Edit `.github/workflows/claude-unified.yml`:

```yaml
on:
  pull_request:
    types: [opened, synchronize]
    # ... existing paths config ...

  # Add these new event types:
  pull_request_review:
    types: [submitted]

  pull_request_review_comment:
    types: [created]

  issue_comment:
    types: [created]
```

### Fix: Update Detection Logic

In the `determine-action` job, update the detection step (around line 82):

```bash
# Handle issue comments (regular PR comments)
elif [[ "${{ github.event_name }}" == "issue_comment" ]] && [[ "${{ github.event.issue.pull_request }}" != "" ]]; then
  COMMENT="${{ github.event.comment.body }}"

  # Check for different triggers
  if [[ "$COMMENT" == *"@claude"* ]]; then
    ACTION_TYPE="question"
    SHOULD_RUN="true"
    PROMPT_TYPE="question"
    TIMEOUT=10
    MAX_TURNS=3
  fi

# NEW: Handle pull request reviews
elif [[ "${{ github.event_name }}" == "pull_request_review" ]]; then
  COMMENT="${{ github.event.review.body }}"

  # Check for @claude mentions in review
  if [[ "$COMMENT" == *"@claude"* ]]; then
    ACTION_TYPE="review-response"
    SHOULD_RUN="true"
    PROMPT_TYPE="review-response"
    TIMEOUT=15
    MAX_TURNS=5
    CHECKOUT_REF="${{ github.event.pull_request.head.ref }}"
  fi

# NEW: Handle inline review comments
elif [[ "${{ github.event_name }}" == "pull_request_review_comment" ]]; then
  COMMENT="${{ github.event.comment.body }}"

  # Check for @claude mentions in inline comment
  if [[ "$COMMENT" == *"@claude"* ]]; then
    ACTION_TYPE="inline-question"
    SHOULD_RUN="true"
    PROMPT_TYPE="inline-question"
    TIMEOUT=10
    MAX_TURNS=3
  fi
fi
```

### Fix: Add New Prompt Types

In the `build-prompt` step (around line 169), add new cases:

```bash
case "${{ needs.determine-action.outputs.prompt_type }}" in
  # ... existing cases ...

  review-response)
    PROMPT="You are responding to review comments in PR #${{ github.event.pull_request.number }}.

Review comment: ${{ github.event.review.body }}

Tasks:
1. Read the review comments carefully
2. Address each point raised
3. Make necessary code changes
4. Commit changes with descriptive message
5. Respond to the review explaining what was changed

Focus on:
- Addressing all review feedback
- Maintaining code quality
- Following project standards
- Testing changes"
    ;;

  inline-question)
    PROMPT="You are responding to an inline code review comment in PR #${{ github.event.pull_request.number }}.

Comment: ${{ github.event.comment.body }}
File: ${{ github.event.comment.path }}
Line: ${{ github.event.comment.line }}

Provide a helpful response about the specific code in question."
    ;;
esac
```

### Fix: Update Extract Question Step

Update the extract question step (around line 149) to handle review events:

```yaml
- name: Extract question
  id: extract-question
  if: |
    needs.determine-action.outputs.action_type == 'question' ||
    needs.determine-action.outputs.action_type == 'review-response' ||
    needs.determine-action.outputs.action_type == 'inline-question'
  run: |
    COMMENT=""

    if [[ "${{ github.event_name }}" == "issue_comment" ]]; then
      COMMENT="${{ github.event.comment.body }}"
    elif [[ "${{ github.event_name }}" == "pull_request_review" ]]; then
      COMMENT="${{ github.event.review.body }}"
    elif [[ "${{ github.event_name }}" == "pull_request_review_comment" ]]; then
      COMMENT="${{ github.event.comment.body }}"
    fi

    QUESTION=$(echo "$COMMENT" | sed 's/@claude//' | sed 's/^[[:space:]]*//')
    echo "question<<EOF" >> $GITHUB_OUTPUT
    echo "$QUESTION" >> $GITHUB_OUTPUT
    echo "EOF" >> $GITHUB_OUTPUT
```

---

## Testing the Fix

After implementing the changes:

### 1. Commit and push the workflow update
```bash
git checkout -b fix/claude-review-comments
# Make the changes to claude-unified.yml
git add .github/workflows/claude-unified.yml
git commit -m "fix: add support for PR review comment triggers"
git push -u origin fix/claude-review-comments
```

### 2. Create a test PR
```bash
gh pr create --title "Test: Claude review comment support"
```

### 3. Test different comment types

**Test 1: Regular PR comment (should already work)**
```
@claude What is the current epic status?
```

**Test 2: Submit a review (will work after fix)**
1. Go to PR Files tab
2. Click "Review changes"
3. Write: `@claude - Review my comments and make changes.`
4. Submit review

**Test 3: Inline code comment (will work after fix)**
1. Go to PR Files tab
2. Hover over a line of code
3. Click "+" to add comment
4. Write: `@claude - Why is this implemented this way?`
5. Click "Add single comment"

### 4. Verify workflow runs
```bash
gh run list --workflow=claude-unified.yml --limit 5
```

---

## Other Workflows

### `update-claude-docs.yml`

**Purpose**: Automatically update Claude documentation
**Triggers**:
- Push to backend/frontend code
- Changes to `.claude/**/*.md` or `CLAUDE.md`
- Manual dispatch

**What it does**:
1. Updates timestamps in documentation
2. Checks files approaching token limits
3. Creates PR if changes needed
4. Creates issues for token limit warnings

**NOT** related to Claude responding to comments.

### `context-health-check.yml`

**Purpose**: Validate `.claude/` directory structure
**NOT** related to Claude AI integration

### `ci.yml`

**Purpose**: Run tests, linting, builds
**NOT** related to Claude AI integration

---

## FAQ

### Q: Why didn't my `@claude` review comment work?
**A**: The workflow only listens to `issue_comment` (regular PR comments), not `pull_request_review` (review submissions). See [Solution](#solution-adding-review-comment-support).

### Q: How do I ask Claude a question on a PR right now?
**A**: Leave a **regular comment** (not a review) containing `@claude`:
1. Go to PR "Conversation" tab
2. Scroll to bottom comment box
3. Write: `@claude [your question]`
4. Click "Comment"

### Q: Can Claude make commits on GitHub?
**A**: Yes! Claude can commit changes when triggered by:
- `implement doc suggestions` comment
- `approved` comment
- Review response prompts (after fix)

### Q: How long does Claude take to respond?
**A**: 5-20 minutes depending on task complexity and timeout settings.

### Q: Can I use Claude for code changes, not just docs?
**A**: Currently the prompts are focused on documentation and reviews. You can extend the prompts to handle code changes by updating the `build-prompt` step.

### Q: Why do some workflow runs fail?
**A**: Common reasons:
- ANTHROPIC_API_KEY not set (requires secret)
- Timeout exceeded
- Claude encountered error
- Check workflow logs: `gh run view [run-id] --log`

### Q: How do I disable auto-review for a PR?
**A**: Add the label `skip-claude-review` to the PR.

---

## Required Secrets

For Claude GitHub Actions to work, you need:

### `ANTHROPIC_API_KEY`
**Where**: GitHub Settings → Secrets and variables → Actions
**What**: Your Anthropic API key for Claude
**Required for**: All Claude action runs

### `GITHUB_TOKEN`
**Where**: Automatically provided by GitHub
**What**: Token for GitHub API access
**Required for**: Reading PRs, posting comments, creating commits

---

## Best Practices

### 1. Use Regular Comments for Questions
Until review comment support is added, use regular PR comments (Conversation tab) for `@claude` mentions.

### 2. Be Specific in Prompts
When mentioning `@claude`, be clear about what you want:
- ✅ `@claude - Check if Epic 3 API endpoints follow FastAPI best practices`
- ❌ `@claude - check this`

### 3. Monitor Token Limits
Claude context has limits. Keep documentation concise:
- CLAUDE.md: < 5K tokens
- Module guides: < 3K tokens each

### 4. Use Skip Label for WIP PRs
Add `skip-claude-review` label to draft PRs to avoid unnecessary reviews.

### 5. Check Workflow Logs
If Claude doesn't respond:
```bash
gh run list --workflow=claude-unified.yml
gh run view [run-id] --log
```

---

## Summary

| Trigger | Event Type | Status | How to Use |
|---------|-----------|--------|------------|
| PR opened/updated | `pull_request` | ✅ Works | Automatic |
| Regular PR comment | `issue_comment` | ✅ Works | Comment with `@claude` |
| PR review submission | `pull_request_review` | ❌ Not supported | Need to add trigger |
| Inline code comment | `pull_request_review_comment` | ❌ Not supported | Need to add trigger |
| Doc suggestions | `issue_comment` | ✅ Works | Comment `implement doc suggestions` |
| Approval | `issue_comment` | ✅ Works | Comment `approved` |

**Next Steps**: Implement the [review comment support fix](#solution-adding-review-comment-support) to enable `@claude` mentions in review submissions and inline comments.

---

**Related Documentation**:
- [Claude Code GitHub Actions Docs](https://docs.claude.com/en/docs/claude-code/github-actions)
- [anthropics/claude-code-action](https://github.com/anthropics/claude-code-action)
- [Development Workflow](./.development-workflow.md)
