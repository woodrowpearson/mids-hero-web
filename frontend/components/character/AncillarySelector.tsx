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

  // Check if this archetype has any ancillary powersets available
  // Epic ATs (Peacebringer, Warshade, Soldier, Widow) don't have ancillary powersets
  // so they will have an empty list here. Hide the selector entirely for these ATs.
  const hasAncillaryPowersets = ancillaryPowersets.length > 0;

  // Hide completely if no ancillary powersets are available (Epic ATs)
  // Only hide if we have loaded powersets and confirmed there are none
  if (!isLoading && !error && archetype && !hasAncillaryPowersets) {
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
