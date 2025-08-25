#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["sqlalchemy", "psycopg2-binary"]
# ///
"""Cache clearing script for power cache management."""

import sys
from pathlib import Path

# Add backend to path for imports
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

try:
    from app.services.power_cache import get_power_cache
    
    def main():
        """Clear all power cache data."""
        cache = get_power_cache()
        cache.clear_all_cache()
        print('Cache cleared')

    if __name__ == '__main__':
        main()
        
except ImportError:
    print("Cache service not available - backend not properly initialized")