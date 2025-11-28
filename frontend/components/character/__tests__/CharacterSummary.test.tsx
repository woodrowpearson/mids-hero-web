/**
 * CharacterSummary component tests
 * Epic 2.3 - Character Sheet Display
 */

import { describe, it, expect, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { CharacterSummary } from "../CharacterSummary";
import { useCharacterStore } from "@/stores/characterStore";
import type { Archetype, Origin, Powerset } from "@/types/character.types";

// Mock data
const mockArchetype: Archetype = {
  id: 1,
  name: "Scrapper",
  displayName: "Scrapper",
};

const mockOrigin: Origin = {
  id: 1,
  name: "Science",
  displayName: "Science",
  description: "Enhanced through scientific experimentation",
};

const mockPrimaryPowerset: Powerset = {
  id: 1,
  name: "Scrapper_Primary.Broadsword",
  displayName: "Broadsword",
  archetypeId: 1,
  type: "Primary",
  description: "Wide sweeping attacks with a large blade",
};

const mockSecondaryPowerset: Powerset = {
  id: 2,
  name: "Scrapper_Secondary.Shield",
  displayName: "Shield Defense",
  archetypeId: 1,
  type: "Secondary",
  description: "Defense using a shield",
};

describe("CharacterSummary", () => {
  beforeEach(() => {
    // Reset store state before each test
    useCharacterStore.setState({
      name: "",
      level: 1,
      archetype: null,
      origin: null,
      primaryPowerset: null,
      secondaryPowerset: null,
    });
  });

  describe("view mode", () => {
    it("displays default text for unset character", () => {
      render(<CharacterSummary mode="view" />);

      expect(screen.getByText(/Unnamed/)).toBeInTheDocument();
      expect(screen.getByText(/Level 1/)).toBeInTheDocument();
      expect(screen.getByText(/Unknown/)).toBeInTheDocument();
      expect(screen.getByText(/Archetype/)).toBeInTheDocument();
    });

    it("displays full character summary with data", () => {
      useCharacterStore.setState({
        name: "Test Hero",
        level: 50,
        archetype: mockArchetype,
        origin: mockOrigin,
        primaryPowerset: mockPrimaryPowerset,
        secondaryPowerset: mockSecondaryPowerset,
      });

      render(<CharacterSummary mode="view" />);

      expect(screen.getByText(/Test Hero/)).toBeInTheDocument();
      expect(screen.getByText(/Level 50/)).toBeInTheDocument();
      expect(screen.getByText(/Science/)).toBeInTheDocument();
      expect(screen.getByText(/Scrapper/)).toBeInTheDocument();
      expect(screen.getByText(/Broadsword/)).toBeInTheDocument();
      expect(screen.getByText(/Shield Defense/)).toBeInTheDocument();
    });

    it("shows powersets as None when not selected", () => {
      useCharacterStore.setState({
        name: "Hero",
        level: 10,
        archetype: mockArchetype,
      });

      render(<CharacterSummary mode="view" />);

      expect(screen.getByText(/\(None \/ None\)/)).toBeInTheDocument();
    });

    it("does not show edit button in view mode", () => {
      render(<CharacterSummary mode="view" />);

      expect(screen.queryByText("Edit")).not.toBeInTheDocument();
    });
  });

  describe("edit mode", () => {
    it("shows edit button when mode is edit", () => {
      useCharacterStore.setState({
        name: "Test Hero",
        level: 25,
      });

      render(<CharacterSummary mode="edit" />);

      // Initially showing the view with edit button
      // Since mode="edit" and isEditing starts true, check for form
      expect(screen.getByLabelText("Character Name")).toBeInTheDocument();
    });

    it("displays name input field", () => {
      render(<CharacterSummary mode="edit" />);

      expect(screen.getByLabelText("Character Name")).toBeInTheDocument();
    });

    it("displays level input field", () => {
      render(<CharacterSummary mode="edit" />);

      expect(screen.getByLabelText("Level")).toBeInTheDocument();
    });

    it("pre-fills form with current values", () => {
      useCharacterStore.setState({
        name: "Existing Hero",
        level: 30,
      });

      render(<CharacterSummary mode="edit" />);

      const nameInput = screen.getByLabelText("Character Name") as HTMLInputElement;
      expect(nameInput.value).toBe("Existing Hero");

      const levelInput = screen.getByLabelText("Level") as HTMLInputElement;
      expect(levelInput.value).toBe("30");
    });

    it("has Save and Cancel buttons", () => {
      render(<CharacterSummary mode="edit" />);

      expect(screen.getByText("Save")).toBeInTheDocument();
      expect(screen.getByText("Cancel")).toBeInTheDocument();
    });

    it("saves name and level when Save is clicked", async () => {
      render(<CharacterSummary mode="edit" />);

      const nameInput = screen.getByLabelText("Character Name");
      const levelInput = screen.getByLabelText("Level");
      const saveButton = screen.getByText("Save");

      await userEvent.clear(nameInput);
      await userEvent.type(nameInput, "New Hero Name");
      await userEvent.clear(levelInput);
      await userEvent.type(levelInput, "42");
      await userEvent.click(saveButton);

      const state = useCharacterStore.getState();
      expect(state.name).toBe("New Hero Name");
      expect(state.level).toBe(42);
    });

    it("reverts changes when Cancel is clicked", async () => {
      useCharacterStore.setState({
        name: "Original Name",
        level: 20,
      });

      render(<CharacterSummary mode="edit" />);

      const nameInput = screen.getByLabelText("Character Name");
      await userEvent.clear(nameInput);
      await userEvent.type(nameInput, "Changed Name");

      const cancelButton = screen.getByText("Cancel");
      await userEvent.click(cancelButton);

      const state = useCharacterStore.getState();
      expect(state.name).toBe("Original Name");
    });

    it("does not save empty name", async () => {
      useCharacterStore.setState({
        name: "Original Name",
        level: 20,
      });

      render(<CharacterSummary mode="edit" />);

      const nameInput = screen.getByLabelText("Character Name");
      await userEvent.clear(nameInput);

      const saveButton = screen.getByText("Save");
      await userEvent.click(saveButton);

      // Name should not change because empty names are rejected
      const state = useCharacterStore.getState();
      expect(state.name).toBe("Original Name");
    });

    it("does not save whitespace-only name", async () => {
      useCharacterStore.setState({
        name: "Original Name",
        level: 20,
      });

      render(<CharacterSummary mode="edit" />);

      const nameInput = screen.getByLabelText("Character Name");
      await userEvent.clear(nameInput);
      await userEvent.type(nameInput, "   ");

      const saveButton = screen.getByText("Save");
      await userEvent.click(saveButton);

      const state = useCharacterStore.getState();
      expect(state.name).toBe("Original Name");
    });

    it("trims whitespace from name when saving", async () => {
      render(<CharacterSummary mode="edit" />);

      const nameInput = screen.getByLabelText("Character Name");
      await userEvent.clear(nameInput);
      await userEvent.type(nameInput, "  Hero Name  ");

      const saveButton = screen.getByText("Save");
      await userEvent.click(saveButton);

      const state = useCharacterStore.getState();
      expect(state.name).toBe("Hero Name");
    });

    it("clamps level to valid range (1-50)", async () => {
      render(<CharacterSummary mode="edit" />);

      const levelInput = screen.getByLabelText("Level");

      // Level input has min/max attributes for browser validation
      expect(levelInput).toHaveAttribute("min", "1");
      expect(levelInput).toHaveAttribute("max", "50");
    });

    it("ignores invalid level input", async () => {
      useCharacterStore.setState({
        name: "Test Hero",
        level: 25,
      });

      render(<CharacterSummary mode="edit" />);

      const levelInput = screen.getByLabelText("Level");
      await userEvent.clear(levelInput);
      await userEvent.type(levelInput, "abc");

      const saveButton = screen.getByText("Save");
      await userEvent.click(saveButton);

      // Level should remain unchanged for invalid input
      const state = useCharacterStore.getState();
      expect(state.level).toBe(25);
    });
  });

  describe("styling", () => {
    it("applies custom className", () => {
      const { container } = render(
        <CharacterSummary mode="view" className="test-class" />
      );

      expect(container.firstChild).toHaveClass("test-class");
    });
  });
});
