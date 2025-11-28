/**
 * Archetype API service
 * Handles archetype-related endpoints
 */

import api from "./api";
import type {
  GetArchetypesResponse,
  GetArchetypeResponse,
  GetPowersetsResponse,
} from "@/types/api.types";

export const archetypeApi = {
  /**
   * Get all archetypes
   * GET /api/archetypes
   */
  getAll: async (): Promise<GetArchetypesResponse> => {
    const response = await api.get("/archetypes");
    return response.data;
  },

  /**
   * Get archetype by ID
   * GET /api/archetypes/:id
   */
  getById: async (id: number): Promise<GetArchetypeResponse> => {
    const response = await api.get(`/archetypes/${id}`);
    return response.data;
  },

  /**
   * Get powersets for a specific archetype
   * GET /api/archetypes/:id/powersets
   * Epic 2.3: Supports filtering by powerset_type query parameter
   */
  getPowersets: async (
    archetypeId: number,
    powersetType?: string
  ): Promise<GetPowersetsResponse> => {
    const response = await api.get(`/archetypes/${archetypeId}/powersets`, {
      params: powersetType ? { powerset_type: powersetType } : undefined,
    });
    return response.data;
  },
};
