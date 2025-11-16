/**
 * SidePanel - Optional collapsible left sidebar
 * Epic 1.3: Layout Shell + Navigation
 *
 * NOTE: This is a placeholder. Full implementation in Task 4.
 */

"use client";

import { cn } from "@/lib/utils";

export interface SidePanelProps {
  collapsed?: boolean;
}

export function SidePanel({ collapsed = false }: SidePanelProps) {
  return (
    <aside
      className={cn(
        "border-r bg-muted/10 transition-all duration-300",
        collapsed ? "w-0 overflow-hidden" : "w-[250px]"
      )}
      role="complementary"
      aria-hidden={collapsed}
    >
      {!collapsed && (
        <div className="p-4">
          <h2 className="font-semibold mb-4">Character Creation</h2>
          <p className="text-sm text-muted-foreground">
            Placeholder for Epic 2
          </p>
        </div>
      )}
    </aside>
  );
}
