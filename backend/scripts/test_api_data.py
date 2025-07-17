#!/usr/bin/env python3
"""Test script to verify imported data through API endpoints."""

import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def test_archetypes():
    """Test archetypes endpoint."""
    print("Testing /api/archetypes...")
    response = requests.get(f"{BASE_URL}/api/archetypes")
    if response.status_code != 200:
        print(f"  ❌ Failed with status {response.status_code}")
        return False
    
    data = response.json()
    print(f"  ✓ Found {len(data)} archetypes")
    
    # Show some sample archetypes
    for arch in data[:5]:
        print(f"    - {arch['display_name']} ({arch['name']})")
    
    return True

def test_archetype_detail():
    """Test archetype detail endpoint."""
    print("\nTesting /api/archetypes/1...")
    response = requests.get(f"{BASE_URL}/api/archetypes/1")
    if response.status_code != 200:
        print(f"  ❌ Failed with status {response.status_code}")
        return False
    
    data = response.json()
    print(f"  ✓ Archetype: {data['display_name']}")
    print(f"    - HP Base: {data['hit_points_base']}")
    print(f"    - Primary: {data['primary_group']}")
    print(f"    - Secondary: {data['secondary_group']}")
    
    return True

def test_powersets():
    """Test powersets for an archetype."""
    print("\nTesting /api/archetypes/1/powersets...")
    response = requests.get(f"{BASE_URL}/api/archetypes/1/powersets")
    if response.status_code != 200:
        print(f"  ❌ Failed with status {response.status_code}")
        return False
    
    data = response.json()
    print(f"  ✓ Found {len(data)} powersets for Blaster")
    
    # Group by type
    by_type = {}
    for ps in data:
        ps_type = ps.get('powerset_type', 'unknown')
        by_type[ps_type] = by_type.get(ps_type, 0) + 1
    
    for ps_type, count in by_type.items():
        print(f"    - {ps_type}: {count}")
    
    return True

def test_powers():
    """Test powers endpoint."""
    print("\nTesting /api/powers...")
    response = requests.get(f"{BASE_URL}/api/powers?limit=5")
    if response.status_code != 200:
        print(f"  ❌ Failed with status {response.status_code}")
        return False
    
    data = response.json()
    print(f"  ✓ Powers endpoint works (returned {len(data)} powers)")
    
    if len(data) == 0:
        print("    - No powers in database yet")
    
    return True

def main():
    """Run all tests."""
    print("Testing Mids Hero Web API with imported data")
    print("=" * 50)
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code != 200:
            print("❌ Server is not running. Start it with: just backend-dev")
            sys.exit(1)
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Start it with: just backend-dev")
        sys.exit(1)
    
    print("✓ Server is running\n")
    
    # Run tests
    tests = [
        test_archetypes,
        test_archetype_detail,
        test_powersets,
        test_powers
    ]
    
    passed = sum(1 for test in tests if test())
    
    print("\n" + "=" * 50)
    print(f"Tests passed: {passed}/{len(tests)}")
    
    if passed == len(tests):
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed")
        sys.exit(1)

if __name__ == "__main__":
    main()