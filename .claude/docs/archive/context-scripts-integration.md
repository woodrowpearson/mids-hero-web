# Context Scripts Integration Analysis

## Current State

### Scripts in `/scripts/context/`

1. **analyze_token_usage.py**
   - Purpose: Analyze token usage in project documentation
   - Uses tiktoken to count tokens in files
   - Could be integrated with our context management

2. **update_progress.py**
   - Purpose: Update progress tracking for roadmap epics
   - References old path: `.claude/progress.json`
   - Needs update to: `.claude/state/progress.json`

## Integration Opportunities

### 1. Token Analysis Integration

The `analyze_token_usage.py` script could be enhanced to:
- Monitor our modular context system
- Validate file size limits defined in `context-map.json`
- Generate reports on context efficiency

**Proposed Enhancement:**
```python
# Add to analyze_token_usage.py
def validate_context_limits():
    """Validate files against context-map.json limits."""
    with open('.claude/context-map.json') as f:
        config = json.load(f)
    
    limits = config['file_health_checks']['max_file_sizes']
    
    # Check CLAUDE.md
    claude_tokens = count_tokens(Path('CLAUDE.md').read_text())
    if claude_tokens > limits['CLAUDE.md']:
        print(f"WARNING: CLAUDE.md exceeds limit ({claude_tokens} > {limits['CLAUDE.md']})")
```

### 2. Progress Update Integration

The `update_progress.py` script needs:
- Path update to `.claude/state/progress.json`
- Integration with our session management
- Could power automatic session summaries

**Required Changes:**
```python
# Update path reference
progress_file = Path(".claude/state/progress.json")
```

### 3. New Scripts Needed

Based on our context management plan, we should create:

1. **context_monitor.py** - Real-time context usage tracking
2. **session_summarizer.py** - Auto-summarize when hitting 50K tokens
3. **module_loader.py** - Simulate module loading based on keywords

## Recommendations

### Immediate Actions

1. **Update existing scripts**:
   ```bash
   # Fix progress.json path
   sed -i '' 's|\.claude/progress\.json|.claude/state/progress.json|g' scripts/context/update_progress.py
   ```

2. **Create validation script**:
   ```bash
   # New script to validate our context structure
   scripts/context/validate_context.py
   ```

3. **Add to justfile**:
   ```makefile
   # Token analysis
   token-analyze:
       python scripts/context/analyze_token_usage.py .claude/
   
   # Validate context limits
   context-validate:
       python scripts/context/validate_context.py
   ```

### Future Integration

1. **Automated Monitoring**:
   - Hook into Claude sessions
   - Track actual token usage
   - Alert when approaching limits

2. **Smart Pruning**:
   - Use token analysis to identify unused content
   - Suggest files to remove from modules
   - Optimize loading patterns

3. **Usage Analytics**:
   - Track which modules are loaded most
   - Identify rarely-used content
   - Optimize module boundaries

## Current Integration Status

**Currently NOT integrated** ❌
- Scripts exist but aren't connected to our new context system
- They use old paths and don't know about modules
- No automation or hooks in place

**Could be valuable** ✅
- Token counting aligns with our token budget management
- Progress tracking could power session summaries
- Foundation for smart context management

## Next Steps

1. Update script paths to match new structure
2. Create wrapper commands in justfile
3. Build new scripts for context validation
4. Consider GitHub Actions for automated checks