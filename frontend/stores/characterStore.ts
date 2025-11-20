/**
 * Zustand character store
 * Manages character build state (local, editable)
 *
 * TODO: Add undo/redo functionality in future epic (requires zustand/middleware/temporal package)
 */

import { create } from "zustand";
import { devtools, persist, subscribeWithSelector } from "zustand/middleware";
import type {
  Archetype,
  Origin,
  Alignment,
  Powerset,
  Power,
  PowerEntry,
  Enhancement,
  BuildData,
  CalculatedTotals,
} from "@/types/character.types";

// Store state interface
export interface CharacterState {
  // Character data
  name: string;
  archetype: Archetype | null;
  origin: Origin | null;
  alignment: Alignment | null;
  level: number;

  // Powersets
  primaryPowerset: Powerset | null;
  secondaryPowerset: Powerset | null;
  poolPowersets: [Powerset | null, Powerset | null, Powerset | null, Powerset | null];
  ancillaryPowerset: Powerset | null;

  // Build data
  powers: PowerEntry[];

  // Calculated totals (from backend)
  totals: CalculatedTotals | undefined;
  isCalculating: boolean;

  // Actions - Character
  setName: (name: string) => void;
  setArchetype: (archetype: Archetype | null) => void;
  setOrigin: (origin: Origin | null) => void;
  setAlignment: (alignment: Alignment | null) => void;
  setLevel: (level: number) => void;

  // Actions - Powersets
  setPrimaryPowerset: (powerset: Powerset | null) => void;
  setSecondaryPowerset: (powerset: Powerset | null) => void;
  setPoolPowerset: (index: number, powerset: Powerset | null) => void;
  setAncillaryPowerset: (powerset: Powerset | null) => void;

  // Actions - Powers
  addPower: (power: Power, level: number) => void;
  removePower: (index: number) => void;
  updatePowerLevel: (index: number, level: number) => void;

  // Actions - Slotting
  addSlot: (powerIndex: number) => void;
  removeSlot: (powerIndex: number, slotIndex: number) => void;
  slotEnhancement: (
    powerIndex: number,
    slotIndex: number,
    enhancement: Enhancement,
    level: number
  ) => void;
  removeEnhancement: (powerIndex: number, slotIndex: number) => void;

  // Actions - Calculations
  setTotals: (totals: CalculatedTotals) => void;
  setIsCalculating: (isCalculating: boolean) => void;

  // Actions - Build management
  loadBuild: (build: BuildData) => void;
  clearBuild: () => void;
  exportBuild: () => BuildData;
}

// Initial state
const initialState = {
  name: "",
  archetype: null,
  origin: null,
  alignment: null,
  level: 1,
  primaryPowerset: null,
  secondaryPowerset: null,
  poolPowersets: [null, null, null, null] as [
    Powerset | null,
    Powerset | null,
    Powerset | null,
    Powerset | null
  ],
  ancillaryPowerset: null,
  powers: [],
  totals: undefined,
  isCalculating: false,
};

// Create store with middleware
export const useCharacterStore = create<CharacterState>()(
  subscribeWithSelector(
    devtools(
      persist(
        (set, get) => ({
          ...initialState,

          // Character actions
          setName: (name) => set({ name }),
          setArchetype: (archetype) => set({ archetype }),
          setOrigin: (origin) => set({ origin }),
          setAlignment: (alignment) => set({ alignment }),
          setLevel: (level) => set({ level: Math.max(1, Math.min(50, level)) }),

          // Powerset actions
          setPrimaryPowerset: (powerset) => set({ primaryPowerset: powerset }),
          setSecondaryPowerset: (powerset) => set({ secondaryPowerset: powerset }),
          setPoolPowerset: (index, powerset) => {
            const poolPowersets = [...get().poolPowersets] as [
              Powerset | null,
              Powerset | null,
              Powerset | null,
              Powerset | null
            ];
            poolPowersets[index] = powerset;
            set({ poolPowersets });
          },
          setAncillaryPowerset: (powerset) => set({ ancillaryPowerset: powerset }),

          // Power actions
          addPower: (power, level) => {
            const powers = [...get().powers];
            powers.push({
              power,
              level,
              slots: [], // Start with no slots
            });
            set({ powers });
          },
          removePower: (index) => {
            const powers = [...get().powers];
            powers.splice(index, 1);
            set({ powers });
          },
          updatePowerLevel: (index, level) => {
            const powers = [...get().powers];
            const power = powers[index];
            if (!power) return;
            powers[index] = { ...power, level };
            set({ powers });
          },

          // Slotting actions
          addSlot: (powerIndex) => {
            const powers = [...get().powers];
            const power = powers[powerIndex];
            if (!power) return;
            if (power.slots.length < 6) {
              // Max 6 slots
              power.slots.push({
                enhancement: null,
                level: get().level,
              });
              set({ powers });
            }
          },
          removeSlot: (powerIndex, slotIndex) => {
            const powers = [...get().powers];
            const power = powers[powerIndex];
            if (!power) return;
            power.slots.splice(slotIndex, 1);
            set({ powers });
          },
          slotEnhancement: (powerIndex, slotIndex, enhancement, level) => {
            const powers = [...get().powers];
            const power = powers[powerIndex];
            if (!power) return;
            power.slots[slotIndex] = {
              enhancement,
              level,
            };
            set({ powers });
          },
          removeEnhancement: (powerIndex, slotIndex) => {
            const powers = [...get().powers];
            const power = powers[powerIndex];
            if (!power) return;
            const slot = power.slots[slotIndex];
            if (!slot) return;
            power.slots[slotIndex] = {
              ...slot,
              enhancement: null,
            };
            set({ powers });
          },

          // Calculation actions
          setTotals: (totals) => set({ totals }),
          setIsCalculating: (isCalculating) => set({ isCalculating }),

          // Build management
          loadBuild: (build) => {
            const { character, powersets, powers, totals } = build;
            set({
              name: character.name,
              archetype: character.archetype,
              origin: character.origin,
              alignment: character.alignment,
              level: character.level,
              primaryPowerset: powersets.primary,
              secondaryPowerset: powersets.secondary,
              poolPowersets: powersets.pools,
              ancillaryPowerset: powersets.ancillary,
              powers,
              totals,
            });
          },
          clearBuild: () => set(initialState),
          exportBuild: () => {
            const state = get();
            return {
              character: {
                name: state.name,
                archetype: state.archetype,
                origin: state.origin,
                alignment: state.alignment,
                level: state.level,
              },
              powersets: {
                primary: state.primaryPowerset,
                secondary: state.secondaryPowerset,
                pools: state.poolPowersets,
                ancillary: state.ancillaryPowerset,
              },
              powers: state.powers,
              totals: state.totals,
            };
          },
        }),
      {
        name: "character-build-storage",
        partialize: (state) => ({
          // Only persist essential fields (exclude calculated totals)
          name: state.name,
          archetype: state.archetype,
          origin: state.origin,
          alignment: state.alignment,
          level: state.level,
          primaryPowerset: state.primaryPowerset,
          secondaryPowerset: state.secondaryPowerset,
          poolPowersets: state.poolPowersets,
          ancillaryPowerset: state.ancillaryPowerset,
          powers: state.powers,
        }),
      }
    )
  )
  )
);

// TODO: Implement undo/redo in future epic
// export const undo = () => { /* to be implemented */ };
// export const redo = () => { /* to be implemented */ };
