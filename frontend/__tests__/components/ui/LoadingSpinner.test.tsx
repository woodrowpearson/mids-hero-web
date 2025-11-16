/**
 * Tests for LoadingSpinner component
 */

import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { LoadingSpinner } from "@/components/ui/LoadingSpinner";

describe("LoadingSpinner", () => {
  it("renders with default size (md)", () => {
    render(<LoadingSpinner />);
    const spinner = screen.getByRole("status");
    expect(spinner).toBeInTheDocument();
    expect(spinner).toHaveClass("h-8", "w-8");
  });

  it("renders with small size", () => {
    render(<LoadingSpinner size="sm" />);
    const spinner = screen.getByRole("status");
    expect(spinner).toHaveClass("h-4", "w-4");
  });

  it("renders with large size", () => {
    render(<LoadingSpinner size="lg" />);
    const spinner = screen.getByRole("status");
    expect(spinner).toHaveClass("h-12", "w-12");
  });

  it("applies custom className", () => {
    render(<LoadingSpinner className="custom-class" />);
    const spinner = screen.getByRole("status");
    expect(spinner).toHaveClass("custom-class");
  });

  it("has accessibility attributes", () => {
    render(<LoadingSpinner />);
    const spinner = screen.getByRole("status");
    expect(spinner).toHaveAttribute("aria-label", "Loading");
  });
});
