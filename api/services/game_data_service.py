"""
Game Data Service - Direct JSON file access with smart caching
Epic 2.5.5: Demonstrates the power of JSON-native architecture
"""
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from functools import lru_cache
import hashlib
from datetime import datetime

from ..core.config import settings

class GameDataService:
    """
    JSON-native data service that directly serves City of Heroes game data.
    No database, no ORM, no transformations - just clean JSON access.
    """
    
    def __init__(self, data_path: Optional[Path] = None):
        self.data_path = data_path or settings.game_data_path
        self._cache_checksums: Dict[str, str] = {}
        
    def _get_file_checksum(self, file_path: Path) -> str:
        """Calculate file checksum for cache invalidation"""
        if not file_path.exists():
            return ""
        return hashlib.md5(file_path.read_bytes()).hexdigest()
    
    def _should_invalidate_cache(self, file_path: Path) -> bool:
        """Check if cache should be invalidated based on file changes"""
        current_checksum = self._get_file_checksum(file_path)
        cached_checksum = self._cache_checksums.get(str(file_path))
        
        if cached_checksum != current_checksum:
            self._cache_checksums[str(file_path)] = current_checksum
            return True
        return False
    
    @lru_cache(maxsize=32)
    def get_archetype(self, name: str) -> Dict[str, Any]:
        """
        Get archetype data by name.
        Example: get_archetype("blaster") returns Blaster archetype data
        """
        file_path = self.data_path / "archetypes" / f"{name.lower()}.json"
        
        if not file_path.exists():
            raise FileNotFoundError(f"Archetype '{name}' not found")
        
        if self._should_invalidate_cache(file_path):
            self.get_archetype.cache_clear()
            
        return json.loads(file_path.read_text())
    
    @lru_cache(maxsize=1)
    def get_all_archetypes(self) -> List[Dict[str, Any]]:
        """Get all available archetypes"""
        archetype_dir = self.data_path / "archetypes"
        
        if not archetype_dir.exists():
            return []
        
        archetypes = []
        for file_path in archetype_dir.glob("*.json"):
            if file_path.stem != "_index":  # Skip index files
                archetype_data = json.loads(file_path.read_text())
                archetypes.append(archetype_data)
        
        return sorted(archetypes, key=lambda x: x.get("display_name", ""))
    
    @lru_cache(maxsize=1)
    def get_all_powers(self) -> Dict[str, Any]:
        """
        Get comprehensive power database.
        This is the main power search index with all powers and their details.
        """
        file_path = self.data_path / "all_power_search.json"
        
        if not file_path.exists():
            raise FileNotFoundError("Power database not found")
        
        if self._should_invalidate_cache(file_path):
            self.get_all_powers.cache_clear()
            
        return json.loads(file_path.read_text())
    
    @lru_cache(maxsize=64)
    def get_powerset(self, archetype: str, powerset_name: str) -> Dict[str, Any]:
        """
        Get specific powerset for an archetype.
        Example: get_powerset("blaster", "fire_blast")
        """
        file_path = self.data_path / "powersets" / archetype.lower() / f"{powerset_name.lower()}.json"
        
        if not file_path.exists():
            raise FileNotFoundError(f"Powerset '{powerset_name}' not found for archetype '{archetype}'")
        
        if self._should_invalidate_cache(file_path):
            self.get_powerset.cache_clear()
            
        return json.loads(file_path.read_text())
    
    @lru_cache(maxsize=32)
    def get_archetype_powersets(self, archetype: str) -> List[str]:
        """Get all available powersets for an archetype"""
        powerset_dir = self.data_path / "powersets" / archetype.lower()
        
        if not powerset_dir.exists():
            return []
        
        return [
            file_path.stem 
            for file_path in powerset_dir.glob("*.json")
            if file_path.stem != "_index"
        ]
    
    @lru_cache(maxsize=128)
    def get_enhancement(self, name: str) -> Dict[str, Any]:
        """Get enhancement/boost data by name"""
        # Try different locations where enhancement data might be
        possible_paths = [
            self.data_path / "boosts" / f"{name.lower()}.json",
            self.data_path / "boost_sets" / f"{name.lower()}.json",
            self.data_path / "enhancements" / f"{name.lower()}.json",
        ]
        
        for file_path in possible_paths:
            if file_path.exists():
                if self._should_invalidate_cache(file_path):
                    self.get_enhancement.cache_clear()
                return json.loads(file_path.read_text())
        
        raise FileNotFoundError(f"Enhancement '{name}' not found")
    
    @lru_cache(maxsize=1)
    def get_boost_sets(self) -> List[Dict[str, Any]]:
        """Get all enhancement sets"""
        boost_dir = self.data_path / "boost_sets"
        
        if not boost_dir.exists():
            return []
        
        sets = []
        for file_path in boost_dir.glob("*.json"):
            if file_path.stem != "_index":
                set_data = json.loads(file_path.read_text())
                sets.append(set_data)
        
        return sorted(sets, key=lambda x: x.get("display_name", ""))
    
    def search_powers(self, query: str, archetype: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search powers by name or description.
        Optionally filter by archetype.
        """
        all_powers = self.get_all_powers()
        query_lower = query.lower()
        
        results = []
        for power_id, power_data in all_powers.items():
            # Check if power matches query
            if (query_lower in power_data.get("display_name", "").lower() or
                query_lower in power_data.get("description", "").lower()):
                
                # Apply archetype filter if specified
                if archetype:
                    power_archetypes = power_data.get("archetypes", [])
                    if archetype.lower() not in [a.lower() for a in power_archetypes]:
                        continue
                
                results.append(power_data)
        
        return results[:100]  # Limit results for performance
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about available game data"""
        try:
            archetype_count = len(list((self.data_path / "archetypes").glob("*.json")))
        except:
            archetype_count = 0
            
        try:
            all_powers = self.get_all_powers()
            power_count = len(all_powers)
        except:
            power_count = 0
            
        try:
            boost_count = len(list((self.data_path / "boost_sets").glob("*.json")))
        except:
            boost_count = 0
        
        return {
            "archetypes": archetype_count,
            "powers": power_count,
            "enhancement_sets": boost_count,
            "data_path": str(self.data_path),
            "data_exists": self.data_path.exists(),
        }
    
    def clear_cache(self):
        """Clear all caches - useful after data updates"""
        self.get_archetype.cache_clear()
        self.get_all_archetypes.cache_clear()
        self.get_all_powers.cache_clear()
        self.get_powerset.cache_clear()
        self.get_archetype_powersets.cache_clear()
        self.get_enhancement.cache_clear()
        self.get_boost_sets.cache_clear()
        self._cache_checksums.clear()

# Singleton instance
game_data_service = GameDataService()