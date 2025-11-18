/**
 * EndurancePanel - Endurance stats display component
 * Shows Max End, Recovery/s, and Usage/s
 * Epic 4.2 component
 */

"use client";

import { cn } from "@/lib/utils";
import { EnduranceStats } from "@/types/totals.types";
import { StatBar } from "./StatBar";

export interface EndurancePanelProps {
  endurance: EnduranceStats | null;
  maxEnduranceCap?: number; // Usually 100, some ATs higher
  recoveryCap?: number; // Visual cap for recovery bar
  variant?: "default" | "compact";
  className?: string;
}

export function EndurancePanel({
  endurance,
  maxEnduranceCap = 100, // Base endurance cap
  recoveryCap = 10, // Visual cap for bar width
  variant = "default",
  className,
}: EndurancePanelProps) {
  if (!endurance) {
    return (
      <div className={cn("p-4 bg-gray-50 dark:bg-gray-800 rounded-lg", className)}>
        <h3 className={cn("font-semibold mb-2", variant === "compact" ? "text-sm" : "text-lg")}>
          Endurance
        </h3>
        <p className="text-sm text-gray-500 dark:text-gray-400">No endurance data</p>
      </div>
    );
  }

  const isCompact = variant === "compact";

  return (
    <div className={cn("p-4 bg-gray-50 dark:bg-gray-800 rounded-lg space-y-2", className)}>
      <h3 className={cn("font-semibold mb-3", isCompact ? "text-sm" : "text-lg")}>
        Endurance
      </h3>

      {/* Max End */}
      <StatBar
        label="Max End"
        value={endurance.max}
        cap={maxEnduranceCap}
        color="endurance"
        format="number"
        variant={variant}
      />

      {/* End Rec (Recovery/s) */}
      <StatBar
        label="End Rec"
        value={endurance.recovery_per_second}
        cap={recoveryCap}
        color="endurance"
        format="decimal"
        suffix="/s"
        variant={variant}
      />

      {/* End Use (Usage/s) */}
      <StatBar
        label="End Use"
        value={endurance.usage_per_second}
        cap={recoveryCap}
        color="endurance-usage"
        format="decimal"
        suffix="/s"
        allowNegative={false}
        variant={variant}
      />
    </div>
  );
}
