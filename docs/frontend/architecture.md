# Mids Hero Web - Frontend Architecture

**Created**: 2025-11-13
**Status**: Draft
**Version**: 1.0

---

## Executive Summary

Mids Hero Web frontend is a modern React web application built with Next.js 14, providing feature parity with the MidsReborn desktop application while delivering a superior web-native experience.

**Tech Stack**:
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript (strict mode)
- **State Management**: TanStack Query + Zustand
- **UI Components**: shadcn/ui + Tailwind CSS
- **Testing**: Vitest + React Testing Library
- **Backend API**: FastAPI (Python) - already complete

**Key Architectural Principles**:
1. **API-First**: All calculations via FastAPI backend
2. **Type-Safe**: TypeScript end-to-end
3. **Component-Driven**: Reusable, tested React components
4. **Performance-Optimized**: SSR for sharing, client-side for building
5. **Accessible**: WCAG 2.1 AA compliance

---

## Technical Stack Decisions

### Framework: Next.js 14 (App Router)

**Rationale**:
- **SSR/SSG**: Required for rich preview cards when sharing build links on Discord/Twitter
- **SEO**: Better discoverability for public builds
- **API Routes**: Can handle build persistence without separate server (if needed)
- **Performance**: Automatic code splitting, image optimization
- **Modern**: App Router with Server Components

**Key Features Used**:
- App Router (`app/` directory)
- Server Components for static layouts
- Client Components for interactive build UI
- API routes for build sharing (optional - can use FastAPI directly)
- Static generation for shared builds (`generateStaticParams`)
- Dynamic routes for builds: `/build/[id]`

**Migration from CRA**:
- **Recommendation**: Start fresh Next.js project
- **Rationale**: Current `frontend/` is minimal (just skeleton)
- Cherry-pick useful code if any (API client, types)

---

### State Management

#### TanStack Query (Server State)

**Purpose**: Manage server data (powers, archetypes, enhancements, shared builds)

**Usage**:
```typescript
// Database (powers, archetypes, enhancements)
const { data: powers } = useQuery({
  queryKey: ['powers'],
  queryFn: () => fetch('/api/powers').then(r => r.json()),
  staleTime: Infinity, // Cache forever
});

// Shared build
const { data: build } = useQuery({
  queryKey: ['build', buildId],
  queryFn: () => fetchBuild(buildId),
  enabled: !!buildId,
});

// Build sharing mutation
const shareMutation = useMutation({
  mutationFn: (buildData: BuildData) =>
    fetch('/api/builds', {
      method: 'POST',
      body: JSON.stringify(buildData),
    }),
  onSuccess: (response) => {
    // response.id, response.downloadUrl, response.imageUrl
    showShareDialog(response);
  },
});
```

**Configuration**:
```typescript
// app/providers.tsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
}
```

#### Zustand (Client State)

**Purpose**: Manage character build state (local, editable)

**Store Design**:
```typescript
// stores/characterStore.ts
import { create } from 'zustand';
import { temporal } from 'zustand/middleware';
import { devtools, persist } from 'zustand/middleware';

interface CharacterState {
  // Character data
  name: string;
  archetype: Archetype | null;
  origin: Origin | null;
  alignment: Alignment | null;
  primaryPowerset: Powerset | null;
  secondaryPowerset: Powerset | null;
  poolPowersets: (Powerset | null)[];
  ancillaryPowerset: Powerset | null;

  // Build data
  powers: PowerEntry[];
  level: number;

  // Calculated totals (from backend)
  totals: CalculatedTotals | null;
  isCalculating: boolean;

  // Actions
  setName: (name: string) => void;
  setArchetype: (archetype: Archetype) => void;
  setOrigin: (origin: Origin) => void;
  setAlignment: (alignment: Alignment) => void;
  setPrimaryPowerset: (powerset: Powerset) => void;
  setSecondaryPowerset: (powerset: Powerset) => void;
  setPoolPowerset: (index: number, powerset: Powerset | null) => void;
  setAncillaryPowerset: (powerset: Powerset) => void;
  addPower: (power: Power, level: number) => void;
  removePower: (index: number) => void;
  addSlot: (powerIndex: number) => void;
  removeSlot: (powerIndex: number, slotIndex: number) => void;
  slotEnhancement: (powerIndex: number, slotIndex: number, enhancement: Enhancement) => void;
  removeEnhancement: (powerIndex: number, slotIndex: number) => void;

  // Calculations
  recalculate: () => Promise<void>;

  // Build management
  loadBuild: (build: BuildData) => void;
  clearBuild: () => void;
  exportBuild: () => BuildData;
}

export const useCharacterStore = create<CharacterState>()(
  devtools(
    persist(
      temporal((set, get) => ({
        // Initial state
        name: '',
        archetype: null,
        origin: null,
        alignment: null,
        primaryPowerset: null,
        secondaryPowerset: null,
        poolPowersets: [null, null, null, null],
        ancillaryPowerset: null,
        powers: [],
        level: 1,
        totals: null,
        isCalculating: false,

        // Actions
        setName: (name) => set({ name }),
        setArchetype: (archetype) => {
          set({ archetype });
          get().recalculate();
        },
        // ... other actions

        recalculate: async () => {
          set({ isCalculating: true });
          try {
            const buildData = get().exportBuild();
            const response = await fetch('/api/calculations/totals', {
              method: 'POST',
              body: JSON.stringify(buildData),
            });
            const totals = await response.json();
            set({ totals, isCalculating: false });
          } catch (error) {
            console.error('Calculation failed:', error);
            set({ isCalculating: false });
          }
        },

        // ... other actions
      })),
      {
        name: 'character-build-storage',
        partialize: (state) => ({
          name: state.name,
          archetype: state.archetype,
          // ... only persist essential fields
        }),
      }
    )
  )
);

// Undo/Redo access
const undo = useCharacterStore.temporal.getState().undo;
const redo = useCharacterStore.temporal.getState().redo;
```

