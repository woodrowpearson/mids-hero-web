/**
 * Keyboard shortcuts hook
 * Handles keyboard shortcuts for the application
 * TODO: Add undo/redo shortcuts when temporal middleware is implemented
 */

import { useEffect } from "react";

export function useKeyboardShortcuts() {
  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      // TODO: Implement undo/redo in future epic
      // // Undo: Ctrl/Cmd + Z
      // if ((e.metaKey || e.ctrlKey) && e.key === "z" && !e.shiftKey) {
      //   e.preventDefault();
      //   undo();
      // }

      // // Redo: Ctrl/Cmd + Shift + Z
      // if ((e.metaKey || e.ctrlKey) && e.key === "z" && e.shiftKey) {
      //   e.preventDefault();
      //   redo();
      // }

      // Future shortcuts can be added here:
      // - Ctrl/Cmd + S: Save build
      // - Ctrl/Cmd + O: Open build
      // - Ctrl/Cmd + K: Quick power search
      // - Escape: Close modals
    };

    window.addEventListener("keydown", handleKeyPress);

    return () => {
      window.removeEventListener("keydown", handleKeyPress);
    };
  }, []);
}
