/**
 * TanStack Query hook for fetching archetype inherent powers
 * Epic 2.3 - Character Sheet Display
 */

import { useQuery } from "@tanstack/react-query";
import { archetypeApi } from "@/services";
import type { Power } from "@/types/character.types";

/**
 * Fetch inherent powers for a specific archetype
 * Returns powers sorted by priority for proper display order
 *
 * @param archetypeId - The archetype ID to fetch inherent powers for
 * @returns Query result with inherent powers array
 *
 * @example
 * const { data: inherentPowers, isLoading } = useInherentPowers(archetype?.id);
 */
export function useInherentPowers(archetypeId: number | undefined) {
  return useQuery({
    queryKey: ["inherent-powers", archetypeId],
    queryFn: async (): Promise<Power[]> => {
      if (!archetypeId) return [];

      // Fetch powersets with type filter for "inherent"
      // Uses GET /api/archetypes/{id}/powersets?powerset_type=inherent
      const powersets = await archetypeApi.getPowersets(archetypeId, "inherent");

      // Extract powers from the inherent powerset(s)
      const inherentPowers: Power[] = [];
      for (const powerset of powersets) {
        if (powerset.powers) {
          inherentPowers.push(...powerset.powers);
        }
      }

      // Sort by priority (MidsReborn behavior)
      // Powers with lower priority values appear first
      return inherentPowers.sort((a, b) => {
        const priorityA = a.priority ?? 999;
        const priorityB = b.priority ?? 999;
        return priorityA - priorityB;
      });
    },
    staleTime: Infinity, // Static game data, cache forever
    enabled: !!archetypeId, // Only fetch when archetype is selected
  });
}
