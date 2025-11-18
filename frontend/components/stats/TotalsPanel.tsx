/**
 * TotalsPanel - Main container for all stat displays
 * Integrates with characterStore and useCalculateTotals
 * Implements MidsReborn frmTotals window functionality
 *
 * Epic 4.1: Defense and Resistance displays
 * Epic 4.2: HP, Endurance, Recharge, and Misc stats displays
 */

"use client";

import { useEffect } from "react";
import { cn } from "@/lib/utils";
import { useCharacterStore } from "@/stores/characterStore";
import { useCalculateTotals } from "@/hooks/useCalculations";
import { DefensePanel } from "./DefensePanel";
import { ResistancePanel } from "./ResistancePanel";
import { HPPanel } from "./HPPanel"; // Epic 4.2
import { EndurancePanel } from "./EndurancePanel"; // Epic 4.2
import { RechargePanel } from "./RechargePanel"; // Epic 4.2
import { MiscStatsPanel } from "./MiscStatsPanel"; // Epic 4.2
import { LoadingSpinner } from "../ui/LoadingSpinner";
import { ErrorMessage } from "../ui/ErrorMessage";

export interface TotalsPanelProps {
  variant?: "default" | "compact";
  className?: string;
}

export function TotalsPanel({ variant = "default", className }: TotalsPanelProps) {
  // Get character state
  const archetype = useCharacterStore((state) => state.archetype);
  const totals = useCharacterStore((state) => state.totals);
  const isCalculating = useCharacterStore((state) => state.isCalculating);
  const setTotals = useCharacterStore((state) => state.setTotals);
  const setIsCalculating = useCharacterStore((state) => state.setIsCalculating);
  const exportBuild = useCharacterStore((state) => state.exportBuild);

  // TanStack Query mutation for calculations
  const {
    mutate: calculateTotals,
    isError,
    error,
    isPending,
  } = useCalculateTotals();

  // Auto-recalculate on mount if no totals
  useEffect(() => {
    if (!totals && archetype) {
      const buildData = exportBuild();
      setIsCalculating(true);

      calculateTotals(
        {
          archetype_id: buildData.character.archetype?.id || 0,
          origin_id: buildData.character.origin?.id || 0,
          alignment: buildData.character.alignment?.name || "Hero",
          level: buildData.character.level,
          powers: buildData.powers.map((powerEntry) => ({
            power_id: powerEntry.power.id,
            level_taken: powerEntry.level,
            slots: powerEntry.slots.map((slot) => ({
              enhancement_id: slot.enhancement?.id || 0,
              level: slot.level,
            })),
          })),
        },
        {
          onSuccess: (data) => {
            setTotals(data);
            setIsCalculating(false);
          },
          onError: () => {
            setIsCalculating(false);
          },
        }
      );
    }
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // Handle retry on error
  const handleRetry = () => {
    const buildData = exportBuild();
    setIsCalculating(true);

    calculateTotals(
      {
        archetype_id: buildData.character.archetype?.id || 0,
        origin_id: buildData.character.origin?.id || 0,
        alignment: buildData.character.alignment?.name || "Hero",
        level: buildData.character.level,
        powers: buildData.powers.map((powerEntry) => ({
          power_id: powerEntry.power.id,
          level_taken: powerEntry.level,
          slots: powerEntry.slots.map((slot) => ({
            enhancement_id: slot.enhancement?.id || 0,
            level: slot.level,
          })),
        })),
      },
      {
        onSuccess: (data) => {
          setTotals(data);
          setIsCalculating(false);
        },
        onError: () => {
          setIsCalculating(false);
        },
      }
    );
  };

  // No archetype selected
  if (!archetype) {
    return (
      <div className={cn("text-center py-8", className)}>
        <p className="text-gray-500 dark:text-gray-400">
          Select an archetype to view build totals
        </p>
      </div>
    );
  }

  // Loading state
  if (isCalculating || isPending) {
    return (
      <div className={cn("flex items-center justify-center py-8", className)}>
        <LoadingSpinner size="lg" />
        <span className="ml-3 text-gray-600 dark:text-gray-400">
          Calculating totals...
        </span>
      </div>
    );
  }

  // Error state
  if (isError) {
    return (
      <div className={cn(className)}>
        <ErrorMessage
          message={
            error instanceof Error
              ? error.message
              : "Failed to calculate build totals"
          }
          onRetry={handleRetry}
        />
      </div>
    );
  }

  // No totals yet
  if (!totals) {
    return null;
  }

  // Get archetype-specific caps (Epic 4.1)
  const defenseCap = archetype.defenseCap || 45;
  const resistanceCap = archetype.resistanceCap || 75;

  // Epic 4.2: Get archetype-specific caps for HP, Endurance
  const maxHPCap = archetype.maxHP || 2409; // Tanker cap (varies by AT)
  const regenCap = archetype.regenCap || 300; // Soft cap at 300%
  const maxEnduranceCap = archetype.maxEndurance || 100; // Usually 100
  const recoveryCap = archetype.recoveryCap || 10; // Visual cap

  // Render all stat panels (Epic 4.1 + Epic 4.2)
  return (
    <div
      className={cn(
        "grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6",
        variant === "compact" && "gap-4",
        className
      )}
    >
      {/* Epic 4.1: Defense and Resistance */}
      <DefensePanel
        defense={totals.defense}
        defenseCap={defenseCap}
        variant={variant}
      />
      <ResistancePanel
        resistance={totals.resistance}
        resistanceCap={resistanceCap}
        variant={variant}
      />

      {/* Epic 4.2: HP, Endurance, Recharge, Misc */}
      <HPPanel
        hp={totals.hp}
        maxHPCap={maxHPCap}
        regenCap={regenCap}
        variant={variant}
      />
      <EndurancePanel
        endurance={totals.endurance}
        maxEnduranceCap={maxEnduranceCap}
        recoveryCap={recoveryCap}
        variant={variant}
      />
      <RechargePanel
        recharge={totals.recharge}
        variant={variant}
      />
      <MiscStatsPanel
        misc={totals.misc}
        variant={variant}
      />
    </div>
  );
}
