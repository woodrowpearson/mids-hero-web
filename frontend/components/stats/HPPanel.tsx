/**
 * HPPanel - Health/HP stats display component
 * Shows Max HP, Regeneration %, and Absorb (optional)
 * Epic 4.2 component
 */

"use client";

import { cn } from "@/lib/utils";
import { HPStats } from "@/types/totals.types";
import { StatBar } from "./StatBar";

export interface HPPanelProps {
  hp: HPStats | null;
  maxHPCap?: number; // Archetype-specific max HP cap
  regenCap?: number; // Regen % cap (usually 300%)
  variant?: "default" | "compact";
  className?: string;
}

export function HPPanel({
  hp,
  maxHPCap = 2409, // Tanker cap (varies by AT)
  regenCap = 300, // Soft cap at 300%
  variant = "default",
  className,
}: HPPanelProps) {
  if (!hp) {
    return (
      <div className={cn("p-4 bg-gray-50 dark:bg-gray-800 rounded-lg", className)}>
        <h3 className={cn("font-semibold mb-2", variant === "compact" ? "text-sm" : "text-lg")}>
          Health
        </h3>
        <p className="text-sm text-gray-500 dark:text-gray-400">No HP data</p>
      </div>
    );
  }

  const isCompact = variant === "compact";

  return (
    <div className={cn("p-4 bg-gray-50 dark:bg-gray-800 rounded-lg space-y-2", className)}>
      <h3 className={cn("font-semibold mb-3", isCompact ? "text-sm" : "text-lg")}>
        Health
      </h3>

      {/* Max HP */}
      <StatBar
        label="Max HP"
        value={hp.max}
        cap={maxHPCap}
        color="hp"
        format="number"
        variant={variant}
      />

      {/* Regeneration % with per-second sub-value */}
      <StatBar
        label="Regeneration"
        value={hp.regen_percent}
        cap={regenCap}
        color="hp"
        format="percent"
        showSubValue={`${hp.regen_per_second.toFixed(1)}/s`}
        variant={variant}
      />

      {/* Absorb (only show if > 0) */}
      {hp.absorb !== undefined && hp.absorb > 0 && (
        <StatBar
          label="Absorb"
          value={hp.absorb}
          color="hp-absorb"
          format="number"
          variant={variant}
        />
      )}
    </div>
  );
}
