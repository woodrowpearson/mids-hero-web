"use client";

import * as React from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";

export function TopNav() {
  return (
    <header className="sticky top-0 z-50 w-full border-b border-border bg-mids-panel backdrop-blur supports-[backdrop-filter]:bg-mids-panel/95">
      <div className="container flex h-14 items-center">
        <div className="mr-4 flex">
          <Link href="/" className="mr-6 flex items-center space-x-2">
            <span className="text-xl font-bold text-hero-cyan">
              Mids Hero Web
            </span>
          </Link>
          <nav className="flex items-center space-x-6 text-sm font-medium">
            <Link
              href="/builder"
              className="transition-colors hover:text-hero-cyan"
            >
              Builder
            </Link>
            <Link
              href="/browse"
              className="transition-colors hover:text-hero-cyan"
            >
              Browse Builds
            </Link>
          </nav>
        </div>
        <div className="flex flex-1 items-center justify-end space-x-2">
          <Button variant="outline" size="sm">
            Sign In
          </Button>
        </div>
      </div>
    </header>
  );
}
