/**
 * TanStack Query hooks for Archetype data
 */

import { useQuery } from "@tanstack/react-query";
import { archetypeApi } from "@/services";

/**
 * Fetch all archetypes
 * Cached forever (static game data)
 */
export function useArchetypes() {
  return useQuery({
    queryKey: ["archetypes"],
    queryFn: () => archetypeApi.getAll(),
    staleTime: Infinity, // Never refetch (static data)
  });
}

/**
 * Fetch archetype by ID
 */
export function useArchetype(id: number) {
  return useQuery({
    queryKey: ["archetype", id],
    queryFn: () => archetypeApi.getById(id),
    staleTime: Infinity,
    enabled: id > 0, // Only run if valid ID
  });
}
