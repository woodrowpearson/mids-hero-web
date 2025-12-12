/**
 * RechargePanel component tests
 * Epic 4.2
 */

import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { RechargePanel } from "../RechargePanel";
import type { RechargeStats } from "@/types/character.types";

describe("RechargePanel", () => {
  const mockRecharge: RechargeStats = {
    global_percent: 125.0,
  };

  it("renders panel header", () => {
    render(<RechargePanel recharge={mockRecharge} />);

    expect(screen.getByText("Recharge")).toBeInTheDocument();
  });

  it("renders Global Recharge with percent-offset format", () => {
    render(<RechargePanel recharge={mockRecharge} />);

    expect(screen.getByText("Global Recharge")).toBeInTheDocument();
    expect(screen.getByText("+125.0%")).toBeInTheDocument();
  });

  it("uses orange color theme for recharge bar", () => {
    render(<RechargePanel recharge={mockRecharge} />);

    const bar = screen.getByRole("presentation");
    expect(bar).toHaveClass("from-orange-500");
    expect(bar).toHaveClass("to-orange-700");
  });

  it("shows perma-Hasten indicator when recharge >= 70%", () => {
    const permaHaste: RechargeStats = {
      global_percent: 70.0,
    };

    render(<RechargePanel recharge={permaHaste} />);

    expect(screen.getByText("Perma-Hasten achieved (+70% threshold)")).toBeInTheDocument();
  });

  it("shows perma-Hasten indicator when recharge > 70%", () => {
    render(<RechargePanel recharge={mockRecharge} />);

    expect(screen.getByText("Perma-Hasten achieved (+70% threshold)")).toBeInTheDocument();
  });

  it("hides perma-Hasten indicator when recharge < 70%", () => {
    const lowRecharge: RechargeStats = {
      global_percent: 50.0,
    };

    render(<RechargePanel recharge={lowRecharge} />);

    expect(screen.queryByText("Perma-Hasten achieved (+70% threshold)")).not.toBeInTheDocument();
  });

  it("renders compact variant with smaller text", () => {
    render(<RechargePanel recharge={mockRecharge} variant="compact" />);

    const header = screen.getByText("Recharge");
    expect(header).toHaveClass("text-sm");
  });

  it("shows placeholder when recharge is null", () => {
    render(<RechargePanel recharge={null} />);

    expect(screen.getByText("Recharge")).toBeInTheDocument();
    expect(screen.getByText("No recharge data")).toBeInTheDocument();
  });

  it("applies custom className", () => {
    const { container } = render(
      <RechargePanel recharge={mockRecharge} className="custom-class" />
    );

    expect(container.firstChild).toHaveClass("custom-class");
  });

  it("bar width uses 200% visual cap", () => {
    render(<RechargePanel recharge={mockRecharge} />);

    const bar = screen.getByRole("presentation");
    // 125/200 = 62.5%
    expect(bar).toHaveStyle({ width: "62.5%" });
  });

  it("bar caps at 100% width for high values", () => {
    const highRecharge: RechargeStats = {
      global_percent: 250.0,
    };

    render(<RechargePanel recharge={highRecharge} />);

    const bar = screen.getByRole("presentation");
    // 250/200 > 1, capped at 100%
    expect(bar).toHaveStyle({ width: "100%" });
  });

  it("handles zero recharge correctly", () => {
    const zeroRecharge: RechargeStats = {
      global_percent: 0,
    };

    render(<RechargePanel recharge={zeroRecharge} />);

    expect(screen.getByText("+0.0%")).toBeInTheDocument();
  });
});
