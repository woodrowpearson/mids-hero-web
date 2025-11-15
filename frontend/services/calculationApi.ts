/**
 * Calculation API service
 * Handles build calculation endpoints
 */

import api from "./api";
import type {
  CalculateTotalsRequest,
  CalculateTotalsResponse,
  CalculatePowerRequest,
  CalculatePowerResponse,
} from "@/types/api.types";

export const calculationApi = {
  /**
   * Calculate build totals
   * POST /api/calculations/totals
   */
  calculateTotals: async (
    request: CalculateTotalsRequest
  ): Promise<CalculateTotalsResponse> => {
    const response = await api.post("/calculations/totals", request);
    return response.data;
  },

  /**
   * Calculate single power stats
   * POST /api/calculations/power
   */
  calculatePower: async (request: CalculatePowerRequest): Promise<CalculatePowerResponse> => {
    const response = await api.post("/calculations/power", request);
    return response.data;
  },
};
