/**
 * ATModifiersDisplay - Display archetype base modifiers
 * Epic 2.3 - Character Sheet Display
 *
 * Shows base HP, regeneration, recovery, and threat modifiers
 */

import type { Archetype } from "@/types/character.types";

export interface ATModifiersDisplayProps {
  archetype: Archetype | null;
  className?: string;
}

interface ModifierRow {
  name: string;
  value: number | undefined;
  format: (val: number) => string;
}

export function ATModifiersDisplay({
  archetype,
  className = "",
}: ATModifiersDisplayProps) {
  if (!archetype) {
    return (
      <div className="text-sm text-muted-foreground py-4 text-center">
        Select an archetype to view base modifiers.
      </div>
    );
  }

  const modifiers: ModifierRow[] = [
    {
      name: "Base HP (Level 50)",
      value: archetype.baseHp,
      format: (val: number) => val.toFixed(1),
    },
    {
      name: "Base Regeneration",
      value: archetype.baseRegen,
      format: (val: number) => `${(val * 100).toFixed(2)}%/s`,
    },
    {
      name: "Base Recovery",
      value: archetype.baseRecovery,
      format: (val: number) => `${(val * 100).toFixed(2)}%/s`,
    },
    {
      name: "Base Threat",
      value: archetype.baseThreat,
      format: (val: number) => `${(val * 100).toFixed(0)}%`,
    },
  ];

  return (
    <div className={`rounded-lg border ${className}`}>
      <div className="overflow-hidden">
        {/* Table Header */}
        <div className="border-b bg-muted/50 grid grid-cols-2 gap-4 px-4 py-3">
          <div className="text-sm font-medium">Modifier</div>
          <div className="text-sm font-medium text-right">Value</div>
        </div>

        {/* Table Body */}
        <div className="divide-y">
          {modifiers.map((mod) => (
            <div
              key={mod.name}
              className="grid grid-cols-2 gap-4 px-4 py-3 hover:bg-muted/30 transition-colors"
            >
              <div className="text-sm font-medium">{mod.name}</div>
              <div className="text-sm font-mono text-right">
                {mod.value !== undefined ? mod.format(mod.value) : "N/A"}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
