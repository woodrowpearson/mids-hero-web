/**
 * TanStack Query hooks for Powerset data
 */

import { useQuery } from "@tanstack/react-query";
import { powerApi } from "@/services";
import type { GetPowersetsParams } from "@/types/api.types";

/**
 * Fetch all powersets (optionally filtered by archetype)
 * Cached forever (static game data)
 */
export function usePowersets(params?: GetPowersetsParams) {
  return useQuery({
    queryKey: ["powersets", params],
    queryFn: () => powerApi.getPowersets(params),
    staleTime: Infinity, // Never refetch (static data)
  });
}

/**
 * Fetch powersets for a specific archetype
 * Lazy loading - only fetches when archetype is selected
 */
export function usePowersetsByArchetype(archetypeId?: number) {
  return useQuery({
    queryKey: ["powersets", { archetypeId }],
    queryFn: () => powerApi.getPowersets({ archetypeId }),
    staleTime: Infinity,
    enabled: !!archetypeId && archetypeId > 0, // Only fetch when archetype selected
  });
}
