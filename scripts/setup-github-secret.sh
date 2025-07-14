#!/bin/bash
# Setup script for GitHub workflows - helps configure required secrets

set -euo pipefail

echo "🤖 Mids Hero Web - GitHub Workflows Setup"
echo "=========================================="
echo ""

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) is not installed."
    echo "   Please install it from: https://cli.github.com/"
    exit 1
fi

# Check if authenticated
if ! gh auth status > /dev/null 2>&1; then
    echo "❌ Not authenticated with GitHub CLI."
    echo "   Please run: gh auth login"
    exit 1
fi

echo "✅ GitHub CLI is installed and authenticated"
echo ""

# Get repository info
REPO_INFO=$(gh repo view --json owner,name)
REPO_OWNER=$(echo "$REPO_INFO" | jq -r '.owner.login')
REPO_NAME=$(echo "$REPO_INFO" | jq -r '.name')

echo "📁 Repository: $REPO_OWNER/$REPO_NAME"
echo ""

# Check if ANTHROPIC_API_KEY is already set
echo "🔑 Checking for required secrets..."
if gh secret list | grep -q "ANTHROPIC_API_KEY"; then
    echo "✅ ANTHROPIC_API_KEY is already configured"
    NEED_API_KEY=false
else
    echo "❌ ANTHROPIC_API_KEY is not configured"
    NEED_API_KEY=true
fi

echo ""

if [ "$NEED_API_KEY" = true ]; then
    echo "🔧 Setting up ANTHROPIC_API_KEY..."
    echo ""
    echo "You need an Anthropic API key to enable AI workflows."
    echo "Get one at: https://console.anthropic.com/"
    echo ""
    
    read -p "Do you have an Anthropic API key? (y/n): " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        echo "🔒 Please enter your Anthropic API key:"
        echo "   (Input will be hidden for security)"
        read -s API_KEY
        echo ""
        
        if [ -z "$API_KEY" ]; then
            echo "❌ No API key provided. Exiting."
            exit 1
        fi
        
        echo "🔄 Setting secret..."
        if echo "$API_KEY" | gh secret set ANTHROPIC_API_KEY; then
            echo "✅ ANTHROPIC_API_KEY configured successfully!"
        else
            echo "❌ Failed to set secret. Please check your permissions."
            exit 1
        fi
    else
        echo ""
        echo "ℹ️  To set up the API key later:"
        echo "   1. Get an API key from https://console.anthropic.com/"
        echo "   2. Go to your repository Settings → Secrets and variables → Actions"
        echo "   3. Create a new secret named 'ANTHROPIC_API_KEY'"
        echo "   4. Or run this script again"
        echo ""
        echo "⚠️  AI workflows will not work without the API key."
    fi
else
    echo "🎉 All required secrets are configured!"
fi

echo ""
echo "📋 Workflow Status Summary:"
echo "=========================="

# Check workflow files
WORKFLOWS_DIR=".github/workflows"
if [ -d "$WORKFLOWS_DIR" ]; then
    echo "✅ Workflow files are present:"
    ls -1 "$WORKFLOWS_DIR"/*.yml | sed 's|.*/||' | sed 's/^/   - /'
else
    echo "❌ No workflow files found in $WORKFLOWS_DIR"
fi

echo ""

# Check configuration files
CONFIG_DIR=".new-project/workflows"
if [ -d "$CONFIG_DIR" ]; then
    echo "✅ Configuration files are present:"
    ls -1 "$CONFIG_DIR" | sed 's/^/   - /'
else
    echo "❌ No configuration files found in $CONFIG_DIR"
fi

echo ""
echo "🚀 Next Steps:"
echo "=============="
echo ""

if [ "$NEED_API_KEY" = true ] && [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "1. 🔑 Set up your Anthropic API key (see instructions above)"
    echo "2. 🧪 Create a test PR to verify workflows are working"
    echo "3. 💬 Try mentioning @claude in an issue or PR comment"
    echo "4. 📊 Check the Actions tab for workflow runs"
else
    echo "1. 🧪 Create a test PR to verify workflows are working"
    echo "2. 💬 Try mentioning @claude in an issue or PR comment"
    echo "3. 📊 Check the Actions tab for workflow runs"
    echo "4. 📖 Read .new-project/workflows/implementation-guide.md for details"
fi

echo ""
echo "📚 Documentation:"
echo "   - Workflow guide: .new-project/workflows/implementation-guide.md"
echo "   - Configuration: .new-project/workflows/config.yaml"
echo "   - Workflow README: .github/workflows/README.md"

echo ""
echo "💡 Tips:"
echo "   - Workflows trigger on PRs automatically"
echo "   - Use @claude in comments for help"
echo "   - Run 'just context-health' to check Claude Code setup"
echo "   - Monitor token usage with 'just token-usage'"

echo ""
echo "✨ Mids Hero Web AI workflows are ready!"