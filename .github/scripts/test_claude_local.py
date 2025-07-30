#!/usr/bin/env python3
"""
Local test script for Claude integration
Tests that the API key is valid and Claude responds
"""

import os
import sys
import anthropic

def test_claude_connection():
    """Test basic Claude API connection"""
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    
    if not api_key:
        print("❌ Error: ANTHROPIC_API_KEY environment variable not set")
        print("Please set: export ANTHROPIC_API_KEY='your-key-here'")
        return False
    
    print("✅ API key found")
    
    try:
        client = anthropic.Anthropic(api_key=api_key)
        print("✅ Anthropic client created")
        
        # Test with a simple message
        print("Testing Claude API...")
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=100,
            messages=[
                {
                    "role": "user",
                    "content": "Say 'Hello from Mids Hero Web!' in exactly 5 words."
                }
            ]
        )
        
        response = message.content[0].text if message.content else "No response"
        print(f"✅ Claude responded: {response}")
        
        return True
        
    except anthropic.APIError as e:
        print(f"❌ API Error: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

def test_wrapper_script():
    """Test that wrapper script exists and is executable"""
    wrapper_path = ".github/scripts/claude_wrapper.sh"
    
    if not os.path.exists(wrapper_path):
        print(f"❌ Wrapper script not found at {wrapper_path}")
        return False
    
    print(f"✅ Wrapper script exists")
    
    if not os.access(wrapper_path, os.X_OK):
        print(f"❌ Wrapper script is not executable")
        print(f"Run: chmod +x {wrapper_path}")
        return False
    
    print(f"✅ Wrapper script is executable")
    return True

def main():
    """Run all tests"""
    print("🧪 Testing Claude Integration Setup")
    print("-" * 40)
    
    all_passed = True
    
    # Test wrapper script
    if not test_wrapper_script():
        all_passed = False
    
    print()
    
    # Test Claude connection
    if not test_claude_connection():
        all_passed = False
    
    print("-" * 40)
    
    if all_passed:
        print("✅ All tests passed! Claude integration is ready.")
        sys.exit(0)
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()