"""Caching service for power data optimization."""

import hashlib
import json
import logging
from functools import lru_cache
from typing import Any, Dict, List, Optional, Union

from sqlalchemy.orm import Session

from app.models import Power, Powerset

logger = logging.getLogger(__name__)


class PowerCacheService:
    """Multi-tier caching service for power data."""

    def __init__(self, redis_client=None, max_memory_cache_size: int = 1000):
        """Initialize caching service.
        
        Args:
            redis_client: Optional Redis client for distributed caching
            max_memory_cache_size: Maximum size of in-memory LRU cache
        """
        self.redis_client = redis_client
        self.max_memory_cache_size = max_memory_cache_size
        self._memory_cache: Dict[str, Any] = {}
        
        # Cache TTL settings (in seconds)
        self.ttl_power_detail = 3600  # 1 hour
        self.ttl_powerset_list = 1800  # 30 minutes
        self.ttl_build_summary = 600   # 10 minutes
        
        # Cache hit/miss statistics
        self.stats = {
            "memory_hits": 0,
            "memory_misses": 0,
            "redis_hits": 0,
            "redis_misses": 0,
            "db_queries": 0
        }

    def _generate_cache_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate a cache key from arguments."""
        key_data = f"{prefix}:{':'.join(map(str, args))}"
        if kwargs:
            sorted_kwargs = sorted(kwargs.items())
            key_data += f":{':'.join(f'{k}={v}' for k, v in sorted_kwargs)}"
        
        # Hash long keys to keep them manageable
        if len(key_data) > 200:
            key_data = f"{prefix}:{hashlib.md5(key_data.encode()).hexdigest()}"
        
        return key_data

    def _get_from_memory(self, key: str) -> Optional[Any]:
        """Get value from in-memory cache."""
        if key in self._memory_cache:
            self.stats["memory_hits"] += 1
            return self._memory_cache[key]
        
        self.stats["memory_misses"] += 1
        return None

    def _set_to_memory(self, key: str, value: Any) -> None:
        """Set value in in-memory cache with LRU eviction."""
        # Simple LRU: remove oldest if at capacity
        if len(self._memory_cache) >= self.max_memory_cache_size:
            # Remove the first item (oldest in insertion order)
            oldest_key = next(iter(self._memory_cache))
            del self._memory_cache[oldest_key]
        
        self._memory_cache[key] = value

    def _get_from_redis(self, key: str) -> Optional[Any]:
        """Get value from Redis cache."""
        if not self.redis_client:
            return None
        
        try:
            cached_data = self.redis_client.get(key)
            if cached_data:
                self.stats["redis_hits"] += 1
                return json.loads(cached_data)
            
            self.stats["redis_misses"] += 1
            return None
        
        except Exception as e:
            logger.warning(f"Redis get error for key {key}: {e}")
            return None

    def _set_to_redis(self, key: str, value: Any, ttl: int) -> None:
        """Set value in Redis cache with TTL."""
        if not self.redis_client:
            return
        
        try:
            self.redis_client.setex(
                key, 
                ttl, 
                json.dumps(value, default=str)
            )
        except Exception as e:
            logger.warning(f"Redis set error for key {key}: {e}")

    def get_power_by_id(self, session: Session, power_id: int) -> Optional[Dict[str, Any]]:
        """Get power details by ID with caching."""
        cache_key = self._generate_cache_key("power", power_id)
        
        # Try memory cache first
        cached_power = self._get_from_memory(cache_key)
        if cached_power:
            return cached_power
        
        # Try Redis cache
        cached_power = self._get_from_redis(cache_key)
        if cached_power:
            # Store in memory cache for faster access
            self._set_to_memory(cache_key, cached_power)
            return cached_power
        
        # Query database
        self.stats["db_queries"] += 1
        power = session.query(Power).filter(Power.id == power_id).first()
        
        if not power:
            return None
        
        # Convert to dictionary for caching
        power_dict = {
            "id": power.id,
            "name": power.name,
            "display_name": power.display_name,
            "description": power.description,
            "powerset_id": power.powerset_id,
            "level_available": power.level_available,
            "power_type": power.power_type,
            "target_type": power.target_type,
            "accuracy": float(power.accuracy) if power.accuracy else None,
            "damage_scale": float(power.damage_scale) if power.damage_scale else None,
            "endurance_cost": float(power.endurance_cost) if power.endurance_cost else None,
            "recharge_time": float(power.recharge_time) if power.recharge_time else None,
            "activation_time": float(power.activation_time) if power.activation_time else None,
            "range_feet": power.range_feet,
            "radius_feet": power.radius_feet,
            "max_targets": power.max_targets,
            "effects": power.effects,
            "effect_groups": power.effect_groups,
            "icon_path": power.icon_path,
            "internal_name": power.internal_name,
            "requires_line_of_sight": power.requires_line_of_sight,
            "modes_required": power.modes_required,
            "modes_disallowed": power.modes_disallowed,
            "ai_report": power.ai_report,
            "display_info": power.display_info
        }
        
        # Cache the result
        self._set_to_memory(cache_key, power_dict)
        self._set_to_redis(cache_key, power_dict, self.ttl_power_detail)
        
        return power_dict

    def get_powers_by_powerset(
        self, 
        session: Session, 
        powerset_id: int, 
        level_filter: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get powers by powerset with optional level filtering."""
        cache_key = self._generate_cache_key(
            "powerset_powers", 
            powerset_id, 
            level=level_filter
        )
        
        # Try cache layers
        cached_powers = self._get_from_memory(cache_key)
        if cached_powers:
            return cached_powers
        
        cached_powers = self._get_from_redis(cache_key)
        if cached_powers:
            self._set_to_memory(cache_key, cached_powers)
            return cached_powers
        
        # Query database
        self.stats["db_queries"] += 1
        query = session.query(Power).filter(Power.powerset_id == powerset_id)
        
        if level_filter:
            query = query.filter(Power.level_available <= level_filter)
        
        powers = query.order_by(Power.level_available, Power.display_order).all()
        
        # Convert to list of dictionaries
        powers_list = []
        for power in powers:
            power_dict = {
                "id": power.id,
                "name": power.name,
                "display_name": power.display_name,
                "level_available": power.level_available,
                "power_type": power.power_type,
                "target_type": power.target_type,
                "accuracy": float(power.accuracy) if power.accuracy else None,
                "damage_scale": float(power.damage_scale) if power.damage_scale else None,
                "endurance_cost": float(power.endurance_cost) if power.endurance_cost else None,
                "recharge_time": float(power.recharge_time) if power.recharge_time else None,
                "icon_path": power.icon_path
            }
            powers_list.append(power_dict)
        
        # Cache the result
        self._set_to_memory(cache_key, powers_list)
        self._set_to_redis(cache_key, powers_list, self.ttl_powerset_list)
        
        return powers_list

    def get_build_summary_data(
        self, 
        session: Session, 
        archetype_id: Optional[int] = None,
        powerset_id: Optional[int] = None,
        max_level: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get build summary data with caching."""
        cache_key = self._generate_cache_key(
            "build_summary",
            archetype=archetype_id,
            powerset=powerset_id,
            max_level=max_level
        )
        
        # Try cache layers
        cached_data = self._get_from_memory(cache_key)
        if cached_data:
            return cached_data
        
        cached_data = self._get_from_redis(cache_key)
        if cached_data:
            self._set_to_memory(cache_key, cached_data)
            return cached_data
        
        # Query materialized view if available, otherwise regular query
        self.stats["db_queries"] += 1
        try:
            # Try materialized view first
            query = """
                SELECT * FROM power_build_summary 
                WHERE 1=1
            """
            params = {}
            
            if archetype_id:
                query += " AND archetype_id = :archetype_id"
                params["archetype_id"] = archetype_id
            
            if powerset_id:
                query += " AND powerset_id = :powerset_id"
                params["powerset_id"] = powerset_id
            
            if max_level:
                query += " AND level_available <= :max_level"
                params["max_level"] = max_level
            
            query += " ORDER BY level_available, display_order"
            
            result = session.execute(query, params)
            summary_data = [dict(row) for row in result]
            
        except Exception as e:
            logger.warning(f"Materialized view query failed, falling back to regular query: {e}")
            
            # Fallback to regular query
            query = session.query(
                Power.id,
                Power.name,
                Power.internal_name,
                Power.display_name,
                Power.powerset_id,
                Powerset.name.label('powerset_name'),
                Powerset.archetype_id,
                Power.level_available,
                Power.power_type,
                Power.target_type,
                Power.accuracy,
                Power.damage_scale,
                Power.endurance_cost,
                Power.recharge_time,
                Power.activation_time,
                Power.range_feet,
                Power.max_targets,
                Power.icon_path,
                Power.display_order
            ).join(Powerset)
            
            if archetype_id:
                query = query.filter(Powerset.archetype_id == archetype_id)
            
            if powerset_id:
                query = query.filter(Power.powerset_id == powerset_id)
            
            if max_level:
                query = query.filter(Power.level_available <= max_level)
            
            results = query.order_by(Power.level_available, Power.display_order).all()
            
            summary_data = []
            for row in results:
                summary_data.append({
                    "id": row.id,
                    "name": row.name,
                    "internal_name": row.internal_name,
                    "display_name": row.display_name,
                    "powerset_id": row.powerset_id,
                    "powerset_name": row.powerset_name,
                    "archetype_id": row.archetype_id,
                    "level_available": row.level_available,
                    "power_type": row.power_type,
                    "target_type": row.target_type,
                    "accuracy": float(row.accuracy) if row.accuracy else None,
                    "damage_scale": float(row.damage_scale) if row.damage_scale else None,
                    "endurance_cost": float(row.endurance_cost) if row.endurance_cost else None,
                    "recharge_time": float(row.recharge_time) if row.recharge_time else None,
                    "activation_time": float(row.activation_time) if row.activation_time else None,
                    "range_feet": row.range_feet,
                    "max_targets": row.max_targets,
                    "icon_path": row.icon_path,
                    "display_order": row.display_order
                })
        
        # Cache the result
        self._set_to_memory(cache_key, summary_data)
        self._set_to_redis(cache_key, summary_data, self.ttl_build_summary)
        
        return summary_data

    def invalidate_power_cache(self, power_id: int) -> None:
        """Invalidate cache for a specific power."""
        cache_key = self._generate_cache_key("power", power_id)
        
        # Remove from memory cache
        if cache_key in self._memory_cache:
            del self._memory_cache[cache_key]
        
        # Remove from Redis
        if self.redis_client:
            try:
                self.redis_client.delete(cache_key)
            except Exception as e:
                logger.warning(f"Redis delete error for key {cache_key}: {e}")

    def invalidate_powerset_cache(self, powerset_id: int) -> None:
        """Invalidate all cache entries for a powerset."""
        # This is a simplified approach - in production you might want
        # more sophisticated cache invalidation
        if self.redis_client:
            try:
                # Get all keys matching the pattern
                pattern = f"powerset_powers:{powerset_id}:*"
                keys = self.redis_client.keys(pattern)
                if keys:
                    self.redis_client.delete(*keys)
            except Exception as e:
                logger.warning(f"Redis batch delete error: {e}")
        
        # Clear memory cache entries (simple approach: clear all)
        keys_to_remove = [k for k in self._memory_cache.keys() 
                         if k.startswith(f"powerset_powers:{powerset_id}:")]
        for key in keys_to_remove:
            del self._memory_cache[key]

    def clear_all_cache(self) -> None:
        """Clear all cache layers."""
        self._memory_cache.clear()
        
        if self.redis_client:
            try:
                # Clear all power-related keys
                patterns = ["power:*", "powerset_powers:*", "build_summary:*"]
                for pattern in patterns:
                    keys = self.redis_client.keys(pattern)
                    if keys:
                        self.redis_client.delete(*keys)
            except Exception as e:
                logger.warning(f"Redis clear error: {e}")

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics."""
        total_requests = (
            self.stats["memory_hits"] + 
            self.stats["memory_misses"]
        )
        
        redis_requests = (
            self.stats["redis_hits"] + 
            self.stats["redis_misses"]
        )
        
        return {
            "memory_cache_size": len(self._memory_cache),
            "memory_hit_rate": (
                self.stats["memory_hits"] / total_requests 
                if total_requests > 0 else 0
            ),
            "redis_hit_rate": (
                self.stats["redis_hits"] / redis_requests 
                if redis_requests > 0 else 0
            ),
            "total_db_queries": self.stats["db_queries"],
            "stats": self.stats
        }


# Global cache instance
_power_cache_instance: Optional[PowerCacheService] = None


def get_power_cache() -> PowerCacheService:
    """Get the global power cache instance."""
    global _power_cache_instance
    
    if _power_cache_instance is None:
        # Initialize with default settings
        # In production, you'd pass Redis client here
        _power_cache_instance = PowerCacheService()
    
    return _power_cache_instance


def init_power_cache(redis_client=None, max_memory_cache_size: int = 1000) -> None:
    """Initialize the global power cache with custom settings."""
    global _power_cache_instance
    _power_cache_instance = PowerCacheService(redis_client, max_memory_cache_size)


# Decorator for caching function results
def cached_power_query(ttl: int = 300):
    """Decorator for caching power query results."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            cache_key = f"query:{func.__name__}:" + hashlib.md5(
                str(args + tuple(sorted(kwargs.items()))).encode()
            ).hexdigest()
            
            cache = get_power_cache()
            
            # Try to get from cache
            result = cache._get_from_memory(cache_key)
            if result is not None:
                return result
            
            result = cache._get_from_redis(cache_key)
            if result is not None:
                cache._set_to_memory(cache_key, result)
                return result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache._set_to_memory(cache_key, result)
            cache._set_to_redis(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator