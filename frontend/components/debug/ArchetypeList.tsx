/**
 * Debug component to test archetype data fetching
 * Demonstrates loading, error, and success states
 */

"use client";

import { useArchetypes } from "@/hooks";
import { LoadingState } from "@/components/ui/LoadingState";
import { ErrorMessage } from "@/components/ui/ErrorMessage";
import { EmptyState } from "@/components/ui/EmptyState";

export function ArchetypeList() {
  const { data: archetypes, isLoading, error, refetch } = useArchetypes();

  if (isLoading) {
    return <LoadingState message="Loading archetypes from backend..." />;
  }

  if (error) {
    return (
      <ErrorMessage
        title="Failed to Load Archetypes"
        message={error instanceof Error ? error.message : "An unknown error occurred"}
        onRetry={() => refetch()}
      />
    );
  }

  if (!archetypes || archetypes.length === 0) {
    return <EmptyState message="No archetypes found in database" />;
  }

  return (
    <div className="p-4">
      <h2 className="mb-4 text-xl font-bold">Archetypes ({archetypes.length})</h2>
      <p className="mb-4 text-sm text-muted-foreground">
        Data fetched from: <code>{process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"}</code>
      </p>
      <ul className="space-y-2">
        {archetypes.map((at) => (
          <li key={at.id} className="rounded border border-border bg-card p-3">
            <div className="font-semibold">{at.displayName}</div>
            <div className="text-xs text-muted-foreground">
              ID: {at.id} | Damage Scale: {at.damageScale} | Defense Cap: {at.defenseCap}%
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
