/**
 * MiscStatsPanel - Miscellaneous stats display component
 * Shows Accuracy, ToHit, and Damage bonuses
 * Simple text list (no bars) matching MidsReborn "Misc Effects"
 * Epic 4.2 component
 */

"use client";

import { cn } from "@/lib/utils";
import { MiscStats } from "@/types/totals.types";

export interface MiscStatsPanelProps {
  misc: MiscStats | null;
  variant?: "default" | "compact";
  className?: string;
}

export function MiscStatsPanel({
  misc,
  variant = "default",
  className,
}: MiscStatsPanelProps) {
  if (!misc) {
    return (
      <div className={cn("p-4 bg-gray-50 dark:bg-gray-800 rounded-lg", className)}>
        <h3 className={cn("font-semibold mb-2", variant === "compact" ? "text-sm" : "text-lg")}>
          Misc Effects
        </h3>
        <p className="text-sm text-gray-500 dark:text-gray-400">No misc data</p>
      </div>
    );
  }

  const isCompact = variant === "compact";

  // Format stat value with + sign for positive values
  const formatStat = (value: number): string => {
    const sign = value > 0 ? "+" : "";
    return `${sign}${value.toFixed(1)}%`;
  };

  return (
    <div className={cn("p-4 bg-gray-50 dark:bg-gray-800 rounded-lg space-y-2", className)}>
      <h3 className={cn("font-semibold mb-3", isCompact ? "text-sm" : "text-lg")}>
        Misc Effects
      </h3>

      <div className={cn("grid grid-cols-1 gap-2", isCompact ? "text-xs" : "text-sm")}>
        {/* Accuracy */}
        <div className="flex justify-between items-center">
          <span className="text-gray-600 dark:text-gray-400">Accuracy:</span>
          <span className="font-mono font-semibold text-gray-900 dark:text-gray-100">
            {formatStat(misc.accuracy)}
          </span>
        </div>

        {/* ToHit */}
        <div className="flex justify-between items-center">
          <span className="text-gray-600 dark:text-gray-400">ToHit:</span>
          <span className="font-mono font-semibold text-gray-900 dark:text-gray-100">
            {formatStat(misc.tohit)}
          </span>
        </div>

        {/* Damage */}
        <div className="flex justify-between items-center">
          <span className="text-gray-600 dark:text-gray-400">Damage:</span>
          <span className="font-mono font-semibold text-gray-900 dark:text-gray-100">
            {formatStat(misc.damage)}
          </span>
        </div>
      </div>
    </div>
  );
}
