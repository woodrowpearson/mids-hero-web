/**
 * Tests for usePowersets hooks
 */

import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { usePowersets, usePowersetsByArchetype } from "@/hooks/usePowersets";
import { powerApi } from "@/services";
import type { Powerset } from "@/types/character.types";

// Mock the powerApi
vi.mock("@/services", () => ({
  powerApi: {
    getPowersets: vi.fn(),
  },
}));

const mockPowersets: Powerset[] = [
  {
    id: 1,
    name: "Fiery Melee",
    displayName: "Fiery Melee",
    archetypeId: 1,
    type: "Primary",
    description: "Fire powers for tankers",
  },
  {
    id: 2,
    name: "Invulnerability",
    displayName: "Invulnerability",
    archetypeId: 1,
    type: "Secondary",
    description: "Defensive powers",
  },
];

describe("usePowersets", () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false, // Disable retries for tests
        },
      },
    });
    vi.clearAllMocks();
  });

  const wrapper = ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );

  it("fetches powersets successfully", async () => {
    vi.mocked(powerApi.getPowersets).mockResolvedValue(mockPowersets);

    const { result } = renderHook(() => usePowersets(), { wrapper });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data).toEqual(mockPowersets);
    expect(powerApi.getPowersets).toHaveBeenCalledWith(undefined);
  });

  it("handles errors gracefully", async () => {
    const errorMessage = "Network error";
    vi.mocked(powerApi.getPowersets).mockRejectedValue(new Error(errorMessage));

    const { result } = renderHook(() => usePowersets(), { wrapper });

    await waitFor(() => expect(result.current.isError).toBe(true));

    expect(result.current.error).toBeTruthy();
  });
});

describe("usePowersetsByArchetype", () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
        },
      },
    });
    vi.clearAllMocks();
  });

  const wrapper = ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );

  it("does not fetch when archetype ID is not provided", () => {
    const { result } = renderHook(() => usePowersetsByArchetype(), { wrapper });

    expect(result.current.isLoading).toBe(false);
    expect(powerApi.getPowersets).not.toHaveBeenCalled();
  });

  it("fetches powersets when archetype ID is provided", async () => {
    vi.mocked(powerApi.getPowersets).mockResolvedValue(mockPowersets);

    const { result } = renderHook(() => usePowersetsByArchetype(1), { wrapper });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data).toEqual(mockPowersets);
    expect(powerApi.getPowersets).toHaveBeenCalledWith({ archetypeId: 1 });
  });
});
