/**
 * PowersetSelector - Reusable base component for powerset dropdowns
 * Used by Primary, Secondary, Pool, and Ancillary selectors
 */

import React from "react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import type { Powerset } from "@/types/character.types";

export interface PowersetSelectorProps {
  powersets: Powerset[];
  selected: Powerset | null;
  onChange: (powerset: Powerset | null) => void;
  disabled?: boolean;
  placeholder?: string;
  label?: string;
  description?: string;
  allowClear?: boolean;
}

export function PowersetSelector({
  powersets,
  selected,
  onChange,
  disabled = false,
  placeholder = "Select a powerset",
  label,
  description,
  allowClear = false,
}: PowersetSelectorProps) {
  const handleValueChange = (value: string) => {
    if (value === "__clear__" && allowClear) {
      onChange(null);
      return;
    }

    const powerset = powersets.find((p) => p.id.toString() === value);
    onChange(powerset || null);
  };

  return (
    <div className="flex flex-col gap-2">
      {label && (
        <label className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
          {label}
        </label>
      )}

      <Select
        value={selected?.id.toString() || ""}
        onValueChange={handleValueChange}
        disabled={disabled}
      >
        <SelectTrigger className="w-full">
          <SelectValue placeholder={placeholder} />
        </SelectTrigger>
        <SelectContent>
          {allowClear && selected && (
            <SelectItem value="__clear__" className="text-muted-foreground italic">
              (Clear selection)
            </SelectItem>
          )}
          {powersets.map((powerset) => (
            <SelectItem key={powerset.id} value={powerset.id.toString()}>
              {powerset.displayName}
            </SelectItem>
          ))}
          {powersets.length === 0 && (
            <div className="py-6 text-center text-sm text-muted-foreground">
              No powersets available
            </div>
          )}
        </SelectContent>
      </Select>

      {description && (
        <p className="text-sm text-muted-foreground">{description}</p>
      )}

      {selected && selected.description && (
        <p className="text-xs text-muted-foreground italic">
          {selected.description}
        </p>
      )}
    </div>
  );
}
