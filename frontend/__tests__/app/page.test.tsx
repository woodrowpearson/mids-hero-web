/**
 * Tests for Home page
 * Epic 1.3: Layout Shell + Navigation
 */

import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import HomePage from "@/app/page";

describe("HomePage", () => {
  it("displays main heading", () => {
    render(<HomePage />);

    expect(screen.getByRole("heading", { name: /build your hero/i })).toBeInTheDocument();
  });

  it("displays description text", () => {
    render(<HomePage />);

    expect(screen.getByText(/modern web-based build planner/i)).toBeInTheDocument();
    expect(screen.getByText(/city of heroes/i)).toBeInTheDocument();
  });

  it("has Start Building button linking to /builder", () => {
    render(<HomePage />);

    const buildButton = screen.getByRole("link", { name: /start building/i });
    expect(buildButton).toHaveAttribute("href", "/builder");
  });

  it("has Browse Builds button linking to /browse", () => {
    render(<HomePage />);

    const browseButton = screen.getByRole("link", { name: /browse builds/i });
    expect(browseButton).toHaveAttribute("href", "/browse");
  });

  it("centers content vertically", () => {
    const { container } = render(<HomePage />);

    const mainContainer = container.firstChild as HTMLElement;
    expect(mainContainer).toHaveClass("items-center");
    expect(mainContainer).toHaveClass("justify-center");
  });
});
