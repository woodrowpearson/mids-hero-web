/**
 * RechargePanel - Global recharge display component
 * Shows global recharge % from set bonuses and IOs
 * Highlights perma-Hasten milestone at +70%
 * Epic 4.2 component
 */

"use client";

import { cn } from "@/lib/utils";
import { RechargeStats } from "@/types/totals.types";
import { StatBar } from "./StatBar";

export interface RechargePanelProps {
  recharge: RechargeStats | null;
  variant?: "default" | "compact";
  className?: string;
}

export function RechargePanel({
  recharge,
  variant = "default",
  className,
}: RechargePanelProps) {
  if (!recharge) {
    return (
      <div className={cn("p-4 bg-gray-50 dark:bg-gray-800 rounded-lg", className)}>
        <h3 className={cn("font-semibold mb-2", variant === "compact" ? "text-sm" : "text-lg")}>
          Recharge
        </h3>
        <p className="text-sm text-gray-500 dark:text-gray-400">No recharge data</p>
      </div>
    );
  }

  const isCompact = variant === "compact";
  const isPermaHaste = recharge.global_percent >= 70; // Perma-Hasten threshold

  return (
    <div className={cn("p-4 bg-gray-50 dark:bg-gray-800 rounded-lg space-y-2", className)}>
      <h3 className={cn("font-semibold mb-3", isCompact ? "text-sm" : "text-lg")}>
        Recharge
      </h3>

      {/* Global Recharge % */}
      <StatBar
        label="Global Recharge"
        value={recharge.global_percent}
        cap={200} // Visual cap (no hard cap in game)
        color="recharge"
        format="percent-offset"
        showMilestone={70} // Perma-Hasten milestone
        variant={variant}
      />

      {/* Perma-Hasten milestone indicator */}
      {isPermaHaste && (
        <div
          className={cn(
            "text-green-500 dark:text-green-400 flex items-center gap-2",
            isCompact ? "text-xs" : "text-sm"
          )}
        >
          <svg
            className="w-4 h-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M5 13l4 4L19 7"
            />
          </svg>
          <span>Perma-Hasten achieved (+70% threshold)</span>
        </div>
      )}
    </div>
  );
}
