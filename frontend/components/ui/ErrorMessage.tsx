/**
 * Error message component
 * Displays error with optional retry button
 */

import { Button } from "@/components/ui/button";
import { AlertCircle } from "lucide-react";

interface ErrorMessageProps {
  title?: string;
  message: string;
  onRetry?: () => void;
  className?: string;
}

export function ErrorMessage({
  title = "Error",
  message,
  onRetry,
  className,
}: ErrorMessageProps) {
  return (
    <div className={`flex flex-col items-center justify-center p-8 text-center ${className || ""}`}>
      <AlertCircle className="mb-4 h-12 w-12 text-destructive" />
      <h3 className="mb-2 text-lg font-semibold">{title}</h3>
      <p className="mb-4 text-sm text-muted-foreground">{message}</p>
      {onRetry && (
        <Button onClick={onRetry} variant="outline" size="sm">
          Try Again
        </Button>
      )}
    </div>
  );
}
