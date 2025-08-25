#!/usr/bin/env bash
# Check that all .claude documentation files have timestamps
# This is used as a pre-commit hook

MISSING_TIMESTAMPS=0
FILES_CHECKED=0

# Check all .md files in .claude/ that are staged
for file in $(git diff --cached --name-only | grep "^\.claude/.*\.md$"); do
    if [ -f "$file" ]; then
        FILES_CHECKED=$((FILES_CHECKED + 1))
        
        # Check if file has timestamp within first 10 lines
        if ! head -10 "$file" | grep -E "^Last Updated: [0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2} UTC$" > /dev/null; then
            echo "❌ Missing timestamp: $file"
            MISSING_TIMESTAMPS=$((MISSING_TIMESTAMPS + 1))
        fi
    fi
done

if [ "$MISSING_TIMESTAMPS" -gt 0 ]; then
    echo ""
    echo "⚠️  $MISSING_TIMESTAMPS documentation file(s) missing timestamps!"
    echo ""
    echo "To fix, run:"
    echo "  python .claude/scripts/add_timestamp.py <file>"
    echo "Or for all files:"
    echo "  python .claude/scripts/add_timestamp.py .claude --recursive"
    echo ""
    exit 1
fi

if [ "$FILES_CHECKED" -gt 0 ]; then
    echo "✅ All $FILES_CHECKED documentation files have timestamps"
fi

exit 0