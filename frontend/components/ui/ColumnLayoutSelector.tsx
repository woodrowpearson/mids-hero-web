/**
 * ColumnLayoutSelector - Toggle for column count (2-6)
 * Epic 1.3: Layout Shell + Navigation
 *
 * NOTE: This is a placeholder. Full implementation in Task 5.
 */

"use client";

import { useUIStore } from "@/stores/uiStore";

export function ColumnLayoutSelector() {
  const { columnLayout, setColumnLayout } = useUIStore();

  return (
    <div className="flex items-center gap-1" role="group" aria-label="Column layout selector">
      <span className="text-xs text-muted-foreground mr-2">Columns:</span>
      {([2, 3, 4, 5, 6] as const).map((count) => (
        <button
          key={count}
          onClick={() => setColumnLayout(count)}
          className={`px-2 py-1 text-sm rounded ${
            columnLayout === count
              ? "bg-primary text-primary-foreground"
              : "bg-muted hover:bg-muted/80"
          }`}
          aria-pressed={columnLayout === count}
        >
          {count}
        </button>
      ))}
    </div>
  );
}
