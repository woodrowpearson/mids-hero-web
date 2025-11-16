/**
 * Builder Page - Main build editor
 * Epic 1.3: Layout Shell + Navigation
 *
 * Client-side page for creating and editing character builds
 */

"use client";

import { BuildLayout } from "@/components/layout/BuildLayout";
import { useUIStore } from "@/stores/uiStore";

export default function BuilderPage() {
  const { columnLayout, sidebarCollapsed } = useUIStore();

  return (
    <BuildLayout
      columnCount={columnLayout}
      showSidebar={!sidebarCollapsed}
    >
      {/* Empty state placeholder - Power selection in Epic 3 */}
      <div className="col-span-full flex items-center justify-center p-12 border-2 border-dashed border-muted-foreground/25 rounded-lg min-h-[400px]">
        <div className="text-center space-y-2">
          <h2 className="text-2xl font-semibold">Empty Build</h2>
          <p className="text-muted-foreground max-w-md">
            Power selection will be implemented in Epic 3.
            Use the controls above to test the layout.
          </p>
          <p className="text-sm text-muted-foreground/75 mt-4">
            Current layout: {columnLayout} columns
          </p>
        </div>
      </div>
    </BuildLayout>
  );
}
