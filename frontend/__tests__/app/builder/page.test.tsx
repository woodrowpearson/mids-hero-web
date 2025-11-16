/**
 * Tests for Builder page
 * Epic 1.3: Layout Shell + Navigation
 */

import { describe, it, expect, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import BuilderPage from "@/app/builder/page";
import { useUIStore } from "@/stores/uiStore";

describe("BuilderPage", () => {
  beforeEach(() => {
    // Reset store
    const store = useUIStore.getState();
    store.setColumnLayout(3);
    store.setSidebarCollapsed(false);
  });

  it("renders BuildLayout component", () => {
    render(<BuilderPage />);

    // BuildLayout includes TopPanel with "Unnamed Hero"
    expect(screen.getByText("Unnamed Hero")).toBeInTheDocument();
  });

  it("displays empty state message", () => {
    render(<BuilderPage />);

    expect(screen.getByText("Empty Build")).toBeInTheDocument();
    expect(screen.getByText(/power selection will be implemented/i)).toBeInTheDocument();
  });

  it("uses column layout from uiStore", () => {
    const store = useUIStore.getState();
    store.setColumnLayout(5);

    render(<BuilderPage />);

    // Check for column count display in empty state
    expect(screen.getByText(/5 columns/i)).toBeInTheDocument();
  });

  it("respects sidebar visibility from uiStore", () => {
    const store = useUIStore.getState();
    store.setSidebarCollapsed(false);

    render(<BuilderPage />);

    // Sidebar should be visible
    expect(screen.getByRole("complementary")).toBeInTheDocument();
  });

  it("hides sidebar when collapsed in store", () => {
    const store = useUIStore.getState();
    store.setSidebarCollapsed(true);

    render(<BuilderPage />);

    // Sidebar should be hidden (aria-hidden=true)
    const sidebar = screen.getByRole("complementary");
    expect(sidebar).toHaveAttribute("aria-hidden", "true");
  });

  it("displays dashed border for empty state", () => {
    const { container } = render(<BuilderPage />);

    const emptyState = container.querySelector(".border-dashed");
    expect(emptyState).toBeInTheDocument();
  });
});
