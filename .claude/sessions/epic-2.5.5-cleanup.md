# Epic 2.5.5: Project Cleanup & JSON Migration Preparation

## Session Date: 2025-08-24

## Overview
Created Epic 2.5.5 as a critical prerequisite to Epic 2.6 (JSON Data Source Migration). This cleanup epic addresses technical debt and removes all MHD/I12 dependencies from the codebase.

## Issue Structure Created

### Parent Epic
- **#256**: Epic 2.5.5 - Project Cleanup & JSON Migration Preparation

### Main Tasks (7 Priorities)
1. **#262**: Task 2.5.5.1 - Resolve Duplicates & Conflicts (Priority 1)
2. **#263**: Task 2.5.5.2 - Refactor MHD Dependencies (Priority 2)
3. **#257**: Task 2.5.5.3 - Update Claude AI Context (Priority 3)
4. **#258**: Task 2.5.5.4 - Migrate Justfile Commands (Priority 4)
5. **#259**: Task 2.5.5.5 - Evaluate Incomplete Features (Priority 5)
6. **#260**: Task 2.5.5.6 - Verify Cleanup Completeness (Priority 6)
7. **#261**: Task 2.5.5.7 - Organizational Housekeeping (Priority 7)

### Sub-Tasks Created (9 Critical)
#### For Task 2.5.5.1 (Duplicates):
- **#264**: Audit Backend Core Duplicates
- **#265**: Archive Legacy Data Directories  
- **#266**: Fix Import Statements After Merge

#### For Task 2.5.5.2 (MHD Dependencies):
- **#267**: Archive MHD Parser Module
- **#268**: Create JSON Import Module
- **#269**: Update Database Models for JSON

#### For Task 2.5.5.3 (AI Context):
- **#270**: Retrain Import Specialist Agent
- **#271**: Update Context Map Keywords
- **#272**: Rewrite Import Module Documentation

## Key Decisions

### 1. Phased Approach (8 days total)
- **Phase 1**: Audit & Document (2 days)
- **Phase 2**: Safe Cleanup (3 days)
- **Phase 3**: Prepare for JSON (2 days)
- **Phase 4**: Validation (1 day)

### 2. Dependency Chain
```
Priority 1 → Priority 2 → Priority 3
              ↓
        Priority 4 → Priority 5
              ↓
        Priority 6 → Priority 7
```

### 3. Risk Assessment
- **High Risk**: Duplicate resolution, MHD refactoring, command migration
- **Medium Risk**: AI updates, legacy archival, feature evaluation
- **Low Risk**: Housekeeping, documentation, verification

### 4. Critical Path Items
1. Must resolve `/backend/backend/app/core` vs `/backend/app/core` conflict first
2. Archive all MHD code before deletion
3. Maintain system stability throughout
4. Test after each priority level

## Success Criteria
- Zero MHD/I12 references (except in archive)
- All duplicate directories resolved
- Claude agents respond correctly to JSON queries
- All Justfile commands functional
- Documentation fully updated
- Epic 2.6 can start immediately without blockers

## Validation Command
```bash
grep -r "mhd\|i12\|MidsReborn" --exclude-dir=.git --exclude-dir=archive .
```
Should return zero results when complete.

## Archive Strategy
All removed code will be preserved in:
```
/archive/
├── mhd-legacy/       # MHD parser and related
├── data-exports/     # Old data directories
└── experiments/      # Incomplete features
```

## Notes for Implementation
1. Create feature branches for each main task
2. Use atomic commits for easy rollback
3. Update progress.json after each task
4. Keep CLAUDE.md updated with status
5. Test thoroughly before marking complete

## Blocking Relationship
**Epic 2.5.5 MUST be completed before Epic 2.6 can begin.**
Epic 2.6 status changed from "in_progress" to "blocked" until cleanup is complete.

## Created By
Claude Code using Anthropic's native sub-agent system based on comprehensive cleanup requirements from `/shared/user/claude/epic26-project-cleanup.yml`.