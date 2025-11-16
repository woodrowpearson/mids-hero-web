/**
 * TanStack Query hooks for Calculation API
 */

import { useMutation } from "@tanstack/react-query";
import { calculationApi } from "@/services";
import type {
  CalculateTotalsRequest,
  CalculatePowerRequest,
} from "@/types/api.types";

/**
 * Calculate build totals
 * Uses mutation since calculations are POST requests
 * No caching - always recalculate on demand
 */
export function useCalculateTotals() {
  return useMutation({
    mutationFn: (request: CalculateTotalsRequest) =>
      calculationApi.calculateTotals(request),
  });
}

/**
 * Calculate single power stats
 * Uses mutation for POST requests
 */
export function useCalculatePower() {
  return useMutation({
    mutationFn: (request: CalculatePowerRequest) =>
      calculationApi.calculatePower(request),
  });
}
