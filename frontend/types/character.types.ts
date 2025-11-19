/**
 * Character-related TypeScript type definitions
 * Based on City of Heroes game data and MidsReborn architecture
 */

// Archetype (AT) definition
export interface Archetype {
  id: number;
  name: string;
  displayName: string;
  damageScale?: number; // Damage multiplier for this AT (legacy field)

  // Base modifiers (Epic 2.3)
  baseHp?: number; // Base HP at level 50
  baseRegen?: number; // Base regeneration rate (decimal, e.g., 0.02 = 2%/s)
  baseRecovery?: number; // Base endurance recovery (decimal, e.g., 0.0167 = 1.67%/s)
  baseThreat?: number; // Base threat/aggro modifier (decimal, e.g., 1.0 = 100%)

  // Archetype caps (Epic 2.3)
  damageCap?: number; // Max damage bonus (decimal, e.g., 5.0 = 500%)
  resistanceCap?: number; // Max resistance (decimal, e.g., 0.75 = 75%)
  defenseCap?: number; // Max defense display (decimal, e.g., 2.25 = 225%)
  hpCap?: number; // Max HP cap (absolute value)
  regenerationCap?: number; // Max regeneration (decimal, e.g., 30.0 = 3000%)
  recoveryCap?: number; // Max recovery (decimal, e.g., 8.0 = 800%)
  rechargeCap?: number; // Max recharge speed (decimal, e.g., 5.0 = 500%)
}

// Origin definition
export interface Origin {
  id: number;
  name: string;
  displayName: string;
  description: string;
}

// Alignment definition
export type AlignmentType = "Hero" | "Villain" | "Vigilante" | "Rogue";

export interface Alignment {
  id: number;
  name: AlignmentType;
  displayName: string;
}

// Powerset types
export type PowersetType = "Primary" | "Secondary" | "Pool" | "Ancillary" | "Epic" | "Inherent";

export interface Powerset {
  id: number;
  name: string;
  displayName: string;
  archetypeId: number;
  type: PowersetType;
  description: string;
}

// Power definition
export interface Power {
  id: number;
  name: string;
  displayName: string;
  description?: string; // Epic 2.3: For inherent power tooltips
  powersetId: number;
  levelAvailable: number;
  prerequisitePowerIds?: number[]; // Powers that must be taken first
  effects: Effect[];
  iconUrl?: string;
  priority?: number; // Epic 2.3: For sorting inherent powers
}

// Effect types (buffs, debuffs, damage, etc.)
export type EffectType =
  | "Damage"
  | "Defense"
  | "Resistance"
  | "Heal"
  | "Endurance"
  | "ToHit"
  | "Accuracy"
  | "Recharge"
  | "Hold"
  | "Stun"
  | "Sleep"
  | "Immobilize"
  | "Knockback"
  | "Confuse"
  | "Fear"
  | "Taunt"
  | "Recovery"
  | "Regeneration"
  | "MaxHP"
  | "MaxEndurance";

// Damage/Defense types
export type AspectType =
  | "Smashing"
  | "Lethal"
  | "Fire"
  | "Cold"
  | "Energy"
  | "Negative"
  | "Psionic"
  | "Toxic"
  | "Melee"
  | "Ranged"
  | "AoE"
  | "All";

export interface Effect {
  id: number;
  effectType: EffectType;
  aspect: AspectType;
  magnitude: number;
  duration?: number;
  probability?: number;
}

// Power entry (power taken in build with slotting)
export interface PowerEntry {
  power: Power;
  level: number; // Level when power was taken
  slots: Slot[];
}

// Slot definition
export interface Slot {
  enhancement: Enhancement | null;
  level: number; // Level of the enhancement
}

// Enhancement types
export type EnhancementType = "TO" | "DO" | "SO" | "IO";

export interface Enhancement {
  id: number;
  name: string;
  displayName: string;
  type: EnhancementType;
  setId?: number; // If part of an IO set
  bonuses: EnhancementBonus[];
  iconUrl?: string;
}

// Enhancement bonus (what the enhancement provides)
export interface EnhancementBonus {
  attribute: string; // "Damage", "Accuracy", "Recharge", etc.
  value: number; // Percentage boost (e.g., 42.4 for +42.4%)
}

// Enhancement set definition
export interface EnhancementSet {
  id: number;
  name: string;
  displayName: string;
  enhancements: Enhancement[];
  bonuses: SetBonus[];
}

// Set bonus (activated when X pieces slotted)
export interface SetBonus {
  piecesRequired: number; // 2, 3, 4, 5, or 6
  effects: Effect[];
}

// Character state
export interface Character {
  name: string;
  archetype: Archetype | null;
  origin: Origin | null;
  alignment: Alignment | null;
  level: number;
}

// Powerset slots
export interface PowersetSlots {
  primary: Powerset | null;
  secondary: Powerset | null;
  pools: [Powerset | null, Powerset | null, Powerset | null, Powerset | null];
  ancillary: Powerset | null;
}

// Build data (complete build information)
export interface BuildData {
  character: Character;
  powersets: PowersetSlots;
  powers: PowerEntry[];
  totals?: CalculatedTotals; // Optional, calculated by backend
}

// Calculated totals (from backend)
export interface CalculatedTotals {
  defense: DefenseStats;
  resistance: ResistanceStats;
  maxHP: number;
  maxEndurance: number;
  regeneration: number; // HP/sec
  recovery: number; // End/sec
  globalRecharge: number; // Percentage
  globalDamage: number; // Percentage
  globalAccuracy: number; // Percentage
  globalToHit: number; // Percentage
}

// Defense statistics
export interface DefenseStats {
  smashing: number;
  lethal: number;
  fire: number;
  cold: number;
  energy: number;
  negative: number;
  psionic: number;
  toxic: number;
  melee: number;
  ranged: number;
  aoe: number;
}

// Resistance statistics
export interface ResistanceStats {
  smashing: number;
  lethal: number;
  fire: number;
  cold: number;
  energy: number;
  negative: number;
  psionic: number;
  toxic: number;
}
