/**
 * Empty state component
 * Displays when no data is available
 */

import { FileQuestion } from "lucide-react";

interface EmptyStateProps {
  title?: string;
  message: string;
  className?: string;
}

export function EmptyState({
  title = "No Data",
  message,
  className,
}: EmptyStateProps) {
  return (
    <div className={`flex flex-col items-center justify-center p-8 text-center ${className || ""}`}>
      <FileQuestion className="mb-4 h-12 w-12 text-muted-foreground" />
      <h3 className="mb-2 text-lg font-semibold text-foreground">{title}</h3>
      <p className="text-sm text-muted-foreground">{message}</p>
    </div>
  );
}
