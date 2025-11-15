/**
 * Archetype API service
 * Handles archetype-related endpoints
 */

import api from "./api";
import type { GetArchetypesResponse, GetArchetypeResponse } from "@/types/api.types";

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
};