**Undo/Redo**:
```typescript
// Keyboard shortcuts
useEffect(() => {
  const handleKeyPress = (e: KeyboardEvent) => {
    if ((e.metaKey || e.ctrlKey) && e.key === 'z') {
      if (e.shiftKey) {
        useCharacterStore.temporal.getState().redo();
      } else {
        useCharacterStore.temporal.getState().undo();
      }
    }
  };
  window.addEventListener('keydown', handleKeyPress);
  return () => window.removeEventListener('keydown', handleKeyPress);
}, []);
```

---

### UI Components: shadcn/ui + Tailwind CSS

**Rationale**:
- **shadcn/ui**: Copy-paste components, full control, not npm dependency
- **Tailwind**: Utility-first CSS, rapid development, modern aesthetic
- **Customizable**: Can modify components heavily for game-specific needs
- **TypeScript**: Excellent TypeScript support
- **Accessible**: Built-in ARIA attributes

**Installation**:
```bash
npx shadcn-ui@latest init

# Install needed components
npx shadcn-ui@latest add button
npx shadcn-ui@latest add dialog
npx shadcn-ui@latest add select
npx shadcn-ui@latest add tabs
npx shadcn-ui@latest add tooltip
npx shadcn-ui@latest add accordion
npx shadcn-ui@latest add popover
npx shadcn-ui@latest add table
# ... and more as needed
```

**Core Components Used**:
- **Button**: All button interactions
- **Select/Combobox**: Dropdowns (archetype, powersets)
- **Dialog**: Modals (enhancement picker, confirmations)
- **Tabs**: Tabbed interfaces
- **Tooltip**: Hover information
- **Accordion**: Collapsible sections
- **Popover**: Floating panels (power details)
- **Table**: Data tables (TanStack Table integration)
- **Input**: Text inputs (character name)
- **Checkbox/Radio**: Toggles and exclusive choices
- **Progress**: Loading states

**Custom Components** (to build):
- **PowerList**: Vertical scrollable power list
- **PowerCard**: Individual power display with slots
- **EnhancementPicker**: Complex grid-based picker (custom Dialog)
- **StatBar**: Single stat bar with cap indicators
- **StatPanel**: Multi-stat display (defense, resistance, etc.)
- **BuildLayout**: Main build display (2-6 columns)

---

### Testing Strategy

**Test Stack**:
- **Vitest**: Unit testing (faster than Jest)
- **React Testing Library**: Component testing
- **Playwright** (optional): E2E testing for critical flows

**Test Coverage Goals**:
- Components: 80%+ coverage
- Stores: 90%+ coverage
- Utilities: 95%+ coverage

