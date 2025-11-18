/**
 * Tests for PowersetSelector base component
 */

import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { PowersetSelector } from "../PowersetSelector";
import type { Powerset } from "@/types/character.types";

// Mock powersets
const mockPowersets: Powerset[] = [
  {
    id: 1,
    name: "Blaster_Primary.Energy",
    displayName: "Energy Blast",
    archetypeId: 1,
    type: "Primary",
    description: "Energy-based ranged attacks",
  },
  {
    id: 2,
    name: "Blaster_Primary.Fire",
    displayName: "Fire Blast",
    archetypeId: 1,
    type: "Primary",
    description: "Fire-based ranged attacks",
  },
  {
    id: 3,
    name: "Blaster_Primary.Ice",
    displayName: "Ice Blast",
    archetypeId: 1,
    type: "Primary",
    description: "Ice-based ranged attacks with slows",
  },
];

describe("PowersetSelector", () => {
  it("renders with powersets from props", () => {
    const onChange = vi.fn();

    render(
      <PowersetSelector
        powersets={mockPowersets}
        selected={null}
        onChange={onChange}
        placeholder="Select a powerset"
      />
    );

    expect(screen.getByRole("combobox")).toBeInTheDocument();
  });

  it("displays selected powerset", () => {
    const onChange = vi.fn();

    render(
      <PowersetSelector
        powersets={mockPowersets}
        selected={mockPowersets[0]}
        onChange={onChange}
        placeholder="Select a powerset"
      />
    );

    expect(screen.getByText("Energy Blast")).toBeInTheDocument();
  });

  it("shows disabled state when disabled prop is true", () => {
    const onChange = vi.fn();

    render(
      <PowersetSelector
        powersets={mockPowersets}
        selected={null}
        onChange={onChange}
        disabled={true}
        placeholder="Disabled"
      />
    );

    const select = screen.getByRole("combobox");
    expect(select).toBeDisabled();
  });

  it("displays label when provided", () => {
    const onChange = vi.fn();

    render(
      <PowersetSelector
        powersets={mockPowersets}
        selected={null}
        onChange={onChange}
        label="Primary Powerset"
        placeholder="Select"
      />
    );

    expect(screen.getByText("Primary Powerset")).toBeInTheDocument();
  });

  it("displays description when selected powerset has description", () => {
    const onChange = vi.fn();

    render(
      <PowersetSelector
        powersets={mockPowersets}
        selected={mockPowersets[0]}
        onChange={onChange}
      />
    );

    expect(screen.getByText(/Energy-based ranged attacks/i)).toBeInTheDocument();
  });
});
