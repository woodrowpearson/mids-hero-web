/**
 * Tests for UIStore (Zustand)
 * Epic 1.2 + Epic 1.3
 */

import { describe, it, expect, beforeEach } from "vitest";
import { useUIStore } from "@/stores/uiStore";

describe("uiStore", () => {
  beforeEach(() => {
    // Reset store to initial state
    const store = useUIStore.getState();
    store.setColumnLayout(3);
    store.setSidebarCollapsed(false);
    store.setShowTotalsWindow(true);
    store.setShowSetBonusPanel(false);
    store.setTheme("dark");

    // Clear localStorage
    localStorage.clear();
  });

  describe("Column Layout (Epic 1.2)", () => {
    it("has default column layout of 3", () => {
      const { columnLayout } = useUIStore.getState();
      expect(columnLayout).toBe(3);
    });

    it("allows setting column layout within range (2-6)", () => {
      const store = useUIStore.getState();

      store.setColumnLayout(2);
      expect(useUIStore.getState().columnLayout).toBe(2);

      store.setColumnLayout(6);
      expect(useUIStore.getState().columnLayout).toBe(6);

      store.setColumnLayout(4);
      expect(useUIStore.getState().columnLayout).toBe(4);
    });

    it("persists column layout to localStorage", () => {
      const store = useUIStore.getState();
      store.setColumnLayout(5);

      // Wait for persistence
      const stored = localStorage.getItem("ui-preferences-storage");
      expect(stored).toBeTruthy();

      if (stored) {
        const parsed = JSON.parse(stored);
        expect(parsed.state.columnLayout).toBe(5);
      }
    });
  });

  describe("Sidebar State (Epic 1.3)", () => {
    it("has sidebar expanded by default", () => {
      const { sidebarCollapsed } = useUIStore.getState();
      expect(sidebarCollapsed).toBe(false);
    });

    it("allows setting sidebar collapsed state", () => {
      const store = useUIStore.getState();

      store.setSidebarCollapsed(true);
      expect(useUIStore.getState().sidebarCollapsed).toBe(true);

      store.setSidebarCollapsed(false);
      expect(useUIStore.getState().sidebarCollapsed).toBe(false);
    });

    it("toggles sidebar state", () => {
      const store = useUIStore.getState();

      // Initial state: expanded (false)
      expect(useUIStore.getState().sidebarCollapsed).toBe(false);

      // Toggle to collapsed
      store.toggleSidebar();
      expect(useUIStore.getState().sidebarCollapsed).toBe(true);

      // Toggle back to expanded
      store.toggleSidebar();
      expect(useUIStore.getState().sidebarCollapsed).toBe(false);
    });

    it("persists sidebar state to localStorage", () => {
      const store = useUIStore.getState();
      store.toggleSidebar();

      const stored = localStorage.getItem("ui-preferences-storage");
      expect(stored).toBeTruthy();

      if (stored) {
        const parsed = JSON.parse(stored);
        expect(parsed.state.sidebarCollapsed).toBe(true);
      }
    });
  });

  describe("Totals Window (Epic 1.2)", () => {
    it("has totals window visible by default", () => {
      const { showTotalsWindow } = useUIStore.getState();
      expect(showTotalsWindow).toBe(true);
    });

    it("allows toggling totals window visibility", () => {
      const store = useUIStore.getState();

      store.setShowTotalsWindow(false);
      expect(useUIStore.getState().showTotalsWindow).toBe(false);

      store.setShowTotalsWindow(true);
      expect(useUIStore.getState().showTotalsWindow).toBe(true);
    });
  });

  describe("Set Bonus Panel (Epic 1.2)", () => {
    it("has set bonus panel hidden by default", () => {
      const { showSetBonusPanel } = useUIStore.getState();
      expect(showSetBonusPanel).toBe(false);
    });

    it("allows toggling set bonus panel visibility", () => {
      const store = useUIStore.getState();

      store.setShowSetBonusPanel(true);
      expect(useUIStore.getState().showSetBonusPanel).toBe(true);

      store.setShowSetBonusPanel(false);
      expect(useUIStore.getState().showSetBonusPanel).toBe(false);
    });
  });

  describe("Theme (Epic 1.2)", () => {
    it("has dark theme by default", () => {
      const { theme } = useUIStore.getState();
      expect(theme).toBe("dark");
    });

    it("allows setting theme", () => {
      const store = useUIStore.getState();

      store.setTheme("light");
      expect(useUIStore.getState().theme).toBe("light");

      store.setTheme("dark");
      expect(useUIStore.getState().theme).toBe("dark");
    });

    it("persists theme to localStorage", () => {
      const store = useUIStore.getState();
      store.setTheme("light");

      const stored = localStorage.getItem("ui-preferences-storage");
      expect(stored).toBeTruthy();

      if (stored) {
        const parsed = JSON.parse(stored);
        expect(parsed.state.theme).toBe("light");
      }
    });
  });

  describe("Persistence", () => {
    it("persists all UI preferences to localStorage", () => {
      const store = useUIStore.getState();

      // Change all preferences
      store.setColumnLayout(4);
      store.setSidebarCollapsed(true);
      store.setShowTotalsWindow(false);
      store.setShowSetBonusPanel(true);
      store.setTheme("light");

      const stored = localStorage.getItem("ui-preferences-storage");
      expect(stored).toBeTruthy();

      if (stored) {
        const parsed = JSON.parse(stored);
        expect(parsed.state.columnLayout).toBe(4);
        expect(parsed.state.sidebarCollapsed).toBe(true);
        expect(parsed.state.showTotalsWindow).toBe(false);
        expect(parsed.state.showSetBonusPanel).toBe(true);
        expect(parsed.state.theme).toBe("light");
      }
    });
  });
});
