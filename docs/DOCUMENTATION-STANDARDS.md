# Documentation Standards

**Purpose**: Establish clear documentation standards to prevent drift and maintain consistency across the Mids Hero Web project.

**Last Updated**: 2025-11-13

---

## Core Principles

1. **Single Source of Truth**: Each piece of information should live in exactly one place
2. **Progressive Disclosure**: Start with high-level overviews, link to details
3. **Living Documentation**: Update docs as code changes, not after
4. **Findable**: Clear file naming, logical organization, comprehensive READMEs
5. **Maintainable**: Simple structure, clear ownership, regular reviews

---

## Document Headers

All documentation files must include a standard header:

```markdown
# [Title]

**Purpose**: [One sentence describing what this doc is for]
**Last Updated**: YYYY-MM-DD
**Status**: [Current/Deprecated/Archived]
```

### Optional Header Fields

- **Owner**: For specialized documentation
- **Related Docs**: Links to related documentation
- **Prerequisites**: Required knowledge or setup

---

## File Organization

### Top-Level Structure

```
mids-hero-web/
├── CLAUDE.md                    # AI assistant entry point
├── README.md                    # Project overview
├── docs/                        # All project documentation
│   ├── PROJECT_STATUS.md        # Single source of truth for progress
│   ├── DOCUMENTATION-STANDARDS.md  # This file
│   ├── frontend/                # Frontend-specific docs
│   ├── midsreborn/              # Reference specs
│   └── plans/                   # Implementation plans
├── backend/README.md            # Backend overview
├── frontend/README.md           # Frontend overview
└── .claude/                     # Claude configuration & skills
    ├── skills/                  # Development skills
    ├── workflows/               # GitHub workflows docs
    └── archive/                 # Archived documentation
```

### Documentation Categories

**Project Documentation** (`docs/`):
- Project-wide documentation
- Architecture decisions
- Status tracking
- Implementation plans

**Component Documentation** (`backend/`, `frontend/`):
- Component-specific READMEs
- API documentation
- Component architecture

**AI Documentation** (`.claude/`):
- Claude configuration
- Development skills
- Workflow documentation
- Archived context (not for regular browsing)

---

## Naming Conventions

### File Names

- **READMEs**: Always `README.md` (uppercase)
- **Plans**: `YYYY-MM-DD-descriptive-name.md`
- **Status**: `PROJECT_STATUS.md` (uppercase for canonical docs)
- **Standards**: `UPPERCASE-KEBAB-CASE.md` for policy docs
- **Regular Docs**: `lowercase-kebab-case.md` for everything else

### Directory Names

- `lowercase-kebab-case/` for all directories
- Plurals for collections: `docs/plans/`, `docs/investigations/`
- Singular for categories: `docs/frontend/`, `docs/midsreborn/`

---

## README Standards

Every directory with significant content must have a README.md that includes:

1. **Title**: Clear, descriptive title
2. **Purpose**: What this directory contains
3. **Contents**: List of key files with brief descriptions
4. **Getting Started**: How to use this documentation (if applicable)
5. **Related**: Links to related documentation

### Example README Template

```markdown
# [Directory Name]

**Purpose**: [What this directory contains]

## Contents

- **[file.md]** - [Brief description]
- **[another-file.md]** - [Brief description]

## Getting Started

[How to use this documentation]

## Related Documentation

- [Link to related doc](path/to/doc.md)
```

---

## Markdown Standards

### Headings

