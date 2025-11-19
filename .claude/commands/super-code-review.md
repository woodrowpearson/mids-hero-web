Last Updated: 2025-11-19 20:27:56 UTC

Use the superpowers plugin's requesting-code-review skill to perform a comprehensive code review.

Invoke the Skill tool with skill="superpowers:requesting-code-review" to dispatch the superpowers code-reviewer subagent that:
- Reviews code against CLAUDE.md requirements and project standards
- Detects potential bugs and edge cases in changes
- Analyzes historical context via git blame
- Provides confidence-scored feedback (threshold: 80)
- Skips closed, draft, or previously reviewed PRs

Target: $ARGUMENTS

If no arguments provided, review the current branch's changes against the main branch.
