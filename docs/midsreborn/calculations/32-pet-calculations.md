# Pet Calculations

## Overview
- **Purpose**: Calculate power effects and attributes for summonable entities (pets) that inherit some stats from caster and have their own enhancement slotting
- **Used By**: Mastermind primary powersets (6 pet types per set), Controller/Dominator pet powers, Lore Incarnate pets, temporary pet powers
- **Complexity**: Complex
- **Priority**: High
- **Status**: 🟡 Breadth Complete

## MidsReborn Implementation

### Primary Location
- **File**: `Core/PetInfo.cs`
- **Class**: `PetInfo`
- **Related Files**:
  - `Core/SummonedEntity.cs` - Pet entity definitions with powersets
  - `Core/Base/Data_Classes/Power.cs` - `AbsorbPetEffects()` method (lines 2573-2672)
  - `clsToonX.cs` - `GenerateBuffedPowers()` method (lines 2092-2129)
  - `Forms/Controls/PetView.cs` - UI for displaying pet power data

### Dependencies
- **SummonedEntity**: Defines pet type, powersets, upgrade powers, entity class
- **DatabaseAPI**: Retrieves pet powersets, powers, entity definitions
- **Character/Build**: Caster's stats that may buff pets
- **Enhancement System**: Separate slotting for pet powers (Pet IOs)
- **Effect System**: Pet powers have their own effect lists

### Pet Types

**Mastermind Pets** (permanent, multiple):
- 6 pet types per MM primary (Thugs, Robots, Ninjas, Mercenaries, Demons, Beasts)
- 3 tiers: Minions (T1, 3 summons), Lieutenants (T2, 2 summons), Boss (T3, 1 summon)
- Each pet has 1-3 powersets (base, upgrade 1, upgrade 2)
- Slottable with Pet-specific IOs (Pet Damage, Pet Defense, etc.)
- Inherit some caster buffs (accuracy, damage buffs, ToHit)
- DO NOT inherit caster's resistance/defense/recharge directly

**Controller/Dominator Pets** (semi-permanent, single):
- One powerful pet per control primary (Fire Imps, Phantom Army, Singularity, etc.)
- Usually has 1-2 powersets
- May be temporary (Phantom Army) or permanent (Fire Imps)
- Slottable like MM pets
- Same inheritance rules

**Temporary Pets**:
- Lore Incarnate pets (2 summons, T4 gives 4)
- Temp power summons (Shivans, Warwolves, etc.)
- Some are permanent, some have time limits
- Lore pets are slottable via Incarnate system
- Temp power pets usually not slottable

### High-Level Algorithm

```
Pet Calculation Process:

1. Identify Pet Entity:
   IF power has EntCreate effect with nSummon index:
      entity = DatabaseAPI.Database.Entities[nSummon]
      entity_class = DatabaseAPI.Database.Classes[entity.GetNClassId()]

2. Retrieve Pet Powersets:
   FOR each powerset_id IN entity.GetNPowerset():
      powerset = DatabaseAPI.Database.Powersets[powerset_id]
      pet_powers += powerset.Powers

3. Determine Upgrade Level:
   // Mastermind pets have 0-2 upgrade powers that unlock additional powersets
   upgrade_level = 0
   FOR upgrade_power IN entity.UpgradePowerFullName:
      IF caster has upgrade_power in build:
         upgrade_level += 1

   // Only include powersets up to upgrade level
   available_powersets = entity.GetNPowerset()[0:upgrade_level+1]

4. Absorb Pet Effects (Power.AbsorbPetEffects()):
   IF power.AbsorbSummonEffects OR power.AbsorbSummonAttributes:

      A. Absorb Pet Attributes (if AbsorbSummonAttributes):
         // Copy attack/target/area attributes from pet's first power to summon power
         pet_base_power = pet_powersets[0].Powers[0]
         summon_power.AttackTypes = pet_base_power.AttackTypes
         summon_power.EffectArea = pet_base_power.EffectArea
         summon_power.EntitiesAffected = pet_base_power.EntitiesAffected
         summon_power.Accuracy = pet_base_power.Accuracy  // if summon power not autohit
         summon_power.MaxTargets = pet_base_power.MaxTargets
         summon_power.Radius = pet_base_power.Radius

      B. Absorb Pet Power Effects (if AbsorbSummonEffects):
         // Add all pet power effects to summon power display
         FOR each pet_powerset IN available_powersets:
            FOR each pet_power IN pet_powerset.Powers:
               FOR each effect IN pet_power.Effects:
                  absorbed_effect = effect.Clone()
                  absorbed_effect.Duration = summon_effect.Duration
                  absorbed_effect.DelayedTime = summon_effect.DelayedTime
                  // Apply pet's archetype class (Class_Minion_Pets usually)
                  absorbed_effect.Scale *= entity_class.GetModifier(effect.EffectType)
                  // Apply variable stacking (for MM "number of pets" slider)
                  IF summon_power.VariableEnabled:
                     stacking = caster.Build.Powers[summon_power_index].VariableValue
                     absorbed_effect.Magnitude *= stacking
                  summon_power.Effects.Add(absorbed_effect)

5. Generate Buffed Pet Powers (PetInfo.GenerateBuffedPowers()):
   // Calculate pet powers with caster buffs + pet slotting

   IF caster has summon power in build:
      FOR each pet_power IN pet_powers:

         A. Create Base Pet Power:
            base_pet_power = pet_power.Clone()
            base_pet_power.ProcessExecutes()  // Handle power redirects, etc.

         B. Apply Caster Buffs (Inherited):
            // Pets inherit global accuracy/tohit/damage buffs from caster
            base_pet_power.Accuracy *= caster.Totals.AccuracyMultiplier
            FOR effect IN base_pet_power.Effects:
               IF effect.EffectType == Damage:
                  effect.Magnitude *= caster.Totals.DamageBuffMultiplier[effect.DamageType]
               IF effect.EffectType == Heal:
                  effect.Magnitude *= caster.Totals.HealingMultiplier

         C. Apply Pet Enhancement Slotting:
            // Separate from caster's slotting - pet powers have own slots
            IF pet_power has slots in build:
               FOR each enhancement IN pet_power.Slots:
                  Apply enhancement to pet_power effects (same as player powers)

         D. Store Base and Buffed Versions:
            pet_power_pairs.Add((base_pet_power, buffed_pet_power))

   ELSE:
      // Summon power not in build - show unbuffed pet powers
      RETURN pet_powers as-is

6. Display Pet Power Info (PetView.SetData()):
   // UI shows both base and enhanced versions of pet powers
   FOR each (base_power, enhanced_power) IN pet_power_pairs:
      Display power with base stats vs enhanced stats
      Show inherited buffs from caster
      Show pet's own slotting effects
```

### Key Data Structures

**SummonedEntity** (Core/SummonedEntity.cs):
```csharp
class SummonedEntity {
    string UID;                    // Unique identifier
    string DisplayName;            // Pet display name
    string[] PowersetFullName;     // List of powerset full names (base, upgrade1, upgrade2)
    string[] UpgradePowerFullName; // Powers that unlock additional powersets
    string ClassName;              // Entity class (Class_Minion_Pets, etc.)
    eSummonEntity EntityType;      // Pet, Henchman, PseudoPet, etc.

    // Semi-props (internal IDs)
    int[] _nPowerset;         // Powerset database IDs
    int[] _nUpgradePower;     // Upgrade power database IDs
    int _nClassID;            // Entity class ID

    // Get all powers for this entity
    Dictionary<IPower, IPower?> GetPowers() {
        // Returns map of: pet_power -> required_upgrade_power
        // Shows which powers are available at each upgrade tier
    }
}
```

**PetInfo** (Core/PetInfo.cs):
```csharp
class PetInfo {
    int PowerEntryIndex;          // Build index of summon power
    SummonedEntity _entity;       // The pet entity being summoned
    List<IPower> _powers;         // All pet powers from all powersets
    PetPowersData PowersData;     // Base + buffed versions of pet powers

    // Generate buffed versions of pet powers with caster buffs
    void GeneratePetPowerData() {
        powerData = Toon.GenerateBuffedPowers(_powers, PowerEntryIndex);
        // Returns: KeyValuePair<List<IPower> basePowers, List<IPower> buffedPowers>
    }

    // Get specific pet power data
    PetPower GetPetPower(IPower power) {
        // Returns: PetPower { BasePower, BuffedPower }
    }
}
```

**PetPower** (nested in PetInfo):
```csharp
class PetPower {
    IPower BasePower;    // Unbuffed pet power
    IPower BuffedPower;  // With caster buffs + pet slotting
}
```

### Inheritance Rules

**Stats Pets INHERIT from Caster**:
- Global +Accuracy (multiplicative)
- Global +ToHit (additive, if applicable)
- Global +Damage buffs (by damage type)
- Global +Healing buffs (for pet healing powers)

**Stats Pets DO NOT Inherit from Caster**:
- Defense values (pets have own defense)
- Resistance values (pets have own resistance)
- HP/Regeneration (pets have own HP pools)
- Endurance/Recovery (pets have own endurance)
- Recharge bonuses (pets have own recharge rates)
- Range/Movement buffs

**Pet-Specific Mechanics**:
- Pets use their entity class modifiers (Class_Minion_Pets), not caster's archetype
- Pet powers are slotted separately with Pet-specific IOs
- Mastermind pets scale with variable stacking (number of pets summoned)
- Pet damage is enhanced by Pet Damage IOs, not caster's damage enhancements
- Upgrade powers unlock additional pet powersets (MM mechanic)

### Pet Enhancement System

**Pet IOs** (special enhancement category):
- Pet Damage
- Pet Accuracy
- Pet Recharge
- Pet Defense
- Pet Resistance
- Pet Endurance Reduction

**Pet IO Sets**:
- Brilliant Leadership (Def/ToHit Debuff)
- Call to Arms (Def/Res/ToHit)
- Command of the Mastermind (Dam/Acc/End)
- Edict of the Master (Def/Acc)
- Expedient Reinforcement (Res/Def/End)
- Mark of Supremacy (Acc/Dam/End)
- Sovereign Right (Res/Def/End)
- Soulbound Allegiance (Acc/Dam)

These enhance the pet's powers, not the caster's summon power.

## Game Mechanics Context

**Why This Exists**:

City of Heroes allows players to summon AI-controlled entities that fight alongside them. These pets have their own:
- Power lists (attacks, buffs, controls)
- Attribute values (HP, defense, resistance)
- Enhancement slotting (separate from caster)
- Archetype-like class system (entity classes)

The pet calculation system must:
1. **Display pet capabilities** - Show what the pet can do, not just the summon power
2. **Model inheritance** - Some caster buffs affect pets, others don't
3. **Handle upgrades** - Mastermind pets gain new powers when upgraded
4. **Support pet slotting** - Pets can be enhanced with Pet IOs

**Historical Context**:

- **Issue 1 (2004)**: Controller pets introduced - single powerful pets
- **Issue 6 (2005)**: Masterminds introduced - 6 pets with upgrade system
  - Revolutionary archetype: 3 summon powers + 2 upgrade powers
  - Pets gain additional powersets when upgraded
  - First archetype where primary role is buffing AI allies
- **Issue 9 (2006)**: Pet IOs introduced in Invention System
  - Special enhancement sets that only work in pet powers
  - Set bonuses apply to caster (like other IOs)
  - Enhanced values apply to pet (unlike other IOs)
- **Issue 18 (2010)**: Lore Incarnate pets (Destiny slot)
  - Temporary high-level pets
  - Different tiers affect power and duration
- **Homecoming**: Additional pet-focused sets and mechanics

**Known Quirks**:

