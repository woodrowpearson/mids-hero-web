/**
 * SecondaryPowersetSelector - Secondary powerset dropdown
 * Filtered by selected archetype's secondary powersets
 * Handles linked secondaries (e.g., Kheldian ATs)
 */

import React, { useEffect } from "react";
import { PowersetSelector } from "./PowersetSelector";
import { useCharacterStore } from "@/stores/characterStore";
import { usePowersetsByArchetype } from "@/hooks/usePowersets";
import { LoadingSpinner } from "@/components/ui/LoadingSpinner";
import { ErrorMessage } from "@/components/ui/ErrorMessage";

export function SecondaryPowersetSelector() {
  const archetype = useCharacterStore((state) => state.archetype);
  const primaryPowerset = useCharacterStore((state) => state.primaryPowerset);
  const secondaryPowerset = useCharacterStore((state) => state.secondaryPowerset);
  const setSecondaryPowerset = useCharacterStore(
    (state) => state.setSecondaryPowerset
  );

  // Fetch powersets for selected archetype
  const { data: powersets, isLoading, error } = usePowersetsByArchetype(
    archetype?.id
  );

  // Filter to secondary powersets only
  const secondaryPowersets = powersets?.filter((p) => p.type === "Secondary") || [];

  // Check for linked secondary (Epic ATs like Kheldians have linked primary/secondary)
  // Note: This assumes the backend provides a linkedSecondaryId field
  // For now, we'll implement basic logic - can be enhanced later
  const isLinkedSecondary = false; // TODO: Implement linked secondary detection from backend data

  // Auto-select if only one secondary available (common for Epic ATs)
  useEffect(() => {
    if (
      !secondaryPowerset &&
      secondaryPowersets.length === 1 &&
      archetype
    ) {
      setSecondaryPowerset(secondaryPowersets[0]);
    }
  }, [secondaryPowersets, secondaryPowerset, setSecondaryPowerset, archetype]);

  // Loading state
  if (isLoading) {
    return (
      <div className="flex flex-col gap-2">
        <label className="text-sm font-medium">Secondary Powerset</label>
        <LoadingSpinner className="h-10" />
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="flex flex-col gap-2">
        <label className="text-sm font-medium">Secondary Powerset</label>
        <ErrorMessage message="Failed to load powersets" />
      </div>
    );
  }

  return (
    <PowersetSelector
      powersets={secondaryPowersets}
      selected={secondaryPowerset}
      onChange={setSecondaryPowerset}
      disabled={!archetype || isLinkedSecondary}
      placeholder={
        archetype
          ? isLinkedSecondary
            ? "Linked to primary"
            : "Select Secondary Powerset"
          : "Select an archetype first"
      }
      label="Secondary Powerset"
      description={
        !archetype
          ? "Choose an archetype to see available secondary powersets"
          : isLinkedSecondary
          ? "Secondary powerset is linked to your primary selection"
          : undefined
      }
    />
  );
}