**Example Component Test**:
```typescript
// components/ArchetypeSelector.test.tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ArchetypeSelector } from './ArchetypeSelector';

describe('ArchetypeSelector', () => {
  it('renders archetype options', () => {
    render(<ArchetypeSelector archetypes={mockArchetypes} />);
    expect(screen.getByRole('combobox')).toBeInTheDocument();
  });

  it('calls onChange when archetype selected', async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    render(<ArchetypeSelector archetypes={mockArchetypes} onChange={onChange} />);

    await user.click(screen.getByRole('combobox'));
    await user.click(screen.getByText('Blaster'));

    expect(onChange).toHaveBeenCalledWith(expect.objectContaining({ name: 'Blaster' }));
  });
});
```

**Example Store Test**:
```typescript
// stores/characterStore.test.ts
import { renderHook, act } from '@testing-library/react';
import { useCharacterStore } from './characterStore';

describe('characterStore', () => {
  beforeEach(() => {
    useCharacterStore.getState().clearBuild();
  });

  it('sets archetype correctly', () => {
    const { result } = renderHook(() => useCharacterStore());

    act(() => {
      result.current.setArchetype(mockBlaster);
    });

    expect(result.current.archetype).toEqual(mockBlaster);
  });

  it('adds power at specified level', () => {
    const { result } = renderHook(() => useCharacterStore());

    act(() => {
      result.current.addPower(mockPower, 1);
    });

    expect(result.current.powers).toHaveLength(1);
    expect(result.current.powers[0].power).toEqual(mockPower);
    expect(result.current.powers[0].level).toBe(1);
  });
});
```

---

## Folder Structure

```
mids-hero-web/
├── frontend/                    # Next.js app
│   ├── app/                     # Next.js App Router
│   │   ├── layout.tsx           # Root layout
│   │   ├── page.tsx             # Homepage
│   │   ├── build/
│   │   │   └── [id]/
│   │   │       └── page.tsx     # Shared build viewer
│   │   ├── builder/
│   │   │   └── page.tsx         # Build creator/editor
│   │   ├── api/                 # API routes (optional)
│   │   │   └── builds/
│   │   │       └── route.ts     # Build CRUD (or proxy to FastAPI)
│   │   └── providers.tsx        # React Query provider
│   ├── components/              # React components
│   │   ├── ui/                  # shadcn/ui components
│   │   │   ├── button.tsx
│   │   │   ├── dialog.tsx
│   │   │   ├── select.tsx
│   │   │   └── ...
│   │   ├── character/           # Character creation components
│   │   │   ├── ArchetypeSelector.tsx
│   │   │   ├── OriginSelector.tsx
│   │   │   ├── PowersetSelector.tsx
│   │   │   └── CharacterSheet.tsx
│   │   ├── powers/              # Power selection components
│   │   │   ├── PowerList.tsx
│   │   │   ├── PowerCard.tsx
│   │   │   ├── PowerPicker.tsx
│   │   │   └── PowerDetail.tsx
│   │   ├── enhancements/        # Enhancement slotting components
│   │   │   ├── SlotEditor.tsx
│   │   │   ├── EnhancementPicker.tsx
│   │   │   ├── EnhancementGrid.tsx
│   │   │   └── SetBonusDisplay.tsx
│   │   ├── stats/               # Stat display components
│   │   │   ├── StatBar.tsx
│   │   │   ├── DefensePanel.tsx
│   │   │   ├── ResistancePanel.tsx
│   │   │   ├── HPEndurancePanel.tsx
│   │   │   └── TotalsWindow.tsx
│   │   ├── layout/              # Layout components
│   │   │   ├── BuildLayout.tsx  # 2-6 column grid
│   │   │   ├── TopPanel.tsx
│   │   │   ├── SidePanel.tsx
│   │   │   └── Footer.tsx
│   │   └── sharing/             # Build sharing components
│   │       ├── ShareDialog.tsx
│   │       ├── ExportOptions.tsx
│   │       └── BuildCard.tsx
│   ├── hooks/                   # Custom React hooks
│   │   ├── useCharacter.ts      # Character store hook
│   │   ├── usePowers.ts         # Power data hook
│   │   ├── useEnhancements.ts   # Enhancement data hook
│   │   ├── useCalculations.ts   # Calculation API hook
│   │   ├── useKeyboardShortcuts.ts
│   │   └── useAutoSave.ts
│   ├── stores/                  # Zustand stores
│   │   ├── characterStore.ts    # Main character/build state
│   │   ├── uiStore.ts           # UI preferences (column layout, theme)
│   │   └── index.ts
│   ├── services/                # API clients
│   │   ├── api.ts               # Axios/fetch wrapper
│   │   ├── powerApi.ts          # Power endpoints
│   │   ├── enhancementApi.ts    # Enhancement endpoints
│   │   ├── calculationApi.ts    # Calculation endpoints
│   │   └── buildApi.ts          # Build sharing endpoints
│   ├── types/                   # TypeScript types
│   │   ├── character.types.ts   # Character, Archetype, Origin
│   │   ├── power.types.ts       # Power, Powerset, Effect
│   │   ├── enhancement.types.ts # Enhancement, Slot, SetBonus
│   │   ├── build.types.ts       # BuildData, PowerEntry
│   │   ├── totals.types.ts      # CalculatedTotals, Stats
│   │   └── api.types.ts         # API request/response types
│   ├── lib/                     # Utilities
│   │   ├── utils.ts             # General utilities
│   │   ├── cn.ts                # Tailwind class merging
│   │   ├── formatters.ts        # Number/string formatting
│   │   └── validators.ts        # Input validation
│   ├── styles/                  # Global styles
│   │   └── globals.css          # Tailwind imports + custom
│   ├── public/                  # Static assets
│   │   ├── icons/               # Power/enhancement icons
│   │   └── images/
│   ├── __tests__/               # Tests
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── stores/
│   │   └── utils/
│   ├── .env.local               # Environment variables
│   ├── next.config.js           # Next.js config
│   ├── tailwind.config.ts       # Tailwind config
│   ├── tsconfig.json            # TypeScript config
│   ├── vitest.config.ts         # Vitest config
│   └── package.json
└── backend/                     # FastAPI (existing)
    └── ... (already complete)
```

