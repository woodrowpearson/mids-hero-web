/**
 * InherentPowersDisplay - Display archetype inherent powers
 * Epic 2.3 - Character Sheet Display
 *
 * Shows inherent powers list with icons and descriptions using useInherentPowers hook
 */

import { useInherentPowers } from "@/hooks";
import { LoadingSpinner } from "@/components/ui/LoadingSpinner";
import { ErrorMessage } from "@/components/ui/ErrorMessage";
import type { Archetype } from "@/types/character.types";

export interface InherentPowersDisplayProps {
  archetype: Archetype | null;
  className?: string;
}

export function InherentPowersDisplay({
  archetype,
  className = "",
}: InherentPowersDisplayProps) {
  const { data: inherentPowers, isLoading, error } = useInherentPowers(
    archetype?.id
  );

  if (!archetype) {
    return (
      <div className="text-sm text-muted-foreground py-4 text-center">
        Select an archetype to view inherent powers.
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-8">
        <LoadingSpinner />
      </div>
    );
  }

  if (error) {
    return (
      <ErrorMessage
        error={error instanceof Error ? error : new Error("Failed to load inherent powers")}
      />
    );
  }

  if (!inherentPowers || inherentPowers.length === 0) {
    return (
      <div className="text-sm text-muted-foreground py-4 text-center">
        No inherent powers for this archetype.
      </div>
    );
  }

  return (
    <div className={`space-y-2 ${className}`}>
      {inherentPowers.map((power) => (
        <div
          key={power.id}
          className="flex items-start gap-4 p-3 rounded-lg border bg-card hover:bg-accent transition-colors"
        >
          {/* Power Icon */}
          <div className="flex-shrink-0 w-12 h-12 rounded bg-muted flex items-center justify-center">
            {power.iconUrl ? (
              <img
                src={power.iconUrl}
                alt={power.displayName}
                className="w-full h-full rounded object-cover"
              />
            ) : (
              <svg
                className="w-6 h-6 text-muted-foreground"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M13 10V3L4 14h7v7l9-11h-7z"
                />
              </svg>
            )}
          </div>

          {/* Power Info */}
          <div className="flex-1 space-y-1 min-w-0">
            <h4 className="font-semibold text-sm">{power.displayName}</h4>
            {power.description && (
              <p className="text-sm text-muted-foreground line-clamp-2">
                {power.description}
              </p>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
