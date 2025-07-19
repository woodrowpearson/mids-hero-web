#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["sqlalchemy", "psycopg2-binary"]
# ///
"""Cache statistics script for performance monitoring."""

import json
import sys
from pathlib import Path

# Add backend to path for imports
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

try:
    from app.services.power_cache import get_power_cache
    
    def main():
        """Print cache performance statistics."""
        cache = get_power_cache()
        stats = cache.get_cache_stats()
        print(json.dumps(stats, indent=2))

    if __name__ == '__main__':
        main()
        
except ImportError:
    print("Cache service not available - backend not properly initialized")