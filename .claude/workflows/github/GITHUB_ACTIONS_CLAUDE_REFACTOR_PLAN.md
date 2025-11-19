# GitHub Actions Claude Refactoring Plan
Last Updated: 2025-11-19 20:27:56 UTC

## Overview

This document outlines a comprehensive plan for reviewing and refactoring GitHub Actions workflows that use Claude/Anthropic's Claude Code Action. The goal is to modernize these workflows to leverage the latest Claude GitHub App features while improving maintainability and performance.

## Current State Analysis

### Workflows Using Claude

1. **claude-auto-review.yml**
   - Purpose: Automated PR review on opened/synchronized PRs
   - Uses: `anthropics/claude-code-action@beta`
   - Key Features: Code quality analysis, bug detection, security review
   - Status: Using direct_prompt approach

2. **claude-code-integration.yml**
   - Purpose: Responds to @claude mentions and documentation automation
   - Uses: `anthropics/claude-code-action@beta`
   - Key Features: Interactive Q&A, automated doc updates, approval processing
   - Status: Multiple jobs with different triggers

3. **doc-review.yml**
   - Purpose: Reviews documentation impact of code changes
   - Uses: `anthropics/claude-code-action@beta`
   - Key Features: Analyzes changed files, suggests doc updates
   - Status: PR-triggered with file filtering

4. **doc-auto-sync.yml**
   - Purpose: Automatically synchronizes documentation
   - Uses: `anthropics/claude-code-action@beta`
   - Key Features: Full sync, token limit validation, scheduled runs
   - Status: Complex multi-job workflow

### Workflows NOT Using Claude

- **ci.yml** - Standard CI/CD pipeline
- **dataexporter-tests.yml** - Specific test suite
- **context-health-check.yml** - Claude context validation
- **update-claude-docs.yml** - Python-based doc updates

## New Claude GitHub App Features (2025)

### Key Improvements

1. **Native GitHub App Integration**
   - Direct installation via `/install-github-app` command
   - Better authentication and permissions management
   - Improved security model

2. **Enhanced Capabilities**
   - Background tasks via GitHub Actions
   - Native IDE integrations (VS Code, JetBrains)
   - Code execution tool support
   - MCP (Model Context Protocol) connector
   - Files API access
   - Prompt caching (up to 1 hour)

3. **Configuration Options**
   - Tag Mode vs Agent Mode execution
   - Custom MCP servers support
   - Path-based and author-based filtering
   - Headless mode for CI/CD contexts

4. **SDK Availability**
   - Claude Code SDK for custom integrations
   - Programmatic access to agent capabilities
   - Extensibility for custom workflows

## Refactoring Strategy

### Phase 1: Assessment and Planning

1. **Evaluate Current Workflows**
   - Identify redundancies and inefficiencies
   - Document current pain points
   - Measure performance metrics

2. **Define Requirements**
   - Determine which features need migration
   - Identify new features to adopt
   - Set performance targets

### Phase 2: Workflow-Specific Refactoring Plans

#### claude-auto-review.yml Refactoring

**Current Issues:**
- Long timeout (30 minutes)
- Commented out allowed_tools
- Limited to direct_prompt approach

**Proposed Changes:**
```yaml
# Modernized approach
- name: Automatic PR Review
  uses: anthropics/claude-code-action@v1  # Update to stable version
  with:
    mode: agent  # Use agent mode for automated reviews
    anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
    github_token: ${{ secrets.GITHUB_TOKEN }}
    timeout_minutes: "15"  # Reduced timeout
    cache_prompts: true  # Enable prompt caching
    mcp_servers:  # Enable MCP for better context
      - github
    review_config:
      focus_areas:
        - code_quality
        - security
        - performance
        - test_coverage
      respect_claude_md: true
      inline_comments: true
```

**Benefits:**
- Faster execution with prompt caching
- Better context awareness via MCP
- More structured configuration

#### claude-code-integration.yml Refactoring

**Current Issues:**
- Multiple jobs with similar setup
- Complex trigger conditions
- Redundant checkout steps

**Proposed Changes:**
```yaml
# Consolidated job with matrix strategy
jobs:
  claude-handler:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        task:
          - { trigger: '@claude', mode: 'respond' }
          - { trigger: 'implement doc suggestions', mode: 'doc-update' }
          - { trigger: 'approved|approve|implement this', mode: 'approval' }
    steps:
      - uses: actions/checkout@v4
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          ref: ${{ github.event.issue.pull_request.head.ref }}

      - name: Claude Task Handler
        uses: anthropics/claude-code-action@v1
        with:
          mode: agent
          task_type: ${{ matrix.task.mode }}
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          github_token: ${{ secrets.GITHUB_TOKEN }}
          mcp_servers:
            - github
            - filesystem
          headless: ${{ matrix.task.mode != 'respond' }}
```

**Benefits:**
- DRY principle applied
- Easier maintenance
- Better resource utilization

#### doc-review.yml Refactoring

**Current Issues:**
- Manual file change detection
- Limited to PR comments

**Proposed Changes:**
```yaml
# Enhanced documentation review
- name: Documentation Impact Analysis
  uses: anthropics/claude-code-action@v1
  with:
    mode: agent
    anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
    github_token: ${{ secrets.GITHUB_TOKEN }}
    task: documentation_review
    auto_detect_changes: true  # Let Claude detect changes
    output_format: structured  # Get structured output
    review_config:
      check_references: true
      validate_links: true
      suggest_updates: true
      respect_token_limits: true
```

**Benefits:**
- Automatic change detection
- Structured output for better parsing
- More comprehensive checks

#### doc-auto-sync.yml Refactoring

**Current Issues:**
- Complex multi-step process
- Manual token counting
- Separate Python scripts

