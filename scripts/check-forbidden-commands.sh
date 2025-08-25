#!/bin/bash

# Check for forbidden commands in code
# This script enforces the use of modern alternatives

set -e

VIOLATIONS=0

echo "🔍 Checking for forbidden commands..."

# Check for rm -rf (should use trash) - exclude comments
if fd -e sh -e py --exclude check-forbidden-commands.sh | xargs rg "^[^#]*rm -rf" --no-heading 2>/dev/null | rg -v "# |echo " ; then
    echo "❌ Found 'rm -rf' usage - use 'trash' instead"
    VIOLATIONS=$((VIOLATIONS + 1))
fi

# Check for find command (should use fd) - exclude comments
if fd -e sh -e py -e md | xargs rg "^[^#]*find \." --no-heading 2>/dev/null | rg -v "fd|/usr/bin/find" ; then
    echo "❌ Found 'find .' usage - use 'fd' instead"
    VIOLATIONS=$((VIOLATIONS + 1))
fi

# Check for grep usage in scripts (should use rg/ripgrep) - exclude comments
if fd -e sh -e py | xargs rg "^[^#]*grep -r" --no-heading 2>/dev/null | rg -v "rg|ripgrep" ; then
    echo "❌ Found 'grep -r' usage - use 'rg' (ripgrep) instead"
    VIOLATIONS=$((VIOLATIONS + 1))
fi

# Check for pip install (should use uv) - exclude comments and uv pip
if fd -e sh -e py --exclude check-forbidden-commands.sh | xargs rg "^[^#]*pip install" --no-heading 2>/dev/null | rg -v "uv pip" ; then
    echo "❌ Found 'pip install' usage - use 'uv' instead"
    VIOLATIONS=$((VIOLATIONS + 1))
fi

if [ "$VIOLATIONS" -eq 0 ]; then
    echo "✅ No forbidden commands found"
    exit 0
else
    echo ""
    echo "⚠️  Found $VIOLATIONS command compliance violations!"
    echo ""
    echo "Required replacements:"
    echo "  • rm -rf → trash"
    echo "  • find → fd"
    echo "  • grep → rg (ripgrep)"
    echo "  • pip → uv"
    echo ""
    echo "See CLAUDE.md for command compliance rules."
    exit 1
fi