# GitHub Actions vs Claude Code Agents: Complete Guide
Last Updated: 2025-08-25

## Executive Summary

This guide clarifies the distinction between **GitHub Actions workflows** (automated CI/CD processes) and **Claude Code native sub-agents** (interactive development assistants). Understanding this separation prevents confusion and ensures efficient use of both systems.

## 🎯 Quick Decision Matrix

| Task Type | Use This System | Why |
|-----------|----------------|-----|
| Code review on PR | GitHub Action (`claude-auto-review.yml`) | Automated, no user interaction needed |
| Implement a feature | Claude Code Agent (`Task` tool) | Interactive, requires context and iteration |
| Run tests on push | GitHub Action (`ci.yml`) | Automated validation, deterministic |
| Debug complex issue | Claude Code Agent | Requires analysis and exploration |
| Update docs on merge | GitHub Action (`doc-auto-sync.yml`) | Automated, rule-based |
| Design new API | Claude Code Agent (`backend-specialist`) | Creative work, requires decisions |
| Check token limits | GitHub Action (`context-health-check.yml`) | Scheduled monitoring, no interaction |
| Fix failing tests | Claude Code Agent (`testing-specialist`) | Requires code changes and debugging |

## 🏗️ System Architecture

### GitHub Actions Workflows
**Location**: `.github/workflows/`
**Execution**: GitHub's cloud infrastructure
**Trigger**: Events (push, PR, schedule, manual)
**Context**: Repository state at trigger time
**Interaction**: None (fire-and-forget)

### Claude Code Native Sub-Agents
**Location**: In-memory (invoked via `Task` tool)
**Execution**: Local Claude Code session
**Trigger**: User command in terminal
**Context**: Current working directory + loaded files
**Interaction**: Real-time with user

## 📋 Complete Workflow Inventory

### Claude-Integrated GitHub Actions

#### 1. claude-auto-review.yml
- **Purpose**: Automated PR code review
- **Triggers**: PR opened/synchronized
- **Claude Usage**: Reviews code quality, security, game mechanics
- **Key Features**:
  - 15-minute timeout
  - 5 turn limit
  - City of Heroes domain validation
  - Inline PR comments
- **When NOT to use agents**: This runs automatically, no manual intervention needed

#### 2. claude-code-integration.yml
- **Purpose**: Interactive PR/issue assistant
- **Triggers**: Comments with `@claude`, `implement doc suggestions`, approval keywords
- **Claude Usage**: Responds to questions, implements approved changes
- **Matrix Jobs**:
  - Question Response (10 min timeout)
  - Documentation Implementation (15 min)
  - Approval Processing (20 min)
- **When NOT to use agents**: For PR-specific queries that need repository context

#### 3. doc-review.yml
- **Purpose**: Documentation impact analysis
- **Triggers**: PR opened/synchronized
- **Claude Usage**: Analyzes code changes, suggests doc updates
- **Key Features**:
  - Changed file detection
  - Token limit validation
  - Structured feedback format
- **When NOT to use agents**: Automated on every PR

#### 4. doc-auto-sync.yml
- **Purpose**: Automatic documentation synchronization
- **Triggers**: Code push, weekly schedule, manual
- **Claude Usage**: Updates docs based on code changes
- **Smart Detection**:
  - Workflow changes → `.github/README.md`
  - API changes → API docs
  - Database changes → Schema docs
  - Context changes → `.claude/README.md`
- **When NOT to use agents**: Rule-based updates, no creativity needed

#### 5. update-claude-docs.yml
- **Purpose**: Claude documentation maintenance
- **Triggers**: Code changes, manual
- **Claude Usage**: None (Python script-based)
- **Features**: Token counting, timestamp updates
- **When NOT to use agents**: Simple file updates

#### 6. context-health-check.yml
- **Purpose**: Monitor context system health
- **Triggers**: Every 6 hours, push, PR
- **Claude Usage**: None (validation scripts)
- **Checks**: Token limits, file structure, command compliance
- **When NOT to use agents**: Automated monitoring

### Non-Claude GitHub Actions

- **ci.yml**: Standard CI pipeline (tests, linting, security)
- **dataexporter-tests.yml**: Cross-platform .NET testing

## 🤖 Claude Code Native Sub-Agents

### Available Specialists

