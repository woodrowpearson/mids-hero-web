/**
 * Tests for PowersetSelectionPanel container
 */

import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { PowersetSelectionPanel } from "../PowersetSelectionPanel";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

// Create a wrapper with QueryClientProvider for tests
const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });

  const Wrapper = ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
  Wrapper.displayName = "QueryClientWrapper";
  return Wrapper;
};

describe("PowersetSelectionPanel", () => {
  it("renders all child components", () => {
    render(<PowersetSelectionPanel />, { wrapper: createWrapper() });

    // Check for main heading
    expect(screen.getByText("Powersets")).toBeInTheDocument();

    // Check for powerset selector labels
    expect(screen.getByText("Primary Powerset")).toBeInTheDocument();
    expect(screen.getByText("Secondary Powerset")).toBeInTheDocument();

    // Check for all 4 pool power slots
    expect(screen.getByText("Pool Power 1")).toBeInTheDocument();
    expect(screen.getByText("Pool Power 2")).toBeInTheDocument();
    expect(screen.getByText("Pool Power 3")).toBeInTheDocument();
    expect(screen.getByText("Pool Power 4")).toBeInTheDocument();

    // Check for ancillary powerset selector
    expect(screen.getByText(/Ancillary\/Epic Powerset/)).toBeInTheDocument();
  });

  it("displays helper text for powersets", () => {
    render(<PowersetSelectionPanel />, { wrapper: createWrapper() });

    // Check main description
    expect(
      screen.getByText(/Choose your character's power sources/i)
    ).toBeInTheDocument();

    // Check pool power description (on first pool selector)
    expect(
      screen.getByText(/Choose up to 4 pool power sets/i)
    ).toBeInTheDocument();

    // Check ancillary description
    expect(
      screen.getByText(/Choose an archetype to see available ancillary powersets/i)
    ).toBeInTheDocument();
  });
});
