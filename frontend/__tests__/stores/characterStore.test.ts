/**
 * Character store tests
 */

import { describe, it, expect, beforeEach } from "vitest";
import { renderHook, act } from "@testing-library/react";
import { useCharacterStore } from "@/stores/characterStore";
import type { Archetype, Power, Enhancement } from "@/types/character.types";

// Mock data
const mockArchetype: Archetype = {
  id: 1,
  name: "Blaster",
  displayName: "Blaster",
  damageScale: 1.0,
  defenseCap: 45,
  resistanceCap: 75,
  damageCap: 500,
  baseHP: 1000,
  baseRegen: 1.0,
  baseRecovery: 1.0,
};

const mockPower: Power = {
  id: 1,
  name: "Fire Blast",
  displayName: "Fire Blast",
  powersetId: 1,
  levelAvailable: 1,
  effects: [],
};

const mockEnhancement: Enhancement = {
  id: 1,
  name: "Damage",
  displayName: "Damage IO",
  type: "IO",
  bonuses: [{ attribute: "Damage", value: 42.4 }],
};

describe("characterStore", () => {
  beforeEach(() => {
    // Clear build before each test
    const { result } = renderHook(() => useCharacterStore());
    act(() => {
      result.current.clearBuild();
    });
  });

  describe("Character properties", () => {
    it("sets character name", () => {
      const { result } = renderHook(() => useCharacterStore());

      act(() => {
        result.current.setName("Test Hero");
      });

      expect(result.current.name).toBe("Test Hero");
    });

    it("sets archetype", () => {
      const { result } = renderHook(() => useCharacterStore());

      act(() => {
        result.current.setArchetype(mockArchetype);
      });

      expect(result.current.archetype).toEqual(mockArchetype);
    });

    it("sets level between 1 and 50", () => {
      const { result } = renderHook(() => useCharacterStore());

      act(() => {
        result.current.setLevel(25);
      });
      expect(result.current.level).toBe(25);

      // Test bounds
      act(() => {
        result.current.setLevel(0);
      });
      expect(result.current.level).toBe(1);

      act(() => {
        result.current.setLevel(100);
      });
      expect(result.current.level).toBe(50);
    });
  });

  describe("Power management", () => {
    it("adds power to build", () => {
      const { result } = renderHook(() => useCharacterStore());

      act(() => {
        result.current.addPower(mockPower, 1);
      });

      expect(result.current.powers).toHaveLength(1);
      expect(result.current.powers[0].power).toEqual(mockPower);
      expect(result.current.powers[0].level).toBe(1);
    });

    it("removes power from build", () => {
      const { result } = renderHook(() => useCharacterStore());

      act(() => {
        result.current.addPower(mockPower, 1);
        result.current.removePower(0);
      });

      expect(result.current.powers).toHaveLength(0);
    });

    it("updates power level", () => {
      const { result } = renderHook(() => useCharacterStore());

      act(() => {
        result.current.addPower(mockPower, 1);
        result.current.updatePowerLevel(0, 5);
      });

      expect(result.current.powers[0].level).toBe(5);
    });
  });

  describe("Slotting", () => {
    beforeEach(() => {
      const { result } = renderHook(() => useCharacterStore());
      act(() => {
        result.current.addPower(mockPower, 1);
      });
    });

    it("adds slot to power", () => {
      const { result } = renderHook(() => useCharacterStore());

      act(() => {
        result.current.addSlot(0);
      });

      expect(result.current.powers[0].slots).toHaveLength(1);
    });

    it("limits slots to 6 per power", () => {
      const { result } = renderHook(() => useCharacterStore());

      act(() => {
        // Try to add 7 slots
        for (let i = 0; i < 7; i++) {
          result.current.addSlot(0);
        }
      });

      expect(result.current.powers[0].slots).toHaveLength(6);
    });

    it("slots enhancement", () => {
      const { result } = renderHook(() => useCharacterStore());

      act(() => {
        result.current.addSlot(0);
        result.current.slotEnhancement(0, 0, mockEnhancement, 50);
      });

      expect(result.current.powers[0].slots[0].enhancement).toEqual(mockEnhancement);
      expect(result.current.powers[0].slots[0].level).toBe(50);
    });

    it("removes enhancement from slot", () => {
      const { result } = renderHook(() => useCharacterStore());

      act(() => {
        result.current.addSlot(0);
        result.current.slotEnhancement(0, 0, mockEnhancement, 50);
        result.current.removeEnhancement(0, 0);
      });

      expect(result.current.powers[0].slots[0].enhancement).toBeNull();
    });
  });

  describe("Build management", () => {
    it("exports build data", () => {
      const { result } = renderHook(() => useCharacterStore());

      act(() => {
        result.current.setName("Test Hero");
        result.current.setArchetype(mockArchetype);
        result.current.addPower(mockPower, 1);
      });

      const buildData = result.current.exportBuild();

      expect(buildData.character.name).toBe("Test Hero");
      expect(buildData.character.archetype).toEqual(mockArchetype);
      expect(buildData.powers).toHaveLength(1);
    });

    it("loads build data", () => {
      const { result } = renderHook(() => useCharacterStore());

      const buildData = {
        character: {
          name: "Loaded Hero",
          archetype: mockArchetype,
          origin: null,
          alignment: null,
          level: 10,
        },
        powersets: {
          primary: null,
          secondary: null,
          pools: [null, null, null, null] as [null, null, null, null],
          ancillary: null,
        },
        powers: [],
      };

      act(() => {
        result.current.loadBuild(buildData);
      });

      expect(result.current.name).toBe("Loaded Hero");
      expect(result.current.archetype).toEqual(mockArchetype);
      expect(result.current.level).toBe(10);
    });

    it("clears build", () => {
      const { result } = renderHook(() => useCharacterStore());

      act(() => {
        result.current.setName("Test Hero");
        result.current.setArchetype(mockArchetype);
        result.current.addPower(mockPower, 1);
        result.current.clearBuild();
      });

      expect(result.current.name).toBe("");
      expect(result.current.archetype).toBeNull();
      expect(result.current.powers).toHaveLength(0);
    });
  });

  // TODO: Add undo/redo tests when temporal middleware is implemented
  // describe("Undo/Redo", () => {
  //   it("supports undo for archetype change", () => {
  //     const { result } = renderHook(() => useCharacterStore());

  //     act(() => {
  //       result.current.setArchetype(mockArchetype);
  //     });

  //     expect(result.current.archetype).toEqual(mockArchetype);

  //     act(() => {
  //       undo();
  //     });

  //     expect(result.current.archetype).toBeNull();
  //   });

  //   it("supports redo for archetype change", () => {
  //     const { result } = renderHook(() => useCharacterStore());

  //     act(() => {
  //       result.current.setArchetype(mockArchetype);
  //     });

  //     act(() => {
  //       undo();
  //       redo();
  //     });

  //     expect(result.current.archetype).toEqual(mockArchetype);
  //   });
  // });
});
