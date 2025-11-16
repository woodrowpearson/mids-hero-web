# MidsReborn UI Analysis: Epic 1.4 - API Client Integration

**Created**: 2025-11-16
**Epic**: 1.4 - API Client Integration
**MidsReborn Files Analyzed**: 
- `MidsReborn/Core/DatabaseAPI.cs`
- `MidsReborn/Core/Base/Data_Classes/Database.cs`
- `MidsReborn/MainModule.cs`
- `MidsReborn/Forms/Loader.cs`
- `MidsReborn/MrbAppContext.cs`

## Executive Summary

MidsReborn loads **all game data upfront at application startup** from binary database files using a **synchronous, blocking loading sequence**. Data is cached in a singleton `Database.Instance` for the entire application lifecycle with **no reloading or invalidation**. The desktop app uses a splash screen (`Loader`) to show loading progress with status messages for each data loading phase. For the web implementation, we'll replicate this aggressive caching strategy using **TanStack Query with long staleTime values**, but improve UX with **asynchronous loading, progressive enhancement, and React Suspense boundaries**.

**Key Findings**:
- **Sequential loading order**: Archetypes → Powersets → Powers → Enhancements (all in one database file)
- **Aggressive caching**: Load once, cache forever (data rarely changes)
- **Error handling**: Fatal errors exit app with MessageBox dialogs
- **Loading states**: Splash screen with text status updates
- **No lazy loading**: All data loaded upfront (except graphics loaded async)

---

## MidsReborn Data Access Patterns

### Pattern 1: Archetype Loading

**File**: `MidsReborn/Core/DatabaseAPI.cs:1713-1728`

**Pattern**: 
```csharp
// Part of LoadMainDatabase() - sequential read from binary file
if (reader.ReadString() != Files.Headers.Db.Archetypes) {
    MessageBox.Show(@"Expected Archetype Data, got something else!", @"Eeeeee!");
    return false;
}

Database.Classes = new Archetype?[reader.ReadInt32() + 1];
for (var index = 0; index < Database.Classes.Length; ++index) {
    Database.Classes[index] = new Archetype(reader) {
        Idx = index
    };
}
```

**Caching**: Loaded once at startup, stored in singleton `Database.Instance.Classes`, never reloaded

**Error Handling**: Shows MessageBox and returns `false`, causing `Application.Exit()` in caller

**Loading Sequence**: First data loaded after database metadata (version, date, issue)

**Count**: ~13 archetypes (fixed, rarely changes)

---

### Pattern 2: Powerset Loading

**File**: `MidsReborn/Core/DatabaseAPI.cs:1730-1751`

**Pattern**:
```csharp
// Immediately after archetypes in same file
if (reader.ReadString() != Files.Headers.Db.Powersets) {
    MessageBox.Show("Expected Powerset Data, got something else!", "Eeeeee!");
    return false;
}

var num3 = 0;
Database.Powersets = new IPowerset?[reader.ReadInt32() + 1];
for (var index = 0; index < Database.Powersets.Length; ++index) {
    Database.Powersets[index] = new Powerset(reader) {
        nID = index
    };
    ++num3;
    if (num3 <= 10) continue;
    num3 = 0;
    Application.DoEvents(); // UI responsiveness during blocking load
}
```

**Caching**: Loaded once, cached forever in `Database.Instance.Powersets`

**Dependencies**: Must load after archetypes (sequential binary file format)

**Loading**: Synchronous with periodic `Application.DoEvents()` every 10 powersets for UI responsiveness

**Count**: ~300+ powersets (including primary, secondary, pool, epic/ancillary)

---

### Pattern 3: Power Loading

**File**: `MidsReborn/Core/DatabaseAPI.cs:1753-1770`

**Pattern**:
```csharp
// Immediately after powersets in same file
if (reader.ReadString() != Files.Headers.Db.Powers) {
    MessageBox.Show("Expected Power Data, got something else!", "Eeeeee!");
    return false;
}

Database.Power = new IPower[reader.ReadInt32() + 1];
for (var index = 0; index < Database.Power.Length; index++) {
    Database.Power[index] = new Power(reader);
    ++num3;
    if (num3 <= 50) continue;
    num3 = 0;
    Application.DoEvents(); // Every 50 powers
}
```

**Caching**: All powers loaded upfront, cached forever

**Lazy Loading**: **None** - all ~3000+ powers loaded at startup

**Dependencies**: Must load after powersets (powers reference powerset IDs)

**Count**: ~3000+ powers across all powersets

**Performance**: Uses `Application.DoEvents()` every 50 powers to keep UI responsive during blocking load

---

### Pattern 4: Enhancement Loading

**File**: `MidsReborn/Core/DatabaseAPI.cs:2406-2480`

