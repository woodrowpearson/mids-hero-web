/**
 * InherentPowersDisplay component tests
 * Epic 2.3 - Character Sheet Display
 */

import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { InherentPowersDisplay } from "../InherentPowersDisplay";
import type { Archetype, Power } from "@/types/character.types";

// Mock powers data
const mockPowers: Power[] = [
  {
    id: 1,
    name: "Brawl",
    displayName: "Brawl",
    description: "A basic melee attack available to all heroes.",
    powersetId: 100,
    levelAvailable: 1,
    effects: [],
    priority: 1,
  },
  {
    id: 2,
    name: "Sprint",
    displayName: "Sprint",
    description: "A short burst of speed to get around faster.",
    powersetId: 100,
    levelAvailable: 1,
    effects: [],
    priority: 2,
  },
  {
    id: 3,
    name: "Rest",
    displayName: "Rest",
    description: "Sit down and recover health and endurance.",
    powersetId: 100,
    levelAvailable: 1,
    effects: [],
    priority: 3,
  },
];

const mockPowerWithIcon: Power = {
  id: 4,
  name: "Critical",
  displayName: "Critical Strikes",
  description: "Scrappers have a chance to deal critical damage.",
  powersetId: 100,
  levelAvailable: 1,
  effects: [],
  iconUrl: "https://example.com/critical.png",
  priority: 0,
};

// Mock the useInherentPowers hook with different states
const mockUseInherentPowers = vi.fn();

