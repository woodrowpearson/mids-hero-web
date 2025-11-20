/**
 * StatBar - Reusable horizontal stat bar component
 * Displays a label, value, and visual bar with cap indicators
 * Used for defense, resistance, HP, endurance, and other stats
 */

import { cn } from "@/lib/utils";

export interface StatBarProps {
  label: string; // Stat name (e.g., "Smashing", "Fire")
  value: number; // Current value (percentage, 0-100+)
  cap?: number; // Archetype cap (e.g., 45 for defense, 75 for resistance)
  color: "defense" | "resistance" | "hp" | "endurance" | "recharge";
  variant?: "default" | "compact";
  showPercentage?: boolean; // Default: true
  className?: string;
}

export function StatBar({
  label,
  value,
  cap,
  color,
  variant = "default",
  showPercentage = true,
  className,
}: StatBarProps) {
  // Clamp negative values to 0 (debuffs shouldn't show negative bars)
  const clampedValue = Math.max(0, value);

  // Calculate bar width as percentage of cap
  const percentage = cap ? Math.min((clampedValue / cap) * 100, 100) : 0;

  // Determine cap status
  const isAtCap = cap !== undefined && value >= cap && value < cap + 0.01; // Within rounding
  const isOverCap = cap !== undefined && value > cap + 0.01;

  // Color gradient classes by stat type
  const colorClasses = {
    defense: "bg-gradient-to-r from-purple-500 to-purple-700",
    resistance: "bg-gradient-to-r from-cyan-500 to-cyan-700",
    hp: "bg-gradient-to-r from-green-500 to-green-700",
    endurance: "bg-gradient-to-r from-blue-500 to-blue-700",
    recharge: "bg-gradient-to-r from-orange-500 to-orange-700",
  };

  // Size variants
  const isCompact = variant === "compact";

  return (
    <div
      className={cn(
        "flex items-center gap-2",
        isCompact ? "gap-2" : "gap-4",
        className
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

      {/* Percentage value */}
      {showPercentage && (
        <div
          className={cn(
            "text-right font-mono text-gray-900 dark:text-gray-100",
            isCompact ? "w-12 text-xs" : "w-16 text-sm"
          )}
        >
          {value.toFixed(1)}%
        </div>
      )}

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
            isOverCap && "border-2 border-red-400 shadow-red-400/50 shadow-sm"
          )}
          style={{ width: `${percentage}%` }}
          role="presentation"
          aria-label={`${label}: ${value.toFixed(1)}% of ${cap || 100}% cap`}
        />
      </div>
    </div>
  );
}
