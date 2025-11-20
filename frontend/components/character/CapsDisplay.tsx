/**
 * CapsDisplay - Display archetype caps
 * Epic 2.3 - Character Sheet Display
 *
 * Shows 7 archetype caps: HP, Damage, Resistance, Defense, Regen, Recovery, Recharge
 */

import type { Archetype } from "@/types/character.types";

export interface CapsDisplayProps {
  archetype: Archetype | null;
  className?: string;
}

interface CapRow {
  name: string;
  value: number | undefined;
  format: (val: number) => string;
  description: string;
}

export function CapsDisplay({ archetype, className = "" }: CapsDisplayProps) {
  if (!archetype) {
    return (
      <div className="text-sm text-muted-foreground py-4 text-center">
        Select an archetype to view caps.
      </div>
    );
  }

  const caps: CapRow[] = [
    {
      name: "HP Cap",
      value: archetype.hpCap,
      format: (val: number) => val.toFixed(0),
      description: "Maximum HP value",
    },
    {
      name: "Damage Cap",
      value: archetype.damageCap,
      format: (val: number) => `${(val * 100).toFixed(0)}%`,
      description: "Maximum damage buff",
    },
    {
      name: "Resistance Cap",
      value: archetype.resistanceCap,
      format: (val: number) => `${(val * 100).toFixed(0)}%`,
      description: "Maximum damage resistance",
    },
    {
      name: "Defense Cap (Display)",
      value: archetype.defenseCap,
      format: (val: number) => `${(val * 100).toFixed(0)}%`,
      description: "Maximum defense (display only, soft cap is 45%)",
    },
    {
      name: "Regeneration Cap",
      value: archetype.regenerationCap,
      format: (val: number) => `${(val * 100).toFixed(0)}%`,
      description: "Maximum regeneration increase",
    },
    {
      name: "Recovery Cap",
      value: archetype.recoveryCap,
      format: (val: number) => `${(val * 100).toFixed(0)}%`,
      description: "Maximum recovery increase",
    },
    {
      name: "Recharge Cap",
      value: archetype.rechargeCap,
      format: (val: number) => `${(val * 100).toFixed(0)}%`,
      description: "Maximum recharge reduction",
    },
  ];

  return (
    <div className={`rounded-lg border ${className}`}>
      <div className="overflow-hidden">
        {/* Table Header */}
        <div className="border-b bg-muted/50 grid grid-cols-3 gap-4 px-4 py-3">
          <div className="text-sm font-medium">Cap Type</div>
          <div className="text-sm font-medium text-right">Value</div>
          <div className="text-sm font-medium">Description</div>
        </div>

        {/* Table Body */}
        <div className="divide-y">
          {caps.map((cap) => (
            <div
              key={cap.name}
              className="grid grid-cols-3 gap-4 px-4 py-3 hover:bg-muted/30 transition-colors"
            >
              <div className="text-sm font-medium">{cap.name}</div>
              <div className="text-sm font-mono text-right">
                {cap.value !== undefined ? cap.format(cap.value) : "N/A"}
              </div>
              <div className="text-sm text-muted-foreground">
                {cap.description}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
