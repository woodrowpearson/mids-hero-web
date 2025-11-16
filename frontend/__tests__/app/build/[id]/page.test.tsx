/**
 * Tests for Build Viewer page
 * Epic 1.3: Layout Shell + Navigation
 */

import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import BuildViewerPage from "@/app/build/[id]/page";

describe("BuildViewerPage", () => {
  it("renders BuildLayout component", async () => {
    const Page = await BuildViewerPage({ params: { id: "test-123" } });
    render(Page);

    // BuildLayout includes TopPanel
    expect(screen.getByText("Unnamed Hero")).toBeInTheDocument();
  });

  it("displays build ID from params", async () => {
    const Page = await BuildViewerPage({ params: { id: "test-build-456" } });
    render(Page);

    expect(screen.getByText(/test-build-456/i)).toBeInTheDocument();
  });

  it("displays shared build heading", async () => {
    const Page = await BuildViewerPage({ params: { id: "abc123" } });
    render(Page);

    expect(screen.getByText("Shared Build")).toBeInTheDocument();
  });

  it("displays placeholder message for Epic 6", async () => {
    const Page = await BuildViewerPage({ params: { id: "test" } });
    render(Page);

    expect(screen.getByText(/build loading will be implemented/i)).toBeInTheDocument();
    expect(screen.getByText(/epic 6/i)).toBeInTheDocument();
  });

  it("uses fixed 3-column layout", async () => {
    const Page = await BuildViewerPage({ params: { id: "test" } });
    render(Page);

    // Check that grid is set to 3 columns (via data attribute)
    const main = screen.getByRole("main");
    const grid = main.querySelector("div[data-column-count]");
    expect(grid).toHaveAttribute("data-column-count", "3");
  });

  it("hides sidebar for shared builds", async () => {
    const Page = await BuildViewerPage({ params: { id: "test" } });
    render(Page);

    // Sidebar should not be present (showSidebar=false)
    expect(screen.queryByRole("complementary")).not.toBeInTheDocument();
  });
});
