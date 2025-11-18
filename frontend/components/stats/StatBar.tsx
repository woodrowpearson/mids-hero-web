/**
 * StatBar - Reusable horizontal stat bar component
 * Displays a label, value, and visual bar with cap indicators
 * Used for defense, resistance, HP, endurance, and other stats
 *
 * Epic 4.1: Basic bar with percentage display
 * Epic 4.2: Extended with formats, sub-values, milestones
 */

import { cn } from "@/lib/utils";

export interface StatBarProps {
  label: string; // Stat name (e.g., "Smashing", "Fire", "Max HP")
  value: number; // Current value (can be percentage, whole number, decimal)
  cap?: number; // Archetype cap (e.g., 45 for defense, 75 for resistance)
  color: "defense" | "resistance" | "hp" | "hp-absorb" | "endurance" | "endurance-usage" | "recharge";
  variant?: "default" | "compact";

  // Epic 4.2: New formatting options
  format?: "percent" | "number" | "decimal" | "percent-offset"; // Default: "percent"
  suffix?: string; // Additional suffix (e.g., "/s")
  showSubValue?: string; // Sub-value shown below main value (e.g., "2.8/s")
  showMilestone?: number; // Highlight when value >= milestone
  allowNegative?: boolean; // Allow negative values (default: true)

  // Epic 4.1: Original props
  showPercentage?: boolean; // DEPRECATED: Use format instead
  className?: string;
}

export function StatBar({
  label,
  value,
  cap,
  color,
  variant = "default",
  format = "percent",
  suffix,
  showSubValue,
  showMilestone,
  allowNegative = true,
  showPercentage = true, // Deprecated, for Epic 4.1 backward compatibility
  className,
}: StatBarProps) {
  // Backward compatibility: if showPercentage is false, use format="number"
  const actualFormat = showPercentage === false ? "number" : format;

  // Calculate bar width as percentage of cap
  const percentage = cap ? Math.min((value / cap) * 100, 100) : 0;

  // Determine cap status
  const isAtCap = cap !== undefined && value >= cap && value < cap + 0.01; // Within rounding
  const isOverCap = cap !== undefined && value > cap + 0.01;

  // Check milestone status
  const isMilestoneReached = showMilestone !== undefined && value >= showMilestone;

  // Color gradient classes by stat type (Epic 4.2: added hp-absorb, endurance-usage)
  const colorClasses = {
    defense: "bg-gradient-to-r from-purple-500 to-purple-700",
    resistance: "bg-gradient-to-r from-cyan-500 to-cyan-700",
    hp: "bg-gradient-to-r from-green-500 to-green-700",
    "hp-absorb": "bg-gradient-to-r from-cyan-400 to-cyan-600",
    endurance: "bg-gradient-to-r from-blue-500 to-blue-700",
    "endurance-usage": "bg-gradient-to-r from-red-500 to-red-700",
    recharge: "bg-gradient-to-r from-orange-500 to-orange-700",
  };

  // Size variants
  const isCompact = variant === "compact";

  // Format value display (Epic 4.2)
  const formatValue = (val: number): string => {
    if (!allowNegative && val < 0) val = 0;

    switch (actualFormat) {
      case "number":
        return Math.round(val).toString();
      case "decimal":
        return val.toFixed(val % 1 === 0 ? 0 : 1); // 0 decimals if whole, 1 otherwise
      case "percent-offset":
        const sign = val > 0 ? "+" : "";
        return `${sign}${val.toFixed(1)}%`;
      case "percent":
      default:
        return `${val.toFixed(1)}%`;
    }
  };

  const displayValue = formatValue(value) + (suffix || "");

  return (
    <div className={cn("flex flex-col gap-1", className)}>
      <div
        className={cn(
          "flex items-center gap-2",
          isCompact ? "gap-2" : "gap-4"
        )}
      >
        {/* Label */}
        <div
          className={cn(
            "font-medium text-gray-700 dark:text-gray-300",
            isCompact ? "w-20 text-xs" : "w-24 text-sm"
          )}
        >
          {label}
        </div>

        {/* Value display (Epic 4.2: supports multiple formats) */}
        <div
          className={cn(
            "text-right font-mono text-gray-900 dark:text-gray-100",
            isCompact ? "w-16 text-xs" : "w-20 text-sm",
            isMilestoneReached && "text-green-500 dark:text-green-400 font-bold"
          )}
        >
          {displayValue}
        </div>

        {/* Visual bar */}
        <div
          className={cn(
            "relative flex-1 bg-gray-200 dark:bg-gray-700 rounded overflow-hidden",
            isCompact ? "h-4" : "h-6"
          )}
        >
          <div
            className={cn(
              "h-full rounded transition-all duration-300 ease-out",
              colorClasses[color],
              isAtCap && "border-2 border-yellow-400 shadow-yellow-400/50 shadow-sm",
              isOverCap && "border-2 border-red-400 shadow-red-400/50 shadow-sm",
              isMilestoneReached && "border-2 border-green-400 shadow-green-400/50 shadow-sm"
            )}
            style={{ width: `${percentage}%` }}
            role="presentation"
            aria-label={`${label}: ${displayValue} of ${cap ? `${cap}${suffix || '%'}` : '100%'} cap`}
          />
        </div>
      </div>

      {/* Sub-value (Epic 4.2: optional secondary value below main bar) */}
      {showSubValue && (
        <div className="flex items-center gap-2">
          <div className={cn(isCompact ? "w-20" : "w-24")} />
          <div
            className={cn(
              "text-xs text-gray-500 dark:text-gray-400 font-mono",
              isCompact ? "w-16" : "w-20"
            )}
          >
            {showSubValue}
          </div>
        </div>
      )}
    </div>
  );
}
