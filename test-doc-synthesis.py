#!/usr/bin/env python3
"""
Test script to verify doc-synthesis workflow functionality
"""

import os
import sys

def test_basic_functionality():
    """Test basic functionality without API calls"""
    print("Testing doc-synthesis workflow components...")
    
    # Test 1: File reading
    try:
        with open('README.md', 'r') as f:
            content = f.read()[:100]
        print(f"✅ Can read README.md: {len(content)} chars")
    except Exception as e:
        print(f"❌ Cannot read README.md: {e}")
        return False
    
    # Test 2: CLAUDE.md reading
    try:
        with open('CLAUDE.md', 'r') as f:
            content = f.read()[:100]
        print(f"✅ Can read CLAUDE.md: {len(content)} chars")
    except Exception as e:
        print(f"❌ Cannot read CLAUDE.md: {e}")
        return False
    
    # Test 3: Environment variables
    changed_files = os.environ.get('CHANGED_FILES', 'README.md .github/workflows/doc-synthesis.yml')
    print(f"✅ Changed files: {changed_files}")
    
    # Test 4: File writing
    try:
        with open('test_output.md', 'w') as f:
            f.write("# Test Documentation Suggestions\n\nThis is a test.\n")
        print("✅ Can write output file")
        os.remove('test_output.md')
    except Exception as e:
        print(f"❌ Cannot write file: {e}")
        return False
    
    print("✅ All basic tests passed!")
    return True

def test_with_api():
    """Test with actual API call"""
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        print("❌ No ANTHROPIC_API_KEY found")
        return False
    
    try:
        import anthropic
        client = anthropic.Anthropic()
        
        response = client.messages.create(
            model='claude-3-5-sonnet-20241022',
            max_tokens=100,
            messages=[{'role': 'user', 'content': 'Say "Hello from doc-synthesis test"'}]
        )
        
        result = response.content[0].text
        print(f"✅ API call successful: {result[:50]}...")
        return True
        
    except Exception as e:
        print(f"❌ API call failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing doc-synthesis workflow components\n")
    
    basic_ok = test_basic_functionality()
    
    if basic_ok:
        print("\n🔌 Testing API connection...")
        api_ok = test_with_api()
        
        if api_ok:
            print("\n🎉 All tests passed! Workflow should work.")
        else:
            print("\n⚠️ API test failed - check ANTHROPIC_API_KEY")
    else:
        print("\n💥 Basic tests failed - workflow has fundamental issues")