/**
 * PowersetSelectionPanel - Container component for all powerset selectors
 * Composes Primary, Secondary, Pool (x4), and Ancillary selectors
 */

import { PrimaryPowersetSelector } from "./PrimaryPowersetSelector";
import { SecondaryPowersetSelector } from "./SecondaryPowersetSelector";
import { PoolPowerSelector } from "./PoolPowerSelector";
import { AncillarySelector } from "./AncillarySelector";

export function PowersetSelectionPanel() {
  return (
    <div className="flex flex-col gap-6 p-4">
      <div>
        <h2 className="text-xl font-semibold mb-4">Powersets</h2>
        <p className="text-sm text-muted-foreground mb-6">
          Choose your character&apos;s power sources. Primary and Secondary are required,
          while Pool and Ancillary/Epic powersets are optional.
        </p>
      </div>

      {/* Primary and Secondary Powersets */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <PrimaryPowersetSelector />
        <SecondaryPowersetSelector />
      </div>

      {/* Pool Powers and Ancillary */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Pool Powers Column */}
        <div className="flex flex-col gap-4">
          <PoolPowerSelector index={0} />
          <PoolPowerSelector index={1} />
          <PoolPowerSelector index={2} />
          <PoolPowerSelector index={3} />
        </div>

        {/* Ancillary/Epic Column */}
        <div className="flex flex-col gap-4">
          <AncillarySelector />
        </div>
      </div>
    </div>
  );
}
