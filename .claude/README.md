# Claude Context System

This directory contains the Claude Code context management system for the Mids Hero Web project.

## 📁 Directory Structure

- **`agents/`** - Native Claude Code sub-agents for specialized tasks
- **`docs/`** - All project documentation
- **`hooks/`** - Active Claude Code hooks for automation
- **`modules/`** - Task-based context modules (database, api, frontend, etc.)
- **`sessions/`** - Session data and summaries
- **`state/`** - Runtime state including progress tracking and logs
- **`workflows/`** - Development workflow guides

## 🔧 Configuration Files

- **`settings.json`** - Claude Code configuration and permissions
- **`context-map.json`** - Context loading rules and thresholds
- **`CLEANUP_LOG.md`** - Recent directory reorganization details

## 📖 How It Works

1. **Progressive Loading**: Claude loads only the context needed for your declared task
2. **Token Management**: Automatic warnings when approaching limits
3. **Activity Tracking**: All actions logged for session continuity
4. **Native Sub-Agents**: Specialized agents for database, frontend, API work

## 🚀 Quick Start

Tell Claude what you're working on:
- "I need to work on database migrations"
- "Help me import I12 power data"
- "I want to build API endpoints"

Claude will automatically load the appropriate modules and tools for your task.

## 📊 Context Health

Run `just context-validate` to check:
- File sizes and token counts
- Required files presence
- Module organization
- Loading scenarios

## 🔗 Related Documentation

- Main guide: `/CLAUDE.md`
- Development workflow: `.claude/docs/development-workflow.md`
- Session management: `.claude/docs/session-management.md`