| Agent | Primary Use | Example Commands |
|-------|------------|------------------|
| `backend-specialist` | API development | "Create a new endpoint for power calculations" |
| `frontend-specialist` | React components | "Build a character stats display component" |
| `database-specialist` | Schema & migrations | "Add a table for build templates" |
| `import-specialist` | Game data parsing | "Import I12 power data file" |
| `testing-specialist` | Test creation/fixing | "Write tests for the enhancement calculator" |
| `calculation-specialist` | Game mechanics | "Implement damage formula with enhancements" |
| `devops-specialist` | Deploy & infrastructure | "Set up Docker configuration" |
| `documentation-specialist` | Doc updates | "Update API documentation" |

### When to Use Native Agents

**USE agents when:**
- Writing new code
- Debugging issues
- Implementing features
- Exploring the codebase
- Making architectural decisions
- Refactoring existing code
- Creating tests interactively

**DON'T use agents when:**
- Running automated checks
- Responding to PR events
- Scheduled maintenance
- Deterministic updates
- Simple validations

## 🔄 Interaction Patterns

### Pattern 1: PR Development Flow
```
1. Developer works locally → Uses Claude Code agents
2. Developer pushes code → GitHub Action (CI) runs
3. Developer opens PR → GitHub Actions (review + doc check)
4. Reviewer has question → Comments with @claude
5. Approved for merge → GitHub Action (doc sync)
```

### Pattern 2: Feature Implementation
```
1. User: "Help me implement power calculations"
   → Claude Code: Uses calculation-specialist agent
2. Agent writes code, creates tests
3. User: "just test"
   → Local test execution
4. User pushes to branch
   → GitHub Actions validate
```

### Pattern 3: Documentation Update
```
Automatic (code change):
- Push triggers doc-auto-sync.yml
- Claude analyzes changes
- Updates relevant docs
- Creates PR if needed

Manual (user request):
- User: "Update the API documentation"
- Claude Code: Uses documentation-specialist
- Makes changes interactively
- User reviews and commits
```

## 🚫 Common Confusions to Avoid

### Confusion 1: "Claude should run the GitHub Action"
**Wrong**: "Claude, trigger the documentation sync workflow"
**Right**: GitHub Actions run automatically or via GitHub UI/API
**Solution**: Use `gh workflow run` command if manual trigger needed

### Confusion 2: "GitHub Action should write code"
**Wrong**: Expecting claude-auto-review.yml to fix issues it finds
**Right**: GitHub Actions review/validate; agents implement fixes
**Solution**: Use Claude Code agents to fix issues found by Actions

### Confusion 3: "Agent should monitor continuously"
**Wrong**: "Use the testing-specialist to watch for test failures"
**Right**: GitHub Actions monitor; agents fix when notified
**Solution**: Let context-health-check.yml monitor, use agents to fix

### Confusion 4: "Both systems for same task"
**Wrong**: Running both GitHub Action and agent for documentation
**Right**: Choose based on trigger and interaction needs
**Solution**: Automated = Action, Interactive = Agent

## 📊 Context Management Strategies

### GitHub Actions Context
- **Scope**: Full repository at trigger commit
- **Limits**: Controlled by `timeout_minutes` and `max_turns`
- **Optimization**: 
  - Use file filters to reduce scope
  - Cache frequently used prompts
  - Limit turn count for efficiency

### Claude Code Agent Context
- **Scope**: Loaded based on task declaration
- **Limits**: Token warnings at 90K
- **Optimization**:
  - Declare specific task to load minimal context
  - Use `/clear` between different tasks
  - Let native sub-agents manage their own context

## 🔧 Optimization Recommendations

### 1. Reduce Workflow Redundancy
**Current Issue**: Multiple workflows reading similar files
**Solution**: 
- Consolidate doc-review.yml and doc-auto-sync.yml triggers
- Share change detection logic via reusable workflow

### 2. Optimize Claude Interactions
**Current Issue**: Fixed timeouts regardless of task complexity
**Solution**:
```yaml
timeout_minutes: ${{ 
  github.event.pull_request.changed_files < 10 && '5' ||
  github.event.pull_request.changed_files < 50 && '10' ||
  '15'
}}
```

### 3. Improve Trigger Specificity
**Current Issue**: Workflows run on all file changes
**Solution**:
```yaml
on:
  push:
    paths:
      - 'backend/**/*.py'
      - '!backend/**/*_test.py'  # Exclude test files
      - '!backend/**/__pycache__/**'  # Exclude cache
```

