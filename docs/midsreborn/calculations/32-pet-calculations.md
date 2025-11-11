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

## References

- Related specs:
  - [01-power-effects-core.md](01-power-effects-core.md) - Effect system foundation
  - [11-enhancement-slotting.md](11-enhancement-slotting.md) - Enhancement application to powers
  - [16-archetype-modifiers.md](16-archetype-modifiers.md) - Entity class modifiers (pet version of AT modifiers)
  - [33-pseudopet-mechanics.md](33-pseudopet-mechanics.md) - Invisible pseudopets (different from real pets)
- MidsReborn files:
  - `Core/PetInfo.cs` - Main pet calculation class
  - `Core/SummonedEntity.cs` - Pet entity definitions
  - `Core/Base/Data_Classes/Power.cs` - AbsorbPetEffects() method
  - `Forms/Controls/PetView.cs` - Pet power display UI
- Game data:
  - Mastermind primary powersets (Thugs, Robots, Ninjas, Mercenaries, Demons, Beasts)
  - Controller/Dominator pets (Fire Imps, Phantom Army, Singularity, Jack Frost, etc.)
  - Pet IO sets (Call to Arms, Mark of Supremacy, Soulbound Allegiance, etc.)

---

**Document Status**: 🟡 Breadth Complete - High-level spec for pet calculations with inheritance, upgrade mechanics, and separate slotting
**Spec Number**: 32/43
**Priority**: High (critical for Mastermind builds, important for Controllers/Dominators)
