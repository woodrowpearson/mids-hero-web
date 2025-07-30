#!/bin/bash
# Wrapper script for Claude integration in GitHub Actions

set -e

# Function to display usage
usage() {
    echo "Usage: $0 --prompt <prompt> [--timeout <minutes>] [--pr <number>] [--post-comment]"
    echo "  --prompt        : The prompt to send to Claude (required)"
    echo "  --timeout       : Timeout in minutes (default: 10)"
    echo "  --pr            : PR number for context (optional)"
    echo "  --post-comment  : Post response as GitHub comment (optional)"
    exit 1
}

# Default values
TIMEOUT_MINUTES=10
PR_NUMBER=""
POST_COMMENT="false"
PROMPT=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --prompt)
            PROMPT="$2"
            shift 2
            ;;
        --timeout)
            TIMEOUT_MINUTES="$2"
            shift 2
            ;;
        --pr)
            PR_NUMBER="$2"
            shift 2
            ;;
        --post-comment)
            POST_COMMENT="true"
            shift
            ;;
        *)
            echo "Unknown option: $1"
            usage
            ;;
    esac
done

# Validate required arguments
if [ -z "$PROMPT" ]; then
    echo "Error: --prompt is required"
    usage
fi

# Set environment variables for Python script
export INPUT_DIRECT_PROMPT="$PROMPT"
export INPUT_TIMEOUT_MINUTES="$TIMEOUT_MINUTES"
export INPUT_PR_NUMBER="$PR_NUMBER"
export INPUT_POST_COMMENT="$POST_COMMENT"

# Ensure we're in the right directory
cd "$GITHUB_WORKSPACE" || exit 1

# Install Python dependencies
echo "Installing dependencies..."
pip install anthropic requests --quiet

# Copy GitHub event data if available
if [ -n "$GITHUB_EVENT_PATH" ] && [ -f "$GITHUB_EVENT_PATH" ]; then
    cp "$GITHUB_EVENT_PATH" github_event.json
fi

# Run the Python script
echo "Running Claude integration..."
python .github/scripts/claude_action.py

# Check if response file was created
if [ -f "claude_response.txt" ]; then
    echo "Claude integration completed successfully"
    exit 0
else
    echo "Error: Claude response file not created"
    exit 1
fi