# Code Review Command

Automatically review pull requests using multiple specialized agents.

## Usage

Run: `/code-review` in any PR context

## Configuration

**Confidence Threshold**: 80 (issues below this score are filtered)

**Agent Types**:
- CLAUDE.md compliance auditors (2x for redundancy)
- Bug detection agent (focuses on changes only)
- Historical context analyzer (uses git blame)

## Behavior

**Skips**:
- Closed or draft PRs
- Trivial/automated changes
- Previously reviewed PRs

**Output**: Review comments with CLAUDE.md references and GitHub blob links
