/**
 * MiscStatsPanel component tests
 * Epic 4.2
 */

import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { MiscStatsPanel } from "../MiscStatsPanel";
import type { MiscStats } from "@/types/character.types";

describe("MiscStatsPanel", () => {
  const mockMisc: MiscStats = {
    accuracy: 15.0,
    tohit: 10.0,
    damage: 50.0,
  };

  it("renders panel header", () => {
    render(<MiscStatsPanel misc={mockMisc} />);

    expect(screen.getByText("Misc Effects")).toBeInTheDocument();
  });

  it("renders Accuracy with offset format", () => {
    render(<MiscStatsPanel misc={mockMisc} />);

    expect(screen.getByText("Accuracy:")).toBeInTheDocument();
    expect(screen.getByText("+15.0%")).toBeInTheDocument();
  });

  it("renders ToHit with offset format", () => {
    render(<MiscStatsPanel misc={mockMisc} />);

    expect(screen.getByText("ToHit:")).toBeInTheDocument();
    expect(screen.getByText("+10.0%")).toBeInTheDocument();
  });

  it("renders Damage with offset format", () => {
    render(<MiscStatsPanel misc={mockMisc} />);

    expect(screen.getByText("Damage:")).toBeInTheDocument();
    expect(screen.getByText("+50.0%")).toBeInTheDocument();
  });

  it("renders compact variant with smaller text", () => {
    render(<MiscStatsPanel misc={mockMisc} variant="compact" />);

    const header = screen.getByText("Misc Effects");
    expect(header).toHaveClass("text-sm");
  });

  it("shows placeholder when misc is null", () => {
    render(<MiscStatsPanel misc={null} />);

    expect(screen.getByText("Misc Effects")).toBeInTheDocument();
    expect(screen.getByText("No misc data")).toBeInTheDocument();
  });

  it("applies custom className", () => {
    const { container } = render(
      <MiscStatsPanel misc={mockMisc} className="custom-class" />
    );

    expect(container.firstChild).toHaveClass("custom-class");
  });

  it("handles zero values correctly", () => {
    const zeroMisc: MiscStats = {
      accuracy: 0,
      tohit: 0,
      damage: 0,
    };

    render(<MiscStatsPanel misc={zeroMisc} />);

    // Zero values should not show + sign
    const values = screen.getAllByText("0.0%");
    expect(values).toHaveLength(3);
  });

  it("handles negative values correctly", () => {
    const negativeMisc: MiscStats = {
      accuracy: -5.0,
      tohit: -2.0,
      damage: -10.0,
    };

    render(<MiscStatsPanel misc={negativeMisc} />);

    expect(screen.getByText("-5.0%")).toBeInTheDocument();
    expect(screen.getByText("-2.0%")).toBeInTheDocument();
    expect(screen.getByText("-10.0%")).toBeInTheDocument();
  });

  it("uses text-only layout (no bars)", () => {
    render(<MiscStatsPanel misc={mockMisc} />);

    // Should not have any presentation bars
    const bars = screen.queryAllByRole("presentation");
    expect(bars).toHaveLength(0);
  });

  it("displays stats in correct order", () => {
    render(<MiscStatsPanel misc={mockMisc} />);

    const container = screen.getByText("Misc Effects").parentElement;
    const grid = container?.querySelector(".grid");

    expect(grid).toBeInTheDocument();
    expect(grid?.children.length).toBe(3);
  });

  it("uses monospace font for values", () => {
    render(<MiscStatsPanel misc={mockMisc} />);

    const value = screen.getByText("+15.0%");
    expect(value).toHaveClass("font-mono");
  });
});
