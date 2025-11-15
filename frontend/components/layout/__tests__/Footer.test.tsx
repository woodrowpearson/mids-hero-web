import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { Footer } from "../Footer";

describe("Footer", () => {
  it("renders copyright text", () => {
    render(<Footer />);
    const currentYear = new Date().getFullYear();
    expect(
      screen.getByText(
        new RegExp(`© ${currentYear} Mids Hero Web`, "i")
      )
    ).toBeInTheDocument();
  });

  it("renders footer links", () => {
    render(<Footer />);
    expect(screen.getByText("GitHub")).toBeInTheDocument();
    expect(screen.getByText("Docs")).toBeInTheDocument();
  });
});
