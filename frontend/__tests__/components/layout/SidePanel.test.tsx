/**
 * Tests for SidePanel component
 * Epic 1.3: Layout Shell + Navigation
 */

import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { userEvent } from "@testing-library/user-event";
import { SidePanel } from "@/components/layout/SidePanel";

describe("SidePanel", () => {
  it("renders with default width when not collapsed", () => {
    render(<SidePanel collapsed={false} />);

    const sidebar = screen.getByRole("complementary");
    expect(sidebar).toHaveClass("w-[250px]");
    expect(sidebar).not.toHaveClass("w-0");
  });

  it("collapses to zero width when collapsed prop is true", () => {
    render(<SidePanel collapsed={true} />);

    const sidebar = screen.getByRole("complementary");
    expect(sidebar).toHaveClass("w-0");
    expect(sidebar).not.toHaveClass("w-[250px]");
  });

  it("shows placeholder content when expanded", () => {
    render(<SidePanel collapsed={false} />);

    expect(screen.getByText("Character Creation")).toBeInTheDocument();
    expect(screen.getByText(/placeholder for epic 2/i)).toBeInTheDocument();
  });

  it("hides content when collapsed", () => {
    render(<SidePanel collapsed={true} />);

    expect(screen.queryByText("Character Creation")).not.toBeInTheDocument();
  });

  it("has aria-hidden attribute when collapsed", () => {
    render(<SidePanel collapsed={true} />);

    const sidebar = screen.getByRole("complementary");
    expect(sidebar).toHaveAttribute("aria-hidden", "true");
  });

  it("does not have aria-hidden when expanded", () => {
    render(<SidePanel collapsed={false} />);

    const sidebar = screen.getByRole("complementary");
    expect(sidebar).toHaveAttribute("aria-hidden", "false");
  });

  it("has transition classes for smooth animation", () => {
    render(<SidePanel />);

    const sidebar = screen.getByRole("complementary");
    expect(sidebar).toHaveClass("transition-all");
    expect(sidebar).toHaveClass("duration-300");
  });

  it("has border and background styling", () => {
    render(<SidePanel />);

    const sidebar = screen.getByRole("complementary");
    expect(sidebar).toHaveClass("border-r");
    expect(sidebar).toHaveClass("bg-muted/10");
  });
});
