#!/usr/bin/env python3
"""
Validation script for JSON import data

Checks imported data for:
- Required records present
- Data integrity
- Relationship consistency
- Common issues
"""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal
from app.models import Archetype, EnhancementSet, Power, Powerset


def validate_archetypes(db):
    """Validate archetype data"""
    print("\n=== Validating Archetypes ===")

    archetypes = db.query(Archetype).all()
    print(f"Total archetypes: {len(archetypes)}")

    issues = []
    for arch in archetypes:
        # Check required fields
        if not arch.name:
            issues.append(f"Archetype {arch.id} missing name")
        if not arch.display_name:
            issues.append(f"Archetype {arch.name} missing display_name")

        # Check source metadata
        if not arch.source_metadata:
            issues.append(f"Archetype {arch.name} missing source_metadata")

    if issues:
        print(f"❌ Found {len(issues)} issues:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("✅ All archetypes valid")

    return len(issues) == 0


def validate_enhancement_sets(db):
    """Validate enhancement set data"""
    print("\n=== Validating Enhancement Sets ===")

    sets = db.query(EnhancementSet).all()
    print(f"Total enhancement sets: {len(sets)}")

    issues = []
    for enh_set in sets:
        if not enh_set.name:
            issues.append(f"Enhancement set {enh_set.id} missing name")
        if enh_set.min_level and enh_set.max_level:
            if enh_set.min_level > enh_set.max_level:
                issues.append(f"Set {enh_set.name}: min_level > max_level")

    if issues:
        print(f"❌ Found {len(issues)} issues:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("✅ All enhancement sets valid")

    return len(issues) == 0


def validate_powersets(db):
    """Validate powerset data"""
    print("\n=== Validating Powersets ===")

    powersets = db.query(Powerset).all()
    print(f"Total powersets: {len(powersets)}")

    issues = []
    for ps in powersets:
        if not ps.name:
            issues.append(f"Powerset {ps.id} missing name")

        # Check archetype relationship
        if ps.archetype_id:
            archetype = db.query(Archetype).get(ps.archetype_id)
            if not archetype:
                issues.append(
                    f"Powerset {ps.name} references non-existent archetype {ps.archetype_id}"
                )

    if issues:
        print(f"❌ Found {len(issues)} issues:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("✅ All powersets valid")

    # Show distribution
    ps_with_arch = db.query(Powerset).filter(Powerset.archetype_id.isnot(None)).count()
    print(f"  Powersets with archetype: {ps_with_arch}/{len(powersets)}")

    return len(issues) == 0


def validate_powers(db):
    """Validate power data"""
    print("\n=== Validating Powers ===")

    powers = db.query(Power).all()
    print(f"Total powers: {len(powers)}")

    issues = []
    for power in powers:
        if not power.name:
            issues.append(f"Power {power.id} missing name")

        # Check powerset relationship
        if power.powerset_id:
            powerset = db.query(Powerset).get(power.powerset_id)
            if not powerset:
                issues.append(
                    f"Power {power.name} references non-existent powerset {power.powerset_id}"
                )

        # Check power_data
        if not power.power_data and not power.source_metadata:
            issues.append(
                f"Power {power.name} missing both power_data and source_metadata"
            )

    if issues:
        print(f"❌ Found {len(issues)} issues:")
        for issue in issues[:10]:  # Show first 10
            print(f"  - {issue}")
        if len(issues) > 10:
            print(f"  ... and {len(issues) - 10} more")
    else:
        print("✅ All powers valid")

    # Show distribution
    powers_with_ps = db.query(Power).filter(Power.powerset_id.isnot(None)).count()
    print(f"  Powers with powerset: {powers_with_ps}/{len(powers)}")

    return len(issues) == 0


def validate_relationships(db):
    """Validate cross-table relationships"""
    print("\n=== Validating Relationships ===")

    issues = []

    # Check archetype → powerset relationship
    archetypes = db.query(Archetype).all()
    for arch in archetypes:
        powersets = db.query(Powerset).filter_by(archetype_id=arch.id).all()
        if not powersets:
            issues.append(f"Archetype {arch.name} has no powersets")

    # Check powerset → power relationship
    powersets = db.query(Powerset).all()
    for ps in powersets:
        powers = db.query(Power).filter_by(powerset_id=ps.id).all()
        if not powers:
            issues.append(f"Powerset {ps.name} has no powers")

    if issues:
        print(f"⚠️  Found {len(issues)} relationship gaps:")
        for issue in issues[:5]:
            print(f"  - {issue}")
        if len(issues) > 5:
            print(f"  ... and {len(issues) - 5} more")
    else:
        print("✅ All relationships valid")

    return len(issues) == 0


def main():
    """Run all validations"""
    print("=" * 60)
    print("JSON Import Validation")
    print("=" * 60)

    db = SessionLocal()

    try:
        results = {
            "archetypes": validate_archetypes(db),
            "enhancement_sets": validate_enhancement_sets(db),
            "powersets": validate_powersets(db),
            "powers": validate_powers(db),
            "relationships": validate_relationships(db),
        }

        print("\n" + "=" * 60)
        print("Summary")
        print("=" * 60)

        all_valid = all(results.values())

        for check, valid in results.items():
            status = "✅ PASS" if valid else "❌ FAIL"
            print(f"{check:20s}: {status}")

        print("=" * 60)

        if all_valid:
            print("✅ All validations passed!")
            return 0
        else:
            print("❌ Some validations failed - review issues above")
            return 1

    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
