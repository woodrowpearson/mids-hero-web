/**
 * DefensePanel component tests
 */

import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { DefensePanel } from "../DefensePanel";
import type { DefenseStats } from "@/types/character.types";

describe("DefensePanel", () => {
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

  it("renders panel header", () => {
    render(<DefensePanel defense={mockDefense} defenseCap={45} />);

    expect(screen.getByText("Defense")).toBeInTheDocument();
  });

  it("renders all 8 typed defense types", () => {
    render(<DefensePanel defense={mockDefense} defenseCap={45} />);

    expect(screen.getByText("Smashing")).toBeInTheDocument();
    expect(screen.getByText("Lethal")).toBeInTheDocument();
    expect(screen.getByText("Fire")).toBeInTheDocument();
    expect(screen.getByText("Cold")).toBeInTheDocument();
    expect(screen.getByText("Energy")).toBeInTheDocument();
    expect(screen.getByText("Negative")).toBeInTheDocument();
    expect(screen.getByText("Toxic")).toBeInTheDocument();
    expect(screen.getByText("Psionic")).toBeInTheDocument();
  });

  it("renders all 3 positional defense types", () => {
    render(<DefensePanel defense={mockDefense} defenseCap={45} />);

    expect(screen.getByText("Melee")).toBeInTheDocument();
    expect(screen.getByText("Ranged")).toBeInTheDocument();
    expect(screen.getByText("AoE")).toBeInTheDocument();
  });

  it("shows two section headers", () => {
    render(<DefensePanel defense={mockDefense} defenseCap={45} />);

    expect(screen.getByText("Typed Defense")).toBeInTheDocument();
    expect(screen.getByText("Positional Defense")).toBeInTheDocument();
  });

  it("displays correct percentage values", () => {
    render(<DefensePanel defense={mockDefense} defenseCap={45} />);

    expect(screen.getAllByText("45.0%")).toHaveLength(3); // Smashing, Lethal, Melee at cap
    expect(screen.getAllByText("30.5%")).toHaveLength(3); // Fire, Cold, Ranged
    expect(screen.getAllByText("25.2%")).toHaveLength(2); // Energy, AoE
    expect(screen.getByText("18.0%")).toBeInTheDocument(); // Negative (unique)
    expect(screen.getAllByText("0.0%")).toHaveLength(2); // Toxic, Psionic
  });

  it("uses purple color theme for all bars", () => {
    render(<DefensePanel defense={mockDefense} defenseCap={45} />);

    const bars = screen.getAllByRole("presentation");
    bars.forEach((bar) => {
      expect(bar).toHaveClass("from-purple-500");
      expect(bar).toHaveClass("to-purple-700");
    });
  });

  it("passes correct defense cap to StatBars", () => {
    render(<DefensePanel defense={mockDefense} defenseCap={50} />);

    // Smashing is 45, cap is 50, so bar should be 90% width
    const bars = screen.getAllByRole("presentation");
    const smashingBar = bars[0]; // First bar is Smashing
    expect(smashingBar).toHaveStyle({ width: "90%" }); // 45/50 = 90%
  });

  it("handles Tanker defense cap (50%)", () => {
    const tankerDefense: DefenseStats = {
      ...mockDefense,
      smashing: 50,
      lethal: 50,
      melee: 50,
      ranged: 0,
      aoe: 0,
    };

    render(<DefensePanel defense={tankerDefense} defenseCap={50} />);

    expect(screen.getAllByText("50.0%")).toHaveLength(3); // Smashing, Lethal, Melee at cap
  });

  it("renders compact variant with smaller text", () => {
    render(
      <DefensePanel defense={mockDefense} defenseCap={45} variant="compact" />
    );

    const header = screen.getByText("Defense");
    expect(header).toHaveClass("text-base");

    const sectionHeader = screen.getByText("Typed Defense");
    expect(sectionHeader).toHaveClass("text-xs");
  });

  it("handles all zero defense values", () => {
    const zeroDefense: DefenseStats = {
      smashing: 0,
      lethal: 0,
      fire: 0,
      cold: 0,
      energy: 0,
      negative: 0,
      toxic: 0,
      psionic: 0,
      melee: 0,
      ranged: 0,
      aoe: 0,
    };

    render(<DefensePanel defense={zeroDefense} defenseCap={45} />);

    // All bars should show 0.0%
    const percentages = screen.getAllByText("0.0%");
    expect(percentages).toHaveLength(11); // 8 typed + 3 positional
  });

  it("applies custom className", () => {
    const { container } = render(
      <DefensePanel
        defense={mockDefense}
        defenseCap={45}
        className="custom-class"
      />
    );

    expect(container.firstChild).toHaveClass("custom-class");
  });

  it("renders bars in correct order", () => {
    render(<DefensePanel defense={mockDefense} defenseCap={45} />);

    const bars = screen.getAllByRole("presentation");

    // Verify order: 8 typed + 3 positional = 11 total
    expect(bars).toHaveLength(11);

    // First should be Smashing (45%)
    expect(bars[0]).toHaveStyle({ width: "100%" });

    // Last should be AoE (25.2%)
    const aoePercentage = (25.2 / 45) * 100;
    expect(bars[10]).toHaveStyle({ width: `${aoePercentage}%` });
  });
});
