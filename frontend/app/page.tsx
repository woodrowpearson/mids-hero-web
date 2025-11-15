import * as React from "react";
import { Button } from "@/components/ui/button";
import Link from "next/link";

export default function HomePage() {
  return (
    <div className="container flex min-h-[calc(100vh-7rem)] flex-col items-center justify-center space-y-8">
      <div className="flex flex-col items-center space-y-4 text-center">
        <h1 className="text-4xl font-bold tracking-tighter sm:text-5xl md:text-6xl lg:text-7xl">
          Build Your Hero
        </h1>
        <p className="max-w-[700px] text-lg text-muted-foreground sm:text-xl">
          Modern web-based build planner for City of Heroes. Create, share, and
          analyze character builds with the community.
        </p>
      </div>
      <div className="flex flex-col gap-2 sm:flex-row">
        <Button asChild size="lg" className="bg-hero-blue hover:bg-hero-cyan">
          <Link href="/builder">Start Building</Link>
        </Button>
        <Button asChild variant="outline" size="lg">
          <Link href="/browse">Browse Builds</Link>
        </Button>
      </div>
    </div>
  );
}
