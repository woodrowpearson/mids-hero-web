/**
 * Enhancement API service
 * Handles enhancement and enhancement set endpoints
 */

import api from "./api";
import type {
  GetEnhancementsResponse,
  GetEnhancementsParams,
  GetEnhancementSetsResponse,
  GetEnhancementSetResponse,
} from "@/types/api.types";

export const enhancementApi = {
  /**
   * Get all enhancements (optionally filtered)
   * GET /api/enhancements
   */
  getAll: async (params?: GetEnhancementsParams): Promise<GetEnhancementsResponse> => {
    const response = await api.get("/enhancements", { params });
    return response.data;
  },

  /**
   * Get all enhancement sets
   * GET /api/enhancement-sets
   */
  getSets: async (): Promise<GetEnhancementSetsResponse> => {
    const response = await api.get("/enhancement-sets");
    return response.data;
  },

  /**
   * Get enhancement set by ID
   * GET /api/enhancement-sets/:id
   */
  getSetById: async (setId: number): Promise<GetEnhancementSetResponse> => {
    const response = await api.get(`/enhancement-sets/${setId}`);
    return response.data;
  },
};
