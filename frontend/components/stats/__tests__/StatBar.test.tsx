/**
 * StatBar component tests
 */

import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { StatBar } from "../StatBar";

describe("StatBar", () => {
  it("renders with label and value", () => {
    render(<StatBar label="Smashing" value={45} cap={45} color="defense" />);

    expect(screen.getByText("Smashing")).toBeInTheDocument();
    expect(screen.getByText("45.0%")).toBeInTheDocument();
  });

  it("renders bar at correct width for value below cap", () => {
    render(<StatBar label="Fire" value={30} cap={45} color="defense" />);

    const bar = screen.getByRole("presentation");
    // 30/45 = 66.67%
    expect(bar).toHaveStyle({ width: "66.66666666666666%" });
  });

  it("renders bar at 100% width when value equals cap", () => {
    render(<StatBar label="Lethal" value={45} cap={45} color="defense" />);

    const bar = screen.getByRole("presentation");
    expect(bar).toHaveStyle({ width: "100%" });
  });

  it("renders bar at 100% width when value exceeds cap", () => {
    render(<StatBar label="Cold" value={52} cap={45} color="defense" />);

    const bar = screen.getByRole("presentation");
    // Width capped at 100% even though value > cap
    expect(bar).toHaveStyle({ width: "100%" });
  });

  it("shows yellow border indicator when at cap", () => {
    render(<StatBar label="Energy" value={45} cap={45} color="defense" />);

    const bar = screen.getByRole("presentation");
    expect(bar).toHaveClass("border-yellow-400");
  });

  it("shows red border indicator when over cap", () => {
    render(<StatBar label="Negative" value={50} cap={45} color="defense" />);

    const bar = screen.getByRole("presentation");
    expect(bar).toHaveClass("border-red-400");
  });

  it("applies defense color gradient", () => {
    render(<StatBar label="Toxic" value={20} cap={45} color="defense" />);

    const bar = screen.getByRole("presentation");
    expect(bar).toHaveClass("from-purple-500");
    expect(bar).toHaveClass("to-purple-700");
  });

  it("applies resistance color gradient", () => {
    render(<StatBar label="Psionic" value={30} cap={75} color="resistance" />);

    const bar = screen.getByRole("presentation");
    expect(bar).toHaveClass("from-cyan-500");
    expect(bar).toHaveClass("to-cyan-700");
  });

  it("applies HP color gradient", () => {
    render(<StatBar label="Max HP" value={1205} cap={1500} color="hp" />);

    const bar = screen.getByRole("presentation");
    expect(bar).toHaveClass("from-green-500");
    expect(bar).toHaveClass("to-green-700");
  });

  it("applies endurance color gradient", () => {
    render(<StatBar label="Max End" value={100} cap={100} color="endurance" />);

    const bar = screen.getByRole("presentation");
    expect(bar).toHaveClass("from-blue-500");
    expect(bar).toHaveClass("to-blue-700");
  });

  it("applies recharge color gradient", () => {
    render(<StatBar label="Recharge" value={25} cap={100} color="recharge" />);

    const bar = screen.getByRole("presentation");
    expect(bar).toHaveClass("from-orange-500");
    expect(bar).toHaveClass("to-orange-700");
  });

  it("hides percentage when showPercentage is false", () => {
    render(
      <StatBar
        label="Melee"
        value={30}
        cap={45}
        color="defense"
        showPercentage={false}
      />
    );

    expect(screen.queryByText("30.0%")).not.toBeInTheDocument();
    expect(screen.getByText("Melee")).toBeInTheDocument();
  });

  it("renders compact variant with smaller sizes", () => {
    render(
      <StatBar
        label="Ranged"
        value={25}
        cap={45}
        color="defense"
        variant="compact"
      />
    );

    const label = screen.getByText("Ranged");
    expect(label).toHaveClass("text-xs");
    expect(label).toHaveClass("w-20");
  });

  it("formats value with 1 decimal place", () => {
    render(<StatBar label="AoE" value={33.333333} cap={45} color="defense" />);

    expect(screen.getByText("33.3%")).toBeInTheDocument();
  });

  it("handles zero value correctly", () => {
    render(<StatBar label="Toxic" value={0} cap={45} color="defense" />);

    expect(screen.getByText("0.0%")).toBeInTheDocument();
    const bar = screen.getByRole("presentation");
    expect(bar).toHaveStyle({ width: "0%" });
  });

  it("handles negative values (debuffs)", () => {
    render(<StatBar label="Fire" value={-10} cap={45} color="defense" />);

    expect(screen.getByText("-10.0%")).toBeInTheDocument();
    const bar = screen.getByRole("presentation");
    // Negative value results in 0% width (clamped by Math.min)
    expect(bar).toHaveStyle({ width: "0%" });
  });

  it("applies custom className", () => {
    const { container } = render(
      <StatBar
        label="Smashing"
        value={30}
        cap={45}
        color="defense"
        className="custom-class"
      />
    );

    expect(container.firstChild).toHaveClass("custom-class");
  });

  it("has accessible aria-label on bar", () => {
    render(<StatBar label="Lethal" value={30} cap={45} color="defense" />);

    const bar = screen.getByLabelText("Lethal: 30.0% of 45% cap");
    expect(bar).toBeInTheDocument();
  });

  // Epic 4.2: New format tests
  describe("Epic 4.2 formats", () => {
    it("formats value as number (whole number)", () => {
      render(<StatBar label="Max HP" value={1205} cap={2409} color="hp" format="number" />);

      expect(screen.getByText("1205")).toBeInTheDocument();
    });

    it("formats value as decimal with 1 decimal place", () => {
      render(<StatBar label="End Rec" value={2.08} cap={10} color="endurance" format="decimal" />);

      expect(screen.getByText("2.1")).toBeInTheDocument();
    });

    it("formats value as decimal with 0 decimals for whole numbers", () => {
      render(<StatBar label="End Rec" value={3} cap={10} color="endurance" format="decimal" />);

      expect(screen.getByText("3")).toBeInTheDocument();
    });

    it("formats value as percent-offset with + sign", () => {
      render(<StatBar label="Recharge" value={125} cap={200} color="recharge" format="percent-offset" />);

      expect(screen.getByText("+125.0%")).toBeInTheDocument();
    });

    it("formats zero value without + sign for percent-offset", () => {
      render(<StatBar label="Recharge" value={0} cap={200} color="recharge" format="percent-offset" />);

      expect(screen.getByText("0.0%")).toBeInTheDocument();
    });
  });

  // Epic 4.2: Suffix tests
  describe("Epic 4.2 suffix", () => {
    it("displays suffix after value", () => {
      render(<StatBar label="Recovery" value={2.08} cap={10} color="endurance" format="decimal" suffix="/s" />);

      expect(screen.getByText("2.1/s")).toBeInTheDocument();
    });
  });

  // Epic 4.2: Sub-value tests
  describe("Epic 4.2 showSubValue", () => {
    it("displays sub-value below main bar", () => {
      render(<StatBar label="Regen" value={140} cap={300} color="hp" format="percent" showSubValue="2.8/s" />);

      expect(screen.getByText("140.0%")).toBeInTheDocument();
      expect(screen.getByText("2.8/s")).toBeInTheDocument();
    });
  });

  // Epic 4.2: Milestone tests
  describe("Epic 4.2 showMilestone", () => {
    it("highlights value when milestone is reached", () => {
      render(<StatBar label="Recharge" value={75} cap={200} color="recharge" format="percent-offset" showMilestone={70} />);

      const valueDisplay = screen.getByText("+75.0%");
      expect(valueDisplay).toHaveClass("text-green-500");
      expect(valueDisplay).toHaveClass("font-bold");
    });

    it("shows green border on bar when milestone is reached", () => {
      render(<StatBar label="Recharge" value={75} cap={200} color="recharge" format="percent-offset" showMilestone={70} />);

      const bar = screen.getByRole("presentation");
      expect(bar).toHaveClass("border-green-400");
    });

    it("does not highlight when below milestone", () => {
      render(<StatBar label="Recharge" value={50} cap={200} color="recharge" format="percent-offset" showMilestone={70} />);

      const valueDisplay = screen.getByText("+50.0%");
      expect(valueDisplay).not.toHaveClass("text-green-500");
    });
  });

  // Epic 4.2: New color themes
  describe("Epic 4.2 color themes", () => {
    it("applies hp-absorb color gradient", () => {
      render(<StatBar label="Absorb" value={500} cap={1000} color="hp-absorb" />);

      const bar = screen.getByRole("presentation");
      expect(bar).toHaveClass("from-cyan-400");
      expect(bar).toHaveClass("to-cyan-600");
    });

    it("applies endurance-usage color gradient", () => {
      render(<StatBar label="End Use" value={0.5} cap={10} color="endurance-usage" />);

      const bar = screen.getByRole("presentation");
      expect(bar).toHaveClass("from-red-500");
      expect(bar).toHaveClass("to-red-700");
    });
  });

  // Epic 4.2: allowNegative tests
  describe("Epic 4.2 allowNegative", () => {
    it("clamps negative values to 0 when allowNegative is false", () => {
      render(<StatBar label="End Use" value={-5} cap={10} color="endurance-usage" format="decimal" allowNegative={false} />);

      expect(screen.getByText("0")).toBeInTheDocument();
    });

    it("shows negative values when allowNegative is true (default)", () => {
      render(<StatBar label="Fire" value={-10} cap={45} color="defense" />);

      expect(screen.getByText("-10.0%")).toBeInTheDocument();
    });
  });
});
