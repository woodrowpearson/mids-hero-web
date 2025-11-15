/**
 * Character-related TypeScript type definitions
 * Based on City of Heroes game data and MidsReborn architecture
 */

// Archetype (AT) definition
export interface Archetype {
  id: number;
  name: string;
  displayName: string;
  damageScale: number; // Damage multiplier for this AT
  defenseCap: number; // Max defense (typically 45% or 50%)
  resistanceCap: number; // Max resistance (typically 75% or 90%)
  damageCap: number; // Max damage bonus (typically 400% or 500%)
  baseHP: number; // Base HP at level 50
  baseRegen: number; // Base regeneration rate
  baseRecovery: number; // Base endurance recovery
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
  powersetId: number;
  levelAvailable: number;
  prerequisitePowerIds?: number[]; // Powers that must be taken first
  effects: Effect[];
  iconUrl?: string;
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
