# Code Review Command

Automatically review pull requests using the superpowers plugin's code review functionality.

## Usage

Tell Claude: "code review this PR" or "review PR #XXX"

This invokes the `superpowers:requesting-code-review` skill.

## How It Works

The superpowers plugin dispatches a `superpowers:code-reviewer` subagent that:
- Reviews code against CLAUDE.md requirements
- Detects potential bugs in changes
- Analyzes historical context via git blame
- Provides confidence-scored feedback

## Configuration

**Via Superpowers Plugin**:
- Uses official Anthropic code review implementation
- Confidence threshold: 80 (issues below this score are filtered)
- Multiple specialized review agents for redundancy

## Behavior

**Skips**:
- Closed or draft PRs
- Trivial/automated changes
- Previously reviewed PRs

**Output**: Review comments with references and links to specific code locations