**Pattern**:
```csharp
// Separate file: LoadEnhancementDb(path)
public static void LoadEnhancementDb(string? iPath) {
    var path = Files.SelectDataFileLoad(Files.MxdbFileEnhDb, iPath);
    Database.Enhancements = Array.Empty<IEnhancement>();
    
    // ... file opening ...
    
    Database.Enhancements = new IEnhancement[reader.ReadInt32() + 1];
    for (var index = 0; index < Database.Enhancements.Length; ++index) {
        Database.Enhancements[index] = new Enhancement(reader);
        ++num1;
        if (num1 <= 5) continue;
        num1 = 0;
        Application.DoEvents(); // Every 5 enhancements
    }
    
    // Enhancement Sets in same file
    Database.EnhancementSets = new EnhancementSetCollection();
    var num2 = reader.ReadInt32() + 1;
    for (var index = 0; index < num2; ++index) {
        Database.EnhancementSets.Add(new EnhancementSet(reader));
        ++num1;
        if (num1 <= 5) continue;
        num1 = 0;
        Application.DoEvents();
    }
}
```

**Caching**: All enhancements and sets loaded upfront, cached forever

**File**: Separate binary file (`MxdbFileEnhDb`) from main database

**Filtering**: No server-side filtering - all loaded, client filters as needed

**Count**: ~3000+ enhancements, ~200+ enhancement sets

**Error Handling**: Shows error but continues (enhancements optional for basic functionality)

---

## Data Loading Sequence

MidsReborn follows a **strict sequential loading order** at application startup:

```
Application Startup (MrbAppContext.InitializeApplication)
│
├─> Loader (Splash Screen) shown
│   │
│   ├─> ConfigData.Initialize()
│   │
│   └─> MainModule.MidsController.LoadData(messenger, path)
│       │
│       ├─> 1. LoadServerData(path)
│       │   └─> Server config, version info
│       │
│       ├─> 2. LoadOverrides(path)
│       │   └─> Custom user overrides
│       │
│       ├─> 3. LoadAttributeModifiers(path)
│       │   └─> Combat modifiers (damage, resistance, etc.)
│       │
│       ├─> 4. LoadTypeGrades(path)
│       │   └─> Enhancement types, grades, special enhancements
│       │
│       ├─> 5. LoadLevelsDatabase(path) ⚠️ CRITICAL
│       │   └─> Level caps, XP tables
│       │   └─> Fatal error if fails
│       │
│       ├─> 6. LoadMainDatabase(path) ⚠️ CRITICAL
│       │   ├─> 6a. Archetypes (first in file)
│       │   ├─> 6b. Powersets (second in file)
│       │   ├─> 6c. Powers (third in file)
│       │   └─> 6d. Summons/Entities (fourth in file)
│       │   └─> Fatal error if fails
│       │
│       ├─> 7. LoadMaths(path) ⚠️ CRITICAL
│       │   └─> ED multipliers, TO/DO/SO/HO/IO tables
│       │   └─> Fatal error if fails
│       │
│       ├─> 8. LoadEffectIdsDatabase(path) ⚠️ CRITICAL
│       │   └─> Global effect IDs
│       │   └─> Fatal error if fails
│       │
│       ├─> 9. LoadEnhancementClasses(path) ⚠️ CRITICAL
│       │   └─> Enhancement class definitions
│       │   └─> Fatal error if fails
│       │
│       ├─> 10. LoadEnhancementDb(path) ⚠️ IMPORTANT
│       │   ├─> 10a. Enhancements
│       │   └─> 10b. Enhancement Sets
│       │   └─> Non-fatal - shows error but continues
│       │
│       ├─> 11. LoadOrigins(path)
│       │   └─> Origin definitions (Natural, Magic, etc.)
│       │
│       ├─> 12. LoadRecipes(path)
│       │   └─> Crafting recipes
│       │
│       ├─> 13. LoadSalvage(path)
│       │   └─> Crafting materials
│       │
│       ├─> 14. LoadReplacementTable(path)
│       │   └─> Power name replacements (optional)
│       │
│       ├─> 15. LoadCrypticReplacementTable(path)
│       │   └─> Cryptic-specific power names
│       │
│       ├─> 16. LoadGraphics(path) [ASYNC]
│       │   └─> Power icons, UI images
│       │   └─> Loaded asynchronously (only async operation!)
│       │
│       ├─> 17. MatchAllIDs(messenger)
│       │   └─> Cross-reference all entity IDs
│       │
│       ├─> 18. AssignSetBonusIndexes()
│       │   └─> Link set bonuses to powers
│       │
│       └─> 19. AssignRecipeIDs()
│           └─> Link recipes to enhancements
│
└─> Loader closes, frmMain shown
```