---

## API Integration

### FastAPI Backend Endpoints

**Base URL**: `http://localhost:8000/api` (dev), `https://api.midshero.com/api` (prod)

**Endpoints** (from backend documentation):

#### Database Endpoints
- `GET /api/archetypes` - List all archetypes
- `GET /api/powersets` - List all powersets
- `GET /api/powersets/{id}/powers` - Powers in powerset
- `GET /api/enhancements` - List all enhancements
- `GET /api/enhancement-sets` - List all enhancement sets

#### Calculation Endpoints
- `POST /api/calculations/power` - Calculate single power stats
- `POST /api/calculations/totals` - Calculate build totals
- `POST /api/calculations/set-bonuses` - Calculate set bonuses

#### Build Endpoints (to be implemented)
- `POST /api/builds` - Create/share build (returns ID, URLs)
- `GET /api/builds/{id}` - Fetch shared build
- `PUT /api/builds/{id}` - Update existing build
- `DELETE /api/builds/{id}` - Delete build (if owned)

### API Client Setup

```typescript
// services/api.ts
import axios from 'axios';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor (add auth if needed)
api.interceptors.request.use((config) => {
  // Add auth token if available
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor (error handling)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export default api;
```

---

## Build Sharing Implementation

### Permalink Strategy

**URL Structure**:
- Shared builds: `/build/:buildId`
- Example: `https://midshero.com/build/abc123`

**Server-Side Rendering** (for rich previews):
```typescript
// app/build/[id]/page.tsx
export async function generateMetadata({ params }: { params: { id: string } }) {
  const build = await fetchBuild(params.id);

  return {
    title: `${build.name} - ${build.archetype} Build`,
    description: `${build.primaryPowerset} / ${build.secondaryPowerset} build`,
    openGraph: {
      title: `${build.name}`,
      description: `A ${build.primaryPowerset}/${build.secondaryPowerset} ${build.archetype} build`,
      images: [
        {
          url: build.imageUrl, // Infographic from backend
          width: 1200,
          height: 630,
        },
      ],
    },
    twitter: {
      card: 'summary_large_image',
      title: `${build.name}`,
      description: `${build.archetype} build`,
      images: [build.imageUrl],
    },
  };
}

export default async function BuildPage({ params }: { params: { id: string } }) {
  const build = await fetchBuild(params.id);

  return <BuildViewer build={build} />;
}
```

