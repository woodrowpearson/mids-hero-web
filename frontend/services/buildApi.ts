/**
 * Build API service
 * Handles build sharing endpoints (future feature)
 */

import api from "./api";
import type {
  CreateBuildRequest,
  CreateBuildResponse,
  GetBuildResponse,
  UpdateBuildRequest,
  UpdateBuildResponse,
} from "@/types/api.types";

export const buildApi = {
  /**
   * Create/share a build
   * POST /api/builds
   */
  create: async (request: CreateBuildRequest): Promise<CreateBuildResponse> => {
    const response = await api.post("/builds", request);
    return response.data;
  },

  /**
   * Get a shared build by ID
   * GET /api/builds/:id
   */
  getById: async (buildId: string): Promise<GetBuildResponse> => {
    const response = await api.get(`/builds/${buildId}`);
    return response.data;
  },

  /**
   * Update an existing build
   * PUT /api/builds/:id
   */
  update: async (buildId: string, request: UpdateBuildRequest): Promise<UpdateBuildResponse> => {
    const response = await api.put(`/builds/${buildId}`, request);
    return response.data;
  },

  /**
   * Delete a build
   * DELETE /api/builds/:id
   */
  delete: async (buildId: string): Promise<void> => {
    await api.delete(`/builds/${buildId}`);
  },
};
