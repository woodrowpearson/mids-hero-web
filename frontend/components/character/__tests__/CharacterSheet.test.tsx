/**
 * CharacterSheet component tests
 * Epic 2.3 - Character Sheet Display
 */

import { describe, it, expect, beforeEach, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { CharacterSheet } from "../CharacterSheet";
import { useCharacterStore } from "@/stores/characterStore";
import type { Archetype } from "@/types/character.types";

// Mock the useInherentPowers hook
vi.mock("@/hooks", () => ({
  useInherentPowers: () => ({
    data: [],
    isLoading: false,
    error: null,
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

// Mock archetype with full data
const mockArchetype: Archetype = {
  id: 1,
  name: "Scrapper",
  displayName: "Scrapper",
  damageScale: 1.125,
  baseHp: 1338.6,
  baseRegen: 0.02,
  baseRecovery: 0.0167,
  baseThreat: 1.0,
  damageCap: 5.0,
  resistanceCap: 0.75,
  defenseCap: 2.25,
  hpCap: 3213,
  regenerationCap: 30.0,
  recoveryCap: 8.0,
  rechargeCap: 5.0,
};

describe("CharacterSheet", () => {
  beforeEach(() => {
    // Reset store state before each test
    useCharacterStore.setState({
      name: "Test Hero",
      level: 50,
      archetype: mockArchetype,
      origin: null,
      primaryPowerset: null,
      secondaryPowerset: null,
    });
  });

  describe("header", () => {
    it("renders the card header", () => {
      render(<CharacterSheet />, { wrapper: createWrapper() });

      expect(screen.getByText("Character Sheet")).toBeInTheDocument();
      expect(
        screen.getByText(/View your character information/)
      ).toBeInTheDocument();
    });
  });

  describe("character summary", () => {
    it("renders CharacterSummary component", () => {
      render(<CharacterSheet />, { wrapper: createWrapper() });

      expect(screen.getByText(/Test Hero/)).toBeInTheDocument();
      // Use more specific match to avoid hitting "Base HP (Level 50)" text
      expect(screen.getByText(/Test Hero.*Level 50/)).toBeInTheDocument();
    });

    it("passes mode prop to CharacterSummary", () => {
      render(<CharacterSheet mode="edit" />, { wrapper: createWrapper() });

      // In edit mode, form fields should be visible
      expect(screen.getByLabelText("Character Name")).toBeInTheDocument();
    });
  });

  describe("tabs", () => {
    it("renders three tab triggers", () => {
      render(<CharacterSheet />, { wrapper: createWrapper() });

      expect(screen.getByRole("tab", { name: "Base Modifiers" })).toBeInTheDocument();
      expect(screen.getByRole("tab", { name: "Caps" })).toBeInTheDocument();
      expect(screen.getByRole("tab", { name: "Inherent Powers" })).toBeInTheDocument();
    });

    it("shows Base Modifiers tab content by default", () => {
      render(<CharacterSheet />, { wrapper: createWrapper() });

      // Base Modifiers content should be visible
      expect(screen.getByText("Base HP (Level 50)")).toBeInTheDocument();
      expect(screen.getByText("Base Regeneration")).toBeInTheDocument();
    });

    it("switches to Caps tab on click", async () => {
      const user = userEvent.setup();
      render(<CharacterSheet />, { wrapper: createWrapper() });

      const capsTab = screen.getByRole("tab", { name: "Caps" });
      await user.click(capsTab);

      expect(screen.getByText("HP Cap")).toBeInTheDocument();
      expect(screen.getByText("Damage Cap")).toBeInTheDocument();
    });

    it("switches to Inherent Powers tab on click", async () => {
      const user = userEvent.setup();
      render(<CharacterSheet />, { wrapper: createWrapper() });

      const inherentsTab = screen.getByRole("tab", { name: "Inherent Powers" });
      await user.click(inherentsTab);

      // Since we mocked useInherentPowers to return empty array
      expect(
        screen.getByText("No inherent powers for this archetype.")
      ).toBeInTheDocument();
    });
  });

  describe("when no archetype is selected", () => {
    beforeEach(() => {
      useCharacterStore.setState({
        archetype: null,
      });
    });

    it("shows placeholder in Base Modifiers tab", () => {
      render(<CharacterSheet />, { wrapper: createWrapper() });

      expect(
        screen.getByText("Select an archetype to view base modifiers.")
      ).toBeInTheDocument();
    });

    it("shows placeholder in Caps tab", async () => {
      const user = userEvent.setup();
      render(<CharacterSheet />, { wrapper: createWrapper() });

      const capsTab = screen.getByRole("tab", { name: "Caps" });
      await user.click(capsTab);

      expect(
        screen.getByText("Select an archetype to view caps.")
      ).toBeInTheDocument();
    });

    it("shows placeholder in Inherent Powers tab", async () => {
      const user = userEvent.setup();
      render(<CharacterSheet />, { wrapper: createWrapper() });

      const inherentsTab = screen.getByRole("tab", { name: "Inherent Powers" });
      await user.click(inherentsTab);

      expect(
        screen.getByText("Select an archetype to view inherent powers.")
      ).toBeInTheDocument();
    });
  });

  describe("styling", () => {
    it("applies custom className", () => {
      const { container } = render(
        <CharacterSheet className="custom-sheet-class" />,
        { wrapper: createWrapper() }
      );

      expect(container.firstChild).toHaveClass("custom-sheet-class");
    });

    it("has card styling", () => {
      const { container } = render(<CharacterSheet />, {
        wrapper: createWrapper(),
      });

      expect(container.firstChild).toHaveClass("rounded-lg");
      expect(container.firstChild).toHaveClass("border");
      expect(container.firstChild).toHaveClass("bg-card");
      expect(container.firstChild).toHaveClass("shadow-sm");
    });
  });

  describe("mode prop", () => {
    it("defaults to view mode", () => {
      render(<CharacterSheet />, { wrapper: createWrapper() });

      // In view mode, no form fields should be visible
      expect(screen.queryByLabelText("Character Name")).not.toBeInTheDocument();
    });

    it("accepts edit mode", () => {
      render(<CharacterSheet mode="edit" />, { wrapper: createWrapper() });

      expect(screen.getByLabelText("Character Name")).toBeInTheDocument();
    });
  });
});
