/**
 * CharacterSummary - Display character info in MidsReborn format with edit mode
 * Epic 2.3 - Character Sheet Display
 *
 * Format: "{Name}: Level {level} {Origin} {Archetype} ({Primary} / {Secondary})"
 */

import { useState } from "react";
import { useCharacterStore } from "@/stores";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

export interface CharacterSummaryProps {
  mode?: "view" | "edit";
  className?: string;
}

export function CharacterSummary({
  mode = "view",
  className = "",
}: CharacterSummaryProps) {
  const {
    name,
    level,
    origin,
    archetype,
    primaryPowerset,
    secondaryPowerset,
    setName,
    setLevel,
  } = useCharacterStore();

  const [isEditing, setIsEditing] = useState(mode === "edit");
  const [editName, setEditName] = useState(name);
  const [editLevel, setEditLevel] = useState(level.toString());

  // MidsReborn format: "{Name}: Level {level} {Origin} {Archetype} ({Primary} / {Secondary})"
  const summaryText = `${name || "Unnamed"}: Level ${level} ${origin?.displayName || "Unknown"} ${archetype?.displayName || "Archetype"} (${primaryPowerset?.displayName || "None"} / ${secondaryPowerset?.displayName || "None"})`;

  const handleSave = () => {
    setName(editName);
    const newLevel = parseInt(editLevel, 10);
    if (!isNaN(newLevel) && newLevel >= 1 && newLevel <= 50) {
      setLevel(newLevel);
    }
    setIsEditing(false);
  };

  const handleCancel = () => {
    setEditName(name);
    setEditLevel(level.toString());
    setIsEditing(false);
  };

  if (isEditing) {
    return (
      <div className={`space-y-4 ${className}`}>
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <label
              htmlFor="character-name"
              className="text-sm font-medium leading-none"
            >
              Character Name
            </label>
            <Input
              id="character-name"
              value={editName}
              onChange={(e) => setEditName(e.target.value)}
              placeholder="Enter character name"
            />
          </div>
          <div className="space-y-2">
            <label
              htmlFor="character-level"
              className="text-sm font-medium leading-none"
            >
              Level
            </label>
            <Input
              id="character-level"
              type="number"
              min={1}
              max={50}
              value={editLevel}
              onChange={(e) => setEditLevel(e.target.value)}
            />
          </div>
        </div>
        <div className="flex gap-2">
          <Button variant="default" size="sm" onClick={handleSave}>
            Save
          </Button>
          <Button variant="outline" size="sm" onClick={handleCancel}>
            Cancel
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className={`flex items-center justify-between ${className}`}>
      <p className="text-lg font-semibold">{summaryText}</p>
      {mode === "edit" && (
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setIsEditing(true)}
        >
          <svg
            className="h-4 w-4 mr-2"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
            />
          </svg>
          Edit
        </Button>
      )}
    </div>
  );
}
