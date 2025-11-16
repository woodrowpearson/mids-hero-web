/**
 * Tests for ColumnLayoutSelector component
 * Epic 1.3: Layout Shell + Navigation
 */

import { describe, it, expect, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { userEvent } from "@testing-library/user-event";
import { ColumnLayoutSelector } from "@/components/ui/ColumnLayoutSelector";
import { useUIStore } from "@/stores/uiStore";

describe("ColumnLayoutSelector", () => {
  beforeEach(() => {
    // Reset store
    const store = useUIStore.getState();
    store.setColumnLayout(3);
    localStorage.clear();
  });

  it("displays all column options (2-6)", () => {
    render(<ColumnLayoutSelector />);

    [2, 3, 4, 5, 6].forEach((count) => {
      expect(screen.getByText(String(count))).toBeInTheDocument();
    });
  });

  it("has accessible label", () => {
    render(<ColumnLayoutSelector />);

    expect(screen.getByRole("group", { name: /column layout selector/i })).toBeInTheDocument();
  });

  it("highlights current column count from store", () => {
    const store = useUIStore.getState();
    store.setColumnLayout(4);

    render(<ColumnLayoutSelector />);

    const button4 = screen.getByText("4");
    expect(button4).toHaveAttribute("aria-pressed", "true");
  });

  it("updates uiStore when column button clicked", async () => {
    const user = userEvent.setup();
    render(<ColumnLayoutSelector />);

    const button5 = screen.getByText("5");
    await user.click(button5);

    expect(useUIStore.getState().columnLayout).toBe(5);
  });

  it("persists selection to localStorage", async () => {
    const user = userEvent.setup();
    render(<ColumnLayoutSelector />);

    const button6 = screen.getByText("6");
    await user.click(button6);

    const stored = localStorage.getItem("ui-preferences-storage");
    expect(stored).toBeTruthy();

    if (stored) {
      const parsed = JSON.parse(stored);
      expect(parsed.state.columnLayout).toBe(6);
    }
  });

  it("shows correct active state for each option", () => {
    render(<ColumnLayoutSelector />);

    // Button 3 should be active (default)
    const button3 = screen.getByText("3");
    expect(button3).toHaveAttribute("aria-pressed", "true");

    // Other buttons should not be active
    [2, 4, 5, 6].forEach((count) => {
      const button = screen.getByText(String(count));
      expect(button).toHaveAttribute("aria-pressed", "false");
    });
  });

  it("applies correct styling to active button", () => {
    render(<ColumnLayoutSelector />);

    const button3 = screen.getByText("3");
    expect(button3).toHaveClass("bg-primary");
    expect(button3).toHaveClass("text-primary-foreground");
  });

  it("applies correct styling to inactive buttons", () => {
    render(<ColumnLayoutSelector />);

    const button2 = screen.getByText("2");
    expect(button2).toHaveClass("bg-muted");
    expect(button2).toHaveClass("hover:bg-muted/80");
  });

  it("displays 'Columns:' label", () => {
    render(<ColumnLayoutSelector />);

    expect(screen.getByText("Columns:")).toBeInTheDocument();
  });
});
