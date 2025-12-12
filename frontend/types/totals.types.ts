/**
 * TypeScript types for build totals and stats
 * Used by TotalsPanel and all stat display components
 *
 * Re-exports types from character.types.ts for backward compatibility.
 * The canonical definitions are in character.types.ts.
 */

// Re-export all stat types from character.types.ts (canonical source)
export type {
  DefenseStats,
  ResistanceStats,
  HPStats,
  EnduranceStats,
  RechargeStats,
  MiscStats,
  CalculatedTotals,
  Archetype,
} from "./character.types";
