# Epic 1.4: API Client Integration - Summary

**Date**: 2025-11-16
**Status**: Planning Complete
**Epic**: 1.4 - API Client Integration
**Detailed Plan**: 2025-11-16-epic-1.4-api-client-integration.md

---

## What This Epic Accomplishes

Epic 1.4 establishes the **data fetching foundation** for Mids Hero Web, connecting the React frontend to the FastAPI backend. This epic creates:

1. **API Service Layers** - Type-safe wrappers for all backend endpoints
2. **TanStack Query Hooks** - Automatic caching, refetching, and error handling
3. **Loading & Error Components** - Consistent UX for async operations
4. **Lazy Loading Strategy** - Efficient data fetching patterns

Unlike MidsReborn's blocking synchronous loads, this implementation uses modern async patterns with progressive loading and graceful error handling.

---

## Key Components Created

### API Service Layers (6 files)

**Base API Client** (`services/api.ts`):
- Axios instance with baseURL configuration
- Request/response interceptors
- 10-second timeout
- Error logging

**Domain-Specific Services**:
- `services/archetypeApi.ts` - Archetype data operations
- `services/powersetApi.ts` - Powerset data operations (filtered by archetype)
- `services/powerApi.ts` - Power data operations (lazy by powerset)
- `services/enhancementApi.ts` - Enhancement data with pagination
- `services/calculationApi.ts` - Build calculation triggers

### TanStack Query Hooks (5 files)

**Data Fetching Hooks**:
- `hooks/useArchetypes.ts` - Fetch all archetypes (`staleTime: Infinity`)
- `hooks/usePowersets.ts` - Fetch powersets by archetype (lazy, cached)
- `hooks/usePowers.ts` - Fetch powers by powerset (lazy, 5min cache)
- `hooks/useEnhancements.ts` - Fetch paginated enhancements (1hr cache)
- `hooks/useCalculations.ts` - Mutation hook for calculations (no cache)

### UI Components (4 files)

**Loading & Error States**:
- `components/ui/LoadingSpinner.tsx` - Spinner with size variants (sm/md/lg)
- `components/ui/LoadingState.tsx` - Full-page loading state
- `components/ui/ErrorMessage.tsx` - Error display with retry button
- `components/ui/EmptyState.tsx` - Empty/no-data state

---

## State Management Approach

### TanStack Query (Server State)

All backend data managed by TanStack Query with aggressive caching:

**Caching Strategy**:
- **Archetypes**: `staleTime: Infinity` (never changes)
- **Powersets**: `staleTime: Infinity` (rarely changes)
- **Powers**: `staleTime: 5 minutes` (semi-static)
- **Enhancements**: `staleTime: 1 hour` (semi-static)
- **Calculations**: No caching (always fresh)

**Lazy Loading**:
- Powersets: Only fetch when archetype selected
- Powers: Only fetch when powerset selected
- Enhancements: Paginated (100 per page)

**Error Handling**:
- Retry: 3 attempts with exponential backoff
- Network errors: Show ErrorMessage with retry button
- API errors: User-friendly messages

### Zustand (Client State)

No new Zustand stores for Epic 1.4. TanStack Query handles all server state.

**Existing stores** (from Epic 1.2):
- `characterStore` - User's build selections
- `uiStore` - Layout preferences

---

## MidsReborn Reference Implementation

From `MIDSREBORN-UI-ANALYSIS-epic-1.4.md`:

**MidsReborn's Approach**:
- **Upfront loading**: All data (archetypes, powersets, powers, enhancements) loaded at startup
- **Synchronous**: Blocking UI with splash screen progress messages
- **Singleton cache**: Data stored in `Database.Instance` for entire app lifetime
- **No lazy loading**: All 3000+ powers, 3000+ enhancements loaded upfront
- **Fatal errors**: Application exits on data load failure

**Web Implementation Improvements**:
- **Lazy loading**: Only fetch data when needed (by archetype, by powerset)
- **Asynchronous**: Non-blocking with loading states
- **Automatic caching**: TanStack Query manages cache lifetime
- **Pagination**: Enhancements loaded 100 at a time
- **Graceful errors**: Show error + retry, don't exit app

---

## API Integration

### Backend Endpoints Used

All endpoints verified as existing in FastAPI backend:

| Endpoint | Purpose |
|----------|---------|
| `GET /api/archetypes` | Fetch all archetypes (~13) |
| `GET /api/archetypes/:id/powersets` | Powersets for archetype |
| `GET /api/powersets/:id/powers` | Powers in powerset |
| `GET /api/enhancements` | Paginated enhancements (3000+) |
| `GET /api/enhancement-sets` | All enhancement sets |
| `POST /api/calculations/totals` | Calculate build totals |

**Base URL**:
- Development: `http://localhost:8000/api`
- Production: `https://api.midshero.com/api` (configured via env)

### TypeScript Types

**Type Files Created**:
- `types/character.types.ts` - Archetype, Origin, Alignment
- `types/power.types.ts` - Powerset, Power
- `types/enhancement.types.ts` - Enhancement, EnhancementSet
- `types/build.types.ts` - BuildData, CalculatedTotals

