/**
 * TanStack Query hooks for Power and Powerset data
 */

import { useQuery } from "@tanstack/react-query";
import { powerApi } from "@/services";
import type { GetPowersetsParams } from "@/types/api.types";

/**
 * Fetch all powersets (optionally filtered)
 * Cached forever (static game data)
 */
export function usePowersets(params?: GetPowersetsParams) {
  return useQuery({
    queryKey: ["powersets", params],
    queryFn: () => powerApi.getPowersets(params),
    staleTime: Infinity,
  });
}

/**
 * Fetch powers in a specific powerset
 */
export function usePowersetPowers(powersetId: number) {
  return useQuery({
    queryKey: ["powerset-powers", powersetId],
    queryFn: () => powerApi.getPowersetPowers(powersetId),
    staleTime: Infinity,
    enabled: powersetId > 0,
  });
}

/**
 * Fetch all powers
 */
export function usePowers() {
  return useQuery({
    queryKey: ["powers"],
    queryFn: () => powerApi.getAllPowers(),
    staleTime: Infinity,
  });
}

/**
 * Fetch power by ID
 */
export function usePower(powerId: number) {
  return useQuery({
    queryKey: ["power", powerId],
    queryFn: () => powerApi.getPowerById(powerId),
    staleTime: Infinity,
    enabled: powerId > 0,
  });
}