**Critical Path for Epic 1.4** (must have):
- Archetypes (#6a)
- Powersets (#6b)
- Powers (#6c)
- Enhancements (#10a)
- Enhancement Sets (#10b)

**Progress Messages** (shown in Loader):
- "Loading Application Configuration..."
- "Loading Overrides..."
- "Loading Server Data..."
- "Loading Build Preferences"
- "Loading Attribute Modifiers..."
- "Loading Main Data..."
- "Loading Global Chance Modifiers..."
- "Loading Enhancement Database..."
- "Loading Recipe Database..."
- "Loading Powers Replacement Table..."
- "Loading Cryptic-specific power names translation table"
- "Loading Graphics..."
- "Matching Set Bonus IDs..."
- "Matching Recipe IDs..."

---

## Caching Strategy

### MidsReborn Approach

**Cache Duration**: **Forever** (entire application lifetime)

**Cache Location**: Singleton `Database.Instance`

**Cache Invalidation**: **None** - only way to reload is restart application

**Rationale**: 
- Game data changes very infrequently (only with game updates)
- Binary file format is fast to parse (~2-3 seconds for all data)
- Desktop app has full file system access
- No network latency concerns

### Code Example

```csharp
// Singleton pattern - single instance for entire app lifetime
public sealed class Database : IDatabase {
    public static Database Instance { get; } = new();
    
    public Archetype[]? Classes { get; set; }
    public IPowerset?[] Powersets { get; set; }
    public IPower?[] Power { get; set; }
    public IEnhancement[] Enhancements { get; set; }
    public EnhancementSetCollection EnhancementSets { get; set; }
    // ... etc
}

// Usage throughout app
var archetype = DatabaseAPI.Database.Classes[archetypeId];
var powerset = DatabaseAPI.Database.Powersets[powersetId];
```

**Key Observations**:
- No cache expiration logic
- No cache invalidation logic
- No "stale" data handling
- No background refresh
- **Assumption**: Data is immutable after load

---

## Error Handling Patterns

### Fatal Errors (Application Exit)

**Pattern**:
```csharp
if (!DatabaseAPI.LoadMainDatabase(path)) {
    MessageBox.Show(
        @"There was an error reading the database. Aborting!", 
        @"Error!", 
        MessageBoxButtons.OK, 
        MessageBoxIcon.Error
    );
    Application.Exit(); // Hard exit
}
```

**Affected Operations**:
- LoadServerData (server config missing)
- LoadLevelsDatabase (level data critical for calculations)
- LoadMainDatabase (archetypes, powersets, powers)
- LoadMaths (enhancement multipliers)
- LoadEffectIdsDatabase (effect ID mappings)
- LoadEnhancementClasses (enhancement classes)

**User Experience**: 
- Blocking error dialog
- No retry mechanism
- No fallback/degraded mode
- **Must restart app** to retry

### Non-Fatal Errors (Continue Execution)

**Pattern**:
```csharp
try {
    DatabaseAPI.LoadEnhancementDb(path);
} catch (Exception ex) {
    MessageBox.Show(
        "Enhancement Database file isn't how it should be (" + ex.Message + 
        "\r\n" + ex.StackTrace + ")\nNo Enhancements have been loaded.", 
        "Huh..."
    );
    Database.Enhancements = Array.Empty<IEnhancement>(); // Empty fallback
}
```

**Affected Operations**:
- LoadEnhancementDb (enhancements optional for basic planning)

**User Experience**:
- Shows error message
- Continues with empty data
- App still functional (builds work, just no enhancements)

### File Not Found

**Pattern**:
```csharp
try {
    fileStream = new FileStream(path, FileMode.Open, FileAccess.Read);
    reader = new BinaryReader(fileStream);
} catch {
    return false; // Caller handles error
}
```

**User Experience**:
- Silent failure → returned to caller
- Caller shows generic error message
- **No specific "file not found" message**

---

## Loading States

### Splash Screen (Loader)

**UI Component**: `Loader.cs` (custom WinForms form with WebView2)

**Loading Indicator**: 
- WebView2 showing animated HTML/CSS loader
- Text label showing current operation
- No progress percentage (qualitative only)

**Loading Messages**:
```csharp
messenger.SetMessage("Loading Application Configuration...");
messenger.SetMessage("Loading Overrides...");
messenger.SetMessage("Loading Server Data...");
messenger.SetMessage("Loading Main Data...");
messenger.SetMessage("Loading Enhancement Database...");
// ... etc
```

**Update Frequency**: 
- Message updates before each major loading phase
- `Application.DoEvents()` during long loops to keep UI responsive
- No spinner animation (static HTML animation handles that)

**Close Behavior**:
- Splash closes when `LoadCompleted` TaskCompletionSource resolves
- Main form (`frmMain`) shown immediately after
- **No transition animation**

### In-App Loading (None)

**MidsReborn does NOT show loading states during runtime** because:
- All data loaded at startup
- No network calls during usage
- No lazy loading
- Synchronous data access from singleton

---

## Feature Requirements for Web

### MUST-HAVE Features

#### 1. Fetch Archetypes on App Load

**Description**: Load all archetypes at application startup (or first access)

**MidsReborn Implementation**: 
- Loaded in `LoadMainDatabase()` first thing after DB metadata
- Synchronous, blocking
- Fatal error if fails

**Web Equivalent**:
```typescript
// TanStack Query hook
export function useArchetypes() {
  return useQuery({
    queryKey: ['archetypes'],
    queryFn: async () => {
      const response = await fetch('/api/archetypes?limit=100');
      if (!response.ok) throw new Error('Failed to fetch archetypes');
      return response.json();
    },
    staleTime: Infinity, // Archetypes never change
    cacheTime: Infinity,
    retry: 3,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}
```

**Why MUST-HAVE**: Archetypes are required to filter powersets and determine build calculations

---

#### 2. Fetch Powersets (All or by Archetype)

**Description**: Load all powersets, or lazy-load by archetype

**MidsReborn Implementation**:
- All powersets loaded upfront
- Client-side filtering by archetype ID
- ~300+ powersets loaded in ~100ms

**Web Equivalent (Option A - Eager)**:
```typescript
// Load all powersets upfront
export function usePowersets() {
  return useQuery({
    queryKey: ['powersets'],
    queryFn: async () => {
      const response = await fetch('/api/powersets?limit=1000');
      if (!response.ok) throw new Error('Failed to fetch powersets');
      return response.json();
    },
    staleTime: Infinity, // Powersets rarely change
    cacheTime: Infinity,
  });
}

// Client-side filter
const filteredPowersets = powersets?.filter(
  ps => ps.archetype_id === selectedArchetypeId
);
```

**Web Equivalent (Option B - Lazy by Archetype)** ⭐ RECOMMENDED:
```typescript
// Only fetch powersets for selected archetype
export function usePowersetsByArchetype(archetypeId: number | null) {
  return useQuery({
    queryKey: ['powersets', 'archetype', archetypeId],
    queryFn: async () => {
      if (!archetypeId) return [];
      const response = await fetch(`/api/archetypes/${archetypeId}/powersets`);
      if (!response.ok) throw new Error('Failed to fetch powersets');
      return response.json();
    },
    enabled: !!archetypeId, // Only run when archetype selected
    staleTime: Infinity,
    cacheTime: Infinity,
  });
}
```

**Why MUST-HAVE**: Powersets required for character creation flow

**Recommendation**: Use **Option B (lazy by archetype)** to reduce initial load, then prefetch other archetypes in background

---

#### 3. Lazy Load Powers by Powerset

**Description**: Only load powers when user selects a powerset

**MidsReborn Implementation**:
- All ~3000+ powers loaded upfront
- Client-side lookup by powerset ID
- Fast because all in memory

**Web Equivalent**:
```typescript
// Lazy load powers only when powerset selected
export function usePowersByPowerset(powersetId: number | null) {
  return useQuery({
    queryKey: ['powers', 'powerset', powersetId],
    queryFn: async () => {
      if (!powersetId) return [];
      const response = await fetch(`/api/powersets/${powersetId}/powers`);
      if (!response.ok) throw new Error('Failed to fetch powers');
      return response.json();
    },
    enabled: !!powersetId,
    staleTime: 5 * 60 * 1000, // 5 minutes (powers change occasionally with patches)
    cacheTime: 60 * 60 * 1000, // Keep in cache 1 hour
  });
}
```

**Why MUST-HAVE**: User needs to see available powers to select them

**Why Lazy**: Loading 3000+ powers upfront is unnecessary - user only sees 1-2 powersets at a time

**Optimization**: Prefetch powers for commonly-selected powersets

---

#### 4. Cache Enhancement Data Aggressively

**Description**: Enhancements rarely change, cache for long periods

**MidsReborn Implementation**:
- All ~3000+ enhancements loaded upfront
- All ~200+ sets loaded upfront
- Cached forever in singleton

**Web Equivalent (Lazy + Paginated)**:
```typescript
// Load enhancements on-demand with pagination
export function useEnhancements(
  filters?: { type?: string; grade?: string; skip?: number; limit?: number }
) {
  const { type, grade, skip = 0, limit = 100 } = filters || {};
  
  return useQuery({
    queryKey: ['enhancements', { type, grade, skip, limit }],
    queryFn: async () => {
      const params = new URLSearchParams({
        skip: skip.toString(),
        limit: limit.toString(),
      });
      if (type) params.append('enhancement_type', type);
      
      const response = await fetch(`/api/enhancements?${params}`);
      if (!response.ok) throw new Error('Failed to fetch enhancements');
      return response.json();
    },
    staleTime: 60 * 60 * 1000, // 1 hour
    cacheTime: 24 * 60 * 60 * 1000, // Keep in cache 24 hours
    keepPreviousData: true, // Show old data while fetching new page
  });
}

// Enhancement sets
export function useEnhancementSets() {
  return useQuery({
    queryKey: ['enhancement-sets'],
    queryFn: async () => {
      const response = await fetch('/api/enhancement-sets?limit=500');
      if (!response.ok) throw new Error('Failed to fetch enhancement sets');
      return response.json();
    },
    staleTime: Infinity, // Sets never change
    cacheTime: Infinity,
  });
}
```

**Why MUST-HAVE**: Enhancements needed for slotting powers

**Why Paginated**: 3000+ enhancements is too much to load upfront for web

**UX Improvement**: Lazy load with search/filter, show 50-100 at a time

---

#### 5. Handle Network Failures Gracefully

**Description**: Unlike desktop app, web app must handle network failures

**MidsReborn Implementation**: Not applicable (local files)

**Web Equivalent**:
```typescript
// Global error handling wrapper
function useQueryWithErrorHandling<T>(
  queryKey: QueryKey,
  queryFn: QueryFunction<T>,
  options?: UseQueryOptions<T>
) {
  return useQuery<T>({
    ...options,
    queryKey,
    queryFn,
    retry: 3,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
    onError: (error) => {
      console.error('Query failed:', error);
      // Show toast notification
      toast.error(`Failed to load data: ${error.message}`);
    },
  });
}
```

**Error States**:
- Network timeout (30s)
- 404 Not Found
- 500 Server Error
- CORS errors
- Parse errors (invalid JSON)

**User Experience**:
- Show error message (toast or inline)
- Provide retry button
- Show last successfully loaded data if available
- **Do NOT exit app** (unlike MidsReborn)

**Why MUST-HAVE**: Network failures are common in web apps, must handle gracefully

---

#### 6. Loading State Components

**Description**: Show loading spinners/skeletons while data loads

**MidsReborn Implementation**: 
- Single splash screen at startup
- No loading states during runtime (all data preloaded)

**Web Equivalent**:
```typescript
// LoadingSpinner.tsx
export function LoadingSpinner({ size = 'md' }: { size?: 'sm' | 'md' | 'lg' }) {
  return (
    <div className="flex items-center justify-center p-4">
      <div className={cn(
        "animate-spin rounded-full border-b-2 border-primary",
        size === 'sm' && "h-4 w-4",
        size === 'md' && "h-8 w-8",
        size === 'lg' && "h-12 w-12"
      )} />
    </div>
  );
}

// Usage in components
function ArchetypeSelector() {
  const { data: archetypes, isLoading, isError, error } = useArchetypes();
  
  if (isLoading) return <LoadingSpinner />;
  if (isError) return <ErrorMessage error={error} />;
  
  return (
    <Select>
      {archetypes.map(at => (
        <SelectItem key={at.id} value={at.id}>{at.name}</SelectItem>
      ))}
    </Select>
  );
}
```

**Loading Patterns**:
- **Spinner**: Small inline loading (dropdowns, buttons)
- **Skeleton**: Placeholder shapes (lists, cards)
- **Suspense**: Page-level loading boundaries
- **Progress**: Multi-step loading (character creation flow)

**Why MUST-HAVE**: Web users expect visual feedback during async operations

---

### SHOULD-HAVE Features

#### 1. Prefetch Likely-Needed Data

**Description**: Preload data user is likely to need next

**Example**:
```typescript
// When user selects archetype, prefetch powersets
function useArchetypeSelection() {
  const queryClient = useQueryClient();
  
  const selectArchetype = (archetypeId: number) => {
    // Prefetch powersets for this archetype
    queryClient.prefetchQuery({
      queryKey: ['powersets', 'archetype', archetypeId],
      queryFn: () => fetch(`/api/archetypes/${archetypeId}/powersets`).then(r => r.json()),
    });
    
    // Update state
    // ...
  };
  
  return { selectArchetype };
}
```

**Benefits**: Faster perceived performance, smoother UX

---

#### 2. Optimistic UI Updates

**Description**: Show UI changes immediately, rollback if server fails

**Example**:
```typescript
// When slotting an enhancement, show it immediately
const slotEnhancement = useMutation({
  mutationFn: async ({ powerId, slotId, enhancementId }) => {
    // Optimistically update UI
    queryClient.setQueryData(['build'], (old) => ({
      ...old,
      powers: old.powers.map(p => 
        p.id === powerId 
          ? { ...p, slots: [...p.slots, { slotId, enhancementId }] }
          : p
      )
    }));
    
    // No server call needed (client-side build state)
  },
});
```

**Benefits**: Instant feedback, feels native-app fast

---

#### 3. Background Data Refresh

**Description**: Periodically check for updated data (new patches)

**Example**:
```typescript
// Check for data updates every 24 hours
export function useArchetypes() {
  return useQuery({
    queryKey: ['archetypes'],
    queryFn: fetchArchetypes,
    staleTime: 24 * 60 * 60 * 1000, // Consider stale after 24h
    refetchOnWindowFocus: true, // Recheck when user returns to tab
    refetchInterval: 24 * 60 * 60 * 1000, // Auto-refresh daily
  });
}
```

**Benefits**: Users see latest data without manual refresh

---

#### 4. Offline Mode (Service Worker Cache)

**Description**: Cache API responses for offline access

**Implementation**: Use service worker to cache API responses

**Benefits**: App works offline (for previously-loaded data)

**Note**: Out of scope for Epic 1.4, but consider for future

---

### COULD-SKIP Features

#### 1. Real-time Data Sync (WebSockets)

**Why Skip**: Game data is static, no need for real-time updates

---

#### 2. Server-Side Rendering (SSR) for Data

**Why Skip**: Data needs client-side interactivity, CSR is fine

**Note**: SSR for layout/shell is good (Next.js App Router), but not for dynamic data

---

#### 3. GraphQL Instead of REST

**Why Skip**: REST endpoints already implemented, working well

**Note**: GraphQL would be nice for fetching exact fields needed, but overkill for MVP

---

## State Management Analysis

### Server State (TanStack Query)

All **server-fetched data** should be managed by TanStack Query, NOT Zustand.

#### Queries Needed

##### 1. `useArchetypes`

**Endpoint**: `GET /api/archetypes`

**Query Key**: `['archetypes']`

**Caching Strategy**: 
```typescript
{
  staleTime: Infinity, // Never becomes stale
  cacheTime: Infinity, // Never evict from cache
  retry: 3,
}
```

**Error Handling**: 
- Retry 3 times with exponential backoff
- Show error toast if all retries fail
- Provide "Retry" button

**Data Shape**:
```typescript
interface Archetype {
  id: number;
  name: string;
  display_name: string;
  hit_points: number;
  // ... etc
}
```

---

##### 2. `usePowersetsByArchetype`

**Endpoint**: `GET /api/archetypes/{archetype_id}/powersets`

**Query Key**: `['powersets', 'archetype', archetypeId]`

**Caching Strategy**:
```typescript
{
  staleTime: Infinity,
  cacheTime: Infinity,
  enabled: !!archetypeId, // Only fetch when archetype selected
}
```

**Filtering**: Server-side by archetype ID

**Prefetching**: Consider prefetching all archetypes' powersets on idle

---

##### 3. `usePowersByPowerset`

**Endpoint**: `GET /api/powersets/{powerset_id}/powers`

**Query Key**: `['powers', 'powerset', powersetId]`

**Caching Strategy**:
```typescript
{
  staleTime: 5 * 60 * 1000, // 5 minutes
  cacheTime: 60 * 60 * 1000, // 1 hour
  enabled: !!powersetId,
}
```

**Lazy Loading**: Only fetch when powerset selected

**Why Shorter staleTime**: Powers occasionally get balance patches

---

##### 4. `useEnhancements`

**Endpoint**: `GET /api/enhancements`

**Query Key**: `['enhancements', { type, grade, skip, limit }]`

**Caching Strategy**:
```typescript
{
  staleTime: 60 * 60 * 1000, // 1 hour
  cacheTime: 24 * 60 * 60 * 1000, // 24 hours
  keepPreviousData: true, // Show old page while loading new
}
```

**Pagination**: Required (3000+ enhancements)

**Filtering**: Client-side after fetch (or server-side if backend supports)

---

##### 5. `useEnhancementSets`

**Endpoint**: `GET /api/enhancement-sets`

**Query Key**: `['enhancement-sets']`

**Caching Strategy**:
```typescript
{
  staleTime: Infinity,
  cacheTime: Infinity,
}
```

**Count**: ~200 sets, can load all upfront

---

##### 6. `useEnhancementSet` (with bonuses)

**Endpoint**: `GET /api/enhancement-sets/{set_id}`

**Query Key**: `['enhancement-sets', setId]`

**Caching Strategy**:
```typescript
{
  staleTime: Infinity,
  cacheTime: Infinity,
}
```

**Use Case**: Show set bonuses when hovering over enhancement

---

#### Mutations Needed

**None for Epic 1.4** - this epic is read-only data fetching.

Mutations will be needed in later epics for:
- Saving builds (Epic 5)
- Exporting builds (Epic 5)
- Sharing builds (Epic 5)

---

### Client State (Zustand)

**TanStack Query handles ALL server data**, so Zustand only stores:

1. **UI Preferences** (already in `uiStore` from Epic 1.3):
   - Theme (light/dark)
   - Sidebar collapsed state
   - Panel sizes
   - View settings

2. **Character Build State** (will be in `characterStore` from Epic 2+):
   - Selected archetype ID (just the ID, not full archetype object)
   - Selected powerset IDs
   - Selected power IDs
   - Slotted enhancements IDs
   - Level

**Why separate**:
- **Zustand**: User's choices and UI state (persists to localStorage)
- **TanStack Query**: Server data (caches in memory, refetches as needed)

**Example**:
```typescript
// ❌ DON'T store server data in Zustand
const characterStore = create((set) => ({
  archetype: { id: 1, name: 'Tanker', ... }, // ❌ Wrong!
}));

// ✅ DO store only IDs
const characterStore = create((set) => ({
  archetypeId: 1, // ✅ Correct!
}));

// Then fetch archetype data with TanStack Query
const { data: archetype } = useArchetype(characterStore.archetypeId);
```

---

## Web Component Mapping

| MidsReborn Pattern | Web Equivalent | Library/Component |
|--------------------|----------------|-------------------|
| **Synchronous DB call** | Async fetch with `await` | `fetch()` + `async/await` |
| **Binary file read** | REST API call | `fetch('/api/...')` |
| **File-based cache (singleton)** | TanStack Query cache | `useQuery()` with `staleTime` |
| **MessageBox error dialog** | Toast notification | `sonner` or `react-hot-toast` |
| **Application.Exit()** | Show error state (no exit) | Error boundary + retry button |
| **Splash screen (Loader)** | Suspense boundary | `<Suspense fallback={<Loading />}>` |
| **Application.DoEvents()** | Not needed (async/await) | N/A |
| **Progress text updates** | Loading state messages | `isLoading` + conditional text |
| **Blocking load** | Non-blocking with loading UI | `isLoading` flag + spinner |
| **Fatal error = exit** | Show error + retry | Error boundary component |

---

## API Integration Points

### Backend Endpoints Available

Verified from `backend/app/routers/`:

#### Archetypes (`archetypes.py`)

✅ **GET /api/archetypes**
- Query params: `skip`, `limit`
- Response: `Archetype[]`
- Expected count: ~13 archetypes

✅ **GET /api/archetypes/{archetype_id}**
- Path param: `archetype_id`
- Response: `Archetype`
- Error: 404 if not found

✅ **GET /api/archetypes/{archetype_id}/powersets**
- Path param: `archetype_id`
- Query param: `powerset_type` (primary, secondary, pool, epic)
- Response: `Powerset[]`
- Error: 404 if archetype not found

---

#### Powersets (`powersets.py`)

✅ **GET /api/powersets/{powerset_id}**
- Path param: `powerset_id`
- Response: `Powerset`
- Error: 404 if not found

✅ **GET /api/powersets/{powerset_id}/detailed**
- Path param: `powerset_id`
- Response: `PowersetWithPowers` (includes all powers)
- Use case: Fetch powerset + all its powers in one call

✅ **GET /api/powersets/{powerset_id}/powers**
- Path param: `powerset_id`
- Response: `Power[]`
- Error: 404 if powerset not found

---

#### Powers (`powers.py`)

✅ **GET /api/powers/{power_id}**
- Path param: `power_id`
- Response: `Power` (as raw dict with decimals → floats)
- Error: 404 if not found

✅ **GET /api/powers**
- Query params: `name`, `power_type`, `min_level`, `max_level`, `skip`, `limit`
- Response: `Power[]`
- Use case: Search powers by name or filter

⚠️ **GET /api/powers/test/{power_id}**
- Debug endpoint (remove in production)

---

#### Enhancements (`enhancements.py`)

✅ **GET /api/enhancements**
- Query params: `skip`, `limit`, `enhancement_type`
- Response: `Enhancement[]`
- Expected count: ~3000+ enhancements

✅ **GET /api/enhancements/{enhancement_id}**
- Path param: `enhancement_id`
- Response: `Enhancement`
- Error: 404 if not found

✅ **GET /api/enhancement-sets**
- Query params: `skip`, `limit`
- Response: `EnhancementSet[]`
- Expected count: ~200+ sets

✅ **GET /api/enhancement-sets/{set_id}**
- Path param: `set_id`
- Query params: `include_enhancements`, `include_bonuses`
- Response: `EnhancementSetWithBonuses`
- Error: 404 if not found

---

#### Calculations (`calculations.py`)

✅ **POST /api/v1/calculations/power/damage**
- Request: `DamageCalculationRequest`
- Response: `DamageCalculationResponse`
- Use case: Calculate power damage with enhancements

✅ **POST /api/v1/calculations/build/defense**
- Request: `DefenseCalculationRequest`
- Response: `DefenseCalculationResponse`
- Use case: Calculate build defense totals

✅ **POST /api/v1/calculations/build/resistance**
- Request: `ResistanceCalculationRequest`
- Response: `ResistanceCalculationResponse`
- Use case: Calculate build resistance totals

(Additional calculation endpoints exist - see `calculations.py`)

---

### Missing Endpoints (Need Implementation)

None for Epic 1.4! All required endpoints exist.

**Future Epics May Need**:
- `POST /api/builds` - Save build to server (Epic 5)
- `GET /api/builds/{build_id}` - Load build (Epic 5)
- `GET /api/builds/user/{user_id}` - List user's builds (Epic 5)
- `POST /api/builds/share` - Generate share link (Epic 5)

---

## Screenshot Analysis

**Location**: `/home/user/mids-hero-web/shared/user/midsreborn-screenshots`

### Available Screenshots

1. **mids-new-build.png** - Main build window
2. **power-desc-mouse-over.png** - Power tooltip on hover
3. **pool-desc-mouse-over.png** - Pool power tooltip
4. **power-enh-slot-pick.png** - Enhancement picker dialog
5. **power-enh.png** - Power with slotted enhancements
6. **build-active-sets-bonuses.png** - Active set bonuses panel
7. **total-screen-1.png** - Totals window (defense/resistance)
8. **view-total-window.png** - Another totals view

### Relevant to Epic 1.4

**None directly** - Epic 1.4 is about API infrastructure, not visible UI.

However:
- Screenshots show **no loading states** (because MidsReborn preloads all data)
- No visible error messages in screenshots
- UI is always ready because data is always available

**Implication for Web**:
- We need to **design loading states** that MidsReborn doesn't have
- Need to **design error states** that MidsReborn doesn't show during runtime
- Should match MidsReborn's aesthetic when showing loading/error UI

### Additional Screenshots Recommended

For Epic 1.4 specifically:

**Loading States**:
- ❓ MidsReborn splash screen (Loader) - **would be helpful**
- ❓ Loading progress messages - **would be helpful**

**Error States**:
- ❓ Error MessageBox dialogs - **would be helpful**
- ❓ Missing file error - **would be helpful**

**Note**: These may not exist in current screenshot set. If implementing Epic 1.4, consider capturing these from running MidsReborn app.

---

## Implementation Notes

### Key Behaviors to Replicate

1. **Aggressive Caching**
   - MidsReborn loads data once and caches forever
   - Web should do same with TanStack Query `staleTime: Infinity`
   - Exception: Powers can use shorter staleTime (5min) to catch patches

2. **Startup Sequence**
   - MidsReborn has strict loading order (Archetypes → Powersets → Powers → Enhancements)
   - Web should load **Archetypes first** (blocking), then lazy-load rest
   - Show loading state during initial archetype load

3. **Error Resilience**
   - MidsReborn exits on critical errors (database missing)
   - Web should **show error + retry**, not exit
   - Degrade gracefully (e.g., show builds without enhancements if enhancement API fails)

4. **No Runtime Loading**
   - MidsReborn never loads data during usage (all upfront)
   - Web should **prefetch likely-needed data** to mimic this
   - Example: When user selects archetype, prefetch powersets

---

### UX Improvements for Web

1. **Progressive Loading**
   - Don't block on loading all data
   - Show UI shell immediately (layout, navigation)
   - Load data sections as user navigates
   - Use Suspense boundaries for code splitting

2. **Optimistic Updates**
   - When user makes selection, update UI immediately
   - No server call needed for client-side state (archetype selection, power picks)
   - Calculate totals client-side if possible (use calculation API as fallback)

3. **Better Error Messages**
   - Clear, actionable error messages
   - "Failed to load archetypes. Check your internet connection. [Retry]"
   - Avoid generic "Error!" messages

4. **Retry Logic**
   - Automatic retry with exponential backoff (3 attempts)
   - Manual retry button if all auto-retries fail
   - Show "Retrying (1/3)..." in UI

5. **Perceived Performance**
   - Show skeleton loaders instead of blank space
   - Prefetch data on hover (e.g., hover archetype → prefetch powersets)
   - Use `keepPreviousData` to avoid flicker when paginating

---

## Warnings & Edge Cases

### Network Failures

**Issue**: Web apps depend on network, MidsReborn doesn't

**Solutions**:
- Retry with exponential backoff
- Show cached/stale data if available
- Provide manual retry button
- Show clear error messages

---

### CORS Errors

**Issue**: Browser blocks requests to backend if CORS not configured

**Solution**: Ensure backend sends CORS headers

```python
# backend/app/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

### Stale Data

**Issue**: Game receives patch, cached data is outdated

**Solutions**:
- Set reasonable `staleTime` (not Infinity for powers)
- Provide manual "Refresh Data" button
- Check backend for data version, invalidate cache if mismatch
- Show "Data updated" notification when new data available

---

### Large Datasets

**Issue**: 3000+ enhancements, 3000+ powers

**Solutions**:
- **Pagination**: Load 100 enhancements at a time
- **Virtualization**: Use `react-window` for long lists
- **Search**: Filter enhancements by name/type before loading
- **Lazy loading**: Only load when needed (don't load all powers upfront)

---

### Type Mismatches

**Issue**: Backend uses `Decimal`, frontend expects `number`

**Current Solution**: Backend converts `Decimal → float` in endpoints

**Watch For**: Ensure all numeric fields are converted

---

### Loading State Flicker

**Issue**: Data loads fast, spinner shows for 50ms and flickers

**Solutions**:
- Set minimum loading time (e.g., 300ms) before showing content
- Use CSS transitions for smooth fade-in
- Use `keepPreviousData` to avoid flicker when refetching

---

### Build Data Size

**Issue**: Full character build JSON could be large (10KB+)

**Solutions**:
- Compress when sending to server (gzip)
- Only send changed fields on update
- Use efficient serialization format
- Defer calculation API calls until user requests totals

---

### Race Conditions

**Issue**: User selects Archetype A, then quickly switches to B. Request for A's powersets returns after request for B.

**Solution**: TanStack Query handles this automatically
- Each query key is separate
- Cancelled queries are ignored
- Latest query wins

**Example**:
```typescript
// User rapidly switches archetypes: 1 → 2 → 3
// Query keys:
// ['powersets', 'archetype', 1] - cancelled
// ['powersets', 'archetype', 2] - cancelled
// ['powersets', 'archetype', 3] - active (only this one shows in UI)
```

---

## Analysis Status

**Status**: ✅ **Complete**

**Confidence**: 🟢 **High**

**Data Sources**:
- ✅ MidsReborn C# source code analyzed
- ✅ Backend API endpoints verified
- ✅ Loading sequence documented
- ✅ Caching strategy identified
- ✅ Error handling patterns extracted
- ✅ Screenshots reviewed (limited relevance to Epic 1.4)

**Gaps**:
- ⚠️ No screenshots of MidsReborn splash screen (Loader) with loading messages
- ⚠️ No screenshots of error dialogs
- ℹ️ Not critical for Epic 1.4 (infrastructure, not UI)

---

## Next Steps

**Phase 3: Planning** (`/superpowers:write-plan`)

1. Create implementation plan for Epic 1.4
2. Define API service functions (`powerApi.ts`, etc.)
3. Define TanStack Query hooks (`usePowers.ts`, etc.)
4. Define loading/error components
5. Set up TanStack Query provider configuration
6. Plan tests (API services, hooks, components)

**Key Decisions**:
- ✅ Use TanStack Query for all server state (not Zustand)
- ✅ Lazy load powers by powerset (not upfront)
- ✅ Paginate enhancements (not all upfront)
- ✅ Aggressive caching with long `staleTime`
- ✅ Graceful error handling (no app exit)
- ✅ Loading states with spinners/skeletons

**Dependencies**:
- Epic 1.1 ✅ (Next.js + shadcn/ui)
- Epic 1.2 ✅ (Zustand + TanStack Query installed)
- Epic 1.3 ✅ (Layout + Navigation)
- Backend API ✅ (all endpoints exist)

**Ready to Proceed**: ✅ Yes

---

**End of Analysis**
