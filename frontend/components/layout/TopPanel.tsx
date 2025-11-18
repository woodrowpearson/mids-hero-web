/**
 * TopPanel - Fixed top header with character info and controls
 * Epic 1.3: Layout Shell + Navigation
 *
 * Displays:
 * - Character info (name, archetype, level)
 * - Action buttons (New, Save, Load, Export - placeholders)
 * - Column layout selector
 * - Settings icon
 */

"use client";

import { Button } from "@/components/ui/button";
import { useCharacterStore } from "@/stores/characterStore";
import { ColumnLayoutSelector } from "@/components/ui/ColumnLayoutSelector";

export function TopPanel() {
  const { name, archetype, level } = useCharacterStore();

  return (
    <header className="h-[77px] border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 sticky top-0 z-50">
      <div className="flex items-center justify-between px-6 h-full">
        {/* Left: Character Info */}
        <div className="flex items-center gap-4">
          <div className="flex flex-col">
            <span className="font-semibold text-lg">
              {name || "Unnamed Hero"}
            </span>
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <span>{archetype?.displayName || "No Archetype"}</span>
              <span>•</span>
              <span>Level {level}</span>
            </div>
          </div>
        </div>

        {/* Center: Primary Actions */}
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm">
            New
          </Button>
          <Button variant="outline" size="sm">
            Save
          </Button>
          <Button variant="outline" size="sm">
            Load
          </Button>
          <Button variant="outline" size="sm">
            Export
          </Button>
        </div>

        {/* Right: View Controls */}
        <div className="flex items-center gap-4">
          <ColumnLayoutSelector />
          <Button variant="ghost" size="icon" aria-label="Settings">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z" />
              <circle cx="12" cy="12" r="3" />
            </svg>
          </Button>
        </div>
      </div>
    </header>
  );
}
