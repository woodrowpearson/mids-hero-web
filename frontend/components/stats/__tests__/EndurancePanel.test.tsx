/**
 * EndurancePanel component tests
 * Epic 4.2
 */

import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { EndurancePanel } from "../EndurancePanel";
import type { EnduranceStats } from "@/types/character.types";

describe("EndurancePanel", () => {
  const mockEndurance: EnduranceStats = {
    max: 100,
    recovery_per_second: 2.08,
    usage_per_second: 0.5,
  };

  it("renders panel header", () => {
    render(<EndurancePanel endurance={mockEndurance} />);

    expect(screen.getByText("Endurance")).toBeInTheDocument();
  });

  it("renders Max End with number format", () => {
    render(<EndurancePanel endurance={mockEndurance} />);

    expect(screen.getByText("Max End")).toBeInTheDocument();
    expect(screen.getByText("100")).toBeInTheDocument();
  });

  it("renders End Rec with decimal format and /s suffix", () => {
    render(<EndurancePanel endurance={mockEndurance} />);

    expect(screen.getByText("End Rec")).toBeInTheDocument();
    expect(screen.getByText("2.08/s")).toBeInTheDocument();
  });

  it("renders End Use with decimal format and /s suffix", () => {
    render(<EndurancePanel endurance={mockEndurance} />);

    expect(screen.getByText("End Use")).toBeInTheDocument();
    expect(screen.getByText("0.5/s")).toBeInTheDocument();
  });

  it("uses blue color theme for Max End and Recovery bars", () => {
    render(<EndurancePanel endurance={mockEndurance} />);

    const bars = screen.getAllByRole("presentation");
    // First two bars (Max End, Recovery) should be blue
    expect(bars[0]).toHaveClass("from-blue-500");
    expect(bars[0]).toHaveClass("to-blue-700");
    expect(bars[1]).toHaveClass("from-blue-500");
    expect(bars[1]).toHaveClass("to-blue-700");
  });

  it("uses red color theme for End Use bar", () => {
    render(<EndurancePanel endurance={mockEndurance} />);

    const bars = screen.getAllByRole("presentation");
    const usageBar = bars[2];
    expect(usageBar).toHaveClass("from-red-500");
    expect(usageBar).toHaveClass("to-red-700");
  });

  it("renders compact variant with smaller text", () => {
    render(<EndurancePanel endurance={mockEndurance} variant="compact" />);

    const header = screen.getByText("Endurance");
    expect(header).toHaveClass("text-sm");
  });

  it("shows placeholder when endurance is null", () => {
    render(<EndurancePanel endurance={null} />);

    expect(screen.getByText("Endurance")).toBeInTheDocument();
    expect(screen.getByText("No endurance data")).toBeInTheDocument();
  });

  it("applies custom className", () => {
    const { container } = render(
      <EndurancePanel endurance={mockEndurance} className="custom-class" />
    );

    expect(container.firstChild).toHaveClass("custom-class");
  });

  it("uses default maxEnduranceCap when not provided", () => {
    render(<EndurancePanel endurance={mockEndurance} />);

    const bars = screen.getAllByRole("presentation");
    const maxEndBar = bars[0];
    // Default cap is 100, 100/100 = 100%
    expect(maxEndBar).toHaveStyle({ width: "100%" });
  });

  it("respects custom maxEnduranceCap", () => {
    render(<EndurancePanel endurance={mockEndurance} maxEnduranceCap={125} />);

    const bars = screen.getAllByRole("presentation");
    const maxEndBar = bars[0];
    // 100/125 = 80%
    expect(maxEndBar).toHaveStyle({ width: "80%" });
  });

  it("respects custom recoveryCap", () => {
    render(<EndurancePanel endurance={mockEndurance} recoveryCap={5} />);

    const bars = screen.getAllByRole("presentation");
    const recoveryBar = bars[1];
    // 2.08/5 = 41.6%
    expect(recoveryBar).toHaveStyle({ width: "41.6%" });
  });

  it("handles zero usage correctly", () => {
    const zeroUsage: EnduranceStats = {
      ...mockEndurance,
      usage_per_second: 0,
    };

    render(<EndurancePanel endurance={zeroUsage} />);

    expect(screen.getByText("0/s")).toBeInTheDocument();
  });
});
