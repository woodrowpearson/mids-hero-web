/**
 * ResistancePanel - Displays all resistance statistics
 * Shows 8 typed resistance values (no positional resistance)
 * Implements MidsReborn frmTotals resistance section
 */

import { cn } from "@/lib/utils";
import { StatBar } from "./StatBar";
import type { ResistanceStats } from "@/types/character.types";

export interface ResistancePanelProps {
  resistance: ResistanceStats;
  resistanceCap: number; // Archetype-specific cap (75 for most, 90 for Tanker/Brute)
  variant?: "default" | "compact";
  className?: string;
}

export function ResistancePanel({
  resistance,
  resistanceCap,
  variant = "default",
  className,
}: ResistancePanelProps) {
  // Typed resistance values (8 damage types, no positional resistance)
  const resistances = [
    { label: "Smashing", value: resistance.smashing },
    { label: "Lethal", value: resistance.lethal },
    { label: "Fire", value: resistance.fire },
    { label: "Cold", value: resistance.cold },
    { label: "Energy", value: resistance.energy },
    { label: "Negative", value: resistance.negative },
    { label: "Toxic", value: resistance.toxic },
    { label: "Psionic", value: resistance.psionic },
  ];

  return (
    <div className={cn("space-y-4", className)}>
      {/* Panel Header */}
      <h3
        className={cn(
          "font-semibold text-cyan-600 dark:text-cyan-400",
          variant === "compact" ? "text-base" : "text-lg"
        )}
      >
        Resistance
      </h3>

      {/* Resistance Bars */}
      <div className="space-y-1">
        {resistances.map(({ label, value }) => (
          <StatBar
            key={label}
            label={label}
            value={value}
            cap={resistanceCap}
            color="resistance"
            variant={variant}
          />
        ))}
      </div>
    </div>
  );
}
