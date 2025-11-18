/**
 * PrimaryPowersetSelector - Primary powerset dropdown
 * Filtered by selected archetype's primary powersets
 */

import React from "react";
import { PowersetSelector } from "./PowersetSelector";
import { useCharacterStore } from "@/stores/characterStore";
import { usePowersetsByArchetype } from "@/hooks/usePowersets";
import { LoadingSpinner } from "@/components/ui/LoadingSpinner";
import { ErrorMessage } from "@/components/ui/ErrorMessage";

export function PrimaryPowersetSelector() {
  const archetype = useCharacterStore((state) => state.archetype);
  const primaryPowerset = useCharacterStore((state) => state.primaryPowerset);
  const setPrimaryPowerset = useCharacterStore((state) => state.setPrimaryPowerset);

  // Fetch powersets for selected archetype
  const { data: powersets, isLoading, error } = usePowersetsByArchetype(
    archetype?.id
  );

  // Filter to primary powersets only
  const primaryPowersets = powersets?.filter((p) => p.type === "Primary") || [];

  // Loading state
  if (isLoading) {
    return (
      <div className="flex flex-col gap-2">
        <label className="text-sm font-medium">Primary Powerset</label>
        <LoadingSpinner className="h-10" />
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="flex flex-col gap-2">
        <label className="text-sm font-medium">Primary Powerset</label>
        <ErrorMessage message="Failed to load powersets" />
      </div>
    );
  }

  return (
    <PowersetSelector
      powersets={primaryPowersets}
      selected={primaryPowerset}
      onChange={setPrimaryPowerset}
      disabled={!archetype}
      placeholder={
        archetype
          ? "Select Primary Powerset"
          : "Select an archetype first"
      }
      label="Primary Powerset"
      description={
        !archetype
          ? "Choose an archetype to see available primary powersets"
          : undefined
      }
    />
  );
}
