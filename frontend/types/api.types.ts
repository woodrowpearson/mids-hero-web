/**
 * API request/response TypeScript type definitions
 * Based on FastAPI backend endpoints
 */

import type {
  Archetype,
  Powerset,
  Power,
  Enhancement,
  EnhancementSet,
  BuildData,
  CalculatedTotals,
} from "./character.types";

// ============================================================================
// Database Endpoints
// ============================================================================

// GET /api/archetypes
export type GetArchetypesResponse = Archetype[];

// GET /api/archetypes/:id
export type GetArchetypeResponse = Archetype;

// GET /api/powersets
export interface GetPowersetsParams {
  archetypeId?: number;
  type?: string; // Legacy field
  powersetType?: string; // Epic 2.3: Filter by powerset type (primary, secondary, pool, inherent, etc.)
}
export type GetPowersetsResponse = Powerset[];

// GET /api/powersets/:id/powers
export type GetPowersetPowersResponse = Power[];

// GET /api/powers
export type GetPowersResponse = Power[];

// GET /api/powers/:id
export type GetPowerResponse = Power;

// GET /api/enhancements
export interface GetEnhancementsParams {
  type?: string;
  setId?: number;
}
export type GetEnhancementsResponse = Enhancement[];

// GET /api/enhancement-sets
export type GetEnhancementSetsResponse = EnhancementSet[];

// GET /api/enhancement-sets/:id
export type GetEnhancementSetResponse = EnhancementSet;

// ============================================================================
// Calculation Endpoints
// ============================================================================

// POST /api/calculations/totals
export interface CalculateTotalsRequest {
  buildData: BuildData;
}
export type CalculateTotalsResponse = CalculatedTotals;

// POST /api/calculations/power
export interface CalculatePowerRequest {
  powerId: number;
  level: number;
  archetypeId: number;
  slotting: {
    enhancementId: number;
    level: number;
  }[];
}
export interface CalculatePowerResponse {
  damage: number;
  accuracy: number;
  recharge: number;
  endurance: number;
  // ... other calculated power stats
}

// ============================================================================
// Build Sharing Endpoints (future)
// ============================================================================

// POST /api/builds
export interface CreateBuildRequest {
  name: string;
  description?: string;
  buildData: BuildData;
}
export interface CreateBuildResponse {
  id: string;
  downloadUrl: string;
  imageUrl: string;
  schemaUrl: string;
  expirationDate: string;
}

// GET /api/builds/:id
export type GetBuildResponse = BuildData & {
  id: string;
  name: string;
  description?: string;
  createdAt: string;
};

// PUT /api/builds/:id
export interface UpdateBuildRequest {
  name?: string;
  description?: string;
  buildData?: BuildData;
}
export type UpdateBuildResponse = CreateBuildResponse;

// ============================================================================
// Error Response
// ============================================================================

export interface APIError {
  message: string;
  code?: string;
  details?: unknown;
}
