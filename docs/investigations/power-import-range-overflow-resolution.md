# Power Import Range Overflow Issue - Resolution Summary

**Date**: 2025-11-12
**Status**: RESOLVED
**Issue**: Numeric field overflow errors during power import for powers with range=10000.0

## Problem

During power import, 12 errors occurred with the message:
```
numeric field overflow
DETAIL: A field with precision 6, scale 2 must round to an absolute value less than 10^4.
```

Powers affected included:
- Shadow_Recall (Inherent and Warshade versions)
- Incandescence variants (Destiny powers)

## Root Cause

The `powers.range` column was initially defined as `NUMERIC(6,2)`, which can only store values up to 9,999.99. Teleport powers and some Incarnate Destiny powers have a range of exactly 10,000.0, which exceeded this limit.

## Solution

Migration `362fd2d09d23_increase_powers_range_column_precision.py` was created on 2025-11-09 to:
- Increase `powers.range` from `NUMERIC(6,2)` to `NUMERIC(8,2)`
- This allows values up to 999,999.99

## Verification

Confirmed resolution by:
1. Checking database schema: `powers.range` is `NUMERIC(8,2)` ✓
2. Checking migration status: At head revision `362fd2d09d23` ✓
3. Querying database: 10 powers with range >= 10000 exist successfully ✓
4. Timestamp analysis: Powers were imported successfully at 16:55 UTC on 2025-11-09, after the migration

## Current State

- **Database**: Correctly configured with `NUMERIC(8,2)`
- **Powers Imported**: 2,273 powers total, including all 10 with range=10000.0
- **Migration**: Applied and working correctly
- **No Action Required**: Issue is already resolved

## Notes

The errors seen in background import logs were from an initial import attempt at 16:19 UTC (before the migration fix). A subsequent import at 16:55 UTC (after migration) succeeded completely. The errors were historical and do not represent a current problem.
