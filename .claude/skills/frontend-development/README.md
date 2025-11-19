# Frontend Development - Usage Guide
Last Updated: 2025-11-19 20:27:56 UTC

**Frontend-specific orchestration using superpowers plugin**

This skill orchestrates frontend development by integrating with the superpowers plugin's `write-plan` and `execute-plan` skills. It does NOT directly create files - instead it coordinates the workflow and invokes the appropriate superpowers skills via slash commands.

## Quick Start

### Running a Frontend Stage

```bash
/frontend-development epic-X.Y
```

Replace `epic-X.Y` with your epic/stage number (e.g., `epic-1.1`, `epic-2.1`).

### Complete Flow

```
1. Context Collection
   → Loads all previous artifacts + MidsReborn UI references

2. MidsReborn UI Analysis
   → Launches Explore agent via Task tool
   → Analyzes MidsReborn C# UI code for feature implementation
   → Identifies available screenshots from shared/user/midsreborn-screenshots

3. Planning
   → Invokes `/superpowers:write-plan` via SlashCommand
   → Planning agent creates implementation plan
   → Includes component specs, state management, API integration

🚧 GATE 1: Human Approval
   → Review MidsReborn analysis + plan
   → Type: "proceed to execute"

4. Execution
   → Invokes `/superpowers:execute-plan` via SlashCommand
   → Execution agent creates React components with tests
   → Follows TDD pattern for component development

5. Visual Verification & Checkpoint
   → Manual visual comparison with MidsReborn
   → Generates checkpoint document
   → Updates project status

🚧 GATE 2: Human Approval + Visual Check
   → Review checkpoint
   → Visually verify component matches MidsReborn UX
   → Type: "approved - proceed to Epic X.Y+1"
```

## What This Skill Includes

✅ MidsReborn UI code analysis (Forms/ directory)
✅ Screenshot-based visual verification workflow
✅ React component planning with TDD
✅ State management integration (TanStack Query + Zustand)
✅ API integration with FastAPI backend
✅ Component testing with React Testing Library
✅ Two-gate approval flow with visual verification
✅ Checkpoint generation with screenshots
✅ Epic-level progress tracking

## Files Created Per Epic/Stage

```
docs/frontend/analysis/
└── MIDSREBORN-UI-ANALYSIS-epic-X.Y.md

docs/frontend/plans/
├── YYYY-MM-DD-epic-X.Y-[feature].md
└── PLAN-SUMMARY-epic-X.Y.md

docs/frontend/checkpoints/
└── CHECKPOINT-epic-X.Y-[name].md

docs/frontend/screenshots/
└── implementation-[feature]-epic-X.Y.png (our implementation)

shared/user/midsreborn-screenshots/
└── [various reference screenshots from MidsReborn]

frontend/src/ (components, hooks, services created via execute-plan)
```

## Epic Structure

```
Epic 1: Foundation & Setup
├── Epic 1.1: Next.js migration + design system
├── Epic 1.2: State management setup
├── Epic 1.3: Layout shell + navigation
└── Epic 1.4: API client integration

Epic 2: Character Creation
├── Epic 2.1: Archetype selector
├── Epic 2.2: Powerset selection
└── Epic 2.3: Character sheet display

Epic 3: Power Selection & Slotting
├── Epic 3.1: Available powers panel
├── Epic 3.2: Power picker UI
├── Epic 3.3: Enhancement browser
└── Epic 3.4: Slot editor

Epic 4: Build Totals & Stats
├── Epic 4.1: Defense/Resistance displays
├── Epic 4.2: Damage/Recharge displays
└── Epic 4.3: Visual aids (graphs, charts)

Epic 5: Set Bonuses & Advanced
├── Epic 5.1: Active set bonuses
└── Epic 5.2: Set bonus browser

Epic 6: Build Persistence & Sharing
├── Epic 6.1: Save/load builds
├── Epic 6.2: Permalink generation
└── Epic 6.3: Auto-save + undo/redo

Epic 7: Polish & Performance
├── Epic 7.1: Loading states & errors
└── Epic 7.2: Performance optimization
```

## Visual Verification Workflow

Each stage includes visual verification:

1. **Reference Screenshot**: Capture MidsReborn UI for the feature
2. **Implementation Screenshot**: Capture your implementation
3. **Side-by-Side Comparison**: Include both in checkpoint document
4. **UX Parity Checklist**: Verify functional parity (not pixel-perfect match)

## Troubleshooting

**"ERROR: MidsReborn UI code not found"**
→ Check `/Users/w/code/mids-hero-web/external/dev/MidsReborn` exists

**"Need screenshot for verification"**
→ Capture MidsReborn screenshot and save to `shared/user/midsreborn-screenshots/`

**Component tests failing**
→ Type 'retry' to re-run execution phase

## Design Reference

Modeled after: `.claude/skills/verified-stage-development`
Frontend-specific adaptations for React/Next.js development