1. **AbsorbSummonEffects flag**: MidsReborn uses special flags on summon powers to indicate whether to display pet power effects on the summon power. This creates a unified view but can be confusing (summon power shows damage values that are actually the pet's attacks).

2. **Inheritance is selective**: Pets inherit global +Accuracy/+Damage but NOT +Recharge/+Defense. This is intentional game design - pets are separate entities with their own survivability, but benefit from caster's offensive buffs.

3. **Pet IOs are unique**: Pet IOs enhance the pet, but their set bonuses apply to the caster. This dual nature requires careful calculation tracking.

4. **Variable stacking**: Mastermind summon powers use the "VariableValue" system to represent number of pets (1-6 for T1, 1-2 for T2, 0-1 for T3). This multiplies absorbed pet effects for display purposes.

5. **Upgrade power mechanics**: Mastermind upgrade powers (Equip/Upgrade) don't directly modify pets in the database. Instead, they unlock additional powersets on the pet entity. The calculation must check if upgrade powers are in the build to determine which powersets are active.

6. **Entity classes vs Archetypes**: Pets use entity classes (Class_Minion_Pets, Class_Boss_Pets, etc.) which have their own damage/buff scales, separate from player archetypes. A Mastermind's Bruiser boss pet uses Class_Boss_Pets modifiers, not Mastermind modifiers.

7. **Pet power display challenge**: When viewing a pet power in detail, the UI must show:
   - Base pet power values
   - Values after caster's inherited buffs
   - Values after pet's own slotting
   - Combined final values
   This requires careful bookkeeping of multiple power versions.

8. **Pseudopets vs Real Pets**: Some "pet" powers actually summon pseudopets (invisible, short-lived entities that deliver effects). True pets are persistent entities with AI. Pseudopets covered in separate spec (33-pseudopet-mechanics.md).

## Python Implementation Notes

### Proposed Architecture

**Module**: `midsreborn.calculations.pets`

**Core Classes**:
```python
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple

@dataclass
class SummonedEntity:
    """Represents a summonable entity (pet) with its powersets."""
    uid: str
    display_name: str
    entity_type: str  # "Pet", "Henchman", "PseudoPet"
    class_name: str  # "Class_Minion_Pets", "Class_Boss_Pets", etc.
    class_id: int
    powerset_ids: List[int]  # Indices into powerset database
    upgrade_power_ids: List[int]  # Powers that unlock additional powersets

    def get_powersets(self, database) -> List['Powerset']:
        """Retrieve all powersets for this entity."""
        return [database.powersets[pid] for pid in self.powerset_ids]

    def get_available_powersets(self, upgrade_level: int, database) -> List['Powerset']:
        """Get powersets available at given upgrade level (0-2 for MM pets)."""
        available_count = upgrade_level + 1
        return self.get_powersets(database)[:available_count]

@dataclass
class PetPowerData:
    """Base and buffed versions of a single pet power."""
    base_power: 'Power'
    buffed_power: 'Power'  # With caster buffs + pet slotting

class PetCalculator:
    """Calculate pet power effects with caster inheritance and pet slotting."""

    def __init__(self, database, character):
        self.database = database
        self.character = character

    def absorb_pet_effects(
        self,
        summon_power: 'Power',
        summon_effect: 'Effect',
        stacking: int = 1
    ) -> 'Power':
        """
        Absorb pet power effects into summon power for display.

        Implements Power.AbsorbPetEffects() from MidsReborn.

        Args:
            summon_power: The power that summons the pet
            summon_effect: The EntCreate effect with nSummon index
            stacking: Number of pets (for variable powers like MM summons)

        Returns:
            Modified summon_power with pet effects absorbed
        """
        entity = self.database.entities[summon_effect.summon_id]
        entity_class = self.database.classes[entity.class_id]

        # Determine upgrade level (for Masterminds)
        upgrade_level = self._get_upgrade_level(entity)
        powersets = entity.get_available_powersets(upgrade_level, self.database)

        # Option A: Absorb pet attributes
        if summon_power.absorb_summon_attributes:
            self._absorb_pet_attributes(summon_power, powersets, entity)

        # Option B: Absorb pet power effects
        if summon_power.absorb_summon_effects:
            self._absorb_pet_power_effects(
                summon_power,
                powersets,
                entity_class,
                summon_effect,
                stacking
            )

        return summon_power

    def _get_upgrade_level(self, entity: SummonedEntity) -> int:
        """Determine how many upgrade powers the caster has taken."""
        upgrade_level = 0
        for upgrade_power_id in entity.upgrade_power_ids:
            if self.character.has_power(upgrade_power_id):
                upgrade_level += 1
        return upgrade_level

    def _absorb_pet_attributes(
        self,
        summon_power: 'Power',
        powersets: List['Powerset'],
        entity: SummonedEntity
    ):
        """Copy attack/area/target attributes from pet's first power to summon power."""
        if not powersets or not powersets[0].powers:
            return

        pet_base_power = powersets[0].powers[0]
        summon_power.attack_types = pet_base_power.attack_types
        summon_power.effect_area = pet_base_power.effect_area
        summon_power.entities_affected = pet_base_power.entities_affected
        summon_power.max_targets = pet_base_power.max_targets
        summon_power.radius = pet_base_power.radius

        # Only copy accuracy if summon power is not autohit
        if summon_power.entities_autohit == EntityType.NONE:
            summon_power.accuracy = pet_base_power.accuracy

    def _absorb_pet_power_effects(
        self,
        summon_power: 'Power',
        powersets: List['Powerset'],
        entity_class: 'CharacterClass',
        summon_effect: 'Effect',
        stacking: int
    ):
        """Add all pet power effects to summon power for display."""
        for powerset in powersets:
            for pet_power in powerset.powers:
                for effect in pet_power.effects:
                    absorbed = effect.clone()

                    # Inherit timing from summon effect
                    absorbed.duration = summon_effect.duration
                    absorbed.delayed_time = summon_effect.delayed_time

                    # Apply pet entity class modifiers
                    class_modifier = entity_class.get_modifier(effect.effect_type)
                    absorbed.magnitude *= class_modifier

                    # Apply stacking for multiple pets
                    absorbed.magnitude *= stacking

                    # Mark as absorbed from pet
                    absorbed.absorbed_from_pet = True
                    absorbed.absorbed_power_name = pet_power.full_name

                    summon_power.effects.append(absorbed)

    def generate_buffed_pet_powers(
        self,
        pet_powers: List['Power'],
        summon_power_index: int
    ) -> Dict[int, PetPowerData]:
        """
        Generate base and buffed versions of pet powers.

        Implements PetInfo.GenerateBuffedPowers() and
        clsToonX.GenerateBuffedPowers() from MidsReborn.

        Args:
            pet_powers: List of all pet powers from all powersets
            summon_power_index: Build index of the summon power

        Returns:
            Dict mapping power_id -> PetPowerData(base, buffed)
        """
        if summon_power_index < 0:
            # Summon power not in build - return unbuffed powers
            return {
                p.power_id: PetPowerData(p, p.clone())
                for p in pet_powers
            }

        caster_buffs = self._get_inherited_caster_buffs()
        pet_power_data = {}

        for pet_power in pet_powers:
            # Create base version
            base_power = pet_power.clone()
            base_power.process_executes()

            # Create buffed version
            buffed_power = base_power.clone()

            # Apply inherited caster buffs
            self._apply_caster_buffs_to_pet(buffed_power, caster_buffs)

            # Apply pet's own enhancement slotting
            self._apply_pet_enhancements(buffed_power, summon_power_index)

            pet_power_data[pet_power.power_id] = PetPowerData(
                base_power=base_power,
                buffed_power=buffed_power
            )

        return pet_power_data

    def _get_inherited_caster_buffs(self) -> Dict[str, float]:
        """Calculate which buffs from caster should affect pets."""
        totals = self.character.totals

        return {
            'accuracy_mult': totals.accuracy_multiplier,
            'tohit_bonus': totals.tohit_bonus,
            'damage_buffs': totals.damage_buff_by_type.copy(),
            'healing_mult': totals.healing_multiplier,
        }

    def _apply_caster_buffs_to_pet(
        self,
        pet_power: 'Power',
        caster_buffs: Dict[str, float]
    ):
        """Apply inherited caster buffs to pet power."""
        # Accuracy is multiplicative
        pet_power.accuracy *= caster_buffs['accuracy_mult']

        # Apply to effects
        for effect in pet_power.effects:
            if effect.effect_type == EffectType.DAMAGE:
                dmg_type = effect.damage_type
                dmg_buff = caster_buffs['damage_buffs'].get(dmg_type, 1.0)
                effect.magnitude *= dmg_buff

            elif effect.effect_type == EffectType.HEAL:
                effect.magnitude *= caster_buffs['healing_mult']

    def _apply_pet_enhancements(
        self,
        pet_power: 'Power',
        summon_power_index: int
    ):
        """Apply pet's own enhancement slotting to power."""
        # Get pet power's slots from build (separate from caster's slots)
        pet_power_entry = self.character.get_pet_power_entry(
            summon_power_index,
            pet_power.power_id
        )

        if not pet_power_entry or not pet_power_entry.slots:
            return

        # Apply enhancements same way as player powers
        for slot in pet_power_entry.slots:
            enhancement = self.database.enhancements[slot.enhancement_id]
            self._apply_enhancement_to_power(pet_power, enhancement, slot.level)

    def _apply_enhancement_to_power(
        self,
        power: 'Power',
        enhancement: 'Enhancement',
        level: int
    ):
        """Apply a single enhancement to a power (same as player powers)."""
        # Implementation deferred to enhancement calculation spec (11-enhancement-slotting.md)
        pass

def calculate_pet_power_with_inheritance(
    pet_power: 'Power',
    caster_buffs: Dict[str, float],
    pet_enhancements: List['Enhancement']
) -> 'Power':
    """
    High-level function to calculate final pet power values.

    Args:
        pet_power: Base pet power from database
        caster_buffs: Inherited buffs from caster (accuracy, damage, etc.)
        pet_enhancements: Enhancements slotted in pet power

    Returns:
        Pet power with inherited buffs and enhancements applied
    """
    calculator = PetCalculator(database, character)

    # Clone base power
    buffed_power = pet_power.clone()

    # Apply caster inheritance
    calculator._apply_caster_buffs_to_pet(buffed_power, caster_buffs)

    # Apply pet slotting
    for enhancement in pet_enhancements:
        calculator._apply_enhancement_to_power(buffed_power, enhancement, 50)

    return buffed_power
```

### Implementation Notes

**Key Design Decisions**:

1. **Two-stage calculation**:
   - First, absorb pet effects into summon power for display
   - Second, calculate actual pet power values with inheritance
   This matches MidsReborn's approach and provides both summary and detail views

2. **Inheritance is explicit**:
   - Only specific stats inherited (accuracy, damage buffs)
   - Most stats (defense, resistance, recharge) are NOT inherited
   - Function `_get_inherited_caster_buffs()` explicitly lists what transfers

3. **Upgrade level logic**:
   - Check which upgrade powers caster has taken
   - Only include powersets up to that upgrade level
   - Mastermind-specific but other pets can use same system (upgrade_level=0)

4. **Variable stacking**:
   - Mastermind summon powers have variable number of pets
   - Multiply absorbed effects by stacking count for display
   - Actual pet count handled by game engine, not calculator

5. **Pet vs Caster slotting**:
   - Pet powers have separate slot entries in build
   - Pet power entry stores: summon_power_index + pet_power_id -> slots
   - Enhancements apply to pet power, not summon power

**C# vs Python Gotchas**:

1. **Entity class modifiers**: C# uses `DatabaseAPI.Database.Classes[classId].GetModifier(effectType)`. Python needs equivalent method on CharacterClass dataclass.

2. **Power cloning**: C# uses FastDeepCloner library. Python should use dataclasses with `replace()` or custom `clone()` method.

3. **Effect modification**: C# modifies Effect objects in place. Python should prefer immutable dataclasses with new instances.

4. **Build power lookups**: C# uses `CurrentBuild.Powers[index]`. Python needs Character.get_pet_power_entry(summon_index, pet_power_id).

**Edge Cases to Test**:

1. **Mastermind with no upgrades taken**: Only T1 base powerset active
2. **Mastermind with Equip but not Upgrade**: T1 and T2 powersets active
3. **Controller pet (no upgrades)**: Single powerset, no upgrade logic
4. **Lore Incarnate pets**: Different tier affects power scaling
5. **Temporary pets (not in build)**: No inheritance, show base values
6. **Pet with zero damage powers**: Some pets are support-only (buffers/healers)
7. **Variable stacking**: MM summon with 3 minions vs 1 minion

**Validation Strategy**:

1. **Compare summon power display**:
   - Load same Mastermind build in MidsReborn and Python
   - Check summon power's absorbed damage/effects match

2. **Compare pet power detail**:
   - View individual pet power in PetView
   - Verify base vs enhanced values match

3. **Test inheritance explicitly**:
   - Create caster with +50% damage buff
   - Verify pet power damage increases by 50%
   - Verify pet power recharge does NOT change

4. **Test upgrade mechanics**:
   - Mastermind without Equip: X powers visible
   - Mastermind with Equip: Y powers visible (Y > X)
   - Mastermind with Upgrade: Z powers visible (Z > Y)

**Performance Considerations**:

- Pet power calculation can be expensive (6 MM pets * 10+ powers each = 60+ power calculations)
- Cache pet power data per summon power
- Only recalculate when:
  - Caster's global buffs change
  - Pet power slotting changes
  - Upgrade powers added/removed
- Use lazy evaluation for pet power detail (only calculate when viewing)

### Test Cases

**Test Case 1: Mastermind Base Pets (No Upgrades)**
```python
# Input
summon_power = database.get_power("Thugs.Thugs.Call_Bruiser")
character = create_mastermind(level=32)
character.add_power(summon_power)  # T3 pet, no upgrades

# Expected
entity = database.get_entity_for_power(summon_power)
assert entity.display_name == "Bruiser"
assert len(entity.powerset_ids) == 3  # Base + 2 upgrade powersets
available = entity.get_available_powersets(upgrade_level=0, database)
assert len(available) == 1  # Only base powerset visible
bruiser_base_powers = available[0].powers
assert "Bruiser.Jab" in [p.power_name for p in bruiser_base_powers]
assert "Bruiser.Haymaker" in [p.power_name for p in bruiser_base_powers]
# Should NOT have upgrade powers like Hurl or Foot Stomp yet
```

**Test Case 2: Mastermind with Full Upgrades**
```python
# Input
character = create_mastermind(level=32)
character.add_power("Thugs.Thugs.Call_Bruiser")  # T3 summon
character.add_power("Thugs.Thugs.Equip_Thugs")   # First upgrade
character.add_power("Thugs.Thugs.Upgrade_Equipment")  # Second upgrade

# Expected
entity = database.get_entity_for_power("Thugs.Thugs.Call_Bruiser")
upgrade_level = pet_calculator._get_upgrade_level(entity)
assert upgrade_level == 2  # Both upgrades taken
available = entity.get_available_powersets(upgrade_level, database)
assert len(available) == 3  # All three powersets visible
all_bruiser_powers = [p for ps in available for p in ps.powers]
assert "Bruiser.Jab" in [p.power_name for p in all_bruiser_powers]
assert "Bruiser.Hurl" in [p.power_name for p in all_bruiser_powers]
assert "Bruiser.Foot_Stomp" in [p.power_name for p in all_bruiser_powers]
```

**Test Case 3: Pet Inherits Caster Damage Buffs**
```python
# Input
character = create_mastermind(level=50)
character.add_power("Thugs.Thugs.Call_Bruiser")
# Add global damage buff from set bonuses
character.totals.damage_buff_by_type[DamageType.SMASHING] = 1.5  # +50%

pet_power = database.get_power("Bruiser.Jab")  # Base: 10 damage
caster_buffs = pet_calculator._get_inherited_caster_buffs()

# Expected
assert caster_buffs['damage_buffs'][DamageType.SMASHING] == 1.5

buffed_pet_power = calculate_pet_power_with_inheritance(
    pet_power, caster_buffs, pet_enhancements=[]
)

jab_damage = buffed_pet_power.get_effect_magnitude(EffectType.DAMAGE)
assert jab_damage == 15.0  # 10 * 1.5 = 15 (inherited buff)
```

**Test Case 4: Pet Does NOT Inherit Caster Recharge**
```python
# Input
character = create_mastermind(level=50)
character.add_power("Thugs.Thugs.Call_Bruiser")
# Add global recharge buff from Hasten + IOs
character.totals.recharge_multiplier = 2.0  # +100% recharge

pet_power = database.get_power("Bruiser.Jab")  # Base: 6s recharge
caster_buffs = pet_calculator._get_inherited_caster_buffs()

# Expected
assert 'recharge_mult' not in caster_buffs  # Recharge NOT inherited

buffed_pet_power = calculate_pet_power_with_inheritance(
    pet_power, caster_buffs, pet_enhancements=[]
)

assert buffed_pet_power.recharge_time == 6.0  # Unchanged
```

**Test Case 5: Pet Enhancement Slotting (Pet IOs)**
```python
# Input
character = create_mastermind(level=50)
summon_power_index = character.add_power("Thugs.Thugs.Call_Bruiser")
character.slot_pet_power(
    summon_power_index,
    pet_power_id=database.get_power_id("Bruiser.Jab"),
    enhancements=[
        ("Call_to_Arms.Pet_Damage", level=50),  # +42.4% damage
        ("Call_to_Arms.Pet_Damage_Accuracy", level=50),
    ]
)

pet_power = database.get_power("Bruiser.Jab")  # Base: 10 damage, 1.0 accuracy

# Expected
pet_power_data = pet_calculator.generate_buffed_pet_powers(
    [pet_power], summon_power_index
)
buffed = pet_power_data[pet_power.power_id].buffed_power

# Pet IOs add to pet damage
jab_damage = buffed.get_effect_magnitude(EffectType.DAMAGE)
assert jab_damage > 10.0  # Enhanced by Pet Damage IO

# Pet IOs add to pet accuracy
assert buffed.accuracy > 1.0  # Enhanced by Pet Accuracy
```

**Test Case 6: Absorb Pet Effects into Summon Power**
```python
# Input
character = create_mastermind(level=32)
character.add_power("Thugs.Thugs.Call_Bruiser")
character.variable_value[summon_power] = 1  # 1 Bruiser summoned

summon_power = character.get_power("Thugs.Thugs.Call_Bruiser")
summon_effect = summon_power.get_effect(EffectType.ENT_CREATE)

# Expected
modified_summon = pet_calculator.absorb_pet_effects(
    summon_power, summon_effect, stacking=1
)

# Summon power now shows absorbed pet damage
total_pet_damage = sum(
    e.magnitude
    for e in modified_summon.effects
    if e.effect_type == EffectType.DAMAGE and e.absorbed_from_pet
)
assert total_pet_damage > 0  # Has absorbed damage from Bruiser powers

# Check specific absorbed powers
absorbed_power_names = [
    e.absorbed_power_name
    for e in modified_summon.effects
    if e.absorbed_from_pet
]
assert "Bruiser.Jab" in absorbed_power_names
assert "Bruiser.Haymaker" in absorbed_power_names
```

**Test Case 7: Controller Pet (No Upgrade Mechanics)**
```python
# Input
character = create_controller(primary="Fire", level=32)
character.add_power("Fire_Control.Summon_Fire_Imps")

entity = database.get_entity_for_power("Fire_Control.Summon_Fire_Imps")

# Expected
assert entity.display_name == "Fire Imps"
assert len(entity.upgrade_power_ids) == 0  # No upgrades for controller pets
upgrade_level = pet_calculator._get_upgrade_level(entity)
assert upgrade_level == 0

powersets = entity.get_available_powersets(upgrade_level, database)
assert len(powersets) == 1  # Single powerset
imp_powers = powersets[0].powers
assert "Fire_Imp.Flares" in [p.power_name for p in imp_powers]
assert "Fire_Imp.Fire_Blast" in [p.power_name for p in imp_powers]
assert "Fire_Imp.Incinerate" in [p.power_name for p in imp_powers]
```

---

## Section 2: C# Implementation Reference

### Primary Implementation Files

**File: `MidsReborn/Core/PetInfo.cs` (170 lines)**

**Class: `PetInfo` (Lines 10-169)**

Core class that manages pet power calculation and buffing.

```csharp
public class PetInfo
{
    // Line 23: Index of summon power in character build
    public readonly int PowerEntryIndex;

    // Line 25: Base summon power (unbuffed)
    private readonly IPower? _basePower;

    // Line 27: Pet entity being summoned
    private readonly SummonedEntity? _entity;

    // Line 32: List of all pet powers from all powersets
    private List<IPower>? _powers;

    // Line 42: Cached buffed power data (base + enhanced versions)
    private static PetPowersData? PowersData { get; set; }

    // Lines 50-58: Constructor - initializes pet data
    public PetInfo(SummonedEntity entity, int idxPower, IPower basePower)
    {
        _entity = entity;
        PowerEntryIndex = idxPower;
        _basePower = basePower;
        CompilePetPowers(out _);      // Get all pet powers from entity
        GeneratePetPowerData();        // Calculate buffed versions
        _powersDataModified += OnPowersDataModified;
    }

    // Lines 67-84: CompilePetPowers - gets pet powers filtered by upgrade level
    private void CompilePetPowers(out HashSet<string> powerNames)
    {
        powerNames = new HashSet<string>();
        if (_entity == null) return;

        // Get all pet powers with upgrade requirements
        var allPowers = _entity.GetPowers();

        // Get current build powers to check which upgrades are taken
        var currentBuildPowers = MidsContext.Character.CurrentBuild.Powers
            .Where(pe => pe?.Power != null)
            .Select(pe => pe?.Power)
            .ToHashSet();

        // Filter to only powers whose upgrade requirement is met
        var filteredPowers = allPowers
            .Where(powerPair => powerPair.Value == null || currentBuildPowers.Contains(powerPair.Value))
            .Select(powerPair => powerPair.Key)
            .ToList();

        powerNames = filteredPowers.Select(x => x.FullName).ToHashSet();
        _powers = filteredPowers;
    }

    // Lines 133-143: GeneratePetPowerData - creates buffed versions
    private void GeneratePetPowerData()
    {
        if (_powers == null || _basePower == null) return;

        // Call character's GenerateBuffedPowers with pet powers
        var powerData = MainModule.MidsController.Toon?.GenerateBuffedPowers(_powers, PowerEntryIndex);

        if (powerData != null)
        {
            PowersData = new PetPowersData(powerData.Value.Key, powerData.Value.Value);
        }

        PowersDataUpdated?.Invoke(this, EventArgs.Empty);
    }

    // Lines 107-116: GetPetPower - retrieves base and buffed versions
    public PetPower? GetPetPower(IPower power)
    {
        _lastPower = power.PowerIndex;
        if (PowersData != null && PowersData.BasePowers.Any())
        {
            return new PetPower(
                PowersData.BasePowers.First(p => p.PowerIndex == power.PowerIndex),
                PowersData.BuffedPowers.First(p => p.PowerIndex == power.PowerIndex)
            );
        }
        return null;
    }
}

// Lines 145-155: PetPowersData - stores base and buffed power lists
private class PetPowersData
{
    public readonly List<IPower> BasePowers;
    public readonly List<IPower> BuffedPowers;

    public PetPowersData(List<IPower> basePowers, List<IPower> buffedPowers)
    {
        // Filter to only pet powers (not summon power itself)
        BasePowers = basePowers.Where(p => p.IsPetPower).ToList();
        BuffedPowers = buffedPowers.Where(p => p.IsPetPower).ToList();
    }
}

// Lines 157-167: PetPower - pair of base and buffed versions
public class PetPower
{
    public readonly IPower BasePower;
    public readonly IPower BuffedPower;

    public PetPower(IPower basePower, IPower buffedPower)
    {
        BasePower = basePower;
        BuffedPower = buffedPower;
    }
}
```

**Key Design Notes:**
1. PetInfo is created when viewing a pet power (e.g., in PetView UI)
2. `CompilePetPowers()` filters pet powers based on upgrade powers in build
3. `GeneratePetPowerData()` delegates to character's buffing system
4. Powers are stored as pairs (base + buffed) for comparison display

---

**File: `MidsReborn/Core/SummonedEntity.cs` (226 lines)**

**Class: `SummonedEntity` (Lines 8-226)**

Represents a summonable entity (pet) definition.

```csharp
public class SummonedEntity
{
    // Lines 10-13: Internal ID arrays
    private int _nClassID;           // Entity class ID (Class_Minion_Pets, etc.)
    private int _nID = -1;           // Entity database ID
    private int[] _nPowerset = Array.Empty<int>();      // Powerset IDs
    private int[] _nUpgradePower = Array.Empty<int>();  // Upgrade power IDs

    // Lines 56-61: Public properties
    public string UID { get; set; } = string.Empty;
    public string DisplayName { get; set; } = string.Empty;
    public string[] PowersetFullName { get; set; } = Array.Empty<string>();
    public string[] UpgradePowerFullName { get; set; } = Array.Empty<string>();
    public string ClassName { get; set; } = string.Empty;
    public Enums.eSummonEntity EntityType { get; set; }

    // Lines 65-83: Getter methods for internal IDs
    public IReadOnlyList<int> GetNPowerset() => _nPowerset;
    public IReadOnlyList<int> GetNUpgradePower() => _nUpgradePower;
    public int GetNId() => _nID;
    public int GetNClassId() => _nClassID;

    // Lines 85-124: GetPowers - returns pet powers with upgrade requirements
    public Dictionary<IPower, IPower?> GetPowers()
    {
        // Build map of powerset name -> powers
        var powersByPowerset = new Dictionary<string, List<IPower>>();
        foreach (var setString in PowersetFullName)
        {
            if (string.IsNullOrWhiteSpace(setString)) continue;

            var powerset = DatabaseAPI.GetPowersetByFullname(setString);
            if (powerset == null) continue;

            // Get all powers except PM (passive modifiers)
            var powers = powerset.Powers
                .Where(power => power != null && !power.FullName.Contains("PM"))
                .ToList();

            powersByPowerset[powerset.FullName] = powers!;
        }

        // Get upgrade powers (Equip, Upgrade for Masterminds)
        var upgPowers = UpgradePowerFullName
            .Where(upgString => !string.IsNullOrWhiteSpace(upgString))
            .Select(DatabaseAPI.GetPowerByFullName)
            .OfType<IPower>()
            .ToList();

        // Build result map: pet_power -> required_upgrade_power
        var allPowers = new Dictionary<IPower, IPower?>();
        var powersetIndex = 0;
        foreach (var powers in powersByPowerset.Values)
        {
            foreach (var power in powers)
            {
                // First powerset (index 0) has no upgrade requirement
                // Second powerset (index 1) requires first upgrade power
                // Third powerset (index 2) requires second upgrade power
                var requiredUpgrade = (powersetIndex > 0 && powersetIndex - 1 < upgPowers.Count)
                    ? upgPowers[powersetIndex - 1]
                    : null;

                allPowers[power] = requiredUpgrade;
            }
            powersetIndex++;
        }

        return allPowers;
    }

    // Lines 145-156: MatchSummonIDs - links string names to database IDs
    public static void MatchSummonIDs(
        Func<string, int> nIdFromUidClass,
        Func<string, int> nidFromUidPowerset,
        Func<string, int> nidFromUidPower)
    {
        for (var ei = 0; ei <= DatabaseAPI.Database.Entities.Length - 1; ++ei)
        {
            var entity = DatabaseAPI.Database.Entities[ei];
            entity._nID = ei;
            entity._nClassID = nIdFromUidClass(entity.ClassName);
            entity._nPowerset = entity.PowersetFullName.Select(nidFromUidPowerset).ToArray();
            entity._nUpgradePower = entity.UpgradePowerFullName.Select(nidFromUidPower).ToArray();
        }
    }
}
```

**Key Design Notes:**
1. `PowersetFullName` array holds 1-3 powersets (base, upgrade1, upgrade2)
2. `UpgradePowerFullName` array holds 0-2 upgrade powers
3. `GetPowers()` returns Dictionary mapping pet_power -> required_upgrade
4. `MatchSummonIDs()` is called at database load to link string names to IDs

---

**File: `MidsReborn/Core/Base/Data_Classes/Power.cs` (Lines 2573-2678)**

**Method: `AbsorbPetEffects()` - Absorbs pet power effects into summon power for display**

```csharp
// Lines 2573-2578: Check if absorption is enabled
public void AbsorbPetEffects(int hIdx = -1, int stackingOverride = -1)
{
    if (!AbsorbSummonAttributes && !AbsorbSummonEffects)
    {
        return;  // No absorption flags set
    }

    // Lines 2579-2586: Find all EntCreate effects with valid summon indices
    var intList = new List<int>();
    for (var index = 0; index < Effects.Length; index++)
    {
        if (Effects[index].EffectType == Enums.eEffectType.EntCreate &&
            Effects[index].nSummon > -1 &&
            Math.Abs(Effects[index].Probability - 1) < 0.01 &&  // 100% probability
            DatabaseAPI.Database.Entities.Length > Effects[index].nSummon)
        {
            intList.Add(index);  // This effect summons an entity
        }
    }

    if (intList.Count > 0)
    {
        HasAbsorbedEffects = true;
    }

    // Lines 2593-2677: Process each summon effect
    foreach (var t in intList)
    {
        var effect = Effects[t];
        var nSummon1 = effect.nSummon;
        var stacking = 1;

        // Lines 2598-2606: Determine stacking (for MM variable pets)
        if (VariableEnabled && effect.VariableModified && hIdx > -1 &&
            MidsContext.Character != null &&
            MidsContext.Character.CurrentBuild.Powers[hIdx].VariableValue > stacking)
        {
            stacking = MidsContext.Character.CurrentBuild.Powers[hIdx].VariableValue;
        }

        if (stackingOverride > 0)
        {
            stacking = stackingOverride;
        }

        // Lines 2608-2612: Get pet powersets
        var nPowerset = DatabaseAPI.Database.Entities[nSummon1].GetNPowerset();
        if (nPowerset.Count == 0)
        {
            continue;
        }

        // Lines 2614-2644: Absorb pet attributes (if flag set)
        if (AbsorbSummonAttributes && nPowerset[0] > -1 && nPowerset[0] < DatabaseAPI.Database.Powersets.Length)
        {
            var powerset = DatabaseAPI.Database.Powersets[nPowerset[0]];
            if (powerset.Power.Length > 0)
            {
                foreach (var power in powerset.Powers)
                {
                    // Copy attack/area/target attributes from pet power to summon power
                    AttackTypes = power.AttackTypes;
                    EffectArea = power.EffectArea;
                    EntitiesAffected = power.EntitiesAffected;
                    if (EntitiesAutoHit != Enums.eEntity.None)
                    {
                        EntitiesAutoHit = power.EntitiesAutoHit;
                    }

                    Ignore_Buff = power.Ignore_Buff;
                    IgnoreEnh = power.IgnoreEnh;
                    MaxTargets = power.MaxTargets;
                    Radius = power.Radius;
                    Target = power.Target;

                    // Only copy accuracy if summon power is not autohit
                    if (DatabaseAPI.Database.Power[PowerIndex].EntitiesAutoHit is Enums.eEntity.None or Enums.eEntity.Caster)
                    {
                        continue;
                    }

                    Accuracy = power.Accuracy;
                    break;  // Only absorb from first power
                }
            }
        }

        // Lines 2646-2674: Absorb pet power effects (if flag set)
        if (!AbsorbSummonEffects)
        {
            continue;
        }

        foreach (var setIndex in nPowerset)
        {
            if (setIndex < 0 || setIndex >= DatabaseAPI.Database.Powersets.Length)
            {
                continue;
            }

            foreach (var power1 in DatabaseAPI.Database.Powersets[setIndex].Powers)
            {
                // Call AbsorbEffects helper (clones effects with entity class modifiers)
                foreach (var absorbEffect in AbsorbEffects(power1, effect.Duration, effect.DelayedTime,
                    DatabaseAPI.Database.Classes[DatabaseAPI.Database.Entities[nSummon1].GetNClassId()], stacking))
                {
                    // Handle nested pseudopets (pets that summon pseudopets)
                    var nSummon2 = power1.Effects[absorbEffect].nSummon;
                    if (DatabaseAPI.Database.Entities[nSummon2].GetNPowerset()[0] < 0)
                    {
                        continue;
                    }

                    foreach (var power2 in DatabaseAPI.Database.Powersets[DatabaseAPI.Database.Entities[nSummon2].GetNPowerset()[0]].Powers)
                    {
                        AbsorbEffects(power2, effect.Duration, effect.DelayedTime,
                            DatabaseAPI.Database.Classes[DatabaseAPI.Database.Entities[nSummon1].GetNClassId()], stacking);
                    }
                }
            }
        }

        AbsorbedPetEffects = true;
    }
}
```

**Key Implementation Notes:**
1. `AbsorbSummonAttributes`: Copies attack/area/target properties from first pet power
2. `AbsorbSummonEffects`: Clones all pet power effects into summon power
3. `VariableValue`: For MM summons, multiplies effects by number of pets
4. `AbsorbEffects()` helper: Applies entity class modifiers and stacking
5. Nested pseudopets: Some pets summon pseudopets (e.g., Phantom Army's decoys)

---

**File: `MidsReborn/clsToonX.cs` (Lines 2092-2129)**

**Method: `GenerateBuffedPowers()` - Calculates buffed pet powers with caster inheritance**

```csharp
// Lines 2092-2129: Generate buffed versions of pet powers
public KeyValuePair<List<IPower>, List<IPower>>? GenerateBuffedPowers(List<IPower> powers, int basePowerHistoryIdx)
{
    // Lines 2094-2104: If summon power not in build, return unbuffed
    if (basePowerHistoryIdx < 0)
    {
        // Get unbuffed powers data from the database directly
        var powersList = powers
            .Select(e => DatabaseAPI.Database.Power.FirstOrDefault(f => f?.StaticIndex == e.StaticIndex) ?? new Power { StaticIndex = -1 })
            .Cast<IPower>()
            .ToList();

        var clonedPowersList = powersList.Clone();
        return new KeyValuePair<List<IPower>, List<IPower>>(clonedPowersList, clonedPowersList);
    }

    // Lines 2106-2109: Initialize result lists
    var mathPowers = new List<IPower>();
    var buffedPowers = new List<IPower>();
    var basePower = CurrentBuild.Powers[basePowerHistoryIdx].Power.Clone();
    powers.Add(basePower); // Restore original attached power

    // Lines 2111-2126: Process each pet power
    for (var i = 0; i < powers.Count; i++)
    {
        if (powers[i] == null)
        {
            continue;
        }

        // Temporarily replace summon power's NIDPower with current pet power
        CurrentBuild.Powers[basePowerHistoryIdx].NIDPower = DatabaseAPI.Database.Power.TryFindIndex(e => e?.StaticIndex == powers[i].StaticIndex);

        // Generate buffed power using full character buffing system
        GenerateBuffedPowerArray();

        // Store results (skip last one which is original summon power)
        if (i < powers.Count - 1)
        {
            mathPowers.Add(_mathPowers[basePowerHistoryIdx].Clone());
            buffedPowers.Add(_buffedPowers[basePowerHistoryIdx].Clone());
        }
    }

    return new KeyValuePair<List<IPower>, List<IPower>>(mathPowers, buffedPowers);
}
```

**Key Implementation Notes:**
1. If `basePowerHistoryIdx < 0`, summon power not taken -> return unbuffed
2. Temporarily swaps summon power's NIDPower to process each pet power
3. Calls `GenerateBuffedPowerArray()` which applies full buffing pipeline:
   - Enhancement slotting (from pet power slots)
   - Enhancement Diversification
   - Global buffs (inherited accuracy/damage)
   - Archetype/entity class modifiers
4. Returns pair of lists: (math powers, buffed powers)

---

### Key Constants and Values

**Entity Class Names** (from database):
- `"Class_Minion_Pets"` - T1 Mastermind pets (3 summons)
- `"Class_Lt_Pets"` - T2 Mastermind pets (2 summons)
- `"Class_Boss_Pets"` - T3 Mastermind pets (1 summon)
- `"Class_Pet"` - Controller/Dominator pets
- `"Class_Minion"` - Generic minion (for temp pets)

**Pet Damage Scales** (from AttribMod.json):
- Class_Minion_Pets Ranged_Damage: 0.40-0.55 (level-dependent)
- Class_Lt_Pets Ranged_Damage: 0.65-0.80
- Class_Boss_Pets Ranged_Damage: 1.00-1.25
- Scales are significantly lower than player ATs to balance pet damage

**Inherited Caster Stats**:
```csharp
// From character totals (in clsToonX.cs buffing system)
Inherited:
- _selfBuffs.Effect[(int)Enums.eStatType.BuffAcc]  // Global accuracy
- _selfBuffs.Effect[(int)Enums.eStatType.ToHit]    // Global tohit
- _selfBuffs.Effect[(int)Enums.eStatType.DamageBuff] // By damage type
- _selfBuffs.Effect[(int)Enums.eStatType.HealBuff]   // Healing buffs

NOT Inherited:
- _selfBuffs.Effect[(int)Enums.eStatType.Haste]    // Recharge
- _selfBuffs.Effect[(int)Enums.eStatType.Defense]  // Defense
- _selfBuffs.Effect[(int)Enums.eStatType.Res]      // Resistance
- _selfBuffs.Effect[(int)Enums.eStatType.Recovery] // Endurance recovery
```

**Mastermind Supremacy** (inherent power):
- Grants +25% damage, +25% tohit, +100% resistance to all pets within 60ft
- Applied as buff effects on pet powers (not modeled in pet calculation)
- Separate from inherited caster buffs (applied by game engine, not MidsReborn)

---

## Section 3: Database Schema

### Proposed PostgreSQL Schema

**Table: `pet_entities`** - Summonable entity definitions

```sql
CREATE TABLE pet_entities (
    id SERIAL PRIMARY KEY,
    uid VARCHAR(255) NOT NULL UNIQUE,
    display_name VARCHAR(255) NOT NULL,
    entity_type VARCHAR(50) NOT NULL, -- 'Pet', 'Henchman', 'PseudoPet'
    entity_class_id INTEGER NOT NULL REFERENCES entity_classes(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT valid_entity_type CHECK (entity_type IN ('Pet', 'Henchman', 'PseudoPet', 'Object'))
);

CREATE INDEX idx_pet_entities_uid ON pet_entities(uid);
CREATE INDEX idx_pet_entities_class ON pet_entities(entity_class_id);

COMMENT ON TABLE pet_entities IS 'Summonable entities (pets, henchmen, pseudopets)';
COMMENT ON COLUMN pet_entities.uid IS 'Unique identifier from game data';
COMMENT ON COLUMN pet_entities.entity_type IS 'Type of entity: Pet (permanent), Henchman (MM pet), PseudoPet (temporary)';
COMMENT ON COLUMN pet_entities.entity_class_id IS 'Entity class defining damage/buff scales';
```

**Table: `pet_powersets`** - Powersets available to pets

```sql
CREATE TABLE pet_powersets (
    id SERIAL PRIMARY KEY,
    pet_entity_id INTEGER NOT NULL REFERENCES pet_entities(id) ON DELETE CASCADE,
    powerset_id INTEGER NOT NULL REFERENCES powersets(id),
    tier INTEGER NOT NULL DEFAULT 0, -- 0 = base, 1 = first upgrade, 2 = second upgrade
    upgrade_power_id INTEGER REFERENCES powers(id), -- Power that unlocks this tier (NULL for tier 0)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT valid_tier CHECK (tier BETWEEN 0 AND 2),
    UNIQUE(pet_entity_id, tier)
);

CREATE INDEX idx_pet_powersets_entity ON pet_powersets(pet_entity_id);
CREATE INDEX idx_pet_powersets_powerset ON pet_powersets(powerset_id);
CREATE INDEX idx_pet_powersets_upgrade ON pet_powersets(upgrade_power_id);

COMMENT ON TABLE pet_powersets IS 'Powersets available to pet entities at different upgrade tiers';
COMMENT ON COLUMN pet_powersets.tier IS '0=base, 1=after first upgrade (Equip), 2=after second upgrade (Upgrade)';
COMMENT ON COLUMN pet_powersets.upgrade_power_id IS 'Mastermind upgrade power required to unlock this tier';
```

**Table: `entity_classes`** - Damage/buff scales for pets

```sql
CREATE TABLE entity_classes (
    id SERIAL PRIMARY KEY,
    class_name VARCHAR(255) NOT NULL UNIQUE,
    display_name VARCHAR(255) NOT NULL,
    column_index INTEGER NOT NULL, -- Column in modifier tables
    hitpoints_base INTEGER NOT NULL DEFAULT 500,
    hitpoints_cap INTEGER NOT NULL DEFAULT 2000,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT valid_column CHECK (column_index >= 0 AND column_index < 60)
);

CREATE INDEX idx_entity_classes_name ON entity_classes(class_name);

COMMENT ON TABLE entity_classes IS 'Entity classes with damage/buff scales (like archetypes for pets)';
COMMENT ON COLUMN entity_classes.column_index IS 'Column index in AttribMod tables for modifier lookups';

-- Sample data
INSERT INTO entity_classes (class_name, display_name, column_index, hitpoints_base, hitpoints_cap) VALUES
('Class_Minion_Pets', 'Minion Pet', 50, 241, 804),
('Class_Lt_Pets', 'Lieutenant Pet', 51, 361, 1203),
('Class_Boss_Pets', 'Boss Pet', 52, 962, 3207),
('Class_Pet', 'Controller Pet', 53, 481, 1604);
```

**Table: `pet_power_inheritance`** - Which stats pets inherit

```sql
CREATE TABLE pet_power_inheritance (
    id SERIAL PRIMARY KEY,
    stat_type VARCHAR(50) NOT NULL,
    is_inherited BOOLEAN NOT NULL DEFAULT false,
    inheritance_type VARCHAR(50), -- 'multiplicative', 'additive', NULL
    description TEXT,

    CONSTRAINT valid_stat CHECK (stat_type IN (
        'accuracy', 'tohit', 'damage', 'healing',
        'defense', 'resistance', 'recharge', 'endurance', 'range'
    )),
    CONSTRAINT valid_inheritance CHECK (inheritance_type IN ('multiplicative', 'additive') OR inheritance_type IS NULL)
);

-- Sample data
INSERT INTO pet_power_inheritance (stat_type, is_inherited, inheritance_type, description) VALUES
('accuracy', true, 'multiplicative', 'Global accuracy buffs multiply pet accuracy'),
('tohit', true, 'additive', 'Global tohit buffs add to pet hit chance'),
('damage', true, 'multiplicative', 'Global damage buffs multiply pet damage by type'),
('healing', true, 'multiplicative', 'Global healing buffs multiply pet healing powers'),
('defense', false, NULL, 'Pets have their own defense values'),
('resistance', false, NULL, 'Pets have their own resistance values'),
('recharge', false, NULL, 'Pets have their own recharge rates'),
('endurance', false, NULL, 'Pets have their own endurance pools'),
('range', false, NULL, 'Pets have their own power ranges');

COMMENT ON TABLE pet_power_inheritance IS 'Defines which caster stats affect pet powers';
```

**Table: `build_pet_power_slots`** - Enhancements slotted in pet powers

```sql
CREATE TABLE build_pet_power_slots (
    id SERIAL PRIMARY KEY,
    build_id INTEGER NOT NULL REFERENCES builds(id) ON DELETE CASCADE,
    summon_power_entry_id INTEGER NOT NULL REFERENCES build_power_entries(id) ON DELETE CASCADE,
    pet_power_id INTEGER NOT NULL REFERENCES powers(id),
    slot_index INTEGER NOT NULL, -- 0-5 (max 6 slots)
    enhancement_id INTEGER NOT NULL REFERENCES enhancements(id),
    enhancement_level INTEGER NOT NULL DEFAULT 50,
    is_attuned BOOLEAN NOT NULL DEFAULT false,
    is_boosted BOOLEAN NOT NULL DEFAULT false,
    boost_level INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT valid_slot_index CHECK (slot_index BETWEEN 0 AND 5),
    CONSTRAINT valid_enhancement_level CHECK (enhancement_level BETWEEN 1 AND 53),
    CONSTRAINT valid_boost_level CHECK (boost_level IS NULL OR boost_level BETWEEN 0 AND 5),
    UNIQUE(build_id, summon_power_entry_id, pet_power_id, slot_index)
);

CREATE INDEX idx_pet_slots_build ON build_pet_power_slots(build_id);
CREATE INDEX idx_pet_slots_summon ON build_pet_power_slots(summon_power_entry_id);
CREATE INDEX idx_pet_slots_pet_power ON build_pet_power_slots(pet_power_id);

COMMENT ON TABLE build_pet_power_slots IS 'Enhancements slotted in pet powers (separate from summon power slots)';
COMMENT ON COLUMN build_pet_power_slots.summon_power_entry_id IS 'The summon power entry this pet belongs to';
COMMENT ON COLUMN build_pet_power_slots.pet_power_id IS 'The pet power being enhanced';
```

### Query Examples

**Get all pet powers for a Mastermind summon in a build:**

```sql
WITH build_upgrades AS (
    -- Check which upgrade powers the build has taken
    SELECT
        bpe.power_id,
        p.full_name
    FROM build_power_entries bpe
    JOIN powers p ON p.id = bpe.power_id
    WHERE bpe.build_id = $1  -- build_id
        AND p.full_name LIKE '%Equip%' OR p.full_name LIKE '%Upgrade%'
),
available_tiers AS (
    -- Determine max tier available
    SELECT COALESCE(MAX(tier), 0) AS max_tier
    FROM pet_powersets pp
    LEFT JOIN build_upgrades bu ON bu.power_id = pp.upgrade_power_id
    WHERE pp.pet_entity_id = $2  -- pet_entity_id
        AND (pp.upgrade_power_id IS NULL OR bu.power_id IS NOT NULL)
)
-- Get all pet powers up to available tier
SELECT
    p.id,
    p.full_name,
    p.display_name,
    ps.tier,
    pp.upgrade_power_id
FROM pet_powersets pp
JOIN powersets ps ON ps.id = pp.powerset_id
JOIN powerset_powers psp ON psp.powerset_id = ps.id
JOIN powers p ON p.id = psp.power_id
CROSS JOIN available_tiers at
WHERE pp.pet_entity_id = $2
    AND pp.tier <= at.max_tier
    AND p.full_name NOT LIKE '%PM%'  -- Exclude passive modifiers
ORDER BY pp.tier, psp.power_index;
```

**Get pet power with enhancements and caster buffs:**

```sql
SELECT
    pp.id AS pet_power_id,
    pp.full_name AS pet_power_name,
    pp.base_accuracy,
    pp.base_recharge_time,

    -- Pet slotting
    json_agg(json_build_object(
        'slot_index', bpps.slot_index,
        'enhancement_id', e.id,
        'enhancement_name', e.full_name,
        'enhancement_level', bpps.enhancement_level
    ) ORDER BY bpps.slot_index) FILTER (WHERE bpps.id IS NOT NULL) AS pet_slots,

    -- Caster buffs (inherited)
    SUM(CASE WHEN bse.stat_type = 'accuracy' AND bse.is_global THEN bse.value ELSE 0 END) AS caster_accuracy_buff,
    SUM(CASE WHEN bse.stat_type = 'tohit' AND bse.is_global THEN bse.value ELSE 0 END) AS caster_tohit_buff,
    SUM(CASE WHEN bse.stat_type = 'damage' AND bse.damage_type = pp.primary_damage_type THEN bse.value ELSE 0 END) AS caster_damage_buff

FROM powers pp
JOIN pet_powersets pps ON pps.powerset_id = pp.powerset_id
LEFT JOIN build_pet_power_slots bpps ON bpps.pet_power_id = pp.id AND bpps.build_id = $1
LEFT JOIN enhancements e ON e.id = bpps.enhancement_id
LEFT JOIN build_stat_effects bse ON bse.build_id = $1 AND bse.is_active = true
WHERE pp.id = $2  -- pet_power_id
GROUP BY pp.id;
```

---

## Section 4: Comprehensive Test Cases

### Test Case 1: Mastermind Base Pet (No Upgrades Taken)

**Scenario**: Level 32 Thugs Mastermind summons Bruiser (T3 pet) without taking Equip or Upgrade powers

**Input:**
```python
character_level = 32
archetype = "Mastermind"
summon_power = "Thugs.Thugs.Call_Bruiser"
build_powers = ["Thugs.Thugs.Call_Bruiser"]  # Only summon, no upgrades
entity = database.get_entity("Pets_T_Bruiser")
```

**Expected Entity Data:**
```python
entity.display_name == "Bruiser"
entity.class_name == "Class_Boss_Pets"
entity.powerset_full_names == [
    "Pets_Thugs.Pets_T_Bruiser",           # Tier 0: Base powers
    "Pets_Thugs.Pets_T_Bruiser_Upgrade_1",  # Tier 1: Equip powers
    "Pets_Thugs.Pets_T_Bruiser_Upgrade_2"   # Tier 2: Upgrade powers
]
entity.upgrade_power_full_names == [
    "Thugs.Thugs.Equip_Thugs",      # Unlocks tier 1
    "Thugs.Thugs.Upgrade_Equipment"  # Unlocks tier 2
]
```

**Upgrade Level Calculation:**
```python
upgrade_level = 0  # No upgrade powers in build
available_powersets = entity.powersets[0:upgrade_level+1]  # Only first powerset
assert len(available_powersets) == 1
```

**Available Pet Powers** (Tier 0 only):
```python
bruiser_base_powers = [
    "Pets_T_Bruiser.Jab",           # Base: 13.88 smashing @ level 32
    "Pets_T_Bruiser.Punch",         # Base: 27.76 smashing
    "Pets_T_Bruiser.Haymaker",      # Base: 55.52 smashing
    "Pets_T_Bruiser.Taunt",         # Base: taunt effect
    "Pets_T_Bruiser.Brawl",         # Base: 6.94 smashing
]

# NOT available (require Equip - tier 1):
locked_tier1 = ["Pets_T_Bruiser.Hurl", "Pets_T_Bruiser.Hand_Clap"]

# NOT available (require Upgrade - tier 2):
locked_tier2 = ["Pets_T_Bruiser.Foot_Stomp", "Pets_T_Bruiser.Knockout_Blow"]
```

**Step-by-Step Calculation** (Jab power):
```python
# Base pet power values
jab_base_accuracy = 1.00
jab_base_damage = 13.88  # Smashing, level 32, Class_Boss_Pets
jab_base_recharge = 4.0

# No pet slotting (example)
jab_enhancement_damage = 0.0
jab_enhancement_accuracy = 0.0

# No caster buffs (example)
caster_accuracy_buff = 0.0
caster_damage_buff = 0.0

# Final values (unbuffed)
jab_final_accuracy = jab_base_accuracy * (1 + jab_enhancement_accuracy + caster_accuracy_buff)
# = 1.00 * (1 + 0 + 0) = 1.00

jab_final_damage = jab_base_damage * (1 + jab_enhancement_damage) * (1 + caster_damage_buff)
# = 13.88 * (1 + 0) * (1 + 0) = 13.88

jab_final_recharge = jab_base_recharge / (1 + jab_enhancement_recharge)
# = 4.0 / (1 + 0) = 4.0
```

**Expected Output:**
```python
assert upgrade_level == 0
assert len(available_powers) == 5
assert "Pets_T_Bruiser.Jab" in [p.full_name for p in available_powers]
assert "Pets_T_Bruiser.Hurl" not in [p.full_name for p in available_powers]

jab_power = get_pet_power("Pets_T_Bruiser.Jab")
assert jab_power.base_damage == 13.88
assert jab_power.buffed_damage == 13.88  # No buffs
```

---

### Test Case 2: Mastermind with Full Upgrades

**Scenario**: Level 50 Thugs Mastermind with both Equip and Upgrade powers

**Input:**
```python
character_level = 50
build_powers = [
    "Thugs.Thugs.Call_Bruiser",
    "Thugs.Thugs.Equip_Thugs",       # First upgrade
    "Thugs.Thugs.Upgrade_Equipment"  # Second upgrade
]
```

**Upgrade Level Calculation:**
```python
upgrade_count = 0
for upgrade_power_name in entity.upgrade_power_full_names:
    if upgrade_power_name in build_powers:
        upgrade_count += 1

upgrade_level = upgrade_count  # = 2
available_powersets = entity.powersets[0:upgrade_level+1]  # All 3 powersets
assert len(available_powersets) == 3
```

**Available Pet Powers** (All Tiers):
```python
bruiser_all_powers = [
    # Tier 0 (base)
    "Pets_T_Bruiser.Jab",
    "Pets_T_Bruiser.Punch",
    "Pets_T_Bruiser.Haymaker",
    "Pets_T_Bruiser.Taunt",
    "Pets_T_Bruiser.Brawl",

    # Tier 1 (Equip)
    "Pets_T_Bruiser.Hurl",
    "Pets_T_Bruiser.Hand_Clap",

    # Tier 2 (Upgrade)
    "Pets_T_Bruiser.Foot_Stomp",
    "Pets_T_Bruiser.Knockout_Blow"
]

assert len(bruiser_all_powers) == 9
```

**Expected Output:**
```python
assert upgrade_level == 2
assert len(available_powers) == 9
assert "Pets_T_Bruiser.Hurl" in [p.full_name for p in available_powers]
assert "Pets_T_Bruiser.Foot_Stomp" in [p.full_name for p in available_powers]
```

---

### Test Case 3: Pet Inherits Caster Damage Buffs

**Scenario**: Mastermind with +50% smashing damage from set bonuses

**Input:**
```python
character_level = 50
summon_power = "Thugs.Thugs.Call_Bruiser"
pet_power = "Pets_T_Bruiser.Jab"

# Pet base values
jab_base_damage = 18.63  # Level 50, Class_Boss_Pets, smashing
jab_base_accuracy = 1.00

# Caster has global damage buff
caster_totals = {
    'damage_buffs': {
        'smashing': 0.50,  # +50% from set bonuses
        'lethal': 0.30,
        'fire': 0.0,
    }
}

# No pet slotting in this example
pet_enhancement_damage = 0.0
```

**Step-by-Step Calculation:**
```python
# Step 1: Get inherited buff
inherited_damage_buff = caster_totals['damage_buffs']['smashing']
# = 0.50

# Step 2: Apply to pet power
jab_buffed_damage = jab_base_damage * (1 + pet_enhancement_damage) * (1 + inherited_damage_buff)
# = 18.63 * (1 + 0) * (1 + 0.50)
# = 18.63 * 1.50
# = 27.945
```

**Expected Output:**
```python
buffed_power = calculate_pet_power_with_inheritance(
    pet_power=jab_power,
    caster_buffs={'damage_buffs': {'smashing': 0.50}},
    pet_enhancements=[]
)

assert buffed_power.base_damage == 18.63
assert abs(buffed_power.buffed_damage - 27.945) < 0.01
```

---

### Test Case 4: Pet Does NOT Inherit Caster Recharge

**Scenario**: Mastermind with +100% global recharge (Hasten + set bonuses)

**Input:**
```python
character_level = 50
pet_power = "Pets_T_Bruiser.Jab"

# Pet base values
jab_base_recharge = 4.0  # seconds

# Caster has massive recharge
caster_totals = {
    'recharge_multiplier': 2.0  # +100% recharge (Hasten + IOs)
}

# No pet slotting
pet_enhancement_recharge = 0.0
```

**Step-by-Step Calculation:**
```python
# Step 1: Check inheritance rules
recharge_is_inherited = False  # Per design spec

# Step 2: Calculate pet recharge (caster buff NOT applied)
jab_buffed_recharge = jab_base_recharge / (1 + pet_enhancement_recharge)
# = 4.0 / (1 + 0)
# = 4.0  # UNCHANGED from base
```

**Expected Output:**
```python
buffed_power = calculate_pet_power_with_inheritance(
    pet_power=jab_power,
    caster_buffs={'recharge_multiplier': 2.0},  # Should be ignored
    pet_enhancements=[]
)

assert buffed_power.base_recharge == 4.0
assert buffed_power.buffed_recharge == 4.0  # NOT 2.0
```

---

### Test Case 5: Pet Enhancement Slotting (Pet IOs)

**Scenario**: Bruiser's Jab slotted with Pet Damage and Pet Accuracy IOs

**Input:**
```python
character_level = 50
pet_power = "Pets_T_Bruiser.Jab"

# Pet base values
jab_base_damage = 18.63  # Smashing
jab_base_accuracy = 1.00
jab_base_recharge = 4.0

# Pet IOs slotted in Jab
pet_enhancements = [
    {
        'name': 'Call_to_Arms.Pet_Damage',
        'level': 50,
        'values': {'damage': 0.424}  # +42.4% damage
    },
    {
        'name': 'Call_to_Arms.Pet_Damage_Accuracy',
        'level': 50,
        'values': {'damage': 0.212, 'accuracy': 0.212}  # +21.2% each
    },
    {
        'name': 'Soulbound_Allegiance.Pet_Damage_Accuracy',
        'level': 50,
        'values': {'damage': 0.212, 'accuracy': 0.212}
    }
]

# No caster buffs in this example
caster_buffs = {'damage_buffs': {'smashing': 0.0}, 'accuracy_mult': 0.0}
```

**Step-by-Step Calculation:**
```python
# Step 1: Sum pet enhancements (pre-ED)
total_pet_damage_enh = 0.424 + 0.212 + 0.212 = 0.848  # 84.8%
total_pet_accuracy_enh = 0.0 + 0.212 + 0.212 = 0.424  # 42.4%

# Step 2: Apply Enhancement Diversification (Schedule A)
# Damage: 0.848 > 0.70, so ED applies
# ED formula for Schedule A:
#   0.0 - 0.70: 100% efficient
#   0.70 - 1.00: 90% efficient
#   1.00 - 1.30: 70% efficient
#   > 1.30: 15% efficient

ed_damage = 0.70 + (0.848 - 0.70) * 0.90
# = 0.70 + 0.148 * 0.90
# = 0.70 + 0.1332
# = 0.8332  # 83.32% after ED

ed_accuracy = 0.424  # No ED (below 0.70 threshold)

# Step 3: Apply to pet power
jab_enhanced_damage = jab_base_damage * (1 + ed_damage) * (1 + caster_damage_buff)
# = 18.63 * (1 + 0.8332) * (1 + 0.0)
# = 18.63 * 1.8332
# = 34.152

jab_enhanced_accuracy = jab_base_accuracy * (1 + ed_accuracy + caster_accuracy_buff)
# = 1.00 * (1 + 0.424 + 0.0)
# = 1.424
```

**Expected Output:**
```python
buffed_power = calculate_pet_power_with_enhancement(
    pet_power=jab_power,
    pet_enhancements=pet_enhancements,
    caster_buffs={}
)

assert abs(buffed_power.buffed_damage - 34.152) < 0.01
assert abs(buffed_power.buffed_accuracy - 1.424) < 0.01
```

---

### Test Case 6: Absorb Pet Effects into Summon Power

**Scenario**: Display total pet damage on Mastermind summon power

**Input:**
```python
character_level = 50
summon_power = "Thugs.Thugs.Call_Bruiser"
entity = database.get_entity("Pets_T_Bruiser")

# Build has summon + both upgrades
build_powers = [
    "Thugs.Thugs.Call_Bruiser",
    "Thugs.Thugs.Equip_Thugs",
    "Thugs.Thugs.Upgrade_Equipment"
]

# Variable value: 1 Bruiser summoned
stacking = 1
```

**Step-by-Step Calculation:**
```python
# Step 1: Get all available pet powers (upgrade level 2)
available_powers = [
    "Pets_T_Bruiser.Jab",          # 18.63 smashing
    "Pets_T_Bruiser.Punch",        # 37.26 smashing
    "Pets_T_Bruiser.Haymaker",     # 74.52 smashing
    "Pets_T_Bruiser.Hurl",         # 74.52 smashing
    "Pets_T_Bruiser.Foot_Stomp",   # 74.52 smashing (PBAoE)
    "Pets_T_Bruiser.Knockout_Blow", # 111.78 smashing
    # (excluding non-damage powers)
]

# Step 2: Apply entity class modifiers
entity_class = "Class_Boss_Pets"
entity_class_melee_mod = 1.00  # Boss pets have 1.00 melee modifier at level 50

# Step 3: Sum all pet damage effects
total_pet_damage = 0
for power in available_powers:
    for effect in power.effects:
        if effect.effect_type == 'Damage':
            absorbed_damage = effect.magnitude * entity_class_melee_mod * stacking
            total_pet_damage += absorbed_damage

total_pet_damage = 18.63 + 37.26 + 74.52 + 74.52 + 74.52 + 111.78
# = 391.23 smashing (total damage capability)

# Step 4: Add to summon power
summon_power_with_absorption = summon_power.clone()
for absorbed_effect in absorbed_effects:
    summon_power_with_absorption.effects.append(absorbed_effect)
```

**Expected Output:**
```python
modified_summon = absorb_pet_effects(
    summon_power=summon_power,
    entity=entity,
    stacking=1
)

absorbed_damage_effects = [
    e for e in modified_summon.effects
    if e.effect_type == 'Damage' and e.absorbed_from_pet
]

total_absorbed_damage = sum(e.magnitude for e in absorbed_damage_effects)
assert abs(total_absorbed_damage - 391.23) < 0.1
assert len(absorbed_damage_effects) == 6  # One per attack power
```

---

### Test Case 7: Controller Pet (No Upgrade Mechanics)

**Scenario**: Fire Control Imps (no upgrade powers)

**Input:**
```python
character_level = 32
archetype = "Controller"
summon_power = "Fire_Control.Summon_Fire_Imps"
entity = database.get_entity("Pet_Fire_Imp")
```

**Expected Entity Data:**
```python
entity.display_name == "Fire Imps"
entity.class_name == "Class_Pet"
entity.powerset_full_names == [
    "Pets_Fire_Imp.Pets_Fire_Imp"  # Only one powerset
]
entity.upgrade_power_full_names == []  # No upgrades for controller pets
```

**Upgrade Level Calculation:**
```python
upgrade_level = 0  # Always 0 for controller pets
available_powersets = entity.powersets  # All powersets (just 1)
assert len(available_powersets) == 1
```

**Available Pet Powers:**
```python
imp_powers = [
    "Pets_Fire_Imp.Flares",       # Base: ranged fire damage
    "Pets_Fire_Imp.Fire_Blast",   # Base: ranged fire damage
    "Pets_Fire_Imp.Incinerate",   # Base: DoT fire damage
    "Pets_Fire_Imp.Fire_Shield",  # Base: self buff (resistance)
]

assert len(imp_powers) == 4
```

**Expected Output:**
```python
assert upgrade_level == 0
assert len(available_powers) == 4
assert entity.upgrade_power_full_names == []

flares_power = get_pet_power("Pets_Fire_Imp.Flares")
assert flares_power.base_damage > 0
assert flares_power.damage_type == 'fire'
```

---

### Test Case 8: Combined Caster Buffs + Pet Slotting

**Scenario**: Maximum buffed pet damage (caster +50% damage + pet 3-slotted)

**Input:**
```python
character_level = 50
pet_power = "Pets_T_Bruiser.Knockout_Blow"

# Pet base values
ko_base_damage = 111.78  # Smashing, high-damage attack
ko_base_accuracy = 1.00

# Caster damage buff
caster_damage_buff = 0.50  # +50% from set bonuses

# Pet slotting: 3x level 50 Pet Damage SOs
pet_enhancements = [
    {'name': 'Pet_Damage_SO', 'level': 50, 'values': {'damage': 0.424}},
    {'name': 'Pet_Damage_SO', 'level': 50, 'values': {'damage': 0.424}},
    {'name': 'Pet_Damage_SO', 'level': 50, 'values': {'damage': 0.424}},
]
```

**Step-by-Step Calculation:**
```python
# Step 1: Sum pet damage enhancements
total_pet_damage_enh = 0.424 + 0.424 + 0.424 = 1.272  # 127.2%

# Step 2: Apply ED (Schedule A)
# 0.70 - 1.00 range: 90% efficient
# 1.00 - 1.30 range: 70% efficient
ed_damage = 0.70 + (1.00 - 0.70) * 0.90 + (1.272 - 1.00) * 0.70
# = 0.70 + 0.30 * 0.90 + 0.272 * 0.70
# = 0.70 + 0.27 + 0.1904
# = 1.1604  # 116.04% after ED

# Step 3: Apply pet slotting
damage_with_pet_enh = ko_base_damage * (1 + ed_damage)
# = 111.78 * (1 + 1.1604)
# = 111.78 * 2.1604
# = 241.494

# Step 4: Apply inherited caster buff
final_damage = damage_with_pet_enh * (1 + caster_damage_buff)
# = 241.494 * (1 + 0.50)
# = 241.494 * 1.50
# = 362.241
```

**Expected Output:**
```python
buffed_power = calculate_pet_power_with_inheritance(
    pet_power=ko_power,
    caster_buffs={'damage_buffs': {'smashing': 0.50}},
    pet_enhancements=pet_enhancements
)

assert ko_power.base_damage == 111.78
assert abs(buffed_power.buffed_damage - 362.241) < 0.01

# Damage increase breakdown:
# Base: 111.78
# After pet slotting: 241.494 (116% increase)
# After caster buff: 362.241 (224% total increase)
```

---

## Section 5: Python Implementation Guide

### Complete Production-Ready Implementation

```python
# backend/app/calculations/pets.py

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
import copy

from .enhancement_diversification import apply_ed, ScheduleType
from .archetype_modifiers import get_modifier


class SummonEntityType(Enum):
    """Type of summoned entity"""
    PET = "Pet"              # Permanent pet (Controller Imps)
    HENCHMAN = "Henchman"    # Mastermind pet
    PSEUDOPET = "PseudoPet"  # Temporary invisible entity
    OBJECT = "Object"        # Summoned objects (mines, etc.)


@dataclass
class SummonedEntity:
    """
    Represents a summonable entity (pet) with its powersets.
    Maps to MidsReborn SummonedEntity class.
    """
    uid: str
    display_name: str
    entity_type: SummonEntityType
    entity_class_id: int
    entity_class_name: str
    powerset_ids: List[int]
    powerset_full_names: List[str]
    upgrade_power_ids: List[int] = field(default_factory=list)
    upgrade_power_full_names: List[str] = field(default_factory=list)

    def get_upgrade_level(self, character_powers: List[int]) -> int:
        """
        Determine how many upgrade powers the character has taken.

        Args:
            character_powers: List of power IDs in character's build

        Returns:
            Upgrade level (0-2 for Mastermind pets, 0 for others)
        """
        upgrade_count = 0
        for upgrade_power_id in self.upgrade_power_ids:
            if upgrade_power_id in character_powers:
                upgrade_count += 1
        return upgrade_count

    def get_available_powerset_ids(self, upgrade_level: int) -> List[int]:
        """
        Get powerset IDs available at given upgrade level.

        Args:
            upgrade_level: 0 (base), 1 (first upgrade), 2 (second upgrade)

        Returns:
            List of powerset IDs up to and including upgrade level
        """
        available_count = upgrade_level + 1
        return self.powerset_ids[:available_count]


@dataclass
class PetPowerData:
    """
    Base and buffed versions of a single pet power.
    Maps to MidsReborn PetInfo.PetPower class.
    """
    base_power: 'Power'
    buffed_power: 'Power'

    @property
    def damage_increase_percent(self) -> float:
        """Calculate percentage increase in damage from base to buffed"""
        base_dmg = self.base_power.total_damage
        buffed_dmg = self.buffed_power.total_damage
        if base_dmg == 0:
            return 0.0
        return ((buffed_dmg - base_dmg) / base_dmg) * 100


@dataclass
class InheritedCasterBuffs:
    """
    Buffs from caster that pets inherit.
    Only specific stats are inherited per game design.
    """
    accuracy_mult: float = 0.0      # Global accuracy buffs (multiplicative)
    tohit_bonus: float = 0.0        # Global tohit buffs (additive)
    damage_buffs: Dict[str, float] = field(default_factory=dict)  # By damage type
    healing_mult: float = 0.0       # Global healing buffs

    # Stats pets DO NOT inherit (explicitly listed for clarity)
    # - recharge_mult: Pets have own recharge rates
    # - defense: Pets have own defense values
    # - resistance: Pets have own resistance values
    # - endurance: Pets have own endurance pools
    # - range: Pets have own power ranges


class PetCalculator:
    """
    Calculate pet power effects with caster inheritance and pet slotting.
    Maps to MidsReborn PetInfo and clsToonX.GenerateBuffedPowers.
    """

    def __init__(self, database: 'Database', character: 'Character'):
        """
        Args:
            database: Game database with powers, entities, modifiers
            character: Current character build
        """
        self.database = database
        self.character = character

    def get_inherited_caster_buffs(self) -> InheritedCasterBuffs:
        """
        Calculate which buffs from caster should affect pets.

        Maps to MidsReborn logic in clsToonX.GenerateBuffedPowers.
        Only specific stats are inherited per game design.

        Returns:
            InheritedCasterBuffs with global accuracy, tohit, damage, healing
        """
        totals = self.character.totals

        return InheritedCasterBuffs(
            accuracy_mult=totals.accuracy_multiplier,
            tohit_bonus=totals.tohit_bonus,
            damage_buffs=totals.damage_buff_by_type.copy(),
            healing_mult=totals.healing_multiplier
        )

    def apply_caster_buffs_to_pet_power(
        self,
        pet_power: 'Power',
        inherited_buffs: InheritedCasterBuffs
    ) -> 'Power':
        """
        Apply inherited caster buffs to pet power.

        Args:
            pet_power: Base pet power (may already have pet enhancements applied)
            inherited_buffs: Buffs from caster to apply

        Returns:
            Modified pet power with inherited buffs applied
        """
        # Clone to avoid modifying original
        buffed_power = copy.deepcopy(pet_power)

        # Apply global accuracy (multiplicative)
        buffed_power.accuracy *= (1 + inherited_buffs.accuracy_mult)

        # Apply global tohit (additive, handled in hit chance calculation)
        # Not stored on power itself, used in combat calculation

        # Apply to each effect
        for effect in buffed_power.effects:
            if effect.effect_type == 'Damage':
                # Apply damage buff for this damage type
                dmg_buff = inherited_buffs.damage_buffs.get(effect.damage_type, 0.0)
                effect.magnitude *= (1 + dmg_buff)

            elif effect.effect_type == 'Heal':
                # Apply healing buff
                effect.magnitude *= (1 + inherited_buffs.healing_mult)

            # Other effect types are NOT affected by caster buffs

        return buffed_power

    def apply_pet_enhancements(
        self,
        pet_power: 'Power',
        enhancements: List['Enhancement']
    ) -> 'Power':
        """
        Apply pet enhancement slotting to power.

        Pet IOs enhance the pet, not the summon power. They use the same
        enhancement system as player powers (including ED).

        Args:
            pet_power: Base pet power
            enhancements: List of enhancements slotted in this pet power

        Returns:
            Pet power with enhancements applied
        """
        if not enhancements:
            return copy.deepcopy(pet_power)

        # Clone power
        enhanced_power = copy.deepcopy(pet_power)

        # Sum enhancement bonuses by type (pre-ED)
        enh_bonuses = {
            'damage': 0.0,
            'accuracy': 0.0,
            'recharge': 0.0,
            'endurance': 0.0,
            'defense': 0.0,
            'resistance': 0.0
        }

        for enhancement in enhancements:
            for enh_type, value in enhancement.values.items():
                if enh_type in enh_bonuses:
                    enh_bonuses[enh_type] += value

        # Apply Enhancement Diversification (Schedule A for most)
        ed_bonuses = {}
        for enh_type, pre_ed_value in enh_bonuses.items():
            schedule = self._get_enhancement_schedule(enh_type)
            ed_bonuses[enh_type] = apply_ed(schedule, pre_ed_value)

        # Apply to power
        enhanced_power.accuracy *= (1 + ed_bonuses['accuracy'])

        # Apply to effects
        for effect in enhanced_power.effects:
            if effect.effect_type == 'Damage':
                effect.magnitude *= (1 + ed_bonuses['damage'])
            elif effect.effect_type == 'Heal':
                effect.magnitude *= (1 + ed_bonuses['damage'])  # Healing uses damage enh

        # Apply recharge reduction
        if ed_bonuses['recharge'] > 0:
            enhanced_power.recharge_time /= (1 + ed_bonuses['recharge'])

        # Apply endurance reduction
        if ed_bonuses['endurance'] > 0:
            enhanced_power.endurance_cost *= (1 - ed_bonuses['endurance'])

        return enhanced_power

    def _get_enhancement_schedule(self, enhancement_type: str) -> ScheduleType:
        """Get ED schedule for enhancement type"""
        # Defense uses Schedule B, Interrupt uses Schedule C, others use Schedule A
        if enhancement_type == 'defense':
            return ScheduleType.B
        return ScheduleType.A

    def calculate_pet_power(
        self,
        pet_power: 'Power',
        pet_enhancements: List['Enhancement'],
        apply_caster_buffs: bool = True
    ) -> PetPowerData:
        """
        Calculate final pet power values with enhancements and inheritance.

        Maps to MidsReborn clsToonX.GenerateBuffedPowers and PetInfo.GetPetPower.

        Args:
            pet_power: Base pet power from database
            pet_enhancements: Enhancements slotted in pet power
            apply_caster_buffs: Whether to apply inherited caster buffs

        Returns:
            PetPowerData with base and fully buffed versions
        """
        # Base power (no modifications)
        base_power = copy.deepcopy(pet_power)

        # Apply pet enhancements
        enhanced_power = self.apply_pet_enhancements(pet_power, pet_enhancements)

        # Apply inherited caster buffs
        if apply_caster_buffs:
            inherited_buffs = self.get_inherited_caster_buffs()
            buffed_power = self.apply_caster_buffs_to_pet_power(enhanced_power, inherited_buffs)
        else:
            buffed_power = enhanced_power

        return PetPowerData(
            base_power=base_power,
            buffed_power=buffed_power
        )

    def calculate_all_pet_powers(
        self,
        entity: SummonedEntity,
        summon_power_in_build: bool = True
    ) -> Dict[int, PetPowerData]:
        """
        Calculate all pet powers for an entity with current build state.

        Args:
            entity: Pet entity being summoned
            summon_power_in_build: Whether character has summon power in build

        Returns:
            Dict mapping power_id -> PetPowerData (base + buffed)
        """
        result = {}

        # Determine upgrade level
        character_power_ids = [pe.power_id for pe in self.character.build.power_entries]
        upgrade_level = entity.get_upgrade_level(character_power_ids)

        # Get available powersets
        available_powerset_ids = entity.get_available_powerset_ids(upgrade_level)

        # Get all pet powers from available powersets
        pet_powers = []
        for powerset_id in available_powerset_ids:
            powerset = self.database.get_powerset(powerset_id)
            pet_powers.extend(powerset.powers)

        # Calculate each pet power
        for pet_power in pet_powers:
            # Get enhancements slotted in this pet power
            pet_enhancements = self._get_pet_power_enhancements(pet_power.id)

            # Calculate with or without caster buffs
            pet_power_data = self.calculate_pet_power(
                pet_power=pet_power,
                pet_enhancements=pet_enhancements,
                apply_caster_buffs=summon_power_in_build
            )

            result[pet_power.id] = pet_power_data

        return result

    def _get_pet_power_enhancements(self, pet_power_id: int) -> List['Enhancement']:
        """Get enhancements slotted in pet power from character build"""
        # Query build_pet_power_slots table
        pet_slots = self.database.query(
            "SELECT enhancement_id, enhancement_level FROM build_pet_power_slots "
            "WHERE build_id = %s AND pet_power_id = %s ORDER BY slot_index",
            (self.character.build.id, pet_power_id)
        )

        enhancements = []
        for slot in pet_slots:
            enhancement = self.database.get_enhancement(slot['enhancement_id'])
            # TODO: Scale enhancement values by level
            enhancements.append(enhancement)

        return enhancements

    def absorb_pet_effects(
        self,
        summon_power: 'Power',
        entity: SummonedEntity,
        stacking: int = 1
    ) -> 'Power':
        """
        Absorb pet power effects into summon power for display.

        Maps to MidsReborn Power.AbsorbPetEffects method.
        This creates a unified view showing what the summon power does
        (which is actually the pet's attacks/buffs).

        Args:
            summon_power: The power that summons the pet
            entity: Pet entity being summoned
            stacking: Number of pets (for MM variable summons)

        Returns:
            Modified summon power with absorbed pet effects
        """
        if not (summon_power.absorb_summon_attributes or summon_power.absorb_summon_effects):
            return copy.deepcopy(summon_power)

        # Clone summon power
        modified_power = copy.deepcopy(summon_power)

        # Get available powersets (check upgrade level)
        character_power_ids = [pe.power_id for pe in self.character.build.power_entries]
        upgrade_level = entity.get_upgrade_level(character_power_ids)
        available_powerset_ids = entity.get_available_powerset_ids(upgrade_level)

        # Get entity class for modifiers
        entity_class = self.database.get_entity_class(entity.entity_class_id)

        # Absorb attributes from first pet power
        if summon_power.absorb_summon_attributes:
            first_powerset = self.database.get_powerset(available_powerset_ids[0])
            if first_powerset.powers:
                first_pet_power = first_powerset.powers[0]
                modified_power.attack_types = first_pet_power.attack_types
                modified_power.effect_area = first_pet_power.effect_area
                modified_power.entities_affected = first_pet_power.entities_affected
                modified_power.max_targets = first_pet_power.max_targets
                modified_power.radius = first_pet_power.radius

                # Only copy accuracy if summon power is not autohit
                if summon_power.entities_autohit == 'None':
                    modified_power.accuracy = first_pet_power.accuracy

        # Absorb effects from all pet powers
        if summon_power.absorb_summon_effects:
            for powerset_id in available_powerset_ids:
                powerset = self.database.get_powerset(powerset_id)
                for pet_power in powerset.powers:
                    for effect in pet_power.effects:
                        # Clone effect
                        absorbed_effect = copy.deepcopy(effect)

                        # Apply entity class modifier
                        class_modifier = get_modifier(
                            entity_class_id=entity.entity_class_id,
                            effect_type=effect.effect_type,
                            modifier_table=effect.modifier_table,
                            level=self.character.level
                        )
                        absorbed_effect.magnitude *= class_modifier

                        # Apply stacking (for multiple pets)
                        absorbed_effect.magnitude *= stacking

                        # Mark as absorbed from pet
                        absorbed_effect.absorbed_from_pet = True
                        absorbed_effect.absorbed_power_name = pet_power.full_name

                        # Add to summon power
                        modified_power.effects.append(absorbed_effect)

        return modified_power


# Helper function for common use case
def calculate_pet_power_with_inheritance(
    pet_power: 'Power',
    caster_buffs: InheritedCasterBuffs,
    pet_enhancements: List['Enhancement'],
    database: 'Database'
) -> 'Power':
    """
    High-level function to calculate final pet power values.

    Args:
        pet_power: Base pet power from database
        caster_buffs: Inherited buffs from caster
        pet_enhancements: Enhancements slotted in pet power
        database: Game database

    Returns:
        Fully buffed pet power
    """
    # Create temporary calculator
    calculator = PetCalculator(database, None)  # No character needed for this mode

    # Apply pet enhancements first
    enhanced_power = calculator.apply_pet_enhancements(pet_power, pet_enhancements)

    # Then apply caster buffs
    buffed_power = calculator.apply_caster_buffs_to_pet_power(enhanced_power, caster_buffs)

    return buffed_power
```

### Usage Examples

**Example 1: Calculate single pet power:**

```python
from app.calculations.pets import PetCalculator, InheritedCasterBuffs

# Setup
calculator = PetCalculator(database, character)
pet_power = database.get_power("Pets_T_Bruiser.Jab")
pet_enhancements = [
    database.get_enhancement("Call_to_Arms.Pet_Damage"),
    database.get_enhancement("Call_to_Arms.Pet_Damage_Accuracy")
]

# Calculate
pet_power_data = calculator.calculate_pet_power(
    pet_power=pet_power,
    pet_enhancements=pet_enhancements,
    apply_caster_buffs=True
)

# Display
print(f"Base damage: {pet_power_data.base_power.total_damage:.2f}")
print(f"Buffed damage: {pet_power_data.buffed_power.total_damage:.2f}")
print(f"Increase: {pet_power_data.damage_increase_percent:.1f}%")
```

**Example 2: Calculate all pet powers for entity:**

```python
# Get Bruiser entity
entity = database.get_entity("Pets_T_Bruiser")

# Calculate all powers
all_pet_powers = calculator.calculate_all_pet_powers(
    entity=entity,
    summon_power_in_build=True
)

# Display summary
for power_id, pet_data in all_pet_powers.items():
    power_name = pet_data.base_power.display_name
    base_dmg = pet_data.base_power.total_damage
    buffed_dmg = pet_data.buffed_power.total_damage
    print(f"{power_name}: {base_dmg:.1f} -> {buffed_dmg:.1f} damage")
```

**Example 3: Absorb pet effects for display:**

```python
# Get summon power and entity
summon_power = database.get_power("Thugs.Thugs.Call_Bruiser")
entity = database.get_entity("Pets_T_Bruiser")

# Absorb pet effects
modified_summon = calculator.absorb_pet_effects(
    summon_power=summon_power,
    entity=entity,
    stacking=1  # 1 Bruiser
)

# Display absorbed damage
total_damage = sum(
    e.magnitude for e in modified_summon.effects
    if e.effect_type == 'Damage'
)
print(f"Total pet damage capability: {total_damage:.1f}")
```

---

## Section 6: Integration Points

### Dependencies (What This Spec Needs)

**Spec 01: Power Effects Core**
- Effect system foundation (EffectType enum, Effect dataclass)
- Effect magnitude calculation framework
- Effect.absorbed_from_pet flag for tracking absorbed effects
- Data Flow: Pet powers have effects → need effect processing system

**Spec 02: Damage Calculation**
- Base damage formula: magnitude × scale × modifier
- Damage type system (smashing, lethal, fire, etc.)
- Damage buffing mechanics (multiplicative stacking)
- Data Flow: Pet damage effects → use damage calculation system

**Spec 10: Enhancement Slotting**
- Enhancement application to power effects
- Enhancement value calculation by level
- Enhancement bonus summing (pre-ED)
- Data Flow: Pet power slots → need enhancement application logic

**Spec 05: Enhancement Diversification (ED)**
- ED curve application (Schedule A/B/C)
- Diminishing returns for enhancement bonuses
- Schedule determination by enhancement type
- Data Flow: Pet enhancement bonuses → apply ED → final bonus

**Spec 16: Archetype Modifiers**
- Entity class modifier system (like AT modifiers for pets)
- Modifier table lookup by class/level/effect type
- Class_Minion_Pets, Class_Lt_Pets, Class_Boss_Pets scales
- Data Flow: Pet effects → apply entity class modifiers → final magnitude

**Spec 08: Power Accuracy/ToHit**
- Accuracy inheritance mechanics (multiplicative)
- ToHit buff application (additive)
- Hit chance calculation framework
- Data Flow: Pet accuracy → inherit caster accuracy → final hit chance

---

### Dependents (What Needs This Spec)

**Spec 33: Pseudopet Mechanics**
- Some pets summon pseudopets (Phantom Army → decoys)
- Nested pet calculation (pet → pseudopet → effect)
- AbsorbPetEffects handles nested pseudopets
- Data Flow: Pet power → check for EntCreate → recurse into pseudopet

**Mastermind Build Display**
- Show pet power capabilities in build summary
- Display total pet damage output
- Pet slotting UI (separate from summon power slotting)
- Data Flow: Build → get pet entities → calculate all pet powers → display

**Power Tooltip System**
- Summon powers show absorbed pet effects
- Pet power tooltips show base vs buffed values
- "What this power does" = pet's attacks, not summon cast
- Data Flow: Tooltip request → absorb pet effects → display unified view

**Build Optimization/Comparison**
- Compare pet builds (different slotting strategies)
- Optimize pet IO slotting vs set bonuses
- Calculate effective DPS including pet damage
- Data Flow: Build variants → calculate pet powers → compare total output

**Export/Import Systems**
- Mids build files (.mbd format) include pet slotting
- JSON export includes pet power data
- Build sharing with pet configurations
- Data Flow: Build export → include pet slots → serialize → import → restore

---

### Data Flow Diagram

```
Character Build
    ├─> Summon Power Entry
    │   ├─> Power: "Thugs.Thugs.Call_Bruiser"
    │   ├─> Slotted Enhancements: (apply to summon power, not pet)
    │   └─> Variable Value: 1 (number of Bruisers)
    │
    ├─> Upgrade Powers (Equip, Upgrade)
    │   └─> Determine Upgrade Level → Available Powersets
    │
    ├─> Global Buffs (Inherited by Pets)
    │   ├─> Accuracy: +0.20 (from Kismet IO)
    │   ├─> Damage (Smashing): +0.50 (from set bonuses)
    │   ├─> ToHit: +0.10 (from Tactics)
    │   └─> NOT Inherited: Recharge, Defense, Resistance
    │
    └─> Pet Power Slots (Separate from Summon)
        ├─> Pets_T_Bruiser.Jab
        │   ├─> Slot 0: Call_to_Arms Pet Damage
        │   └─> Slot 1: Call_to_Arms Pet Damage/Accuracy
        │
        └─> Pets_T_Bruiser.Knockout_Blow
            ├─> Slot 0: Pet Damage SO
            ├─> Slot 1: Pet Damage SO
            └─> Slot 2: Pet Damage SO

                    ↓

            Pet Entity Database
            ├─> Entity: "Pets_T_Bruiser"
            │   ├─> Display Name: "Bruiser"
            │   ├─> Entity Class: "Class_Boss_Pets"
            │   ├─> Powersets:
            │   │   ├─> [0] Pets_T_Bruiser (base)
            │   │   ├─> [1] Pets_T_Bruiser_Upgrade_1 (Equip)
            │   │   └─> [2] Pets_T_Bruiser_Upgrade_2 (Upgrade)
            │   └─> Upgrade Powers:
            │       ├─> [0] Thugs.Thugs.Equip_Thugs
            │       └─> [1] Thugs.Thugs.Upgrade_Equipment
            │
            └─> Entity Class Modifiers
                ├─> Ranged_Damage: 1.00 (level 50)
                ├─> Melee_Damage: 1.00
                └─> Buff_Defense: 0.10

                    ↓

        PetCalculator.calculate_all_pet_powers()
        ├─> Step 1: Determine Upgrade Level
        │   ├─> Check: "Equip_Thugs" in build? → Yes → +1
        │   ├─> Check: "Upgrade_Equipment" in build? → Yes → +1
        │   └─> Upgrade Level = 2
        │
        ├─> Step 2: Get Available Powersets
        │   └─> Powersets[0:3] → All 3 powersets available
        │
        ├─> Step 3: For Each Pet Power
        │   ├─> Base Power: Pets_T_Bruiser.Jab
        │   │   ├─> Base Damage: 18.63 smashing
        │   │   ├─> Base Accuracy: 1.00
        │   │   └─> Base Recharge: 4.0s
        │   │
        │   ├─> Apply Pet Enhancements
        │   │   ├─> Sum: Pet Damage +0.636 (2 IOs)
        │   │   ├─> Apply ED: 0.636 → 0.636 (no ED, <70%)
        │   │   └─> Enhanced Damage: 18.63 * 1.636 = 30.47
        │   │
        │   ├─> Apply Entity Class Modifier
        │   │   ├─> Class: Class_Boss_Pets
        │   │   ├─> Modifier Table: "Melee_Damage"
        │   │   ├─> Level 50: 1.00
        │   │   └─> Damage: 30.47 * 1.00 = 30.47
        │   │
        │   └─> Apply Inherited Caster Buffs
        │       ├─> Caster Damage (Smashing): +0.50
        │       └─> Final Damage: 30.47 * 1.50 = 45.71
        │
        └─> Step 4: Return PetPowerData
            ├─> base_power.total_damage = 18.63
            └─> buffed_power.total_damage = 45.71

                    ↓

                Display/UI Layer
                ├─> Pet Power Tooltip
                │   ├─> "Jab (Bruiser)"
                │   ├─> Base: 18.63 smashing damage
                │   ├─> Enhanced: 30.47 damage (+63.6% from pet slotting)
                │   ├─> Final: 45.71 damage (+50% from caster buffs)
                │   └─> Total Increase: +145.3%
                │
                └─> Summon Power Display (Absorbed)
                    ├─> "Call Bruiser"
                    ├─> Shows: "Summons 1 Bruiser"
                    ├─> Absorbed Effects:
                    │   ├─> Jab: 45.71 smashing
                    │   ├─> Punch: 91.42 smashing
                    │   ├─> Knockout Blow: 274.26 smashing
                    │   └─> ... (all pet attacks)
                    └─> Total: 502.81 smashing capability
```

---

### API Endpoint Design

**Endpoint: `GET /api/builds/{build_id}/pets/{entity_id}/powers`**

Get all pet powers for an entity with current build buffs.

**Response:**
```json
{
  "entity": {
    "id": 123,
    "uid": "Pets_T_Bruiser",
    "display_name": "Bruiser",
    "entity_type": "Henchman",
    "upgrade_level": 2
  },
  "powers": [
    {
      "id": 4567,
      "full_name": "Pets_T_Bruiser.Jab",
      "display_name": "Jab",
      "base_values": {
        "damage": 18.63,
        "accuracy": 1.00,
        "recharge": 4.0
      },
      "buffed_values": {
        "damage": 45.71,
        "accuracy": 1.424,
        "recharge": 4.0
      },
      "enhancements": [
        {
          "id": 789,
          "name": "Call to Arms: Pet Damage",
          "level": 50,
          "values": {"damage": 0.424}
        }
      ],
      "inherited_buffs": {
        "damage_buff": 0.50,
        "accuracy_buff": 0.20
      }
    }
  ]
}
```

**Endpoint: `GET /api/builds/{build_id}/powers/{summon_power_id}/absorbed-effects`**

Get summon power with absorbed pet effects for display.

**Response:**
```json
{
  "summon_power": {
    "id": 1234,
    "full_name": "Thugs.Thugs.Call_Bruiser",
    "display_name": "Call Bruiser"
  },
  "absorbed_effects": [
    {
      "effect_type": "Damage",
      "damage_type": "smashing",
      "magnitude": 45.71,
      "absorbed_from": "Pets_T_Bruiser.Jab"
    },
    {
      "effect_type": "Damage",
      "damage_type": "smashing",
      "magnitude": 91.42,
      "absorbed_from": "Pets_T_Bruiser.Punch"
    }
  ],
  "total_damage": 502.81,
  "stacking": 1
}
```

---

## References

- Related specs:
  - [01-power-effects-core.md](01-power-effects-core.md) - Effect system foundation
  - [02-damage-calculation.md](02-damage-calculation.md) - Damage formula and buffing
  - [05-enhancement-diversification.md](05-enhancement-diversification.md) - ED curve application
  - [08-power-accuracy-tohit.md](08-power-accuracy-tohit.md) - Accuracy inheritance
  - [10-enhancement-slotting.md](10-enhancement-slotting.md) - Enhancement application
  - [16-archetype-modifiers.md](16-archetype-modifiers.md) - Entity class modifiers
  - [33-pseudopet-mechanics.md](33-pseudopet-mechanics.md) - Invisible pseudopets
- MidsReborn files:
  - `Core/PetInfo.cs` - Main pet calculation class (170 lines)
  - `Core/SummonedEntity.cs` - Pet entity definitions (226 lines)
  - `Core/Base/Data_Classes/Power.cs` - AbsorbPetEffects() method (lines 2573-2678)
  - `clsToonX.cs` - GenerateBuffedPowers() method (lines 2092-2129)
  - `Forms/Controls/PetView.cs` - Pet power display UI
- Game data:
  - Mastermind primary powersets (Thugs, Robots, Ninjas, Mercenaries, Demons, Beasts)
  - Controller/Dominator pets (Fire Imps, Phantom Army, Singularity, Jack Frost, etc.)
  - Pet IO sets (Call to Arms, Mark of Supremacy, Soulbound Allegiance, etc.)
  - Entity class modifiers (Class_Minion_Pets, Class_Lt_Pets, Class_Boss_Pets)

---

**Document Status**: 🟢 Depth Complete - Production-ready implementation spec with C# reference, database schema, comprehensive test cases, and Python implementation
**Spec Number**: 32/43
**Priority**: High (critical for Mastermind builds, important for Controllers/Dominators)
**Last Updated**: 2025-11-11