- Use ATX-style headings (`#` not `===`)
- One H1 per document
- Hierarchical structure (don't skip levels)
- Blank line before and after headings

### Lists

- Blank line before and after lists
- Consistent bullet style (use `-` for unordered)
- Indent nested lists by 2 spaces

### Code Blocks

- Always specify language: \`\`\`python, \`\`\`bash, \`\`\`typescript
- Use backticks for inline code: \`variable\`
- Use code blocks for multi-line code

### Links

- Use relative paths for internal docs: `[link](../other-doc.md)`
- Use descriptive link text (not "click here")
- Check links remain valid after doc moves

### Status Indicators

Use consistent emoji indicators:
- ✅ Complete/Implemented
- 🚧 In Progress/Partial
- 📋 Planned/Not Started
- ⚠️ Needs Attention/Warning
- ❌ Not Doing/Abandoned

---

## Documentation Lifecycle

### Creating New Documentation

1. **Check Existing**: Search for existing docs on topic
2. **Choose Location**: Follow file organization standards
3. **Use Template**: Include standard header
4. **Link Bidirectionally**: Update related docs to link to new doc
5. **Update Index**: Add to relevant README or index

### Updating Documentation

1. **Update Date**: Change "Last Updated" field
2. **Track Changes**: For major revisions, note what changed
3. **Update Links**: Verify all links still work
4. **Test Instructions**: Verify commands/instructions still work

### Deprecating Documentation

When documentation becomes outdated:

1. **Add Status**: Change status to "Deprecated" in header
2. **Add Notice**: Add deprecation notice with replacement link
3. **Keep Temporarily**: Don't delete immediately (may have backlinks)
4. **Move to Archive**: After 30 days, move to appropriate archive

Example deprecation notice:

```markdown
> **⚠️ DEPRECATED**: This document is outdated. See [new-doc.md](new-doc.md) instead.
```

### Archiving Documentation

1. **Move to Archive**: `.claude/archive/` or `docs/archive/`
2. **Update Links**: Update any remaining links to archived doc
3. **Add README**: Ensure archive directory has README explaining contents

---

## Special Documentation Types

### Implementation Plans

**Location**: `docs/plans/`

**Standards**:
- File name: `YYYY-MM-DD-descriptive-name.md`
- Include plan summary in `docs/plans/PLAN-SUMMARY-[name].md`
- Mark completion status in summary
- Link to plan from PROJECT_STATUS.md

**Required Sections**:
1. Background & Context
2. Objectives
3. Technical Constraints
4. Implementation Tasks
5. Acceptance Criteria

### Status Documentation

**Location**: `docs/PROJECT_STATUS.md`

**Standards**:
- Single source of truth for project progress
- Update weekly at minimum
- Include completion dates for major milestones
- Link to detailed documentation

**Required Sections**:
1. Overall Progress
2. Epic Status (with completion %)
3. Development Workflow
4. Key Metrics
5. Next Steps
6. Technical Decisions
7. Risks & Mitigation

### API Documentation

**Location**: Backend code with OpenAPI/Swagger, overview in `backend/README.md`

**Standards**:
- Auto-generated from code (OpenAPI/Swagger)
- Manual overview in README
- Include example requests/responses
- Document error codes

---

## Review Schedule

### Regular Reviews

**Weekly**: During active development
- Review PROJECT_STATUS.md
- Update any stale documentation
- Check for broken links

**Monthly**: Maintenance phase
- Review all README files
- Archive completed plans
- Update technical decisions

**Quarterly**: Major milestones
- Full documentation audit
- Update CLAUDE.md if workflow changes
- Reorganize if structure isn't working

---

## Anti-Patterns to Avoid

### Don't:

❌ **Duplicate Information**: Copy/paste content across multiple docs
- Instead: Link to single source of truth

❌ **Orphan Documentation**: Create docs without linking from parent README
- Instead: Always update parent README when creating new doc

❌ **Stale Dates**: Leave "Last Updated" unchanged for months
- Instead: Update date when reviewing, even if no changes

❌ **Generic Titles**: "Notes.md", "Misc.md", "Temp.md"
- Instead: Use descriptive, specific titles

❌ **Deep Nesting**: Directories 4+ levels deep
- Instead: Keep max 3 levels; use flat structure when possible

❌ **Ambiguous Status**: Unclear if doc is current or outdated
- Instead: Always include status in header

❌ **Missing Context**: Documentation assumes too much knowledge
- Instead: Include prerequisites, link to background material

---

## AI-Assisted Documentation

### Using Claude Code

**Superpowers Workflow**:
- Claude uses `/superpowers:write-plan` to create implementation plans
- Plans automatically follow standards (stored in `docs/plans/`)
- Claude maintains PROJECT_STATUS.md during development

**Best Practices**:
- Let Claude create new documentation during implementation
- Review generated docs for accuracy
- Claude will update CLAUDE.md when workflow changes

**Documentation Tasks**:
- Tell Claude: "Update PROJECT_STATUS.md" to refresh progress
- Tell Claude: "Create a plan for [feature]" to generate plan
- Tell Claude: "Audit documentation" to check for drift

---

## Version Control

### Git Practices

**Commit Documentation Changes**:
- Commit documentation changes with related code
- Separate doc-only updates into dedicated commits
- Use clear commit messages: `docs: update PROJECT_STATUS for epic 3 completion`

**Pull Requests**:
- Include documentation updates in feature PRs
- Document new features in README files
- Update PROJECT_STATUS.md when completing epics

---

## Enforcement

### Pre-Commit Checks

The project may use hooks to enforce:
- Markdown linting
- Broken link detection
- Required headers

### Code Review

Reviewers should check:
- Documentation updated for code changes
- README files updated for new directories
- Links are valid
- Status indicators are accurate

---

## Questions & Feedback

For questions about these standards or suggestions for improvement:

1. Open a GitHub issue with `[docs]` prefix
2. Propose changes via pull request
3. Discuss in project meetings

---

## Examples

### Good Documentation

✅ Clear purpose and structure:
```markdown
# Frontend Architecture

**Purpose**: Technical design decisions for the Mids Hero Web frontend
**Last Updated**: 2025-11-13
**Status**: Current

## Tech Stack

We chose Next.js 14+ because...
```

✅ Linked hierarchy:
- `docs/frontend/README.md` → Lists all frontend docs
- `docs/frontend/architecture.md` → Links back to README
- `frontend/README.md` → Links to `docs/frontend/`

### Poor Documentation

❌ No context:
```markdown
# Notes

Some stuff about the API.
```

❌ Duplicate content:
- Backend API docs in 3 places
- Each version slightly different
- Unclear which is authoritative

❌ Orphaned file:
- `docs/random-notes.md` exists
- Not linked from any README
- No header, unclear if current

---

## Summary

**Golden Rules**:

1. ✅ Include standard header in every doc
2. ✅ Update "Last Updated" when reviewing
3. ✅ Link bidirectionally (parent ↔ child)
4. ✅ One source of truth per topic
5. ✅ Keep PROJECT_STATUS.md current
6. ✅ Follow naming conventions
7. ✅ Archive don't delete

**When in Doubt**:
- Check existing docs for examples
- Ask Claude for guidance
- Prefer simple structure over complex
- Link rather than duplicate

---

_These standards were established during documentation housekeeping on 2025-11-13 to prevent future drift._
