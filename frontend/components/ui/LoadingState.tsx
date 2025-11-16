/**
 * Full-page loading state component
 * Displays spinner with loading message
 */

import { LoadingSpinner } from "./LoadingSpinner";

interface LoadingStateProps {
  message?: string;
  className?: string;
}

export function LoadingState({ message = "Loading...", className }: LoadingStateProps) {
  return (
    <div className={`flex flex-col items-center justify-center p-8 ${className || ""}`}>
      <LoadingSpinner size="lg" />
      <p className="mt-4 text-sm text-muted-foreground">{message}</p>
    </div>
  );
}