vi.mock("@/hooks", () => ({
  useInherentPowers: (archetypeId: number | undefined) => mockUseInherentPowers(archetypeId),
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

// Mock archetype
const mockArchetype: Archetype = {
  id: 1,
  name: "Scrapper",
  displayName: "Scrapper",
};

describe("InherentPowersDisplay", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Default: return empty data
    mockUseInherentPowers.mockReturnValue({
      data: [],
      isLoading: false,
      error: null,
    });
  });

  describe("when no archetype is selected", () => {
    it("displays placeholder message", () => {
      render(<InherentPowersDisplay archetype={null} />, {
        wrapper: createWrapper(),
      });

      expect(
        screen.getByText("Select an archetype to view inherent powers.")
      ).toBeInTheDocument();
    });

    it("does not call useInherentPowers with undefined", () => {
      render(<InherentPowersDisplay archetype={null} />, {
        wrapper: createWrapper(),
      });

      expect(mockUseInherentPowers).toHaveBeenCalledWith(undefined);
    });
  });

  describe("loading state", () => {
    it("shows loading spinner while loading", () => {
      mockUseInherentPowers.mockReturnValue({
        data: undefined,
        isLoading: true,
        error: null,
      });

      render(<InherentPowersDisplay archetype={mockArchetype} />, {
        wrapper: createWrapper(),
      });

      expect(screen.getByRole("status")).toBeInTheDocument();
    });
  });

  describe("error state", () => {
    it("shows error message when error occurs", () => {
      mockUseInherentPowers.mockReturnValue({
        data: undefined,
        isLoading: false,
        error: new Error("Network error"),
      });

      render(<InherentPowersDisplay archetype={mockArchetype} />, {
        wrapper: createWrapper(),
      });

      // ErrorMessage component renders with title and message
      expect(screen.getByRole("heading", { name: "Error" })).toBeInTheDocument();
      expect(screen.getByText("Network error")).toBeInTheDocument();
    });

    it("shows generic error message for non-Error errors", () => {
      mockUseInherentPowers.mockReturnValue({
        data: undefined,
        isLoading: false,
        error: "Something went wrong",
      });

      render(<InherentPowersDisplay archetype={mockArchetype} />, {
        wrapper: createWrapper(),
      });

      // ErrorMessage component renders with title and message
      expect(screen.getByRole("heading", { name: "Error" })).toBeInTheDocument();
      expect(screen.getByText("Failed to load inherent powers")).toBeInTheDocument();
    });
  });

  describe("empty state", () => {
    it("shows message when no inherent powers exist", () => {
      mockUseInherentPowers.mockReturnValue({
        data: [],
        isLoading: false,
        error: null,
      });

      render(<InherentPowersDisplay archetype={mockArchetype} />, {
        wrapper: createWrapper(),
      });

      expect(
        screen.getByText("No inherent powers for this archetype.")
      ).toBeInTheDocument();
    });

    it("shows message when data is undefined", () => {
      mockUseInherentPowers.mockReturnValue({
        data: undefined,
        isLoading: false,
        error: null,
      });

      render(<InherentPowersDisplay archetype={mockArchetype} />, {
        wrapper: createWrapper(),
      });

      expect(
        screen.getByText("No inherent powers for this archetype.")
      ).toBeInTheDocument();
    });
  });

  describe("with inherent powers", () => {
    beforeEach(() => {
      mockUseInherentPowers.mockReturnValue({
        data: mockPowers,
        isLoading: false,
        error: null,
      });
    });

    it("displays all inherent powers", () => {
      render(<InherentPowersDisplay archetype={mockArchetype} />, {
        wrapper: createWrapper(),
      });

      expect(screen.getByText("Brawl")).toBeInTheDocument();
      expect(screen.getByText("Sprint")).toBeInTheDocument();
      expect(screen.getByText("Rest")).toBeInTheDocument();
    });

    it("displays power descriptions", () => {
      render(<InherentPowersDisplay archetype={mockArchetype} />, {
        wrapper: createWrapper(),
      });

      expect(
        screen.getByText("A basic melee attack available to all heroes.")
      ).toBeInTheDocument();
      expect(
        screen.getByText("A short burst of speed to get around faster.")
      ).toBeInTheDocument();
    });

    it("shows fallback icon when power has no iconUrl", () => {
      const { container } = render(
        <InherentPowersDisplay archetype={mockArchetype} />,
        { wrapper: createWrapper() }
      );

      // Should have SVG icons (fallback) - SVGs don't have role="img"
      const svgElements = container.querySelectorAll("svg");
      expect(svgElements.length).toBe(3); // One for each power without iconUrl
    });
  });

  describe("with power icons", () => {
    beforeEach(() => {
      mockUseInherentPowers.mockReturnValue({
        data: [mockPowerWithIcon],
        isLoading: false,
        error: null,
      });
    });

    it("displays power icon when iconUrl is provided", () => {
      render(<InherentPowersDisplay archetype={mockArchetype} />, {
        wrapper: createWrapper(),
      });

      const img = screen.getByAltText("Critical Strikes");
      expect(img).toBeInTheDocument();
      expect(img).toHaveAttribute("src", "https://example.com/critical.png");
    });
  });

  describe("hook integration", () => {
    it("passes archetype id to useInherentPowers", () => {
      mockUseInherentPowers.mockReturnValue({
        data: [],
        isLoading: false,
        error: null,
      });

      render(<InherentPowersDisplay archetype={mockArchetype} />, {
        wrapper: createWrapper(),
      });

      expect(mockUseInherentPowers).toHaveBeenCalledWith(1);
    });

    it("passes undefined when archetype has no id", () => {
      render(<InherentPowersDisplay archetype={null} />, {
        wrapper: createWrapper(),
      });

      expect(mockUseInherentPowers).toHaveBeenCalledWith(undefined);
    });
  });

  describe("styling", () => {
    beforeEach(() => {
      mockUseInherentPowers.mockReturnValue({
        data: mockPowers,
        isLoading: false,
        error: null,
      });
    });

    it("applies custom className", () => {
      const { container } = render(
        <InherentPowersDisplay
          archetype={mockArchetype}
          className="custom-inherent-class"
        />,
        { wrapper: createWrapper() }
      );

      expect(container.firstChild).toHaveClass("custom-inherent-class");
    });

    it("power cards have proper styling", () => {
      render(<InherentPowersDisplay archetype={mockArchetype} />, {
        wrapper: createWrapper(),
      });

      const brawlText = screen.getByText("Brawl");
      const card = brawlText.closest(".rounded-lg");
      expect(card).toHaveClass("border");
      expect(card).toHaveClass("bg-card");
    });
  });
});
