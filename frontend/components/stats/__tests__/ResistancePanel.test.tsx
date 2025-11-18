/**
 * ResistancePanel component tests
 */

import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { ResistancePanel } from "../ResistancePanel";
import type { ResistanceStats } from "@/types/character.types";

describe("ResistancePanel", () => {
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

  it("renders panel header", () => {
    render(<ResistancePanel resistance={mockResistance} resistanceCap={75} />);

    expect(screen.getByText("Resistance")).toBeInTheDocument();
  });

  it("renders all 8 resistance types", () => {
    render(<ResistancePanel resistance={mockResistance} resistanceCap={75} />);

    expect(screen.getByText("Smashing")).toBeInTheDocument();
    expect(screen.getByText("Lethal")).toBeInTheDocument();
    expect(screen.getByText("Fire")).toBeInTheDocument();
    expect(screen.getByText("Cold")).toBeInTheDocument();
    expect(screen.getByText("Energy")).toBeInTheDocument();
    expect(screen.getByText("Negative")).toBeInTheDocument();
    expect(screen.getByText("Toxic")).toBeInTheDocument();
    expect(screen.getByText("Psionic")).toBeInTheDocument();
  });

  it("displays correct percentage values", () => {
    render(<ResistancePanel resistance={mockResistance} resistanceCap={75} />);

    expect(screen.getAllByText("60.0%")).toHaveLength(2); // Smashing, Lethal
    expect(screen.getAllByText("40.0%")).toHaveLength(2); // Fire, Cold
    expect(screen.getByText("30.0%")).toBeInTheDocument(); // Energy
    expect(screen.getByText("20.0%")).toBeInTheDocument(); // Negative
    expect(screen.getAllByText("0.0%")).toHaveLength(2); // Toxic, Psionic
  });

  it("uses cyan color theme for all bars", () => {
    render(<ResistancePanel resistance={mockResistance} resistanceCap={75} />);

    const bars = screen.getAllByRole("presentation");
    bars.forEach((bar) => {
      expect(bar).toHaveClass("from-cyan-500");
      expect(bar).toHaveClass("to-cyan-700");
    });
  });

  it("passes correct resistance cap to StatBars", () => {
    render(<ResistancePanel resistance={mockResistance} resistanceCap={75} />);

    // Smashing is 60, cap is 75, so bar should be 80% width
    const bars = screen.getAllByRole("presentation");
    const smashingBar = bars[0]; // First bar is Smashing
    expect(smashingBar).toHaveStyle({ width: "80%" }); // 60/75 = 80%
  });

  it("handles Tanker resistance cap (90%)", () => {
    const tankerResistance: ResistanceStats = {
      smashing: 90,
      lethal: 90,
      fire: 75,
      cold: 75,
      energy: 60,
      negative: 45,
      toxic: 0,
      psionic: 0,
    };

    render(
      <ResistancePanel resistance={tankerResistance} resistanceCap={90} />
    );

    expect(screen.getAllByText("90.0%")).toHaveLength(2); // Smashing, Lethal at cap
    expect(screen.getAllByText("75.0%")).toHaveLength(2); // Fire, Cold
  });

  it("renders compact variant with smaller text", () => {
    render(
      <ResistancePanel
        resistance={mockResistance}
        resistanceCap={75}
        variant="compact"
      />
    );

    const header = screen.getByText("Resistance");
    expect(header).toHaveClass("text-base");
  });

  it("handles all zero resistance values", () => {
    const zeroResistance: ResistanceStats = {
      smashing: 0,
      lethal: 0,
      fire: 0,
      cold: 0,
      energy: 0,
      negative: 0,
      toxic: 0,
      psionic: 0,
    };

    render(
      <ResistancePanel resistance={zeroResistance} resistanceCap={75} />
    );

    // All bars should show 0.0%
    const percentages = screen.getAllByText("0.0%");
    expect(percentages).toHaveLength(8); // 8 typed resistance values
  });

  it("handles overcap resistance values", () => {
    const overcapResistance: ResistanceStats = {
      smashing: 85, // Over 75% cap
      lethal: 80, // Over 75% cap
      fire: 75, // At cap
      cold: 60,
      energy: 30,
      negative: 20,
      toxic: 0,
      psionic: 0,
    };

    render(
      <ResistancePanel resistance={overcapResistance} resistanceCap={75} />
    );

    const bars = screen.getAllByRole("presentation");

    // Smashing (85%) should be at 100% width and have red border
    const smashingBar = bars[0];
    expect(smashingBar).toHaveStyle({ width: "100%" });
    expect(smashingBar).toHaveClass("border-red-400");

    // Lethal (80%) should be at 100% width and have red border
    const lethalBar = bars[1];
    expect(lethalBar).toHaveStyle({ width: "100%" });
    expect(lethalBar).toHaveClass("border-red-400");

    // Fire (75%) should be at 100% width and have yellow border (at cap)
    const fireBar = bars[2];
    expect(fireBar).toHaveStyle({ width: "100%" });
    expect(fireBar).toHaveClass("border-yellow-400");
  });

  it("applies custom className", () => {
    const { container } = render(
      <ResistancePanel
        resistance={mockResistance}
        resistanceCap={75}
        className="custom-class"
      />
    );

    expect(container.firstChild).toHaveClass("custom-class");
  });

  it("renders bars in correct order", () => {
    render(<ResistancePanel resistance={mockResistance} resistanceCap={75} />);

    const bars = screen.getAllByRole("presentation");

    // Verify 8 resistance bars total
    expect(bars).toHaveLength(8);

    // First should be Smashing (60%)
    expect(bars[0]).toHaveStyle({ width: "80%" }); // 60/75

    // Last should be Psionic (0%)
    expect(bars[7]).toHaveStyle({ width: "0%" });
  });

  it("does not render positional resistance section", () => {
    render(<ResistancePanel resistance={mockResistance} resistanceCap={75} />);

    // Resistance has no positional component (unlike Defense)
    expect(screen.queryByText("Positional Resistance")).not.toBeInTheDocument();
    expect(screen.queryByText("Melee")).not.toBeInTheDocument();
    expect(screen.queryByText("Ranged")).not.toBeInTheDocument();
    expect(screen.queryByText("AoE")).not.toBeInTheDocument();
  });
});
