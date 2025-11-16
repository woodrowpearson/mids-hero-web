/**
 * Zustand UI store for user preferences
 * Manages UI state (not part of character build data)
 */

import { create } from "zustand";
import { persist } from "zustand/middleware";

// UI Store state interface
export interface UIState {
  // Layout preferences
  columnLayout: 2 | 3 | 4 | 5 | 6; // Number of columns for power display
  showTotalsWindow: boolean;
  showSetBonusPanel: boolean;
  sidebarCollapsed: boolean; // Epic 1.3: Sidebar collapsed state

  // Theme preferences (future)
  theme: "dark" | "light";

  // Actions
  setColumnLayout: (columns: 2 | 3 | 4 | 5 | 6) => void;
  setShowTotalsWindow: (show: boolean) => void;
  setShowSetBonusPanel: (show: boolean) => void;
  setSidebarCollapsed: (collapsed: boolean) => void;
  toggleSidebar: () => void;
  setTheme: (theme: "dark" | "light") => void;
}

// Create UI store
export const useUIStore = create<UIState>()(
  persist(
    (set) => ({
      // Initial state
      columnLayout: 3, // Default to 3 columns
      showTotalsWindow: true,
      showSetBonusPanel: false,
      sidebarCollapsed: false, // Epic 1.3: Sidebar visible by default
      theme: "dark",

      // Actions
      setColumnLayout: (columns) => set({ columnLayout: columns }),
      setShowTotalsWindow: (show) => set({ showTotalsWindow: show }),
      setShowSetBonusPanel: (show) => set({ showSetBonusPanel: show }),
      setSidebarCollapsed: (collapsed) => set({ sidebarCollapsed: collapsed }),
      toggleSidebar: () => set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),
      setTheme: (theme) => set({ theme }),
    }),
    {
      name: "ui-preferences-storage",
    }
  )
);
