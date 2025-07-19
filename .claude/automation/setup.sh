#!/bin/bash
# Quick setup for Claude Code integration

echo "🚀 Setting up Claude Code for Mids Hero Web..."

# Install context management dependencies
if command -v pip3 &> /dev/null; then
    echo "📦 Installing context tools..."
    pip3 install -r requirements-context.txt
fi

# Create progress tracking file
if [ ! -f ".claude/progress.json" ]; then
    echo "📊 Initializing progress tracking..."
    cat > .claude/progress.json << EOF
{
  "epics": {
    "1": {"status": "complete", "percentage": 100},
    "2": {"status": "blocked", "percentage": 20},
    "3": {"status": "planned", "percentage": 0},
    "4": {"status": "planned", "percentage": 0},
    "5": {"status": "planned", "percentage": 0},
    "6": {"status": "future", "percentage": 0}
  },
  "last_updated": "$(date -Iseconds)"
}
EOF
fi

# Check for just command
if ! command -v just &> /dev/null; then
    echo "⚠️  'just' command not found. Install it from: https://github.com/casey/just"
    echo "   macOS: brew install just"
    echo "   Linux: cargo install just"
fi

# Make scripts executable
chmod +x scripts/context/*.py scripts/dev.py .claude/setup.sh

echo "✅ Claude Code setup complete!"
echo ""
echo "Next steps:"
echo "1. Run 'just quickstart' to set up development environment"
echo "2. Run 'just token-usage' to check context size"
echo "3. Run 'just dev' to start development"
echo ""
echo "📚 See CLAUDE.md for development guidelines"