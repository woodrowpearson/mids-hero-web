# GitHub Workflows Documentation

This directory contains GitHub Actions workflows that automate CI/CD, code review, and documentation management for the Mids Hero Web project.

## 📋 Active Workflows

### 🔄 ci.yml - Continuous Integration
**Triggers**: Push to main/develop, Pull requests

**Purpose**: Complete CI/CD pipeline ensuring code quality and tests pass

**Jobs**:
- **backend-lint**: Python linting with ruff, black, isort, mypy
- **frontend-lint**: TypeScript/React linting with ESLint
- **backend-test**: pytest with PostgreSQL integration
- **frontend-test**: React component testing
- **security**: Trivy vulnerability scanning
- **just-commands**: Validates just command functionality
- **docker-build**: Docker image build validation (currently disabled)

**Requirements**: Uses uv for Python, Node.js 18, PostgreSQL 15

---

### 🤖 claude-unified.yml - AI Code Review & Interaction
**Triggers**: Pull requests, Issue comments containing "@claude"

**Purpose**: Unified Claude integration for code review and interactive assistance

**Features**:
- **PR Auto-Review**: Reviews code quality, City of Heroes mechanics, security issues
- **Interactive Comments**: 
  - `@claude [question]` - Ask Claude about the codebase
  - `implement doc suggestions` - Apply documentation updates
  - Approval keywords - Apply suggested changes
- Dynamic timeout based on PR size
- Context-aware responses about Epic progress

**Configuration**: Requires `ANTHROPIC_API_KEY` secret

---

### 🏥 context-health-check.yml - Context System Monitor
**Triggers**: Every 6 hours, push to main/develop, PRs, manual

**Purpose**: Ensures Claude context system remains healthy and performant

**Checks**:
- CLAUDE.md token count (<5K limit)
- Context file sizes and structure
- Required directories and files exist
- Command compliance (uv/fd/trash usage)
- Markdown file token analysis

**Output**: GitHub Step Summary with health report

---

### 📚 doc-management.yml - Unified Documentation Management
**Triggers**: Pull requests, code pushes, weekly schedule, manual dispatch

**Purpose**: Combined documentation review and auto-synchronization

**Operation Modes**:
- **Review Mode** (PRs): Analyzes documentation impact, suggests updates
- **Sync Mode** (pushes): Auto-updates docs based on code changes
- **Full Mode** (schedule/manual): Complete documentation validation

**Smart Detection**:
- Workflow changes → Updates .github/README.md files
- Context changes → Updates .claude/README.md  
- API changes → Updates API documentation
- Model changes → Updates database docs
- Command changes → Updates quick reference

**Features**:
- Unified mode detection based on trigger
- Token limit validation with warnings
- Intelligent change analysis
- Weekly full synchronization
- Dynamic timeouts based on scope

---

### 🔧 update-claude-docs.yml - Claude Documentation Updates
**Triggers**: Changes to Python/TypeScript files, Claude docs, manual

**Purpose**: Updates Claude-specific documentation and monitors token usage

**Features**:
- Updates timestamps in documentation
- Checks token limits with warnings
- Creates PRs for documentation updates
- Reports token limit issues

---

### ⚙️ dataexporter-tests.yml - DataExporter Module Tests
**Triggers**: Changes to DataExporter module

**Purpose**: Cross-platform testing of the DataExporter .NET module

**Platforms**: Ubuntu, Windows, macOS
**Requirements**: .NET 9.0

---

## 🔧 Configuration

### Required Secrets
- `ANTHROPIC_API_KEY` - For all Claude-powered features
- `CODECOV_TOKEN` - For code coverage reporting (optional)

### Permissions
All workflows require appropriate permissions:
- `contents: read/write` - For file operations
- `pull-requests: write` - For PR comments
- `issues: write` - For issue comments

### Environment Variables
- `PYTHON_VERSION: "3.11"`
- `NODE_VERSION: "18"`

## 📊 Workflow Interactions

```mermaid
graph LR
    PR[Pull Request] --> CI[CI Tests]
    PR --> CU[Claude Unified]
    PR --> DM[Doc Management - Review]
    
    Code[Code Push] --> CI
    Code --> DM2[Doc Management - Sync]
    Code --> CHC[Context Health Check]
    
    Comment[@claude] --> CU
    
    Schedule[Cron Schedule] --> CHC
    Schedule --> DM3[Doc Management - Full]
    
    Manual[Manual Trigger] --> DM4[Doc Management]
    Manual --> UCD[Update Claude Docs]
```

## 💡 Usage Tips

### For Developers

1. **PR Workflow**:
   - Create PR → Automatic CI + Claude review
   - Address feedback → Push changes
   - Get approval → Merge

2. **Getting Help**:
   ```
   @claude How do I implement enhancement calculations?
   @claude What's the best way to structure this API endpoint?
   ```

3. **Documentation**:
   - Code changes trigger automatic doc suggestions
   - Weekly full sync ensures consistency
   - Token warnings prevent context overflow

### For Maintainers

1. **Monitoring**:
   - Check Actions tab for workflow status
   - Review context health reports
   - Monitor token usage warnings

2. **Manual Controls**:
   - Force documentation sync from Actions tab
   - Trigger specific workflows as needed
   - Review and merge doc update PRs

## 🚨 Troubleshooting

### Common Issues

**Workflow not running**:
- Check trigger conditions match
- Verify secrets are configured
- Review workflow permissions

**Claude not responding**:
- Verify ANTHROPIC_API_KEY is valid
- Check API rate limits
- Review workflow logs

**Documentation not updating**:
- Check change detection patterns
- Verify file paths in workflow
- Run manual sync if needed

**Token limit warnings**:
- Review flagged files
- Refactor large documentation
- Update token limits if necessary

### Debug Commands

```bash
# Check workflow syntax
actionlint .github/workflows/*.yml

# Test locally with act
act pull_request -W .github/workflows/ci.yml

# View workflow runs
gh run list --workflow=ci.yml
```

## 🔐 Security Considerations

1. **Secrets Management**:
   - Never commit API keys
   - Use GitHub secrets for sensitive data
   - Rotate keys periodically

2. **Permissions**:
   - Use minimal required permissions
   - Review third-party action permissions
   - Audit workflow access regularly

3. **Code Execution**:
   - Validate inputs in workflows
   - Use specific action versions
   - Review automated changes before merging

## 📈 Performance Optimization

1. **Caching**:
   - Dependencies cached for faster runs
   - Docker layer caching enabled
   - Node modules cached by lock file

2. **Parallelization**:
   - Jobs run in parallel where possible
   - Matrix builds for cross-platform testing
   - Independent checks don't block each other

3. **Conditional Execution**:
   - Skip unnecessary jobs based on changes
   - Smart change detection for targeted updates
   - Early exit on non-relevant changes

## 🔄 Maintenance

### Weekly Tasks
- Review context health reports
- Check for workflow updates
- Monitor token usage trends

### Monthly Tasks
- Audit workflow permissions
- Update action versions
- Review and optimize performance

### Quarterly Tasks
- Full workflow review
- Security audit
- Performance baseline update

---

*Last updated: 2025-01-27*