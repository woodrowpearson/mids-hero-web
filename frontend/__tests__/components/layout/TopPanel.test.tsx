/**
 * Tests for TopPanel component
 * Epic 1.3: Layout Shell + Navigation
 */

import { describe, it, expect, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { TopPanel } from "@/components/layout/TopPanel";
import { useCharacterStore } from "@/stores/characterStore";

describe("TopPanel", () => {
  beforeEach(() => {
    // Reset character store
    const store = useCharacterStore.getState();
    store.clearBuild();
  });

  it("displays default character name when none set", () => {
    render(<TopPanel />);
    expect(screen.getByText("Unnamed Hero")).toBeInTheDocument();
  });

  it("displays character name from store", () => {
    const store = useCharacterStore.getState();
    store.setName("Test Hero");

    render(<TopPanel />);
    expect(screen.getByText("Test Hero")).toBeInTheDocument();
  });

  it("displays archetype display name", () => {
    const store = useCharacterStore.getState();
    store.setArchetype({
      id: 1,
      name: "Blaster",
      display_name: "Blaster",
      icon: null,
      origin: null,
    });

    render(<TopPanel />);
    expect(screen.getByText("Blaster")).toBeInTheDocument();
  });

  it("displays default archetype text when none set", () => {
    render(<TopPanel />);
    expect(screen.getByText("No Archetype")).toBeInTheDocument();
  });

  it("displays character level", () => {
    const store = useCharacterStore.getState();
    store.setLevel(25);

    render(<TopPanel />);
    expect(screen.getByText("Level 25")).toBeInTheDocument();
  });

  it("renders action buttons", () => {
    render(<TopPanel />);

    expect(screen.getByRole("button", { name: /new/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /save/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /load/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /export/i })).toBeInTheDocument();
  });

  it("renders settings button with aria-label", () => {
    render(<TopPanel />);

    const settingsButton = screen.getByRole("button", { name: /settings/i });
    expect(settingsButton).toBeInTheDocument();
    expect(settingsButton).toHaveAttribute("aria-label", "Settings");
  });

  it("renders ColumnLayoutSelector", () => {
    render(<TopPanel />);

    expect(screen.getByRole("group", { name: /column layout selector/i })).toBeInTheDocument();
  });

  it("has fixed height of 77px", () => {
    render(<TopPanel />);

    const header = screen.getByRole("banner");
    expect(header).toHaveClass("h-[77px]");
  });

  it("is sticky positioned at top", () => {
    render(<TopPanel />);

    const header = screen.getByRole("banner");
    expect(header).toHaveClass("sticky");
    expect(header).toHaveClass("top-0");
  });

  it("has high z-index for layering", () => {
    render(<TopPanel />);

    const header = screen.getByRole("banner");
    expect(header).toHaveClass("z-50");
  });

  it("updates when character store changes", () => {
    const { rerender } = render(<TopPanel />);
    expect(screen.getByText("Unnamed Hero")).toBeInTheDocument();

    const store = useCharacterStore.getState();
    store.setName("Updated Hero");

    rerender(<TopPanel />);
    expect(screen.getByText("Updated Hero")).toBeInTheDocument();
  });
});
