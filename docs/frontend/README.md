# Frontend Documentation

Overview of Mids Hero Web frontend development documentation.

## 📚 Documentation Files

### Core Documentation

- **[architecture.md](./architecture.md)** - Frontend architecture design
  - Tech stack decisions (Next.js, React 19, shadcn/ui)
  - Component structure and organization
  - State management strategy
  - API integration patterns
  - Testing approach

- **[epic-breakdown.md](./epic-breakdown.md)** - Complete frontend roadmap
  - Epic 1: Foundation & Setup (Next.js, design system, layout)
  - Epic 2: Character Creation (archetype selection, initial setup)
  - Epic 3: Power Selection (powerset browser, power picker)
  - Epic 4: Enhancement Slotting (slot management, set bonuses)
  - Epic 5: Build Statistics (stat calculations, visual displays)
  - Epic 6: Build Management (save, load, share builds)
  - Epic 7: Polish & UX (responsive design, accessibility)

- **[midsreborn-ui-analysis.md](./midsreborn-ui-analysis.md)** - MidsReborn UI reference
  - Comprehensive analysis of MidsReborn desktop application
  - Component inventory and behavior
  - User interaction patterns
  - Reference for modern web adaptation

## 🚀 Getting Started

**Status**: Frontend is in development using the superpowers plugin workflow.

**To Start Development**:
1. Tell Claude: "start epic 1.1" or describe your frontend task
2. Claude will invoke the frontend-development skill
3. Follow the superpowers workflow (plan → approve → execute → review)

## 🏗️ Development Approach

The frontend is being built using a **systematic, quality-gated approach**:

1. **Planning**: Each epic gets a detailed implementation plan via `/superpowers:write-plan`
2. **Review**: Plans are reviewed and approved before execution
3. **Execution**: Plans are executed in batches via `/superpowers:execute-plan`
4. **Checkpoints**: Regular review checkpoints ensure quality

This approach ensures:
- Consistent implementation quality
- Clear progress tracking
- Alignment with MidsReborn functionality
- Modern web best practices

## 🎯 Current Status

**Next Epic**: Epic 1.1 - Next.js Setup + Design System

**Backend**: 100% complete with full API coverage

**Reference**: MidsReborn UI fully analyzed and documented

## 📖 Related Documentation

- **Frontend README**: `frontend/README.md` - Frontend directory overview
- **Root README**: `README.md` - Project overview and setup
- **Backend README**: `backend/README.md` - Backend API documentation
- **Project Status**: `docs/PROJECT_STATUS.md` - Overall project progress

---

_This documentation supports systematic frontend development using the superpowers plugin workflow._
