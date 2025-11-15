# MidsReborn State Management Analysis: Epic 1.2

**Created**: 2025-11-15
**Epic**: 1.2 - State Management Setup
**Purpose**: Analyze MidsReborn state patterns for web implementation

## Executive Summary

MidsReborn uses a singleton-based state architecture with centralized calculation orchestration. The `clsToonX` class maintains character state, `Build.cs` coordinates all calculations, and a static `DatabaseAPI` provides cached data access. UI updates use an observer pattern where controls subscribe to character change events. For Mids Hero Web, this translates to: Zustand for reactive client state, TanStack Query for server-cached database queries, and React's built-in reactivity replacing manual observer subscriptions.

## MidsReborn State Architecture

### 1. Character State Management (clsToonX.cs)

**Pattern**: Singleton character instance maintained throughout application lifecycle

**Responsibilities**:
- Maintains current archetype, origin, alignment, and powersets
- Tracks power selections by level (levels 1-50)
- Holds enhancement slotting data for all powers
- Triggers recalculation cascade on any state changes
- Provides single source of truth for build configuration

**Key Data Structures**:
```typescript
// Web equivalent types
interface Character {
  name: string;
  archetype: Archetype | null;
  origin: Origin | null;
  alignment: Alignment | null;
  level: number;
  powersets: PowersetSlots;
}

interface PowersetSlots {
  primary: Powerset | null;
  secondary: Powerset | null;
  pools: [Powerset | null, Powerset | null, Powerset | null, Powerset | null];
  ancillary: Powerset | null;  // Unlocks at level 35+
}

interface PowerEntry {
  power: Power;
  level: number;          // Level when power was taken
  slots: Slot[];          // 1-6 slots (base + 5 additional)
}

interface Slot {
  enhancement: Enhancement | null;
  level: number;          // Enhancement level (relative -3 to +3)
  boosted: boolean;       // +5 from catalyst
  attuned: boolean;       // Scales with character level
}
```

**State Change Triggers**:
- Archetype changed → Clear powersets, reset build, recalculate all
- Powerset changed → Clear powers from that category, recalculate
- Power picked → Add to build, recalculate power and totals
- Power removed → Remove from build, recalculate totals
- Slot added → Recalculate power
- Enhancement slotted → Recalculate power, update set bonuses, recalculate totals
- Enhancement removed → Same as slotting
- Level changed → Unlock/lock powers, recalculate all

### 2. Database Access (DatabaseAPI)

**Pattern**: Static singleton providing cached database access to power data

