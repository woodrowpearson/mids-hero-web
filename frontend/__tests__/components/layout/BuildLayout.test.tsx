/**
 * Tests for BuildLayout component
 * Epic 1.3: Layout Shell + Navigation
 */

import { describe, it, expect, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { BuildLayout } from "@/components/layout/BuildLayout";
import { useUIStore } from "@/stores/uiStore";

describe("BuildLayout", () => {
  beforeEach(() => {
    // Reset store
    const store = useUIStore.getState();
    store.setColumnLayout(3);
    store.setSidebarCollapsed(false);
  });

  it("renders children correctly", () => {
    render(
      <BuildLayout>
        <div data-testid="child-content">Test Content</div>
      </BuildLayout>
    );

    expect(screen.getByTestId("child-content")).toBeInTheDocument();
    expect(screen.getByText("Test Content")).toBeInTheDocument();
  });

  it("renders TopPanel component", () => {
    render(
      <BuildLayout>
        <div>Content</div>
      </BuildLayout>
    );

    // TopPanel contains "Mids Hero Web"
    expect(screen.getByText("Mids Hero Web")).toBeInTheDocument();
  });

  it("renders SidePanel when showSidebar is true", () => {
    render(
      <BuildLayout showSidebar={true}>
        <div>Content</div>
      </BuildLayout>
    );

    // SidePanel has role="complementary"
    expect(screen.getByRole("complementary")).toBeInTheDocument();
  });

  it("does not render SidePanel when showSidebar is false", () => {
    render(
      <BuildLayout showSidebar={false}>
        <div>Content</div>
      </BuildLayout>
    );

    // SidePanel should not be in the document
    expect(screen.queryByRole("complementary")).not.toBeInTheDocument();
  });

  it("uses default column count from uiStore", () => {
    const store = useUIStore.getState();
    store.setColumnLayout(4);

    render(
      <BuildLayout>
        <div>Content</div>
      </BuildLayout>
    );

    const mainGrid = screen.getByRole("main").querySelector("div[data-column-count]");
    expect(mainGrid).toHaveAttribute("data-column-count", "4");
  });

  it("allows column count override via prop", () => {
    // Set store to 3, but override with 5
    const store = useUIStore.getState();
    store.setColumnLayout(3);

    render(
      <BuildLayout columnCount={5}>
        <div>Content</div>
      </BuildLayout>
    );

    const mainGrid = screen.getByRole("main").querySelector("div[data-column-count]");
    expect(mainGrid).toHaveAttribute("data-column-count", "5");
  });

  it("applies correct grid column classes for 2 columns", () => {
    render(
      <BuildLayout columnCount={2}>
        <div>Content</div>
      </BuildLayout>
    );

    const mainGrid = screen.getByRole("main").querySelector("div[data-column-count]");
    expect(mainGrid).toHaveClass("md:grid-cols-2");
    expect(mainGrid).not.toHaveClass("lg:grid-cols-3");
  });

  it("applies correct grid column classes for 3 columns", () => {
    render(
      <BuildLayout columnCount={3}>
        <div>Content</div>
      </BuildLayout>
    );

    const mainGrid = screen.getByRole("main").querySelector("div[data-column-count]");
    expect(mainGrid).toHaveClass("md:grid-cols-2");
    expect(mainGrid).toHaveClass("lg:grid-cols-3");
    expect(mainGrid).not.toHaveClass("xl:grid-cols-4");
  });

  it("applies correct grid column classes for 6 columns", () => {
    render(
      <BuildLayout columnCount={6}>
        <div>Content</div>
      </BuildLayout>
    );

    const mainGrid = screen.getByRole("main").querySelector("div[data-column-count]");
    expect(mainGrid).toHaveClass("md:grid-cols-2");
    expect(mainGrid).toHaveClass("lg:grid-cols-3");
    expect(mainGrid).toHaveClass("2xl:grid-cols-6");
  });

  it("respects sidebar collapsed state from uiStore", () => {
    const store = useUIStore.getState();
    store.setSidebarCollapsed(true);

    render(
      <BuildLayout showSidebar={true}>
        <div>Content</div>
      </BuildLayout>
    );

    // Sidebar should be in document but hidden
    const sidebar = screen.getByRole("complementary");
    expect(sidebar).toHaveAttribute("aria-hidden", "true");
  });

  it("applies custom className to main content area", () => {
    render(
      <BuildLayout className="custom-class">
        <div>Content</div>
      </BuildLayout>
    );

    const main = screen.getByRole("main");
    expect(main).toHaveClass("custom-class");
  });

  it("renders main content area as scrollable", () => {
    render(
      <BuildLayout>
        <div>Content</div>
      </BuildLayout>
    );

    const main = screen.getByRole("main");
    expect(main).toHaveClass("overflow-y-auto");
  });
});