All types match backend response schemas for type safety.

---

## Testing Strategy

### Test Coverage (~40 tests)

**Service Tests** (~18 tests):
- API client configuration
- Success responses
- Error handling
- Query parameters
- Pagination

**Hook Tests** (~12 tests):
- Loading states
- Success states
- Error states
- Caching behavior
- Lazy loading (enabled flag)

**Component Tests** (~10 tests):
- LoadingSpinner rendering
- ErrorMessage retry button
- LoadingState message
- EmptyState display

**Test Coverage Goal**: >80% for all services and hooks

**Tools**:
- Vitest
- React Testing Library
- `@testing-library/react-hooks`
- Mock Service Worker (MSW) for API mocking

---

## Implementation Tasks

1. **Install dependencies** - TanStack Query, Axios, lucide-react
2. **Create base API client** - Axios with interceptors
3. **Create API service layers** - 5 domain services
4. **Create TanStack Query hooks** - 5 data fetching hooks
5. **Create UI components** - 4 loading/error components
6. **Update providers** - Wrap app with QueryClientProvider
7. **Configure environment** - API URL in .env.local
8. **Integration testing** - Verify data fetching works
9. **Run all tests** - Ensure >80% coverage

**Estimated Time**: 4-6 hours

---

## Acceptance Criteria

### Functional

✅ Can fetch archetypes from backend
✅ Can fetch powersets filtered by archetype
✅ Can fetch powers by powerset
✅ Can fetch enhancements with pagination
✅ Error handling works (network failures, API errors)
✅ Data caches correctly (no unnecessary refetches)
✅ Loading states display during async operations

### Visual

✅ LoadingSpinner shows during data fetch
✅ ErrorMessage displays on failure with retry button
✅ EmptyState shows when no data available
✅ No console errors or warnings

### Technical

✅ All TypeScript strict mode compliant (no `any`)
✅ All services and hooks tested (>80% coverage)
✅ ESLint and Prettier passing
✅ Integration tests with backend pass

---

## Deferred Features

**Epic 2.1** (Character Creation):
- Archetype selector component (uses `useArchetypes` hook)
- Origin selector component
- Powerset selectors (uses `usePowersets` hook)

**Epic 3.1** (Power Selection):
- Power list component (uses `usePowers` hook)
- Power picking interaction

**Epic 3.3** (Enhancement Browser):
- Enhancement browser component (uses `useEnhancements` hook)
- Pagination controls

---

## Next Epic Preview

**Epic 2.1**: Archetype & Origin Selection

**Will build on Epic 1.4**:
- Use `useArchetypes` hook to populate archetype selector
- Use `usePowersets` hook to populate powerset selectors
- Display loading states while data fetches
- Handle errors gracefully

**Prerequisites Met**:
- ✅ API client configured
- ✅ Data fetching hooks ready
- ✅ Loading/error components created
- ✅ Backend endpoints verified

---

## Key Design Decisions

### 1. TanStack Query Over Manual State Management

**Rationale**: TanStack Query provides automatic caching, refetching, error handling, and retry logic out of the box.

**Impact**: Simpler code, better UX, less boilerplate.

### 2. Lazy Loading Over Upfront Loading

**Rationale**: MidsReborn loads 3000+ powers upfront. Web can lazy load by powerset for better performance.

**Impact**: Faster initial load, reduced memory usage, better perceived performance.

### 3. Aggressive Caching for Static Data

**Rationale**: Archetypes and powersets rarely change. Cache indefinitely to avoid unnecessary API calls.

**Impact**: Reduced backend load, instant data retrieval on subsequent accesses.

### 4. Pagination for Enhancements

**Rationale**: 3000+ enhancements is too large for single request.

**Impact**: Faster load times, better UX, reduced backend load.

### 5. Axios Over Fetch API

**Rationale**: Axios provides request/response interceptors, automatic JSON parsing, and better error handling.

**Impact**: Simpler code, easier auth integration (future), consistent error handling.

---

## Summary

Epic 1.4 delivers the **data fetching foundation** for Mids Hero Web:
- **6 API service layers** (type-safe wrappers for backend)
- **5 TanStack Query hooks** (automatic caching, refetching, error handling)
- **4 UI components** (loading, error, empty states)
- **Lazy loading strategy** (defer data fetching until needed)
- **Aggressive caching** (static data cached indefinitely)

This foundation enables all future epics to fetch and display game data efficiently.

---

**Status**: ✅ Planning Complete - Ready for Execution
**Services**: 6 (api, archetypeApi, powersetApi, powerApi, enhancementApi, calculationApi)
**Hooks**: 5 (useArchetypes, usePowersets, usePowers, useEnhancements, useCalculations)
**Components**: 4 (LoadingSpinner, ErrorMessage, LoadingState, EmptyState)
**Tests**: ~40 tests
**Dependencies**: Epic 1.3 complete ✅
**Next**: Execute implementation
