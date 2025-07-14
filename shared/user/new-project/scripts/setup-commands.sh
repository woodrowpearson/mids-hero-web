#!/usr/bin/env bash
# Setup required command-line tools for Claude Code projects

set -euo pipefail

echo "🔧 Setting up required command-line tools..."

# Detect OS
OS="$(uname -s)"

# Install fd (find alternative)
if ! command -v fd &> /dev/null; then
    echo "📦 Installing fd..."
    case "$OS" in
        Darwin)
            brew install fd
            ;;
        Linux)
            if command -v apt-get &> /dev/null; then
                sudo apt-get install -y fd-find
                sudo ln -s /usr/bin/fdfind /usr/local/bin/fd
            elif command -v dnf &> /dev/null; then
                sudo dnf install -y fd-find
            else
                echo "⚠️  Please install fd manually: https://github.com/sharkdp/fd"
            fi
            ;;
        *)
            echo "⚠️  Unsupported OS. Please install fd manually."
            ;;
    esac
else
    echo "✅ fd is already installed"
fi

# Install trash-cli
if ! command -v trash &> /dev/null; then
    echo "📦 Installing trash-cli..."
    case "$OS" in
        Darwin)
            brew install trash
            ;;
        Linux)
            pip install --user trash-cli
            ;;
        *)
            echo "⚠️  Please install trash-cli manually: pip install trash-cli"
            ;;
    esac
else
    echo "✅ trash is already installed"
fi

# Install ripgrep (grep alternative)
if ! command -v rg &> /dev/null; then
    echo "📦 Installing ripgrep..."
    case "$OS" in
        Darwin)
            brew install ripgrep
            ;;
        Linux)
            if command -v apt-get &> /dev/null; then
                sudo apt-get install -y ripgrep
            elif command -v dnf &> /dev/null; then
                sudo dnf install -y ripgrep
            else
                echo "⚠️  Please install ripgrep manually: https://github.com/BurntSushi/ripgrep"
            fi
            ;;
        *)
            echo "⚠️  Unsupported OS. Please install ripgrep manually."
            ;;
    esac
else
    echo "✅ ripgrep is already installed"
fi

echo ""
echo "🎉 Setup complete! Installed tools:"
echo "  - fd (use instead of find)"
echo "  - trash (use instead of rm -rf)"
echo "  - rg (use instead of grep)"
echo ""
echo "Remember: NEVER use find, rm -rf, or grep in your commands!"