**Proposed Changes:**
```yaml
# Simplified sync with Claude SDK
- name: Documentation Sync
  uses: anthropics/claude-code-action@v1
  with:
    mode: agent
    anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
    github_token: ${{ secrets.GITHUB_TOKEN }}
    task: documentation_sync
    headless: true
    sync_config:
      auto_detect_impact: true
      respect_token_limits: true
      create_pr_on_changes: true
      schedule_aware: ${{ github.event_name == 'schedule' }}
    mcp_servers:
      - github
      - filesystem
```

**Benefits:**
- Built-in token management
- Simplified workflow
- Better error handling

### Phase 3: Implementation Steps

1. **Setup and Configuration**
   - Install Claude GitHub App via `/install-github-app`
   - Configure repository secrets and permissions
   - Update CLAUDE.md with workflow guidelines

2. **Gradual Migration**
   - Start with non-critical workflows (doc-review.yml)
   - Test in feature branches first
   - Monitor performance and accuracy
   - Migrate critical workflows after validation

3. **Optimization**
   - Enable prompt caching where applicable
   - Configure MCP servers for better context
   - Fine-tune timeouts and resource limits

## Test Plan

### Unit Testing

1. **Workflow Syntax Validation**
   ```bash
   # Validate YAML syntax
   yamllint .github/workflows/*.yml

   # Validate GitHub Actions syntax
   act --list  # Using act tool for local testing
   ```

2. **Mock Testing**
   - Use act to run workflows locally
   - Test with mock PRs and issues
   - Validate trigger conditions

### Integration Testing

1. **Feature Branch Testing**
   - Create test PRs with various scenarios
   - Test @claude mentions
   - Test automated reviews
   - Test documentation sync

2. **Performance Testing**
   - Measure execution times
   - Monitor API usage
   - Check for rate limiting issues

3. **Edge Case Testing**
   - Large PRs (>100 files)
   - Complex merge conflicts
   - Token limit scenarios
   - Concurrent workflow runs

### Acceptance Criteria

1. **Functionality**
   - All existing features work as expected
   - New features are properly integrated
   - No regression in capabilities

2. **Performance**
   - 50% reduction in average execution time
   - Improved accuracy in reviews
   - Better resource utilization

3. **Reliability**
   - 99% success rate for triggered workflows
   - Proper error handling and recovery
   - Clear error messages

## Migration Checklist

### Pre-Migration
- [ ] Backup current workflow files
- [ ] Document current behavior and metrics
- [ ] Install Claude GitHub App
- [ ] Configure new secrets (if needed)
- [ ] Update CLAUDE.md with new guidelines
- [ ] Create feature branch for migration

### During Migration
- [ ] Refactor workflows one by one
- [ ] Test each workflow in isolation
- [ ] Update documentation
- [ ] Monitor for issues
- [ ] Collect performance metrics

### Post-Migration
- [ ] Validate all workflows functioning
- [ ] Compare metrics with baseline
- [ ] Update team documentation
- [ ] Remove old workflow versions
- [ ] Archive migration artifacts

## Rollback Plan

### Immediate Rollback

If critical issues are discovered:

1. **Revert Workflow Files**
   ```bash
   git revert <migration-commit>
   git push
   ```

2. **Restore Secrets**
   - Keep old API keys active during migration
   - Switch back if needed

3. **Communication**
   - Notify team of rollback
   - Document issues encountered
   - Plan remediation

### Gradual Rollback

For non-critical issues:

1. **Selective Reversion**
   - Revert only affected workflows
   - Keep working workflows on new version

2. **Hybrid Approach**
   - Run old and new workflows in parallel
   - Compare results
   - Fix issues incrementally

## Success Metrics

### Quantitative Metrics

1. **Performance**
   - Workflow execution time: -50%
   - API token usage: -30%
   - Success rate: >99%

2. **Efficiency**
   - Lines of YAML code: -40%
   - Maintenance time: -60%
   - False positive rate: <5%

### Qualitative Metrics

1. **Developer Experience**
   - Easier to understand workflows
   - Better error messages
   - More predictable behavior

2. **Code Quality**
   - More accurate reviews
   - Better documentation sync
   - Improved context awareness

## Timeline

### Week 1: Preparation
- Day 1-2: Assessment and planning
- Day 3-4: Environment setup
- Day 5: Team alignment

### Week 2: Implementation
- Day 1-2: Refactor doc-review.yml
- Day 3-4: Refactor claude-auto-review.yml
- Day 5: Testing and validation

### Week 3: Completion
- Day 1-2: Refactor remaining workflows
- Day 3-4: Integration testing
- Day 5: Documentation and handoff

## Risks and Mitigations

### Technical Risks

1. **API Breaking Changes**
   - Risk: Claude API changes during migration
   - Mitigation: Pin to specific version, monitor changelog

2. **GitHub Permissions**
   - Risk: New app requires different permissions
   - Mitigation: Test in sandbox first, document requirements

3. **Rate Limiting**
   - Risk: Increased usage hits limits
   - Mitigation: Implement caching, optimize prompts

### Operational Risks

1. **Team Disruption**
   - Risk: Workflows fail during business hours
   - Mitigation: Deploy during off-hours, have rollback ready

2. **Knowledge Gap**
   - Risk: Team unfamiliar with new features
   - Mitigation: Create documentation, provide training

## Conclusion

This refactoring plan provides a structured approach to modernizing Claude-based GitHub Actions workflows. By leveraging new features like the native GitHub App, MCP servers, and prompt caching, we can achieve significant improvements in performance, maintainability, and functionality.

The phased approach ensures minimal disruption while allowing for proper testing and validation at each step. With clear success metrics and a robust rollback plan, this migration can be executed safely and effectively.
