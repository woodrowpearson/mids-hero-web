/**
 * BuildLayout - Main layout wrapper for build editor
 * Epic 1.3: Layout Shell + Navigation
 *
 * Provides:
 * - Fixed top panel with character info and controls
 * - Optional collapsible sidebar
 * - Main content area with configurable CSS Grid (2-6 columns)
 * - Responsive breakpoints
 */

"use client";

import React from "react";
import { TopPanel } from "./TopPanel";
import { SidePanel } from "./SidePanel";
import { useUIStore } from "@/stores/uiStore";
import { cn } from "@/lib/utils";

export interface BuildLayoutProps {
  children: React.ReactNode;
  columnCount?: number; // Optional override, defaults to uiStore value
  showSidebar?: boolean; // Optional sidebar visibility
  className?: string;
}

export function BuildLayout({
  children,
  columnCount,
  showSidebar = true,
  className,
}: BuildLayoutProps) {
  const { columnLayout, sidebarCollapsed } = useUIStore();

  // Use prop override or store value
  const columns = columnCount ?? columnLayout;

  return (
    <div className="flex flex-col h-screen bg-background">
      {/* Top Panel - fixed at top */}
      <TopPanel />

      {/* Main content area */}
      <div className="flex flex-1 overflow-hidden">
        {/* Optional Left Sidebar */}
        {showSidebar && <SidePanel collapsed={sidebarCollapsed} />}

        {/* Main scrollable content with grid */}
        <main
          className={cn(
            "flex-1 overflow-y-auto p-6",
            className
          )}
        >
          <div
            className={cn(
              "grid gap-4 auto-rows-min",
              // Dynamic column classes based on column count
              // Mobile: Always 1 column
              "grid-cols-1",
              // Tablet: Max 3 columns
              columns >= 2 && "md:grid-cols-2",
              columns >= 3 && "lg:grid-cols-3",
              // Desktop: Full user control (2-6)
              columns === 4 && "xl:grid-cols-4",
              columns === 5 && "xl:grid-cols-5",
              columns === 6 && "2xl:grid-cols-6"
            )}
            data-column-count={columns}
          >
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