**Share Dialog**:
```typescript
// components/sharing/ShareDialog.tsx
export function ShareDialog({ buildData }: { buildData: BuildData }) {
  const shareMutation = useMutation({
    mutationFn: (data: BuildData) => api.post('/builds', data),
  });

  const handleShare = async () => {
    const result = await shareMutation.mutateAsync(buildData);

    // result.id, result.downloadUrl, result.imageUrl, result.expiresAt
    // Show share URLs to user
  };

  return (
    <Dialog>
      <DialogContent>
        <Tabs>
          <TabsList>
            <TabsTrigger value="link">Link</TabsTrigger>
            <TabsTrigger value="code">Data Chunk</TabsTrigger>
            <TabsTrigger value="export">Export</TabsTrigger>
          </TabsList>

          <TabsContent value="link">
            <Input value={shareUrl} readOnly />
            <Button onClick={() => navigator.clipboard.writeText(shareUrl)}>
              Copy Link
            </Button>
            <div>
              <strong>Discord Format:</strong>
              <Textarea value={discordMarkdown} readOnly />
            </div>
          </TabsContent>

          <TabsContent value="code">
            <Textarea value={base64DataChunk} readOnly />
            <Button onClick={() => navigator.clipboard.writeText(base64DataChunk)}>
              Copy Code
            </Button>
          </TabsContent>

          <TabsContent value="export">
            <Select>
              <SelectItem value="markdown">Markdown</SelectItem>
              <SelectItem value="bbcode">BBCode</SelectItem>
              <SelectItem value="html">HTML</SelectItem>
            </Select>
            <Button onClick={handleExport}>Export</Button>
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
}
```

---

## Performance Optimization

### Calculation Debouncing

```typescript
// hooks/useAutoCalculate.ts
import { useEffect, useRef } from 'react';
import { useCharacterStore } from '@/stores/characterStore';
import { useDebouncedCallback } from 'use-debounce';

export function useAutoCalculate() {
  const recalculate = useCharacterStore((state) => state.recalculate);

  const debouncedRecalculate = useDebouncedCallback(() => {
    recalculate();
  }, 200); // 200ms debounce

  useEffect(() => {
    const unsubscribe = useCharacterStore.subscribe(
      (state) => [state.powers, state.archetype, state.primaryPowerset],
      () => debouncedRecalculate()
    );

    return unsubscribe;
  }, [debouncedRecalculate]);
}
```

### Auto-Save

```typescript
// hooks/useAutoSave.ts
import { useEffect } from 'react';
import { useCharacterStore } from '@/stores/characterStore';
import { useDebouncedCallback } from 'use-debounce';

export function useAutoSave() {
  const exportBuild = useCharacterStore((state) => state.exportBuild);

  const debouncedSave = useDebouncedCallback(async () => {
    const buildData = exportBuild();
    localStorage.setItem('autosave', JSON.stringify(buildData));
  }, 2000); // 2 second debounce

  useEffect(() => {
    const unsubscribe = useCharacterStore.subscribe(
      () => debouncedSave()
    );

    return unsubscribe;
  }, [debouncedSave]);
}
```

---

## Accessibility

### WCAG 2.1 AA Compliance

**Requirements**:
- Keyboard navigation for all interactions
- Focus indicators on all interactive elements
- ARIA labels for screen readers
- Sufficient color contrast (4.5:1 for text)
- Skip links for navigation
- Form labels and error messages

**Keyboard Shortcuts**:
- `Ctrl/Cmd + Z`: Undo
- `Ctrl/Cmd + Shift + Z`: Redo
- `Ctrl/Cmd + S`: Save build
- `Ctrl/Cmd + O`: Open build
- `Ctrl/Cmd + K`: Quick power search
- `Escape`: Close modals/popups
- Arrow keys: Navigate lists
- Enter: Select item
- Tab: Navigate form fields

---

## Deployment

### Development
```bash
cd frontend
npm install
npm run dev
# Runs on http://localhost:3000
```

### Production Build
```bash
npm run build
npm run start
```

### Environment Variables
```env
# .env.local (development)
NEXT_PUBLIC_API_URL=http://localhost:8000/api

# .env.production
NEXT_PUBLIC_API_URL=https://api.midshero.com/api
```

### Hosting (GCP - To Be Planned Later)
- Cloud Run (containerized Next.js)
- Cloud CDN (static assets)
- Cloud Storage (build images)

---

## Next Steps

1. **Create Epic Breakdown** (`epic-breakdown.md`)
2. **Set up Next.js project** (Epic 1.1)
3. **Install shadcn/ui + Tailwind** (Epic 1.1)
4. **Create component library** (Epic 1.2-1.4)
5. **Build character creation flow** (Epic 2.x)
6. **Implement power selection** (Epic 3.x)
7. **Add enhancement slotting** (Epic 3.x)
8. **Display build totals** (Epic 4.x)
9. **Implement build sharing** (Epic 6.x)
10. **Polish and optimize** (Epic 7.x)

---

**Document Status**: ✅ Complete
**Last Updated**: 2025-11-13
**Version**: 1.0
