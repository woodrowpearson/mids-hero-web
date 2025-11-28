/**
 * CapsDisplay component tests
 * Epic 2.3 - Character Sheet Display
 */

import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { CapsDisplay } from "../CapsDisplay";
import type { Archetype } from "@/types/character.types";

// Mock archetype with full caps
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

// Tanker archetype with higher caps
const tankerArchetype: Archetype = {
  id: 2,
  name: "Tanker",
  displayName: "Tanker",
  damageCap: 4.0,
  resistanceCap: 0.9,
  defenseCap: 2.25,
  hpCap: 4000,
  regenerationCap: 30.0,
  recoveryCap: 8.0,
  rechargeCap: 5.0,
};

// Archetype with partial caps
const partialArchetype: Archetype = {
  id: 3,
  name: "Blaster",
  displayName: "Blaster",
  damageCap: 5.0,
  resistanceCap: 0.75,
  // Other caps undefined
};

describe("CapsDisplay", () => {
  describe("when no archetype is selected", () => {
    it("displays placeholder message", () => {
      render(<CapsDisplay archetype={null} />);

      expect(
        screen.getByText("Select an archetype to view caps.")
      ).toBeInTheDocument();
    });
  });

  describe("when archetype is selected", () => {
    it("renders the caps table with headers", () => {
      render(<CapsDisplay archetype={mockArchetype} />);

      expect(screen.getByText("Cap Type")).toBeInTheDocument();
      expect(screen.getByText("Value")).toBeInTheDocument();
      expect(screen.getByText("Description")).toBeInTheDocument();
    });

    it("displays all 7 cap types", () => {
      render(<CapsDisplay archetype={mockArchetype} />);

      expect(screen.getByText("HP Cap")).toBeInTheDocument();
      expect(screen.getByText("Damage Cap")).toBeInTheDocument();
      expect(screen.getByText("Resistance Cap")).toBeInTheDocument();
      expect(screen.getByText("Defense Cap (Display)")).toBeInTheDocument();
      expect(screen.getByText("Regeneration Cap")).toBeInTheDocument();
      expect(screen.getByText("Recovery Cap")).toBeInTheDocument();
      expect(screen.getByText("Recharge Cap")).toBeInTheDocument();
    });

    it("formats HP cap as whole number", () => {
      render(<CapsDisplay archetype={mockArchetype} />);

      expect(screen.getByText("3213")).toBeInTheDocument();
    });

    it("formats damage cap as percentage", () => {
      render(<CapsDisplay archetype={mockArchetype} />);

      // Both damage and recharge caps are 500%, so use getAllByText
      const fiveHundredElements = screen.getAllByText("500%");
      expect(fiveHundredElements.length).toBeGreaterThanOrEqual(1);
    });

    it("formats resistance cap as percentage", () => {
      render(<CapsDisplay archetype={mockArchetype} />);

      expect(screen.getByText("75%")).toBeInTheDocument();
    });

    it("formats defense cap as percentage", () => {
      render(<CapsDisplay archetype={mockArchetype} />);

      expect(screen.getByText("225%")).toBeInTheDocument();
    });

    it("formats regeneration cap as percentage", () => {
      render(<CapsDisplay archetype={mockArchetype} />);

      expect(screen.getByText("3000%")).toBeInTheDocument();
    });

    it("formats recovery cap as percentage", () => {
      render(<CapsDisplay archetype={mockArchetype} />);

      expect(screen.getByText("800%")).toBeInTheDocument();
    });

    it("formats recharge cap as percentage", () => {
      render(<CapsDisplay archetype={mockArchetype} />);

      // 500% for recharge cap (5.0 * 100)
      // Note: Two 500% values exist (damage and recharge)
      const fiveHundredPercent = screen.getAllByText("500%");
      expect(fiveHundredPercent.length).toBeGreaterThanOrEqual(2);
    });

    it("shows descriptions for each cap", () => {
      render(<CapsDisplay archetype={mockArchetype} />);

      expect(screen.getByText("Maximum HP value")).toBeInTheDocument();
      expect(screen.getByText("Maximum damage buff")).toBeInTheDocument();
      expect(screen.getByText("Maximum damage resistance")).toBeInTheDocument();
      expect(
        screen.getByText("Maximum defense (display only, soft cap is 45%)")
      ).toBeInTheDocument();
    });
  });

  describe("different archetypes", () => {
    it("displays tanker higher resistance cap", () => {
      render(<CapsDisplay archetype={tankerArchetype} />);

      expect(screen.getByText("90%")).toBeInTheDocument();
    });

    it("displays tanker higher HP cap", () => {
      render(<CapsDisplay archetype={tankerArchetype} />);

      expect(screen.getByText("4000")).toBeInTheDocument();
    });
  });

  describe("when archetype has partial data", () => {
    it("shows N/A for undefined caps", () => {
      render(<CapsDisplay archetype={partialArchetype} />);

      const naElements = screen.getAllByText("N/A");
      // HP Cap, Defense Cap, Regen Cap, Recovery Cap, Recharge Cap should be N/A
      expect(naElements.length).toBe(5);
    });

    it("still shows available caps correctly", () => {
      render(<CapsDisplay archetype={partialArchetype} />);

      expect(screen.getByText("500%")).toBeInTheDocument(); // Damage cap
      expect(screen.getByText("75%")).toBeInTheDocument(); // Resistance cap
    });
  });

  describe("styling", () => {
    it("applies custom className", () => {
      const { container } = render(
        <CapsDisplay archetype={mockArchetype} className="my-custom-class" />
      );

      expect(container.firstChild).toHaveClass("my-custom-class");
    });

    it("has rounded border styling", () => {
      const { container } = render(<CapsDisplay archetype={mockArchetype} />);

      expect(container.firstChild).toHaveClass("rounded-lg");
      expect(container.firstChild).toHaveClass("border");
    });
  });
});
