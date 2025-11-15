/**
 * Auto-calculate hook
 * Triggers calculation API calls when build changes (with debouncing)
 */

import { useEffect } from "react";
import { useDebouncedCallback } from "use-debounce";
import { useCharacterStore } from "@/stores/characterStore";
import { calculationApi } from "@/services";

export function useAutoCalculate() {
  const exportBuild = useCharacterStore((state) => state.exportBuild);
  const setTotals = useCharacterStore((state) => state.setTotals);
  const setIsCalculating = useCharacterStore((state) => state.setIsCalculating);

  // Debounced calculation function (200ms delay)
  const debouncedCalculate = useDebouncedCallback(async () => {
    const buildData = exportBuild();

    // Only calculate if build has meaningful data
    if (!buildData.character.archetype || buildData.powers.length === 0) {
      setTotals({
        defense: {
          smashing: 0,
          lethal: 0,
          fire: 0,
          cold: 0,
          energy: 0,
          negative: 0,
          psionic: 0,
          toxic: 0,
          melee: 0,
          ranged: 0,
          aoe: 0,
        },
        resistance: {
          smashing: 0,
          lethal: 0,
          fire: 0,
          cold: 0,
          energy: 0,
          negative: 0,
          psionic: 0,
          toxic: 0,
        },
        maxHP: 0,
        maxEndurance: 0,
        regeneration: 0,
        recovery: 0,
        globalRecharge: 0,
        globalDamage: 0,
        globalAccuracy: 0,
        globalToHit: 0,
      });
      return;
    }

    setIsCalculating(true);
    try {
      const totals = await calculationApi.calculateTotals({ buildData });
      setTotals(totals);
    } catch (error) {
      console.error("Calculation failed:", error);
      // Keep previous totals on error
    } finally {
      setIsCalculating(false);
    }
  }, 200); // 200ms debounce

  // Subscribe to store changes
  useEffect(() => {
    const unsubscribe = useCharacterStore.subscribe(
      (state) => [state.powers, state.archetype, state.primaryPowerset, state.secondaryPowerset],
      () => {
        debouncedCalculate();
      }
    );

    return () => {
      unsubscribe();
      debouncedCalculate.cancel(); // Cancel pending debounced calls
    };
  }, [debouncedCalculate]);
}
