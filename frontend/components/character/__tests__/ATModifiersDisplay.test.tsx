/**
 * ATModifiersDisplay component tests
 * Epic 2.3 - Character Sheet Display
 */

import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { ATModifiersDisplay } from "../ATModifiersDisplay";
import type { Archetype } from "@/types/character.types";

// Mock archetype with full caps and modifiers
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

// Archetype with partial modifiers
const partialArchetype: Archetype = {
  id: 2,
  name: "Blaster",
  displayName: "Blaster",
  baseHp: 1017,
  baseRegen: 0.02,
  // baseRecovery is undefined
  // baseThreat is undefined
};

describe("ATModifiersDisplay", () => {
  describe("when no archetype is selected", () => {
    it("displays placeholder message", () => {
      render(<ATModifiersDisplay archetype={null} />);

      expect(
        screen.getByText("Select an archetype to view base modifiers.")
      ).toBeInTheDocument();
    });
  });

  describe("when archetype is selected", () => {
    it("renders the modifiers table", () => {
      render(<ATModifiersDisplay archetype={mockArchetype} />);

      expect(screen.getByText("Modifier")).toBeInTheDocument();
      expect(screen.getByText("Value")).toBeInTheDocument();
    });

    it("displays all 4 modifier rows", () => {
      render(<ATModifiersDisplay archetype={mockArchetype} />);

      expect(screen.getByText("Base HP (Level 50)")).toBeInTheDocument();
      expect(screen.getByText("Base Regeneration")).toBeInTheDocument();
      expect(screen.getByText("Base Recovery")).toBeInTheDocument();
      expect(screen.getByText("Base Threat")).toBeInTheDocument();
    });

    it("formats base HP correctly", () => {
      render(<ATModifiersDisplay archetype={mockArchetype} />);

      expect(screen.getByText("1338.6")).toBeInTheDocument();
    });

    it("formats regeneration as percentage per second", () => {
      render(<ATModifiersDisplay archetype={mockArchetype} />);

      expect(screen.getByText("2.00%/s")).toBeInTheDocument();
    });

    it("formats recovery as percentage per second", () => {
      render(<ATModifiersDisplay archetype={mockArchetype} />);

      expect(screen.getByText("1.67%/s")).toBeInTheDocument();
    });

    it("formats threat as percentage", () => {
      render(<ATModifiersDisplay archetype={mockArchetype} />);

      expect(screen.getByText("100%")).toBeInTheDocument();
    });
  });

  describe("when archetype has partial data", () => {
    it("shows N/A for undefined values", () => {
      render(<ATModifiersDisplay archetype={partialArchetype} />);

      // Should show N/A for missing recovery and threat
      const naElements = screen.getAllByText("N/A");
      expect(naElements).toHaveLength(2);
    });

    it("still shows available values correctly", () => {
      render(<ATModifiersDisplay archetype={partialArchetype} />);

      expect(screen.getByText("1017.0")).toBeInTheDocument();
      expect(screen.getByText("2.00%/s")).toBeInTheDocument();
    });
  });

  describe("styling", () => {
    it("applies custom className", () => {
      const { container } = render(
        <ATModifiersDisplay archetype={mockArchetype} className="custom-class" />
      );

      expect(container.firstChild).toHaveClass("custom-class");
    });

    it("has rounded border styling", () => {
      const { container } = render(
        <ATModifiersDisplay archetype={mockArchetype} />
      );

      expect(container.firstChild).toHaveClass("rounded-lg");
      expect(container.firstChild).toHaveClass("border");
    });
  });
});
