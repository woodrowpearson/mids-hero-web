"""JSON export functionality for MHD parsed data."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Union

from .main_database_parser import MainDatabase
from .enhancement_database_parser import EnhancementDatabase
from .salvage_parser import SalvageDatabase
from .recipe_parser import RecipeDatabase
from .text_mhd_parser import TextMhdFile


class MhdJsonExporter:
    """Exports MHD parsed data to JSON format for comparison and validation."""
    
    def __init__(self, indent: int = 2):
        """Initialize the exporter with formatting options."""
        self.indent = indent
    
    def export_main_database(self, db: MainDatabase, output_path: Union[str, Path]) -> None:
        """Export main database to JSON file."""
        data = self._main_database_to_dict(db)
        self._write_json(data, output_path)
    
    def export_enhancement_database(self, db: EnhancementDatabase, 
                                  output_path: Union[str, Path]) -> None:
        """Export enhancement database to JSON file."""
        data = self._enhancement_database_to_dict(db)
        self._write_json(data, output_path)
    
    def export_salvage_database(self, db: SalvageDatabase, 
                               output_path: Union[str, Path]) -> None:
        """Export salvage database to JSON file."""
        data = self._salvage_database_to_dict(db)
        self._write_json(data, output_path)
    
    def export_recipe_database(self, db: RecipeDatabase, 
                              output_path: Union[str, Path]) -> None:
        """Export recipe database to JSON file."""
        data = self._recipe_database_to_dict(db)
        self._write_json(data, output_path)
    
    def export_text_mhd(self, text_file: TextMhdFile, 
                       output_path: Union[str, Path]) -> None:
        """Export text MHD file to JSON."""
        data = {
            "version": text_file.version,
            "headers": text_file.headers,
            "data": text_file.data
        }
        self._write_json(data, output_path)
    
    def _main_database_to_dict(self, db: MainDatabase) -> Dict[str, Any]:
        """Convert main database to dictionary."""
        return {
            "header": db.header,
            "version": db.version,
            "date": self._serialize_date(db.date),
            "issue": db.issue,
            "page_vol": db.page_vol,
            "page_vol_text": db.page_vol_text,
            "statistics": {
                "archetype_count": len(db.archetypes),
                "powerset_count": len(db.powersets),
                "power_count": len(db.powers),
                "summon_count": len(db.summons)
            },
            "archetypes": [self._archetype_to_dict(a) for a in db.archetypes],
            "powersets": [self._powerset_to_dict(ps) for ps in db.powersets],
            "powers": [self._power_to_dict(p) for p in db.powers],
            "summons": [self._summon_to_dict(s) for s in db.summons]
        }
    
    def _archetype_to_dict(self, archetype) -> Dict[str, Any]:
        """Convert archetype to dictionary."""
        return {
            "display_name": archetype.display_name,
            "hitpoints": archetype.hitpoints,
            "hp_cap": archetype.hp_cap,
            "desc_long": archetype.desc_long,
            "res_cap": archetype.res_cap,
            "origins": archetype.origins,
            "class_name": archetype.class_name,
            "class_type": archetype.class_type,
            "column": archetype.column,
            "desc_short": archetype.desc_short,
            "primary_group": archetype.primary_group,
            "secondary_group": archetype.secondary_group,
            "playable": archetype.playable,
            "recharge_cap": archetype.recharge_cap,
            "damage_cap": archetype.damage_cap,
            "recovery_cap": archetype.recovery_cap,
            "regen_cap": archetype.regen_cap,
            "threat_cap": archetype.threat_cap,
            "resist_cap": archetype.resist_cap,
            "damage_resist_cap": archetype.damage_resist_cap,
            "base_recovery": archetype.base_recovery,
            "base_regen": archetype.base_regen,
            "base_threat": archetype.base_threat,
            "perception_cap": archetype.perception_cap
        }
    
    def _powerset_to_dict(self, powerset) -> Dict[str, Any]:
        """Convert powerset to dictionary."""
        return {
            "display_name": powerset.display_name,
            "archetype_index": powerset.archetype_index,
            "set_type": powerset.set_type.name,
            "set_type_value": powerset.set_type.value,
            "image_name": powerset.image_name,
            "full_name": powerset.full_name,
            "set_name": powerset.set_name,
            "description": powerset.description,
            "sub_name": powerset.sub_name,
            "at_class": powerset.at_class,
            "uid_trunk_set": powerset.uid_trunk_set,
            "uid_link_secondary": powerset.uid_link_secondary,
            "mutex_list": [{"name": m[0], "index": m[1]} for m in powerset.mutex_list]
        }
    
    def _power_to_dict(self, power) -> Dict[str, Any]:
        """Convert power to dictionary."""
        return {
            "full_name": power.full_name,
            "group_name": power.group_name,
            "set_name": power.set_name,
            "power_name": power.power_name,
            "display_name": power.display_name,
            "available": power.available,
            "requirement": {
                "class_name": power.requirement.class_name,
                "class_name_not": power.requirement.class_name_not,
                "classes_required": power.requirement.classes_required,
                "classes_disallowed": power.requirement.classes_disallowed,
                "power_ids": power.requirement.power_ids,
                "power_ids_not": power.requirement.power_ids_not
            },
            "power_type": power.power_type.name,
            "power_type_value": power.power_type.value,
            "accuracy": power.accuracy,
            "attack_types": power.attack_types,
            "group_membership": power.group_membership,
            "entities_affected": power.entities_affected,
            "entities_auto_hit": power.entities_auto_hit,
            "target": power.target,
            "target_line_special_range": power.target_line_special_range,
            "range": power.range,
            "range_secondary": power.range_secondary,
            "end_cost": power.end_cost,
            "interrupt_time": power.interrupt_time,
            "cast_time": power.cast_time,
            "recharge_time": power.recharge_time,
            "base_recharge_time": power.base_recharge_time,
            "activate_period": power.activate_period,
            "effect_area": power.effect_area,
            "radius": power.radius,
            "arc": power.arc,
            "max_targets": power.max_targets,
            "max_boosts": power.max_boosts,
            "cast_flags": power.cast_flags,
            "ai_report": power.ai_report,
            "num_effects": power.num_effects,
            "effect_count": len(power.effects),
            "desc_short": power.desc_short,
            "desc_long": power.desc_long,
            "set_types": power.set_types,
            "click_buff": power.click_buff,
            "always_toggle": power.always_toggle,
            "level": power.level,
            "allow_front_loading": power.allow_front_loading,
            "forced_class": power.forced_class,
            "hidden_power": power.hidden_power
        }
    
    def _summon_to_dict(self, summon) -> Dict[str, Any]:
        """Convert summon to dictionary."""
        return {
            "uid": summon.uid,
            "display_name": summon.display_name,
            "entity_type": summon.entity_type,
            "class_name": summon.class_name,
            "powerset_full_names": summon.powerset_full_names,
            "upgrade_power_full_names": summon.upgrade_power_full_names
        }
    
    def _enhancement_database_to_dict(self, db: EnhancementDatabase) -> Dict[str, Any]:
        """Convert enhancement database to dictionary."""
        return {
            "header": db.header,
            "version": db.version,
            "date": self._serialize_date(db.date),
            "statistics": {
                "enhancement_count": len(db.enhancements),
                "enhancement_set_count": len(db.enhancement_sets)
            },
            "enhancements": [self._enhancement_to_dict(e) for e in db.enhancements],
            "enhancement_sets": [self._enhancement_set_to_dict(s) for s in db.enhancement_sets]
        }
    
    def _enhancement_to_dict(self, enhancement) -> Dict[str, Any]:
        """Convert enhancement to dictionary."""
        return {
            "static_index": enhancement.static_index,
            "name": enhancement.name,
            "short_name": enhancement.short_name,
            "description": enhancement.description,
            "type_id": enhancement.type_id,
            "sub_type_id": enhancement.sub_type_id,
            "class_ids": enhancement.class_ids,
            "image": enhancement.image,
            "n_id_set": enhancement.n_id_set,
            "uid_set": enhancement.uid_set,
            "effect_chance": enhancement.effect_chance,
            "level_min": enhancement.level_min,
            "level_max": enhancement.level_max,
            "unique": enhancement.unique,
            "mut_ex_id": enhancement.mut_ex_id,
            "buff_mode": enhancement.buff_mode,
            "effects": [
                {
                    "mode": eff.mode,
                    "buff_mode": eff.buff_mode,
                    "enhance_id": eff.enhance_id,
                    "enhance_sub_id": eff.enhance_sub_id,
                    "schedule": eff.schedule,
                    "multiplier": eff.multiplier,
                    "has_fx": eff.fx is not None
                } for eff in enhancement.effects
            ],
            "uid": enhancement.uid,
            "recipe_name": enhancement.recipe_name,
            "superior": enhancement.superior,
            "is_proc": enhancement.is_proc,
            "is_scalable": enhancement.is_scalable
        }
    
    def _enhancement_set_to_dict(self, enh_set) -> Dict[str, Any]:
        """Convert enhancement set to dictionary."""
        return {
            "display_index": enh_set.display_index,
            "display_name": enh_set.display_name,
            "short_name": enh_set.short_name,
            "description": enh_set.description,
            "set_type": enh_set.set_type,
            "enhancement_indices": enh_set.enhancement_indices,
            "bonuses": enh_set.bonuses,
            "bonus_min": enh_set.bonus_min,
            "bonus_max": enh_set.bonus_max,
            "special_bonuses": enh_set.special_bonuses,
            "uid_set": enh_set.uid_set,
            "level_min": enh_set.level_min,
            "level_max": enh_set.level_max
        }
    
    def _salvage_database_to_dict(self, db: SalvageDatabase) -> Dict[str, Any]:
        """Convert salvage database to dictionary."""
        return {
            "header": db.header,
            "version": db.version,
            "salvage_count": len(db.salvage_items),
            "salvage_items": [
                {
                    "internal_name": s.internal_name,
                    "display_name": s.display_name,
                    "rarity": s.rarity.name,
                    "rarity_value": s.rarity.value,
                    "salvage_type": s.salvage_type.name,
                    "salvage_type_value": s.salvage_type.value,
                    "description": s.description
                } for s in db.salvage_items
            ]
        }
    
    def _recipe_database_to_dict(self, db: RecipeDatabase) -> Dict[str, Any]:
        """Convert recipe database to dictionary."""
        return {
            "header": db.header,
            "version": db.version,
            "recipe_count": len(db.recipes),
            "recipes": [
                {
                    "recipe_id": r.recipe_id,
                    "name": r.name,
                    "level_requirement": r.level_requirement,
                    "rarity": r.rarity.name,
                    "rarity_value": r.rarity.value,
                    "ingredient_count": len(r.ingredients),
                    "ingredients": r.ingredients,
                    "quantities": r.quantities,
                    "crafting_cost": r.crafting_cost,
                    "reward": r.reward
                } for r in db.recipes
            ]
        }
    
    def _serialize_date(self, date: Union[int, datetime]) -> Union[int, str]:
        """Serialize date to JSON-compatible format."""
        if isinstance(date, datetime):
            return date.isoformat()
        return date
    
    def _write_json(self, data: Dict[str, Any], output_path: Union[str, Path]) -> None:
        """Write data to JSON file."""
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=self.indent, ensure_ascii=False)