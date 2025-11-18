/**
 * PoolPowerSelector - Pool power dropdown (used 4 times)
 * Prevents duplicate pool selection across the 4 slots
 */

import { PowersetSelector } from "./PowersetSelector";
import { useCharacterStore } from "@/stores/characterStore";
import { usePowersets } from "@/hooks/usePowersets";
import { LoadingSpinner } from "@/components/ui/LoadingSpinner";
import { ErrorMessage } from "@/components/ui/ErrorMessage";

export interface PoolPowerSelectorProps {
  index: number; // 0-3 for the 4 pool slots
}

export function PoolPowerSelector({ index }: PoolPowerSelectorProps) {
  const poolPowersets = useCharacterStore((state) => state.poolPowersets);
  const setPoolPowerset = useCharacterStore((state) => state.setPoolPowerset);

  // Fetch all pool powersets (not archetype-specific)
  const { data: allPowersets, isLoading, error } = usePowersets({
    type: "Pool",
  });

  // Filter to pool powersets only
  const poolPowers = allPowersets?.filter((p) => p.type === "Pool") || [];

  // Filter out already-selected pools from OTHER slots
  const availablePools = poolPowers.filter((pool) => {
    const selectedInOtherSlot = poolPowersets.some(
      (p, idx) => idx !== index && p?.id === pool.id
    );
    return !selectedInOtherSlot;
  });

  const handleChange = (powerset: typeof poolPowersets[0]) => {
    setPoolPowerset(index, powerset);
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="flex flex-col gap-2">
        <label className="text-sm font-medium">Pool Power {index + 1}</label>
        <LoadingSpinner className="h-10" />
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="flex flex-col gap-2">
        <label className="text-sm font-medium">Pool Power {index + 1}</label>
        <ErrorMessage message="Failed to load pool powers" />
      </div>
    );
  }

  return (
    <PowersetSelector
      powersets={availablePools}
      selected={poolPowersets[index] ?? null}
      onChange={handleChange}
      disabled={false}
      placeholder={`Select Pool Power ${index + 1}`}
      label={`Pool Power ${index + 1}`}
      description={
        poolPowersets[index]
          ? undefined
          : index === 0
          ? "Optional: Choose up to 4 pool power sets"
          : undefined
      }
      allowClear={true}
    />
  );
}