### 4. Enable Prompt Caching
**Current Issue**: Repeated similar prompts without caching
**Solution**: Add to Claude action steps:
```yaml
cache_prompts: true
cache_duration: 3600  # 1 hour
```

### 5. Separate Concerns Clearly
**Current Implementation**: Some overlap between systems
**Recommended Separation**:

| Task Category | GitHub Action | Claude Code Agent |
|--------------|---------------|-------------------|
| Validation | ✅ All checks | ❌ |
| Code Generation | ❌ | ✅ All creation |
| Review | ✅ Automated | ✅ On-demand |
| Monitoring | ✅ All metrics | ❌ |
| Debugging | ❌ | ✅ All investigation |
| Documentation | ✅ Rule-based | ✅ Creative/complex |

## 📈 Performance Metrics

### Current Performance
- **claude-auto-review.yml**: ~5-15 min per PR
- **doc-auto-sync.yml**: ~3-10 min per sync
- **claude-code-integration.yml**: ~2-5 min per query

### Optimization Targets
- Reduce average review time by 30%
- Decrease false positive rate to <5%
- Improve context relevance score

## 🔐 Security Considerations

### GitHub Actions
- Uses repository secrets (`ANTHROPIC_API_KEY`)
- Limited to repository scope
- Audit trail via Action logs

### Claude Code Agents
- Uses local environment API key
- Access to full file system
- Interactive approval for changes

## 📚 Best Practices

### For GitHub Actions
1. **Keep prompts focused** - Single responsibility per workflow
2. **Use matrix strategies** - Avoid duplicate job definitions
3. **Set reasonable timeouts** - Prevent hanging workflows
4. **Filter file changes** - Reduce unnecessary triggers
5. **Cache when possible** - Improve performance

### For Claude Code Agents
1. **Declare specific tasks** - Load minimal context
2. **Use specialists** - Leverage domain expertise
3. **Clear between tasks** - Prevent context pollution
4. **Review before committing** - Agents suggest, users decide
5. **Update progress** - Use TodoWrite for tracking

## 🚀 Migration Path to Modern Claude GitHub App

### Phase 1: Assessment (Current)
- Document existing workflows ✅
- Identify optimization opportunities ✅
- Define clear boundaries ✅

### Phase 2: Preparation (Next)
- Install Claude GitHub App via `/install-github-app`
- Update workflow configurations
- Test in feature branches

### Phase 3: Migration (Future)
- Gradually update workflows
- Enable new features (MCP, caching)
- Monitor and optimize

## 📋 Quick Reference Commands

### Check Workflow Status
```bash
# List recent workflow runs
gh run list

# View specific workflow
gh workflow view claude-auto-review.yml

# Trigger manual workflow
gh workflow run doc-auto-sync.yml
```

### Debug Workflow Issues
```bash
# View workflow logs
gh run view <run-id> --log

# Download artifacts
gh run download <run-id>

# Cancel stuck workflow  
gh run cancel <run-id>
```

### Local Testing
```bash
# Validate workflow syntax
actionlint .github/workflows/*.yml

# Test locally with act
act pull_request -W .github/workflows/claude-auto-review.yml
```

## 🎯 Decision Flowchart

```
Start
  ↓
Is it triggered by an event?
  ├─ Yes → Is it deterministic/rule-based?
  │         ├─ Yes → Use GitHub Action
  │         └─ No → Requires creativity?
  │                  ├─ Yes → Use Claude Code Agent
  │                  └─ No → Use GitHub Action
  └─ No → Requires user interaction?
          ├─ Yes → Use Claude Code Agent
          └─ No → Can it be scheduled?
                  ├─ Yes → Use GitHub Action
                  └─ No → Use Claude Code Agent
```

## 📝 Summary

**GitHub Actions** excel at:
- Automated, event-driven tasks
- Deterministic validation
- Scheduled monitoring
- Repository-wide operations

**Claude Code Agents** excel at:
- Interactive development
- Creative problem-solving
- Complex debugging
- Contextual assistance

By understanding these boundaries and using each system for its strengths, we achieve:
- Better performance
- Clearer responsibilities  
- Reduced confusion
- Improved developer experience

---

*For workflow implementation details, see [.github/workflows/README.md](../../.github/workflows/README.md)*
*For agent documentation, see [.claude/agents/](../agents/)*