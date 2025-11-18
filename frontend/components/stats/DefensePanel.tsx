/**
 * DefensePanel - Displays all defense statistics
 * Shows 8 typed defense values + 3 positional defense values
 * Implements MidsReborn frmTotals defense section
 */

import { cn } from "@/lib/utils";
import { StatBar } from "./StatBar";
import type { DefenseStats } from "@/types/character.types";

export interface DefensePanelProps {
  defense: DefenseStats;
  defenseCap: number; // Archetype-specific cap (45 for most, 50 for Tanker/Brute)
  variant?: "default" | "compact";
  className?: string;
}

export function DefensePanel({
  defense,
  defenseCap,
  variant = "default",
  className,
}: DefensePanelProps) {
  // Typed defense values (8 damage types)
  const typedDefenses = [
    { label: "Smashing", value: defense.smashing },
    { label: "Lethal", value: defense.lethal },
    { label: "Fire", value: defense.fire },
    { label: "Cold", value: defense.cold },
    { label: "Energy", value: defense.energy },
    { label: "Negative", value: defense.negative },
    { label: "Toxic", value: defense.toxic },
    { label: "Psionic", value: defense.psionic },
  ];

  // Positional defense values (3 positions)
  const positionalDefenses = [
    { label: "Melee", value: defense.melee },
    { label: "Ranged", value: defense.ranged },
    { label: "AoE", value: defense.aoe },
  ];

  return (
    <div className={cn("space-y-4", className)}>
      {/* Panel Header */}
      <h3
        className={cn(
          "font-semibold text-purple-600 dark:text-purple-400",
          variant === "compact" ? "text-base" : "text-lg"
        )}
      >
        Defense
      </h3>

      {/* Typed Defense Section */}
      <div className="space-y-2">
        <h4
          className={cn(
            "font-medium text-gray-600 dark:text-gray-400",
            variant === "compact" ? "text-xs" : "text-sm"
          )}
        >
          Typed Defense
        </h4>
        <div className="space-y-1">
          {typedDefenses.map(({ label, value }) => (
            <StatBar
              key={label}
              label={label}
              value={value}
              cap={defenseCap}
              color="defense"
              variant={variant}
            />
          ))}
        </div>
      </div>

      {/* Positional Defense Section */}
      <div className="space-y-2">
        <h4
          className={cn(
            "font-medium text-gray-600 dark:text-gray-400",
            variant === "compact" ? "text-xs" : "text-sm"
          )}
        >
          Positional Defense
        </h4>
        <div className="space-y-1">
          {positionalDefenses.map(({ label, value }) => (
            <StatBar
              key={label}
              label={label}
              value={value}
              cap={defenseCap}
              color="defense"
              variant={variant}
            />
          ))}
        </div>
      </div>
    </div>
  );
}
