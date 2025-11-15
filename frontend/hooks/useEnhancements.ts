/**
 * TanStack Query hooks for Enhancement data
 */

import { useQuery } from "@tanstack/react-query";
import { enhancementApi } from "@/services";
import type { GetEnhancementsParams } from "@/types/api.types";

/**
 * Fetch all enhancements (optionally filtered)
 * Cached forever (static game data)
 */
export function useEnhancements(params?: GetEnhancementsParams) {
  return useQuery({
    queryKey: ["enhancements", params],
    queryFn: () => enhancementApi.getAll(params),
    staleTime: Infinity,
  });
}

/**
 * Fetch all enhancement sets
 */
export function useEnhancementSets() {
  return useQuery({
    queryKey: ["enhancement-sets"],
    queryFn: () => enhancementApi.getSets(),
    staleTime: Infinity,
  });
}

/**
 * Fetch enhancement set by ID
 */
export function useEnhancementSet(setId: number) {
  return useQuery({
    queryKey: ["enhancement-set", setId],
    queryFn: () => enhancementApi.getSetById(setId),
    staleTime: Infinity,
    enabled: setId > 0,
  });
}
