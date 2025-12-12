/**
 * HPPanel component tests
 * Epic 4.2
 */

import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { HPPanel } from "../HPPanel";
import type { HPStats } from "@/types/character.types";

describe("HPPanel", () => {
  const mockHP: HPStats = {
    max: 1205,
    regen_percent: 140.0,
    regen_per_second: 2.8,
    absorb: 0,
  };

  it("renders panel header", () => {
    render(<HPPanel hp={mockHP} />);

    expect(screen.getByText("Health")).toBeInTheDocument();
  });

  it("renders Max HP with number format", () => {
    render(<HPPanel hp={mockHP} />);

    expect(screen.getByText("Max HP")).toBeInTheDocument();
    expect(screen.getByText("1205")).toBeInTheDocument();
  });

  it("renders Regeneration with percent format", () => {
    render(<HPPanel hp={mockHP} />);

    expect(screen.getByText("Regeneration")).toBeInTheDocument();
    expect(screen.getByText("140.0%")).toBeInTheDocument();
  });

  it("renders regen per-second sub-value", () => {
    render(<HPPanel hp={mockHP} />);

    expect(screen.getByText("2.8/s")).toBeInTheDocument();
  });

  it("hides Absorb when value is 0", () => {
    render(<HPPanel hp={mockHP} />);

    expect(screen.queryByText("Absorb")).not.toBeInTheDocument();
  });

  it("shows Absorb when value is greater than 0", () => {
    const hpWithAbsorb: HPStats = {
      ...mockHP,
      absorb: 500,
    };

    render(<HPPanel hp={hpWithAbsorb} />);

    expect(screen.getByText("Absorb")).toBeInTheDocument();
    expect(screen.getByText("500")).toBeInTheDocument();
  });

  it("uses green color theme for HP bars", () => {
    render(<HPPanel hp={mockHP} />);

    const bars = screen.getAllByRole("presentation");
    bars.forEach((bar) => {
      expect(bar).toHaveClass("from-green-500");
      expect(bar).toHaveClass("to-green-700");
    });
  });

  it("uses cyan color theme for Absorb bar", () => {
    const hpWithAbsorb: HPStats = {
      ...mockHP,
      absorb: 500,
    };

    render(<HPPanel hp={hpWithAbsorb} />);

    const bars = screen.getAllByRole("presentation");
    const absorbBar = bars[bars.length - 1];
    expect(absorbBar).toHaveClass("from-cyan-400");
    expect(absorbBar).toHaveClass("to-cyan-600");
  });

  it("renders compact variant with smaller text", () => {
    render(<HPPanel hp={mockHP} variant="compact" />);

    const header = screen.getByText("Health");
    expect(header).toHaveClass("text-sm");
  });

  it("shows placeholder when hp is null", () => {
    render(<HPPanel hp={null} />);

    expect(screen.getByText("Health")).toBeInTheDocument();
    expect(screen.getByText("No HP data")).toBeInTheDocument();
  });

  it("applies custom className", () => {
    const { container } = render(
      <HPPanel hp={mockHP} className="custom-class" />
    );

    expect(container.firstChild).toHaveClass("custom-class");
  });

  it("uses default maxHPCap when not provided", () => {
    render(<HPPanel hp={mockHP} />);

    const bars = screen.getAllByRole("presentation");
    const maxHPBar = bars[0];
    // Default cap is 2409, 1205/2409 = 50.02%
    expect(maxHPBar).toHaveStyle({ width: "50.020756745952266%" });
  });

  it("respects custom maxHPCap", () => {
    render(<HPPanel hp={mockHP} maxHPCap={1500} />);

    const bars = screen.getAllByRole("presentation");
    const maxHPBar = bars[0];
    // 1205/1500 = 80.33%
    expect(maxHPBar).toHaveStyle({ width: "80.33333333333333%" });
  });

  it("respects custom regenCap", () => {
    render(<HPPanel hp={mockHP} regenCap={200} />);

    const bars = screen.getAllByRole("presentation");
    const regenBar = bars[1];
    // 140/200 = 70%
    expect(regenBar).toHaveStyle({ width: "70%" });
  });
});
