
Review the completed work using Claude Code's built-in code-reviewer subagent.

Use the Task tool with subagent_type="superpowers:code-reviewer" to dispatch a specialized code review agent that will:
- Review implementation against the original plan and requirements
- Check for bugs, edge cases, and code quality issues
- Verify coding standards and best practices
- Provide actionable feedback with specific file references

Target: $ARGUMENTS

If no arguments provided, review the most recent changes in the current working directory.
