/**
 * TypeScript types for build totals and stats
 * Used by TotalsPanel and all stat display components
 */

// Epic 4.1: Defense stats
export interface DefenseStats {
  smashing: number;
  lethal: number;
  fire: number;
  cold: number;
  energy: number;
  negative: number;
  toxic: number;
  psionic: number;
  melee: number;
  ranged: number;
  aoe: number;
}

// Epic 4.1: Resistance stats
export interface ResistanceStats {
  smashing: number;
  lethal: number;
  fire: number;
  cold: number;
  energy: number;
  negative: number;
  toxic: number;
  psionic: number;
}

// Epic 4.2: HP stats
export interface HPStats {
  max: number; // Max HP value
  regen_percent: number; // Regeneration % (base 100%)
  regen_per_second: number; // HP regenerated per second
  absorb?: number; // Absorb shield value (optional)
}

// Epic 4.2: Endurance stats
export interface EnduranceStats {
  max: number; // Max Endurance value (usually 100)
  recovery_per_second: number; // Endurance recovered per second
  usage_per_second: number; // Endurance used per second (0 for static build)
}

// Epic 4.2: Recharge stats
export interface RechargeStats {
  global_percent: number; // Global recharge % from set bonuses, IOs (base 0%)
}

// Epic 4.2: Misc stats
export interface MiscStats {
  accuracy: number; // Global accuracy bonus %
  tohit: number; // Global tohit bonus %
  damage: number; // Global damage bonus %
}

// Combined totals interface
export interface CalculatedTotals {
  defense: DefenseStats;
  resistance: ResistanceStats;
  hp: HPStats; // Epic 4.2
  endurance: EnduranceStats; // Epic 4.2
  recharge: RechargeStats; // Epic 4.2
  misc: MiscStats; // Epic 4.2
}

// Archetype interface (with caps for all stat types)
export interface Archetype {
  id: number;
  name: string;
  displayName?: string;
  icon?: string;

  // Epic 4.1 caps
  defenseCap: number; // 45% or 50%
  resistanceCap: number; // 75% or 90%

  // Epic 4.2 caps
  maxHP?: number; // Archetype-specific max HP
  regenCap?: number; // Regen % cap (usually 300%)
  maxEndurance?: number; // Usually 100, some ATs higher
  recoveryCap?: number; // Recovery cap

  // Damage cap (for future use)
  damageCap?: number; // 400% for Tanker, 500% for Scrapper, etc.
}
