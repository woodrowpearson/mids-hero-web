/**
 * Tests for useCalculations hooks
 */

import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useCalculateTotals } from "@/hooks/useCalculations";
import { calculationApi } from "@/services";
import type { CalculatedTotals } from "@/types/character.types";

// Mock the calculationApi
vi.mock("@/services", () => ({
  calculationApi: {
    calculateTotals: vi.fn(),
  },
}));

const mockCalculatedTotals: CalculatedTotals = {
  defense: {
    smashing: 25.5,
    lethal: 25.5,
    fire: 10.0,
    cold: 10.0,
    energy: 15.0,
    negative: 10.0,
    psionic: 5.0,
    toxic: 0.0,
    melee: 30.0,
    ranged: 15.0,
    aoe: 10.0,
  },
  resistance: {
    smashing: 45.0,
    lethal: 45.0,
    fire: 20.0,
    cold: 20.0,
    energy: 25.0,
    negative: 15.0,
    psionic: 10.0,
    toxic: 0.0,
  },
  maxHP: 2500,
  maxEndurance: 100,
  regeneration: 15.5,
  recovery: 2.5,
  globalRecharge: 75.0,
  globalDamage: 50.0,
  globalAccuracy: 10.0,
  globalToHit: 5.0,
};

describe("useCalculateTotals", () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        mutations: {
          retry: false, // Disable retries for tests
        },
      },
    });
    vi.clearAllMocks();
  });

  const wrapper = ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );

  it("calculates totals successfully", async () => {
    vi.mocked(calculationApi.calculateTotals).mockResolvedValue(mockCalculatedTotals);

    const { result } = renderHook(() => useCalculateTotals(), { wrapper });

    const mockBuildData = {
      character: {
        name: "Test Hero",
        archetype: null,
        origin: null,
        alignment: null,
        level: 50,
      },
      powersets: {
        primary: null,
        secondary: null,
        pools: [null, null, null, null],
        ancillary: null,
      },
      powers: [],
    };

    result.current.mutate({ buildData: mockBuildData });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data).toEqual(mockCalculatedTotals);
    expect(calculationApi.calculateTotals).toHaveBeenCalledWith({ buildData: mockBuildData });
  });

  it("handles calculation errors", async () => {
    const errorMessage = "Calculation failed";
    vi.mocked(calculationApi.calculateTotals).mockRejectedValue(new Error(errorMessage));

    const { result } = renderHook(() => useCalculateTotals(), { wrapper });

    result.current.mutate({
      buildData: {
        character: {
          name: "Test Hero",
          archetype: null,
          origin: null,
          alignment: null,
          level: 50,
        },
        powersets: {
          primary: null,
          secondary: null,
          pools: [null, null, null, null],
          ancillary: null,
        },
        powers: [],
      },
    });

    await waitFor(() => expect(result.current.isError).toBe(true));

    expect(result.current.error).toBeTruthy();
  });
});
