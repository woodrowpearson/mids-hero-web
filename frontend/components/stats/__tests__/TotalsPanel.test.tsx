/**
 * TotalsPanel component tests
 */

import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { TotalsPanel } from "../TotalsPanel";
import { useCharacterStore } from "@/stores/characterStore";
import type {
  Archetype,
  CalculatedTotals,
  DefenseStats,
  ResistanceStats,
} from "@/types/character.types";

// Mock the useCalculateTotals hook
vi.mock("@/hooks/useCalculations", () => ({
  useCalculateTotals: () => ({
    mutate: vi.fn(),
    isError: false,
    error: null,
    isPending: false,
  }),
}));

// Create a wrapper with QueryClient
const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });
  const Wrapper = ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
  Wrapper.displayName = "QueryClientWrapper";
  return Wrapper;
};

describe("TotalsPanel", () => {
  const mockArchetype: Archetype = {
    id: 1,
    name: "Scrapper",
    displayName: "Scrapper",
    damageScale: 1.125,
    defenseCap: 45,
    resistanceCap: 75,
    damageCap: 500,
    baseHP: 1338.6,
    baseRegen: 100,
    baseRecovery: 100,
  };

  const mockDefense: DefenseStats = {
    smashing: 45,
    lethal: 45,
    fire: 30.5,
    cold: 30.5,
    energy: 25.2,
    negative: 18,
    toxic: 0,
    psionic: 0,
    melee: 45,
    ranged: 30.5,
    aoe: 25.2,
  };

  const mockResistance: ResistanceStats = {
    smashing: 60,
    lethal: 60,
    fire: 40,
    cold: 40,
    energy: 30,
    negative: 20,
    toxic: 0,
    psionic: 0,
  };

  const mockTotals: CalculatedTotals = {
    defense: mockDefense,
    resistance: mockResistance,
    maxHP: 1338.6,
    maxEndurance: 100,
    regeneration: 2.5,
    recovery: 1.67,
    globalRecharge: 0,
    globalDamage: 0,
    globalAccuracy: 0,
    globalToHit: 0,
  };

  beforeEach(() => {
    // Reset store before each test
    useCharacterStore.setState({
      archetype: null,
      totals: undefined,
      isCalculating: false,
    });
  });

  it("shows message when no archetype selected", () => {
    render(<TotalsPanel />, { wrapper: createWrapper() });

    expect(
      screen.getByText("Select an archetype to view build totals")
    ).toBeInTheDocument();
  });

  it("shows loading state while calculating", () => {
    useCharacterStore.setState({
      archetype: mockArchetype,
      totals: undefined,
      isCalculating: true,
    });

    render(<TotalsPanel />, { wrapper: createWrapper() });

    expect(screen.getByText("Calculating totals...")).toBeInTheDocument();
    expect(screen.getByRole("status")).toBeInTheDocument(); // LoadingSpinner
  });

  it("renders defense and resistance panels when data loaded", () => {
    useCharacterStore.setState({
      archetype: mockArchetype,
      totals: mockTotals,
      isCalculating: false,
    });

    render(<TotalsPanel />, { wrapper: createWrapper() });

    expect(screen.getByText("Defense")).toBeInTheDocument();
    expect(screen.getByText("Resistance")).toBeInTheDocument();
  });

  it("displays all defense types", () => {
    useCharacterStore.setState({
      archetype: mockArchetype,
      totals: mockTotals,
      isCalculating: false,
    });

    render(<TotalsPanel />, { wrapper: createWrapper() });

    // Typed defense (appears in both Defense and Resistance panels)
    expect(screen.getAllByText("Smashing")).toHaveLength(2); // Defense + Resistance
    expect(screen.getAllByText("Lethal")).toHaveLength(2);
    expect(screen.getAllByText("Fire")).toHaveLength(2);

    // Positional defense (only in Defense panel)
    expect(screen.getByText("Melee")).toBeInTheDocument();
    expect(screen.getByText("Ranged")).toBeInTheDocument();
    expect(screen.getByText("AoE")).toBeInTheDocument();
  });

  it("displays all resistance types", () => {
    useCharacterStore.setState({
      archetype: mockArchetype,
      totals: mockTotals,
      isCalculating: false,
    });

    render(<TotalsPanel />, { wrapper: createWrapper() });

    expect(screen.getAllByText("Smashing")).toHaveLength(2); // Defense + Resistance
    expect(screen.getAllByText("Lethal")).toHaveLength(2);
    expect(screen.getAllByText("Fire")).toHaveLength(2);
  });

  it("uses archetype defense cap for defense panel", () => {
    useCharacterStore.setState({
      archetype: mockArchetype,
      totals: mockTotals,
      isCalculating: false,
    });

    render(<TotalsPanel />, { wrapper: createWrapper() });

    // Scrapper has 45% defense cap
    // Smashing defense is 45%, so it should be at 100% width
    const bars = screen.getAllByRole("presentation");
    const smashingBar = bars[0]; // First bar is defense Smashing
    expect(smashingBar).toHaveStyle({ width: "100%" });
  });

  it("uses archetype resistance cap for resistance panel", () => {
    useCharacterStore.setState({
      archetype: mockArchetype,
      totals: mockTotals,
      isCalculating: false,
    });

    render(<TotalsPanel />, { wrapper: createWrapper() });

    // Scrapper has 75% resistance cap
    // Smashing resistance is 60%, so it should be at 80% width (60/75)
    const bars = screen.getAllByRole("presentation");
    const smashingResistanceBar = bars[11]; // After 11 defense bars, first resistance bar
    expect(smashingResistanceBar).toHaveStyle({ width: "80%" });
  });

  it("handles Tanker with higher defense cap", () => {
    const tankerArchetype: Archetype = {
      ...mockArchetype,
      name: "Tanker",
      defenseCap: 50, // Tankers have 50% defense cap
      resistanceCap: 90, // Tankers have 90% resistance cap
    };

    useCharacterStore.setState({
      archetype: tankerArchetype,
      totals: mockTotals,
      isCalculating: false,
    });

    render(<TotalsPanel />, { wrapper: createWrapper() });

    // Smashing defense is 45%, cap is 50%, so bar should be 90% width
    const bars = screen.getAllByRole("presentation");
    const smashingBar = bars[0];
    expect(smashingBar).toHaveStyle({ width: "90%" }); // 45/50
  });

  it("renders in compact variant", () => {
    useCharacterStore.setState({
      archetype: mockArchetype,
      totals: mockTotals,
      isCalculating: false,
    });

    render(<TotalsPanel variant="compact" />, { wrapper: createWrapper() });

    const defenseHeader = screen.getByText("Defense");
    expect(defenseHeader).toHaveClass("text-base");
  });

  it("applies responsive grid layout", () => {
    useCharacterStore.setState({
      archetype: mockArchetype,
      totals: mockTotals,
      isCalculating: false,
    });

    const { container } = render(<TotalsPanel />, { wrapper: createWrapper() });

    const gridContainer = container.querySelector(".grid");
    expect(gridContainer).toHaveClass("grid-cols-1");
    expect(gridContainer).toHaveClass("lg:grid-cols-2");
  });

  it("applies custom className", () => {
    useCharacterStore.setState({
      archetype: mockArchetype,
      totals: mockTotals,
      isCalculating: false,
    });

    const { container } = render(<TotalsPanel className="custom-class" />, {
      wrapper: createWrapper(),
    });

    expect(container.firstChild).toHaveClass("custom-class");
  });

  it("renders both panels side-by-side on desktop", () => {
    useCharacterStore.setState({
      archetype: mockArchetype,
      totals: mockTotals,
      isCalculating: false,
    });

    render(<TotalsPanel />, { wrapper: createWrapper() });

    // Both Defense and Resistance should be rendered
    expect(screen.getByText("Defense")).toBeInTheDocument();
    expect(screen.getByText("Resistance")).toBeInTheDocument();
  });

  it("handles missing totals gracefully", () => {
    useCharacterStore.setState({
      archetype: null, // No archetype prevents auto-calculation
      totals: undefined,
      isCalculating: false,
    });

    render(<TotalsPanel />, { wrapper: createWrapper() });

    // Should show message when no archetype
    expect(
      screen.getByText("Select an archetype to view build totals")
    ).toBeInTheDocument();
  });

  it("uses default caps when archetype caps are undefined", () => {
    const archetypeNoCaps: Archetype = {
      ...mockArchetype,
      defenseCap: undefined as unknown as number,
      resistanceCap: undefined as unknown as number,
    };

    useCharacterStore.setState({
      archetype: archetypeNoCaps,
      totals: mockTotals,
      isCalculating: false,
    });

    render(<TotalsPanel />, { wrapper: createWrapper() });

    // Should use default 45% defense cap and 75% resistance cap
    const bars = screen.getAllByRole("presentation");
    const smashingDefenseBar = bars[0];
    expect(smashingDefenseBar).toHaveStyle({ width: "100%" }); // 45/45
  });
});