**Responsibilities**:
- Load powers, archetypes, powersets, enhancements, and enhancement sets on startup
- Provide static accessor methods throughout application
- Cache data permanently in memory (game database doesn't change during session)
- No network calls after initial load

**Key Methods** (C# static class):
```csharp
public static class DatabaseAPI
{
    public static IPower GetPowerByFullName(string fullName);
    public static Archetype GetArchetypeByName(string name);
    public static EnhancementSet GetSetByName(string name);
    public static List<IPower> GetPowersInPowerset(string powersetName);
    public static List<Powerset> GetPowersetsByArchetype(string archetypeName);
}
```

**Web Equivalent**: TanStack Query with `staleTime: Infinity`

Since the powers database is static (loaded from game files), we can cache indefinitely:

```typescript
const { data: archetypes } = useQuery({
  queryKey: ['archetypes'],
  queryFn: () => api.get('/archetypes'),
  staleTime: Infinity,  // Never refetch - data doesn't change
  cacheTime: Infinity,  // Keep in cache forever
});
```

### 3. Calculation Orchestration (Build.cs)

**Pattern**: Build object coordinates all calculations and maintains calculated state

**Trigger Points** (when `Recalculate()` is called):
- Power added/removed from build
- Enhancement slotted/removed from any power
- Archetype changed (affects all power calculations)
- Level changed (affects power availability and enhancement effectiveness)
- Set bonus activation changes

**Calculation Flow**:
```
User Action (e.g., slot enhancement)
  ↓
clsToonX.cs: Update build state
  ↓
Build.Recalculate() triggered
  ↓
FOR EACH PowerEntry in Powers:
  ├─> PowerEntry.Calculate()
  │   ├─> Load base power data from Power.cs
  │   ├─> Apply Archetype scale modifier (damage, buff, debuff)
  │   ├─> Sum enhancement bonuses by attribute
  │   ├─> Apply Enhancement Diminishing Returns (ED curves)
  │   ├─> Multiply base × (1 + ED_bonus)
  │   ├─> Apply global modifiers (set bonuses, globals)
  │   └─> Store FinalDamage, FinalAccuracy, FinalRecharge, etc.
  └─> Add power effects to global effect pool
  ↓
CalculateSetBonuses()
  ├─> Scan all slotted enhancements
  ├─> Count set pieces per power (2/3/4/5/6 completion)
  ├─> Activate set bonuses for completed sets
  ├─> Apply Rule of 5 suppression (max 5 of same bonus)
  └─> Add set bonus effects to global effect pool
  ↓
GetBuildTotals()
  ├─> GroupedFx.Aggregate() - Combine all effects
  ├─> Sum defense from all sources (powers + sets)
  ├─> Sum resistance from all sources
  ├─> Sum damage bonuses, recharge bonuses, etc.
  ├─> Apply archetype caps (defense, resistance, damage)
  └─> Return Stats object with final totals
  ↓
Fire UI update events
  ↓
All subscribed UI controls refresh automatically
```

**Web Equivalent**: 
```typescript
// In Zustand store
recalculate: async () => {
  set({ isCalculating: true });
  try {
    const buildData = get().exportBuild();
    
    // Backend does ALL calculation logic (Build.cs, PowerEntry.cs, etc.)
    const response = await api.post('/calculations/totals', buildData);
    const totals = await response.json();
    
    set({ totals, isCalculating: false });
  } catch (error) {
    console.error('Calculation failed:', error);
    set({ isCalculating: false, totals: null });
  }
};
```

Key difference: Web sends build data to FastAPI backend, which performs all calculations server-side using Python implementation of MidsReborn calculation logic.

### 4. Observer Pattern (UI Updates)

**Pattern**: UI controls subscribe to character/build change events and auto-refresh

**Implementation in MidsReborn**:
```csharp
// Character state fires events
public event EventHandler CharacterChanged;
public event EventHandler BuildUpdated;

// UI controls subscribe
MidsContext.Character.CharacterChanged += OnCharacterChanged;
MidsContext.Character.BuildUpdated += OnBuildUpdated;

// When state changes:
CharacterChanged?.Invoke(this, EventArgs.Empty);

// All subscribed controls automatically refresh
private void OnCharacterChanged(object sender, EventArgs e)
{
    this.Refresh();  // Redraw UI
}
```

**Web Equivalent**:

React's built-in reactivity + Zustand subscriptions replace manual observer pattern:

```typescript
// Components automatically re-render when store state changes
function DefensePanel() {
  const totals = useCharacterStore((state) => state.totals);
  
  // Component re-renders automatically when totals changes
  return <div>{totals?.defense.smashing}</div>;
}

// For non-React code (e.g., auto-save), use explicit subscription
useEffect(() => {
  const unsubscribe = useCharacterStore.subscribe(
    (state) => state.powers,  // Watch specific state
    () => {
      console.log('Powers changed, trigger auto-save');
    }
  );
  
  return unsubscribe;
}, []);
```

No manual event registration needed - React handles reactivity automatically.

## Web Architecture Design

### TanStack Query (Server State)

**Purpose**: Manage database data and shared build fetching from backend

**Queries to Implement**:

```typescript
// ============================================================================
// DATABASE QUERIES (Static data - cache forever)
// ============================================================================

// Archetypes
const { data: archetypes, isLoading, error } = useQuery({
  queryKey: ['archetypes'],
  queryFn: () => api.get('/archetypes').then(r => r.data),
  staleTime: Infinity,  // Never refetch
  cacheTime: Infinity,  // Never remove from cache
});

// Powersets (all)
const { data: powersets } = useQuery({
  queryKey: ['powersets'],
  queryFn: () => api.get('/powersets').then(r => r.data),
  staleTime: Infinity,
  cacheTime: Infinity,
});

// Powersets filtered by archetype
const { data: archetypePowersets } = useQuery({
  queryKey: ['powersets', archetypeId],
  queryFn: () => api.get(`/powersets?archetype_id=${archetypeId}`).then(r => r.data),
  enabled: !!archetypeId,  // Only run when archetype selected
  staleTime: Infinity,
  cacheTime: Infinity,
});

// Powers in a specific powerset
const { data: powers } = useQuery({
  queryKey: ['powers', powersetId],
  queryFn: () => api.get(`/powersets/${powersetId}/powers`).then(r => r.data),
  enabled: !!powersetId,
  staleTime: Infinity,
  cacheTime: Infinity,
});

// All enhancements
const { data: enhancements } = useQuery({
  queryKey: ['enhancements'],
  queryFn: () => api.get('/enhancements').then(r => r.data),
  staleTime: Infinity,
  cacheTime: Infinity,
});

// Enhancement sets
const { data: enhancementSets } = useQuery({
  queryKey: ['enhancement-sets'],
  queryFn: () => api.get('/enhancement-sets').then(r => r.data),
  staleTime: Infinity,
  cacheTime: Infinity,
});

// ============================================================================
// BUILD CALCULATION QUERIES (Dynamic - recalculate on demand)
// ============================================================================

// Build totals calculation (main calculation endpoint)
const { data: totals, isLoading: isCalculating, refetch: recalculate } = useQuery({
  queryKey: ['totals', buildData],
  queryFn: () => api.post('/calculations/totals', buildData).then(r => r.data),
  enabled: !!buildData && buildData.powers.length > 0,  // Only run when build exists
  staleTime: 0,  // Always recalculate (don't use stale data)
  cacheTime: 0,  // Don't cache (build changes frequently)
});

// ============================================================================
// BUILD PERSISTENCE QUERIES (Dynamic - fetch shared builds)
// ============================================================================

// Fetch shared build by ID
const { data: sharedBuild } = useQuery({
  queryKey: ['build', buildId],
  queryFn: () => api.get(`/builds/${buildId}`).then(r => r.data),
  enabled: !!buildId,
  staleTime: 5 * 60 * 1000,  // 5 minutes (builds don't change often)
});

// Share build mutation
const shareMutation = useMutation({
  mutationFn: (buildData: BuildData) => api.post('/builds', buildData),
  onSuccess: (response) => {
    // response: { id, url, downloadUrl, imageUrl, expiresAt }
    console.log('Build shared:', response.url);
  },
});
```

**Configuration**:
```typescript
// app/providers.tsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,  // Don't refetch on tab focus
      retry: 1,                      // Retry failed queries once
      staleTime: 5 * 60 * 1000,      // 5 minutes default (overridden per query)
    },
  },
});

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <QueryClientProvider client={queryClient}>
      {children}
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
}
```

### Zustand (Client State)

**Purpose**: Manage character build state with undo/redo support

**Store Structure**:

```typescript
// stores/characterStore.ts
import { create } from 'zustand';
import { temporal } from 'zustand/middleware';
import { devtools, persist } from 'zustand/middleware';

interface CharacterState {
  // ============================================================================
  // CHARACTER IDENTITY
  // ============================================================================
  name: string;
  archetype: Archetype | null;
  origin: Origin | null;
  alignment: Alignment | null;  // Hero, Villain, Vigilante, Rogue
  level: number;  // 1-50
  
  // ============================================================================
  // POWERSET SELECTIONS
  // ============================================================================
  primaryPowerset: Powerset | null;
  secondaryPowerset: Powerset | null;
  poolPowersets: (Powerset | null)[];  // Array of 4 pool power slots
  ancillaryPowerset: Powerset | null;  // Epic/Ancillary (level 35+)
  
  // ============================================================================
  // BUILD DATA (Power picks and slotting)
  // ============================================================================
  powers: PowerEntry[];  // All selected powers with slots
  
  // ============================================================================
  // CALCULATED TOTALS (From backend API)
  // ============================================================================
  totals: CalculatedTotals | null;  // Defense, resistance, damage, etc.
  isCalculating: boolean;            // Loading state for calculations
  
  // ============================================================================
  // ACTIONS - Character Identity
  // ============================================================================
  setName: (name: string) => void;
  setArchetype: (archetype: Archetype) => void;
  setOrigin: (origin: Origin) => void;
  setAlignment: (alignment: Alignment) => void;
  setLevel: (level: number) => void;
  
  // ============================================================================
  // ACTIONS - Powerset Selection
  // ============================================================================
  setPrimaryPowerset: (powerset: Powerset) => void;
  setSecondaryPowerset: (powerset: Powerset) => void;
  setPoolPowerset: (index: number, powerset: Powerset | null) => void;  // index 0-3
  setAncillaryPowerset: (powerset: Powerset) => void;
  
  // ============================================================================
  // ACTIONS - Power Selection
  // ============================================================================
  addPower: (power: Power, level: number) => void;
  removePower: (powerIndex: number) => void;
  movePower: (fromIndex: number, toIndex: number) => void;  // Reorder powers
  
  // ============================================================================
  // ACTIONS - Slotting
  // ============================================================================
  addSlot: (powerIndex: number) => void;                    // Add empty slot (max 6)
  removeSlot: (powerIndex: number, slotIndex: number) => void;
  slotEnhancement: (powerIndex: number, slotIndex: number, enhancement: Enhancement, level: number) => void;
  removeEnhancement: (powerIndex: number, slotIndex: number) => void;
  
  // ============================================================================
  // ACTIONS - Calculations
  // ============================================================================
  recalculate: () => Promise<void>;  // Trigger backend calculation
  
  // ============================================================================
  // ACTIONS - Build Management
  // ============================================================================
  loadBuild: (build: BuildData) => void;       // Load from file/URL
  clearBuild: () => void;                       // Reset to empty
  exportBuild: () => BuildData;                 // Export to JSON
}

export const useCharacterStore = create<CharacterState>()(
  devtools(
    persist(
      temporal(
        (set, get) => ({
          // ============================================================================
          // INITIAL STATE
          // ============================================================================
          name: '',
          archetype: null,
          origin: null,
          alignment: null,
          level: 1,
          primaryPowerset: null,
          secondaryPowerset: null,
          poolPowersets: [null, null, null, null],
          ancillaryPowerset: null,
          powers: [],
          totals: null,
          isCalculating: false,

          // ============================================================================
          // CHARACTER IDENTITY ACTIONS
          // ============================================================================
          setName: (name) => set({ name }),
          
          setArchetype: (archetype) => {
            set({
              archetype,
              // Clear powersets when archetype changes (different options available)
              primaryPowerset: null,
              secondaryPowerset: null,
              poolPowersets: [null, null, null, null],
              ancillaryPowerset: null,
              powers: [],  // Clear all powers
              totals: null,
            });
            // Recalculate after clearing
            get().recalculate();
          },
          
          setOrigin: (origin) => set({ origin }),
          setAlignment: (alignment) => set({ alignment }),
          setLevel: (level) => {
            set({ level });
            // Level change may unlock/lock powers, so recalculate
            get().recalculate();
          },

          // ============================================================================
          // POWERSET SELECTION ACTIONS
          // ============================================================================
          setPrimaryPowerset: (powerset) => {
            set({
              primaryPowerset: powerset,
              // Clear powers from old primary powerset
              powers: get().powers.filter(p => p.power.powersetId !== get().primaryPowerset?.id),
            });
            get().recalculate();
          },
          
          setSecondaryPowerset: (powerset) => {
            set({
              secondaryPowerset: powerset,
              powers: get().powers.filter(p => p.power.powersetId !== get().secondaryPowerset?.id),
            });
            get().recalculate();
          },
          
          setPoolPowerset: (index, powerset) => {
            const poolPowersets = [...get().poolPowersets];
            const oldPowerset = poolPowersets[index];
            poolPowersets[index] = powerset;
            
            set({
              poolPowersets,
              // Clear powers from old pool powerset
              powers: oldPowerset
                ? get().powers.filter(p => p.power.powersetId !== oldPowerset.id)
                : get().powers,
            });
            get().recalculate();
          },
          
          setAncillaryPowerset: (powerset) => {
            set({
              ancillaryPowerset: powerset,
              powers: get().powers.filter(p => p.power.powersetId !== get().ancillaryPowerset?.id),
            });
            get().recalculate();
          },

          // ============================================================================
          // POWER SELECTION ACTIONS
          // ============================================================================
          addPower: (power, level) => {
            set({
              powers: [
                ...get().powers,
                {
                  power,
                  level,
                  slots: [{ enhancement: null, level: 50, boosted: false, attuned: false }],  // Base slot
                },
              ],
            });
            get().recalculate();
          },
          
          removePower: (powerIndex) => {
            set({
              powers: get().powers.filter((_, i) => i !== powerIndex),
            });
            get().recalculate();
          },
          
          movePower: (fromIndex, toIndex) => {
            const powers = [...get().powers];
            const [moved] = powers.splice(fromIndex, 1);
            powers.splice(toIndex, 0, moved);
            set({ powers });
            // No recalculation needed (just reordering)
          },

          // ============================================================================
          // SLOTTING ACTIONS
          // ============================================================================
          addSlot: (powerIndex) => {
            const powers = [...get().powers];
            const power = powers[powerIndex];
            
            if (power.slots.length < 6) {  // Max 6 slots
              power.slots.push({
                enhancement: null,
                level: 50,
                boosted: false,
                attuned: false,
              });
              set({ powers });
              get().recalculate();
            }
          },
          
          removeSlot: (powerIndex, slotIndex) => {
            const powers = [...get().powers];
            powers[powerIndex].slots.splice(slotIndex, 1);
            set({ powers });
            get().recalculate();
          },
          
          slotEnhancement: (powerIndex, slotIndex, enhancement, level) => {
            const powers = [...get().powers];
            powers[powerIndex].slots[slotIndex] = {
              enhancement,
              level,
              boosted: false,
              attuned: false,
            };
            set({ powers });
            get().recalculate();
          },
          
          removeEnhancement: (powerIndex, slotIndex) => {
            const powers = [...get().powers];
            powers[powerIndex].slots[slotIndex].enhancement = null;
            set({ powers });
            get().recalculate();
          },

          // ============================================================================
          // CALCULATION ACTION
          // ============================================================================
          recalculate: async () => {
            const buildData = get().exportBuild();
            
            // Don't calculate if no powers in build
            if (buildData.powers.length === 0) {
              set({ totals: null, isCalculating: false });
              return;
            }
            
            set({ isCalculating: true });
            try {
              const response = await fetch('/api/calculations/totals', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(buildData),
              });
              
              if (!response.ok) {
                throw new Error(`Calculation failed: ${response.statusText}`);
              }
              
              const totals = await response.json();
              set({ totals, isCalculating: false });
            } catch (error) {
              console.error('Calculation failed:', error);
              set({ isCalculating: false, totals: null });
            }
          },

          // ============================================================================
          // BUILD MANAGEMENT ACTIONS
          // ============================================================================
          loadBuild: (build) => {
            set({
              name: build.name,
              archetype: build.archetype,
              origin: build.origin,
              alignment: build.alignment,
              level: build.level,
              primaryPowerset: build.primaryPowerset,
              secondaryPowerset: build.secondaryPowerset,
              poolPowersets: build.poolPowersets,
              ancillaryPowerset: build.ancillaryPowerset,
              powers: build.powers,
            });
            get().recalculate();
          },
          
          clearBuild: () => {
            set({
              name: '',
              archetype: null,
              origin: null,
              alignment: null,
              level: 1,
              primaryPowerset: null,
              secondaryPowerset: null,
              poolPowersets: [null, null, null, null],
              ancillaryPowerset: null,
              powers: [],
              totals: null,
              isCalculating: false,
            });
          },
          
          exportBuild: () => ({
            name: get().name,
            archetype: get().archetype,
            origin: get().origin,
            alignment: get().alignment,
            level: get().level,
            primaryPowerset: get().primaryPowerset,
            secondaryPowerset: get().secondaryPowerset,
            poolPowersets: get().poolPowersets,
            ancillaryPowerset: get().ancillaryPowerset,
            powers: get().powers,
          }),
        }),
        {
          limit: 50,  // Store last 50 states for undo/redo
          equality: (a, b) => a === b,
        }
      ),
      {
        name: 'character-build-storage',
        partialize: (state) => ({
          // Only persist essential fields (not calculated totals)
          name: state.name,
          archetype: state.archetype,
          origin: state.origin,
          alignment: state.alignment,
          level: state.level,
          primaryPowerset: state.primaryPowerset,
          secondaryPowerset: state.secondaryPowerset,
          poolPowersets: state.poolPowersets,
          ancillaryPowerset: state.ancillaryPowerset,
          powers: state.powers,
        }),
      }
    ),
    { name: 'CharacterStore' }
  )
);

// ============================================================================
// UNDO/REDO EXPORTS
// ============================================================================
export const undo = () => useCharacterStore.temporal.getState().undo();
export const redo = () => useCharacterStore.temporal.getState().redo();
export const canUndo = () => useCharacterStore.temporal.getState().pastStates.length > 0;
export const canRedo = () => useCharacterStore.temporal.getState().futureStates.length > 0;
```

**Middleware Configuration**:

1. **`temporal`**: Undo/redo support (innermost - wraps state changes)
2. **`persist`**: LocalStorage auto-save (middle - wraps temporal)
3. **`devtools`**: Redux DevTools integration (outermost - wraps everything)

### API Client Service

**Base Configuration**:

```typescript
// services/api.ts
import axios from 'axios';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,  // 10 second timeout
});

// ============================================================================
// REQUEST INTERCEPTOR (Add auth token if available)
// ============================================================================
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// ============================================================================
// RESPONSE INTERCEPTOR (Error handling)
// ============================================================================
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // Server responded with error status
      console.error('API Error:', error.response.status, error.response.data);
      
      if (error.response.status === 401) {
        // Unauthorized - clear auth token
        localStorage.removeItem('auth_token');
      }
    } else if (error.request) {
      // No response received
      console.error('Network Error:', error.message);
    } else {
      // Request setup error
      console.error('Request Error:', error.message);
    }
    
    return Promise.reject(error);
  }
);

export default api;
```

**Service Modules**:

```typescript
// services/archetypeApi.ts
import api from './api';
import type { Archetype } from '@/types/character.types';

export const archetypeApi = {
  getAll: async (): Promise<Archetype[]> => {
    const response = await api.get('/archetypes');
    return response.data;
  },
  
  getById: async (id: number): Promise<Archetype> => {
    const response = await api.get(`/archetypes/${id}`);
    return response.data;
  },
};
```

```typescript
// services/powerApi.ts
import api from './api';
import type { Power, Powerset } from '@/types/power.types';

export const powerApi = {
  getAllPowersets: async (): Promise<Powerset[]> => {
    const response = await api.get('/powersets');
    return response.data;
  },
  
  getPowersetsByArchetype: async (archetypeId: number): Promise<Powerset[]> => {
    const response = await api.get(`/powersets?archetype_id=${archetypeId}`);
    return response.data;
  },
  
  getPowersInPowerset: async (powersetId: number): Promise<Power[]> => {
    const response = await api.get(`/powersets/${powersetId}/powers`);
    return response.data;
  },
  
  getPowerById: async (powerId: number): Promise<Power> => {
    const response = await api.get(`/powers/${powerId}`);
    return response.data;
  },
};
```

```typescript
// services/enhancementApi.ts
import api from './api';
import type { Enhancement, EnhancementSet } from '@/types/enhancement.types';

export const enhancementApi = {
  getAll: async (): Promise<Enhancement[]> => {
    const response = await api.get('/enhancements');
    return response.data;
  },
  
  getById: async (id: number): Promise<Enhancement> => {
    const response = await api.get(`/enhancements/${id}`);
    return response.data;
  },
  
  getAllSets: async (): Promise<EnhancementSet[]> => {
    const response = await api.get('/enhancement-sets');
    return response.data;
  },
  
  getSetById: async (id: number): Promise<EnhancementSet> => {
    const response = await api.get(`/enhancement-sets/${id}`);
    return response.data;
  },
};
```

```typescript
// services/calculationApi.ts
import api from './api';
import type { BuildData, CalculatedTotals } from '@/types/build.types';

export const calculationApi = {
  calculateTotals: async (buildData: BuildData): Promise<CalculatedTotals> => {
    const response = await api.post('/calculations/totals', buildData);
    return response.data;
  },
  
  calculatePower: async (powerData: any): Promise<any> => {
    const response = await api.post('/calculations/power', powerData);
    return response.data;
  },
  
  calculateSetBonuses: async (buildData: BuildData): Promise<any> => {
    const response = await api.post('/calculations/set-bonuses', buildData);
    return response.data;
  },
};
```

```typescript
// services/buildApi.ts
import api from './api';
import type { BuildData, SharedBuildResponse } from '@/types/build.types';

export const buildApi = {
  shareBuild: async (buildData: BuildData): Promise<SharedBuildResponse> => {
    const response = await api.post('/builds', buildData);
    return response.data;  // { id, url, downloadUrl, imageUrl, expiresAt }
  },
  
  getBuildById: async (buildId: string): Promise<BuildData> => {
    const response = await api.get(`/builds/${buildId}`);
    return response.data;
  },
  
  updateBuild: async (buildId: string, buildData: BuildData): Promise<BuildData> => {
    const response = await api.put(`/builds/${buildId}`, buildData);
    return response.data;
  },
  
  deleteBuild: async (buildId: string): Promise<void> => {
    await api.delete(`/builds/${buildId}`);
  },
};
```

## Undo/Redo Implementation

### Zustand Temporal Middleware

**Setup**:
```typescript
import { create } from 'zustand';
import { temporal } from 'zustand/middleware';

export const useCharacterStore = create<CharacterState>()(
  temporal(
    (set, get) => ({
      // ... state and actions
    }),
    {
      limit: 50,  // Store last 50 states (balance between UX and memory)
      equality: (a, b) => a === b,  // Default equality check
    }
  )
);
```

**Usage**:
```typescript
// hooks/useUndoRedo.ts
import { useCharacterStore } from '@/stores/characterStore';

export function useUndoRedo() {
  const undo = () => useCharacterStore.temporal.getState().undo();
  const redo = () => useCharacterStore.temporal.getState().redo();
  const canUndo = () => useCharacterStore.temporal.getState().pastStates.length > 0;
  const canRedo = () => useCharacterStore.temporal.getState().futureStates.length > 0;
  
  return { undo, redo, canUndo, canRedo };
}
```

**Keyboard Shortcuts**:
```typescript
// hooks/useKeyboardShortcuts.ts
import { useEffect } from 'react';
import { useUndoRedo } from './useUndoRedo';

export function useKeyboardShortcuts() {
  const { undo, redo, canUndo, canRedo } = useUndoRedo();
  
  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      // Undo: Ctrl/Cmd + Z
      if ((e.metaKey || e.ctrlKey) && e.key === 'z' && !e.shiftKey) {
        if (canUndo()) {
          e.preventDefault();
          undo();
        }
      }
      
      // Redo: Ctrl/Cmd + Shift + Z
      if ((e.metaKey || e.ctrlKey) && e.key === 'z' && e.shiftKey) {
        if (canRedo()) {
          e.preventDefault();
          redo();
        }
      }
      
      // Alternative Redo: Ctrl/Cmd + Y
      if ((e.metaKey || e.ctrlKey) && e.key === 'y') {
        if (canRedo()) {
          e.preventDefault();
          redo();
        }
      }
    };
    
    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [undo, redo, canUndo, canRedo]);
}
```

**What Gets Tracked by Temporal Middleware**:
- All character property changes (name, archetype, origin, alignment, level)
- All powerset selections (primary, secondary, pools, ancillary)
- All power additions/removals
- All slot additions/removals
- All enhancement slotting/removal changes

**What Doesn't Get Tracked** (excluded from undo/redo):
- UI preferences (separate `uiStore` - not wrapped in temporal)
- Calculated totals (derived from build, recalculated on undo/redo)
- API responses (server data)
- Loading states (`isCalculating`)

## Calculation Debouncing Strategy

### Auto-Recalculate Hook

```typescript
// hooks/useAutoCalculate.ts
import { useEffect, useRef } from 'react';
import { useCharacterStore } from '@/stores/characterStore';
import { useDebouncedCallback } from 'use-debounce';

export function useAutoCalculate() {
  const recalculate = useCharacterStore((state) => state.recalculate);
  const powers = useCharacterStore((state) => state.powers);
  const archetype = useCharacterStore((state) => state.archetype);
  const level = useCharacterStore((state) => state.level);
  
  const debouncedRecalculate = useDebouncedCallback(
    () => {
      console.log('Auto-recalculating build totals...');
      recalculate();
    },
    200  // 200ms debounce - balance between responsiveness and API load
  );
  
  useEffect(() => {
    // Trigger recalculation when build changes
    debouncedRecalculate();
  }, [powers, archetype, level, debouncedRecalculate]);
  
  // Cleanup on unmount
  useEffect(() => {
    return () => {
      debouncedRecalculate.cancel();
    };
  }, [debouncedRecalculate]);
}
```

**Trigger Points**:

| Action | Debounce Strategy | Rationale |
|--------|-------------------|-----------|
| Archetype change | Immediate (0ms) | Major change, user expects immediate feedback |
| Power addition | Debounced (200ms) | May add multiple powers rapidly |
| Enhancement slotting | Debounced (200ms) | May slot multiple enhancements rapidly |
| Slot addition | Debounced (200ms) | May add multiple slots at once |
| Level change | Debounced (200ms) | Rare action, but may happen via slider |
| Multiple rapid changes | Batched into one call | Debounce ensures only last change triggers API |

**Usage in Layout**:
```typescript
// app/builder/page.tsx
export default function BuilderPage() {
  useKeyboardShortcuts();  // Enable Ctrl+Z undo/redo
  useAutoCalculate();      // Enable auto-recalculation on changes
  useAutoSave();           // Enable auto-save to localStorage
  
  return (
    <BuildLayout>
      {/* ... build UI */}
    </BuildLayout>
  );
}
```

## TypeScript Type Definitions

### Core Types

```typescript
// types/character.types.ts
export interface Archetype {
  id: number;
  name: string;
  displayName: string;
  
  // Damage scaling
  damageScale: number;       // Tanker: 0.8, Scrapper: 1.125, Blaster: 1.125
  
  // Buff/debuff modifiers
  buffModifier: number;      // Affects buff strength (Tanker: 0.75, Defender: 1.0)
  debuffModifier: number;    // Affects debuff strength
  
  // Control modifiers
  controlDuration: number;   // Hold/stun duration multiplier
  
  // Caps
  defenseCap: number;        // 45% for most, 50% for Tanker/Brute
  resistanceCap: number;     // 75% for most, 90% for Tanker/Brute
  damageCap: number;         // 400% for Tanker, 500% for Scrapper, etc.
  
  // Base stats
  baseHP: number;            // HP at level 50
  baseRegen: number;         // Regen rate (HP/s)
  baseRecovery: number;      // Endurance recovery (End/s)
}

export interface Origin {
  id: number;
  name: string;
  displayName: string;
  description: string;
}

export interface Alignment {
  id: number;
  name: 'Hero' | 'Villain' | 'Vigilante' | 'Rogue';
  displayName: string;
}
```

```typescript
// types/power.types.ts
export interface Powerset {
  id: number;
  name: string;
  displayName: string;
  archetypeId: number;
  type: 'Primary' | 'Secondary' | 'Pool' | 'Ancillary' | 'Epic';
  iconPath?: string;
}

export interface Power {
  id: number;
  name: string;
  displayName: string;
  description: string;
  powersetId: number;
  
  // Availability
  levelAvailable: number;    // Minimum level to take power
  prerequisites: number[];   // Power IDs that must be taken first
  
  // Base attributes
  damage: number;
  accuracy: number;
  recharge: number;
  endurance: number;
  range: number;
  
  // Effects
  effects: Effect[];
  
  // UI
  iconPath: string;
}

export interface Effect {
  id: number;
  type: EffectType;
  aspect: EffectAspect;      // Damage type, control type, etc.
  magnitude: number;
  duration: number;
  probability: number;       // 0-1 (100% = 1.0)
  isEnhanceable: boolean;
}

export enum EffectType {
  Damage = 'Damage',
  Defense = 'Defense',
  Resistance = 'Resistance',
  Heal = 'Heal',
  Endurance = 'Endurance',
  ToHit = 'ToHit',
  Accuracy = 'Accuracy',
  Recharge = 'Recharge',
  Hold = 'Hold',
  Stun = 'Stun',
  Sleep = 'Sleep',
  // ... 50+ effect types
}

export enum EffectAspect {
  Smashing = 'Smashing',
  Lethal = 'Lethal',
  Fire = 'Fire',
  Cold = 'Cold',
  Energy = 'Energy',
  Negative = 'Negative',
  Psionic = 'Psionic',
  Toxic = 'Toxic',
  Melee = 'Melee',
  Ranged = 'Ranged',
  AoE = 'AoE',
  // ...
}
```

```typescript
// types/enhancement.types.ts
export interface Enhancement {
  id: number;
  name: string;
  displayName: string;
  type: 'TO' | 'DO' | 'SO' | 'IO';
  grade: number;             // 10-50 for IOs
  setId?: number;            // If part of enhancement set
  
  // Bonuses
  bonuses: EnhancementBonus[];
  
  // UI
  iconPath: string;
}

export interface EnhancementBonus {
  attribute: string;         // 'Damage', 'Accuracy', 'Recharge', etc.
  value: number;             // Percentage bonus (e.g., 42.4 for +42.4%)
}

export interface EnhancementSet {
  id: number;
  name: string;
  displayName: string;
  type: string;              // 'Healing', 'Defense', 'Damage', etc.
  levelRange: [number, number];  // [10, 30] for level 10-30 set
  
  // Set bonuses by piece count
  bonuses: {
    2?: SetBonus[];
    3?: SetBonus[];
    4?: SetBonus[];
    5?: SetBonus[];
    6?: SetBonus[];
  };
  
  // Enhancements in set
  enhancements: Enhancement[];
}

export interface SetBonus {
  attribute: string;
  value: number;
  description: string;
}

export interface Slot {
  enhancement: Enhancement | null;
  level: number;             // Enhancement level (relative -3 to +3 from character level)
  boosted: boolean;          // +5 from catalyst
  attuned: boolean;          // Scales with character level
}
```

```typescript
// types/build.types.ts
export interface PowerEntry {
  power: Power;
  level: number;             // Level when power was taken
  slots: Slot[];             // 1-6 slots (base + 5 additional)
}

export interface BuildData {
  // Character identity
  name: string;
  archetype: Archetype | null;
  origin: Origin | null;
  alignment: Alignment | null;
  level: number;
  
  // Powersets
  primaryPowerset: Powerset | null;
  secondaryPowerset: Powerset | null;
  poolPowersets: (Powerset | null)[];
  ancillaryPowerset: Powerset | null;
  
  // Powers
  powers: PowerEntry[];
}

export interface CalculatedTotals {
  // Defense (typed)
  defense: {
    smashing: number;
    lethal: number;
    fire: number;
    cold: number;
    energy: number;
    negative: number;
    psionic: number;
    toxic: number;
  };
  
  // Defense (positional)
  defensePositional: {
    melee: number;
    ranged: number;
    aoe: number;
  };
  
  // Resistance (typed)
  resistance: {
    smashing: number;
    lethal: number;
    fire: number;
    cold: number;
    energy: number;
    negative: number;
    psionic: number;
    toxic: number;
  };
  
  // HP/Endurance
  maxHP: number;
  maxEndurance: number;
  regeneration: number;       // HP/s
  recovery: number;           // End/s
  
  // Global modifiers
  globalRecharge: number;     // Percentage (e.g., 70 for +70% recharge)
  globalAccuracy: number;
  globalDamage: number;
  
  // Misc
  movementSpeed: number;
  jumpHeight: number;
  flySpeed: number;
  
  // Set bonuses (for display)
  activeSets: {
    setId: number;
    setName: string;
    piecesSlotted: number;
    bonuses: SetBonus[];
  }[];
}

export interface SharedBuildResponse {
  id: string;
  url: string;               // Permalink URL
  downloadUrl: string;       // .mbd file download
  imageUrl: string;          // Build infographic
  expiresAt: string;         // ISO timestamp
}
```

## API Integration Points

### Backend Endpoints

**Database Endpoints** (Static data - cache forever):
- `GET /api/archetypes` → `Archetype[]`
- `GET /api/powersets` → `Powerset[]`
- `GET /api/powersets?archetype_id={id}` → `Powerset[]` (filtered)
- `GET /api/powersets/{id}/powers` → `Power[]`
- `GET /api/powers/{id}` → `Power`
- `GET /api/enhancements` → `Enhancement[]`
- `GET /api/enhancements/{id}` → `Enhancement`
- `GET /api/enhancement-sets` → `EnhancementSet[]`
- `GET /api/enhancement-sets/{id}` → `EnhancementSet`

**Calculation Endpoints** (Dynamic - recalculate on demand):
- `POST /api/calculations/totals` → `CalculatedTotals`
  - Body: `BuildData` (character + powers + slotting)
  - Returns: Aggregated stats with archetype caps applied
- `POST /api/calculations/power` → `PowerCalculation`
  - Body: Single power with slots
  - Returns: Calculated power stats
- `POST /api/calculations/set-bonuses` → `SetBonusCalculation`
  - Body: `BuildData`
  - Returns: Active set bonuses with Rule of 5 applied

**Build Endpoints** (Future - for build sharing):
- `POST /api/builds` → `SharedBuildResponse`
  - Body: `BuildData`
  - Returns: { id, url, downloadUrl, imageUrl, expiresAt }
- `GET /api/builds/{id}` → `BuildData`
  - Returns: Full build data for sharing/loading
- `PUT /api/builds/{id}` → `BuildData`
  - Body: `BuildData`
  - Returns: Updated build
- `DELETE /api/builds/{id}` → `void`
  - Deletes shared build (if user owns it)

## Implementation Notes

### Key Behaviors to Replicate from MidsReborn

1. **Immediate Feedback**: UI updates feel instant
   - Use optimistic updates where possible
   - Show loading state only for backend calculations
   - Local state updates (name, selections) are instant

2. **Batch Calculations**: Multiple rapid changes = one API call
   - 200ms debounce on all calculation triggers
   - Cancel pending calls if new changes occur
   - Show "Calculating..." indicator during API calls

3. **Undo Preservation**: Undo/redo works across all actions
   - Temporal middleware tracks all state changes
   - 50-state history (balance between UX and memory)
   - Keyboard shortcuts (Ctrl/Cmd+Z, Ctrl/Cmd+Shift+Z)

4. **Error Resilience**: Failed calculations don't break UI
   - Try/catch around all API calls
   - Display error messages to user
   - Keep previous totals on calculation failure
   - Retry button for manual retry

5. **Auto-Save**: Build auto-saves to localStorage
   - Debounced auto-save (2 seconds)
   - Persist middleware in Zustand
   - Load from localStorage on app start
   - Clear localStorage on explicit "New Build"

### Differences from MidsReborn

1. **Separation of Concerns**: State (Zustand) vs Server Data (TanStack Query)
   - MidsReborn: Static DatabaseAPI in memory
   - Web: TanStack Query with backend API calls
   - Benefit: Easier to scale, update data without client changes

2. **Async Calculations**: Backend API calls vs synchronous C# methods
   - MidsReborn: Calculations instant (local C# code)
   - Web: Calculations async (backend API)
   - Benefit: Offload heavy computation to server, lighter client

3. **React Reactivity**: No manual observer registration needed
   - MidsReborn: Manual event subscription (CharacterChanged, BuildUpdated)
   - Web: React re-renders automatically on state changes
   - Benefit: Simpler code, less boilerplate

4. **Immutable Updates**: Zustand enforces immutability
   - MidsReborn: Mutable objects (PowerEntry.Slots modified in-place)
   - Web: Immutable updates (spread operators, new arrays)
   - Benefit: Better debugging, time-travel debugging, undo/redo easier

5. **Type Safety**: Full TypeScript coverage
   - MidsReborn: C# with compile-time types
   - Web: TypeScript with strict mode
   - Benefit: Catch errors at compile time, better IDE support

## Testing Strategy

### Store Tests

```typescript
// stores/__tests__/characterStore.test.ts
import { renderHook, act } from '@testing-library/react';
import { useCharacterStore } from '../characterStore';

describe('characterStore', () => {
  beforeEach(() => {
    // Reset store before each test
    const { result } = renderHook(() => useCharacterStore());
    act(() => {
      result.current.clearBuild();
    });
  });
  
  it('sets archetype correctly', () => {
    const { result } = renderHook(() => useCharacterStore());
    
    act(() => {
      result.current.setArchetype(mockBlaster);
    });
    
    expect(result.current.archetype).toEqual(mockBlaster);
  });
  
  it('clears powersets when archetype changes', () => {
    const { result } = renderHook(() => useCharacterStore());
    
    act(() => {
      result.current.setArchetype(mockBlaster);
      result.current.setPrimaryPowerset(mockFireBlast);
    });
    
    expect(result.current.primaryPowerset).toEqual(mockFireBlast);
    
    act(() => {
      result.current.setArchetype(mockTanker);
    });
    
    expect(result.current.primaryPowerset).toBeNull();
  });
  
  it('adds power to build', () => {
    const { result } = renderHook(() => useCharacterStore());
    
    act(() => {
      result.current.addPower(mockFireBlast, 1);
    });
    
    expect(result.current.powers).toHaveLength(1);
    expect(result.current.powers[0].power).toEqual(mockFireBlast);
    expect(result.current.powers[0].level).toBe(1);
  });
  
  it('removes power from build', () => {
    const { result } = renderHook(() => useCharacterStore());
    
    act(() => {
      result.current.addPower(mockFireBlast, 1);
      result.current.addPower(mockFireBall, 2);
    });
    
    expect(result.current.powers).toHaveLength(2);
    
    act(() => {
      result.current.removePower(0);
    });
    
    expect(result.current.powers).toHaveLength(1);
    expect(result.current.powers[0].power).toEqual(mockFireBall);
  });
  
  it('supports undo/redo', () => {
    const { result } = renderHook(() => useCharacterStore());
    
    act(() => {
      result.current.setArchetype(mockBlaster);
    });
    
    expect(result.current.archetype).toEqual(mockBlaster);
    
    act(() => {
      useCharacterStore.temporal.getState().undo();
    });
    
    expect(result.current.archetype).toBeNull();
    
    act(() => {
      useCharacterStore.temporal.getState().redo();
    });
    
    expect(result.current.archetype).toEqual(mockBlaster);
  });
  
  it('adds slot to power', () => {
    const { result } = renderHook(() => useCharacterStore());
    
    act(() => {
      result.current.addPower(mockFireBlast, 1);
    });
    
    expect(result.current.powers[0].slots).toHaveLength(1);  // Base slot
    
    act(() => {
      result.current.addSlot(0);
    });
    
    expect(result.current.powers[0].slots).toHaveLength(2);
  });
  
  it('slots enhancement in power', () => {
    const { result } = renderHook(() => useCharacterStore());
    
    act(() => {
      result.current.addPower(mockFireBlast, 1);
      result.current.slotEnhancement(0, 0, mockDamageIO, 50);
    });
    
    expect(result.current.powers[0].slots[0].enhancement).toEqual(mockDamageIO);
    expect(result.current.powers[0].slots[0].level).toBe(50);
  });
});
```

### API Client Tests

```typescript
// services/__tests__/api.test.ts
import { archetypeApi } from '../archetypeApi';
import { powerApi } from '../powerApi';
import { calculationApi } from '../calculationApi';

describe('API Client', () => {
  it('fetches all archetypes', async () => {
    const archetypes = await archetypeApi.getAll();
    expect(archetypes).toBeInstanceOf(Array);
    expect(archetypes.length).toBeGreaterThan(0);
  });
  
  it('fetches archetype by ID', async () => {
    const archetype = await archetypeApi.getById(1);
    expect(archetype).toHaveProperty('id');
    expect(archetype).toHaveProperty('name');
    expect(archetype).toHaveProperty('damageScale');
  });
  
  it('handles 404 errors gracefully', async () => {
    await expect(archetypeApi.getById(9999))
      .rejects.toThrow();
  });
  
  it('fetches powersets by archetype', async () => {
    const powersets = await powerApi.getPowersetsByArchetype(1);
    expect(powersets).toBeInstanceOf(Array);
  });
  
  it('calculates build totals', async () => {
    const totals = await calculationApi.calculateTotals(mockBuildData);
    expect(totals).toHaveProperty('defense');
    expect(totals).toHaveProperty('resistance');
    expect(totals).toHaveProperty('maxHP');
  });
});
```

### Hook Tests

```typescript
// hooks/__tests__/useKeyboardShortcuts.test.ts
import { renderHook, act } from '@testing-library/react';
import { useKeyboardShortcuts } from '../useKeyboardShortcuts';
import { useCharacterStore } from '@/stores/characterStore';

describe('useKeyboardShortcuts', () => {
  it('triggers undo on Ctrl+Z', () => {
    const { result } = renderHook(() => useCharacterStore());
    renderHook(() => useKeyboardShortcuts());
    
    act(() => {
      result.current.setArchetype(mockBlaster);
    });
    
    expect(result.current.archetype).toEqual(mockBlaster);
    
    act(() => {
      const event = new KeyboardEvent('keydown', {
        key: 'z',
        ctrlKey: true,
      });
      window.dispatchEvent(event);
    });
    
    expect(result.current.archetype).toBeNull();
  });
  
  it('triggers redo on Ctrl+Shift+Z', () => {
    const { result } = renderHook(() => useCharacterStore());
    renderHook(() => useKeyboardShortcuts());
    
    act(() => {
      result.current.setArchetype(mockBlaster);
    });
    
    act(() => {
      useCharacterStore.temporal.getState().undo();
    });
    
    expect(result.current.archetype).toBeNull();
    
    act(() => {
      const event = new KeyboardEvent('keydown', {
        key: 'z',
        ctrlKey: true,
        shiftKey: true,
      });
      window.dispatchEvent(event);
    });
    
    expect(result.current.archetype).toEqual(mockBlaster);
  });
});
```

## Dependencies

### npm Packages to Install

```json
{
  "dependencies": {
    "@tanstack/react-query": "^5.56.2",
    "@tanstack/react-query-devtools": "^5.56.2",
    "zustand": "^5.0.0-rc.2",
    "axios": "^1.7.7",
    "use-debounce": "^10.0.3"
  },
  "devDependencies": {
    "@testing-library/react": "^16.0.1",
    "@testing-library/jest-dom": "^6.5.0",
    "@testing-library/user-event": "^14.5.2",
    "vitest": "^2.1.1"
  }
}
```

**Installation Command**:
```bash
npm install @tanstack/react-query @tanstack/react-query-devtools zustand axios use-debounce
npm install -D @testing-library/react @testing-library/jest-dom @testing-library/user-event
```

---

**Document Status**: ✅ Complete
**Epic**: 1.2 - State Management Setup
**Ready for**: Planning phase (Phase 3)
**Next Steps**: Review analysis, create implementation plan, execute Epic 1.2
