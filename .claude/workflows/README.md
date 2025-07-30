# Claude Workflows vs GitHub Workflows

This directory contains **Claude-specific development workflows** - guides and processes for developers working with Claude Code on the Mids Hero Web project.

## 📁 Directory Purpose

- **`.claude/workflows/`** - Human-readable workflow guides for development tasks
  - `daily.md` - Daily development workflow with Claude
  - `testing.md` - Testing strategies and processes
  - `troubleshooting.md` - Common issues and solutions

- **`.github/workflows/`** - GitHub Actions CI/CD automation
  - YAML files defining automated pipelines
  - PR checks, tests, deployments
  - Not for human consumption

## 🎯 Key Difference

- **Claude Workflows**: Instructions for developers using Claude Code
- **GitHub Workflows**: Automated scripts that run on GitHub's servers

## 📖 Usage

When Claude loads context based on your task, it may include relevant workflow guides from this directory to help you follow best practices for the project.