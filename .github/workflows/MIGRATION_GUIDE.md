# Workflow Architecture Migration Guide

This guide documents the consolidation of GitHub workflows for the Mids Hero Web project.

## 🔄 Migration Overview

### Workflows to Remove
The following redundant workflows should be removed after verifying the new consolidated workflows are working:

1. **ci.yml** → Replaced by `ci-complete.yml`
2. **dataexporter-tests.yml** → Integrated into `ci-complete.yml`
3. **doc-synthesis.yml** → Replaced by `doc-auto-sync.yml`
4. **doc-synthesis-auto.yml** → Replaced by `doc-auto-sync.yml`
5. **doc-synthesis-simple.yml** → Replaced by `doc-auto-sync.yml`
6. **update-claude-docs.yml** → Integrated into `doc-auto-sync.yml`
7. **claude-auto-review.yml** → Replaced by `claude-pr-assistant.yml`
8. **claude-code-integration.yml** → Integrated into `claude-pr-assistant.yml`
9. **context-health-check.yml** → Replaced by `context-guardian.yml`

### New Consolidated Workflows

| New Workflow | Consolidates | Purpose |
|--------------|--------------|---------|
| `ci-complete.yml` | ci.yml, dataexporter-tests.yml | Unified CI/CD pipeline |
| `claude-pr-assistant.yml` | claude-auto-review.yml, claude-code-integration.yml | AI-powered PR assistance |
| `doc-auto-sync.yml` | All doc-synthesis*.yml, update-claude-docs.yml | Documentation synchronization |
| `context-guardian.yml` | context-health-check.yml | Enhanced context monitoring |

## 📋 Migration Steps

### 1. Test New Workflows (Complete this first!)

```bash
# Create a test branch
git checkout -b test/workflow-migration

# Push to trigger workflows
git push -u origin test/workflow-migration

# Create a test PR to verify:
# - ci-complete.yml runs all tests
# - claude-pr-assistant.yml provides review
# - doc-auto-sync.yml suggests updates
# - context-guardian.yml checks health
```

### 2. Update Repository Settings

Ensure these secrets are configured:
- `ANTHROPIC_API_KEY` - Required for Claude features
- `CODECOV_TOKEN` - Optional but recommended

### 3. Remove Old Workflows

After confirming new workflows are functioning:

```bash
# Remove old workflow files
git rm .github/workflows/ci.yml
git rm .github/workflows/dataexporter-tests.yml
git rm .github/workflows/doc-synthesis.yml
git rm .github/workflows/doc-synthesis-auto.yml
git rm .github/workflows/doc-synthesis-simple.yml
git rm .github/workflows/update-claude-docs.yml
git rm .github/workflows/claude-auto-review.yml
git rm .github/workflows/claude-code-integration.yml
git rm .github/workflows/context-health-check.yml

# Also remove this migration guide after completion
git rm .github/workflows/MIGRATION_GUIDE.md

# Commit the cleanup
git commit -m "chore: remove deprecated workflows after consolidation

- Removed 9 redundant workflows
- Consolidated into 4 purpose-driven workflows
- See .github/workflows/README.md for new architecture"
```

### 4. Update Branch Protection Rules

Update main branch protection to require these status checks:
- `ci-complete` (replaces individual test jobs)
- `context-health-check` (from context-guardian workflow)

### 5. Update Documentation References

Search for references to old workflows in:
- README files
- Documentation
- Issue templates
- Wiki pages

## 🔍 Verification Checklist

Before removing old workflows, verify:

- [ ] CI/CD tests run successfully in `ci-complete.yml`
- [ ] PR reviews work with `claude-pr-assistant.yml`
- [ ] @claude mentions get responses
- [ ] Documentation analysis runs on main push
- [ ] Context health checks run on schedule
- [ ] All caching strategies work efficiently
- [ ] Workflow permissions are correctly set
- [ ] README files are updated

## 💡 Benefits of Consolidation

1. **Reduced Complexity**: 4 workflows instead of 10+
2. **Better Performance**: Optimized job dependencies and caching
3. **Clearer Purpose**: Each workflow has a distinct role
4. **Easier Maintenance**: Less duplication, clearer structure
5. **Improved Integration**: Better Claude Code compatibility

## ⚠️ Rollback Plan

If issues arise, you can restore old workflows from git history:

```bash
# Restore a specific workflow
git checkout HEAD~1 -- .github/workflows/old-workflow.yml

# Or restore all at once
git checkout HEAD~1 -- .github/workflows/
```

## 📊 Expected Improvements

After migration:
- **CI runtime**: ~20% faster due to better parallelization
- **Maintenance time**: ~50% reduction in workflow updates
- **API usage**: More efficient Claude API calls
- **Cache efficiency**: Better dependency caching

## 🚀 Next Steps

After successful migration:

1. Monitor workflow performance for a week
2. Gather team feedback on new structure
3. Document any customizations needed
4. Consider additional optimizations

## 📞 Support

If you encounter issues:
1. Check workflow logs in Actions tab
2. Review this guide's verification checklist
3. Create an issue with `workflow-migration` label
4. Ask @claude in a PR comment for help

---

*This guide can be removed after successful migration completion.*