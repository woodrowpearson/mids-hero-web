/**
 * Power and Powerset API service
 * Handles power-related endpoints
 */

import api from "./api";
import type {
  GetPowersetsResponse,
  GetPowersetsParams,
  GetPowersetPowersResponse,
  GetPowersResponse,
  GetPowerResponse,
} from "@/types/api.types";

export const powerApi = {
  /**
   * Get all powersets (optionally filtered)
   * GET /api/powersets
   */
  getPowersets: async (params?: GetPowersetsParams): Promise<GetPowersetsResponse> => {
    const response = await api.get("/powersets", { params });
    return response.data;
  },

  /**
   * Get powers in a specific powerset
   * GET /api/powersets/:id/powers
   */
  getPowersetPowers: async (powersetId: number): Promise<GetPowersetPowersResponse> => {
    const response = await api.get(`/powersets/${powersetId}/powers`);
    return response.data;
  },

  /**
   * Get all powers
   * GET /api/powers
   */
  getAllPowers: async (): Promise<GetPowersResponse> => {
    const response = await api.get("/powers");
    return response.data;
  },

  /**
   * Get power by ID
   * GET /api/powers/:id
   */
  getPowerById: async (powerId: number): Promise<GetPowerResponse> => {
    const response = await api.get(`/powers/${powerId}`);
    return response.data;
  },
};
