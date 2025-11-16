/**
 * Tests for ErrorMessage component
 */

import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ErrorMessage } from "@/components/ui/ErrorMessage";

describe("ErrorMessage", () => {
  it("renders error message with default title", () => {
    render(<ErrorMessage message="Something went wrong" />);

    expect(screen.getByText("Error")).toBeInTheDocument();
    expect(screen.getByText("Something went wrong")).toBeInTheDocument();
  });

  it("renders with custom title", () => {
    render(<ErrorMessage title="Custom Error" message="Test message" />);

    expect(screen.getByText("Custom Error")).toBeInTheDocument();
    expect(screen.getByText("Test message")).toBeInTheDocument();
  });

  it("shows retry button when onRetry is provided", () => {
    const onRetry = vi.fn();
    render(<ErrorMessage message="Error" onRetry={onRetry} />);

    expect(screen.getByText("Try Again")).toBeInTheDocument();
  });

  it("hides retry button when onRetry is not provided", () => {
    render(<ErrorMessage message="Error" />);

    expect(screen.queryByText("Try Again")).not.toBeInTheDocument();
  });

  it("calls onRetry when retry button is clicked", async () => {
    const user = userEvent.setup();
    const onRetry = vi.fn();
    render(<ErrorMessage message="Error" onRetry={onRetry} />);

    await user.click(screen.getByText("Try Again"));

    expect(onRetry).toHaveBeenCalledOnce();
  });

  it("displays error icon", () => {
    const { container } = render(<ErrorMessage message="Error" />);

    // lucide-react AlertCircle icon is rendered
    const icon = container.querySelector("svg");
    expect(icon).toBeInTheDocument();
  });
});
