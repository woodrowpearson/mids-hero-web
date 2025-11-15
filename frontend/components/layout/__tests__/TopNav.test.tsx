import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { TopNav } from "../TopNav";

describe("TopNav", () => {
  it("renders the logo", () => {
    render(<TopNav />);
    expect(screen.getByText("Mids Hero Web")).toBeInTheDocument();
  });

  it("renders navigation links", () => {
    render(<TopNav />);
    expect(screen.getByText("Builder")).toBeInTheDocument();
    expect(screen.getByText("Browse Builds")).toBeInTheDocument();
  });

  it("renders sign in button", () => {
    render(<TopNav />);
    expect(screen.getByText("Sign In")).toBeInTheDocument();
  });
});
