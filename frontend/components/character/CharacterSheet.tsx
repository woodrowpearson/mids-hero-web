/**
 * CharacterSheet - Main container for character information display
 * Epic 2.3 - Character Sheet Display
 *
 * Displays character summary, archetype modifiers, caps, and inherent powers
 * Uses tabbed interface for organized display
 */

"use client";

import { useCharacterStore } from "@/stores";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { CharacterSummary } from "./CharacterSummary";
import { ATModifiersDisplay } from "./ATModifiersDisplay";
import { CapsDisplay } from "./CapsDisplay";
import { InherentPowersDisplay } from "./InherentPowersDisplay";

export interface CharacterSheetProps {
  mode?: "view" | "edit";
  className?: string;
}

export function CharacterSheet({
  mode = "view",
  className = "",
}: CharacterSheetProps) {
  const archetype = useCharacterStore((state) => state.archetype);

  return (
    <div className={`rounded-lg border bg-card shadow-sm ${className}`}>
      <div className="p-6 space-y-6">
        {/* Card Header */}
        <div className="space-y-1.5">
          <h3 className="text-2xl font-semibold leading-none tracking-tight">
            Character Sheet
          </h3>
          <p className="text-sm text-muted-foreground">
            View your character information, archetype stats, and inherent powers
          </p>
        </div>

        {/* Card Content */}
        <div className="space-y-6">
          {/* Character Summary */}
          <CharacterSummary mode={mode} />

          {/* Archetype Info Tabs */}
          <Tabs defaultValue="modifiers" className="w-full">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="modifiers">Base Modifiers</TabsTrigger>
              <TabsTrigger value="caps">Caps</TabsTrigger>
              <TabsTrigger value="inherents">Inherent Powers</TabsTrigger>
            </TabsList>

            <TabsContent value="modifiers" className="mt-4">
              <ATModifiersDisplay archetype={archetype} />
            </TabsContent>

            <TabsContent value="caps" className="mt-4">
              <CapsDisplay archetype={archetype} />
            </TabsContent>

            <TabsContent value="inherents" className="mt-4">
              <InherentPowersDisplay archetype={archetype} />
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  );
}
