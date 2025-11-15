import * as React from "react";

export function Footer() {
  return (
    <footer className="border-t border-border bg-mids-panel">
      <div className="container flex h-14 items-center justify-between text-sm text-muted-foreground">
        <p>
          © {new Date().getFullYear()} Mids Hero Web. Built for the City of
          Heroes community.
        </p>
        <div className="flex items-center space-x-4">
          <a
            href="https://github.com/your-repo"
            className="transition-colors hover:text-hero-cyan"
          >
            GitHub
          </a>
          <a
            href="/docs"
            className="transition-colors hover:text-hero-cyan"
          >
            Docs
          </a>
        </div>
      </div>
    </footer>
  );
}
