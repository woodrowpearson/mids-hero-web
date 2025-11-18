/**
 * AncillarySelector - Ancillary/Epic powerset dropdown
 * Unlocks at level 35+, hidden for Epic ATs
 */

import React from "react";
import { PowersetSelector } from "./PowersetSelector";
import { useCharacterStore } from "@/stores/characterStore";
import { usePowersetsByArchetype } from "@/hooks/usePowersets";
import { LoadingSpinner } from "@/components/ui/LoadingSpinner";
import { ErrorMessage } from "@/components/ui/ErrorMessage";

export function AncillarySelector() {
  const archetype = useCharacterStore((state) => state.archetype);
  const ancillaryPowerset = useCharacterStore((state) => state.ancillaryPowerset);
  const setAncillaryPowerset = useCharacterStore(
    (state) => state.setAncillaryPowerset
  );
  const level = useCharacterStore((state) => state.level);

  // Fetch powersets for selected archetype
  const { data: powersets, isLoading, error } = usePowersetsByArchetype(
    archetype?.id
  );

  // Filter to ancillary/epic powersets only
  const ancillaryPowersets =
    powersets?.filter((p) => p.type === "Ancillary" || p.type === "Epic") || [];

  // Check if this is an Epic AT (Peacebringer, Warshade, etc.)
  // Epic ATs don't have ancillary powersets
  // Note: This assumes the backend provides an isEpic flag on archetypes
  // For now, we'll check by archetype name
  const isEpicAT =
    archetype?.name.includes("Peacebringer") ||
    archetype?.name.includes("Warshade") ||
    archetype?.name.includes("Soldier") ||
    archetype?.name.includes("Widow") ||
    false;

  // Hide completely for Epic ATs
  if (isEpicAT) {
    return null;
  }

  const isEnabled = level >= 35;

  // Loading state
  if (isLoading) {
    return (
      <div className="flex flex-col gap-2">
        <label className="text-sm font-medium">
          Ancillary/Epic Powerset
          {!isEnabled && (
            <span className="text-muted-foreground"> (Unlocks at level 35)</span>
          )}
        </label>
        <LoadingSpinner className="h-10" />
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="flex flex-col gap-2">
        <label className="text-sm font-medium">Ancillary/Epic Powerset</label>
        <ErrorMessage message="Failed to load powersets" />
      </div>
    );
  }

  return (
    <PowersetSelector
      powersets={ancillaryPowersets}
      selected={ancillaryPowerset}
      onChange={setAncillaryPowerset}
      disabled={!isEnabled || !archetype}
      placeholder={
        !archetype
          ? "Select an archetype first"
          : !isEnabled
          ? "Unlocks at level 35"
          : "Select Ancillary/Epic Powerset"
      }
      label={
        <span>
          Ancillary/Epic Powerset
          {!isEnabled && (
            <span className="text-muted-foreground font-normal">
              {" "}
              (Unlocks at level 35)
            </span>
          )}
        </span>
      }
      description={
        !archetype
          ? "Choose an archetype to see available ancillary powersets"
          : !isEnabled
          ? `Available at level 35 (current level: ${level})`
          : undefined
      }
      allowClear={true}
    />
  );
}
